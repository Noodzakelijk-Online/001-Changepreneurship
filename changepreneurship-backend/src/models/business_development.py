"""
Phase 6 Business Development models — Sprint 12
================================================
CEO Section 6: "Can we build the necessary business components so the venture can actually function?"

BusinessDevData    — stores Phase 6 question responses per user (upsert, unique per user)
VentureEnvironment — the Phase 6 deliverable ("Personalized Venture Environment")
"""
from datetime import datetime
from src.models.assessment import db


class BusinessDevData(db.Model):
    __tablename__ = 'business_dev_data'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
                           nullable=False, unique=True)
    venture_id = db.Column(db.Integer, db.ForeignKey('venture_record.id', ondelete='SET NULL'),
                           nullable=True)

    # Flat dict of question_id → answer across all 5 sections
    responses  = db.Column(db.JSON, nullable=False, default=dict)

    completed  = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'venture_id': self.venture_id,
            'responses':  self.responses or {},
            'completed':  self.completed,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class VentureEnvironment(db.Model):
    __tablename__ = 'venture_environment'

    id                        = db.Column(db.Integer, primary_key=True)
    user_id                   = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
                                          nullable=False)
    venture_id                = db.Column(db.Integer, db.ForeignKey('venture_record.id', ondelete='SET NULL'),
                                          nullable=True)
    environment_data          = db.Column(db.JSON, nullable=False)
    readiness_score           = db.Column(db.Integer, nullable=True)   # 0-100
    operational_ready         = db.Column(db.Boolean, nullable=False, default=False)
    decision                  = db.Column(db.String(30), nullable=True)
    generated_at              = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':               self.id,
            'venture_id':       self.venture_id,
            'environment_data': self.environment_data or {},
            'readiness_score':  self.readiness_score,
            'operational_ready': self.operational_ready,
            'decision':         self.decision,
            'generated_at':     self.generated_at.isoformat() if self.generated_at else None,
        }
