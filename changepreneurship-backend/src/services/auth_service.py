"""Authentication service - handles user auth logic"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging
import secrets
import re

from werkzeug.security import generate_password_hash, check_password_hash
from src.models.assessment import db, User, UserSession, EntrepreneurProfile
from src.utils.redis_client import cache_session

logger = logging.getLogger(__name__)


class AuthService:
    """Handles authentication business logic"""
    
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    MIN_PASSWORD_LENGTH = 12
    MIN_USERNAME_LENGTH = 3
    SESSION_EXPIRY_DAYS = 7
    PASSWORD_SPECIAL_CHARS = re.compile(r'[!@#$%^&*()_+\-=\[\]{};:\'"\\|,.<>/?`~]')

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        return bool(AuthService.EMAIL_PATTERN.match(email))

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if len(password) < AuthService.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {AuthService.MIN_PASSWORD_LENGTH} characters"
        if not re.search(r'[A-Za-z]', password):
            return False, "Password must contain at least one letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not AuthService.PASSWORD_SPECIAL_CHARS.search(password):
            return False, "Password must contain at least one special character (!@#$%^&* etc.)"
        return True, ""

    @staticmethod
    def create_user(username: str, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """Create new user with profile. Returns (user, error_message)"""
        username = username.strip()
        email = email.strip().lower()
        password = password.strip()

        # Validation
        if len(username) < AuthService.MIN_USERNAME_LENGTH:
            return None, f"Username must be at least {AuthService.MIN_USERNAME_LENGTH} characters"
        
        if not AuthService.validate_email(email):
            return None, "Invalid email format"
        
        valid, msg = AuthService.validate_password(password)
        if not valid:
            return None, msg

        # Check duplicates — use generic message to prevent user enumeration
        existing = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing:
            return None, "An account with this username or email already exists"

        # Create user and profile
        try:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.flush()
            
            profile = EntrepreneurProfile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()
            
            return user, None
        except Exception as e:
            db.session.rollback()
            logger.error(f"[AuthService] create_user failed for '{username}': {e}")
            return None, "An error occurred while creating your account. Please try again."

    @staticmethod
    def authenticate(username_or_email: str, password: str) -> Optional[User]:
        """Authenticate user. Returns User or None"""
        identifier = username_or_email.strip().lower()
        
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return user

    @staticmethod
    def create_session(user_id: int) -> UserSession:
        """Create new user session with Redis caching"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=AuthService.SESSION_EXPIRY_DAYS)
        
        session = UserSession(
            user_id=user_id,
            session_token=token,
            expires_at=expires_at
        )
        db.session.add(session)
        db.session.commit()
        
        # Cache in Redis (best-effort)
        cache_session(token, user_id, ttl_seconds=AuthService.SESSION_EXPIRY_DAYS * 86400)
        
        return session

    @staticmethod
    def invalidate_session(session: UserSession) -> None:
        """Invalidate user session"""
        session.is_active = False
        db.session.commit()
