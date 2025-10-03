"""
Adaptive Assessment Models for Changepreneurship Platform
Implements intelligent questioning, pre-population, and smart routing
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json
from typing import Dict, List, Any, Optional

Base = declarative_base()

class AdaptiveQuestion(Base):
    __tablename__ = 'adaptive_questions'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), nullable=False)
    text = Column(Text, nullable=False)
    question_type = Column(String(30), nullable=False)  # multiple_choice, text, scale, matrix
    options = Column(JSON)  # For multiple choice questions
    priority = Column(Integer, default=2)  # 1=critical, 2=important, 3=nice-to-have
    dependencies = Column(JSON)  # Questions this depends on
    skip_conditions = Column(JSON)  # Conditions to skip this question
    pre_populate_sources = Column(JSON)  # Questions that can pre-populate this
    pre_populate_logic = Column(Text)  # Logic for pre-population
    explanation_level = Column(String(20), default='standard')  # minimal, standard, detailed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    responses = relationship("AdaptiveResponse", back_populates="question")

class AdaptiveResponse(Base):
    __tablename__ = 'adaptive_responses'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('adaptive_questions.id'), nullable=False)
    response_value = Column(Text)
    confidence_score = Column(Float, default=1.0)  # 0-1 confidence in response
    is_pre_populated = Column(Boolean, default=False)
    pre_population_source = Column(String(100))  # Which question/source pre-populated this
    time_spent = Column(Integer)  # Seconds spent on question
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    question = relationship("AdaptiveQuestion", back_populates="responses")

class UserAssessmentPath(Base):
    __tablename__ = 'user_assessment_paths'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    path_type = Column(String(50), nullable=False)  # beginner, experienced, serial_entrepreneur, etc.
    path_config = Column(JSON)  # Configuration for this path
    current_question_id = Column(String(100))
    questions_completed = Column(JSON, default=list)
    questions_skipped = Column(JSON, default=list)
    estimated_completion_time = Column(Integer)  # Minutes
    actual_time_spent = Column(Integer, default=0)  # Minutes
    completion_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PrePopulationRule(Base):
    __tablename__ = 'pre_population_rules'
    
    id = Column(Integer, primary_key=True)
    rule_name = Column(String(100), unique=True, nullable=False)
    target_question_id = Column(String(100), nullable=False)
    source_question_ids = Column(JSON, nullable=False)
    logic_expression = Column(Text, nullable=False)
    confidence_threshold = Column(Float, default=0.7)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AdaptiveAssessmentEngine:
    """Core engine for adaptive assessment logic"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.user_paths = {
            'beginner_entrepreneur': {
                'trigger_conditions': [
                    'entrepreneurship_experience == "none"',
                    'business_knowledge_level <= 2'
                ],
                'question_priorities': [1, 2, 3],  # Ask all questions
                'explanation_level': 'detailed',
                'estimated_time': 180,  # 3 hours
                'skip_advanced': True
            },
            'experienced_professional': {
                'trigger_conditions': [
                    'work_experience >= 5',
                    'leadership_roles > 0'
                ],
                'question_priorities': [1, 2],  # Skip nice-to-have
                'explanation_level': 'standard',
                'estimated_time': 60,  # 1 hour
                'focus_areas': ['strategic_thinking', 'market_opportunity', 'execution']
            },
            'serial_entrepreneur': {
                'trigger_conditions': [
                    'previous_businesses > 0',
                    'startup_experience == "extensive"'
                ],
                'question_priorities': [1],  # Only critical questions
                'explanation_level': 'minimal',
                'estimated_time': 30,  # 30 minutes
                'focus_areas': ['scaling', 'advanced_market_dynamics', 'investor_readiness']
            },
            'industry_specialist': {
                'trigger_conditions': [
                    'industry_experience >= 7',
                    'domain_expertise == "high"'
                ],
                'question_priorities': [1, 2],
                'explanation_level': 'technical',
                'estimated_time': 45,  # 45 minutes
                'pre_populate_areas': ['market_knowledge', 'competitive_landscape']
            },
            'creative_innovator': {
                'trigger_conditions': [
                    'creative_background == "yes"',
                    'innovation_focus == "high"'
                ],
                'question_priorities': [1, 2],
                'explanation_level': 'visual',
                'estimated_time': 75,  # 1.25 hours
                'focus_areas': ['product_development', 'design_thinking', 'user_experience']
            }
        }
    
    def determine_user_path(self, user_responses: Dict[str, Any]) -> str:
        """Determine the optimal assessment path for a user"""
        path_scores = {}
        
        for path_name, path_config in self.user_paths.items():
            score = 0
            for condition in path_config['trigger_conditions']:
                if self._evaluate_condition(condition, user_responses):
                    score += 1
            path_scores[path_name] = score
        
        # Return path with highest score, default to beginner
        if not path_scores or max(path_scores.values()) == 0:
            return 'beginner_entrepreneur'
        
        return max(path_scores, key=path_scores.get)
    
    def _evaluate_condition(self, condition: str, responses: Dict[str, Any]) -> bool:
        """Evaluate a condition string against user responses"""
        try:
            # Simple condition evaluation (in production, use safer evaluation)
            for key, value in responses.items():
                condition = condition.replace(key, f'"{value}"' if isinstance(value, str) else str(value))
            return eval(condition)
        except:
            return False
    
    def get_next_questions(self, user_id: int, current_responses: Dict[str, Any]) -> List[Dict]:
        """Get the next set of questions for a user"""
        # Get user's assessment path
        user_path = self.db.query(UserAssessmentPath).filter_by(user_id=user_id).first()
        if not user_path:
            # Create new path
            path_type = self.determine_user_path(current_responses)
            user_path = UserAssessmentPath(
                user_id=user_id,
                path_type=path_type,
                path_config=self.user_paths[path_type]
            )
            self.db.add(user_path)
            self.db.commit()
        
        # Get questions based on path configuration
        path_config = user_path.path_config
        priority_filter = path_config.get('question_priorities', [1, 2, 3])
        
        # Query questions that haven't been completed or skipped
        completed_questions = user_path.questions_completed or []
        skipped_questions = user_path.questions_skipped or []
        excluded_questions = completed_questions + skipped_questions
        
        questions = self.db.query(AdaptiveQuestion).filter(
            AdaptiveQuestion.priority.in_(priority_filter),
            ~AdaptiveQuestion.question_id.in_(excluded_questions)
        ).limit(5).all()
        
        # Apply skip logic and pre-population
        filtered_questions = []
        for question in questions:
            if self._should_skip_question(question, current_responses):
                continue
            
            question_dict = {
                'id': question.question_id,
                'text': question.text,
                'type': question.question_type,
                'options': question.options,
                'category': question.category,
                'subcategory': question.subcategory,
                'explanation_level': path_config.get('explanation_level', 'standard')
            }
            
            # Check for pre-population
            pre_populated_value = self._get_pre_populated_value(question, current_responses)
            if pre_populated_value:
                question_dict['pre_populated_value'] = pre_populated_value
                question_dict['pre_populated'] = True
            
            filtered_questions.append(question_dict)
        
        return filtered_questions
    
    def _should_skip_question(self, question: AdaptiveQuestion, responses: Dict[str, Any]) -> bool:
        """Determine if a question should be skipped based on skip conditions"""
        if not question.skip_conditions:
            return False
        
        for condition in question.skip_conditions:
            if self._evaluate_condition(condition, responses):
                return True
        
        return False
    
    def _get_pre_populated_value(self, question: AdaptiveQuestion, responses: Dict[str, Any]) -> Optional[str]:
        """Get pre-populated value for a question if available"""
        if not question.pre_populate_sources or not question.pre_populate_logic:
            return None
        
        # Check if all source questions have responses
        for source_id in question.pre_populate_sources:
            if source_id not in responses:
                return None
        
        try:
            # Execute pre-population logic
            logic = question.pre_populate_logic
            for key, value in responses.items():
                logic = logic.replace(key, f'"{value}"' if isinstance(value, str) else str(value))
            
            # Simple logic evaluation (in production, use safer evaluation)
            result = eval(logic)
            return str(result) if result is not None else None
        except:
            return None
    
    def save_response(self, user_id: int, question_id: str, response_value: str, 
                     is_pre_populated: bool = False, confidence: float = 1.0) -> bool:
        """Save a user's response to a question"""
        try:
            # Get question
            question = self.db.query(AdaptiveQuestion).filter_by(question_id=question_id).first()
            if not question:
                return False
            
            # Save response
            response = AdaptiveResponse(
                user_id=user_id,
                question_id=question.id,
                response_value=response_value,
                confidence_score=confidence,
                is_pre_populated=is_pre_populated
            )
            self.db.add(response)
            
            # Update user path progress
            user_path = self.db.query(UserAssessmentPath).filter_by(user_id=user_id).first()
            if user_path:
                completed = user_path.questions_completed or []
                if question_id not in completed:
                    completed.append(question_id)
                    user_path.questions_completed = completed
                    
                    # Update completion percentage
                    total_questions = self._get_total_questions_for_path(user_path.path_type)
                    user_path.completion_percentage = len(completed) / total_questions * 100
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def _get_total_questions_for_path(self, path_type: str) -> int:
        """Get total number of questions for a specific path"""
        path_config = self.user_paths.get(path_type, {})
        priority_filter = path_config.get('question_priorities', [1, 2, 3])
        
        return self.db.query(AdaptiveQuestion).filter(
            AdaptiveQuestion.priority.in_(priority_filter)
        ).count()
    
    def get_assessment_progress(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive assessment progress for a user"""
        user_path = self.db.query(UserAssessmentPath).filter_by(user_id=user_id).first()
        if not user_path:
            return {'progress': 0, 'path_type': 'not_started'}
        
        completed_count = len(user_path.questions_completed or [])
        total_questions = self._get_total_questions_for_path(user_path.path_type)
        
        return {
            'progress': user_path.completion_percentage,
            'path_type': user_path.path_type,
            'questions_completed': completed_count,
            'total_questions': total_questions,
            'estimated_time_remaining': max(0, user_path.estimated_completion_time - user_path.actual_time_spent),
            'current_question': user_path.current_question_id
        }

# Question database initialization
def initialize_adaptive_questions(db_session):
    """Initialize the adaptive questions database with comprehensive question set"""
    
    # Sample questions for each category (in production, load from comprehensive 500+ question set)
    sample_questions = [
        # Critical Priority Questions (Priority 1)
        {
            'question_id': 'core_motivation',
            'category': 'motivation',
            'subcategory': 'core_drivers',
            'text': 'What is your primary motivation for wanting to start a business?',
            'question_type': 'multiple_choice',
            'options': [
                'Financial independence and wealth building',
                'Solving a problem I\'m passionate about',
                'Being my own boss and having autonomy',
                'Creating something innovative and new',
                'Making a positive impact on society'
            ],
            'priority': 1,
            'dependencies': [],
            'skip_conditions': [],
            'pre_populate_sources': [],
            'pre_populate_logic': ''
        },
        {
            'question_id': 'risk_tolerance',
            'category': 'personality',
            'subcategory': 'risk_assessment',
            'text': 'How comfortable are you with taking significant financial risks?',
            'question_type': 'scale',
            'options': {'min': 1, 'max': 10, 'labels': {'1': 'Very uncomfortable', '10': 'Very comfortable'}},
            'priority': 1,
            'dependencies': [],
            'skip_conditions': [],
            'pre_populate_sources': [],
            'pre_populate_logic': ''
        },
        {
            'question_id': 'business_idea_status',
            'category': 'idea_development',
            'subcategory': 'concept_clarity',
            'text': 'Do you currently have a specific business idea you want to pursue?',
            'question_type': 'multiple_choice',
            'options': [
                'Yes, I have a detailed business concept',
                'Yes, but it\'s still quite general',
                'I have a few ideas I\'m considering',
                'No, I\'m still exploring options',
                'No, I need help identifying opportunities'
            ],
            'priority': 1,
            'dependencies': [],
            'skip_conditions': [],
            'pre_populate_sources': [],
            'pre_populate_logic': ''
        },
        # Important Priority Questions (Priority 2)
        {
            'question_id': 'industry_experience',
            'category': 'background',
            'subcategory': 'professional_experience',
            'text': 'How many years of experience do you have in your target industry?',
            'question_type': 'multiple_choice',
            'options': [
                'No experience in this industry',
                '1-2 years',
                '3-5 years',
                '6-10 years',
                'More than 10 years'
            ],
            'priority': 2,
            'dependencies': ['business_idea_status'],
            'skip_conditions': ['business_idea_status == "No, I need help identifying opportunities"'],
            'pre_populate_sources': ['work_history', 'education_background'],
            'pre_populate_logic': 'extract_industry_experience(work_history, education_background)'
        },
        {
            'question_id': 'leadership_experience',
            'category': 'skills',
            'subcategory': 'management',
            'text': 'How would you describe your leadership and team management experience?',
            'question_type': 'multiple_choice',
            'options': [
                'No formal leadership experience',
                'Led small teams or projects',
                'Managed departments or large teams',
                'Senior executive experience',
                'Founded or co-founded organizations'
            ],
            'priority': 2,
            'dependencies': [],
            'skip_conditions': [],
            'pre_populate_sources': ['work_history', 'management_roles'],
            'pre_populate_logic': 'if management_roles > 2: return "Managed departments or large teams"'
        }
    ]
    
    # Add questions to database
    for q_data in sample_questions:
        existing = db_session.query(AdaptiveQuestion).filter_by(question_id=q_data['question_id']).first()
        if not existing:
            question = AdaptiveQuestion(**q_data)
            db_session.add(question)
    
    # Add pre-population rules
    pre_pop_rules = [
        {
            'rule_name': 'business_idea_clarity_from_status',
            'target_question_id': 'business_idea_clarity',
            'source_question_ids': ['business_idea_status', 'idea_development_stage'],
            'logic_expression': 'if business_idea_status == "Yes, I have a detailed business concept": return "high"',
            'confidence_threshold': 0.8
        },
        {
            'rule_name': 'financial_runway_calculation',
            'target_question_id': 'financial_runway',
            'source_question_ids': ['current_savings', 'monthly_expenses'],
            'logic_expression': 'current_savings / monthly_expenses',
            'confidence_threshold': 0.9
        }
    ]
    
    for rule_data in pre_pop_rules:
        existing = db_session.query(PrePopulationRule).filter_by(rule_name=rule_data['rule_name']).first()
        if not existing:
            rule = PrePopulationRule(**rule_data)
            db_session.add(rule)
    
    db_session.commit()

