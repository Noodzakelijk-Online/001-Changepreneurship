"""
Market Research models — Sprint 9
==================================
CEO Section 3.3 Phase 3 data layer.

CompetitorEntry      — one competitor in the user's competitor map
MarketContext        — market-level inputs (pain, WTP, target segment)
MarketValidityReport — generated Market Validity Report (JSON blob + metadata)
"""
from datetime import datetime
from src.models.assessment import db


class CompetitorEntry(db.Model):
    __tablename__ = 'competitor_entry'

    id = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    venture_id = db.Column(db.Integer, db.ForeignKey('venture_record.id', ondelete='SET NULL'), nullable=True)

    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    strengths   = db.Column(db.String(500))
    weaknesses  = db.Column(db.String(500))
    positioning = db.Column(db.String(200))
    is_direct   = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'positioning': self.positioning,
            'is_direct': self.is_direct,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<CompetitorEntry {self.name}>'


class MarketContext(db.Model):
    """Market-level inputs per user (one per user, updated in place)."""
    __tablename__ = 'market_context'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, unique=True)
    venture_id = db.Column(db.Integer, db.ForeignKey('venture_record.id', ondelete='SET NULL'), nullable=True)

    target_segment        = db.Column(db.String(300))
    pain_intensity        = db.Column(db.String(20), nullable=False, default='MEDIUM')
    willingness_to_pay    = db.Column(db.Boolean, nullable=False, default=False)
    estimated_price_range = db.Column(db.String(100))
    market_timing         = db.Column(db.String(200))
    market_size_note      = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'target_segment': self.target_segment,
            'pain_intensity': self.pain_intensity,
            'willingness_to_pay': self.willingness_to_pay,
            'estimated_price_range': self.estimated_price_range,
            'market_timing': self.market_timing,
            'market_size_note': self.market_size_note,
        }


class MarketValidityReport(db.Model):
    """Stored Market Validity Report per user+venture."""
    __tablename__ = 'market_validity_report'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    venture_id = db.Column(db.Integer, db.ForeignKey('venture_record.id', ondelete='CASCADE'), nullable=False)

    report_data  = db.Column(db.JSON, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'venture_id', name='uq_mvr_user_venture'),
    )

    def __repr__(self):
        return f'<MarketValidityReport user={self.user_id} venture={self.venture_id}>'
