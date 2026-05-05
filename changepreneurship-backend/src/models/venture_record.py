"""
VentureRecord + EvidenceItem models — Sprint 3.
Layer 2 (Venture Record System) per CEO Section 7.1.

Evidence strength hierarchy (CEO Section 2.5):
  BELIEF < OPINION < DESK_RESEARCH < AI_RESEARCH < INDIRECT < DIRECT < BEHAVIORAL

VentureRecord versioning: one user can have multiple ventures + history.
"""
from datetime import datetime

from src.models.assessment import db


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VENTURE_STATUS_DRAFT = 'DRAFT'
VENTURE_STATUS_CLARIFIED = 'CLARIFIED'
VENTURE_STATUS_VALIDATED = 'VALIDATED'
VENTURE_STATUS_TESTING = 'TESTING'
VENTURE_STATUS_OPERATIONAL = 'OPERATIONAL'
VENTURE_STATUS_PAUSED = 'PAUSED'
VENTURE_STATUS_ARCHIVED = 'ARCHIVED'

VENTURE_TYPE_FORPROFIT = 'FORPROFIT'
VENTURE_TYPE_NONPROFIT = 'NONPROFIT'
VENTURE_TYPE_SOCIAL = 'SOCIAL'
VENTURE_TYPE_LOCAL = 'LOCAL'
VENTURE_TYPE_DEEPTECH = 'DEEPTECH'
VENTURE_TYPE_HYBRID = 'HYBRID'

# Evidence strength hierarchy — index = numeric weight (higher is stronger)
EVIDENCE_STRENGTH_ORDER = [
    'BELIEF',       # 0 — user belief only
    'OPINION',      # 1 — someone else's opinion
    'DESK_RESEARCH', # 2 — secondary research
    'AI_RESEARCH',  # 3 — AI-generated research (CEO: never VERIFIED)
    'INDIRECT',     # 4 — indirect signal
    'DIRECT',       # 5 — direct signal (interview, survey)
    'BEHAVIORAL',   # 6 — behavioral (payment, signup, repeat)
]

EVIDENCE_TYPE_CHOICES = [
    'INTERVIEW', 'SURVEY', 'PAYMENT', 'SIGNUP',
    'LOI', 'PILOT', 'REPEAT', 'REFERRAL', 'THIRDPARTY',
]


class VentureRecord(db.Model):
    __tablename__ = 'venture_record'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Raw + clarified idea
    idea_raw = db.Column(db.Text)
    idea_clarified = db.Column(db.Text)

    # Structured outputs
    problem_statement = db.Column(db.Text)
    target_user_hypothesis = db.Column(db.Text)
    value_proposition = db.Column(db.Text)

    # Typing
    venture_type = db.Column(db.String(20))
    founder_motivation_summary = db.Column(db.Text)

    # Working lists
    assumptions = db.Column(db.JSON, nullable=False, default=list)
    open_questions = db.Column(db.JSON, nullable=False, default=list)

    # Status
    status = db.Column(db.String(20), nullable=False, default=VENTURE_STATUS_DRAFT)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    evidence_items = db.relationship(
        'EvidenceItem', backref='venture', lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='EvidenceItem.venture_id',
    )

    def is_clarified(self):
        return bool(
            self.problem_statement
            and self.target_user_hypothesis
            and self.value_proposition
        )

    def get_pending_assumptions(self):
        return [a for a in (self.assumptions or []) if not a.get('tested')]

    def get_evidence_count_by_strength(self):
        """Returns dict of {strength: count} from related EvidenceItems."""
        counts = {s: 0 for s in EVIDENCE_STRENGTH_ORDER}
        for item in self.evidence_items:
            if item.strength in counts:
                counts[item.strength] += 1
        return counts

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'version': self.version,
            'is_active': self.is_active,
            'idea_raw': self.idea_raw,
            'idea_clarified': self.idea_clarified,
            'problem_statement': self.problem_statement,
            'target_user_hypothesis': self.target_user_hypothesis,
            'value_proposition': self.value_proposition,
            'venture_type': self.venture_type,
            'founder_motivation_summary': self.founder_motivation_summary,
            'assumptions': self.assumptions or [],
            'open_questions': self.open_questions or [],
            'status': self.status,
            'is_clarified': self.is_clarified(),
            'pending_assumptions': len(self.get_pending_assumptions()),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<VentureRecord user={self.user_id} v{self.version} status={self.status}>'


class EvidenceItem(db.Model):
    __tablename__ = 'evidence_item'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    venture_id = db.Column(db.Integer, db.ForeignKey('venture_record.id', ondelete='CASCADE'), nullable=True)

    evidence_type = db.Column(db.String(30), nullable=False)
    strength = db.Column(db.String(30), nullable=False, default='BELIEF')
    description = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(255))
    evidence_date = db.Column(db.Date)

    is_validated = db.Column(db.Boolean, nullable=False, default=False)
    validation_notes = db.Column(db.Text)
    affects_dimensions = db.Column(db.JSON, nullable=False, default=list)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def strength_weight(self):
        """Numeric weight for sorting/comparison."""
        try:
            return EVIDENCE_STRENGTH_ORDER.index(self.strength)
        except ValueError:
            return 0

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'venture_id': self.venture_id,
            'evidence_type': self.evidence_type,
            'strength': self.strength,
            'strength_weight': self.strength_weight,
            'description': self.description,
            'source': self.source,
            'evidence_date': self.evidence_date.isoformat() if self.evidence_date else None,
            'is_validated': self.is_validated,
            'validation_notes': self.validation_notes,
            'affects_dimensions': self.affects_dimensions or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<EvidenceItem type={self.evidence_type} strength={self.strength}>'
