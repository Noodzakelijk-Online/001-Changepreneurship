"""
Sprint 16: Enhanced Venture Profile API tests.

New in Sprint 16:
- GET /ventures/active — new endpoint
- GET /ventures/profile — founder_matrix section present
- GET /ventures/profile — all 13 dimensions including legal_employment + health_energy
- GET /ventures/profile — status_labels on each dimension
- GET /ventures/profile — pattern_tags computed correctly
- GET /ventures/profile — evidence_breakdown by strength
- GET /ventures/profile — evidence_quality_score computed
- GET /ventures/profile — operating_recommendation present
- GET /ventures/profile — phase_gates section present
- GET /ventures/profile — ai_narrative forwarded from FRP
- GET /ventures/profile — completed_phases count
"""
import pytest
from datetime import datetime, timedelta

from src.models.assessment import db, User, UserSession
from src.models.venture_record import VentureRecord, EvidenceItem
from src.models.founder_profile import FounderReadinessProfile, PhaseGate


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
    return token


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}


def make_venture(session, user, **kw):
    v = VentureRecord(
        user_id=user.id, is_active=True,
        idea_raw=kw.get('idea_raw', 'Idea'),
        idea_clarified=kw.get('idea_clarified', 'Clarified'),
        venture_type='FORPROFIT',
        status=kw.get('status', 'DRAFT'),
    )
    session.add(v)
    session.flush()
    return v


def make_frp(session, user, **kw):
    frp = FounderReadinessProfile(
        user_id=user.id, is_latest=True, version=1,
        overall_readiness_level=kw.get('overall_readiness_level', 0),
        recommended_route=kw.get('recommended_route', 'CONTINUE'),
        founder_type='B',
        financial_readiness_score=80, financial_readiness_level=kw.get('financial_level', 0),
        time_capacity_score=75, time_capacity_level=0,
        personal_stability_score=70, personal_stability_level=0,
        motivation_quality_score=90, motivation_quality_level=0,
        skills_experience_score=65, skills_experience_level=1,
        founder_idea_fit_score=70, founder_idea_fit_level=1,
        founder_market_fit_score=60, founder_market_fit_level=kw.get('founder_market_fit_level', 2),
        idea_clarity_score=75, idea_clarity_level=1,
        market_validity_score=55, market_validity_level=kw.get('market_validity_level', 3),
        business_model_score=65, business_model_level=1,
        legal_employment_score=kw.get('legal_score', 80),
        legal_employment_level=kw.get('legal_level', 0),
        health_energy_score=kw.get('health_score', 75),
        health_energy_level=kw.get('health_level', 0),
        network_mentorship_score=50, network_mentorship_level=kw.get('network_level', 2),
        active_blockers=kw.get('active_blockers', []),
        compensation_rules_applied=[],
        burnout_signal=kw.get('burnout_signal', False),
        overload_signal=kw.get('overload_signal', False),
        ai_narrative=kw.get('ai_narrative', None),
        ai_confidence='MEDIUM',
    )
    session.add(frp)
    session.flush()
    return frp


# ─── GET /ventures/active ─────────────────────────────────────────────────────

