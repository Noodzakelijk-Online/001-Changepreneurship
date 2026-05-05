"""
Sprint 20: Phase 1 End-to-End tests.

Verifies the complete Phase 1 submission flow:
  - POST /phase1/submit creates a FounderReadinessProfile (FRP)
  - POST /phase1/submit creates PhaseGates for the user
  - POST /phase1/submit returns recommended_route
  - POST /phase1/submit returns founder_matrix with dimensions
  - POST /phase1/submit returns phase_gates dict (string keys)
  - Re-submitting creates a versioned FRP (version increments)
  - Unauthenticated POST returns 401
  - Invalid body returns 400
  - POST with minimal required fields succeeds
  - POST with illegal_venture=True triggers Hard Stop
  - PhaseGate status is IN_PROGRESS after normal submit
  - GET /ventures/profile returns founder_matrix after FRP exists
  - GET /ventures/profile phase_gates are populated after submit
"""
import pytest
from datetime import datetime, timedelta

from src.models.assessment import db, User, UserSession
from src.models.founder_profile import FounderReadinessProfile, PhaseGate


_CTR = [0]


def _uniq(p='u'):
    _CTR[0] += 1
    return f"{p}_{_CTR[0]}"


def make_user(session):
    u = User(
        username=_uniq('user'),
        email=_uniq('e') + '@test.com',
        password_hash='x' * 60,
    )
    session.add(u)
    session.flush()
    return u


