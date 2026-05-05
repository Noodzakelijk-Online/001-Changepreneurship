"""
Security tests — Actions API (Sprint 4, S4-07)
Tests: IDOR, duplicate, token, rate limit, state machine invariants
"""
import pytest
from datetime import datetime, timedelta

from src.models.assessment import db, User, UserSession
from src.models.user_action import UserAction, REQUIRES_APPROVAL, AUTO_APPROVE
from src.services.user_action_service import UserActionService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_user(db_session, username, email):
    u = User(username=username, email=email, password_hash='x' * 60)
    db_session.add(u)
    db_session.flush()
    return u


def make_session(db_session, user_id, token):
    s = UserSession(
        user_id=user_id,
        session_token=token,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    db_session.add(s)
    db_session.flush()
    return s


def auth(token):
    return {'Authorization': f'Bearer {token}'}


# ---------------------------------------------------------------------------
# IDOR tests — user cannot act on another user's action
# ---------------------------------------------------------------------------
class TestIDOR:
    def test_approve_other_user_action_denied(self, client, app):
        with app.app_context():
            u1 = make_user(db.session, 'idor_u1', 'idor1@test.com')
            u2 = make_user(db.session, 'idor_u2', 'idor2@test.com')
            make_session(db.session, u1.id, 'idor-tok1')
            make_session(db.session, u2.id, 'idor-tok2')
            action = UserAction(
                user_id=u1.id,
                action_type='SEND_OUTREACH',
                action_data={'to': 'mentor@test.com'},
                approval_status='PROPOSED',
                proposed_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24),
                audit_trail=[],
            )
            db.session.add(action)
            db.session.commit()
            action_id = action.id

        # u2 tries to approve u1's action — should fail
        resp = client.post(
            f'/api/v1/actions/{action_id}/approve',
            headers=auth('idor-tok2'),
        )
        assert resp.status_code in (400, 404)

    def test_reject_other_user_action_denied(self, client, app):
        with app.app_context():
            u1 = make_user(db.session, 'idor_r1', 'idorr1@test.com')
            u2 = make_user(db.session, 'idor_r2', 'idorr2@test.com')
            make_session(db.session, u1.id, 'idor-rtok1')
            make_session(db.session, u2.id, 'idor-rtok2')
            action = UserAction(
                user_id=u1.id,
                action_type='SEND_OUTREACH',
                action_data={'to': 'mentor@test.com'},
                approval_status='PROPOSED',
                proposed_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24),
                audit_trail=[],
            )
            db.session.add(action)
            db.session.commit()
            action_id = action.id

        resp = client.post(
            f'/api/v1/actions/{action_id}/reject',
            json={'reason': 'not mine'},
            headers=auth('idor-rtok2'),
        )
        assert resp.status_code in (400, 404)

    def test_outcome_other_user_denied(self, client, app):
        with app.app_context():
            u1 = make_user(db.session, 'idor_out1', 'idoro1@test.com')
            u2 = make_user(db.session, 'idor_out2', 'idoro2@test.com')
            make_session(db.session, u1.id, 'idor-otok1')
            make_session(db.session, u2.id, 'idor-otok2')
            action = UserAction(
                user_id=u1.id,
                action_type='SEND_OUTREACH',
                action_data={'to': 'mentor@test.com'},
                approval_status='EXECUTED',
                proposed_at=datetime.utcnow(),
                executed_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24),
                audit_trail=[],
            )
            db.session.add(action)
            db.session.commit()
            action_id = action.id

        resp = client.post(
            f'/api/v1/actions/{action_id}/outcome',
            json={'outcome': 'Got response'},
            headers=auth('idor-otok2'),
        )
        assert resp.status_code in (400, 404)


# ---------------------------------------------------------------------------
# Duplicate action detection
# ---------------------------------------------------------------------------
class TestDuplicateDetection:
    def test_duplicate_propose_rejected(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'dup_user', 'dup@test.com')
            make_session(db.session, u.id, 'dup-tok')
            db.session.commit()

        payload = {
            'action_type': 'SEND_OUTREACH',
            'action_data': {'mentor_id': 'mentor_1', 'subject': 'Help'},
            'rationale': 'First attempt',
        }
        resp1 = client.post('/api/v1/actions/propose', json=payload, headers=auth('dup-tok'))
        assert resp1.status_code == 201

        resp2 = client.post('/api/v1/actions/propose', json=payload, headers=auth('dup-tok'))
        assert resp2.status_code == 409  # Conflict — duplicate


