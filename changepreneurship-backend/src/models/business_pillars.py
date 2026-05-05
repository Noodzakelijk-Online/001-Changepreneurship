"""
Phase 4 Business Pillars models — Sprint 10
============================================
CEO Section 4: "Can this idea become a coherent business?"

BusinessPillarsData — stores pillar answers per user (upsert, unique per user)
BusinessPillarsBlueprint — generated deliverable at Phase 4 completion
"""
from datetime import datetime
from src.models.assessment import db


class BusinessPillarsData(db.Model):
    __tablename__ = 'business_pillars_data'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
                           nullable=False, unique=True)
    venture_id = db.Column(db.Integer, db.ForeignKey('venture_record.id', ondelete='SET NULL'),
                           nullable=True)

    # All 10 CEO pillars stored as a dict keyed by pillar name
    # Keys: value_proposition, customer_structure, revenue_model, cost_structure,
    #       delivery_model, positioning, operations, legal_structure, metrics, strategic_risks
    pillars    = db.Column(db.JSON, nullable=False, default=dict)

    completed  = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'venture_id': self.venture_id,
            'pillars':    self.pillars or {},
            'completed':  self.completed,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class BusinessPillarsBlueprint(db.Model):
    __tablename__ = 'business_pillars_blueprint'

    id                      = db.Column(db.Integer, primary_key=True)
    user_id                 = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
                                        nullable=False)
    venture_id              = db.Column(db.Integer, db.ForeignKey('venture_record.id', ondelete='SET NULL'),
                                        nullable=True)
    blueprint_data          = db.Column(db.JSON, nullable=False)
    coherence_score         = db.Column(db.Integer, nullable=True)
    ready_for_concept_testing = db.Column(db.Boolean, nullable=False, default=False)
    generated_at            = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':                       self.id,
            'venture_id':               self.venture_id,
            'blueprint_data':           self.blueprint_data or {},
            'coherence_score':          self.coherence_score,
            'ready_for_concept_testing': self.ready_for_concept_testing,
            'generated_at':             self.generated_at.isoformat() if self.generated_at else None,
        }
