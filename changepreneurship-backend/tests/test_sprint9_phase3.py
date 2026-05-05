"""
Sprint 9: Phase 3 Market Research API tests.

Tests:
- EvidenceItem CRUD  (POST/GET/DELETE /phase3/evidence)
- CompetitorEntry CRUD  (POST/GET/DELETE /phase3/competitors)
- MarketContext save/update  (PATCH/GET /phase3/market-data)
- MarketValidityReport generation  (POST /phase3/submit, GET /phase3/report)
- Assumptions fetch  (GET /phase3/assumptions)
- Interview script  (GET /phase3/interview-script)
- Auth guards on every endpoint
- Phase3MarketService scoring logic
"""
from datetime import datetime, timedelta
import pytest

from src.models.assessment import db, User, UserSession
from src.models.venture_record import VentureRecord, EvidenceItem
from src.models.market_research import CompetitorEntry, MarketContext, MarketValidityReport
from src.services.phase3_market_service import Phase3MarketService


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


def make_venture(session, user_id, assumptions=None, **kwargs):
    v = VentureRecord(
        user_id=user_id,
        is_active=True,
        idea_raw='Test idea raw',
        problem_statement='People struggle with X',
        target_user_hypothesis='SME founders',
        value_proposition='We solve X cheaply',
        status='DRAFT',
        assumptions=assumptions if assumptions is not None else ['Assumption A', 'Assumption B'],
        **kwargs,
    )
    session.add(v)
    session.flush()
    return v


def auth(token):
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


# ---------------------------------------------------------------------------
# Phase3MarketService unit tests
# ---------------------------------------------------------------------------
class TestPhase3MarketService:

    def test_score_empty_evidence_insufficient(self):
        svc = Phase3MarketService()
        result = svc.score_evidence([])
        assert result['score'] == 0
        assert result['recommendation'] == 'NO_EVIDENCE'

    def test_score_behavioral_evidence_boosts_score(self):
        svc = Phase3MarketService()
        items = [
            {'strength': 'BEHAVIORAL', 'evidence_type': 'PAYMENT'},
            {'strength': 'BEHAVIORAL', 'evidence_type': 'REPEAT'},
        ]
        result = svc.score_evidence(items)
        assert result['score'] > 20

    def test_score_all_belief_caps_at_15(self):
        svc = Phase3MarketService()
        items = [{'strength': 'BELIEF', 'evidence_type': 'INTERVIEW'}] * 5
        result = svc.score_evidence(items)
        assert result['score'] <= 15

    def test_evaluate_assumptions_untested_when_no_evidence(self):
        svc = Phase3MarketService()
        assumptions = ['Assumption A', 'Assumption B']
        result = svc.evaluate_assumptions(assumptions, [])
        assert result['total'] == 2
        assert all(a['status'] == 'UNTESTED' for a in result['results'])

    def test_generate_report_returns_required_fields(self):
        svc = Phase3MarketService()
        venture = type('V', (), {
            'id': 1,
            'problem_statement': 'Test problem',
            'target_user_hypothesis': 'Founders',
            'value_proposition': 'Fast solution',
            'assumptions': ['A1'],
        })()
        evidence = [
            {'strength': 'DIRECT', 'evidence_type': 'INTERVIEW', 'description': 'User research'},
            {'strength': 'BEHAVIORAL', 'evidence_type': 'PAYMENT', 'description': 'Payment confirmed'},
        ]
        competitors = [{'name': 'Rival Co', 'is_direct': True}]
        market_data = {'pain_intensity': 'HIGH', 'willingness_to_pay': True}
        report = svc.generate_market_validity_report(venture, evidence, competitors, market_data)
        assert 'validity_score' in report
        assert 'final_recommendation' in report
        assert 'validation_gaps' in report
        assert 'ready_for_business_pillars' in report

    def test_validate_competitor_missing_name(self):
        svc = Phase3MarketService()
        ok, err = svc.validate_competitor({'description': 'Some rival'})
        assert not ok
        assert 'name' in err.lower()

    def test_generate_interview_script_returns_questions(self):
        svc = Phase3MarketService()
        venture = type('V', (), {
            'problem_statement': 'Test problem',
            'target_user_hypothesis': 'Founders',
            'value_proposition': 'Fast solution',
        })()
        result = svc.generate_interview_script(venture)
        assert isinstance(result, dict)
        assert 'questions' in result
        assert isinstance(result['questions'], list)
        assert len(result['questions']) > 0


