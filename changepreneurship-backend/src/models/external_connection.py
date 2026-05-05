"""
ExternalConnection model — Sprint 7 (S7-01)

Stores OAuth/API connections to external platforms.
CEO (Section 13.2): "No action on an external platform without a
connected/approved account or explicit manual mode selection."

Security requirements:
  - access_token and refresh_token are NEVER stored in plaintext
  - Encrypted at rest via Fernet symmetric encryption
  - encryption key loaded from environment (ENCRYPTION_KEY env var)
  - permission_level limits what the platform can do on the account

Supported platforms (initial):
  - EMAIL       — SMTP/Gmail/Outlook for outreach
  - MICROMENTOR — mentor search and outreach
  - LINKEDIN    — professional outreach (future)
  - CALENDAR    — scheduling (future)

Connection lifecycle:
  PENDING → ACTIVE → REVOKED / EXPIRED
"""
import os
import base64
import logging
from datetime import datetime

from src.models.assessment import db

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Encryption helpers (Fernet symmetric, key from env)
# ---------------------------------------------------------------------------
def _get_fernet():
    """Return a Fernet instance using ENCRYPTION_KEY env var."""
    try:
        from cryptography.fernet import Fernet
        key = os.environ.get('ENCRYPTION_KEY', '')
        if not key:
            # Dev fallback — generate ephemeral key (tokens lost on restart)
            if os.environ.get('FLASK_ENV') != 'production':
                key = Fernet.generate_key().decode()
                logger.warning('[ExternalConnection] No ENCRYPTION_KEY set — using ephemeral key (dev only)')
            else:
                raise RuntimeError('ENCRYPTION_KEY must be set in production')
        # Accept both raw bytes and base64url strings
        if isinstance(key, str):
            key = key.encode()
        return Fernet(key)
    except ImportError:
        logger.warning('[ExternalConnection] cryptography not installed — tokens stored as plaintext (dev only)')
        return None


def _encrypt(value: str) -> str:
    """Encrypt a string. Returns base64-encoded ciphertext or plaintext fallback."""
    if not value:
        return ''
    f = _get_fernet()
    if f is None:
        return value  # dev fallback only
    return f.encrypt(value.encode()).decode()


def _decrypt(value: str) -> str:
    """Decrypt a Fernet-encrypted string. Returns plaintext or empty on failure."""
    if not value:
        return ''
    f = _get_fernet()
    if f is None:
        return value  # dev fallback only
    try:
        return f.decrypt(value.encode()).decode()
    except Exception:
        logger.error('[ExternalConnection] Failed to decrypt token — token may be corrupt or key changed')
        return ''


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PLATFORM_EMAIL       = 'EMAIL'
PLATFORM_MICROMENTOR = 'MICROMENTOR'
PLATFORM_LINKEDIN    = 'LINKEDIN'
PLATFORM_CALENDAR    = 'CALENDAR'

ALL_PLATFORMS = {PLATFORM_EMAIL, PLATFORM_MICROMENTOR, PLATFORM_LINKEDIN, PLATFORM_CALENDAR}

# Connection lifecycle states
STATUS_PENDING = 'PENDING'
STATUS_ACTIVE  = 'ACTIVE'
STATUS_REVOKED = 'REVOKED'
STATUS_EXPIRED = 'EXPIRED'

# Permission levels (what the platform may do on this account)
PERM_READ_ONLY   = 'READ_ONLY'    # search, view
PERM_DRAFT       = 'DRAFT'        # prepare content but not send
PERM_SEND        = 'SEND'         # prepare and send (after user approval)
PERM_FULL        = 'FULL'         # all above + manage settings


class ExternalConnection(db.Model):
    """
    One row per connected external account per user.
    A user may have multiple connections to different platforms.
    Tokens are encrypted at rest.
    """
    __tablename__ = 'external_connection'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    platform = db.Column(db.String(40), nullable=False)  # PLATFORM_* constant
    connection_status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING)

    # Encrypted tokens — NEVER store plaintext in production
    _encrypted_access_token  = db.Column('encrypted_access_token',  db.Text, nullable=True)
    _encrypted_refresh_token = db.Column('encrypted_refresh_token', db.Text, nullable=True)

    # OAuth scope granted by user
    scope = db.Column(db.Text, nullable=True)

    # What the platform may do on this account
    permission_level = db.Column(db.String(20), nullable=False, default=PERM_DRAFT)

    # Account identity on external platform (not a secret)
    external_account_email = db.Column(db.String(255), nullable=True)
    external_account_id    = db.Column(db.String(255), nullable=True)
    external_display_name  = db.Column(db.String(255), nullable=True)

    connected_at = db.Column(db.DateTime, nullable=True)
    expires_at   = db.Column(db.DateTime, nullable=True)
    revoked_at   = db.Column(db.DateTime, nullable=True)
    last_used_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ----------------------------------------------------------------
    # Token helpers (encrypt/decrypt transparently)
    # ----------------------------------------------------------------

    @property
    def access_token(self) -> str:
        return _decrypt(self._encrypted_access_token or '')

    @access_token.setter
    def access_token(self, value: str):
        self._encrypted_access_token = _encrypt(value) if value else None

    @property
    def refresh_token(self) -> str:
        return _decrypt(self._encrypted_refresh_token or '')

    @refresh_token.setter
    def refresh_token(self, value: str):
        self._encrypted_refresh_token = _encrypt(value) if value else None

    # ----------------------------------------------------------------
    # State helpers
    # ----------------------------------------------------------------

    def is_active(self) -> bool:
        if self.connection_status != STATUS_ACTIVE:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True

    def revoke(self):
        self.connection_status = STATUS_REVOKED
        self.revoked_at = datetime.utcnow()
        self._encrypted_access_token  = None
        self._encrypted_refresh_token = None

    def activate(self, access_token: str, refresh_token: str = None,
                 expires_at: datetime = None, scope: str = None):
        self.access_token  = access_token
        self.refresh_token = refresh_token or ''
        self.expires_at    = expires_at
        self.scope         = scope
        self.connection_status = STATUS_ACTIVE
        self.connected_at  = datetime.utcnow()

    def can_perform(self, required_perm: str) -> bool:
        """
        Check if this connection has sufficient permission level.
        Hierarchy: READ_ONLY < DRAFT < SEND < FULL
        """
        order = [PERM_READ_ONLY, PERM_DRAFT, PERM_SEND, PERM_FULL]
        try:
            return order.index(self.permission_level) >= order.index(required_perm)
        except ValueError:
            return False

    def to_dict(self, include_tokens: bool = False) -> dict:
        """Safe serialization — never include raw tokens in API responses."""
        d = {
            'id':                    self.id,
            'platform':              self.platform,
            'connection_status':     self.connection_status,
            'permission_level':      self.permission_level,
            'external_account_email': self.external_account_email,
            'external_display_name': self.external_display_name,
            'scope':                 self.scope,
            'is_active':             self.is_active(),
            'connected_at':          self.connected_at.isoformat() if self.connected_at else None,
            'expires_at':            self.expires_at.isoformat() if self.expires_at else None,
            'last_used_at':          self.last_used_at.isoformat() if self.last_used_at else None,
        }
        # Tokens are NEVER included in normal API responses
        return d
