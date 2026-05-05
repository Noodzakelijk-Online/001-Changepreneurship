from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from src.models.assessment import db, Assessment, AssessmentResponse, EntrepreneurProfile
from src.utils.auth import verify_session_token

assessment_bp = Blueprint('assessment', __name__)

PHASE_QUESTION_TOTALS = {
    'self_discovery': 7,
    'idea_discovery': 8,
    'market_research': 13,
    'business_pillars': 13,
    'product_concept_testing': 3,
    'business_development': 3,
    'business_prototype_testing': 3,
}


def recompute_assessment_status(assessment, force_complete=False):
    response_count = AssessmentResponse.query.filter_by(assessment_id=assessment.id).count()
    total_questions = PHASE_QUESTION_TOTALS.get(assessment.phase_id) or 1
    if force_complete:
        progress = 100.0
    else:
        progress = min(100.0, round((response_count / total_questions) * 100, 2))

    assessment.progress_percentage = progress
    metadata = assessment.get_assessment_data() or {}
    metadata['response_count'] = response_count
    metadata['total_questions'] = total_questions
    metadata['last_synced_at'] = datetime.utcnow().isoformat()
    assessment.set_assessment_data(metadata)

    should_complete = force_complete or response_count >= total_questions
    assessment.is_completed = bool(should_complete)
    if should_complete and not assessment.completed_at:
        assessment.completed_at = datetime.utcnow()
    elif not should_complete:
        assessment.completed_at = None

    return assessment

