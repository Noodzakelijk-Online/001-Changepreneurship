"""
Integration tests for Phase 1 API endpoint.

These tests exercise the full request → rule engine → DB → response pipeline
using the Flask test client and in-memory SQLite (from conftest.py).

AI narrative is mocked — we do not call real Groq API in tests.

Run: pytest tests/test_phase1_integration.py -v
"""
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytest

from src.models.assessment import db
from src.models.assessment import User, UserSession


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _create_user(app):
    """Create a test user and session in the DB."""
    with app.app_context():
        user = User(
            username='testfounder',
            email='founder@test.com',
            password_hash='hashed_pw',
        )
        db.session.add(user)
        db.session.flush()

        session = UserSession(
            user_id=user.id,
            session_token='test-token-phase1',
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db.session.add(session)
        db.session.commit()
        return user.id, 'test-token-phase1'


def _auth_headers(token):
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


def _payload_hard_block():
    """Scenario A: Zero runway — should return Hard Block."""
    return {
        'financial_runway_months': 0,
        'income_stable': False,
        'weekly_available_hours': 40,
        'stress_level': 2,
        'burnout_signals': [],
        'life_chaos_signals': [],
        'problem_defined': True,
        'target_user_specific': True,
        'motivation_type': 'PASSION',
        'just_quit_job': True,
    }


def _payload_healthy():
    """Scenario B: All-clear — should return level <= 1."""
    return {
        'financial_runway_months': 18,
        'income_stable': True,
        'high_debt': False,
        'weekly_available_hours': 20,
        'schedule_flexibility': 4,
        'stress_level': 1,
        'burnout_signals': [],
        'life_chaos_signals': [],
        'problem_defined': True,
        'target_user_specific': True,
        'value_prop_clear': True,
        'domain_skill_level': 4,
        'relevant_experience_years': 5,
        'execution_history': True,
        'illegal_venture': False,
        'employer_ip_risk': False,
        'energy_level': 4,
        'motivation_type': 'MISSION',
        'mission_clarity': 4,
    }


def _payload_overload():
    """Scenario F: Overload — operations cleanup route."""
    return {
        'financial_runway_months': 12,
        'income_stable': True,
        'weekly_available_hours': 80,
        'paying_customers_exist': True,
        'stress_level': 4,
        'burnout_signals': ['extreme_urgency'],
        'life_chaos_signals': [],
        'problem_defined': True,
        'target_user_specific': True,
        'value_prop_clear': True,
    }


def _payload_hard_stop():
    """Illegal venture — should return Hard Stop."""
    return {
        'illegal_venture': True,
        'financial_runway_months': 24,
        'income_stable': True,
    }


# ---------------------------------------------------------------------------
# Fixture: mock narrative service to avoid Groq calls
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def mock_narrative():
    """Prevent any real Groq API calls during integration tests."""
    mock_result = {
        'founder_readiness_narrative': 'Test narrative',
        'primary_strength': 'Test strength',
        'primary_risk': 'Test risk',
        'next_step_explanation': 'Test next step',
        'what_not_to_do': ['Do not rush'],
        'confidence': 'MEDIUM',
        'is_template': True,
    }
    with patch(
        'src.services.phase1_narrative_service.Phase1NarrativeService.generate_narrative',
        return_value=mock_result,
    ):
        yield


# ---------------------------------------------------------------------------
# Tests: Authentication
# ---------------------------------------------------------------------------
class TestPhase1Auth:
    def test_requires_auth(self, client):
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps({'financial_runway_months': 6}),
            content_type='application/json',
        )
        assert resp.status_code in (401, 403)

    def test_invalid_token_rejected(self, client):
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps({'financial_runway_months': 6}),
            content_type='application/json',
            headers={'Authorization': 'Bearer invalid-token-xyz'},
        )
        assert resp.status_code in (401, 403)

    def test_invalid_body_rejected(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data='not json',
            content_type='application/json',
            headers=_auth_headers(token),
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Tests: Hard Block (Scenario A — zero runway)
# ---------------------------------------------------------------------------
class TestScenarioAIntegration:
    def test_hard_block_returns_200(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_hard_block()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        assert resp.status_code == 200

    def test_hard_block_overall_level_4(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_hard_block()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        assert data['overall_readiness_level'] == 4

    def test_hard_block_has_active_blockers(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_hard_block()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        assert len(data['active_blockers']) > 0

    def test_hard_block_paid_dev_blocked(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_hard_block()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        blocked_actions = [b['action'] for b in data['blocked_actions']]
        assert 'paid_development' in blocked_actions

    def test_hard_block_phase2_remains_locked(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_hard_block()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        gates = data.get('phase_gates', {})
        assert gates.get('2') in ('LOCKED', None)

    def test_hard_block_profile_persisted(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_hard_block()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        assert 'profile_id' in data
        assert data['profile_id'] > 0


# ---------------------------------------------------------------------------
# Tests: Healthy Founder
# ---------------------------------------------------------------------------
class TestHealthyFounderIntegration:
    def test_healthy_level_ok_or_better(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_healthy()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['overall_readiness_level'] <= 1

    def test_healthy_no_active_blockers(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_healthy()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        assert len(data['active_blockers']) == 0

    def test_healthy_all_actions_allowed(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_healthy()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        assert 'all_actions' in data['allowed_actions']


# ---------------------------------------------------------------------------
# Tests: Overload / Operations Cleanup (Scenario F)
# ---------------------------------------------------------------------------
class TestOverloadIntegration:
    def test_overload_route(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_overload()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['recommended_route'] == 'OPERATIONS_CLEANUP'
        assert data['overload_signal'] is True

    def test_overload_blocks_expansion(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_overload()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        blocked = [b['action'] for b in data['blocked_actions']]
        assert 'new_market_expansion' in blocked


# ---------------------------------------------------------------------------
# Tests: Hard Stop (illegal venture)
# ---------------------------------------------------------------------------
class TestHardStopIntegration:
    def test_hard_stop_level_5(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_hard_stop()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['overall_readiness_level'] == 5
        assert data['recommended_route'] == 'HARD_STOP'


# ---------------------------------------------------------------------------
# Tests: Versioning (re-submit creates new version)
# ---------------------------------------------------------------------------
class TestVersioningIntegration:
    def test_resubmit_increments_version(self, client, app):
        user_id, token = _create_user(app)
        headers = _auth_headers(token)

        # First submit
        resp1 = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_hard_block()),
            content_type='application/json',
            headers=headers,
        )
        data1 = resp1.get_json()

        # Second submit (same or different answers)
        resp2 = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_healthy()),
            content_type='application/json',
            headers=headers,
        )
        data2 = resp2.get_json()

        assert data2['version'] == 2
        # Profile IDs should be different (new row created)
        assert data2['profile_id'] != data1['profile_id']

    def test_resubmit_latest_version_updates(self, client, app):
        user_id, token = _create_user(app)
        headers = _auth_headers(token)

        client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_hard_block()),
            content_type='application/json',
            headers=headers,
        )
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_healthy()),
            content_type='application/json',
            headers=headers,
        )
        data = resp.get_json()
        # Latest submission should reflect the healthy payload
        assert data['overall_readiness_level'] <= 1


# ---------------------------------------------------------------------------
# Tests: Response structure
# ---------------------------------------------------------------------------
class TestResponseStructure:
    def test_response_has_required_keys(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_hard_block()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        required_keys = [
            'profile_id', 'version', 'overall_readiness_level', 'recommended_route',
            'active_blockers', 'allowed_actions', 'blocked_actions',
            'phase_gates', 'dimensions', 'ai_narrative',
        ]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"

    def test_dimensions_has_all_required_dims(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_healthy()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        dims = data['dimensions']
        for dim in ['financial', 'time_capacity', 'personal_stability', 'skills_experience', 'idea_clarity']:
            assert dim in dims, f"Missing dimension: {dim}"
            assert 'score' in dims[dim]
            assert 'level' in dims[dim]

    def test_ai_narrative_has_required_keys(self, client, app):
        user_id, token = _create_user(app)
        resp = client.post(
            '/api/v1/phase1/submit',
            data=json.dumps(_payload_healthy()),
            content_type='application/json',
            headers=_auth_headers(token),
        )
        data = resp.get_json()
        narrative = data['ai_narrative']
        for key in ['narrative', 'primary_strength', 'primary_risk', 'next_step_explanation', 'what_not_to_do']:
            assert key in narrative, f"Missing narrative key: {key}"
