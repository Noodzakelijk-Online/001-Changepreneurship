"""Dashboard API - Executive summary and business insights"""
import json
from flask import Blueprint, request, jsonify, session, current_app
from flask_cors import cross_origin
from datetime import datetime
from sqlalchemy import text

from ..models.assessment import db
from ..services.dashboard_service import DashboardDataGenerator
from ..services.test_data_generator import TestDataGenerator
from ..services.complete_user_generator import CompleteUserGenerator
from ..utils.auth import verify_session_token
from ..utils.redis_client import get_redis_client

dashboard_bp = Blueprint('dashboard', __name__)

# Services
dashboard_service = DashboardDataGenerator()
test_data_generator = TestDataGenerator()
complete_user_generator = CompleteUserGenerator()

_DASHBOARD_CACHE_TTL = 300  # 5 minutes


def _dashboard_cache_key(user_id):
    return f"dashboard:executive_summary:{user_id}"


@dashboard_bp.route('/executive-summary', methods=['GET'])
@dashboard_bp.route('/api/dashboard/executive-summary', methods=['GET'])
@cross_origin()
def get_executive_summary():
    """Get comprehensive executive summary for authenticated user"""
    user, user_session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    current_app.logger.info(f"[Dashboard] Executive summary for user: {user.username} (ID: {user.id})")

    # Try Redis cache first
    redis = get_redis_client()
    cache_key = _dashboard_cache_key(user.id)
    if redis:
        try:
            cached = redis.get(cache_key)
            if cached:
                current_app.logger.info(f"[Dashboard] Cache HIT for user {user.id}")
                return jsonify({
                    'success': True,
                    'data': json.loads(cached),
                    'generated_at': datetime.utcnow().isoformat(),
                    'from_cache': True
                })
        except Exception as e:
            current_app.logger.warning(f"[Dashboard] Redis read error: {e}")

    dashboard_data = dashboard_service.generate_executive_summary(user.id)

    # Store in cache
    if redis:
        try:
            redis.set(cache_key, json.dumps(dashboard_data), ex=_DASHBOARD_CACHE_TTL)
        except Exception as e:
            current_app.logger.warning(f"[Dashboard] Redis write error: {e}")

    return jsonify({
        'success': True,
        'data': dashboard_data,
        'generated_at': datetime.utcnow().isoformat()
    })


@dashboard_bp.route('/api/dashboard/executive-summary/refresh', methods=['POST'])
@cross_origin()
def refresh_executive_summary():
    """Refresh dashboard data for authenticated user"""
    user, user_session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    # Invalidate cache so fresh data is served on next GET
    redis = get_redis_client()
    if redis:
        try:
            redis.delete(_dashboard_cache_key(user.id))
        except Exception as e:
            current_app.logger.warning(f"[Dashboard] Cache invalidation error: {e}")

    current_app.logger.info(f"[Dashboard] Refreshing dashboard for user: {user.username} (ID: {user.id})")
    dashboard_data = dashboard_service.refresh_dashboard_data(user.id)

    return jsonify({
        'success': True,
        'data': dashboard_data,
        'refreshed_at': datetime.utcnow().isoformat()
    })


@dashboard_bp.route('/api/dashboard/sub-element/<element_key>', methods=['GET'])
@cross_origin()
def get_sub_element_details(element_key):
    """Get detailed data for specific business sub-element"""
    # Use proper session authentication
    user, user_session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    
    current_app.logger.info(f"[Dashboard] Sub-element '{element_key}' for user: {user.username} (ID: {user.id})")
    
    sub_element_data = dashboard_service.get_sub_element_details(user.id, element_key)
    
    if not sub_element_data:
        return jsonify({'success': False, 'error': f'Sub-element "{element_key}" not found'}), 404
    
    return jsonify({
        'success': True,
        'data': sub_element_data,
        'element_key': element_key
    })


@dashboard_bp.route('/api/dashboard/metrics', methods=['GET'])
@cross_origin()
def get_dashboard_metrics():
    """Get aggregated dashboard metrics for the authenticated user."""
    user, user_session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    current_app.logger.info(f"[Dashboard] Metrics for user: {user.username} (ID: {user.id})")
    metrics = dashboard_service.get_dashboard_metrics(user.id)

    return jsonify({
        'success': True,
        'data': metrics,
        'user_specific': True
    })


@dashboard_bp.route('/health', methods=['GET'])
@cross_origin()
def dashboard_health_check():
    """
    Health check endpoint for dashboard service
    """
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        
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
    """Get AI insights for the authenticated user."""
    user, user_session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    try:
        current_app.logger.info(f"[Dashboard] AI insights for user: {user.username} (ID: {user.id})")

        dashboard_data = dashboard_service.generate_executive_summary(user.id)
        ai_insights = dashboard_data.get('ai_insights', {})
        ai_insights['overall_score'] = dashboard_data.get('overall_score', 0)
        ai_insights['data_completeness'] = dashboard_data.get('data_completeness', 0)

        return jsonify({
            'success': True,
            'data': ai_insights,
        })

    except Exception as e:
        current_app.logger.error(f"[Dashboard] AI insights error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI insights',
        }), 500

@dashboard_bp.route('/api/dashboard/test-data/create', methods=['POST'])
@cross_origin()
def create_test_data():
    """
    Create comprehensive test data (admin / dev only — requires authentication).
    """
    user, user_session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    try:
        current_app.logger.info(f"[Dashboard] Creating test data (requested by user {user.id})")

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
    """Clean up test data (requires authentication)."""
    user, user_session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    try:
        current_app.logger.info(f"[Dashboard] Cleaning up test data (requested by user {user.id})")
        
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
    """Create a complete test user (requires authentication)."""
    user, user_session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code

    try:
        current_app.logger.info(f"[Dashboard] Creating complete user (requested by user {user.id})")
        
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
        
        tmp_dir = tempfile.gettempdir()
        filename = os.path.join(tmp_dir, f'user_{user_id}_export.json')
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