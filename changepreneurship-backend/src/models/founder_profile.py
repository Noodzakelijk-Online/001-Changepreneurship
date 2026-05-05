"""
Founder Readiness Profile and Phase Gate models.
Layer 2 (Venture Record) — written by Layer 1 (Rule Engine).
"""
from datetime import datetime

from src.models.assessment import db


class FounderReadinessProfile(db.Model):
    __tablename__ = 'founder_readiness_profile'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    is_latest = db.Column(db.Boolean, nullable=False, default=True)

    # 13 Typed Dimensions
    # Level: 0=Healthy, 1=OK, 2=Warning, 3=SoftBlock, 4=HardBlock, 5=HardStop
    financial_readiness_score = db.Column(db.SmallInteger)
    financial_readiness_level = db.Column(db.SmallInteger)

    time_capacity_score = db.Column(db.SmallInteger)
    time_capacity_level = db.Column(db.SmallInteger)

    personal_stability_score = db.Column(db.SmallInteger)
    personal_stability_level = db.Column(db.SmallInteger)

    motivation_quality_score = db.Column(db.SmallInteger)
    motivation_quality_level = db.Column(db.SmallInteger)

    skills_experience_score = db.Column(db.SmallInteger)
    skills_experience_level = db.Column(db.SmallInteger)

    founder_idea_fit_score = db.Column(db.SmallInteger)
    founder_idea_fit_level = db.Column(db.SmallInteger)

    founder_market_fit_score = db.Column(db.SmallInteger)
    founder_market_fit_level = db.Column(db.SmallInteger)

    idea_clarity_score = db.Column(db.SmallInteger)
    idea_clarity_level = db.Column(db.SmallInteger)

    market_validity_score = db.Column(db.SmallInteger)
    market_validity_level = db.Column(db.SmallInteger)

    business_model_score = db.Column(db.SmallInteger)
    business_model_level = db.Column(db.SmallInteger)

    # DB column names match migration 20260502_02 rename
    legal_employment_score = db.Column(db.SmallInteger)
    legal_employment_level = db.Column(db.SmallInteger)

    health_energy_score = db.Column(db.SmallInteger)
    health_energy_level = db.Column(db.SmallInteger)

    # Legacy property aliases (backward compat with old code using strategic_position_* / evidence_quality_*)
    @property
    def strategic_position_score(self):
        return self.legal_employment_score

    @strategic_position_score.setter
    def strategic_position_score(self, v):
        self.legal_employment_score = v

    @property
    def strategic_position_level(self):
        return self.legal_employment_level

    @strategic_position_level.setter
    def strategic_position_level(self, v):
        self.legal_employment_level = v

    @property
    def evidence_quality_score(self):
        return self.health_energy_score

    @evidence_quality_score.setter
    def evidence_quality_score(self, v):
        self.health_energy_score = v

    @property
    def evidence_quality_level(self):
        return self.health_energy_level

    @evidence_quality_level.setter
    def evidence_quality_level(self, v):
        self.health_energy_level = v

    network_mentorship_score = db.Column(db.SmallInteger)
    network_mentorship_level = db.Column(db.SmallInteger)

    # Composite — worst-case wins
    overall_readiness_level = db.Column(db.SmallInteger, nullable=False, default=0)

    # Routing
    recommended_route = db.Column(db.String(30), nullable=False, default='CONTINUE')
    founder_type = db.Column(db.String(2))

    # Blockers/compensation (JSON)
    active_blockers = db.Column(db.JSON, nullable=False, default=list)
    compensation_rules_applied = db.Column(db.JSON, nullable=False, default=list)

    # AI Layer 3 output (written after rule engine)
    ai_narrative = db.Column(db.Text)
    ai_confidence = db.Column(db.String(20), default='LOW')
    raw_ai_analysis = db.Column(db.JSON)

    # Special signals — DB columns match migration rename
    burnout_signal = db.Column(db.Boolean, nullable=False, default=False)
    overload_signal = db.Column(db.Boolean, nullable=False, default=False)

    # Legacy property aliases
    @property
    def burnout_signal_detected(self):
        return self.burnout_signal

    @burnout_signal_detected.setter
    def burnout_signal_detected(self, v):
        self.burnout_signal = bool(v)

    @property
    def overload_signal_detected(self):
        return self.overload_signal

    @overload_signal_detected.setter
    def overload_signal_detected(self, v):
        self.overload_signal = bool(v)
    detected_scenario = db.Column(db.String(30))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_active_blockers(self):
        return self.active_blockers or []

    def has_hard_block(self):
        return self.overall_readiness_level >= 4

    def has_hard_stop(self):
        return self.overall_readiness_level == 5

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'version': self.version,
            'is_latest': self.is_latest,
            'dimensions': {
                'financial_readiness': {
                    'score': self.financial_readiness_score,
                    'level': self.financial_readiness_level,
                },
                'time_capacity': {
                    'score': self.time_capacity_score,
                    'level': self.time_capacity_level,
                },
                'personal_stability': {
                    'score': self.personal_stability_score,
                    'level': self.personal_stability_level,
                },
                'motivation_quality': {
                    'score': self.motivation_quality_score,
                    'level': self.motivation_quality_level,
                },
                'skills_experience': {
                    'score': self.skills_experience_score,
                    'level': self.skills_experience_level,
                },
                'founder_idea_fit': {
                    'score': self.founder_idea_fit_score,
                    'level': self.founder_idea_fit_level,
                },
                'founder_market_fit': {
                    'score': self.founder_market_fit_score,
                    'level': self.founder_market_fit_level,
                },
                'idea_clarity': {
                    'score': self.idea_clarity_score,
                    'level': self.idea_clarity_level,
                },
                'market_validity': {
                    'score': self.market_validity_score,
                    'level': self.market_validity_level,
                },
                'business_model': {
                    'score': self.business_model_score,
                    'level': self.business_model_level,
                },
                'legal_employment': {
                    'score': self.strategic_position_score,
                    'level': self.strategic_position_level,
                },
                'evidence_quality': {
                    'score': self.evidence_quality_score,
                    'level': self.evidence_quality_level,
                },
                'network_mentorship': {
                    'score': self.network_mentorship_score,
                    'level': self.network_mentorship_level,
                },
            },
            'overall_readiness_level': self.overall_readiness_level,
            'recommended_route': self.recommended_route,
            'founder_type': self.founder_type,
            'active_blockers': self.active_blockers or [],
            'compensation_rules_applied': self.compensation_rules_applied or [],
            # Flat level keys for PathDecisionEngine lookups
            'financial_level': self.financial_readiness_level,
            'time_capacity_level': self.time_capacity_level,
            'personal_stability_level': self.personal_stability_level,
            'legal_employment_level': self.strategic_position_level,
            'idea_clarity_level': self.idea_clarity_level,
            'market_validity_level': self.market_validity_level,
            'overload_signal': self.overload_signal_detected,
            'burnout_signal': self.burnout_signal_detected,
            'ai_narrative': self.ai_narrative,
            'ai_confidence': self.ai_confidence,
            'burnout_signal_detected': self.burnout_signal_detected,
            'overload_signal_detected': self.overload_signal_detected,
            'detected_scenario': self.detected_scenario,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<FounderReadinessProfile user={self.user_id} v{self.version} level={self.overall_readiness_level}>'


