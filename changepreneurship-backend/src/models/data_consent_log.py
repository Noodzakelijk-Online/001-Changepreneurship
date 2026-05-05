"""
DataConsentLog model — Sprint 7 (S7-02)

CEO (Section 12.x, GDPR):
  "Users must be able to grant and revoke consent for each category
   of data the platform processes."

Why this is Sprint 7 (not later):
  The platform processes: financial stress, mental health signals, debt,
  employment insecurity, business risk, legal issues, personal vulnerability.
  These are GDPR special categories. Consent must be tracked from day 1.

Consent categories:
  ASSESSMENT_DATA     — questionnaire responses (all phases)
  AI_PROCESSING       — sending data to external AI APIs (Groq, etc.)
  BENCHMARK_SHARING   — anonymised contribution to cohort benchmarks
  EXTERNAL_OUTREACH   — platform sends messages on behalf of user
  ACCOUNT_CONNECTION  — OAuth connection to external platform
  SENSITIVE_DATA      — financial, health, mental health signals

Legal basis options (GDPR Art. 6/9):
  CONSENT             — explicit user consent
  CONTRACT            — necessary for platform service
  LEGITIMATE_INTEREST — platform's legitimate interest (documented)

Design:
  - One row per (user, data_category, legal_basis) combination
  - Revocation creates new row (audit trail preserved)
  - is_active() returns True only if latest record for category is consented
  - consent_text_version links to the exact consent text shown to user
"""
from datetime import datetime

from src.models.assessment import db


# ---------------------------------------------------------------------------
# Consent categories
# ---------------------------------------------------------------------------
CATEGORY_ASSESSMENT    = 'ASSESSMENT_DATA'
CATEGORY_AI_PROCESSING = 'AI_PROCESSING'
CATEGORY_BENCHMARK     = 'BENCHMARK_SHARING'
CATEGORY_OUTREACH      = 'EXTERNAL_OUTREACH'
CATEGORY_ACCOUNT_CONN  = 'ACCOUNT_CONNECTION'
CATEGORY_SENSITIVE     = 'SENSITIVE_DATA'

ALL_CATEGORIES = {
    CATEGORY_ASSESSMENT,
    CATEGORY_AI_PROCESSING,
    CATEGORY_BENCHMARK,
    CATEGORY_OUTREACH,
    CATEGORY_ACCOUNT_CONN,
    CATEGORY_SENSITIVE,
}

# Human-readable descriptions shown to user
CATEGORY_DESCRIPTIONS = {
    CATEGORY_ASSESSMENT:    'Storage and processing of your assessment responses',
    CATEGORY_AI_PROCESSING: 'Sending your data to AI services (Groq) for analysis and insights',
    CATEGORY_BENCHMARK:     'Anonymous contribution of your journey data to improve recommendations for similar founders',
    CATEGORY_OUTREACH:      'Platform sending messages on your behalf through connected accounts',
    CATEGORY_ACCOUNT_CONN:  'Connecting and using your external accounts (email, MicroMentor, etc.)',
    CATEGORY_SENSITIVE:     'Processing sensitive information: financial situation, personal stress, health signals',
}

# Legal basis options
LEGAL_BASIS_CONSENT            = 'CONSENT'
LEGAL_BASIS_CONTRACT           = 'CONTRACT'
LEGAL_BASIS_LEGITIMATE_INTEREST = 'LEGITIMATE_INTEREST'

# Which categories REQUIRE explicit consent (cannot be CONTRACT or LI alone)
REQUIRES_EXPLICIT_CONSENT = {
    CATEGORY_SENSITIVE,
    CATEGORY_OUTREACH,
    CATEGORY_AI_PROCESSING,
    CATEGORY_BENCHMARK,
}

# Minimum required for platform to function (auto-consented on registration)
REQUIRED_FOR_SERVICE = {
    CATEGORY_ASSESSMENT,  # platform cannot function without storing responses
}


class DataConsentLog(db.Model):
    """
    Immutable consent audit trail.
    Each consent grant or revocation is a new row.
    Never update existing rows — append only.
    """
    __tablename__ = 'data_consent_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    data_category = db.Column(db.String(40), nullable=False)
    consent_given = db.Column(db.Boolean, nullable=False)  # True=granted, False=revoked

    # The exact text/version of consent form shown to user
    consent_text_version = db.Column(db.String(20), nullable=False, default='v1.0')

    legal_basis = db.Column(db.String(30), nullable=False, default=LEGAL_BASIS_CONSENT)

    # Additional context (why, from where, IP at time of consent)
    context = db.Column(db.JSON, nullable=True)

    consented_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # For revocations — links back to the original consent record
    revokes_record_id = db.Column(db.Integer, nullable=True)

    def to_dict(self) -> dict:
        return {
            'id':                   self.id,
            'data_category':        self.data_category,
            'consent_given':        self.consent_given,
            'consent_text_version': self.consent_text_version,
            'legal_basis':          self.legal_basis,
            'consented_at':         self.consented_at.isoformat() if self.consented_at else None,
        }


# ---------------------------------------------------------------------------
# Helper: query current consent state for a user
# ---------------------------------------------------------------------------

def get_user_consent_status(user_id: int) -> dict:
    """
    Returns current consent state for all categories.
    Latest record per category wins.
    """
    from sqlalchemy import func

    # Get the latest record per category
    subq = (
        db.session.query(
            DataConsentLog.data_category,
            func.max(DataConsentLog.id).label('latest_id'),
        )
        .filter_by(user_id=user_id)
        .group_by(DataConsentLog.data_category)
        .subquery()
    )

    rows = (
        db.session.query(DataConsentLog)
        .join(subq, DataConsentLog.id == subq.c.latest_id)
        .all()
    )

    result = {cat: False for cat in ALL_CATEGORIES}
    for row in rows:
        result[row.data_category] = row.consent_given

    return result


def has_consent(user_id: int, category: str) -> bool:
    """Quick check: does user have active consent for this category?"""
    latest = (
        DataConsentLog.query
        .filter_by(user_id=user_id, data_category=category)
        .order_by(DataConsentLog.id.desc())
        .first()
    )
    return bool(latest and latest.consent_given)


def record_consent(
    user_id: int,
    category: str,
    given: bool,
    legal_basis: str = LEGAL_BASIS_CONSENT,
    text_version: str = 'v1.0',
    context: dict = None,
) -> DataConsentLog:
    """
    Append a new consent record (grant or revoke).
    Raises ValueError for unknown categories.
    """
    if category not in ALL_CATEGORIES:
        raise ValueError(f'Unknown consent category: {category}')

    record = DataConsentLog(
        user_id=user_id,
        data_category=category,
        consent_given=given,
        consent_text_version=text_version,
        legal_basis=legal_basis,
        context=context,
        consented_at=datetime.utcnow(),
    )
    db.session.add(record)
    return record
