from flask import Blueprint, jsonify, request
from src.models.assessment import User, db
from src.services.auth_service import AuthService
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get current user profile (requires authentication)"""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200

@user_bp.route('/users', methods=['GET'])
def get_users():
    """Return only the authenticated user's own data."""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    # Never expose the full user list — return only the caller's record
    return jsonify([user.to_dict()])

@user_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user account. Requires authentication (admin path)."""
    current_user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password_hash = data.get('password_hash', '')

    if not username or not email or not password_hash:
        return jsonify({'error': 'username, email and password_hash are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already in use'}), 409

    try:
        user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        from flask import current_app
        current_app.logger.error(f'[Users] Create user error: {e}')
        return jsonify({'error': 'Failed to create user'}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    current_user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    current_user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    if current_user.id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    user = User.query.get_or_404(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    current_user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    if current_user.id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204


@user_bp.route('/users/me', methods=['PATCH'])
@limiter.limit('10 per minute')
def update_me():
    """Update authenticated user's own username. Email changes are not supported."""
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

    # Check uniqueness (excluding own record)
    conflict = User.query.filter(User.username == new_username, User.id != user.id).first()
    if conflict:
        return jsonify({'error': 'Username is already taken'}), 409

    try:
        user.username = new_username
        db.session.commit()
        return jsonify({'success': True, 'user': user.to_dict()})
    except Exception:
        db.session.rollback()
        from flask import current_app
        current_app.logger.exception('[Users] update_me error user_id=%d', user.id)
        return jsonify({'error': 'Failed to update profile'}), 500
