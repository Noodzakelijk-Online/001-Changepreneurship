from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    assessments = db.relationship('Assessment', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phase_id = db.Column(db.String(50), nullable=False)  # e.g., 'self_discovery', 'idea_discovery'
    phase_name = db.Column(db.String(100), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)
    progress_percentage = db.Column(db.Float, default=0.0)
    
    # Store assessment data as JSON
    assessment_data = db.Column(db.Text)  # JSON string
    
    # Relationships
    responses = db.relationship('AssessmentResponse', backref='assessment', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Assessment {self.phase_name} for User {self.user_id}>'
    
    def get_assessment_data(self):
        if self.assessment_data:
            return json.loads(self.assessment_data)
        return {}
    
    def set_assessment_data(self, data):
        self.assessment_data = json.dumps(data)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'phase_id': self.phase_id,
            'phase_name': self.phase_name,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_completed': self.is_completed,
            'progress_percentage': self.progress_percentage,
            'assessment_data': self.get_assessment_data()
        }

class AssessmentResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    section_id = db.Column(db.String(100), nullable=False)  # e.g., 'core_motivation', 'life_impact'
    question_id = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    response_type = db.Column(db.String(50), nullable=False)  # 'multiple_choice', 'text', 'scale', 'matrix'
    response_value = db.Column(db.Text)  # JSON string for complex responses
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Response {self.question_id} for Assessment {self.assessment_id}>'
    
    def get_response_value(self):
        if self.response_value:
            try:
                # Always attempt to parse as JSON for consistency
                return json.loads(self.response_value)
            except (json.JSONDecodeError, TypeError):
                # If it fails, return the raw string value
                return self.response_value
        return None
    
    def set_response_value(self, value):
        if isinstance(value, (dict, list)):
            self.response_value = json.dumps(value)
        else:
            self.response_value = str(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'section_id': self.section_id,
            'question_id': self.question_id,
            'question_text': self.question_text,
            'response_type': self.response_type,
            'response_value': self.get_response_value(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EntrepreneurProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # Self-Discovery Results
    entrepreneur_archetype = db.Column(db.String(100))
    core_motivation = db.Column(db.String(200))
    risk_tolerance = db.Column(db.Float)
    confidence_level = db.Column(db.Float)
    
    # Idea Discovery Results
    primary_opportunity = db.Column(db.Text)  # JSON
    opportunity_score = db.Column(db.Float)
    skills_assessment = db.Column(db.Text)  # JSON
    
    # Market Research Results
    market_analysis = db.Column(db.Text)  # JSON
    competitive_analysis = db.Column(db.Text)  # JSON
    target_customers = db.Column(db.Text)  # JSON
    
    # Business Planning Results
    business_model = db.Column(db.Text)  # JSON
    financial_projections = db.Column(db.Text)  # JSON
    go_to_market_strategy = db.Column(db.Text)  # JSON
    
    # Implementation & Testing Results
    product_concept_results = db.Column(db.Text)  # JSON
    business_development_plan = db.Column(db.Text)  # JSON
    prototype_testing_results = db.Column(db.Text)  # JSON
    
    # AI Analysis Results
    success_probability = db.Column(db.Float)
    ai_recommendations = db.Column(db.Text)  # JSON
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('profile', uselist=False))
    
    def __repr__(self):
        return f'<EntrepreneurProfile for User {self.user_id}>'
    
    def get_json_field(self, field_name):
        field_value = getattr(self, field_name)
        if field_value:
            try:
                return json.loads(field_value)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_json_field(self, field_name, value):
        if isinstance(value, (dict, list)):
            setattr(self, field_name, json.dumps(value))
        else:
            setattr(self, field_name, json.dumps({}))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'entrepreneur_archetype': self.entrepreneur_archetype,
            'core_motivation': self.core_motivation,
            'risk_tolerance': self.risk_tolerance,
            'confidence_level': self.confidence_level,
            'primary_opportunity': self.get_json_field('primary_opportunity'),
            'opportunity_score': self.opportunity_score,
            'skills_assessment': self.get_json_field('skills_assessment'),
            'market_analysis': self.get_json_field('market_analysis'),
            'competitive_analysis': self.get_json_field('competitive_analysis'),
            'target_customers': self.get_json_field('target_customers'),
            'business_model': self.get_json_field('business_model'),
            'financial_projections': self.get_json_field('financial_projections'),
            'go_to_market_strategy': self.get_json_field('go_to_market_strategy'),
            'product_concept_results': self.get_json_field('product_concept_results'),
            'business_development_plan': self.get_json_field('business_development_plan'),
            'prototype_testing_results': self.get_json_field('prototype_testing_results'),
            'success_probability': self.success_probability,
            'ai_recommendations': self.get_json_field('ai_recommendations'),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship
    user = db.relationship('User', backref='sessions')
    
    def __repr__(self):
        return f'<UserSession {self.session_token} for User {self.user_id}>'
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_token': self.session_token,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'is_expired': self.is_expired()
        }