"""
Sprint 12: Phase 6 Business Development API tests.

Tests:
- GET  /phase6/business-dev     — load (empty + with data)
- PATCH /phase6/business-dev    — upsert / merge
- GET  /phase6/readiness        — live readiness
- POST /phase6/submit           — generate environment
- GET  /phase6/environment      — latest environment
- Auth guards on every endpoint
- Phase6BusinessDevService unit tests
- User isolation
- Idempotent submit
"""
from datetime import datetime, timedelta
import pytest

from src.models.assessment import db, User, UserSession
from src.models.venture_record import VentureRecord
from src.models.business_development import BusinessDevData, VentureEnvironment
from src.services.phase6_business_dev_service import Phase6BusinessDevService


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
    return {
        'bd-s1-1': 'An AI platform that helps founders build faster',
        'bd-s1-2': 'Saves 10 hours per week on planning and documentation',
        'bd-s1-3': 'Early-stage solo founders aged 25-40',
        'bd-s1-4': 'AI-generated first drafts with founder approval',
        'bd-s2-1': 'SUBSCRIPTION',
        'bd-s2-2': '$49/month for basic, $149/month for pro',
        'bd-s2-3': 'Hosting $200/month, AI API $300/month, ops $100/month',
        'bd-s2-4': '6-month runway from savings, targeting break-even at 50 customers',
        'bd-s3-1': 'Direct outreach via LinkedIn to 50 founders in first month',
        'bd-s3-2': 'LinkedIn content, newsletter, and founder communities',
        'bd-s3-3': 'Beta launch in month 2, paid launch in month 3',
        'bd-s3-4': 'No partners identified yet',
        'bd-s4-1': 'Sole trader initially, transition to Ltd at 20k revenue',
        'bd-s4-2': 'Onboarding, AI generation, founder review, export',
        'bd-s4-3': 'Notion for tasks, GitHub for code, Stripe for payments',
        'bd-s4-4': 'Accountant for tax setup, lawyer for ToS review',
        'bd-s5-1': 'AI costs spike, founder burnout, low conversion',
        'bd-s5-2': 'Cost caps on AI, co-founder search, improve onboarding',
        'bd-s5-3': 'Launch beta to 10 users, set up analytics, first support loop',
    }


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


# ===========================================================================
# Service unit tests
# ===========================================================================

class TestPhase6Service:
    svc = Phase6BusinessDevService()

    def test_assess_readiness_full(self):
        result = self.svc.assess_readiness(_minimal())
        assert result['readiness_score'] > 50
        assert result['readiness_level'] in ('HIGH', 'MODERATE')
        assert 'components' in result

    def test_assess_readiness_empty(self):
        result = self.svc.assess_readiness({})
        assert result['readiness_score'] == 0
        assert result['readiness_level'] == 'CRITICAL'
        assert len(result['blockers']) > 0

    def test_component_keys_present(self):
        result = self.svc.assess_readiness(_minimal())
        for key in ('venture_summary', 'financial_model', 'go_to_market',
                    'operations', 'legal_compliance', 'risk_register', 'roadmap'):
            assert key in result['components']

    def test_component_status_values(self):
        result = self.svc.assess_readiness(_minimal())
        for comp in result['components'].values():
            assert comp['status'] in ('COMPLETE', 'PARTIAL', 'MISSING')

    def test_legal_blocker_detected(self):
        resp = {**_minimal(), 'bd-s4-1': 'unclear, unsure what to do'}
        result = self.svc.assess_readiness(resp)
        assert any('legal' in b.lower() or 'tax' in b.lower() for b in result['blockers'])

    def test_generate_environment_structure(self):
        env = self.svc.generate_environment(None, _minimal())
        for key in ('venture_summary', 'financial_model', 'go_to_market',
                    'operations', 'risk_register', 'roadmap',
                    'readiness_score', 'decision', 'decision_rationale'):
            assert key in env

    def test_decision_values(self):
        env = self.svc.generate_environment(None, _minimal())
        assert env['decision'] in (
            'PROCEED_TO_PROTOTYPE', 'REVISE_COMPONENTS',
            'SEEK_PROFESSIONAL_SUPPORT', 'PAUSE_AND_VALIDATE',
        )

    def test_proceed_decision_on_high_score(self):
        env = self.svc.generate_environment(None, _minimal())
        if env['readiness_level'] == 'HIGH' and not env['blockers']:
            assert env['decision'] == 'PROCEED_TO_PROTOTYPE'

    def test_pause_on_empty(self):
        env = self.svc.generate_environment(None, {
            'bd-s1-1': 'x', 'bd-s1-2': 'x', 'bd-s2-1': 'x',
            'bd-s3-1': 'x', 'bd-s4-1': 'x',
        })
        assert env['decision'] in ('PAUSE_AND_VALIDATE', 'REVISE_COMPONENTS')

    def test_validate_ok(self):
        ok, msg = self.svc.validate_for_submit(_minimal())
        assert ok is True
        assert msg == ''

    def test_validate_missing_required(self):
        resp = {**_minimal()}
        del resp['bd-s2-1']
        ok, msg = self.svc.validate_for_submit(resp)
        assert ok is False
        assert 'bd-s2-1' in msg

    def test_operational_ready_field(self):
        env = self.svc.generate_environment(None, _minimal())
        assert isinstance(env['operational_ready'], bool)


