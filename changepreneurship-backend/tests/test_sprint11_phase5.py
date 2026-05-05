"""
Sprint 11: Phase 5 Product Concept Testing API tests.

Tests:
- GET  /phase5/concept-tests           — load (empty then with data)
- PATCH /phase5/concept-tests          — upsert responses (merge)
- GET  /phase5/adoption-signal         — live adoption signal
- POST /phase5/submit                  — generate result
- GET  /phase5/result                  — latest result
- Auth guards on every endpoint
- Phase5ConceptService unit tests
- User isolation
- Idempotent submit (multiple submits create multiple results)
"""
from datetime import datetime, timedelta
import pytest

from src.models.assessment import db, User, UserSession
from src.models.venture_record import VentureRecord
from src.models.concept_testing import ConceptTestData, ConceptTestResult
from src.services.phase5_concept_service import (
    Phase5ConceptService, INTEREST_SCORE, ADOPTION_THRESHOLDS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_CTR = [0]


def _uniq(prefix='x'):
    _CTR[0] += 1
    return f"{prefix}_{_CTR[0]}"


def make_user(session, **kwargs):
    u = User(
        username=kwargs.get('username', _uniq('user')),
        email=kwargs.get('email', f"{_uniq('e')}@test.com"),
        password_hash='x' * 60,
    )
    session.add(u)
    session.flush()
    return u


def make_session(session, user_id):
    token = _uniq('tok')
    s = UserSession(
        user_id=user_id,
        session_token=token,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    session.add(s)
    session.flush()
    return token


def make_venture(session, user_id):
    v = VentureRecord(
        user_id=user_id,
        is_active=True,
        idea_raw='Test idea',
        problem_statement='Problem statement',
        target_user_hypothesis='Early founders',
        value_proposition='We solve it fast',
        status='DRAFT',
        assumptions=['Assumption A'],
    )
    session.add(v)
    session.flush()
    return v


def make_concept_data(session, user_id, venture_id=None, responses=None):
    r = ConceptTestData(
        user_id=user_id,
        venture_id=venture_id,
        responses=responses or {},
    )
    session.add(r)
    session.flush()
    return r


def _minimal_responses():
    """Minimum valid set of responses for submit."""
    return {
        'pct-s1-1': 'An AI platform for founders',
        'pct-s1-2': 'Early-stage founders aged 25-40',
        'pct-s1-3': 'Saves 10 hours per week on admin',
        'pct-s1-4': 'At least 3 people ask to join',
        'pct-s2-1': 'User interviews and mockup',
        'pct-s2-2': '10',
        'pct-s2-3': 'LinkedIn and startup events',
        'pct-s2-4': 'Shown a clickable mockup',
        'pct-s3-1': 'Most understood it immediately',
        'pct-s3-2': 'STRONG',
        'pct-s3-3': 'Some worried about price',
        'pct-s3-4': '3 asked for early access',
        'pct-s3-5': '3',
        'pct-s4-1': 'Strong comprehension, genuine desire',
        'pct-s4-2': 'Pricing sensitivity',
        'pct-s4-3': 'MODERATE',
        'pct-s4-4': 'Add a free tier',
    }


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


# ===========================================================================
# Service unit tests
# ===========================================================================

class TestPhase5ConceptService:
    svc = Phase5ConceptService()

    def test_assess_adoption_strong(self):
        resp = {
            'pct-s2-2': '20',
            'pct-s3-2': 'STRONG',
            'pct-s3-5': '8',
            'pct-s4-3': 'STRONG',
        }
        result = self.svc.assess_adoption(resp)
        assert result['adoption_signal'] == 'STRONG'
        assert result['adoption_score'] >= ADOPTION_THRESHOLDS['STRONG']

    def test_assess_adoption_moderate(self):
        resp = {
            'pct-s2-2': '10',
            'pct-s3-2': 'MODERATE',
            'pct-s3-5': '1',
            'pct-s4-3': 'MODERATE',
        }
        result = self.svc.assess_adoption(resp)
        assert result['adoption_signal'] == 'MODERATE'

    def test_assess_adoption_none_on_negative(self):
        resp = {
            'pct-s2-2': '5',
            'pct-s3-2': 'NEGATIVE',
            'pct-s3-5': '0',
            'pct-s4-3': 'VERY_WEAK',
        }
        result = self.svc.assess_adoption(resp)
        assert result['adoption_signal'] == 'NONE'
        assert 'No adoption signal' in result['blockers'][-1]

    def test_conversion_rate_calculated(self):
        resp = {'pct-s2-2': '10', 'pct-s3-2': 'MODERATE', 'pct-s3-5': '5'}
        result = self.svc.assess_adoption(resp)
        assert result['conversion_rate'] == pytest.approx(0.5)

    def test_no_contacts_no_crash(self):
        result = self.svc.assess_adoption({})
        assert result['adoption_signal'] in ('NONE', 'WEAK')
        assert result['conversion_rate'] is None

    def test_pricing_blocker_detected(self):
        resp = {
            'pct-s2-2': '5',
            'pct-s3-2': 'POLITE',
            'pct-s3-3': 'They said it was too expensive',
            'pct-s3-5': '0',
        }
        result = self.svc.assess_adoption(resp)
        assert any('Pricing' in b for b in result['blockers'])

    def test_complexity_blocker_detected(self):
        resp = {
            'pct-s2-2': '5',
            'pct-s3-2': 'CONFUSED',
            'pct-s3-3': 'They found it too complex',
            'pct-s3-5': '0',
        }
        result = self.svc.assess_adoption(resp)
        assert any('Complexity' in b or 'Comprehension' in b for b in result['blockers'])

    def test_generate_result_structure(self):
        result = self.svc.generate_result(None, _minimal_responses())
        assert 'test_design' in result
        assert 'response_summary' in result
        assert 'adoption_signal' in result
        assert 'decision' in result
        assert 'decision_rationale' in result
        assert result['decision'] in ('PROCEED', 'REVISE', 'RETEST', 'PIVOT', 'STOP')

    def test_generate_result_proceed_on_strong(self):
        resp = _minimal_responses()
        resp['pct-s3-2'] = 'STRONG'
        resp['pct-s3-5'] = '8'
        resp['pct-s4-3'] = 'STRONG'
        result = self.svc.generate_result(None, resp)
        assert result['decision'] == 'PROCEED'
        assert result['ready_for_business_dev'] is True

    def test_generate_result_pivot_on_none(self):
        resp = _minimal_responses()
        resp['pct-s3-2'] = 'NEGATIVE'
        resp['pct-s3-5'] = '0'
        resp['pct-s4-3'] = 'VERY_WEAK'
        result = self.svc.generate_result(None, resp)
        assert result['decision'] in ('PIVOT', 'STOP')
        assert result['ready_for_business_dev'] is False

    def test_validate_for_submit_ok(self):
        ok, msg = self.svc.validate_for_submit(_minimal_responses())
        assert ok is True
        assert msg == ''

    def test_validate_for_submit_missing_required(self):
        resp = _minimal_responses()
        del resp['pct-s1-1']
        ok, msg = self.svc.validate_for_submit(resp)
        assert ok is False
        assert 'pct-s1-1' in msg

    def test_validate_for_submit_zero_contacts(self):
        resp = _minimal_responses()
        resp['pct-s2-2'] = '0'
        ok, msg = self.svc.validate_for_submit(resp)
        assert ok is False
        assert 'Contact count' in msg


# ===========================================================================
# Endpoint tests
# ===========================================================================

class TestPhase5Endpoints:

    # ── Auth guards ──────────────────────────────────────────────────────────

    def test_get_concept_tests_unauthenticated(self, client):
        r = client.get('/api/v1/phase5/concept-tests')
        assert r.status_code in (401, 403)

    def test_patch_concept_tests_unauthenticated(self, client):
        r = client.patch('/api/v1/phase5/concept-tests', json={'responses': {}})
        assert r.status_code in (401, 403)

    def test_adoption_signal_unauthenticated(self, client):
        r = client.get('/api/v1/phase5/adoption-signal')
        assert r.status_code in (401, 403)

    def test_submit_unauthenticated(self, client):
        r = client.post('/api/v1/phase5/submit')
        assert r.status_code in (401, 403)

    def test_result_unauthenticated(self, client):
        r = client.get('/api/v1/phase5/result')
        assert r.status_code in (401, 403)

    # ── GET concept-tests (empty) ────────────────────────────────────────────

    def test_get_concept_tests_empty(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        r = client.get('/api/v1/phase5/concept-tests',
                       headers=auth_header(token))
        assert r.status_code == 200
        data = r.get_json()
        assert data['responses'] == {}
        assert data['completed'] is False
        assert data['completion_pct'] == 0

    # ── PATCH concept-tests ──────────────────────────────────────────────────

    def test_patch_concept_tests_saves(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        r = client.patch('/api/v1/phase5/concept-tests',
                         headers=auth_header(token),
                         json={'responses': {'pct-s1-1': 'My concept'}})
        assert r.status_code == 200
        assert r.get_json()['responses']['pct-s1-1'] == 'My concept'

    def test_patch_concept_tests_merges(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        client.patch('/api/v1/phase5/concept-tests',
                     headers=auth_header(token),
                     json={'responses': {'pct-s1-1': 'First'}})
        r = client.patch('/api/v1/phase5/concept-tests',
                         headers=auth_header(token),
                         json={'responses': {'pct-s1-2': 'Second'}})
        data = r.get_json()
        assert data['responses']['pct-s1-1'] == 'First'
        assert data['responses']['pct-s1-2'] == 'Second'

    def test_patch_invalid_responses_type(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        r = client.patch('/api/v1/phase5/concept-tests',
                         headers=auth_header(token),
                         json={'responses': 'not a dict'})
        assert r.status_code == 422

    def test_patch_returns_completion_pct(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        resp = _minimal_responses()
        r = client.patch('/api/v1/phase5/concept-tests',
                         headers=auth_header(token),
                         json={'responses': resp})
        assert r.status_code == 200
        assert r.get_json()['completion_pct'] > 0

    # ── GET adoption-signal ──────────────────────────────────────────────────

    def test_adoption_signal_empty_responses(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        r = client.get('/api/v1/phase5/adoption-signal',
                       headers=auth_header(token))
        assert r.status_code == 200
        data = r.get_json()
        assert 'adoption_signal' in data

    def test_adoption_signal_reflects_responses(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        client.patch('/api/v1/phase5/concept-tests',
                     headers=auth_header(token),
                     json={'responses': {'pct-s3-2': 'STRONG', 'pct-s2-2': '20',
                                         'pct-s3-5': '10', 'pct-s4-3': 'STRONG'}})
        r = client.get('/api/v1/phase5/adoption-signal', headers=auth_header(token))
        assert r.get_json()['adoption_signal'] == 'STRONG'

    # ── POST submit ──────────────────────────────────────────────────────────

    def test_submit_no_data_returns_404(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        r = client.post('/api/v1/phase5/submit', headers=auth_header(token))
        assert r.status_code == 404

    def test_submit_missing_required_returns_422(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        # Save incomplete responses
        client.patch('/api/v1/phase5/concept-tests',
                     headers=auth_header(token),
                     json={'responses': {'pct-s1-1': 'Something'}})
        r = client.post('/api/v1/phase5/submit', headers=auth_header(token))
        assert r.status_code == 422

    def test_submit_full_creates_result(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        client.patch('/api/v1/phase5/concept-tests',
                     headers=auth_header(token),
                     json={'responses': _minimal_responses()})
        r = client.post('/api/v1/phase5/submit', headers=auth_header(token))
        assert r.status_code == 201
        data = r.get_json()
        assert 'result_data' in data
        assert data['adoption_signal'] is not None
        assert data['decision'] in ('PROCEED', 'REVISE', 'RETEST', 'PIVOT', 'STOP')

    def test_submit_marks_data_completed(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        client.patch('/api/v1/phase5/concept-tests',
                     headers=auth_header(token),
                     json={'responses': _minimal_responses()})
        client.post('/api/v1/phase5/submit', headers=auth_header(token))
        r = client.get('/api/v1/phase5/concept-tests', headers=auth_header(token))
        assert r.get_json()['completed'] is True

    def test_submit_idempotent(self, client, app):
        """Multiple submits should all succeed (latest wins on GET)."""
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        client.patch('/api/v1/phase5/concept-tests',
                     headers=auth_header(token),
                     json={'responses': _minimal_responses()})
        r1 = client.post('/api/v1/phase5/submit', headers=auth_header(token))
        r2 = client.post('/api/v1/phase5/submit', headers=auth_header(token))
        assert r1.status_code == 201
        assert r2.status_code == 201

    # ── GET result ───────────────────────────────────────────────────────────

    def test_get_result_empty(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        r = client.get('/api/v1/phase5/result', headers=auth_header(token))
        assert r.status_code == 200
        assert r.get_json()['result'] is None

    def test_get_result_after_submit(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            token = make_session(db.session, u.id)
            db.session.commit()
        client.patch('/api/v1/phase5/concept-tests',
                     headers=auth_header(token),
                     json={'responses': _minimal_responses()})
        client.post('/api/v1/phase5/submit', headers=auth_header(token))
        r = client.get('/api/v1/phase5/result', headers=auth_header(token))
        assert r.status_code == 200
        data = r.get_json()
        assert 'result_data' in data
        assert data['decision'] in ('PROCEED', 'REVISE', 'RETEST', 'PIVOT', 'STOP')

    # ── User isolation ───────────────────────────────────────────────────────

    def test_user_isolation_responses(self, client, app):
        with app.app_context():
            u1 = make_user(db.session)
            u2 = make_user(db.session)
            tok1 = make_session(db.session, u1.id)
            tok2 = make_session(db.session, u2.id)
            db.session.commit()
        client.patch('/api/v1/phase5/concept-tests',
                     headers=auth_header(tok1),
                     json={'responses': {'pct-s1-1': 'User1 concept'}})
        r = client.get('/api/v1/phase5/concept-tests', headers=auth_header(tok2))
        assert r.get_json()['responses'] == {}

    def test_user_isolation_result(self, client, app):
        with app.app_context():
            u1 = make_user(db.session)
            u2 = make_user(db.session)
            tok1 = make_session(db.session, u1.id)
            tok2 = make_session(db.session, u2.id)
            db.session.commit()
        client.patch('/api/v1/phase5/concept-tests',
                     headers=auth_header(tok1),
                     json={'responses': _minimal_responses()})
        client.post('/api/v1/phase5/submit', headers=auth_header(tok1))
        r = client.get('/api/v1/phase5/result', headers=auth_header(tok2))
        assert r.get_json()['result'] is None
