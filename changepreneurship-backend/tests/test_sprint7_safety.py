"""
Sprint 7 tests — Safety Foundation
Tests: ExternalConnection, DataConsentLog, Venture, safety API auth guards,
       Phase1→UserAction loop, consent grant/revoke, connection CRUD.

26 tests total.
"""
import pytest
from datetime import datetime, timedelta

from src.models.assessment import db, User, UserSession
from src.models.external_connection import (
    ExternalConnection,
    PLATFORM_EMAIL, PLATFORM_MICROMENTOR,
    STATUS_PENDING, STATUS_ACTIVE, STATUS_REVOKED,
    PERM_DRAFT, PERM_READ_ONLY, PERM_SEND, PERM_FULL,
)
from src.models.data_consent_log import (
    DataConsentLog,
    CATEGORY_ASSESSMENT, CATEGORY_AI_PROCESSING, CATEGORY_BENCHMARK,
    CATEGORY_OUTREACH, CATEGORY_ACCOUNT_CONN, CATEGORY_SENSITIVE,
    REQUIRED_FOR_SERVICE, REQUIRES_EXPLICIT_CONSENT,
    get_user_consent_status, has_consent, record_consent,
)
from src.models.venture import (
    Venture,
    STAGE_IDEA, STAGE_CLARIFYING,
    STATUS_ACTIVE as VENTURE_ACTIVE, STATUS_ARCHIVED,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_user(session, username='testuser', email='test@example.com'):
    u = User(username=username, email=email, password_hash='x' * 60)
    session.add(u)
    session.flush()
    return u


def make_session(session, user_id, token='test-token'):
    s = UserSession(
        user_id=user_id,
        session_token=token,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    session.add(s)
    session.flush()
    return s


def auth(token='test-token'):
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


# ===========================================================================
# ExternalConnection model unit tests
# ===========================================================================

class TestExternalConnectionModel:
    def test_create_connection_pending(self, app):
        with app.app_context():
            u = make_user(db.session)
            conn = ExternalConnection(
                user_id=u.id,
                platform=PLATFORM_EMAIL,
                permission_level=PERM_DRAFT,
            )
            db.session.add(conn)
            db.session.commit()

            assert conn.id is not None
            assert conn.connection_status == STATUS_PENDING
            assert not conn.is_active()

    def test_activate_connection(self, app):
        with app.app_context():
            u = make_user(db.session)
            conn = ExternalConnection(user_id=u.id, platform=PLATFORM_EMAIL)
            db.session.add(conn)
            db.session.flush()

            conn.activate(
                access_token='tok_abc',
                refresh_token='ref_xyz',
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )
            db.session.commit()

            assert conn.connection_status == STATUS_ACTIVE
            assert conn.is_active()
            # Decrypted value must always match original (encrypted or plaintext dev fallback)
            assert conn.access_token == 'tok_abc'
            assert conn.refresh_token == 'ref_xyz'

    def test_revoke_wipes_tokens(self, app):
        with app.app_context():
            u = make_user(db.session)
            conn = ExternalConnection(user_id=u.id, platform=PLATFORM_EMAIL)
            conn.activate('tok_abc', 'ref_xyz')
            db.session.add(conn)
            db.session.flush()

            conn.revoke()
            db.session.commit()

            assert conn.connection_status == STATUS_REVOKED
            assert conn._encrypted_access_token is None
            assert conn._encrypted_refresh_token is None
            assert not conn.is_active()

    def test_expired_connection_not_active(self, app):
        with app.app_context():
            u = make_user(db.session)
            conn = ExternalConnection(user_id=u.id, platform=PLATFORM_EMAIL)
            conn.activate(
                'tok',
                expires_at=datetime.utcnow() - timedelta(hours=1),  # already expired
            )
            db.session.add(conn)
            db.session.commit()

            # Status is ACTIVE but token is expired → is_active() returns False
            assert conn.connection_status == STATUS_ACTIVE
            assert not conn.is_active()

    def test_permission_hierarchy(self, app):
        with app.app_context():
            u = make_user(db.session)
            conn = ExternalConnection(
                user_id=u.id, platform=PLATFORM_EMAIL, permission_level=PERM_SEND
            )
            db.session.add(conn)
            db.session.commit()

            assert conn.can_perform(PERM_READ_ONLY)  # READ_ONLY ≤ SEND
            assert conn.can_perform(PERM_DRAFT)       # DRAFT ≤ SEND
            assert conn.can_perform(PERM_SEND)        # SEND == SEND
            assert not conn.can_perform(PERM_FULL)    # FULL > SEND

    def test_to_dict_never_includes_tokens(self, app):
        with app.app_context():
            u = make_user(db.session)
            conn = ExternalConnection(user_id=u.id, platform=PLATFORM_EMAIL)
            conn.activate('super_secret_token')
            db.session.add(conn)
            db.session.commit()

            d = conn.to_dict()
            assert 'access_token' not in d
            assert 'refresh_token' not in d
            assert 'encrypted_access_token' not in d
            assert 'super_secret_token' not in str(d)


# ===========================================================================
# DataConsentLog model unit tests
# ===========================================================================

class TestDataConsentLogModel:
    def test_grant_consent(self, app):
        with app.app_context():
            u = make_user(db.session)
            record = record_consent(u.id, CATEGORY_AI_PROCESSING, given=True)
            db.session.commit()

            assert record.id is not None
            assert record.consent_given is True
            assert has_consent(u.id, CATEGORY_AI_PROCESSING)

    def test_revoke_consent(self, app):
        with app.app_context():
            u = make_user(db.session)
            record_consent(u.id, CATEGORY_AI_PROCESSING, given=True)
            record_consent(u.id, CATEGORY_AI_PROCESSING, given=False)
            db.session.commit()

            assert not has_consent(u.id, CATEGORY_AI_PROCESSING)

    def test_get_user_consent_status(self, app):
        with app.app_context():
            u = make_user(db.session)
            record_consent(u.id, CATEGORY_ASSESSMENT, given=True)
            record_consent(u.id, CATEGORY_BENCHMARK, given=True)
            db.session.commit()

            status = get_user_consent_status(u.id)
            assert status[CATEGORY_ASSESSMENT] is True
            assert status[CATEGORY_BENCHMARK] is True
            assert status[CATEGORY_AI_PROCESSING] is False  # not granted

    def test_latest_record_wins(self, app):
        with app.app_context():
            u = make_user(db.session)
            record_consent(u.id, CATEGORY_SENSITIVE, given=True)
            record_consent(u.id, CATEGORY_SENSITIVE, given=False)
            record_consent(u.id, CATEGORY_SENSITIVE, given=True)  # granted again
            db.session.commit()

            assert has_consent(u.id, CATEGORY_SENSITIVE)

    def test_invalid_category_raises(self, app):
        with app.app_context():
            u = make_user(db.session)
            with pytest.raises(ValueError, match='Unknown consent category'):
                record_consent(u.id, 'MADE_UP_CATEGORY', given=True)

    def test_required_for_service_not_revocable_via_api(self, client, app):
        """The API should reject revoke for REQUIRED_FOR_SERVICE categories."""
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            # Grant first
            record_consent(u.id, CATEGORY_ASSESSMENT, given=True)
            db.session.commit()

        resp = client.post('/api/v1/consent/revoke',
                           json={'categories': [CATEGORY_ASSESSMENT]},
                           headers=auth())
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data


# ===========================================================================
# Venture model unit tests
# ===========================================================================

class TestVentureModel:
    def test_create_venture(self, app):
        with app.app_context():
            u = make_user(db.session)
            v = Venture(user_id=u.id, venture_name='Test Idea', venture_stage=STAGE_IDEA)
            db.session.add(v)
            db.session.commit()

            assert v.id is not None
            assert v.status == VENTURE_ACTIVE
            assert v.is_primary is True

    def test_archive_venture(self, app):
        with app.app_context():
            u = make_user(db.session)
            v = Venture(user_id=u.id, venture_name='Old Idea')
            db.session.add(v)
            db.session.flush()

            v.archive(reason='Changed direction')
            db.session.commit()

            assert v.status == STATUS_ARCHIVED
            assert v.archived_at is not None
            assert 'Changed direction' in v.notes

    def test_venture_dict(self, app):
        with app.app_context():
            u = make_user(db.session)
            v = Venture(user_id=u.id, venture_name='My Co', venture_type='FORPROFIT')
            db.session.add(v)
            db.session.commit()

            d = v.to_dict()
            assert d['venture_name'] == 'My Co'
            assert d['venture_type'] == 'FORPROFIT'
            assert d['status'] == VENTURE_ACTIVE


# ===========================================================================
# Safety API endpoint tests
# ===========================================================================

class TestConsentAPI:
    def _create_user_and_session(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            db.session.commit()

    def test_get_consent_status_requires_auth(self, client):
        resp = client.get('/api/v1/consent/status')
        assert resp.status_code == 401

    def test_get_consent_status(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            db.session.commit()

        resp = client.get('/api/v1/consent/status', headers=auth())
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'consent' in data
        assert 'AI_PROCESSING' in data['consent']

    def test_grant_consent(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            db.session.commit()

        resp = client.post('/api/v1/consent/grant',
                           json={'categories': ['AI_PROCESSING', 'BENCHMARK_SHARING']},
                           headers=auth())
        assert resp.status_code == 201
        data = resp.get_json()
        assert 'AI_PROCESSING' in data['granted']
        assert 'BENCHMARK_SHARING' in data['granted']

    def test_revoke_consent(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            record_consent(u.id, CATEGORY_AI_PROCESSING, given=True)
            db.session.commit()

        resp = client.post('/api/v1/consent/revoke',
                           json={'categories': ['AI_PROCESSING']},
                           headers=auth())
        assert resp.status_code == 200

    def test_consent_audit_log(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            record_consent(u.id, CATEGORY_BENCHMARK, given=True)
            db.session.commit()

        resp = client.get('/api/v1/consent/log', headers=auth())
        assert resp.status_code == 200
        assert len(resp.get_json()['log']) >= 1

    def test_grant_unknown_category_rejected(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            db.session.commit()

        resp = client.post('/api/v1/consent/grant',
                           json={'categories': ['NONEXISTENT_CAT']},
                           headers=auth())
        assert resp.status_code == 400


class TestConnectionsAPI:
    def test_list_connections_requires_auth(self, client):
        resp = client.get('/api/v1/connections')
        assert resp.status_code == 401

    def test_list_connections_empty(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            db.session.commit()

        resp = client.get('/api/v1/connections', headers=auth())
        assert resp.status_code == 200
        assert resp.get_json()['connections'] == []

    def test_create_connection_requires_consent(self, client, app):
        """Must have ACCOUNT_CONNECTION consent before connecting an account."""
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            db.session.commit()

        resp = client.post('/api/v1/connections',
                           json={'platform': 'EMAIL', 'external_account_email': 'x@y.com'},
                           headers=auth())
        assert resp.status_code == 403
        assert 'ACCOUNT_CONNECTION' in resp.get_json().get('error', '')

    def test_create_connection_with_consent(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            record_consent(u.id, CATEGORY_ACCOUNT_CONN, given=True)
            db.session.commit()

        resp = client.post('/api/v1/connections',
                           json={
                               'platform': 'EMAIL',
                               'external_account_email': 'sender@example.com',
                               'permission_level': 'DRAFT',
                           },
                           headers=auth())
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['connection']['platform'] == 'EMAIL'
        assert 'access_token' not in data['connection']

    def test_revoke_connection(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            record_consent(u.id, CATEGORY_ACCOUNT_CONN, given=True)
            conn = ExternalConnection(user_id=u.id, platform=PLATFORM_EMAIL)
            conn.activate('tok')
            db.session.add(conn)
            db.session.commit()
            conn_id = conn.id

        resp = client.post(f'/api/v1/connections/{conn_id}/revoke', headers=auth())
        assert resp.status_code == 200
        assert resp.get_json()['connection']['connection_status'] == 'REVOKED'

    def test_delete_active_connection_blocked(self, client, app):
        """Cannot delete a connection that is still ACTIVE — must revoke first."""
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            record_consent(u.id, CATEGORY_ACCOUNT_CONN, given=True)
            conn = ExternalConnection(user_id=u.id, platform=PLATFORM_EMAIL)
            conn.activate('tok')
            db.session.add(conn)
            db.session.commit()
            conn_id = conn.id

        resp = client.delete(f'/api/v1/connections/{conn_id}', headers=auth())
        assert resp.status_code == 409

    def test_invalid_platform_rejected(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            record_consent(u.id, CATEGORY_ACCOUNT_CONN, given=True)
            db.session.commit()

        resp = client.post('/api/v1/connections',
                           json={'platform': 'TIKTOK'},
                           headers=auth())
        assert resp.status_code == 400


class TestVentureAPI:
    def test_list_ventures_requires_auth(self, client):
        resp = client.get('/api/v1/ventures')
        assert resp.status_code == 401

    def test_create_and_list_venture(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            db.session.commit()

        resp = client.post('/api/v1/ventures',
                           json={'venture_name': 'GreenTech Co', 'venture_type': 'SOCIAL'},
                           headers=auth())
        assert resp.status_code == 201
        v = resp.get_json()['venture']
        assert v['venture_name'] == 'GreenTech Co'

        list_resp = client.get('/api/v1/ventures', headers=auth())
        assert list_resp.status_code == 200
        assert len(list_resp.get_json()['ventures']) == 1

    def test_update_venture(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            v = Venture(user_id=u.id, venture_name='Draft Name')
            db.session.add(v)
            db.session.commit()
            v_id = v.id

        resp = client.patch(f'/api/v1/ventures/{v_id}',
                            json={'venture_name': 'Final Name'},
                            headers=auth())
        assert resp.status_code == 200
        assert resp.get_json()['venture']['venture_name'] == 'Final Name'

    def test_archive_venture(self, client, app):
        with app.app_context():
            u = make_user(db.session)
            make_session(db.session, u.id)
            v = Venture(user_id=u.id, venture_name='Old Idea')
            db.session.add(v)
            db.session.commit()
            v_id = v.id

        resp = client.post(f'/api/v1/ventures/{v_id}/archive',
                           json={'reason': 'Not viable'},
                           headers=auth())
        assert resp.status_code == 200
        assert resp.get_json()['venture']['status'] == 'ARCHIVED'

    def test_cannot_access_other_users_venture(self, client, app):
        """User A cannot access user B's venture."""
        with app.app_context():
            u1 = make_user(db.session, 'user1', 'u1@test.com')
            u2 = make_user(db.session, 'user2', 'u2@test.com')
            make_session(db.session, u1.id, 'tok1')
            make_session(db.session, u2.id, 'tok2')
            v = Venture(user_id=u2.id, venture_name='User2 Venture')
            db.session.add(v)
            db.session.commit()
            v_id = v.id

        # u1 tries to access u2's venture
        resp = client.get(f'/api/v1/ventures/{v_id}', headers=auth('tok1'))
        assert resp.status_code == 404
