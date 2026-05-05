"""
Sprint 7 API routes — Consent + External Connections + Venture.

Endpoints:
  Consent (GDPR):
    GET  /api/v1/consent/status          — all categories, current state
    POST /api/v1/consent/grant           — grant consent for category
    POST /api/v1/consent/revoke          — revoke consent for category
    GET  /api/v1/consent/log             — audit trail (last 50 records)

  External Connections:
    GET  /api/v1/connections             — list user's connections
    POST /api/v1/connections             — create/register a connection
    GET  /api/v1/connections/<id>        — get single connection
    POST /api/v1/connections/<id>/revoke — revoke a connection
    DELETE /api/v1/connections/<id>      — delete (after revoke)

  Ventures:
    GET  /api/v1/ventures                — list user's ventures
    POST /api/v1/ventures                — create a venture
    GET  /api/v1/ventures/<id>           — get single venture
    PATCH /api/v1/ventures/<id>          — update venture (name, type, etc.)
    POST /api/v1/ventures/<id>/archive   — archive a venture
"""
from datetime import datetime

from flask import Blueprint, request, jsonify

from src.models.assessment import db
from src.models.data_consent_log import (
    DataConsentLog,
    ALL_CATEGORIES,
    CATEGORY_DESCRIPTIONS,
    REQUIRES_EXPLICIT_CONSENT,
    REQUIRED_FOR_SERVICE,
    LEGAL_BASIS_CONSENT,
    LEGAL_BASIS_CONTRACT,
    get_user_consent_status,
    has_consent,
    record_consent,
)
from src.models.external_connection import (
    ExternalConnection,
    ALL_PLATFORMS,
    STATUS_PENDING,
    STATUS_ACTIVE,
    STATUS_REVOKED,
    PERM_DRAFT,
)
from src.models.venture import Venture, STATUS_ACTIVE as VENTURE_ACTIVE
from src.utils.auth import verify_session_token


safety_bp = Blueprint('safety', __name__)


# =============================================================================
# CONSENT ENDPOINTS
# =============================================================================

@safety_bp.route('/consent/status', methods=['GET'])
def get_consent_status():
    """Return current consent state for all categories."""
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    status = get_user_consent_status(user_id)
    return jsonify({
        'user_id': user_id,
        'consent': {
            cat: {
                'granted':     status[cat],
                'description': CATEGORY_DESCRIPTIONS.get(cat, ''),
                'required':    cat in REQUIRED_FOR_SERVICE,
                'sensitive':   cat in REQUIRES_EXPLICIT_CONSENT,
            }
            for cat in ALL_CATEGORIES
        }
    }), 200


@safety_bp.route('/consent/grant', methods=['POST'])
def grant_consent():
    """Grant consent for one or more categories."""
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    data = request.get_json(force=True) or {}

    categories = data.get('categories', [])
    if not categories:
        return jsonify({'error': 'categories list is required'}), 400

    text_version = data.get('consent_text_version', 'v1.0')
    context = {
        'ip': request.remote_addr,
        'user_agent': request.user_agent.string[:200] if request.user_agent else '',
        'source': data.get('source', 'ui'),
    }

    granted = []
    errors = []
    for cat in categories:
        if cat not in ALL_CATEGORIES:
            errors.append(f'Unknown category: {cat}')
            continue
        if cat in REQUIRED_FOR_SERVICE:
            legal_basis = LEGAL_BASIS_CONTRACT
        else:
            legal_basis = LEGAL_BASIS_CONSENT
        record_consent(user_id, cat, given=True,
                       legal_basis=legal_basis,
                       text_version=text_version,
                       context=context)
        granted.append(cat)

    if errors:
        db.session.rollback()
        return jsonify({'error': '; '.join(errors)}), 400

    db.session.commit()
    return jsonify({'granted': granted, 'message': 'Consent recorded'}), 201