# ---------------------------------------------------------------------------
# Token / Auth security
# ---------------------------------------------------------------------------
class TestTokenSecurity:
    def test_no_token_returns_401(self, client):
        resp = client.get('/api/v1/actions/pending')
        assert resp.status_code in (401, 403)

    def test_invalid_token_returns_401(self, client):
        resp = client.get(
            '/api/v1/actions/pending',
            headers={'Authorization': 'Bearer definitely-invalid-token-xyz'},
        )
        assert resp.status_code in (401, 403)

    def test_expired_session_returns_401(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'expired_user', 'exp@test.com')
            expired_session = UserSession(
                user_id=u.id,
                session_token='expired-tok',
                is_active=True,
                expires_at=datetime.utcnow() - timedelta(hours=1),
            )
            db.session.add(expired_session)
            db.session.commit()

        resp = client.get(
            '/api/v1/actions/pending',
            headers={'Authorization': 'Bearer expired-tok'},
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# State machine invariants
# ---------------------------------------------------------------------------
class TestStateMachineInvariants:
    def test_cannot_execute_without_approved(self, app):
        """CEO invariant: QUEUED → EXECUTED requires prior APPROVED."""
        svc = UserActionService()
        with app.app_context():
            u = make_user(db.session, 'inv_user', 'inv@test.com')
            action = UserAction(
                user_id=u.id,
                action_type='SEND_OUTREACH',
                action_data={'mentor': 'x'},
                approval_status='PROPOSED',
                proposed_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24),
                audit_trail=[],
            )
            db.session.add(action)
            db.session.commit()
            action_id = action.id

        with app.app_context():
            with pytest.raises(ValueError, match='APPROVED'):
                svc.queue_action(action_id)

    def test_cannot_queue_proposed(self, app):
        svc = UserActionService()
        with app.app_context():
            u = make_user(db.session, 'inv_user2', 'inv2@test.com')
            action = UserAction(
                user_id=u.id,
                action_type='SEND_OUTREACH',
                action_data={'x': 1},
                approval_status='PROPOSED',
                proposed_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24),
                audit_trail=[],
            )
            db.session.add(action)
            db.session.commit()
            action_id = action.id

        with app.app_context():
            with pytest.raises(ValueError):
                svc.queue_action(action_id)

    def test_terminal_state_no_transitions(self, app):
        """Actions in terminal states cannot be transitioned."""
        with app.app_context():
            u = make_user(db.session, 'term_user', 'term@test.com')
            action = UserAction(
                user_id=u.id,
                action_type='SEND_OUTREACH',
                action_data={},
                approval_status='REJECTED',
                proposed_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24),
                audit_trail=[],
            )
            db.session.add(action)
            db.session.commit()
            assert not action.can_transition_to('PROPOSED')
            assert not action.can_transition_to('APPROVED')
            assert not action.can_transition_to('QUEUED')

    def test_auto_approve_skips_manual_review(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'auto_app', 'aa@test.com')
            make_session(db.session, u.id, 'auto-app-tok')
            db.session.commit()

        resp = client.post(
            '/api/v1/actions/propose',
            json={
                'action_type': 'SEARCH_MENTORS',
                'action_data': {'expertise': ['SaaS']},
            },
            headers=auth('auto-app-tok'),
        )
        assert resp.status_code == 201
        data = resp.get_json()
        # AUTO_APPROVE types should be immediately APPROVED
        assert data['action']['approval_status'] == 'APPROVED'


# ---------------------------------------------------------------------------
# Actions endpoint basic tests
# ---------------------------------------------------------------------------
class TestActionsEndpoints:
    def test_propose_action_requires_action_type(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'prop_user', 'prop@test.com')
            make_session(db.session, u.id, 'prop-tok')
            db.session.commit()

        resp = client.post(
            '/api/v1/actions/propose',
            json={'action_data': {}},
            headers=auth('prop-tok'),
        )
        assert resp.status_code == 400

    def test_pending_actions_empty_initially(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'pend_user', 'pend@test.com')
            make_session(db.session, u.id, 'pend-tok')
            db.session.commit()

        resp = client.get('/api/v1/actions/pending', headers=auth('pend-tok'))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['count'] == 0

    def test_history_returns_actions(self, client, app):
        with app.app_context():
            u = make_user(db.session, 'hist_user', 'hist@test.com')
            make_session(db.session, u.id, 'hist-tok')
            db.session.commit()

        # Propose one
        client.post(
            '/api/v1/actions/propose',
            json={'action_type': 'DRAFT_OUTREACH', 'action_data': {'mentor': 'test'}},
            headers=auth('hist-tok'),
        )

        resp = client.get('/api/v1/actions/history', headers=auth('hist-tok'))
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['history']) >= 1
