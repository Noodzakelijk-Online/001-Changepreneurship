"""Authentication routes - user registration, login, session management"""
import os
from flask import Blueprint, request, jsonify, current_app, make_response

from src.models.assessment import User, EntrepreneurProfile
from src.services.auth_service import AuthService
from src.utils.redis_client import get_session_user
from src.utils.auth import verify_session_token
from src.utils.limiter import limiter

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

_IS_PROD = os.getenv('FLASK_ENV') == 'production'


def _set_session_cookie(response, token, max_age):
    """Attach an HttpOnly session cookie to a response."""
    response.set_cookie(
        'session_token',
        token,
        max_age=max_age,
        httponly=True,
        secure=_IS_PROD,
        samesite='Strict',
        path='/'
    )
    return response


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute; 20 per hour")
def register():
    """Register new user"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')

    if not all([username, email, password]):
        return jsonify({'error': 'Username, email, and password are required'}), 400

    user, error = auth_service.create_user(username, email, password)
    if error:
        status = 409 if 'already' in error else 400
        return jsonify({'error': error}), status

    session = auth_service.create_session(user.id)

    response = make_response(jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'session_token': session.session_token,
        'expires_at': session.expires_at.isoformat()
    }), 201)
    _set_session_cookie(response, session.session_token, max_age=7 * 24 * 3600)
    return response


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute; 50 per hour")
def login():
    """Authenticate user and create session"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username_or_email = data.get('username') or data.get('email') or ''
    password = data.get('password', '')

    if not username_or_email or not password:
        return jsonify({'error': 'Username/email and password are required'}), 400

    user = auth_service.authenticate(username_or_email, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    session = auth_service.create_session(user.id)

    response = make_response(jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'session_token': session.session_token,
        'expires_at': session.expires_at.isoformat()
    }))
    _set_session_cookie(response, session.session_token, max_age=7 * 24 * 3600)
    return response


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Invalidate user session"""
    user, session, error, status = verify_session_token()
    if error:
        return jsonify(error), status

    if session:
        auth_service.invalidate_session(session)

    response = make_response(jsonify({'message': 'Logout successful'}))
    response.delete_cookie('session_token', path='/')
    return response


@auth_bp.route('/verify', methods=['GET'])
def verify_session():
    """Verify session token validity"""
    # Try cache first
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1].strip()
        cached_user_id = get_session_user(token)
        if cached_user_id:
            user = User.query.get(cached_user_id)
            if user:
                return jsonify({
                    'valid': True,
                    'user': user.to_dict(),
                    'session': {'from_cache': True}
                })

    # Fallback to DB
    user, session, error, status = verify_session_token()
    if error:
        return jsonify(error), status

    return jsonify({
        'valid': True,
        'user': user.to_dict(),
        'session': session.to_dict()
    })


@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    user, _, error, status = verify_session_token()
    if error:
        return jsonify(error), status

    profile = EntrepreneurProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    return jsonify({
        'user': user.to_dict(),
        'profile': profile.to_dict()
    })

