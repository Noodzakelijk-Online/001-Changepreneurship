"""
AI Recommendations API Routes
Provides endpoints for personalized AI-driven recommendations
"""
from flask import Blueprint, request, jsonify
from ..services.ai_recommendations_service import AIRecommendationsEngine

ai_recommendations_bp = Blueprint('ai_recommendations', __name__)

@ai_recommendations_bp.route('/api/ai/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """
    Get personalized AI recommendations for a user
    """
    try:
        engine = AIRecommendationsEngine()
        recommendations = engine.generate_recommendations(user_id)
        
        return jsonify({
            'success': True,
            'data': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_recommendations_bp.route('/api/ai/recommendations/strengths/<int:user_id>', methods=['GET'])
def get_user_strengths(user_id):
    """
    Get only strengths analysis for a user
    """
    try:
        engine = AIRecommendationsEngine()
        recommendations = engine.generate_recommendations(user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'strengths': recommendations.get('strengths', []),
                'founder_profile': recommendations.get('founder_profile', {}),
                'ai_confidence': recommendations.get('ai_confidence', 0)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_recommendations_bp.route('/api/ai/recommendations/action-plan/<int:user_id>', methods=['GET'])
def get_action_plan(user_id):
    """
    Get focused action plan (gaps + next steps)
    """
    try:
        engine = AIRecommendationsEngine()
        recommendations = engine.generate_recommendations(user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'gaps': recommendations.get('gaps', []),
                'next_steps': recommendations.get('next_steps', []),
                'recommendations': recommendations.get('recommendations', []),
                'success_probability': recommendations.get('success_probability', {})
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
