from flask import Blueprint, jsonify, request
from src.models.assessment import User, db
from src.utils.auth import verify_session_token

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
