"""
Sprint 10: Phase 4 Business Pillars API tests.

Tests:
- GET  /phase4/pillars          — load (empty then with data)
- PATCH /phase4/pillars         — upsert one or more pillar fields
- GET  /phase4/coherence        — coherence assessment
- POST /phase4/submit           — generate blueprint
- GET  /phase4/blueprint        — latest blueprint
- Auth guards on every endpoint
- Phase4PillarsService unit tests
"""
from datetime import datetime, timedelta
import pytest

from src.models.assessment import db, User, UserSession
from src.models.venture_record import VentureRecord
from src.models.business_pillars import BusinessPillarsData, BusinessPillarsBlueprint
from src.services.phase4_pillars_service import Phase4PillarsService, PILLAR_KEYS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_COUNTER = [0]


def _uniq(prefix):
    _COUNTER[0] += 1
    return f"{prefix}_{_COUNTER[0]}"


def make_user(session, *, username=None, email=None):
    u = User(
        username=username or _uniq('user'),
        email=email or f"{_uniq('u')}@test.com",
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


def make_venture(session, user_id, **kwargs):
    v = VentureRecord(
        user_id=user_id,
        is_active=True,
        idea_raw='Test idea',
        problem_statement='Problem statement',
        target_user_hypothesis='Early founders',
        value_proposition='We solve it fast',
        status='DRAFT',
        assumptions=['Assumption A'],
        **kwargs,
    )
    session.add(v)
    session.flush()
    return v


def make_pillars(session, user_id, venture_id=None, pillars=None):
    record = BusinessPillarsData(
        user_id=user_id,
        venture_id=venture_id,
        pillars=pillars or {},
    )
    session.add(record)
    session.flush()
    return record


def auth(token):
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


# ---------------------------------------------------------------------------
# Phase4PillarsService unit tests
# ---------------------------------------------------------------------------
class TestPhase4PillarsService:

    def test_assess_coherence_empty_returns_score_zero(self):
        svc = Phase4PillarsService()
        result = svc.assess_coherence({})
        assert result['coherence_score'] == 0
        assert result['is_coherent'] is False
        assert result['filled_count'] == 0

    def test_assess_coherence_all_pillars_filled(self):
        svc = Phase4PillarsService()
        pillars = {k: f'Value for {k}' for k in PILLAR_KEYS}
        result = svc.assess_coherence(pillars)
        assert result['coherence_score'] == 100
        assert result['is_coherent'] is True
        assert result['gaps'] == []
        assert result['filled_count'] == len(PILLAR_KEYS)

    def test_assess_coherence_critical_missing_blocks(self):
        svc = Phase4PillarsService()
        # Fill all EXCEPT revenue_model (critical)
        pillars = {k: f'Value for {k}' for k in PILLAR_KEYS if k != 'revenue_model'}
        result = svc.assess_coherence(pillars)
        assert result['is_coherent'] is False
        assert 'revenue_model' in result['critical_missing']

    def test_assess_coherence_recommendation_proceed(self):
        svc = Phase4PillarsService()
        pillars = {k: 'text' for k in PILLAR_KEYS}
        result = svc.assess_coherence(pillars)
        assert result['recommendation'] == 'PROCEED_TO_PHASE5'

    def test_validate_pillar_update_valid(self):
        svc = Phase4PillarsService()
        ok, err = svc.validate_pillar_update('value_proposition', 'A great value')
        assert ok is True
        assert err == ''

    def test_validate_pillar_update_invalid_key(self):
        svc = Phase4PillarsService()
        ok, err = svc.validate_pillar_update('unknown_key', 'some value')
        assert ok is False
        assert 'unknown_key' in err

    def test_validate_pillar_update_too_long(self):
        svc = Phase4PillarsService()
        ok, err = svc.validate_pillar_update('value_proposition', 'x' * 5001)
        assert ok is False
        assert 'long' in err.lower()

    def test_generate_blueprint_returns_required_fields(self):
        svc = Phase4PillarsService()
        venture = type('V', (), {
            'id': 1,
            'problem_statement': 'Problem',
            'target_user_hypothesis': 'Founders',
            'value_proposition': 'Solution',
        })()
        pillars = {k: f'Content for {k}' for k in PILLAR_KEYS}
        blueprint = svc.generate_blueprint(
            venture_record=venture,
            pillars=pillars,
            market_data={'pain_intensity': 'HIGH', 'willingness_to_pay': True},
            mvr={'validity_score': 80, 'final_recommendation': 'PROCEED_TO_PHASE4'},
        )
        assert 'coherence_score' in blueprint
        assert 'is_coherent' in blueprint
        assert 'ready_for_concept_testing' in blueprint
        assert 'recommendation_for_concept_testing' in blueprint
        assert blueprint['is_coherent'] is True
        assert blueprint['ready_for_concept_testing'] is True

    def test_generate_blueprint_no_venture(self):
        svc = Phase4PillarsService()
        blueprint = svc.generate_blueprint(
            venture_record=None,
            pillars={},
            market_data=None,
            mvr=None,
        )
        assert blueprint['venture_id'] is None
        assert blueprint['is_coherent'] is False


# ---------------------------------------------------------------------------
# GET /api/v1/phase4/pillars
# ---------------------------------------------------------------------------
class TestPhase4GetPillars:

    def test_unauthenticated_returns_401(self, client, app):
        resp = client.get('/api/v1/phase4/pillars')
        assert resp.status_code == 401

    def test_empty_returns_empty_dict(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            db.session.commit()

        resp = client.get('/api/v1/phase4/pillars', headers=auth(tok))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['pillars'] == {}
        assert data['completed'] is False
        assert data['completion_pct'] == 0

    def test_returns_existing_pillars(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_pillars(db.session, u.id, pillars={'value_proposition': 'Great VP'})
            db.session.commit()

        resp = client.get('/api/v1/phase4/pillars', headers=auth(tok))
        assert resp.status_code == 200
        assert resp.get_json()['pillars']['value_proposition'] == 'Great VP'


# ---------------------------------------------------------------------------
# PATCH /api/v1/phase4/pillars
# ---------------------------------------------------------------------------
class TestPhase4UpdatePillars:

    def test_unauthenticated_returns_401(self, client, app):
        resp = client.patch('/api/v1/phase4/pillars', json={'value_proposition': 'x'})
        assert resp.status_code == 401

    def test_save_single_pillar(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        resp = client.patch('/api/v1/phase4/pillars', json={
            'value_proposition': 'We help founders validate ideas cheaply.',
        }, headers=auth(tok))
        assert resp.status_code == 200
        assert resp.get_json()['pillars']['value_proposition'] == 'We help founders validate ideas cheaply.'

    def test_idempotent_upsert(self, client, app):
        """PATCH twice — should not create two records."""
        with app.app_context():
            u = make_user(db.session)
            user_id = u.id
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        client.patch('/api/v1/phase4/pillars', json={'revenue_model': 'SUBSCRIPTION'}, headers=auth(tok))
        client.patch('/api/v1/phase4/pillars', json={'revenue_model': 'FREEMIUM'}, headers=auth(tok))

        with app.app_context():
            count = BusinessPillarsData.query.filter_by(user_id=user_id).count()
            record = BusinessPillarsData.query.filter_by(user_id=user_id).first()

        assert count == 1
        assert record.pillars['revenue_model'] == 'FREEMIUM'

    def test_invalid_pillar_key_returns_400(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        resp = client.patch('/api/v1/phase4/pillars', json={
            'not_a_real_pillar': 'some value',
        }, headers=auth(tok))
        assert resp.status_code == 400

    def test_accepts_section_responses(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        resp = client.patch('/api/v1/phase4/pillars', json={
            'section_responses': {
                'business-model': {'revenue-model': 'subscription'},
            },
        }, headers=auth(tok))
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /api/v1/phase4/coherence
# ---------------------------------------------------------------------------
class TestPhase4Coherence:

    def test_unauthenticated_returns_401(self, client, app):
        resp = client.get('/api/v1/phase4/coherence')
        assert resp.status_code == 401

    def test_empty_pillars_low_coherence(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            db.session.commit()

        resp = client.get('/api/v1/phase4/coherence', headers=auth(tok))
        assert resp.status_code == 200
        assert resp.get_json()['coherence']['coherence_score'] == 0

    def test_full_pillars_high_coherence(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_pillars(db.session, u.id, pillars={k: f'text for {k}' for k in PILLAR_KEYS})
            db.session.commit()

        resp = client.get('/api/v1/phase4/coherence', headers=auth(tok))
        assert resp.status_code == 200
        data = resp.get_json()['coherence']
        assert data['is_coherent'] is True
        assert data['coherence_score'] == 100


# ---------------------------------------------------------------------------
# POST /api/v1/phase4/submit
# ---------------------------------------------------------------------------
class TestPhase4Submit:

    def test_unauthenticated_returns_401(self, client, app):
        resp = client.post('/api/v1/phase4/submit', json={})
        assert resp.status_code == 401

    def test_no_venture_returns_400(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            db.session.commit()

        resp = client.post('/api/v1/phase4/submit', json={}, headers=auth(tok))
        assert resp.status_code == 400

    def test_no_pillars_returns_400(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        resp = client.post('/api/v1/phase4/submit', json={}, headers=auth(tok))
        assert resp.status_code == 400

    def test_submit_generates_blueprint(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            v = make_venture(db.session, u.id)
            make_pillars(db.session, u.id, venture_id=v.id, pillars={
                k: f'value for {k}' for k in PILLAR_KEYS
            })
            db.session.commit()

        resp = client.post('/api/v1/phase4/submit', json={}, headers=auth(tok))
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'blueprint' in data
        assert 'coherence' in data
        assert 'ready_for_concept_testing' in data['blueprint']

    def test_submit_idempotent(self, client, app):
        """Submitting twice should upsert, not create two blueprints."""
        with app.app_context():
            u = make_user(db.session)
            user_id = u.id
            tok = make_session(db.session, u.id)
            v = make_venture(db.session, u.id)
            make_pillars(db.session, u.id, venture_id=v.id, pillars={
                k: f'value for {k}' for k in PILLAR_KEYS
            })
            db.session.commit()
            venture_id = v.id

        client.post('/api/v1/phase4/submit', json={}, headers=auth(tok))
        client.post('/api/v1/phase4/submit', json={}, headers=auth(tok))

        with app.app_context():
            count = BusinessPillarsBlueprint.query.filter_by(
                user_id=user_id, venture_id=venture_id
            ).count()
        assert count == 1


# ---------------------------------------------------------------------------
# GET /api/v1/phase4/blueprint
# ---------------------------------------------------------------------------
class TestPhase4Blueprint:

    def test_unauthenticated_returns_401(self, client, app):
        resp = client.get('/api/v1/phase4/blueprint')
        assert resp.status_code == 401

    def test_no_venture_returns_null(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            db.session.commit()

        resp = client.get('/api/v1/phase4/blueprint', headers=auth(tok))
        assert resp.status_code == 200
        assert resp.get_json()['blueprint'] is None

    def test_no_blueprint_generated_returns_null(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        resp = client.get('/api/v1/phase4/blueprint', headers=auth(tok))
        assert resp.status_code == 200
        assert resp.get_json()['blueprint'] is None

    def test_blueprint_returned_after_submit(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            v = make_venture(db.session, u.id)
            make_pillars(db.session, u.id, venture_id=v.id, pillars={
                k: f'value for {k}' for k in PILLAR_KEYS
            })
            db.session.commit()

        client.post('/api/v1/phase4/submit', json={}, headers=auth(tok))
        resp = client.get('/api/v1/phase4/blueprint', headers=auth(tok))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['blueprint'] is not None
        assert 'coherence_score' in data
        assert 'generated_at' in data

    def test_user_isolation(self, client, app):
        """User A's blueprint is not visible to User B."""
        with app.app_context():
            a = make_user(db.session)
            b = make_user(db.session)
            tok_b = make_session(db.session, b.id)
            make_venture(db.session, b.id)  # B has venture but no blueprint
            v_a = make_venture(db.session, a.id)
            make_pillars(db.session, a.id, venture_id=v_a.id, pillars={k: 'x' for k in PILLAR_KEYS})
            db.session.commit()
            # manually create blueprint for A
            from src.models.business_pillars import BusinessPillarsBlueprint
            bp = BusinessPillarsBlueprint(
                user_id=a.id, venture_id=v_a.id,
                blueprint_data={'test': True}, coherence_score=90,
                ready_for_concept_testing=True,
            )
            db.session.add(bp)
            db.session.commit()

        # B should not see A's blueprint
        resp = client.get('/api/v1/phase4/blueprint', headers=auth(tok_b))
        assert resp.status_code == 200
        assert resp.get_json()['blueprint'] is None
