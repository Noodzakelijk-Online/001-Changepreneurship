from flask import request, current_app
from src.models.assessment import UserSession, User


def verify_session_token():
    """Verify session token from Authorization header and return user and session"""
    try:
        session_token = request.headers.get('Authorization')
        if session_token and session_token.startswith('Bearer '):
            session_token = session_token[7:]

        if not session_token:
            return None, None, {'error': 'No session token provided'}, 401

        session = UserSession.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()

        if not session or session.is_expired():
            return None, None, {'error': 'Invalid or expired session'}, 401

        user = User.query.get(session.user_id)
        if not user:
            return None, None, {'error': 'User not found'}, 404

        return user, session, None, None
    except Exception as e:
        current_app.logger.error(f"Session verification error: {str(e)}")
        return None, None, {'error': 'Internal server error'}, 500
