"""
Assessment Modules API Routes
Handles CRUD operations for 20+ interconnected modules
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy import and_, or_
from src.models.assessment import db
from src.models.modules import (
    AssessmentModule,
    ModuleResponse,
    ModuleInterconnection,
    ContextReference,
    MODULES_DEFINITION,
    INTERCONNECTIONS_DEFINITION,
    CONTEXT_REFERENCES_DEFINITION
)
from src.routes.auth import verify_session_token

modules_bp = Blueprint('modules', __name__)


@modules_bp.route('/list', methods=['GET'])
def list_modules():
    """Get all available modules with optional filtering"""
    try:
        category = request.args.get('category')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        query = AssessmentModule.query
        if category:
            query = query.filter_by(category=category)
        if is_active:
            query = query.filter_by(is_active=True)
        
        modules = query.order_by(AssessmentModule.category, AssessmentModule.order).all()
        
        return jsonify({
            'success': True,
            'data': [m.to_dict() for m in modules],
            'count': len(modules)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@modules_bp.route('/<module_id>', methods=['GET'])
def get_module(module_id):
    """Get module definition by ID"""
    try:
        module = AssessmentModule.query.filter_by(module_id=module_id).first()
        if not module:
            return jsonify({'success': False, 'error': 'Module not found'}), 404
        
        return jsonify({
            'success': True,
            'data': module.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@modules_bp.route('/<module_id>/responses', methods=['POST'])
def submit_module_response(module_id):
    """Submit responses for a module"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = verify_session_token(token)
        if not user_data:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        user_id = user_data.get('user_id')
        data = request.get_json()
        
        # Validate module exists
        module = AssessmentModule.query.filter_by(module_id=module_id).first()
        if not module:
            return jsonify({'success': False, 'error': 'Module not found'}), 404
        
        # Store responses
        responses = data.get('responses', [])
        for response in responses:
            module_response = ModuleResponse(
                user_id=user_id,
                module_id=module_id,
                section_id=response.get('section_id'),
                question_id=response.get('question_id'),
            )
            module_response.set_response_value(response.get('value'))
            db.session.add(module_response)
        
        # Mark module as completed if all responses provided
        if data.get('completed'):
            # Check if any existing response for this module
            existing = ModuleResponse.query.filter_by(
                user_id=user_id,
                module_id=module_id
            ).first()
            if existing:
                existing.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Responses saved for module {module_id}',
            'data': {
                'user_id': user_id,
                'module_id': module_id,
                'responses_count': len(responses)
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@modules_bp.route('/<module_id>/responses', methods=['GET'])
def get_module_responses(module_id):
    """Get user's responses for a specific module"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = verify_session_token(token)
        if not user_data:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        user_id = user_data.get('user_id')
        
        responses = ModuleResponse.query.filter_by(
            user_id=user_id,
            module_id=module_id
        ).all()
        
        return jsonify({
            'success': True,
            'data': [r.to_dict() for r in responses],
            'count': len(responses)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@modules_bp.route('/<module_id>/context', methods=['GET'])
def get_context_panel(module_id):
    """Get context panel data (relevant previous answers) for a module"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = verify_session_token(token)
        if not user_data:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        user_id = user_data.get('user_id')
        
        # Get context references for this module
        context_refs = ContextReference.query.filter_by(
            module_id=module_id
        ).order_by(ContextReference.display_order).all()
        
        context_data = []
        for ref in context_refs:
            # Get the referenced module's responses
            responses = ModuleResponse.query.filter_by(
                user_id=user_id,
                module_id=ref.reference_module_id
            ).all()
            
            if responses:
                context_data.append({
                    'label': ref.display_label,
                    'reference_module': ref.reference_module_id,
                    'reference_field': ref.reference_field,
                    'responses': [r.to_dict() for r in responses],
                    'order': ref.display_order
                })
        
        return jsonify({
            'success': True,
            'data': context_data,
            'count': len(context_data)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@modules_bp.route('/interconnections/map', methods=['GET'])
def get_interconnection_map():
    """Get full interconnection map"""
    try:
        interconnections = ModuleInterconnection.query.all()
        
        return jsonify({
            'success': True,
            'data': [i.to_dict() for i in interconnections],
            'count': len(interconnections)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@modules_bp.route('/interconnections/apply/<target_module_id>', methods=['POST'])
def apply_data_bridging(target_module_id):
    """Apply data bridging from source modules to target module"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = verify_session_token(token)
        if not user_data:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        user_id = user_data.get('user_id')
        data = request.get_json()
        source_module_id = data.get('source_module_id')
        
        # Get interconnection rule
        interconnection = ModuleInterconnection.query.filter_by(
            source_module_id=source_module_id,
            target_module_id=target_module_id
        ).first()
        
        if not interconnection:
            return jsonify({'success': False, 'error': 'Interconnection not found'}), 404
        
        # Get source data
        source_responses = ModuleResponse.query.filter_by(
            user_id=user_id,
            module_id=source_module_id
        ).all()
        
        if not source_responses:
            return jsonify({'success': False, 'error': 'No source data found'}), 404
        
        # Apply transformation and create target responses
        transformation = interconnection.get_transformation_logic()
        
        for source_resp in source_responses:
            target_response = ModuleResponse(
                user_id=user_id,
                module_id=target_module_id,
                section_id=interconnection.target_field,
                question_id=f'bridged_from_{source_module_id}',
            )
            target_response.set_response_value(source_resp.get_response_value())
            db.session.add(target_response)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Data bridged from {source_module_id} to {target_module_id}',
            'data': {
                'source_module': source_module_id,
                'target_module': target_module_id,
                'responses_bridged': len(source_responses)
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@modules_bp.route('/interconnections/suggestions/<module_id>', methods=['GET'])
def get_prefill_suggestions(module_id):
    """Get suggested pre-fills from other modules"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = verify_session_token(token)
        if not user_data:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        user_id = user_data.get('user_id')
        
        # Get all interconnections targeting this module
        interconnections = ModuleInterconnection.query.filter_by(
            target_module_id=module_id
        ).all()
        
        suggestions = []
        for interconnection in interconnections:
            # Check if source module has responses
            source_responses = ModuleResponse.query.filter_by(
                user_id=user_id,
                module_id=interconnection.source_module_id
            ).all()
            
            if source_responses:
                suggestions.append({
                    'interconnection_id': interconnection.id,
                    'source_module': interconnection.source_module_id,
                    'target_field': interconnection.target_field,
                    'label': interconnection.label,
                    'description': interconnection.description,
                    'data_available': True,
                    'responses_count': len(source_responses)
                })
        
        return jsonify({
            'success': True,
            'data': suggestions,
            'count': len(suggestions)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@modules_bp.route('/seed', methods=['POST'])
def seed_modules():
    """Seed initial modules, interconnections, and context references (admin only)"""
    try:
        # Check if modules already exist
        existing = AssessmentModule.query.first()
        if existing:
            return jsonify({'success': False, 'error': 'Modules already seeded'}), 400
        
        # Seed modules
        for module_def in MODULES_DEFINITION:
            module = AssessmentModule(**module_def)
            db.session.add(module)
        
        db.session.commit()
        
        # Seed interconnections
        for interconnection_def in INTERCONNECTIONS_DEFINITION:
            interconnection = ModuleInterconnection(**interconnection_def)
            db.session.add(interconnection)
        
        db.session.commit()
        
        # Seed context references
        for context_ref_def in CONTEXT_REFERENCES_DEFINITION:
            context_ref = ContextReference(**context_ref_def)
            db.session.add(context_ref)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Modules seeded successfully',
            'data': {
                'modules_count': len(MODULES_DEFINITION),
                'interconnections_count': len(INTERCONNECTIONS_DEFINITION),
                'context_references_count': len(CONTEXT_REFERENCES_DEFINITION)
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
