"""
Phase 7 Business Prototype Testing models — Sprint 13
======================================================
CEO Section: "Does the venture work when real people, money, operations, and constraints are involved?"

PrototypeTestData   — stores question responses per user (upsert, unique per user)
PrototypeTestResult — generated deliverable at Phase 7 completion
"""
from datetime import datetime
from src.models.assessment import db


class PrototypeTestData(db.Model):
    __tablename__ = 'prototype_test_data'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
                           nullable=False, unique=True)
    venture_id = db.Column(db.Integer, db.ForeignKey('venture_record.id', ondelete='SET NULL'),
                           nullable=True)

    # Flat dict of question_id → answer (6 sections)
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


class PrototypeTestResult(db.Model):
    __tablename__ = 'prototype_test_result'

    id                  = db.Column(db.Integer, primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
                                    nullable=False)
    venture_id          = db.Column(db.Integer, db.ForeignKey('venture_record.id', ondelete='SET NULL'),
                                    nullable=True)
    result_data         = db.Column(db.JSON, nullable=False)
    scale_readiness     = db.Column(db.String(20), nullable=True)   # STRONG | MODERATE | WEAK | NONE
    scale_score         = db.Column(db.Integer, nullable=True)      # 0-100
    decision            = db.Column(db.String(30), nullable=True)   # SCALE_CAREFULLY | FIX_OPERATIONS | etc.
    ready_to_scale      = db.Column(db.Boolean, nullable=False, default=False)
    generated_at        = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':               self.id,
            'venture_id':       self.venture_id,
            'result_data':      self.result_data or {},
            'scale_readiness':  self.scale_readiness,
            'scale_score':      self.scale_score,
            'decision':         self.decision,
            'ready_to_scale':   self.ready_to_scale,
            'generated_at':     self.generated_at.isoformat() if self.generated_at else None,
        }
