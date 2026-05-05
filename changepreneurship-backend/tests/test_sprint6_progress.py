"""
Progress Dashboard + Benchmark API tests — Sprint 6 (S6-06)
Tests: dashboard endpoints, phase status logic, benchmark GDPR,
       blocker display, auth guards, benchmark opt-out.
"""
import hashlib
import pytest
from datetime import datetime, timedelta

from src.models.assessment import db, User, UserSession, Assessment, AssessmentResponse, EntrepreneurProfile
from src.models.user_action import UserAction, BlockerEvent
from src.models.benchmark_data import BenchmarkData, BENCHMARK_MIN_SAMPLE, ALL_METRIC_TYPES
from src.services.progress_dashboard_service import (
    ProgressDashboardService, PHASES, PHASE_IDS,
)
from src.services.benchmark_intelligence_service import BenchmarkIntelligenceService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_user(session, username, email):
    u = User(username=username, email=email, password_hash='x' * 60)
    session.add(u)
    session.flush()
    return u


def make_session(session, user_id, token):
    s = UserSession(
        user_id=user_id,
        session_token=token,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    session.add(s)
    session.flush()
    return s


def make_assessment(session, user_id, phase_id, phase_name, progress=0.0, completed=False):
    a = Assessment(
        user_id=user_id,
        phase_id=phase_id,
        phase_name=phase_name,
        progress_percentage=progress,
        is_completed=completed,
        completed_at=datetime.utcnow() if completed else None,
    )
    session.add(a)
    session.flush()
    return a


def auth(token):
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


# ---------------------------------------------------------------------------
# ProgressDashboardService unit tests
# ---------------------------------------------------------------------------
class TestProgressDashboardService:

    def test_phase_order_has_7_phases(self):
        assert len(PHASES) == 7

    def test_all_phase_ids_present(self):
        expected = {
            'self_discovery', 'idea_discovery', 'market_research',
            'business_pillars', 'product_concept_testing', 'business_development',
            'business_prototype_testing',
        }
        assert set(PHASE_IDS) == expected

    def test_empty_user_first_phase_not_locked(self, app):
        svc = ProgressDashboardService()
        with app.app_context():
            u = make_user(db.session, 'dash_empty', 'dash_empty@test.com')
            db.session.commit()
            phases = svc._get_phase_statuses(u.id)

        assert phases[0]['status'] == 'NOT_STARTED'   # Phase 1 always unlocked
        assert phases[1]['status'] == 'LOCKED'         # Phase 2 locked without Phase 1

    def test_completed_phase1_unlocks_phase2(self, app):
        svc = ProgressDashboardService()
        with app.app_context():
            u = make_user(db.session, 'dash_p1', 'dash_p1@test.com')
            make_assessment(db.session, u.id, 'self_discovery', 'Self Discovery Assessment',
                            progress=100.0, completed=True)
            db.session.commit()
            phases = svc._get_phase_statuses(u.id)

        assert phases[0]['status'] == 'COMPLETED'
        assert phases[1]['status'] == 'NOT_STARTED'    # unlocked
        assert phases[2]['status'] == 'LOCKED'

    def test_in_progress_phase_detected(self, app):
        svc = ProgressDashboardService()
        with app.app_context():
            u = make_user(db.session, 'dash_ip', 'dash_ip@test.com')
            make_assessment(db.session, u.id, 'self_discovery', 'Self Discovery Assessment',
                            progress=60.0, completed=False)
            db.session.commit()
            phases = svc._get_phase_statuses(u.id)

        assert phases[0]['status'] == 'IN_PROGRESS'
        assert phases[0]['progress_percentage'] == 60.0

    def test_compute_stats_all_locked(self, app):
        svc = ProgressDashboardService()
        with app.app_context():
            u = make_user(db.session, 'dash_stats', 'dash_stats@test.com')
            db.session.commit()
            phases = svc._get_phase_statuses(u.id)
            stats = svc._compute_stats(phases)

        assert stats['total_phases'] == 7
        assert stats['completed_phases'] == 0
        assert stats['locked_phases'] == 6    # phases 2-7 locked
        assert stats['overall_progress_pct'] == 0.0

    def test_compute_stats_all_completed(self, app):
        svc = ProgressDashboardService()
        with app.app_context():
            u = make_user(db.session, 'dash_done', 'dash_done@test.com')
            for phase in PHASES:
                make_assessment(db.session, u.id, phase['id'], phase['name'],
                                progress=100.0, completed=True)
            db.session.commit()
            phases = svc._get_phase_statuses(u.id)
            stats = svc._compute_stats(phases)

        assert stats['completed_phases'] == 7
        assert stats['overall_progress_pct'] == 100.0

    def test_next_recommended_action_empty_user(self, app):
        svc = ProgressDashboardService()
        with app.app_context():
            u = make_user(db.session, 'dash_next', 'dash_next@test.com')
            db.session.commit()
            action = svc.get_next_recommended_action(u.id)

        # Should point to Phase 1
        assert action['phase_id'] == 'self_discovery'
        assert action['priority'] == 'NORMAL'

    def test_next_recommended_action_in_progress(self, app):
        svc = ProgressDashboardService()
        with app.app_context():
            u = make_user(db.session, 'dash_inprog', 'dash_inprog@test.com')
            make_assessment(db.session, u.id, 'self_discovery', 'Self Discovery Assessment',
                            progress=40.0, completed=False)
            db.session.commit()
            action = svc.get_next_recommended_action(u.id)

        assert action['phase_id'] == 'self_discovery'
        assert action['priority'] == 'HIGH'

    def test_get_dashboard_returns_all_keys(self, app):
        svc = ProgressDashboardService()
        with app.app_context():
            u = make_user(db.session, 'dash_full', 'dash_full@test.com')
            db.session.commit()
            data = svc.get_user_dashboard(u.id)

        expected_keys = {
            'current_phase', 'phases', 'recommended_next_action',
            'pending_items', 'recent_outcomes', 'active_blockers',
            'venture_summary', 'stats', 'generated_at',
        }
        assert expected_keys.issubset(data.keys())


# ---------------------------------------------------------------------------
# Progress API endpoint tests
# ---------------------------------------------------------------------------
class TestProgressAPI:

    def test_dashboard_requires_auth(self, client):
        resp = client.get('/api/v1/progress/dashboard')
        assert resp.status_code == 401

    def test_phases_requires_auth(self, client):
        resp = client.get('/api/v1/progress/phases')
        assert resp.status_code == 401

    def test_next_action_requires_auth(self, client):
        resp = client.get('/api/v1/progress/next-action')
        assert resp.status_code == 401

    def test_blockers_requires_auth(self, client):
        resp = client.get('/api/v1/progress/blockers')
        assert resp.status_code == 401

    def test_dashboard_authenticated(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'api_dash', 'api_dash@test.com')
            make_session(db.session, u.id, 'api-dash-tok')
            db.session.commit()

        resp = client.get('/api/v1/progress/dashboard', headers=auth('api-dash-tok'))
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'dashboard' in data
        assert 'phases' in data['dashboard']
        assert len(data['dashboard']['phases']) == 7

    def test_phases_authenticated(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'api_ph', 'api_ph@test.com')
            make_session(db.session, u.id, 'api-ph-tok')
            make_assessment(db.session, u.id, 'self_discovery', 'Self Discovery Assessment',
                            progress=100.0, completed=True)
            db.session.commit()

        resp = client.get('/api/v1/progress/phases', headers=auth('api-ph-tok'))
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'phases' in data
        assert data['phases'][0]['status'] == 'COMPLETED'
        assert data['phases'][1]['status'] == 'NOT_STARTED'

    def test_next_action_authenticated(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'api_na', 'api_na@test.com')
            make_session(db.session, u.id, 'api-na-tok')
            db.session.commit()

        resp = client.get('/api/v1/progress/next-action', headers=auth('api-na-tok'))
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'next_action' in data
        assert 'action' in data['next_action']
        assert 'priority' in data['next_action']

    def test_blockers_returns_empty_for_clean_user(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'api_bl', 'api_bl@test.com')
            make_session(db.session, u.id, 'api-bl-tok')
            db.session.commit()

        resp = client.get('/api/v1/progress/blockers', headers=auth('api-bl-tok'))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['count'] == 0

    def test_blockers_returns_active_blocker(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'api_blk', 'api_blk@test.com')
            make_session(db.session, u.id, 'api-blk-tok')
            blocker = BlockerEvent(
                user_id=u.id,
                blocker_type='LOW_RUNWAY',
                severity_level=4,
                dimension='financial_readiness',
                unlock_condition='Secure at least 3 months of financial runway',
                triggered_at=datetime.utcnow(),
                resolved_at=None,
            )
            db.session.add(blocker)
            db.session.commit()

        resp = client.get('/api/v1/progress/blockers', headers=auth('api-blk-tok'))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['count'] == 1
        assert data['blockers'][0]['type'] == 'LOW_RUNWAY'
        assert data['blockers'][0]['level'] == 4


# ---------------------------------------------------------------------------
# Benchmark tests — GDPR / anonymisation / min sample
# ---------------------------------------------------------------------------
class TestBenchmarkIntelligence:

    def test_cohort_key_is_deterministic(self):
        svc = BenchmarkIntelligenceService()
        k1 = svc._build_cohort_key('TYPE_A', 'FORPROFIT', 'self_discovery')
        k2 = svc._build_cohort_key('TYPE_A', 'FORPROFIT', 'self_discovery')
        assert k1 == k2

    def test_cohort_key_is_not_reversible(self):
        svc = BenchmarkIntelligenceService()
        key = svc._build_cohort_key('TYPE_A', 'FORPROFIT', 'self_discovery')
        # Key is SHA-256 hex — 64 chars
        assert len(key) == 64
        assert 'TYPE_A' not in key
        assert 'FORPROFIT' not in key

    def test_record_outcome_stores_no_user_id(self, app):
        svc = BenchmarkIntelligenceService()
        with app.app_context():
            u = make_user(db.session, 'bench_u1', 'bench_u1@test.com')
            db.session.commit()

            svc.record_outcome(
                user_id=u.id,
                metric_type='PHASE_COMPLETION',
                metric_value={'completion_rate_pct': 80.0},
                founder_type='TYPE_A',
                venture_type='FORPROFIT',
                phase_id='self_discovery',
            )

            rows = BenchmarkData.query.all()
            # No row should have user_id column (it doesn't exist in model)
            assert all(not hasattr(row, 'user_id') for row in rows)
            assert len(rows) == 1

    def test_benchmark_not_shown_below_min_sample(self, app):
        svc = BenchmarkIntelligenceService()
        with app.app_context():
            u = make_user(db.session, 'bench_min', 'bench_min@test.com')
            db.session.commit()

            # Record fewer than BENCHMARK_MIN_SAMPLE outcomes
            for i in range(BENCHMARK_MIN_SAMPLE - 1):
                svc.record_outcome(
                    user_id=u.id,
                    metric_type='TIME_TO_COMPLETE',
                    metric_value={'median_days': float(10 + i)},
                    founder_type='TYPE_B',
                    venture_type='SOCIAL',
                    phase_id='idea_discovery',
                )

            result = svc.get_cohort_benchmark('SOCIAL', 'idea_discovery', 'TIME_TO_COMPLETE', 'TYPE_B')
            assert result is None  # Below min sample

    def test_benchmark_shown_at_min_sample(self, app):
        svc = BenchmarkIntelligenceService()
        with app.app_context():
            u = make_user(db.session, 'bench_exact', 'bench_exact@test.com')
            db.session.commit()

            for _ in range(BENCHMARK_MIN_SAMPLE):
                svc.record_outcome(
                    user_id=u.id,
                    metric_type='PHASE_COMPLETION',
                    metric_value={'completion_rate_pct': 75.0},
                    founder_type='TYPE_C',
                    venture_type='NONPROFIT',
                    phase_id='market_research',
                )

            result = svc.get_cohort_benchmark('NONPROFIT', 'market_research', 'PHASE_COMPLETION', 'TYPE_C')
            assert result is not None
            assert result['sample_size'] == BENCHMARK_MIN_SAMPLE

    def test_benchmark_message_includes_sample_size(self, app):
        svc = BenchmarkIntelligenceService()
        with app.app_context():
            u = make_user(db.session, 'bench_msg', 'bench_msg@test.com')
            db.session.commit()

            for _ in range(BENCHMARK_MIN_SAMPLE):
                svc.record_outcome(
                    user_id=u.id,
                    metric_type='MENTOR_RESPONSE',
                    metric_value={'mean_attempts': 3.0},
                    founder_type='TYPE_D',
                    venture_type='DEEPTECH',
                    phase_id='business_pillars',
                )

            msg = svc.get_personalized_benchmark_message(
                user_id=u.id,
                metric_type='MENTOR_RESPONSE',
                founder_type='TYPE_D',
                venture_type='DEEPTECH',
                phase_id='business_pillars',
            )
            assert msg is not None
            assert str(BENCHMARK_MIN_SAMPLE) in msg   # transparency: "Based on 10 founders"

    def test_benchmark_message_none_below_min(self, app):
        svc = BenchmarkIntelligenceService()
        with app.app_context():
            u = make_user(db.session, 'bench_none', 'bench_none@test.com')
            db.session.commit()

            msg = svc.get_personalized_benchmark_message(
                user_id=u.id,
                metric_type='PHASE_COMPLETION',
                founder_type='TYPE_E',
                venture_type='HYBRID',
                phase_id='product_concept_testing',
            )
            assert msg is None

    def test_invalid_metric_type_rejected(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'bench_bad', 'bench_bad@test.com')
            make_session(db.session, u.id, 'bench-bad-tok')
            db.session.commit()

        resp = client.post(
            '/api/v1/benchmark/outcome',
            headers=auth('bench-bad-tok'),
            json={'metric_type': 'INVALID_METRIC', 'metric_value': {}},
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'valid_types' in data

    def test_benchmark_outcome_requires_auth(self, client):
        resp = client.post('/api/v1/benchmark/outcome', json={})
        assert resp.status_code == 401

    def test_benchmark_insight_requires_auth(self, client):
        resp = client.get('/api/v1/benchmark/insight?metric_type=PHASE_COMPLETION')
        assert resp.status_code == 401

    def test_benchmark_outcome_authenticated_records(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'bench_ok', 'bench_ok@test.com')
            make_session(db.session, u.id, 'bench-ok-tok')
            db.session.commit()

        resp = client.post(
            '/api/v1/benchmark/outcome',
            headers=auth('bench-ok-tok'),
            json={
                'metric_type':  'PHASE_COMPLETION',
                'metric_value': {'completion_rate_pct': 70.0},
                'founder_type': 'TYPE_A',
                'venture_type': 'FORPROFIT',
                'phase_id':     'self_discovery',
            },
        )
        assert resp.status_code == 201
        assert resp.get_json()['recorded'] is True

    def test_merge_metrics_updates_running_average(self):
        svc = BenchmarkIntelligenceService()
        existing = {'median_days': 10.0, 'completion_rate_pct': 80.0}
        new_val  = {'median_days': 20.0, 'completion_rate_pct': 60.0}
        merged   = svc._merge_metrics(existing, new_val, old_sample=1)
        # (10 * 1 + 20) / 2 = 15
        assert merged['median_days'] == 15.0
        # (80 * 1 + 60) / 2 = 70
        assert merged['completion_rate_pct'] == 70.0