class TestVenturesActive:
    def test_unauthenticated(self, client):
        r = client.get('/api/v1/ventures/active')
        assert r.status_code == 401

    def test_no_venture_returns_null(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.get('/api/v1/ventures/active', headers=auth_headers(tok))
        assert r.status_code == 200
        assert r.get_json()['venture'] is None

    def test_returns_active_venture(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            make_venture(db.session, u, idea_raw='My Startup', status='CLARIFIED')
            db.session.commit()
        r = client.get('/api/v1/ventures/active', headers=auth_headers(tok))
        assert r.status_code == 200
        v = r.get_json()['venture']
        assert v is not None
        assert v['idea_raw'] == 'My Startup'
        assert v['status'] == 'CLARIFIED'

    def test_returns_venture_fields(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            make_venture(db.session, u)
            db.session.commit()
        r = client.get('/api/v1/ventures/active', headers=auth_headers(tok))
        v = r.get_json()['venture']
        for field in ('id', 'status', 'type', 'idea_raw', 'idea_clarified',
                      'problem_statement', 'value_proposition'):
            assert field in v, f"Missing field: {field}"

    def test_user_isolation(self, client):
        with client.application.app_context():
            u1 = make_user(db.session)
            u2 = make_user(db.session)
            tok1 = make_session(db.session, u1)
            tok2 = make_session(db.session, u2)
            make_venture(db.session, u1, idea_raw='User1 venture')
            db.session.commit()
        r = client.get('/api/v1/ventures/active', headers=auth_headers(tok2))
        assert r.get_json()['venture'] is None


# ─── founder_matrix section ───────────────────────────────────────────────────

class TestFounderMatrix:
    def test_founder_matrix_absent_when_no_frp(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        assert r.status_code == 200
        assert r.get_json()['founder_matrix'] is None

    def test_founder_matrix_present_with_frp(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            make_frp(db.session, u)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        fm = r.get_json()['founder_matrix']
        assert fm is not None
        assert 'dimensions' in fm
        assert 'pattern_tags' in fm
        assert 'operating_recommendation' in fm
        assert 'overall_readiness_level' in fm
        assert 'overall_status_label' in fm

    def test_all_13_dimensions_present(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            make_frp(db.session, u)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        dims = r.get_json()['founder_matrix']['dimensions']
        expected = [
            'financial_readiness', 'time_capacity', 'personal_stability',
            'motivation_quality', 'skills_experience', 'founder_idea_fit',
            'founder_market_fit', 'idea_clarity', 'market_validity',
            'business_model', 'legal_employment', 'health_energy', 'network_mentorship',
        ]
        for d in expected:
            assert d in dims, f"Missing dimension: {d}"

    def test_dimensions_have_status_labels(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            make_frp(db.session, u)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        dims = r.get_json()['founder_matrix']['dimensions']
        for name, d in dims.items():
            assert 'status_label' in d, f"Missing status_label on {name}"
            assert 'label' in d, f"Missing label on {name}"

    def test_status_label_values(self, client):
        """level 0→Strong, 1→Adequate, 2→Watch, 3→Soft Block, 4→Hard Block, 5→Hard Stop"""
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            # financial_readiness_level=0, market_validity_level=3
            make_frp(db.session, u, financial_level=0, market_validity_level=3)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        dims = r.get_json()['founder_matrix']['dimensions']
        assert dims['financial_readiness']['status_label'] == 'Strong'
        assert dims['market_validity']['status_label'] == 'Soft Block'

    def test_legal_employment_and_health_energy_in_dimensions(self, client):
        """Regression: these 2 dims were missing in Sprint 14."""
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            make_frp(db.session, u, legal_score=70, legal_level=1,
                     health_score=60, health_level=2)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        dims = r.get_json()['founder_matrix']['dimensions']
        assert dims['legal_employment']['score'] == 70
        assert dims['legal_employment']['status_label'] == 'Adequate'
        assert dims['health_energy']['status_label'] == 'Watch'


# ─── pattern_tags ────────────────────────────────────────────────────────────

class TestPatternTags:
    def test_no_tags_for_healthy_founder(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            # All levels 0 or 1 — no bad tags expected
            frp = FounderReadinessProfile(
                user_id=u.id, is_latest=True, version=1,
                overall_readiness_level=0, recommended_route='CONTINUE', founder_type='B',
                financial_readiness_score=90, financial_readiness_level=0,
                time_capacity_score=85, time_capacity_level=0,
                personal_stability_score=80, personal_stability_level=0,
                motivation_quality_score=90, motivation_quality_level=0,
                skills_experience_score=70, skills_experience_level=0,
                founder_idea_fit_score=80, founder_idea_fit_level=0,
                founder_market_fit_score=75, founder_market_fit_level=0,
                idea_clarity_score=80, idea_clarity_level=0,
                market_validity_score=75, market_validity_level=0,
                business_model_score=70, business_model_level=0,
                legal_employment_score=85, legal_employment_level=0,
                health_energy_score=80, health_energy_level=0,
                network_mentorship_score=65, network_mentorship_level=1,
                active_blockers=[], burnout_signal=False, overload_signal=False,
                compensation_rules_applied=[],
            )
            db.session.add(frp)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        tags = r.get_json()['founder_matrix']['pattern_tags']
        # Should not contain any critical tags
        assert 'Financial constraint' not in tags
        assert 'Burnout watch' not in tags

    def test_burnout_tag_generated(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            make_frp(db.session, u, burnout_signal=True)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        tags = r.get_json()['founder_matrix']['pattern_tags']
        assert 'Burnout watch' in tags

    def test_financial_constraint_tag(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            make_frp(db.session, u, financial_level=4)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        tags = r.get_json()['founder_matrix']['pattern_tags']
        assert 'Financial constraint' in tags


# ─── evidence breakdown ───────────────────────────────────────────────────────

class TestEvidenceBreakdown:
    def test_evidence_breakdown_by_strength(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            v = make_venture(db.session, u)
            # Add evidence items with different strengths
            for strength in ['DIRECT', 'DIRECT', 'BEHAVIORAL', 'BELIEF']:
                db.session.add(EvidenceItem(
                    user_id=u.id, venture_id=v.id,
                    evidence_type='INTERVIEW', strength=strength,
                    description='Evidence item',
                ))
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        mkt = r.get_json()['market']
        assert mkt['evidence_count'] == 4
        bd = mkt['evidence_by_strength']
        assert bd.get('DIRECT') == 2
        assert bd.get('BEHAVIORAL') == 1
        assert bd.get('BELIEF') == 1

    def test_evidence_quality_score_higher_for_strong_evidence(self, client):
        with client.application.app_context():
            u1 = make_user(db.session)
            u2 = make_user(db.session)
            tok1 = make_session(db.session, u1)
            tok2 = make_session(db.session, u2)
            v1 = make_venture(db.session, u1)
            v2 = make_venture(db.session, u2)
            # u1 has weak evidence, u2 has strong evidence
            db.session.add(EvidenceItem(user_id=u1.id, venture_id=v1.id,
                evidence_type='INTERVIEW', strength='BELIEF', description='weak'))
            db.session.add(EvidenceItem(user_id=u2.id, venture_id=v2.id,
                evidence_type='INTERVIEW', strength='BEHAVIORAL', description='strong'))
            db.session.commit()
        r1 = client.get('/api/v1/ventures/profile', headers=auth_headers(tok1))
        r2 = client.get('/api/v1/ventures/profile', headers=auth_headers(tok2))
        q1 = r1.get_json()['market']['evidence_quality_score']
        q2 = r2.get_json()['market']['evidence_quality_score']
        assert q2 > q1


# ─── phase_gates section ─────────────────────────────────────────────────────

class TestPhaseGatesSection:
    def test_phase_gates_always_present(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        assert 'phase_gates' in r.get_json()

    def test_phase_gates_includes_gate_data(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            gate = PhaseGate(user_id=u.id, phase_number=1, status='COMPLETED')
            db.session.add(gate)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        gates = r.get_json()['phase_gates']
        assert '1' in gates
        assert gates['1']['status'] == 'COMPLETED'


# ─── completed_phases count ──────────────────────────────────────────────────

class TestCompletedPhasesCount:
    def test_zero_when_nothing(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        assert r.get_json()['completed_phases'] == 0

    def test_increments_with_venture(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            make_venture(db.session, u)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        assert r.get_json()['completed_phases'] == 1  # phase 2 counts


# ─── ai_narrative forwarded ──────────────────────────────────────────────────

class TestAINarrative:
    def test_ai_narrative_forwarded(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            make_frp(db.session, u, ai_narrative='You are a strong analytical founder.')
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        fm = r.get_json()['founder_matrix']
        assert fm['ai_narrative'] == 'You are a strong analytical founder.'

    def test_ai_narrative_null_when_no_frp(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.get('/api/v1/ventures/profile', headers=auth_headers(tok))
        assert r.get_json()['founder_matrix'] is None
