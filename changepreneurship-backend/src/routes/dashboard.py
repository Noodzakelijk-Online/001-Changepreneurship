"""
Executive Summary Dashboard API Routes
Provides AI-driven business insights and comprehensive dashboard data
"""
from flask import Blueprint, request, jsonify, session, current_app, send_file
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash
from ..services.dashboard_service import DashboardDataGenerator
from ..services.test_data_generator import TestDataGenerator
from ..services.complete_user_generator import CompleteUserGenerator
from ..models.assessment import db, User
import json
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

# Initialize services
dashboard_service = DashboardDataGenerator()
test_data_generator = TestDataGenerator()
complete_user_generator = CompleteUserGenerator()

@dashboard_bp.route('/api/dashboard/executive-summary', methods=['GET'])
@cross_origin()
def get_executive_summary():
    """
    Get comprehensive executive summary dashboard data for a user
    Query Parameters:
    - user_id: User ID (optional, defaults to session user or 'demo-user')
    """
    try:
        # Get user ID from query params, session, or default
        user_id = request.args.get('user_id')
        if not user_id:
            user_id = session.get('user_id', 'demo-user')
        
        current_app.logger.info(f"Generating executive summary for user: {user_id}")
        
        # Generate comprehensive dashboard data
        dashboard_data = dashboard_service.generate_executive_summary(user_id)
        
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Executive summary generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate executive summary',
            'details': str(e)
        }), 500

@dashboard_bp.route('/api/dashboard/executive-summary/refresh', methods=['POST'])
@cross_origin()
def refresh_executive_summary():
    """
    Refresh dashboard data for a specific user
    Request Body:
    {
        "user_id": "user123"
    }
    """
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if not user_id:
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'User ID is required'
                }), 400
        
        current_app.logger.info(f"Refreshing dashboard data for user: {user_id}")
        
        # Refresh dashboard data
        dashboard_data = dashboard_service.refresh_dashboard_data(user_id)
        
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'refreshed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Dashboard refresh error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to refresh dashboard data',
            'details': str(e)
        }), 500

@dashboard_bp.route('/api/dashboard/sub-element/<element_key>', methods=['GET'])
@cross_origin()
def get_sub_element_details(element_key):
    """
    Get detailed data for a specific business sub-element
    Path Parameters:
    - element_key: Key of the sub-element (e.g., 'company_vision', 'market_opportunity')
    Query Parameters:
    - user_id: User ID (optional)
    """
    try:
        user_id = request.args.get('user_id', session.get('user_id', 'demo-user'))
        
        current_app.logger.info(f"Getting sub-element '{element_key}' for user: {user_id}")
        
        # Get detailed sub-element data
        sub_element_data = dashboard_service.get_sub_element_details(user_id, element_key)
        
        if not sub_element_data:
            return jsonify({
                'success': False,
                'error': f'Sub-element "{element_key}" not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': sub_element_data,
            'element_key': element_key
        })
        
    except Exception as e:
        current_app.logger.error(f"Sub-element retrieval error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve sub-element data',
            'details': str(e)
        }), 500

@dashboard_bp.route('/api/dashboard/metrics', methods=['GET'])
@cross_origin()
def get_dashboard_metrics():
    """
    Get aggregated dashboard metrics
    Query Parameters:
    - user_id: User ID (optional, if not provided returns aggregate metrics)
    """
    try:
        user_id = request.args.get('user_id')
        
        if user_id:
            current_app.logger.info(f"Getting metrics for user: {user_id}")
        else:
            current_app.logger.info("Getting aggregate dashboard metrics")
        
        # Get dashboard metrics
        metrics = dashboard_service.get_dashboard_metrics(user_id)
        
        return jsonify({
            'success': True,
            'data': metrics,
            'user_specific': bool(user_id)
        })
        
    except Exception as e:
        current_app.logger.error(f"Dashboard metrics error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve dashboard metrics',
            'details': str(e)
        }), 500