# ===========================================================================
# Endpoint tests
# ===========================================================================

class TestPhase6Endpoints:

    # ── Auth guards ──────────────────────────────────────────────────────────

    def test_get_unauth(self, client):
        assert client.get('/api/v1/phase6/business-dev').status_code in (401, 403)

    def test_patch_unauth(self, client):
        assert client.patch('/api/v1/phase6/business-dev',
                            json={'responses': {}}).status_code in (401, 403)

    def test_readiness_unauth(self, client):
        assert client.get('/api/v1/phase6/readiness').status_code in (401, 403)

    def test_submit_unauth(self, client):
        assert client.post('/api/v1/phase6/submit').status_code in (401, 403)

    def test_environment_unauth(self, client):
        assert client.get('/api/v1/phase6/environment').status_code in (401, 403)

    # ── GET empty ────────────────────────────────────────────────────────────

    def test_get_empty(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        r = client.get('/api/v1/phase6/business-dev', headers=auth_header(tok))
        assert r.status_code == 200
        assert r.get_json()['responses'] == {}
        assert r.get_json()['completion_pct'] == 0

    # ── PATCH ────────────────────────────────────────────────────────────────

    def test_patch_saves(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        r = client.patch('/api/v1/phase6/business-dev', headers=auth_header(tok),
                         json={'responses': {'bd-s1-1': 'My venture'}})
        assert r.status_code == 200
        assert r.get_json()['responses']['bd-s1-1'] == 'My venture'

    def test_patch_merges(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase6/business-dev', headers=auth_header(tok),
                     json={'responses': {'bd-s1-1': 'A'}})
        r = client.patch('/api/v1/phase6/business-dev', headers=auth_header(tok),
                         json={'responses': {'bd-s1-2': 'B'}})
        data = r.get_json()
        assert data['responses']['bd-s1-1'] == 'A'
        assert data['responses']['bd-s1-2'] == 'B'

    def test_patch_invalid_type(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        r = client.patch('/api/v1/phase6/business-dev', headers=auth_header(tok),
                         json={'responses': 'bad'})
        assert r.status_code == 422

    def test_patch_completion_pct(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        r = client.patch('/api/v1/phase6/business-dev', headers=auth_header(tok),
                         json={'responses': _minimal()})
        assert r.get_json()['completion_pct'] > 0

    # ── GET readiness ────────────────────────────────────────────────────────

    def test_readiness_empty(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        r = client.get('/api/v1/phase6/readiness', headers=auth_header(tok))
        assert r.status_code == 200
        assert 'readiness_score' in r.get_json()

    def test_readiness_with_responses(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase6/business-dev', headers=auth_header(tok),
                     json={'responses': _minimal()})
        r = client.get('/api/v1/phase6/readiness', headers=auth_header(tok))
        assert r.get_json()['readiness_score'] > 0

    # ── POST submit ──────────────────────────────────────────────────────────

    def test_submit_no_data(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        assert client.post('/api/v1/phase6/submit',
                           headers=auth_header(tok)).status_code == 404

    def test_submit_incomplete(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase6/business-dev', headers=auth_header(tok),
                     json={'responses': {'bd-s1-1': 'partial only'}})
        assert client.post('/api/v1/phase6/submit',
                           headers=auth_header(tok)).status_code == 422

    def test_submit_creates_environment(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase6/business-dev', headers=auth_header(tok),
                     json={'responses': _minimal()})
        r = client.post('/api/v1/phase6/submit', headers=auth_header(tok))
        assert r.status_code == 201
        data = r.get_json()
        assert 'environment_data' in data
        assert data['decision'] in (
            'PROCEED_TO_PROTOTYPE', 'REVISE_COMPONENTS',
            'SEEK_PROFESSIONAL_SUPPORT', 'PAUSE_AND_VALIDATE',
        )

    def test_submit_marks_completed(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase6/business-dev', headers=auth_header(tok),
                     json={'responses': _minimal()})
        client.post('/api/v1/phase6/submit', headers=auth_header(tok))
        r = client.get('/api/v1/phase6/business-dev', headers=auth_header(tok))
        assert r.get_json()['completed'] is True

    def test_submit_idempotent(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase6/business-dev', headers=auth_header(tok),
                     json={'responses': _minimal()})
        r1 = client.post('/api/v1/phase6/submit', headers=auth_header(tok))
        r2 = client.post('/api/v1/phase6/submit', headers=auth_header(tok))
        assert r1.status_code == 201
        assert r2.status_code == 201

    # ── GET environment ──────────────────────────────────────────────────────

    def test_environment_empty(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        r = client.get('/api/v1/phase6/environment', headers=auth_header(tok))
        assert r.status_code == 200
        assert r.get_json()['environment'] is None

    def test_environment_after_submit(self, client, app):
        with app.app_context():
            u = make_user(db.session); tok = make_session(db.session, u.id); db.session.commit()
        client.patch('/api/v1/phase6/business-dev', headers=auth_header(tok),
                     json={'responses': _minimal()})
        client.post('/api/v1/phase6/submit', headers=auth_header(tok))
        r = client.get('/api/v1/phase6/environment', headers=auth_header(tok))
        assert r.status_code == 200
        assert r.get_json()['environment_data'] is not None

    # ── User isolation ───────────────────────────────────────────────────────

    def test_isolation_responses(self, client, app):
        with app.app_context():
            u1 = make_user(db.session); u2 = make_user(db.session)
            t1 = make_session(db.session, u1.id); t2 = make_session(db.session, u2.id)
            db.session.commit()
        client.patch('/api/v1/phase6/business-dev', headers=auth_header(t1),
                     json={'responses': {'bd-s1-1': 'User1 venture'}})
        r = client.get('/api/v1/phase6/business-dev', headers=auth_header(t2))
        assert r.get_json()['responses'] == {}

    def test_isolation_environment(self, client, app):
        with app.app_context():
            u1 = make_user(db.session); u2 = make_user(db.session)
            t1 = make_session(db.session, u1.id); t2 = make_session(db.session, u2.id)
            db.session.commit()
        client.patch('/api/v1/phase6/business-dev', headers=auth_header(t1),
                     json={'responses': _minimal()})
        client.post('/api/v1/phase6/submit', headers=auth_header(t1))
        r = client.get('/api/v1/phase6/environment', headers=auth_header(t2))
        assert r.get_json()['environment'] is None
