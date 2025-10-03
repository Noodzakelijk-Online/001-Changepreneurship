"""
Adaptive Assessment API Routes for Changepreneurship Platform
Provides intelligent questioning, pre-population, and smart routing endpoints
"""

from flask import Blueprint, request, jsonify, session
from sqlalchemy.orm import sessionmaker
from ..models.adaptive_assessment import (
    AdaptiveQuestion, AdaptiveResponse, UserAssessmentPath, 
    PrePopulationRule, AdaptiveAssessmentEngine, initialize_adaptive_questions
)
from ..models.assessment import User, db
import json
from datetime import datetime

adaptive_bp = Blueprint('adaptive', __name__)

# Initialize assessment engine
def get_assessment_engine():
    return AdaptiveAssessmentEngine(db.session)

@adaptive_bp.route('/api/adaptive/initialize', methods=['POST'])
def initialize_adaptive_system():
    """Initialize the adaptive assessment system with questions and rules"""
    try:
        initialize_adaptive_questions(db.session)
        return jsonify({
            'success': True,
            'message': 'Adaptive assessment system initialized successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@adaptive_bp.route('/api/adaptive/start', methods=['POST'])
def start_adaptive_assessment():
    """Start or resume adaptive assessment for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        engine = get_assessment_engine()
        
        # Get or create user assessment path
        user_path = db.session.query(UserAssessmentPath).filter_by(user_id=user_id).first()
        
        if not user_path:
            # Determine initial path based on any existing responses
            existing_responses = {}
            if 'initial_responses' in data:
                existing_responses = data['initial_responses']
            
            path_type = engine.determine_user_path(existing_responses)
            
            user_path = UserAssessmentPath(
                user_id=user_id,
                path_type=path_type,
                path_config=engine.user_paths[path_type],
                estimated_completion_time=engine.user_paths[path_type]['estimated_time']
            )
            db.session.add(user_path)
            db.session.commit()
        
        # Get initial questions
        current_responses = get_user_responses_dict(user_id)
        next_questions = engine.get_next_questions(user_id, current_responses)
        
        return jsonify({
            'success': True,
            'path_type': user_path.path_type,
            'path_config': user_path.path_config,
            'questions': next_questions,
            'progress': engine.get_assessment_progress(user_id)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@adaptive_bp.route('/api/adaptive/questions/next', methods=['POST'])
def get_next_questions():
    """Get the next set of questions for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        engine = get_assessment_engine()
        current_responses = get_user_responses_dict(user_id)
        
        # Include any new responses from the request
        if 'new_responses' in data:
            current_responses.update(data['new_responses'])
        
        next_questions = engine.get_next_questions(user_id, current_responses)
        progress = engine.get_assessment_progress(user_id)
        
        return jsonify({
            'success': True,
            'questions': next_questions,
            'progress': progress,
            'has_more_questions': len(next_questions) > 0
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@adaptive_bp.route('/api/adaptive/response', methods=['POST'])
def save_adaptive_response():
    """Save a user's response to an adaptive question"""
    try:
        data = request.get_json()
        user_id = data.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        question_id = data.get('question_id')
        response_value = data.get('response_value')
        is_pre_populated = data.get('is_pre_populated', False)
        confidence = data.get('confidence', 1.0)
        time_spent = data.get('time_spent', 0)
        
        if not question_id or response_value is None:
            return jsonify({'error': 'Missing required fields'}), 400
        
        engine = get_assessment_engine()
        success = engine.save_response(
            user_id=user_id,
            question_id=question_id,
            response_value=str(response_value),
            is_pre_populated=is_pre_populated,
            confidence=confidence
        )
        
        if success:
            # Get updated progress
            progress = engine.get_assessment_progress(user_id)
            
            # Check for pre-population opportunities
            current_responses = get_user_responses_dict(user_id)
            pre_populated_questions = check_pre_population_opportunities(user_id, current_responses)
            
            return jsonify({
                'success': True,
                'progress': progress,
                'pre_populated_questions': pre_populated_questions
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save response'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@adaptive_bp.route('/api/adaptive/pre-populate', methods=['POST'])
def apply_pre_population():
    """Apply pre-population rules to fill in questions automatically"""
    try:
        data = request.get_json()
        user_id = data.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        current_responses = get_user_responses_dict(user_id)
        pre_populated = apply_pre_population_rules(user_id, current_responses)
        
        return jsonify({
            'success': True,
            'pre_populated_count': len(pre_populated),
            'pre_populated_questions': pre_populated
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@adaptive_bp.route('/api/adaptive/path/update', methods=['POST'])
def update_assessment_path():
    """Update user's assessment path based on new information"""
    try:
        data = request.get_json()
        user_id = data.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        engine = get_assessment_engine()
        current_responses = get_user_responses_dict(user_id)
        
        # Determine if path should change
        new_path_type = engine.determine_user_path(current_responses)
        
        user_path = db.session.query(UserAssessmentPath).filter_by(user_id=user_id).first()
        if user_path and user_path.path_type != new_path_type:
            # Update path
            user_path.path_type = new_path_type
            user_path.path_config = engine.user_paths[new_path_type]
            user_path.estimated_completion_time = engine.user_paths[new_path_type]['estimated_time']
            db.session.commit()
            
            return jsonify({
                'success': True,
                'path_changed': True,
                'new_path_type': new_path_type,
                'path_config': user_path.path_config
            })
        
        return jsonify({
            'success': True,
            'path_changed': False,
            'current_path_type': user_path.path_type if user_path else 'none'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@adaptive_bp.route('/api/adaptive/progress', methods=['GET'])
def get_assessment_progress():
    """Get detailed assessment progress for a user"""
    try:
        user_id = request.args.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        engine = get_assessment_engine()
        progress = engine.get_assessment_progress(user_id)
        
        # Add additional progress details
        user_path = db.session.query(UserAssessmentPath).filter_by(user_id=user_id).first()
        if user_path:
            progress.update({
                'path_description': get_path_description(user_path.path_type),
                'estimated_completion_time': user_path.estimated_completion_time,
                'actual_time_spent': user_path.actual_time_spent,
                'questions_skipped': len(user_path.questions_skipped or [])
            })
        
        return jsonify({
            'success': True,
            'progress': progress
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@adaptive_bp.route('/api/adaptive/analytics', methods=['GET'])
def get_adaptive_analytics():
    """Get analytics about the adaptive assessment system"""
    try:
        user_id = request.args.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get user's assessment analytics
        user_path = db.session.query(UserAssessmentPath).filter_by(user_id=user_id).first()
        responses = db.session.query(AdaptiveResponse).filter_by(user_id=user_id).all()
        
        analytics = {
            'total_responses': len(responses),
            'pre_populated_responses': len([r for r in responses if r.is_pre_populated]),
            'average_confidence': sum(r.confidence_score for r in responses) / len(responses) if responses else 0,
            'time_saved_estimate': calculate_time_saved(user_path, responses),
            'path_efficiency': calculate_path_efficiency(user_path),
            'question_categories': get_response_categories(responses)
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Helper functions

def get_user_responses_dict(user_id: int) -> dict:
    """Get all user responses as a dictionary"""
    responses = db.session.query(AdaptiveResponse).filter_by(user_id=user_id).all()
    response_dict = {}
    
    for response in responses:
        question = db.session.query(AdaptiveQuestion).filter_by(id=response.question_id).first()
        if question:
            response_dict[question.question_id] = response.response_value
    
    return response_dict

def check_pre_population_opportunities(user_id: int, current_responses: dict) -> list:
    """Check for questions that can be pre-populated based on current responses"""
    engine = get_assessment_engine()
    pre_populated = []
    
    # Get all questions that haven't been answered yet
    answered_questions = list(current_responses.keys())
    unanswered_questions = db.session.query(AdaptiveQuestion).filter(
        ~AdaptiveQuestion.question_id.in_(answered_questions)
    ).all()
    
    for question in unanswered_questions:
        pre_populated_value = engine._get_pre_populated_value(question, current_responses)
        if pre_populated_value:
            pre_populated.append({
                'question_id': question.question_id,
                'question_text': question.text,
                'pre_populated_value': pre_populated_value,
                'confidence': 0.8  # Default confidence for pre-populated values
            })
    
    return pre_populated

def apply_pre_population_rules(user_id: int, current_responses: dict) -> list:
    """Apply pre-population rules and save pre-populated responses"""
    engine = get_assessment_engine()
    pre_populated = []
    
    opportunities = check_pre_population_opportunities(user_id, current_responses)
    
    for opportunity in opportunities:
        success = engine.save_response(
            user_id=user_id,
            question_id=opportunity['question_id'],
            response_value=opportunity['pre_populated_value'],
            is_pre_populated=True,
            confidence=opportunity['confidence']
        )
        
        if success:
            pre_populated.append(opportunity)
    
    return pre_populated

def get_path_description(path_type: str) -> str:
    """Get human-readable description of assessment path"""
    descriptions = {
        'beginner_entrepreneur': 'Comprehensive assessment for new entrepreneurs with detailed guidance',
        'experienced_professional': 'Accelerated assessment focusing on strategic business development',
        'serial_entrepreneur': 'Expert validation track for experienced business founders',
        'industry_specialist': 'Industry-focused assessment leveraging domain expertise',
        'creative_innovator': 'Innovation-centered assessment for creative entrepreneurs'
    }
    return descriptions.get(path_type, 'Standard entrepreneurship assessment')

def calculate_time_saved(user_path, responses) -> int:
    """Calculate estimated time saved through adaptive assessment"""
    if not user_path:
        return 0
    
    # Estimate time saved based on skipped questions and pre-populated responses
    skipped_count = len(user_path.questions_skipped or [])
    pre_populated_count = len([r for r in responses if r.is_pre_populated])
    
    # Assume 2 minutes per question on average
    time_saved = (skipped_count + pre_populated_count) * 2
    return time_saved

def calculate_path_efficiency(user_path) -> float:
    """Calculate efficiency of the chosen assessment path"""
    if not user_path:
        return 0.0
    
    # Calculate efficiency based on completion rate and time spent
    if user_path.estimated_completion_time > 0:
        efficiency = min(1.0, user_path.estimated_completion_time / max(1, user_path.actual_time_spent))
        return round(efficiency * 100, 1)
    
    return 0.0

def get_response_categories(responses) -> dict:
    """Get breakdown of responses by category"""
    categories = {}
    
    for response in responses:
        question = db.session.query(AdaptiveQuestion).filter_by(id=response.question_id).first()
        if question:
            category = question.category
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
    
    return categories