@assessment_bp.route('/phases', methods=['GET'])
def get_assessment_phases():
    """Get all assessment phases with user progress"""
    try:
        user, session, error, status_code = verify_session_token()
        if error:
            return jsonify(error), status_code
        
        # Define all phases
        phases = [
            {
                'id': 'self_discovery',
                'name': 'Self Discovery',
                'description': 'Understand your entrepreneurial personality and motivations',
                'phase_group': 'Foundation & Strategy',
                'duration': '60-90 minutes',
                'order': 1
            },
            {
                'id': 'idea_discovery',
                'name': 'Idea Discovery',
                'description': 'Transform insights into concrete business opportunities',
                'phase_group': 'Foundation & Strategy',
                'duration': '90-120 minutes',
                'order': 2
            },
            {
                'id': 'market_research',
                'name': 'Market Research',
                'description': 'Validate assumptions and understand competitive dynamics',
                'phase_group': 'Foundation & Strategy',
                'duration': '2-3 weeks',
                'order': 3
            },
            {
                'id': 'business_pillars',
                'name': 'Business Pillars',
                'description': 'Define foundational elements for strategic planning',
                'phase_group': 'Foundation & Strategy',
                'duration': '1-2 weeks',
                'order': 4
            },
            {
                'id': 'product_concept_testing',
                'name': 'Product Concept Testing',
                'description': 'Validate product concepts with real customer feedback',
                'phase_group': 'Implementation & Testing',
                'duration': '2-4 weeks',
                'order': 5
            },
            {
                'id': 'business_development',
                'name': 'Business Development',
                'description': 'Strategic decision-making and resource optimization',
                'phase_group': 'Implementation & Testing',
                'duration': '1-2 weeks',
                'order': 6
            },
            {
                'id': 'business_prototype_testing',
                'name': 'Business Prototype Testing',
                'description': 'Complete business model validation in real market conditions',
                'phase_group': 'Implementation & Testing',
                'duration': '3-6 weeks',
                'order': 7
            }
        ]
        
        # Get user's assessment progress
        user_assessments = Assessment.query.filter_by(user_id=user.id).all()
        assessment_dict = {a.phase_id: a for a in user_assessments}
        
        # Add progress information to each phase
        for phase in phases:
            assessment = assessment_dict.get(phase['id'])
            if assessment:
                phase['started_at'] = assessment.started_at.isoformat() if assessment.started_at else None
                phase['completed_at'] = assessment.completed_at.isoformat() if assessment.completed_at else None
                phase['is_completed'] = assessment.is_completed
                phase['progress_percentage'] = assessment.progress_percentage
                phase['assessment_id'] = assessment.id
            else:
                phase['started_at'] = None
                phase['completed_at'] = None
                phase['is_completed'] = False
                phase['progress_percentage'] = 0.0
                phase['assessment_id'] = None
        
        return jsonify({'phases': phases}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get phases error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@assessment_bp.route('/start/<phase_id>', methods=['POST'])
def start_assessment(phase_id):
    """Start or resume an assessment phase"""
    try:
        user, session, error, status_code = verify_session_token()
        if error:
            return jsonify(error), status_code
        
        # Phase names mapping
        phase_names = {
            'self_discovery': 'Self Discovery',
            'idea_discovery': 'Idea Discovery',
            'market_research': 'Market Research',
            'business_pillars': 'Business Pillars',
            'product_concept_testing': 'Product Concept Testing',
            'business_development': 'Business Development',
            'business_prototype_testing': 'Business Prototype Testing'
        }
        
        if phase_id not in phase_names:
            return jsonify({'error': 'Invalid phase ID'}), 400
        
        # Check if assessment already exists
        assessment = Assessment.query.filter_by(
            user_id=user.id,
            phase_id=phase_id
        ).first()
        
        if not assessment:
            # Create new assessment
            assessment = Assessment(
                user_id=user.id,
                phase_id=phase_id,
                phase_name=phase_names[phase_id],
                started_at=datetime.utcnow()
            )
            db.session.add(assessment)
            db.session.commit()
        
        return jsonify({
            'message': f'Assessment {phase_names[phase_id]} started',
            'assessment': assessment.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Start assessment error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@assessment_bp.route('/<int:assessment_id>/response', methods=['POST'])
def save_response(assessment_id):
    """Save assessment response"""
    try:
        user, session, error, status_code = verify_session_token()
        if error:
            return jsonify(error), status_code
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Verify assessment belongs to user
        assessment = Assessment.query.filter_by(
            id=assessment_id,
            user_id=user.id
        ).first()
        
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        section_id = data.get('section_id')
        question_id = data.get('question_id')
        question_text = data.get('question_text')
        response_type = data.get('response_type')
        response_value = data.get('response_value')
        
        if not all([section_id, question_id, question_text, response_type]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if response already exists
        existing_response = AssessmentResponse.query.filter_by(
            assessment_id=assessment_id,
            question_id=question_id
        ).first()
        
        if existing_response:
            # Update existing response
            existing_response.set_response_value(response_value)
            if response_type:
                existing_response.response_type = response_type
            if question_text:
                existing_response.question_text = question_text
            existing_response.updated_at = datetime.utcnow()
        else:
            # Create new response
            response = AssessmentResponse(
                assessment_id=assessment_id,
                section_id=section_id,
                question_id=question_id,
                question_text=question_text,
                response_type=response_type
            )
            response.set_response_value(response_value)
            db.session.add(response)
        
        recompute_assessment_status(assessment)
        db.session.commit()
        
        return jsonify({
            'message': 'Response saved successfully',
            'assessment': assessment.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Save response error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@assessment_bp.route('/<int:assessment_id>/progress', methods=['PUT'])
def update_progress(assessment_id):
    """Update assessment progress"""
    try:
        user, session, error, status_code = verify_session_token()
        if error:
            return jsonify(error), status_code
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Verify assessment belongs to user
        assessment = Assessment.query.filter_by(
            id=assessment_id,
            user_id=user.id
        ).first()
        
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        is_completed = data.get('is_completed', False)
        assessment_data = data.get('assessment_data', {})

        # Allow direct progress_percentage update
        if 'progress_percentage' in data:
            raw = data['progress_percentage']
            try:
                pct = float(raw)
            except (TypeError, ValueError):
                return jsonify({'error': 'Invalid progress_percentage. Must be a numeric value.'}), 400
            assessment.progress_percentage = max(0.0, min(100.0, pct))
        
        if assessment_data:
            existing = assessment.get_assessment_data() or {}
            existing.update(assessment_data)
            assessment.set_assessment_data(existing)

        if 'progress_percentage' not in data:
            recompute_assessment_status(assessment, force_complete=bool(is_completed))
        
        db.session.commit()
        
        return jsonify({
            'message': 'Progress updated successfully',
            'assessment': assessment.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update progress error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@assessment_bp.route('/<int:assessment_id>/responses', methods=['GET'])
def get_responses(assessment_id):
    """Get all responses for an assessment"""
    try:
        user, session, error, status_code = verify_session_token()
        if error:
            return jsonify(error), status_code
        
        # Verify assessment belongs to user
        assessment = Assessment.query.filter_by(
            id=assessment_id,
            user_id=user.id
        ).first()
        
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        responses = AssessmentResponse.query.filter_by(assessment_id=assessment_id).all()
        
        return jsonify({
            'assessment': assessment.to_dict(),
            'responses': [response.to_dict() for response in responses]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get responses error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@assessment_bp.route('/profile/update', methods=['PUT'])
def update_profile():
    """Update entrepreneur profile with assessment results"""
    try:
        user, session, error, status_code = verify_session_token()
        if error:
            return jsonify(error), status_code
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        profile = EntrepreneurProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = EntrepreneurProfile(user_id=user.id)
            db.session.add(profile)
        
        # Update profile fields
        updatable_fields = [
            'entrepreneur_archetype', 'core_motivation', 'risk_tolerance', 'confidence_level',
            'opportunity_score', 'success_probability'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(profile, field, data[field])
        
        # Update JSON fields
        json_fields = [
            'primary_opportunity', 'skills_assessment', 'market_analysis', 'competitive_analysis',
            'target_customers', 'business_model', 'financial_projections', 'go_to_market_strategy',
            'product_concept_results', 'business_development_plan', 'prototype_testing_results',
            'ai_recommendations'
        ]
        
        for field in json_fields:
            if field in data:
                profile.set_json_field(field, data[field])
        
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': profile.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update profile error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@assessment_bp.route('/responses/user/<int:user_id>', methods=['GET'])
def get_user_responses(user_id):
    """Get all assessment responses for a specific user with question details"""
    try:
        # Authentication check
        user, session, error, status_code = verify_session_token()
        if error:
            return jsonify(error), status_code
        
        # Only allow users to see their own responses (or add admin check)
        if user.id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get all assessments for this user
        user_assessments = Assessment.query.filter_by(user_id=user_id).all()
        assessment_ids = [a.id for a in user_assessments]
        
        if not assessment_ids:
            return jsonify({
                'success': True,
                'total_responses': 0,
                'responses': [],
                'by_phase': {}
            }), 200
        
        # Get all responses for user's assessments
        responses = AssessmentResponse.query.filter(
            AssessmentResponse.assessment_id.in_(assessment_ids)
        ).order_by(
            AssessmentResponse.created_at.desc()
        ).all()
        
        # Create assessment map for phase lookup
        assessment_map = {a.id: a.phase_name for a in user_assessments}
        
        # Format responses with full details
        formatted_responses = []
        for response in responses:
            phase_id = assessment_map.get(response.assessment_id, 'unknown')
            formatted_responses.append({
                'id': response.id,
                'assessment_id': response.assessment_id,
                'phase_id': phase_id,
                'question_id': response.question_id,
                'question_text': response.question_text,
                'response_type': response.response_type,
                'response_value': response.response_value,
                'created_at': response.created_at.isoformat() if response.created_at else None,
                'updated_at': response.updated_at.isoformat() if response.updated_at else None
            })
        
        # Group by phase for easier frontend consumption
        phases_map = {}
        for resp in formatted_responses:
            phase_id = resp['phase_id']
            if phase_id not in phases_map:
                phases_map[phase_id] = []
            phases_map[phase_id].append(resp)
        
        return jsonify({
            'success': True,
            'total_responses': len(formatted_responses),
            'responses': formatted_responses,
            'by_phase': phases_map
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get user responses error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Compatibility routes for tests
@assessment_bp.route('/<phase_id>/submit', methods=['POST'])
def submit_phase_assessment(phase_id):
    """Submit assessment for a specific phase (compatibility route for tests)"""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    
    try:
        data = request.get_json()
        
        # Get or create assessment for this phase
        assessment = Assessment.query.filter_by(
            user_id=user.id,
            phase_id=phase_id
        ).first()
        
        if not assessment:
            # Map phase_id to phase_name
            phase_name_map = {
                'self_discovery': 'Self Discovery',
                'idea_discovery': 'Idea Discovery',
                'market_validation': 'Market Validation',
                'business_model': 'Business Model',
                'financial_planning': 'Financial Planning',
                'execution_roadmap': 'Execution Roadmap',
                'resilience_mindset': 'Resilience & Mindset'
            }
            
            assessment = Assessment(
                user_id=user.id,
                phase_id=phase_id,
                phase_name=phase_name_map.get(phase_id, phase_id.replace('_', ' ').title()),
                started_at=datetime.utcnow()
            )
            db.session.add(assessment)
            db.session.flush()
        
        # Save responses
        responses_data = data.get('responses', {})
        for question_key, answer in responses_data.items():
            response = AssessmentResponse(
                assessment_id=assessment.id,
                section_id='general',  # Default section
                question_id=str(question_key),
                question_text=str(question_key),
                response_type='text',
                response_value=str(answer),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(response)
        
        # Update progress
        assessment.progress_percentage = 100
        assessment.is_completed = True
        assessment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{phase_id} assessment submitted successfully',
            'assessment_id': assessment.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Submit assessment error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@assessment_bp.route('/responses', methods=['GET'])
def get_current_user_responses():
    """Get responses for current authenticated user (compatibility route)"""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    
    try:
        # Redirect to user-specific endpoint
        responses = AssessmentResponse.query.join(Assessment).filter(
            Assessment.user_id == user.id
        ).order_by(AssessmentResponse.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'total_responses': len(responses),
            'responses': [{
                'id': r.id,
                'question_id': r.question_id,
                'response_value': r.response_value,
                'created_at': r.created_at.isoformat()
            } for r in responses]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get responses error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@assessment_bp.route('/<phase_id>/questions', methods=['GET'])
def get_phase_questions(phase_id):
    """Get questions for a specific phase (compatibility route for tests)"""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    
    # Return mock questions structure
    phase_questions = {
        'self_discovery': {
            'title': 'Self Discovery',
            'description': 'Understand your motivations and goals',
            'sections': [
                {
                    'id': 'core_motivation',
                    'title': 'Core Motivation',
                    'questions': [
                        {
                            'id': 'motivation_1',
                            'text': 'What drives you to become an entrepreneur?',
                            'type': 'text'
                        }
                    ]
                }
            ]
        }
    }
    
    questions = phase_questions.get(phase_id, {'title': phase_id, 'sections': []})
    
    return jsonify({
        'success': True,
        'phase_id': phase_id,
        'questions': questions
    }), 200

@assessment_bp.route('/sync-all', methods=['GET'])
def sync_all_assessments():
    """Sync all assessment data - returns phases with full response data in format frontend expects"""
    try:
        user, session, error, status_code = verify_session_token()
        if error:
            return jsonify(error), status_code
        
        # Get all assessments for user
        assessments = Assessment.query.filter_by(user_id=user.id).all()
        
        # Build assessment data in exact format frontend expects
        assessment_payload = {}
        
        for assessment in assessments:
            # Get all responses for this assessment
            responses = AssessmentResponse.query.filter_by(assessment_id=assessment.id).all()
            
            # Group responses by section
            sections = {}
            for response in responses:
                section_id = response.section_id or 'general'
                if section_id not in sections:
                    sections[section_id] = []
                sections[section_id].append({
                    'question_id': response.question_id,
                    'question_text': response.question_text,
                    'response_type': response.response_type,
                    'response_value': response.response_value
                })
            
            # Build phase data in frontend format
            assessment_payload[assessment.phase_id] = {
                'assessmentId': assessment.id,
                'phaseId': assessment.phase_id,
                'completed': assessment.is_completed,
                'progress': int(assessment.progress_percentage),
                'startedAt': assessment.started_at.isoformat() if assessment.started_at else None,
                'completedAt': assessment.completed_at.isoformat() if assessment.completed_at else None,
                'responses': sections,
                'responseCount': len(responses)
            }
        
        return jsonify({
            'success': True,
            'user_id': user.id,
            'username': user.username,
            'assessmentData': assessment_payload,
            'totalAssessments': len(assessments),
            'completedAssessments': sum(1 for a in assessments if a.is_completed)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Sync all error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