class PhaseGate(db.Model):
    __tablename__ = 'phase_gate'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    phase_number = db.Column(db.SmallInteger, nullable=False)

    # LOCKED | UNLOCKED | IN_PROGRESS | COMPLETED | BLOCKED
    status = db.Column(db.String(20), nullable=False, default='LOCKED')

    blockers = db.Column(db.JSON, nullable=False, default=list)
    unlock_conditions = db.Column(db.JSON, nullable=False, default=list)
    blocking_reason = db.Column(db.Text)

    unlocked_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'phase_number', name='uq_phase_gate_user_phase'),
    )

    def is_accessible(self):
        return self.status in ('UNLOCKED', 'IN_PROGRESS', 'COMPLETED')

    def to_dict(self):
        return {
            'id': self.id,
            'phase_number': self.phase_number,
            'status': self.status,
            'blockers': self.blockers or [],
            'unlock_conditions': self.unlock_conditions or [],
            'blocking_reason': self.blocking_reason,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }

    def __repr__(self):
        return f'<PhaseGate user={self.user_id} phase={self.phase_number} status={self.status}>'


def initialize_phase_gates(user_id: int) -> list:
    """
    Create PhaseGate rows for a new user.
    Phase 1 = UNLOCKED. Phases 2-7 = LOCKED.
    Only creates rows that do not already exist.
    """
    gates = []
    for phase_num in range(1, 8):
        existing = PhaseGate.query.filter_by(
            user_id=user_id, phase_number=phase_num
        ).first()
        if existing:
            gates.append(existing)
            continue

        status = 'UNLOCKED' if phase_num == 1 else 'LOCKED'
        unlock_conditions = []
        if phase_num == 2:
            unlock_conditions = [
                {'condition': 'phase_1_completed', 'met': False},
                {'condition': 'no_hard_stop_in_readiness_profile', 'met': True},
            ]
        elif phase_num > 2:
            unlock_conditions = [
                {'condition': f'phase_{phase_num - 1}_completed', 'met': False},
            ]

        gate = PhaseGate(
            user_id=user_id,
            phase_number=phase_num,
            status=status,
            unlock_conditions=unlock_conditions,
            unlocked_at=datetime.utcnow() if phase_num == 1 else None,
        )
        db.session.add(gate)
        gates.append(gate)

    db.session.flush()
    return gates
