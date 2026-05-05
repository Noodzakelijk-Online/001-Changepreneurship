"""
BenchmarkIntelligenceService — Sprint 6 (S6-03)
=================================================
CEO (Section 13.1):
  "Platform can learn — users in this stage usually need 3 mentor outreach
   attempts before a useful reply."

Design constraints:
  - User ID is NEVER stored in benchmark table (GDPR, CEO Section 7.2.N)
  - cohort_key = SHA-256 of "{founder_type}:{venture_type}:{phase_id}"
  - Min sample size = 10 before benchmark message is shown
  - Every benchmark message includes "Based on X founders" for transparency
  - Founder can opt out of contributing to benchmarks (benchmark_opt_out=True
    in their profile — if not set, default is to contribute)
"""
import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from src.models.assessment import db
from src.models.benchmark_data import (
    BenchmarkData,
    BENCHMARK_MIN_SAMPLE,
    ALL_METRIC_TYPES,
    METRIC_PHASE_COMPLETION,
    METRIC_TIME_TO_COMPLETE,
    METRIC_MENTOR_RESPONSE,
    METRIC_BLOCKER_RESOLVED,
)

logger = logging.getLogger(__name__)


class BenchmarkIntelligenceService:
    """
    Records anonymised outcomes and queries cohort benchmarks.
    All writes are aggregate-only — no user_id ever persisted in benchmark_data.
    """

    # ------------------------------------------------------------------
    # Cohort key helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_cohort_key(founder_type: str, venture_type: str, phase_id: str) -> str:
        """SHA-256 of canonical cohort string — irreversible."""
        raw = f"{(founder_type or 'UNKNOWN').upper()}:{(venture_type or 'UNKNOWN').upper()}:{phase_id or 'UNKNOWN'}"
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def _build_cohort_label(founder_type: str, venture_type: str, phase_id: str) -> str:
        """Human-readable label (not a PK, not used for joins)."""
        return f"{(founder_type or 'UNKNOWN').upper()}:{(venture_type or 'UNKNOWN').upper()}:{phase_id or 'UNKNOWN'}"

    # ------------------------------------------------------------------
    # Write: record outcome (anonymised)
    # ------------------------------------------------------------------

    def record_outcome(
        self,
        user_id: int,
        metric_type: str,
        metric_value: Dict[str, Any],
        founder_type: str = 'UNKNOWN',
        venture_type: str = 'UNKNOWN',
        phase_id: str = 'UNKNOWN',
    ) -> bool:
        """
        Increment cohort benchmark aggregate.
        user_id is used ONLY to check opt-out preference — never stored.
        Returns True if recorded, False if user opted out or metric_type invalid.
        """
        if metric_type not in ALL_METRIC_TYPES:
            logger.warning('[Benchmark] Unknown metric_type=%s — ignored', metric_type)
            return False

        # Check opt-out — query profile, check field if it exists
        if self._is_opted_out(user_id):
            logger.debug('[Benchmark] user_id=%d opted out — not recording', user_id)
            return False

        cohort_key   = self._build_cohort_key(founder_type, venture_type, phase_id)
        cohort_label = self._build_cohort_label(founder_type, venture_type, phase_id)

        try:
            existing = BenchmarkData.query.filter_by(
                cohort_key=cohort_key,
                metric_type=metric_type,
            ).first()

            if existing:
                existing.metric_value = self._merge_metrics(
                    existing.metric_value,
                    metric_value,
                    existing.sample_size,
                )
                existing.sample_size  += 1
                existing.last_updated  = datetime.utcnow()
            else:
                row = BenchmarkData(
                    cohort_key   = cohort_key,
                    cohort_label = cohort_label,
                    metric_type  = metric_type,
                    metric_value = metric_value,
                    sample_size  = 1,
                    is_anonymized = True,
                )
                db.session.add(row)

            db.session.commit()
            logger.info(
                '[Benchmark] Recorded metric=%s cohort=%s', metric_type, cohort_label
            )
            return True

        except Exception:
            db.session.rollback()
            logger.exception('[Benchmark] Failed to record outcome')
            return False

    # ------------------------------------------------------------------
    # Read: cohort benchmark
    # ------------------------------------------------------------------

    def get_cohort_benchmark(
        self,
        venture_type: str,
        phase_id: str,
        metric_type: str,
        founder_type: str = 'UNKNOWN',
    ) -> Optional[Dict[str, Any]]:
        """
        Returns aggregate benchmark for a cohort+metric, or None if
        sample_size < BENCHMARK_MIN_SAMPLE (10).
        """
        cohort_key = self._build_cohort_key(founder_type, venture_type, phase_id)
        row = BenchmarkData.query.filter_by(
            cohort_key=cohort_key,
            metric_type=metric_type,
        ).first()

        if row is None or row.sample_size < BENCHMARK_MIN_SAMPLE:
            return None

        return {
            'cohort_label': row.cohort_label,
            'metric_type':  metric_type,
            'metric_value': row.metric_value,
            'sample_size':  row.sample_size,
            'last_updated': row.last_updated.isoformat() if row.last_updated else None,
        }

    def get_personalized_benchmark_message(
        self,
        user_id: int,
        metric_type: str,
        founder_type: str = 'UNKNOWN',
        venture_type: str = 'UNKNOWN',
        phase_id: str = 'UNKNOWN',
    ) -> Optional[str]:
        """
        Returns a human-readable benchmark message, or None if no data yet.
        Always includes "Based on X founders" for transparency (CEO Section 7.2).
        """
        benchmark = self.get_cohort_benchmark(venture_type, phase_id, metric_type, founder_type)
        if not benchmark:
            return None

        n = benchmark['sample_size']
        val = benchmark['metric_value']

        if metric_type == METRIC_PHASE_COMPLETION:
            pct = val.get('completion_rate_pct', 0)
            return f"Based on {n} similar founders, {pct:.0f}% successfully completed this phase."

        if metric_type == METRIC_TIME_TO_COMPLETE:
            days = val.get('median_days', 0)
            return f"Based on {n} similar founders, this phase typically takes {days:.0f} days."

        if metric_type == METRIC_MENTOR_RESPONSE:
            attempts = val.get('mean_attempts', 0)
            return (
                f"Based on {n} similar founders, getting a useful mentor reply "
                f"typically takes {attempts:.1f} outreach attempts."
            )

        if metric_type == METRIC_BLOCKER_RESOLVED:
            days = val.get('median_resolution_days', 0)
            return (
                f"Based on {n} similar founders, this type of blocker "
                f"is typically resolved in {days:.0f} days."
            )

        # Generic fallback
        return f"Benchmark data available from {n} similar founders."

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_opted_out(user_id: int) -> bool:
        """
        Checks if user opted out of benchmark contribution.
        Default: opted IN (False = not opted out).
        Safe if profile doesn't exist or column doesn't exist.
        """
        try:
            from src.models.assessment import EntrepreneurProfile
            profile = EntrepreneurProfile.query.filter_by(user_id=user_id).first()
            if profile is None:
                return False
            # benchmark_opt_out field may not exist yet; getattr with default False
            return bool(getattr(profile, 'benchmark_opt_out', False))
        except Exception:
            return False

    @staticmethod
    def _merge_metrics(
        existing: Dict[str, Any],
        new_val: Dict[str, Any],
        old_sample: int,
    ) -> Dict[str, Any]:
        """
        Incrementally update running averages.
        Only updates numeric fields present in both dicts.
        """
        merged = dict(existing)
        for k, v in new_val.items():
            if k in existing and isinstance(v, (int, float)) and isinstance(existing[k], (int, float)):
                # Weighted running mean: (old_mean * n + new_val) / (n + 1)
                merged[k] = (existing[k] * old_sample + v) / (old_sample + 1)
        return merged
