from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from src.models.assessment import db, Assessment, AssessmentResponse, EntrepreneurProfile
from src.utils.auth import verify_session_token

assessment_bp = Blueprint('assessment', __name__)

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
        
        db.session.commit()
        
        return jsonify({'message': 'Response saved successfully'}), 200
        
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
        
        progress_percentage = data.get('progress_percentage')
        is_completed = data.get('is_completed', False)
        assessment_data = data.get('assessment_data', {})
        
        if progress_percentage is not None:
            try:
                progress_value = float(progress_percentage)
            except (TypeError, ValueError):
                return jsonify({'error': 'Invalid progress_percentage. Must be a numeric value.'}), 400

            assessment.progress_percentage = max(0, min(100, progress_value))
        
        if is_completed:
            assessment.is_completed = True
            assessment.completed_at = datetime.utcnow()
            assessment.progress_percentage = 100.0
        
        if assessment_data:
            assessment.set_assessment_data(assessment_data)
        
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

