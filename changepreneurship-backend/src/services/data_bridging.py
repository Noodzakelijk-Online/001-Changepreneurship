"""
Data Bridging Service
Handles intelligent data flow between assessment modules
"""
import json
from src.models.assessment import db
from src.models.modules import (
    ModuleResponse,
    ModuleInterconnection,
    ContextReference
)


class DataBridgingService:
    """Service for managing data flow between modules"""
    
    @staticmethod
    def get_context_panel_data(user_id, module_id):
        """
        Get context panel data for a module
        Returns relevant previous answers from other modules
        """
        try:
            context_refs = ContextReference.query.filter_by(
                module_id=module_id
            ).order_by(ContextReference.display_order).all()
            
            context_data = []
            for ref in context_refs:
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
            
            return {
                'success': True,
                'data': context_data,
                'count': len(context_data)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_prefill_suggestions(user_id, target_module_id):
        """
        Get suggested pre-fills from other modules
        Returns interconnections where source module has data
        """
        try:
            interconnections = ModuleInterconnection.query.filter_by(
                target_module_id=target_module_id
            ).all()
            
            suggestions = []
            for interconnection in interconnections:
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
                        'responses_count': len(source_responses),
                        'data_preview': [r.get_response_value() for r in source_responses[:3]]
                    })
            
            return {
                'success': True,
                'data': suggestions,
                'count': len(suggestions)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def apply_data_bridge(user_id, source_module_id, target_module_id):
        """
        Apply data bridging from source to target module
        Transforms and copies data according to interconnection rules
        """
        try:
            # Get interconnection rule
            interconnection = ModuleInterconnection.query.filter_by(
                source_module_id=source_module_id,
                target_module_id=target_module_id
            ).first()
            
            if not interconnection:
                return {
                    'success': False,
                    'error': 'Interconnection not found'
                }
            
            # Get source data
            source_responses = ModuleResponse.query.filter_by(
                user_id=user_id,
                module_id=source_module_id
            ).all()
            
            if not source_responses:
                return {
                    'success': False,
                    'error': 'No source data found'
                }
            
            # Apply transformation and create target responses
            transformation = interconnection.get_transformation_logic()
            bridged_count = 0
            
            for source_resp in source_responses:
                # Check if response already exists
                existing = ModuleResponse.query.filter_by(
                    user_id=user_id,
                    module_id=target_module_id,
                    question_id=f'bridged_from_{source_module_id}'
                ).first()
                
                if not existing:
                    target_response = ModuleResponse(
                        user_id=user_id,
                        module_id=target_module_id,
                        section_id=interconnection.target_field,
                        question_id=f'bridged_from_{source_module_id}',
                    )
                    target_response.set_response_value(source_resp.get_response_value())
                    db.session.add(target_response)
                    bridged_count += 1
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Data bridged from {source_module_id} to {target_module_id}',
                'data': {
                    'source_module': source_module_id,
                    'target_module': target_module_id,
                    'responses_bridged': bridged_count,
                    'label': interconnection.label
                }
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_interconnection_map():
        """Get full interconnection map for visualization"""
        try:
            interconnections = ModuleInterconnection.query.all()
            
            # Group by source and target
            map_data = {}
            for interconnection in interconnections:
                source = interconnection.source_module_id
                target = interconnection.target_module_id
                
                if source not in map_data:
                    map_data[source] = {
                        'targets': [],
                        'sources': []
                    }
                if target not in map_data:
                    map_data[target] = {
                        'targets': [],
                        'sources': []
                    }
                
                map_data[source]['targets'].append({
                    'target': target,
                    'label': interconnection.label,
                    'field': interconnection.target_field
                })
                map_data[target]['sources'].append({
                    'source': source,
                    'label': interconnection.label,
                    'field': interconnection.source_field
                })
            
            return {
                'success': True,
                'data': map_data,
                'interconnections_count': len(interconnections)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_module_progress(user_id):
        """Get progress across all modules"""
        try:
            from src.models.modules import AssessmentModule
            
            all_modules = AssessmentModule.query.all()
            progress_data = {}
            
            for module in all_modules:
                responses = ModuleResponse.query.filter_by(
                    user_id=user_id,
                    module_id=module.module_id
                ).all()
                
                progress_data[module.module_id] = {
                    'module_name': module.module_name,
                    'category': module.category,
                    'responses_count': len(responses),
                    'is_completed': len(responses) > 0,
                    'completed_at': responses[0].completed_at.isoformat() if responses and responses[0].completed_at else None
                }
            
            # Calculate completion percentage
            completed = sum(1 for m in progress_data.values() if m['is_completed'])
            total = len(progress_data)
            completion_percentage = (completed / total * 100) if total > 0 else 0
            
            return {
                'success': True,
                'data': progress_data,
                'summary': {
                    'total_modules': total,
                    'completed_modules': completed,
                    'completion_percentage': round(completion_percentage, 2)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
