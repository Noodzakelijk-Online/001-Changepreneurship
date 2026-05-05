"""
Sprint 13: Phase 7 Business Prototype Testing API tests.

Tests:
- GET  /phase7/prototype-test   — load (empty + with data)
- PATCH /phase7/prototype-test  — upsert / merge
- GET  /phase7/readiness        — live scale readiness
- POST /phase7/submit           — generate report
- GET  /phase7/report           — latest report
- Auth guards on every endpoint
- phase7_prototype_service unit tests
- User isolation
- Idempotent submit
"""
from datetime import datetime, timedelta
import pytest

from src.models.assessment import db, User, UserSession
from src.models.venture_record import VentureRecord
from src.models.prototype_testing import PrototypeTestData, PrototypeTestResult
from src.services.phase7_prototype_service import (
    assess_scale_readiness,
    generate_report,
    validate_for_submit,
    REQUIRED_FOR_SUBMIT,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_CTR = [0]


def _uniq(p='x'):
    _CTR[0] += 1
    return f"{p}_{_CTR[0]}"


def make_user(session):
    u = User(username=_uniq('u'), email=f"{_uniq('e')}@t.com", password_hash='x'*60)
    session.add(u); session.flush(); return u


def make_session(session, uid):
    token = _uniq('tok')
    s = UserSession(user_id=uid, session_token=token, is_active=True,
                    expires_at=datetime.utcnow() + timedelta(hours=24))
    session.add(s); session.flush(); return token


def make_venture(session, uid):
    v = VentureRecord(user_id=uid, is_active=True, idea_raw='Idea',
                      problem_statement='Problem', target_user_hypothesis='Users',
                      value_proposition='Value', status='DRAFT', assumptions=[])
    session.add(v); session.flush(); return v


def _minimal():
    """Minimal responses that pass validate_for_submit."""
    return {
        'pt-s1-1': 'paying_customers',
        'pt-s1-2': '5',
        'pt-s2-1': '20',
        'pt-s2-2': '4',
        'pt-s3-1': 'fully_delivered',
        'pt-s3-2': 'Minor onboarding friction',
        'pt-s4-1': 'on_plan',
        'pt-s4-2': 'on_budget',
        'pt-s5-1': 'satisfied',
        'pt-s5-2': 'yes_repeat_customers',
        'pt-s6-1': 'completed_most',
        'pt-s6-2': 'adapted_quickly',
    }


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


# ===========================================================================
# SERVICE UNIT TESTS
# ===========================================================================

class TestAssessScaleReadiness:
    def test_returns_required_keys(self):
        result = assess_scale_readiness({})
        assert {'signal', 'score', 'components', 'blockers'} == set(result.keys())

    def test_empty_responses_signal_none(self):
        r = assess_scale_readiness({})
        assert r['signal'] == 'NONE'
        assert r['score'] == 0

    def test_paying_customers_boosts_traction(self):
        r = assess_scale_readiness({'pt-s1-1': 'paying_customers', 'pt-s1-2': '5'})
        assert r['components']['traction'] == 20

    def test_interest_only_low_traction(self):
        r = assess_scale_readiness({'pt-s1-1': 'interest_expressed', 'pt-s1-2': '2'})
        assert r['components']['traction'] <= 8

    def test_high_conversion_rate_scores_full(self):
        r = assess_scale_readiness({'pt-s2-1': '10', 'pt-s2-2': '5'})
        assert r['components']['conversion'] == 15

    def test_zero_conversions_adds_blocker(self):
        r = assess_scale_readiness({'pt-s2-1': '20', 'pt-s2-2': '0'})
        assert r['components']['conversion'] == 0
        assert any('conversion' in b.lower() or 'zero' in b.lower() for b in r['blockers'])

    def test_fully_delivered_scores_full(self):
        r = assess_scale_readiness({'pt-s3-1': 'fully_delivered'})
        assert r['components']['delivery'] == 15

    def test_no_delivery_adds_blocker(self):
        r = assess_scale_readiness({'pt-s3-1': 'not_delivered'})
        assert r['components']['delivery'] == 0
        assert any('delivery' in b.lower() or 'operational' in b.lower() for b in r['blockers'])

    def test_above_plan_revenue_scores_full(self):
        r = assess_scale_readiness({'pt-s4-1': 'above_plan'})
        assert r['components']['financial_reality'] == 20

    def test_no_revenue_adds_blocker(self):
        r = assess_scale_readiness({'pt-s4-1': 'no_revenue_yet'})
        assert any('revenue' in b.lower() for b in r['blockers'])

    def test_over_budget_reduces_financial_score(self):
        base = assess_scale_readiness({'pt-s4-1': 'on_plan'})
        over = assess_scale_readiness({'pt-s4-1': 'on_plan', 'pt-s4-2': 'over_budget'})
        assert over['components']['financial_reality'] < base['components']['financial_reality']

    def test_strong_signal_on_full_responses(self):
        r = assess_scale_readiness(_minimal())
        assert r['signal'] in ('STRONG', 'MODERATE')
        assert r['score'] >= 50

    def test_component_keys_all_present(self):
        r = assess_scale_readiness(_minimal())
        expected = {'traction', 'conversion', 'delivery', 'financial_reality', 'customer_response', 'founder_performance'}
        assert expected == set(r['components'].keys())


class TestGenerateReport:
    def test_generate_returns_required_keys(self):
        report = generate_report({}, _minimal())
        required = {'generated_at', 'venture_name', 'phase', 'scale_readiness',
                    'scale_score', 'decision', 'prototype_summary', 'what_worked',
                    'what_broke', 'what_must_change', 'operational_lessons',
                    'financial_reality', 'founder_analysis', 'next_90_day_plan',
                    'recommended_mode', 'ready_to_scale'}
        assert required.issubset(set(report.keys()))

    def test_phase_is_correct(self):
        report = generate_report({}, _minimal())
        assert report['phase'] == 'business_prototype_testing'

    def test_90_day_plan_has_5_items(self):
        report = generate_report({}, _minimal())
        assert len(report['next_90_day_plan']) == 5

    def test_decision_values_are_valid(self):
        valid = {'SCALE_CAREFULLY', 'FIX_OPERATIONS', 'REVISE_PRICING', 'REVISE_CUSTOMER',
                 'REVISE_PRODUCT', 'SEEK_FUNDING', 'REMAIN_STABLE', 'PIVOT', 'PAUSE', 'STOP'}
        report = generate_report({}, _minimal())
        assert report['decision'] in valid

    def test_stop_decision_on_empty(self):
        report = generate_report({}, {})
        assert report['decision'] == 'STOP'

    def test_venture_name_used_when_provided(self):
        report = generate_report({'venture_name': 'TestVenture'}, _minimal())
        assert report['venture_name'] == 'TestVenture'


class TestValidateForSubmit:
    def test_valid_with_all_required(self):
        ok, msg = validate_for_submit(_minimal())
        assert ok is True
        assert msg == 'OK'

    def test_invalid_with_missing_field(self):
        r = _minimal()
        del r['pt-s1-1']
        ok, msg = validate_for_submit(r)
        assert ok is False
        assert 'pt-s1-1' in msg

    def test_required_ids_exported(self):
        assert 'pt-s1-1' in REQUIRED_FOR_SUBMIT
        assert 'pt-s2-1' in REQUIRED_FOR_SUBMIT
        assert 'pt-s3-1' in REQUIRED_FOR_SUBMIT
        assert 'pt-s4-1' in REQUIRED_FOR_SUBMIT
        assert 'pt-s5-1' in REQUIRED_FOR_SUBMIT


# ===========================================================================
# ENDPOINT TESTS
# ===========================================================================

class TestPhase7AuthGuards:
    def test_get_prototype_no_auth(self, client):
        rv = client.get('/api/v1/phase7/prototype-test')
        assert rv.status_code == 401

    def test_patch_prototype_no_auth(self, client):
        rv = client.patch('/api/v1/phase7/prototype-test', json={'responses': {}})
        assert rv.status_code == 401

    def test_get_readiness_no_auth(self, client):
        rv = client.get('/api/v1/phase7/readiness')
        assert rv.status_code == 401

    def test_submit_no_auth(self, client):
        rv = client.post('/api/v1/phase7/submit')
        assert rv.status_code == 401

    def test_get_report_no_auth(self, client):
        rv = client.get('/api/v1/phase7/report')
        assert rv.status_code == 401


class TestPhase7GetEmpty:
    def test_get_empty_returns_empty_responses(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        rv = client.get('/api/v1/phase7/prototype-test', headers=auth_header(tok))
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['responses'] == {}
        assert data['completed'] is False
        assert data['completion_pct'] == 0


class TestPhase7Upsert:
    def test_patch_saves_responses(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        rv = client.patch('/api/v1/phase7/prototype-test',
                          json={'responses': {'pt-s1-1': 'paying_customers'}},
                          headers=auth_header(tok))
        assert rv.status_code == 200
        assert rv.get_json()['saved'] is True

    def test_patch_merges_existing(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase7/prototype-test',
                     json={'responses': {'pt-s1-1': 'paying_customers'}},
                     headers=auth_header(tok))
        client.patch('/api/v1/phase7/prototype-test',
                     json={'responses': {'pt-s2-1': '10'}},
                     headers=auth_header(tok))
        rv = client.get('/api/v1/phase7/prototype-test', headers=auth_header(tok))
        resp = rv.get_json()['responses']
        assert resp.get('pt-s1-1') == 'paying_customers'
        assert resp.get('pt-s2-1') == '10'

    def test_patch_invalid_responses_type(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        rv = client.patch('/api/v1/phase7/prototype-test',
                          json={'responses': 'notadict'},
                          headers=auth_header(tok))
        assert rv.status_code == 422

    def test_patch_empty_body_ok(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        rv = client.patch('/api/v1/phase7/prototype-test',
                          json={}, headers=auth_header(tok))
        assert rv.status_code == 200


class TestPhase7Readiness:
    def test_readiness_empty_responses(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        rv = client.get('/api/v1/phase7/readiness', headers=auth_header(tok))
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['scale_readiness'] == 'NONE'
        assert data['scale_score'] == 0
        assert data['can_submit'] is False

    def test_readiness_with_data(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase7/prototype-test',
                     json={'responses': _minimal()},
                     headers=auth_header(tok))
        rv = client.get('/api/v1/phase7/readiness', headers=auth_header(tok))
        data = rv.get_json()
        assert data['scale_score'] > 0
        assert data['can_submit'] is True


class TestPhase7Submit:
    def test_submit_no_data_returns_400(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        rv = client.post('/api/v1/phase7/submit', headers=auth_header(tok))
        assert rv.status_code == 400

    def test_submit_incomplete_returns_422(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase7/prototype-test',
                     json={'responses': {'pt-s1-1': 'paying_customers'}},
                     headers=auth_header(tok))
        rv = client.post('/api/v1/phase7/submit', headers=auth_header(tok))
        assert rv.status_code == 422

    def test_submit_creates_report(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase7/prototype-test',
                     json={'responses': _minimal()},
                     headers=auth_header(tok))
        rv = client.post('/api/v1/phase7/submit', headers=auth_header(tok))
        assert rv.status_code == 201
        data = rv.get_json()
        assert data['success'] is True
        assert data['report']['scale_readiness'] in ('STRONG', 'MODERATE', 'WEAK', 'NONE')

    def test_submit_marks_completed(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase7/prototype-test',
                     json={'responses': _minimal()},
                     headers=auth_header(tok))
        client.post('/api/v1/phase7/submit', headers=auth_header(tok))
        rv = client.get('/api/v1/phase7/prototype-test', headers=auth_header(tok))
        assert rv.get_json()['completed'] is True

    def test_submit_idempotent(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase7/prototype-test',
                     json={'responses': _minimal()},
                     headers=auth_header(tok))
        r1 = client.post('/api/v1/phase7/submit', headers=auth_header(tok))
        r2 = client.post('/api/v1/phase7/submit', headers=auth_header(tok))
        assert r1.status_code == 201
        assert r2.status_code == 201

    def test_submit_with_venture(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_venture(db.session, u.id)
            tok = make_session(db.session, u.id)
            db.session.commit()
        client.patch('/api/v1/phase7/prototype-test',
                     json={'responses': _minimal()},
                     headers=auth_header(tok))
        rv = client.post('/api/v1/phase7/submit', headers=auth_header(tok))
        assert rv.status_code == 201


class TestPhase7Report:
    def test_report_empty_before_submit(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        rv = client.get('/api/v1/phase7/report', headers=auth_header(tok))
        assert rv.status_code == 200
        assert rv.get_json()['report'] is None

    def test_report_after_submit(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase7/prototype-test',
                     json={'responses': _minimal()},
                     headers=auth_header(tok))
        client.post('/api/v1/phase7/submit', headers=auth_header(tok))
        rv = client.get('/api/v1/phase7/report', headers=auth_header(tok))
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['report'] is not None
        assert 'result_data' in data['report']


class TestPhase7UserIsolation:
    def test_user_isolation(self, client, app):
        with app.app_context():
            u1 = make_user(db.session); tok1 = make_session(db.session, u1.id)
            u2 = make_user(db.session); tok2 = make_session(db.session, u2.id)
            db.session.commit()
        client.patch('/api/v1/phase7/prototype-test',
                     json={'responses': _minimal()},
                     headers=auth_header(tok1))
        rv = client.get('/api/v1/phase7/prototype-test', headers=auth_header(tok2))
        assert rv.get_json()['responses'] == {}

    def test_report_isolation(self, client, app):
        with app.app_context():
            u1 = make_user(db.session); tok1 = make_session(db.session, u1.id)
            u2 = make_user(db.session); tok2 = make_session(db.session, u2.id)
            db.session.commit()
        client.patch('/api/v1/phase7/prototype-test',
                     json={'responses': _minimal()},
                     headers=auth_header(tok1))
        client.post('/api/v1/phase7/submit', headers=auth_header(tok1))
        rv = client.get('/api/v1/phase7/report', headers=auth_header(tok2))
        assert rv.get_json()['report'] is None
