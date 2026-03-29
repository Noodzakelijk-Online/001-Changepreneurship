"""
Assessment Modules Models
Supports 20+ interconnected assessment modules with data bridging
"""
from datetime import datetime
import json
from sqlalchemy import func
from src.models.assessment import db


class AssessmentModule(db.Model):
    """
    Defines available assessment modules
    Examples: talents, values, ikigai, effectuation, 7habits, etc.
    """
    __tablename__ = 'assessment_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    module_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)  # 'self_insight', 'strategy', 'execution', 'networking', 'branding'
    order = db.Column(db.Integer, nullable=False)  # Display order within category
    description = db.Column(db.Text)
    estimated_duration = db.Column(db.Integer)  # in minutes
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    responses = db.relationship('ModuleResponse', backref='module', lazy=True, cascade='all, delete-orphan')
    source_interconnections = db.relationship(
        'ModuleInterconnection',
        foreign_keys='ModuleInterconnection.source_module_id',
        backref='source_module',
        lazy=True,
        cascade='all, delete-orphan'
    )
    target_interconnections = db.relationship(
        'ModuleInterconnection',
        foreign_keys='ModuleInterconnection.target_module_id',
        backref='target_module',
        lazy=True,
        cascade='all, delete-orphan'
    )
    context_references = db.relationship('ContextReference', backref='module', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AssessmentModule {self.module_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'module_name': self.module_name,
            'category': self.category,
            'order': self.order,
            'description': self.description,
            'estimated_duration': self.estimated_duration,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ModuleResponse(db.Model):
    """
    User responses for individual modules
    Stores granular response data for each module
    """
    __tablename__ = 'module_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    module_id = db.Column(db.String(100), db.ForeignKey('assessment_modules.module_id', ondelete='CASCADE'), nullable=False, index=True)
    section_id = db.Column(db.String(100))  # e.g., 'core_strengths', 'values_hierarchy'
    question_id = db.Column(db.String(100))  # e.g., 'q_talent_1', 'q_value_primary'
    response_value = db.Column(db.Text)  # JSON for complex responses
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite index for efficient queries
    __table_args__ = (
        db.Index('ix_module_responses_user_module', 'user_id', 'module_id'),
    )
    
    def __repr__(self):
        return f'<ModuleResponse user={self.user_id} module={self.module_id}>'
    
    def get_response_value(self):
        """Parse JSON response value"""
        if self.response_value:
            try:
                return json.loads(self.response_value)
            except (json.JSONDecodeError, TypeError):
                return self.response_value
        return None
    
    def set_response_value(self, value):
        """Store response value as JSON"""
        if isinstance(value, (dict, list)):
            self.response_value = json.dumps(value)
        else:
            self.response_value = str(value) if value is not None else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'module_id': self.module_id,
            'section_id': self.section_id,
            'question_id': self.question_id,
            'response_value': self.get_response_value(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ModuleInterconnection(db.Model):
    """
    Defines data flow between modules
    Example: talents → effectuation (bird_in_hand)
    """
    __tablename__ = 'module_interconnections'
    
    id = db.Column(db.Integer, primary_key=True)
    source_module_id = db.Column(db.String(100), db.ForeignKey('assessment_modules.module_id', ondelete='CASCADE'), nullable=False, index=True)
    source_field = db.Column(db.String(200), nullable=False)  # e.g., 'top_talents'
    target_module_id = db.Column(db.String(100), db.ForeignKey('assessment_modules.module_id', ondelete='CASCADE'), nullable=False, index=True)
    target_field = db.Column(db.String(200), nullable=False)  # e.g., 'bird_in_hand'
    transformation_logic = db.Column(db.Text)  # JSON: transformation rules
    label = db.Column(db.String(200))  # e.g., "Your talents are your Bird in Hand"
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ModuleInterconnection {self.source_module_id} → {self.target_module_id}>'
    
    def get_transformation_logic(self):
        """Parse transformation logic"""
        if self.transformation_logic:
            try:
                return json.loads(self.transformation_logic)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_transformation_logic(self, logic):
        """Store transformation logic as JSON"""
        if isinstance(logic, dict):
            self.transformation_logic = json.dumps(logic)
        else:
            self.transformation_logic = str(logic) if logic else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_module_id': self.source_module_id,
            'source_field': self.source_field,
            'target_module_id': self.target_module_id,
            'target_field': self.target_field,
            'transformation_logic': self.get_transformation_logic(),
            'label': self.label,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ContextReference(db.Model):
    """
    Defines which previous answers to show in context panels
    Example: Show ikigai and values when working on 7habits module
    """
    __tablename__ = 'context_references'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.String(100), db.ForeignKey('assessment_modules.module_id', ondelete='CASCADE'), nullable=False, index=True)
    reference_module_id = db.Column(db.String(100), db.ForeignKey('assessment_modules.module_id', ondelete='CASCADE'), nullable=False)
    reference_field = db.Column(db.String(200), nullable=False)  # e.g., 'ikigai_summary'
    display_label = db.Column(db.String(200), nullable=False)  # e.g., "Your Ikigai"
    display_order = db.Column(db.Integer, nullable=False)  # Order in context panel
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContextReference {self.module_id} ← {self.reference_module_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'reference_module_id': self.reference_module_id,
            'reference_field': self.reference_field,
            'display_label': self.display_label,
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Module definitions (seed data)
MODULES_DEFINITION = [
    # Self-Insight Category
    {'module_id': 'talents', 'module_name': 'Talents & Strengths', 'category': 'self_insight', 'order': 1, 'estimated_duration': 15},
    {'module_id': 'values', 'module_name': 'Values & Beliefs', 'category': 'self_insight', 'order': 2, 'estimated_duration': 15},
    {'module_id': 'ikigai', 'module_name': 'Ikigai Discovery', 'category': 'self_insight', 'order': 3, 'estimated_duration': 20},
    {'module_id': 'personality', 'module_name': 'Personality Profile', 'category': 'self_insight', 'order': 4, 'estimated_duration': 15},
    {'module_id': 'mindset', 'module_name': 'Mindset & Beliefs', 'category': 'self_insight', 'order': 5, 'estimated_duration': 15},
    
    # Strategy Category
    {'module_id': 'effectuation', 'module_name': 'Effectuation Framework', 'category': 'strategy', 'order': 1, 'estimated_duration': 20},
    {'module_id': 'seven_habits', 'module_name': '7 Habits of Effective People', 'category': 'strategy', 'order': 2, 'estimated_duration': 20},
    {'module_id': 'design_your_life', 'module_name': 'Design Your Life', 'category': 'strategy', 'order': 3, 'estimated_duration': 20},
    {'module_id': 'gtd', 'module_name': 'Getting Things Done (GTD)', 'category': 'strategy', 'order': 4, 'estimated_duration': 15},
    
    # Execution Category
    {'module_id': 'eat_that_frog', 'module_name': 'Eat That Frog', 'category': 'execution', 'order': 1, 'estimated_duration': 10},
    {'module_id': 'productivity_matrix', 'module_name': 'Productivity Matrix', 'category': 'execution', 'order': 2, 'estimated_duration': 15},
    {'module_id': 'focus_management', 'module_name': 'Focus Management', 'category': 'execution', 'order': 3, 'estimated_duration': 15},
    
    # Networking Category
    {'module_id': 'networking_strategy', 'module_name': 'Networking Strategy', 'category': 'networking', 'order': 1, 'estimated_duration': 15},
    {'module_id': 'diversity_check', 'module_name': 'Diversity Check', 'category': 'networking', 'order': 2, 'estimated_duration': 10},
    {'module_id': 'partnership', 'module_name': 'Partnership Model', 'category': 'networking', 'order': 3, 'estimated_duration': 15},
    
    # Branding Category
    {'module_id': 'archetype', 'module_name': 'Personal Archetype', 'category': 'branding', 'order': 1, 'estimated_duration': 15},
    {'module_id': 'pitch_canvas', 'module_name': 'Pitch Canvas', 'category': 'branding', 'order': 2, 'estimated_duration': 20},
    {'module_id': 'personal_brand', 'module_name': 'Personal Brand', 'category': 'branding', 'order': 3, 'estimated_duration': 15},
]

# Interconnection definitions (data bridging rules)
INTERCONNECTIONS_DEFINITION = [
    {
        'source_module_id': 'talents',
        'source_field': 'top_talents',
        'target_module_id': 'effectuation',
        'target_field': 'bird_in_hand',
        'label': 'Your talents are your Bird in Hand'
    },
    {
        'source_module_id': 'ikigai',
        'source_field': 'ikigai_summary',
        'target_module_id': 'seven_habits',
        'target_field': 'begin_with_end_in_mind',
        'label': 'Your Ikigai guides your End in Mind'
    },
    {
        'source_module_id': 'values',
        'source_field': 'core_values',
        'target_module_id': 'seven_habits',
        'target_field': 'principles',
        'label': 'Your values are your principles'
    },
    {
        'source_module_id': 'personality',
        'source_field': 'personality_type',
        'target_module_id': 'networking_strategy',
        'target_field': 'communication_style',
        'label': 'Your personality shapes your networking style'
    },
]

# Context references (which previous answers to show)
CONTEXT_REFERENCES_DEFINITION = [
    {
        'module_id': 'seven_habits',
        'reference_module_id': 'ikigai',
        'reference_field': 'ikigai_summary',
        'display_label': 'Your Ikigai',
        'display_order': 1
    },
    {
        'module_id': 'seven_habits',
        'reference_module_id': 'values',
        'reference_field': 'core_values',
        'display_label': 'Your Core Values',
        'display_order': 2
    },
    {
        'module_id': 'effectuation',
        'reference_module_id': 'talents',
        'reference_field': 'top_talents',
        'display_label': 'Your Top Talents',
        'display_order': 1
    },
    {
        'module_id': 'pitch_canvas',
        'reference_module_id': 'ikigai',
        'reference_field': 'why_statement',
        'display_label': 'Your Why',
        'display_order': 1
    },
    {
        'module_id': 'pitch_canvas',
        'reference_module_id': 'archetype',
        'reference_field': 'archetype_name',
        'display_label': 'Your Archetype',
        'display_order': 2
    },
]
