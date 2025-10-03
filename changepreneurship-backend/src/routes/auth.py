from flask import Blueprint, request, jsonify, current_app, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import re

from src.models.assessment import db, User, UserSession, EntrepreneurProfile
from src.utils.auth import verify_session_token

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def generate_session_token():
    return secrets.token_urlsafe(32)

def create_user_session(user_id, expires_in_days=30):
    session_token = generate_session_token()
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    session = UserSession(user_id=user_id, session_token=session_token, expires_at=expires_at)
    db.session.add(session)
    db.session.commit()
    return session

# Handle CORS preflight explicitly (safe even with flask-cors enabled)
@auth_bp.route('/register', methods=['OPTIONS'])
@auth_bp.route('/login', methods=['OPTIONS'])
@auth_bp.route('/logout', methods=['OPTIONS'])
@auth_bp.route('/verify', methods=['OPTIONS'])
@auth_bp.route('/profile', methods=['OPTIONS'])
def auth_options():
    resp = make_response(('', 204))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return resp

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        ok, msg = validate_password(password)
        if not ok:
            return jsonify({'error': msg}), 400

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                return jsonify({'error': 'Username already exists'}), 409
            else:
                return jsonify({'error': 'Email already registered'}), 409

        password_hash = generate_password_hash(password)

        user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.flush()  # Ensure user ID is available for the profile

        profile = EntrepreneurProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

        session = create_user_session(user.id)

        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'session_token': session.session_token,
            'expires_at': session.expires_at.isoformat()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username_or_email = data.get('username') or data.get('email') or ''
        username_or_email = username_or_email.strip()
        password = data.get('password', '')

        if not username_or_email or not password:
            return jsonify({'error': 'Username/email and password are required'}), 400

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email.lower())
        ).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401

        user.last_login = datetime.utcnow()
        db.session.commit()

        session = create_user_session(user.id)

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'session_token': session.session_token,
            'expires_at': session.expires_at.isoformat()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        user, session, error, status_code = verify_session_token()
        if error:
            return jsonify(error), status_code

        if session:
            session.is_active = False
            db.session.commit()

        return jsonify({'message': 'Logout successful'}), 200

    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_session():
    try:
        user, session, error, status_code = verify_session_token()
        if error:
            return jsonify(error), status_code

        return jsonify({
            'valid': True,
            'user': user.to_dict(),
            'session': session.to_dict()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Session verification error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    try:
        user, session, error, status_code = verify_session_token()
        if error:
            return jsonify(error), status_code

        profile = EntrepreneurProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        return jsonify({'user': user.to_dict(), 'profile': profile.to_dict()}), 200

    except Exception as e:
        current_app.logger.error(f"Profile retrieval error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
