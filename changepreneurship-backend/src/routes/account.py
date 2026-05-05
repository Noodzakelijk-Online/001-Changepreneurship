"""Account management routes — change password, update username."""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash

from src.models.assessment import User, db
from src.services.auth_service import AuthService
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

account_bp = Blueprint('account', __name__)
auth_service = AuthService()


@account_bp.route('/auth/change-password', methods=['POST'])
@limiter.limit('5 per minute; 20 per hour')
def change_password():
    """Change authenticated user's password. Requires current password for verification."""
    user, _, error, status = verify_session_token()
    if error:
        return jsonify(error), status

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not current_password or not new_password:
        return jsonify({'error': 'current_password and new_password are required'}), 400

    if not check_password_hash(user.password_hash, current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401

    valid, msg = auth_service.validate_password(new_password)
    if not valid:
        return jsonify({'error': msg}), 422

    if current_password == new_password:
        return jsonify({'error': 'New password must differ from the current password'}), 422

    try:
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        current_app.logger.info('[Account] Password changed for user %s', user.id)
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    except Exception:
        db.session.rollback()
        current_app.logger.exception('[Account] change_password error user_id=%d', user.id)
        return jsonify({'error': 'Failed to update password'}), 500


@account_bp.route('/users/me', methods=['PATCH'])
@limiter.limit('10 per minute')
def update_me():
    """Update authenticated user's own username."""
    user, _, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    new_username = data.get('username', '').strip()
    if not new_username:
        return jsonify({'error': 'username is required'}), 400

    if len(new_username) < AuthService.MIN_USERNAME_LENGTH:
        return jsonify({'error': f'Username must be at least {AuthService.MIN_USERNAME_LENGTH} characters'}), 422

    if len(new_username) > 64:
        return jsonify({'error': 'Username must be 64 characters or fewer'}), 422

    conflict = User.query.filter(User.username == new_username, User.id != user.id).first()
    if conflict:
        return jsonify({'error': 'Username is already taken'}), 409

    try:
        user.username = new_username
        db.session.commit()
        return jsonify({'success': True, 'user': user.to_dict()})
    except Exception:
        db.session.rollback()
        current_app.logger.exception('[Account] update_me error user_id=%d', user.id)
        return jsonify({'error': 'Failed to update profile'}), 500