def make_session(session, user):
    token = _uniq('tok')
    s = UserSession(
        user_id=user.id,
        session_token=token,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    session.add(s)
    session.flush()
    return token


def auth(token):
    return {'Authorization': f'Bearer {token}'}


VALID_PAYLOAD = {
    'idea_description': 'An app for freelancers to track invoices automatically',
    'motivation_raw': 'I believe this problem is underserved',
    'motivation_type': 'MISSION',
    'target_user_description': 'Freelance designers who hate admin work',
    'target_user_specific': True,
    'problem_defined': True,
    'weekly_available_hours': 15,
    'financial_runway_months': 12,
    'income_stable': True,
    'has_spoken_to_users': 'yes_briefly',
    'has_non_compete': False,
    'employer_ip_risk': False,
    'immigration_restriction': False,
    'illegal_venture': False,
    'primary_fear': 'Running out of money before finding traction',
    'paying_customers_exist': False,
    'stress_level': 2,
    'burnout_signals': [],
    'life_chaos_signals': [],
    'energy_level': 4,
}


# ─── Auth guard ────────────────────────────────────────────────────────────────

def test_phase1_submit_requires_auth(client):
    resp = client.post('/api/v1/phase1/submit', json=VALID_PAYLOAD)
    assert resp.status_code == 401


def test_phase1_submit_rejects_non_json(client):
    with client.application.app_context():
        user = make_user(db.session)
        token = make_session(db.session, user)
        db.session.commit()

    resp = client.post(
        '/api/v1/phase1/submit',
        data='not json',
        headers={**auth(token), 'Content-Type': 'text/plain'},
    )
    assert resp.status_code == 400


# ─── Core happy path ────────────────────────────────────────────────────────────

def test_phase1_submit_creates_frp(client):
    """Submitting Phase 1 must create a FounderReadinessProfile row."""
    with client.application.app_context():
        user = make_user(db.session)
        token = make_session(db.session, user)
        db.session.commit()
        uid = user.id

    resp = client.post('/api/v1/phase1/submit', json=VALID_PAYLOAD, headers=auth(token))
    assert resp.status_code == 200

    with client.application.app_context():
        frp = FounderReadinessProfile.query.filter_by(user_id=uid, is_latest=True).first()
        assert frp is not None
        assert frp.version == 1


def test_phase1_submit_creates_phase_gates(client):
    """Submitting Phase 1 must create PhaseGate rows for the user."""
    with client.application.app_context():
        user = make_user(db.session)
        token = make_session(db.session, user)
        db.session.commit()
        uid = user.id

    resp = client.post('/api/v1/phase1/submit', json=VALID_PAYLOAD, headers=auth(token))
    assert resp.status_code == 200

    with client.application.app_context():
        gates = PhaseGate.query.filter_by(user_id=uid).all()
        assert len(gates) == 7


def test_phase1_submit_returns_recommended_route(client):
    with client.application.app_context():
        user = make_user(db.session)
        token = make_session(db.session, user)
        db.session.commit()

    resp = client.post('/api/v1/phase1/submit', json=VALID_PAYLOAD, headers=auth(token))
    data = resp.get_json()

    assert 'recommended_route' in data
    assert data['recommended_route'] in (
        'CONTINUE', 'STABILIZE', 'LOW_CAPITAL', 'OPERATIONS_CLEANUP',
        'IMPACT_SOCIAL', 'DEEP_TECH', 'DEBT_CONSCIOUS', 'CORPORATE_TRANSITION',
        'ACCELERATE', 'HARD_STOP',
    )


def test_phase1_submit_returns_founder_matrix(client):
    with client.application.app_context():
        user = make_user(db.session)
        token = make_session(db.session, user)
        db.session.commit()

    resp = client.post('/api/v1/phase1/submit', json=VALID_PAYLOAD, headers=auth(token))
    data = resp.get_json()

    # phase1/submit response has top-level 'dimensions' (not founder_matrix)
    assert 'dimensions' in data
    dims = data['dimensions']

    for dim in ['financial', 'motivation_quality', 'time_capacity', 'legal_employment']:
        assert dim in dims, f"Missing dimension: {dim}"
        assert 'score' in dims[dim]


def test_phase1_submit_returns_phase_gates_string_keys(client):
    """Phase gates in response must use string keys '1'-'7'."""
    with client.application.app_context():
        user = make_user(db.session)
        token = make_session(db.session, user)
        db.session.commit()

    resp = client.post('/api/v1/phase1/submit', json=VALID_PAYLOAD, headers=auth(token))
    data = resp.get_json()

    assert 'phase_gates' in data
    gates = data['phase_gates']
    assert isinstance(gates, dict)
    for key in gates:
        assert isinstance(key, str), f"Gate key must be a string, got {type(key)}"
    assert '1' in gates


# ─── Versioning ────────────────────────────────────────────────────────────────

def test_phase1_resubmit_increments_version(client):
    """Re-submitting Phase 1 creates a new FRP version, marks old as not latest."""
    with client.application.app_context():
        user = make_user(db.session)
        token = make_session(db.session, user)
        db.session.commit()
        uid = user.id

    client.post('/api/v1/phase1/submit', json=VALID_PAYLOAD, headers=auth(token))
    client.post('/api/v1/phase1/submit', json=VALID_PAYLOAD, headers=auth(token))

    with client.application.app_context():
        latest = FounderReadinessProfile.query.filter_by(user_id=uid, is_latest=True).first()
        assert latest is not None
        assert latest.version == 2

        old = FounderReadinessProfile.query.filter_by(user_id=uid, is_latest=False).first()
        assert old is not None
        assert old.version == 1


# ─── Business rules ────────────────────────────────────────────────────────────

def test_phase1_gate_status_in_progress_normal(client):
    """Phase 1 gate should be IN_PROGRESS (or COMPLETED) after a normal submission."""
    with client.application.app_context():
        user = make_user(db.session)
        token = make_session(db.session, user)
        db.session.commit()

    resp = client.post('/api/v1/phase1/submit', json=VALID_PAYLOAD, headers=auth(token))
    data = resp.get_json()

    gate_status = data['phase_gates'].get('1')
    assert gate_status in ('IN_PROGRESS', 'COMPLETED')


def test_phase1_illegal_venture_blocks(client):
    """illegal_venture=True should result in a STOP/BLOCKED route."""
    with client.application.app_context():
        user = make_user(db.session)
        token = make_session(db.session, user)
        db.session.commit()

    payload = {**VALID_PAYLOAD, 'illegal_venture': True}
    resp = client.post('/api/v1/phase1/submit', json=payload, headers=auth(token))
    assert resp.status_code == 200

    data = resp.get_json()
    route = data.get('recommended_route', '')
    gate1_status = data.get('phase_gates', {}).get('1', '')
    assert 'HARD_STOP' in route or gate1_status == 'BLOCKED', \
        f"Expected blocking state, got route={route} gate1={gate1_status}"


def test_phase1_minimal_required_fields_succeeds(client):
    """A submission with minimal required fields should succeed."""
    with client.application.app_context():
        user = make_user(db.session)
        token = make_session(db.session, user)
        db.session.commit()
        uid = user.id

    minimal = {
        'idea_description': 'A simple idea for testing',
        'motivation_raw': 'I want to test this',
        'motivation_type': 'MIXED',
        'target_user_description': 'Small business owners',
        'target_user_specific': True,
        'problem_defined': True,
        'weekly_available_hours': 5,
        'financial_runway_months': 3,
        'income_stable': False,
        'has_spoken_to_users': 'no',
        'has_non_compete': False,
        'employer_ip_risk': False,
        'immigration_restriction': False,
        'illegal_venture': False,
        'paying_customers_exist': False,
        'stress_level': 3,
        'burnout_signals': [],
        'life_chaos_signals': [],
        'energy_level': 3,
    }
    resp = client.post('/api/v1/phase1/submit', json=minimal, headers=auth(token))
    assert resp.status_code == 200

    with client.application.app_context():
        frp = FounderReadinessProfile.query.filter_by(user_id=uid).first()
        assert frp is not None


# ─── Venture profile reflects FRP after submit ─────────────────────────────────

def test_venture_profile_has_founder_matrix_after_submit(client):
    """After Phase 1 submit, GET /ventures/profile should return founder_matrix."""
    from src.models.venture_record import VentureRecord

    with client.application.app_context():
        user = make_user(db.session)
        token = make_session(db.session, user)
        venture = VentureRecord(
            user_id=user.id,
            is_active=True,
            idea_raw='Freelancer invoice app',
            idea_clarified='Automated invoice management for freelancers',
            venture_type='FORPROFIT',
        )
        db.session.add(venture)
        db.session.commit()

    client.post('/api/v1/phase1/submit', json=VALID_PAYLOAD, headers=auth(token))

    profile_resp = client.get('/api/v1/ventures/profile', headers=auth(token))
    assert profile_resp.status_code == 200

    profile_data = profile_resp.get_json()
    assert 'founder_matrix' in profile_data
    matrix = profile_data['founder_matrix']
    assert 'recommended_route' in matrix
    assert 'dimensions' in matrix


def test_venture_profile_phase_gates_after_submit(client):
    """After Phase 1 submit, GET /ventures/profile should have phase_gates."""
    from src.models.venture_record import VentureRecord

    with client.application.app_context():
        user = make_user(db.session)
        token = make_session(db.session, user)
        venture = VentureRecord(
            user_id=user.id, is_active=True,
            idea_raw='Test idea', idea_clarified='Test',
            venture_type='FORPROFIT',
        )
        db.session.add(venture)
        db.session.commit()

    client.post('/api/v1/phase1/submit', json=VALID_PAYLOAD, headers=auth(token))

    profile_resp = client.get('/api/v1/ventures/profile', headers=auth(token))
    data = profile_resp.get_json()

    assert 'phase_gates' in data
    gates = data['phase_gates']
    assert '1' in gates
    gate1 = gates['1']
    # venture profile returns full gate objects with 'status' key
    status = gate1['status'] if isinstance(gate1, dict) else gate1
    assert status in ('IN_PROGRESS', 'COMPLETED', 'BLOCKED')