@safety_bp.route('/consent/revoke', methods=['POST'])
def revoke_consent():
    """Revoke consent for one or more categories."""
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    data = request.get_json(force=True) or {}

    categories = data.get('categories', [])
    if not categories:
        return jsonify({'error': 'categories list is required'}), 400

    revoked = []
    errors = []
    for cat in categories:
        if cat not in ALL_CATEGORIES:
            errors.append(f'Unknown category: {cat}')
            continue
        if cat in REQUIRED_FOR_SERVICE:
            errors.append(f'{cat} is required for the service and cannot be revoked. '
                          'Delete your account to remove this data.')
            continue
        record_consent(user_id, cat, given=False,
                       legal_basis=LEGAL_BASIS_CONSENT,
                       context={'source': 'revoke_request'})
        revoked.append(cat)

    if errors and not revoked:
        db.session.rollback()
        return jsonify({'error': '; '.join(errors)}), 400

    db.session.commit()
    return jsonify({
        'revoked': revoked,
        'warnings': errors if errors else None,
    }), 200


@safety_bp.route('/consent/log', methods=['GET'])
def get_consent_log():
    """Return consent audit log for this user (last 50 records)."""
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    records = (
        DataConsentLog.query
        .filter_by(user_id=user_id)
        .order_by(DataConsentLog.id.desc())
        .limit(50)
        .all()
    )
    return jsonify({'log': [r.to_dict() for r in records]}), 200


# =============================================================================
# EXTERNAL CONNECTIONS ENDPOINTS
# =============================================================================

@safety_bp.route('/connections', methods=['GET'])
def list_connections():
    """List all external account connections for the current user."""
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    connections = ExternalConnection.query.filter_by(user_id=user_id).all()
    return jsonify({'connections': [c.to_dict() for c in connections]}), 200


@safety_bp.route('/connections', methods=['POST'])
def create_connection():
    """
    Register a new external account connection.

    For real OAuth flows, the frontend would redirect the user to the
    provider's auth page and receive a callback. This endpoint accepts
    the finalised token data after OAuth completion.

    For manual/SMTP connections, access_token may be an app password.
    """
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    data = request.get_json(force=True) or {}

    platform = data.get('platform', '').upper()
    if platform not in ALL_PLATFORMS:
        return jsonify({'error': f'Unknown platform. Valid: {sorted(ALL_PLATFORMS)}'}), 400

    # Check consent for ACCOUNT_CONNECTION category
    if not has_consent(user_id, 'ACCOUNT_CONNECTION'):
        return jsonify({
            'error': 'ACCOUNT_CONNECTION consent is required before connecting an external account',
            'consent_required': ['ACCOUNT_CONNECTION'],
        }), 403

    permission_level = data.get('permission_level', PERM_DRAFT)

    conn = ExternalConnection(
        user_id=user_id,
        platform=platform,
        connection_status=STATUS_PENDING,
        permission_level=permission_level,
        external_account_email=data.get('external_account_email'),
        external_display_name=data.get('external_display_name'),
        scope=data.get('scope'),
    )

    # If tokens are provided (OAuth callback completed), activate immediately
    if data.get('access_token'):
        expires_at = None
        if data.get('expires_at'):
            try:
                expires_at = datetime.fromisoformat(data['expires_at'])
            except ValueError:
                pass
        conn.activate(
            access_token=data['access_token'],
            refresh_token=data.get('refresh_token'),
            expires_at=expires_at,
            scope=data.get('scope'),
        )

    db.session.add(conn)
    db.session.commit()
    return jsonify({
        'message': 'Connection created',
        'connection': conn.to_dict(),
    }), 201


@safety_bp.route('/connections/<int:connection_id>', methods=['GET'])
def get_connection(connection_id):
    """Get details of a single connection."""
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    conn = ExternalConnection.query.filter_by(
        id=connection_id, user_id=user_id
    ).first_or_404()
    return jsonify({'connection': conn.to_dict()}), 200


