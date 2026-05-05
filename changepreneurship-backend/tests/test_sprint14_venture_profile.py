"""
Sprint 14: Venture Profile API tests.

Tests:
- GET /ventures/profile — auth guard
- GET /ventures/profile — empty (no venture, no deliverables)
- GET /ventures/profile — with active venture only
- GET /ventures/profile — with phase 1 deliverable (FounderReadinessProfile)
- GET /ventures/profile — with phase 3 deliverable (MarketValidityReport)
- GET /ventures/profile — with phase 4 deliverable (BusinessPillarsBlueprint)
- GET /ventures/profile — with phase 5 deliverable (ConceptTestResult)
- GET /ventures/profile — with phase 6 deliverable (VentureEnvironment)
- GET /ventures/profile — with phase 7 deliverable (PrototypeTestResult)
- GET /ventures/profile — full profile (all deliverables present)
- GET /ventures/profile — user isolation (user A cannot see user B's data)
- GET /ventures/profile — market context included
- GET /ventures/profile — evidence count correct
"""
import pytest
from datetime import datetime, timedelta

from src.models.assessment import db, User, UserSession
from src.models.venture_record import VentureRecord, EvidenceItem
from src.models.founder_profile import FounderReadinessProfile
from src.models.market_research import MarketContext, MarketValidityReport
from src.models.business_pillars import BusinessPillarsBlueprint
from src.models.concept_testing import ConceptTestResult
from src.models.business_development import VentureEnvironment
from src.models.prototype_testing import PrototypeTestResult


_CTR = [0]


def _uniq(p='u'):
    _CTR[0] += 1
    return f"{p}_{_CTR[0]}"


def make_user(session):
    u = User(username=_uniq('user'), email=_uniq('e') + '@test.com',
             password_hash='x' * 60)
    session.add(u)
    session.flush()
    return u


def make_session(session, user):
    token = _uniq('tok')
    s = UserSession(user_id=user.id, session_token=token,
                    is_active=True,
                    expires_at=datetime.utcnow() + timedelta(hours=24))
    session.add(s)
    session.flush()
    return token  # return token string, not detachable object


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}


def make_venture(session, user, **kwargs):
    v = VentureRecord(
        user_id=user.id, is_active=True,
        idea_raw=kwargs.get('idea_raw', 'Test idea'),
        idea_clarified=kwargs.get('idea_clarified', 'Clarified idea'),
        problem_statement=kwargs.get('problem_statement', 'Problem'),
        target_user_hypothesis=kwargs.get('target_user_hypothesis', 'Target'),
        value_proposition=kwargs.get('value_proposition', 'Value prop'),
        venture_type='FORPROFIT',
        status=kwargs.get('status', 'DRAFT'),
    )
    session.add(v)
    session.flush()
    return v


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------

class TestVentureProfileAuth:
    def test_unauthenticated(self, client):
        r = client.get('/api/v1/ventures/profile')
        assert r.status_code == 401

    def test_bad_token(self, client):
        r = client.get('/api/v1/ventures/profile',
                       headers=auth_headers('bad-token'))
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------

