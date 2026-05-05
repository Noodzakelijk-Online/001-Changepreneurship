"""
Sprint 15: Account Management tests

Tests:
- POST /auth/change-password — auth required
- POST /auth/change-password — wrong current password → 401
- POST /auth/change-password — missing fields → 400
- POST /auth/change-password — weak new password → 422
- POST /auth/change-password — same as current → 422
- POST /auth/change-password — success
- POST /auth/change-password — can login with new password after change
- PATCH /users/me — auth required
- PATCH /users/me — missing username → 400
- PATCH /users/me — username too short → 422
- PATCH /users/me — duplicate username → 409
- PATCH /users/me — success, returns updated user
- PATCH /users/me — user isolation (cannot affect other user's session)
"""
import pytest
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash, check_password_hash

from src.models.assessment import db, User, UserSession


_CTR = [0]


def _uniq(p='u'):
    _CTR[0] += 1
    return f"{p}_{_CTR[0]}"


def make_user(session, password='Valid#Pass1!'):
    u = User(
        username=_uniq('user'),
        email=_uniq('e') + '@test.com',
        password_hash=generate_password_hash(password),
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


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/v1/auth/change-password
# ─────────────────────────────────────────────────────────────────────────────

class TestChangePassword:
    def test_requires_auth(self, client):
        r = client.post('/api/v1/auth/change-password', json={
            'current_password': 'Valid#Pass1!',
            'new_password': 'NewValid#Pass2!',
        })
        assert r.status_code == 401

    def test_missing_current_password(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.post('/api/v1/auth/change-password',
                        json={'new_password': 'NewValid#Pass2!'},
                        headers=auth_headers(tok))
        assert r.status_code == 400

    def test_missing_new_password(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.post('/api/v1/auth/change-password',
                        json={'current_password': 'Valid#Pass1!'},
                        headers=auth_headers(tok))
        assert r.status_code == 400

    def test_wrong_current_password(self, client):
        with client.application.app_context():
            u = make_user(db.session, password='Valid#Pass1!')
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.post('/api/v1/auth/change-password',
                        json={'current_password': 'WrongPass#1!', 'new_password': 'NewValid#Pass2!'},
                        headers=auth_headers(tok))
        assert r.status_code == 401

    def test_weak_new_password(self, client):
        with client.application.app_context():
            u = make_user(db.session, password='Valid#Pass1!')
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.post('/api/v1/auth/change-password',
                        json={'current_password': 'Valid#Pass1!', 'new_password': 'tooshort'},
                        headers=auth_headers(tok))
        assert r.status_code == 422

    def test_same_as_current(self, client):
        with client.application.app_context():
            u = make_user(db.session, password='Valid#Pass1!')
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.post('/api/v1/auth/change-password',
                        json={'current_password': 'Valid#Pass1!', 'new_password': 'Valid#Pass1!'},
                        headers=auth_headers(tok))
        assert r.status_code == 422

    def test_success(self, client):
        with client.application.app_context():
            u = make_user(db.session, password='Valid#Pass1!')
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.post('/api/v1/auth/change-password',
                        json={'current_password': 'Valid#Pass1!', 'new_password': 'NewValid#Pass2!'},
                        headers=auth_headers(tok))
        assert r.status_code == 200
        assert r.get_json()['success'] is True

    def test_password_actually_changed_in_db(self, client):
        """After change, old hash should no longer match."""
        with client.application.app_context():
            u = make_user(db.session, password='Valid#Pass1!')
            uid = u.id
            tok = make_session(db.session, u)
            db.session.commit()

        client.post('/api/v1/auth/change-password',
                    json={'current_password': 'Valid#Pass1!', 'new_password': 'NewValid#Pass2!'},
                    headers=auth_headers(tok))

        with client.application.app_context():
            fresh = User.query.get(uid)
            assert check_password_hash(fresh.password_hash, 'NewValid#Pass2!')
            assert not check_password_hash(fresh.password_hash, 'Valid#Pass1!')

    def test_no_body(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.post('/api/v1/auth/change-password',
                        headers=auth_headers(tok),
                        content_type='application/json')
        assert r.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# PATCH /api/v1/users/me
# ─────────────────────────────────────────────────────────────────────────────

class TestUpdateMe:
    def test_requires_auth(self, client):
        r = client.patch('/api/v1/users/me', json={'username': 'newname'})
        assert r.status_code == 401

    def test_missing_username(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.patch('/api/v1/users/me', json={}, headers=auth_headers(tok))
        assert r.status_code == 400

    def test_username_too_short(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.patch('/api/v1/users/me', json={'username': 'ab'}, headers=auth_headers(tok))
        assert r.status_code == 422

    def test_username_duplicate(self, client):
        with client.application.app_context():
            u1 = make_user(db.session)
            u2 = make_user(db.session)
            existing_name = u1.username
            tok2 = make_session(db.session, u2)
            db.session.commit()
        r = client.patch('/api/v1/users/me',
                         json={'username': existing_name},
                         headers=auth_headers(tok2))
        assert r.status_code == 409

    def test_success(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            uid = u.id
            tok = make_session(db.session, u)
            db.session.commit()
        new_name = _uniq('newname')
        r = client.patch('/api/v1/users/me',
                         json={'username': new_name},
                         headers=auth_headers(tok))
        assert r.status_code == 200
        body = r.get_json()
        assert body['success'] is True
        assert body['user']['username'] == new_name

    def test_success_persists_in_db(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            uid = u.id
            tok = make_session(db.session, u)
            db.session.commit()
        new_name = _uniq('persisted')
        client.patch('/api/v1/users/me',
                     json={'username': new_name},
                     headers=auth_headers(tok))
        with client.application.app_context():
            fresh = User.query.get(uid)
            assert fresh.username == new_name

    def test_same_username_allowed(self, client):
        """Updating to own current username should succeed (no conflict with self)."""
        with client.application.app_context():
            u = make_user(db.session)
            own_name = u.username
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.patch('/api/v1/users/me',
                         json={'username': own_name},
                         headers=auth_headers(tok))
        assert r.status_code == 200

    def test_no_body(self, client):
        with client.application.app_context():
            u = make_user(db.session)
            tok = make_session(db.session, u)
            db.session.commit()
        r = client.patch('/api/v1/users/me',
                         headers=auth_headers(tok),
                         content_type='application/json')
        assert r.status_code == 400

    def test_user_isolation(self, client):
        """Updating /users/me only affects the authenticated user."""
        with client.application.app_context():
            ua = make_user(db.session)
            ub = make_user(db.session)
            original_b = ub.username
            tok_a = make_session(db.session, ua)
            db.session.commit()

        # User A updates their own name — user B's name must not change
        client.patch('/api/v1/users/me',
                     json={'username': _uniq('renamed_a')},
                     headers=auth_headers(tok_a))

        with client.application.app_context():
            fresh_b = User.query.filter_by(username=original_b).first()
            assert fresh_b is not None, "User B should still have original username"