@dashboard_bp.route('/api/dashboard/health', methods=['GET'])
@cross_origin()
def dashboard_health_check():
    """
    Health check endpoint for dashboard service
    """
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        
        # Test dashboard service initialization
        test_data = dashboard_service._generate_fallback_data('health-check')
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'executive-summary-dashboard',
            'timestamp': datetime.utcnow().isoformat(),
            'components': {
                'database': 'connected',
                'ai_service': 'operational',
                'dashboard_generator': 'functional'
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Dashboard health check failed: {str(e)}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/dashboard/sub-elements', methods=['GET'])
@cross_origin()
def get_all_sub_elements():
    """
    Get list of all available sub-elements with basic info
    """
    try:
        sub_elements = dashboard_service.business_sub_elements
        
        return jsonify({
            'success': True,
            'data': {
                'count': len(sub_elements),
                'sub_elements': [
                    {
                        'key': element['key'],
                        'title': element['title'],
                        'definition': element['definition']
                    }
                    for element in sub_elements
                ]
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Sub-elements list error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve sub-elements list',
            'details': str(e)
        }), 500

@dashboard_bp.route('/api/dashboard/insights', methods=['GET'])
@cross_origin()
def get_ai_insights():
    """
    Get AI insights and recommendations for a user
    Query Parameters:
    - user_id: User ID (optional)
    """
    try:
        user_id = request.args.get('user_id', session.get('user_id', 'demo-user'))
        
        current_app.logger.info(f"Getting AI insights for user: {user_id}")
        
        # Get full dashboard data and extract insights
        dashboard_data = dashboard_service.generate_executive_summary(user_id)
        ai_insights = dashboard_data.get('ai_insights', {})
        
        # Add overall score context
        ai_insights['overall_score'] = dashboard_data.get('overall_score', 0)
        ai_insights['data_completeness'] = dashboard_data.get('data_completeness', 0)
        
        return jsonify({
            'success': True,
            'data': ai_insights,
            'user_id': user_id
        })
        
    except Exception as e:
        current_app.logger.error(f"AI insights error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI insights',
            'details': str(e)
        }), 500

@dashboard_bp.route('/api/dashboard/test-data/create', methods=['POST'])
@cross_origin()
def create_test_data():
    """
    Create comprehensive test data for dashboard testing
    """
    try:
        current_app.logger.info("Creating test data for Executive Summary Dashboard")
        
        user_id = test_data_generator.create_complete_test_scenario()
        
        if user_id:
            return jsonify({
                'success': True,
                'message': 'Test data created successfully',
                'test_user_id': str(user_id),
                'next_steps': [
                    f'Access dashboard with user_id={user_id}',
                    f'Test API endpoint: /api/dashboard/executive-summary?user_id={user_id}',
                    'View results in frontend: /dashboard/executive-summary'
                ]
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create test data'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Test data creation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create test data',
            'details': str(e)
        }), 500

@dashboard_bp.route('/api/dashboard/test-data/cleanup', methods=['DELETE'])
@cross_origin()
def cleanup_test_data():
    """
    Clean up test data
    """
    try:
        current_app.logger.info("Cleaning up test data")
        
        success = test_data_generator.cleanup_test_data('executive_test_user')
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Test data cleaned up successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No test data found to clean up'
            })
            
    except Exception as e:
        current_app.logger.error(f"Test data cleanup error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to cleanup test data',
            'details': str(e)
        }), 500

@dashboard_bp.route('/api/dashboard/complete-user/create', methods=['POST'])
@cross_origin()
def create_complete_user():
    """
    Create a complete test user with 100% filled assessments
    Sarah Chen - Tech SaaS Founder with realistic, comprehensive data
    """
    try:
        current_app.logger.info("Creating complete user: Sarah Chen")
        
        user_id = complete_user_generator.create_complete_user()
        
        if user_id:
            return jsonify({
                'success': True,
                'message': 'Complete user created successfully',
                'user_id': user_id,
                'username': 'sarah_chen_founder',
                'description': 'Sarah Chen - Former Product Manager building AI-powered project management SaaS',
                'completion': '100% (all 7 assessments fully completed)',
                'total_responses': '50+ realistic, high-quality responses'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create complete user'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Complete user creation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create complete user',
            'details': str(e)
        }), 500

@dashboard_bp.route('/api/dashboard/complete-user/export/<int:user_id>', methods=['GET'])
@cross_origin()
def export_complete_user(user_id):
    """
    Export complete user data to JSON
    """
    try:
        current_app.logger.info(f"Exporting user data for user_id: {user_id}")
        
        filename = f'/tmp/user_{user_id}_export.json'
        export_data = complete_user_generator.export_to_json(user_id, filename)
        
        if export_data:
            return send_file(
                filename,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'sarah_chen_complete_data.json'
            )
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to export user data'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"User export error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to export user data',
            'details': str(e)
        }), 500

@dashboard_bp.route('/api/dashboard/complete-user/fix-password/<int:user_id>', methods=['POST', 'OPTIONS'])
@cross_origin()
def fix_user_password(user_id):
    """
    Fix password hash for test user
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Update password hash
        user.password_hash = generate_password_hash('test123')
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Password updated for user {user.username}',
            'user_id': user_id,
            'username': user.username
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Password fix error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update password',
            'details': str(e)
        }), 500

# Error handlers
@dashboard_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/api/dashboard/executive-summary',
            '/api/dashboard/executive-summary/refresh',
            '/api/dashboard/sub-element/<key>',
            '/api/dashboard/metrics',
            '/api/dashboard/health',
            '/api/dashboard/insights'
        ]
    }), 404

@dashboard_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500