class TestVentureProfileEmpty:
    def test_no_venture_no_deliverables(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        assert r.status_code == 200
        data = r.get_json()
        assert data['venture'] is None
        assert data['deliverables']['phase1'] is None
        assert data['deliverables']['phase3'] is None
        assert data['deliverables']['phase4'] is None
        assert data['deliverables']['phase5'] is None
        assert data['deliverables']['phase6'] is None
        assert data['deliverables']['phase7'] is None
        assert data['market']['evidence_count'] == 0

    def test_market_section_always_present(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        assert r.status_code == 200
        data = r.get_json()
        assert 'market' in data
        assert 'evidence_count' in data['market']


# ---------------------------------------------------------------------------
# Venture identity
# ---------------------------------------------------------------------------

class TestVentureProfileVenture:
    def test_returns_active_venture(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            make_venture(db.session, u, idea_raw='My App Idea', status='CLARIFIED')
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        assert r.status_code == 200
        v = r.get_json()['venture']
        assert v is not None
        assert v['idea_raw'] == 'My App Idea'
        assert v['status'] == 'CLARIFIED'
        assert v['idea_clarified'] == 'Clarified idea'

    def test_venture_fields_complete(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            make_venture(db.session, u, value_proposition='Strong VP')
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        v = r.get_json()['venture']
        assert 'problem_statement' in v
        assert 'target_user_hypothesis' in v
        assert 'value_proposition' in v
        assert v['value_proposition'] == 'Strong VP'
        assert 'type' in v


# ---------------------------------------------------------------------------
# Phase deliverables
# ---------------------------------------------------------------------------

class TestVentureProfilePhase1:
    def test_phase1_deliverable(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            frp = FounderReadinessProfile(
                user_id=u.id, is_latest=True, version=1,
                overall_readiness_level=0,
                founder_type='B',
                recommended_route='CONTINUE',
                financial_readiness_score=80, financial_readiness_level=0,
                time_capacity_score=75, time_capacity_level=0,
                motivation_quality_score=90, motivation_quality_level=0,
                active_blockers=[],
                burnout_signal_detected=False,
            )
            db.session.add(frp)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        p1 = r.get_json()['deliverables']['phase1']
        assert p1 is not None
        assert p1['founder_type'] == 'B'
        assert p1['recommended_route'] == 'CONTINUE'
        assert p1['overall_readiness_level'] == 0
        assert p1['burnout_signal'] is False
        assert 'financial_readiness' in p1['dimensions']
        assert p1['dimensions']['financial_readiness']['score'] == 80


class TestVentureProfilePhase3:
    def test_phase3_deliverable(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            v = make_venture(db.session, u)
            mvr = MarketValidityReport(
                user_id=u.id, venture_id=v.id,
                report_data={
                    'validity_score': 72,
                    'verdict': 'PROCEED',
                    'market_data': {'size': 'large'},
                },
                generated_at=datetime.utcnow(),
            )
            db.session.add(mvr)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        p3 = r.get_json()['deliverables']['phase3']
        assert p3 is not None
        assert p3['validity_score'] == 72
        assert p3['verdict'] == 'PROCEED'
        assert p3['market_data'] == {'size': 'large'}
        assert p3['generated_at'] is not None

    def test_phase3_none_without_report(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            make_venture(db.session, u)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        assert r.get_json()['deliverables']['phase3'] is None


class TestVentureProfilePhase4:
    def test_phase4_deliverable(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            bpb = BusinessPillarsBlueprint(
                user_id=u.id,
                blueprint_data={'pillars': {}},
                coherence_score=65,
                ready_for_concept_testing=True,
                generated_at=datetime.utcnow(),
            )
            db.session.add(bpb)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        p4 = r.get_json()['deliverables']['phase4']
        assert p4 is not None
        assert p4['coherence_score'] == 65
        assert p4['ready_for_concept_testing'] is True


class TestVentureProfilePhase5:
    def test_phase5_deliverable(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            ctr = ConceptTestResult(
                user_id=u.id,
                result_data={},
                adoption_signal='MODERATE',
                decision='PROCEED',
                ready_for_business_dev=True,
                generated_at=datetime.utcnow(),
            )
            db.session.add(ctr)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        p5 = r.get_json()['deliverables']['phase5']
        assert p5 is not None
        assert p5['adoption_signal'] == 'MODERATE'
        assert p5['decision'] == 'PROCEED'
        assert p5['ready_for_business_dev'] is True


class TestVentureProfilePhase6:
    def test_phase6_deliverable(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            ve = VentureEnvironment(
                user_id=u.id,
                environment_data={},
                readiness_score=78,
                operational_ready=True,
                decision='PROCEED',
                generated_at=datetime.utcnow(),
            )
            db.session.add(ve)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        p6 = r.get_json()['deliverables']['phase6']
        assert p6 is not None
        assert p6['readiness_score'] == 78
        assert p6['operational_ready'] is True
        assert p6['decision'] == 'PROCEED'


class TestVentureProfilePhase7:
    def test_phase7_deliverable(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            ptr = PrototypeTestResult(
                user_id=u.id,
                result_data={},
                scale_readiness='MODERATE',
                scale_score=62,
                decision='SCALE_CAREFULLY',
                ready_to_scale=False,
                generated_at=datetime.utcnow(),
            )
            db.session.add(ptr)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        p7 = r.get_json()['deliverables']['phase7']
        assert p7 is not None
        assert p7['scale_readiness'] == 'MODERATE'
        assert p7['scale_score'] == 62
        assert p7['decision'] == 'SCALE_CAREFULLY'
        assert p7['ready_to_scale'] is False


# ---------------------------------------------------------------------------
# Market context + evidence
# ---------------------------------------------------------------------------

class TestVentureProfileMarket:
    def test_market_context_included(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            make_venture(db.session, u)
            mc = MarketContext(
                user_id=u.id,
                target_segment='Small business owners',
                pain_intensity='HIGH',
                willingness_to_pay=True,
                estimated_price_range='$50-100/mo',
            )
            db.session.add(mc)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        mkt = r.get_json()['market']
        assert mkt['target_segment'] == 'Small business owners'
        assert mkt['pain_intensity'] == 'HIGH'
        assert mkt['willingness_to_pay'] is True

    def test_evidence_count(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            v = make_venture(db.session, u)
            for i in range(3):
                e = EvidenceItem(
                    user_id=u.id, venture_id=v.id,
                    description=f'evidence {i}',
                    evidence_type='INTERVIEW',
                    strength='DIRECT',
                )
                db.session.add(e)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        assert r.get_json()['market']['evidence_count'] == 3


# ---------------------------------------------------------------------------
# Full profile + isolation
# ---------------------------------------------------------------------------

class TestVentureProfileFull:
    def test_full_profile_all_deliverables(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            v = make_venture(db.session, u, status='OPERATIONAL')

            frp = FounderReadinessProfile(
                user_id=u.id, is_latest=True, version=1,
                overall_readiness_level=0, founder_type='A',
                recommended_route='CONTINUE',
                financial_readiness_score=85, financial_readiness_level=0,
                active_blockers=[], burnout_signal_detected=False,
            )
            mvr = MarketValidityReport(
                user_id=u.id, venture_id=v.id,
                report_data={'validity_score': 80, 'verdict': 'STRONG', 'market_data': {}},
                generated_at=datetime.utcnow(),
            )
            bpb = BusinessPillarsBlueprint(
                user_id=u.id, blueprint_data={}, coherence_score=70,
                ready_for_concept_testing=True, generated_at=datetime.utcnow(),
            )
            ctr = ConceptTestResult(
                user_id=u.id, result_data={}, adoption_signal='STRONG',
                decision='PROCEED', ready_for_business_dev=True,
                generated_at=datetime.utcnow(),
            )
            ve = VentureEnvironment(
                user_id=u.id, environment_data={}, readiness_score=82,
                operational_ready=True, decision='PROCEED',
                generated_at=datetime.utcnow(),
            )
            ptr = PrototypeTestResult(
                user_id=u.id, result_data={}, scale_readiness='STRONG',
                scale_score=80, decision='SCALE_CAREFULLY', ready_to_scale=True,
                generated_at=datetime.utcnow(),
            )
            for obj in [frp, mvr, bpb, ctr, ve, ptr]:
                db.session.add(obj)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        assert r.status_code == 200
        data = r.get_json()
        assert data['venture']['status'] == 'OPERATIONAL'
        for phase in ['phase1', 'phase3', 'phase4', 'phase5', 'phase6', 'phase7']:
            assert data['deliverables'][phase] is not None, f"{phase} should not be None"

    def test_user_isolation(self, client):
        """User A cannot see User B's venture data."""
        with client.application.app_context():
            ua = make_user(db.session)
            sa = make_session(db.session, ua)
            ub = make_user(db.session)
            _sb = make_session(db.session, ub)
            make_venture(db.session, ub, idea_raw="User B's secret idea")
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(sa))
        assert r.status_code == 200
        # User A has no venture → venture should be None
        assert r.get_json()['venture'] is None

    def test_response_structure(self, client):
        """Response always has venture, deliverables, market keys."""
        with client.application.app_context():
            u = make_user(db.session)
            s = make_session(db.session, u)
            db.session.commit()

        r = client.get('/api/v1/ventures/profile', headers=auth_headers(s))
        data = r.get_json()
        assert 'venture' in data
        assert 'deliverables' in data
        assert 'market' in data
        for k in ['phase1', 'phase3', 'phase4', 'phase5', 'phase6', 'phase7']:
            assert k in data['deliverables']
