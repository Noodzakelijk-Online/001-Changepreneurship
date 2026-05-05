"""
Phase 5 Concept Testing models — Sprint 11
==========================================
CEO Section 5: "Do real people respond positively to this specific concept?"

ConceptTestData  — stores question responses per user (upsert, unique per user)
ConceptTestResult — generated deliverable at Phase 5 completion
"""
from datetime import datetime
from src.models.assessment import db


class ConceptTestData(db.Model):
    __tablename__ = 'concept_test_data'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
                           nullable=False, unique=True)
    venture_id = db.Column(db.Integer, db.ForeignKey('venture_record.id', ondelete='SET NULL'),
                           nullable=True)

    # Flat dict of question_id → answer (all 4 sections)
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


class ConceptTestResult(db.Model):
    __tablename__ = 'concept_test_result'

    id                     = db.Column(db.Integer, primary_key=True)
    user_id                = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
                                       nullable=False)
    venture_id             = db.Column(db.Integer, db.ForeignKey('venture_record.id', ondelete='SET NULL'),
                                       nullable=True)
    result_data            = db.Column(db.JSON, nullable=False)
    adoption_signal        = db.Column(db.String(20), nullable=True)   # STRONG | MODERATE | WEAK | NONE
    decision               = db.Column(db.String(20), nullable=True)   # PROCEED | REVISE | RETEST | PIVOT | STOP
    ready_for_business_dev = db.Column(db.Boolean, nullable=False, default=False)
    generated_at           = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':                     self.id,
            'venture_id':             self.venture_id,
            'result_data':            self.result_data or {},
            'adoption_signal':        self.adoption_signal,
            'decision':               self.decision,
            'ready_for_business_dev': self.ready_for_business_dev,
            'generated_at':           self.generated_at.isoformat() if self.generated_at else None,
        }