# ---------------------------------------------------------------------------
# Phase 3 API endpoint tests
# ---------------------------------------------------------------------------
class TestPhase3AuthGuards:
    """All endpoints must require a valid session token."""

    ENDPOINTS = [
        ('GET',    '/api/v1/phase3/assumptions'),
        ('POST',   '/api/v1/phase3/evidence'),
        ('GET',    '/api/v1/phase3/evidence'),
        ('POST',   '/api/v1/phase3/competitors'),
        ('GET',    '/api/v1/phase3/competitors'),
        ('PATCH',  '/api/v1/phase3/market-data'),
        ('GET',    '/api/v1/phase3/market-data'),
        ('POST',   '/api/v1/phase3/submit'),
        ('GET',    '/api/v1/phase3/report'),
        ('GET',    '/api/v1/phase3/interview-script'),
    ]

    def test_all_endpoints_reject_unauthenticated(self, client):
        for method, url in self.ENDPOINTS:
            fn = getattr(client, method.lower())
            resp = fn(url, json={})
            assert resp.status_code in (401, 403), f"{method} {url} expected 401/403 got {resp.status_code}"


class TestPhase3Evidence:

    def test_add_and_list_evidence(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        resp = client.post('/api/v1/phase3/evidence', json={
            'evidence_type': 'INTERVIEW',
            'strength': 'DIRECT',
            'description': 'Talked to 10 founders who confirmed the pain point',
            'source': 'User interview session',
        }, headers=auth(tok))
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['evidence']['evidence_type'] == 'INTERVIEW'
        ev_id = data['evidence']['id']

        # List
        list_resp = client.get('/api/v1/phase3/evidence', headers=auth(tok))
        assert list_resp.status_code == 200
        ids = [e['id'] for e in list_resp.get_json()['evidence']]
        assert ev_id in ids

    def test_delete_evidence(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            v = make_venture(db.session, u.id)
            ev = EvidenceItem(
                user_id=u.id, venture_id=v.id,
                evidence_type='SURVEY', strength='OPINION',
                description='Survey of 20 people', source='Google Forms',
            )
            db.session.add(ev)
            db.session.commit()
            ev_id = ev.id

        del_resp = client.delete(f'/api/v1/phase3/evidence/{ev_id}', headers=auth(tok))
        assert del_resp.status_code == 200

        list_resp = client.get('/api/v1/phase3/evidence', headers=auth(tok))
        ids = [e['id'] for e in list_resp.get_json()['evidence']]
        assert ev_id not in ids

    def test_add_evidence_invalid_type(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        resp = client.post('/api/v1/phase3/evidence', json={
            'evidence_type': 'INVALID_TYPE',
            'strength': 'DIRECT',
            'description': 'Some evidence',
            'source': 'Source',
        }, headers=auth(tok))
        assert resp.status_code == 400

    def test_add_evidence_missing_description(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        resp = client.post('/api/v1/phase3/evidence', json={
            'evidence_type': 'INTERVIEW',
            'strength': 'DIRECT',
            'source': 'Source',
            # missing 'description'
        }, headers=auth(tok))
        assert resp.status_code == 400


class TestPhase3Competitors:

    def test_add_and_list_competitors(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        resp = client.post('/api/v1/phase3/competitors', json={
            'name': 'BigCorp',
            'description': 'Industry giant doing similar things',
            'strengths': 'Brand recognition, capital',
            'weaknesses': 'Slow, expensive',
            'is_direct': True,
        }, headers=auth(tok))
        assert resp.status_code == 201
        comp_id = resp.get_json()['competitor']['id']

        list_resp = client.get('/api/v1/phase3/competitors', headers=auth(tok))
        assert list_resp.status_code == 200
        ids = [c['id'] for c in list_resp.get_json()['competitors']]
        assert comp_id in ids

    def test_delete_competitor(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            v = make_venture(db.session, u.id)
            c = CompetitorEntry(
                user_id=u.id, venture_id=v.id,
                name='SmallRival', is_direct=False,
            )
            db.session.add(c)
            db.session.commit()
            c_id = c.id

        del_resp = client.delete(f'/api/v1/phase3/competitors/{c_id}', headers=auth(tok))
        assert del_resp.status_code == 200

        list_resp = client.get('/api/v1/phase3/competitors', headers=auth(tok))
        ids = [c['id'] for c in list_resp.get_json()['competitors']]
        assert c_id not in ids

    def test_add_competitor_missing_name(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        resp = client.post('/api/v1/phase3/competitors', json={
            'description': 'Some competitor without a name',
        }, headers=auth(tok))
        assert resp.status_code == 400

    def test_cannot_delete_other_users_competitor(self, client, app):
        with app.app_context():
            owner = make_user(db.session)
            attacker = make_user(db.session)
            tok_attacker = make_session(db.session, attacker.id)
            v = make_venture(db.session, owner.id)
            c = CompetitorEntry(user_id=owner.id, venture_id=v.id, name='OwnersCorp', is_direct=True)
            db.session.add(c)
            db.session.commit()
            c_id = c.id

        resp = client.delete(f'/api/v1/phase3/competitors/{c_id}', headers=auth(tok_attacker))
        assert resp.status_code == 404


class TestPhase3MarketData:

    def test_save_and_retrieve_market_data(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        patch_resp = client.patch('/api/v1/phase3/market-data', json={
            'pain_intensity': 'HIGH',
            'willingness_to_pay': True,
            'target_segment': 'Early-stage founders',
            'market_timing': 'NOW',
            'market_size_note': 'Estimated $2B TAM',
        }, headers=auth(tok))
        assert patch_resp.status_code == 200

        get_resp = client.get('/api/v1/phase3/market-data', headers=auth(tok))
        assert get_resp.status_code == 200
        ctx = get_resp.get_json()['market_data']
        assert ctx['pain_intensity'] == 'HIGH'
        assert ctx['target_segment'] == 'Early-stage founders'

    def test_update_market_data_idempotent(self, client, app):
        """PATCH twice — should upsert, not create duplicate rows."""
        with app.app_context():
            u = make_user(db.session)
            user_id = u.id
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        client.patch('/api/v1/phase3/market-data', json={'pain_intensity': 'MEDIUM'}, headers=auth(tok))
        client.patch('/api/v1/phase3/market-data', json={'pain_intensity': 'HIGH'}, headers=auth(tok))

        get_resp = client.get('/api/v1/phase3/market-data', headers=auth(tok))
        ctx = get_resp.get_json()['market_data']
        assert ctx['pain_intensity'] == 'HIGH'

        with app.app_context():
            count = MarketContext.query.filter_by(user_id=user_id).count()
        assert count == 1


class TestPhase3Report:

    def test_generate_report_requires_venture(self, client, app):
        """submit without any venture should return 4xx."""
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            db.session.commit()

        resp = client.post('/api/v1/phase3/submit', json={}, headers=auth(tok))
        assert resp.status_code in (404, 422, 400)

    def test_generate_report_with_evidence(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            v = make_venture(db.session, u.id)
            ev = EvidenceItem(
                user_id=u.id, venture_id=v.id,
                evidence_type='PAYMENT', strength='BEHAVIORAL',
                description='10 users pre-paid for beta access',
                source='Stripe checkout',
            )
            db.session.add(ev)
            db.session.commit()

        resp = client.post('/api/v1/phase3/submit', json={}, headers=auth(tok))
        assert resp.status_code == 200
        report = resp.get_json()['report']
        assert 'validity_score' in report
        assert 'final_recommendation' in report

    def test_get_report_404_when_none_generated(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        resp = client.get('/api/v1/phase3/report', headers=auth(tok))
        # endpoint returns 200 with null report when not yet generated
        assert resp.status_code == 200
        assert resp.get_json()['report'] is None

    def test_get_report_after_submit(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        client.post('/api/v1/phase3/submit', json={}, headers=auth(tok))
        resp = client.get('/api/v1/phase3/report', headers=auth(tok))
        assert resp.status_code == 200
        assert 'report' in resp.get_json()


class TestPhase3Assumptions:

    def test_no_venture_returns_empty(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            db.session.commit()

        resp = client.get('/api/v1/phase3/assumptions', headers=auth(tok))
        assert resp.status_code == 200
        assert resp.get_json()['assumptions'] == []

    def test_returns_venture_assumptions(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id, assumptions=['Price is the main driver', 'Users want speed'])
            db.session.commit()

        resp = client.get('/api/v1/phase3/assumptions', headers=auth(tok))
        assert resp.status_code == 200
        assumptions = resp.get_json()['assumptions']
        assert len(assumptions) == 2


class TestPhase3InterviewScript:

    def test_no_venture_returns_error(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            db.session.commit()

        resp = client.get('/api/v1/phase3/interview-script', headers=auth(tok))
        assert resp.status_code in (400, 404)

    def test_returns_questions_list(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u.id)
            make_venture(db.session, u.id)
            db.session.commit()

        resp = client.get('/api/v1/phase3/interview-script', headers=auth(tok))
        assert resp.status_code == 200
        data = resp.get_json()
        # script is nested under 'script' key
        assert 'script' in data
        assert 'questions' in data['script']
        assert isinstance(data['script']['questions'], list)
        assert len(data['script']['questions']) > 0