@safety_bp.route('/connections/<int:connection_id>/revoke', methods=['POST'])
def revoke_connection(connection_id):
    """Revoke an external account connection and wipe stored tokens."""
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    conn = ExternalConnection.query.filter_by(
        id=connection_id, user_id=user_id
    ).first_or_404()

    if conn.connection_status == STATUS_REVOKED:
        return jsonify({'message': 'Connection already revoked'}), 200

    conn.revoke()
    db.session.commit()
    return jsonify({'message': 'Connection revoked', 'connection': conn.to_dict()}), 200


@safety_bp.route('/connections/<int:connection_id>', methods=['DELETE'])
def delete_connection(connection_id):
    """Permanently delete a connection record (must be revoked first)."""
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    conn = ExternalConnection.query.filter_by(
        id=connection_id, user_id=user_id
    ).first_or_404()

    if conn.connection_status == STATUS_ACTIVE:
        return jsonify({
            'error': 'Revoke the connection before deleting it'
        }), 409

    db.session.delete(conn)
    db.session.commit()
    return jsonify({'message': 'Connection deleted'}), 200


# =============================================================================
# VENTURE ENDPOINTS
# =============================================================================

@safety_bp.route('/ventures', methods=['GET'])
def list_ventures():
    """List all ventures for the current user."""
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    ventures = (
        Venture.query
        .filter_by(user_id=user_id)
        .order_by(Venture.created_at.desc())
        .all()
    )
    return jsonify({'ventures': [v.to_dict() for v in ventures]}), 200


@safety_bp.route('/ventures', methods=['POST'])
def create_venture():
    """Create a new venture. At most one venture can be primary+active."""
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    data = request.get_json(force=True) or {}

    venture_name = data.get('venture_name', '').strip()

    # Mark any existing primary venture as non-primary if creating a new primary
    is_primary = data.get('is_primary', True)
    if is_primary:
        existing_primary = Venture.query.filter_by(
            user_id=user_id, is_primary=True, status=VENTURE_ACTIVE
        ).first()
        if existing_primary:
            existing_primary.is_primary = False

    venture = Venture(
        user_id=user_id,
        venture_name=venture_name or None,
        venture_description=data.get('venture_description'),
        venture_type=data.get('venture_type'),
        is_primary=is_primary,
    )
    db.session.add(venture)
    db.session.commit()
    return jsonify({
        'message': 'Venture created',
        'venture': venture.to_dict(),
    }), 201


@safety_bp.route('/ventures/<int:venture_id>', methods=['GET'])
def get_venture(venture_id):
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    venture = Venture.query.filter_by(
        id=venture_id, user_id=user_id
    ).first_or_404()
    return jsonify({'venture': venture.to_dict()}), 200


@safety_bp.route('/ventures/<int:venture_id>', methods=['PATCH'])
def update_venture(venture_id):
    """Update venture name, description, or type."""
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    venture = Venture.query.filter_by(
        id=venture_id, user_id=user_id
    ).first_or_404()

    data = request.get_json(force=True) or {}
    if 'venture_name' in data:
        venture.venture_name = data['venture_name']
    if 'venture_description' in data:
        venture.venture_description = data['venture_description']
    if 'venture_type' in data:
        venture.venture_type = data['venture_type']
    if 'notes' in data:
        venture.notes = data['notes']

    venture.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'venture': venture.to_dict()}), 200


@safety_bp.route('/ventures/<int:venture_id>/archive', methods=['POST'])
def archive_venture(venture_id):
    """Archive a venture (soft delete)."""
    user, _session, error, code = verify_session_token()
    if error:
        return jsonify({'error': error}), code
    user_id = user.id
    venture = Venture.query.filter_by(
        id=venture_id, user_id=user_id
    ).first_or_404()

    data = request.get_json(force=True) or {}
    reason = data.get('reason', '')
    venture.archive(reason=reason)
    db.session.commit()
    return jsonify({
        'message': 'Venture archived',
        'venture': venture.to_dict(),
    }), 200
