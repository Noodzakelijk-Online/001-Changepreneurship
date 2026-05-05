"""
BenchmarkData model — Sprint 6 (S6-02).

CEO (Section 13.1): "Platform learns from aggregate outcomes."
CEO (Section 7.2.N): "No individual identification via benchmarks."
CEO (Section 12.x): "User can delete own data — benchmark aggregate survives."

GDPR Design:
  - user_id is NEVER stored in this table
  - cohort_key is a hash of (founder_type + venture_type + phase_id)
  - Individual rows are aggregate statistics, not individual records
  - is_anonymized is always True (enforced in service layer)
"""
from datetime import datetime

from src.models.assessment import db

# Metric types tracked in benchmark
METRIC_PHASE_COMPLETION  = 'PHASE_COMPLETION'
METRIC_BLOCKER_RESOLVED  = 'BLOCKER_RESOLUTION'
METRIC_MENTOR_RESPONSE   = 'MENTOR_RESPONSE'
METRIC_TIME_TO_COMPLETE  = 'TIME_TO_COMPLETE'
METRIC_EVIDENCE_QUALITY  = 'EVIDENCE_QUALITY'
METRIC_ACTION_APPROVED   = 'ACTION_APPROVED'
METRIC_OUTREACH_REPLY    = 'OUTREACH_REPLY'

ALL_METRIC_TYPES = {
    METRIC_PHASE_COMPLETION,
    METRIC_BLOCKER_RESOLVED,
    METRIC_MENTOR_RESPONSE,
    METRIC_TIME_TO_COMPLETE,
    METRIC_EVIDENCE_QUALITY,
    METRIC_ACTION_APPROVED,
    METRIC_OUTREACH_REPLY,
}

# Minimum sample size before benchmark is shown (CEO: no individual identification)
BENCHMARK_MIN_SAMPLE = 10


class BenchmarkData(db.Model):
    """
    Anonymised cohort aggregate benchmark.
    One row per (cohort_key, metric_type) pair.
    Updated incrementally as founders complete phases.
    NEVER contains a user_id column.
    """
    __tablename__ = 'benchmark_data'

    id = db.Column(db.Integer, primary_key=True)

    # cohort_key = SHA-256 of "{founder_type}:{venture_type}:{phase_id}"
    # Ensures no individual identification even via join
    cohort_key = db.Column(db.String(64), nullable=False, index=True)

    # Readable cohort label (stored for transparency, not for re-identification)
    # Format: "TYPE_A:FORPROFIT:self_discovery"
    cohort_label = db.Column(db.String(100), nullable=False)

    metric_type = db.Column(db.String(40), nullable=False)

    # Aggregate value — JSON so any shape is supported
    # e.g. {"mean_days": 14.2, "median_days": 11.0, "p75_days": 21.0}
    metric_value = db.Column(db.JSON, nullable=False, default=dict)

    # Number of data points that went into this aggregate
    sample_size = db.Column(db.Integer, nullable=False, default=0)

    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Always True — enforced in service; never allow False
    is_anonymized = db.Column(db.Boolean, nullable=False, default=True)

    __table_args__ = (
        db.UniqueConstraint('cohort_key', 'metric_type', name='uq_benchmark_cohort_metric'),
    )

    def to_dict(self):
        return {
            'cohort_label':  self.cohort_label,
            'metric_type':   self.metric_type,
            'metric_value':  self.metric_value,
            'sample_size':   self.sample_size,
            'last_updated':  self.last_updated.isoformat() if self.last_updated else None,
        }
