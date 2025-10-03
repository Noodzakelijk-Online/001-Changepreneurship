"""
Modernized Analytics Module for Changepreneurship Platform
Uses token-based authentication and aligns with current model fields
"""

from flask import Blueprint, request, jsonify, current_app
from src.models.assessment import db, Assessment, AssessmentResponse, EntrepreneurProfile
from src.utils.auth import verify_session_token
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard/overview', methods=['GET'])
def get_dashboard_overview():
    """Get comprehensive dashboard overview for authenticated user"""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    user_id = user.id
    
    try:
        # Get user's assessments
        assessments = Assessment.query.filter_by(user_id=user_id).all()
        
        # Calculate overall progress using correct field name
        total_phases = 7  # 7-part framework
        completed_phases = len([a for a in assessments if a.is_completed])
        overall_progress = (completed_phases / total_phases) * 100 if total_phases > 0 else 0
        
        # Calculate total time spent (estimate based on progress)
        total_time = sum([a.progress_percentage * 0.6 for a in assessments])  # Rough estimate
        
        # Get current phase
        current_phase = None
        phase_order = ['self_discovery', 'idea_discovery', 'market_research', 'business_pillars', 
                      'product_concept_testing', 'business_development', 'business_prototype_testing']
        
        for phase_id in phase_order:
            assessment = next((a for a in assessments if a.phase_id == phase_id), None)
            if not assessment or not assessment.is_completed:
                current_phase = phase_id
                break
        
        # Get recent activity (using updated_at from AssessmentResponse)
        recent_responses = db.session.query(AssessmentResponse)\
            .join(Assessment)\
            .filter(Assessment.user_id == user_id)\
            .filter(AssessmentResponse.updated_at >= datetime.utcnow() - timedelta(days=30))\
            .order_by(desc(AssessmentResponse.updated_at))\
            .limit(10).all()
        
        # Generate insights
        insights = generate_user_insights(assessments, overall_progress)
        
        # Calculate achievements
        achievements = calculate_achievements(assessments)
        
        # Get assessment progress with updated_at from responses
        phase_progress = []
        for phase_id in phase_order:
            assessment = next((a for a in assessments if a.phase_id == phase_id), None)
            if assessment:
                # Get latest response for this assessment
                latest_response = AssessmentResponse.query.filter_by(assessment_id=assessment.id)\
                    .order_by(desc(AssessmentResponse.updated_at)).first()
                last_updated = latest_response.updated_at if latest_response else assessment.started_at
            else:
                last_updated = None
            
            phase_progress.append({
                'phase_id': phase_id,
                'progress': assessment.progress_percentage if assessment else 0,
                'is_completed': assessment.is_completed if assessment else False,
                'last_updated': last_updated.isoformat() if last_updated else None
            })
        
        dashboard_data = {
            'overall_progress': round(overall_progress, 1),
            'completed_phases': completed_phases,
            'total_phases': total_phases,
            'current_phase': current_phase,
            'time_spent': round(total_time),
            'insights': insights,
            'achievements': achievements,
            'recent_activity': [
                {
                    'section_id': r.section_id,
                    'question_id': r.question_id,
                    'response_type': r.response_type,
                    'updated_at': r.updated_at.isoformat(),
                    'assessment_phase': next((a.phase_id for a in assessments if a.id == r.assessment_id), 'unknown')
                } for r in recent_responses
            ],
            'phase_progress': phase_progress
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Dashboard overview error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/dashboard/progress-history', methods=['GET'])
def get_progress_history():
    """Get historical progress data for charts"""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    user_id = user.id
    
    days = request.args.get('days', 30, type=int)
    
    try:
        # Get assessment responses updated in the last N days
        start_date = datetime.utcnow() - timedelta(days=days)
        responses = db.session.query(AssessmentResponse)\
            .join(Assessment)\
            .filter(Assessment.user_id == user_id)\
            .filter(AssessmentResponse.updated_at >= start_date)\
            .order_by(AssessmentResponse.updated_at).all()
        
        # Group by date and calculate daily progress
        daily_progress = {}
        assessments = Assessment.query.filter_by(user_id=user_id).all()
        assessment_dict = {a.id: a for a in assessments}
        
        for response in responses:
            date_key = response.updated_at.date().isoformat()
            if date_key not in daily_progress:
                daily_progress[date_key] = {
                    'date': date_key,
                    'responses_count': 0,
                    'assessments_updated': set(),
                    'phases_completed': 0
                }
            
            daily_progress[date_key]['responses_count'] += 1
            if response.assessment_id in assessment_dict:
                daily_progress[date_key]['assessments_updated'].add(response.assessment_id)
                assessment = assessment_dict[response.assessment_id]
                if assessment.is_completed:
                    daily_progress[date_key]['phases_completed'] += 1
        
        # Convert to list and calculate metrics
        history_data = []
        for date_data in daily_progress.values():
            history_data.append({
                'date': date_data['date'],
                'responses_count': date_data['responses_count'],
                'assessments_updated': len(date_data['assessments_updated']),
                'phases_completed': date_data['phases_completed']
            })
        
        return jsonify({
            'success': True,
            'data': sorted(history_data, key=lambda x: x['date'])
        })
        
    except Exception as e:
        current_app.logger.error(f"Progress history error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/dashboard/entrepreneur-profile', methods=['GET'])
def get_entrepreneur_profile():
    """Get detailed entrepreneur profile and archetype analysis"""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    user_id = user.id
    
    try:
        # Get entrepreneur profile
        profile = EntrepreneurProfile.query.filter_by(user_id=user_id).first()
        
        # Get self-discovery assessment
        self_discovery = Assessment.query.filter_by(
            user_id=user_id, 
            phase_id='self_discovery'
        ).first()
        
        profile_data = {
            'entrepreneur_archetype': profile.entrepreneur_archetype if profile else None,
            'core_motivation': profile.core_motivation if profile else None,
            'risk_tolerance': profile.risk_tolerance if profile else None,
            'confidence_level': profile.confidence_level if profile else None,
            'primary_opportunity': profile.get_json_field('primary_opportunity') if profile else {},
            'opportunity_score': profile.opportunity_score if profile else None,
            'skills_assessment': profile.get_json_field('skills_assessment') if profile else {},
            'success_probability': profile.success_probability if profile else None,
            'ai_recommendations': profile.get_json_field('ai_recommendations') if profile else {},
            'assessment_completed': self_discovery.is_completed if self_discovery else False,
            'last_updated': profile.updated_at.isoformat() if profile and profile.updated_at else None
        }
        
        # Add archetype details
        if profile_data['entrepreneur_archetype']:
            archetype_details = get_archetype_details(profile_data['entrepreneur_archetype'])
            profile_data['archetype_details'] = archetype_details
        
        return jsonify({
            'success': True,
            'data': profile_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Entrepreneur profile error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/dashboard/recommendations', methods=['GET'])
def get_personalized_recommendations():
    """Get AI-powered personalized recommendations"""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    user_id = user.id
    
    try:
        # Get user's assessment data
        assessments = Assessment.query.filter_by(user_id=user_id).all()
        profile = EntrepreneurProfile.query.filter_by(user_id=user_id).first()
        
        # Generate recommendations based on progress and profile
        recommendations = generate_recommendations(assessments, profile)
        
        return jsonify({
            'success': True,
            'data': recommendations
        })
        
    except Exception as e:
        current_app.logger.error(f"Recommendations error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/dashboard/assessment-stats', methods=['GET'])
def get_assessment_statistics():
    """Get detailed assessment statistics"""
    user, session, error, status_code = verify_session_token()
    if error:
        return jsonify(error), status_code
    user_id = user.id
    
    try:
        # Get all user assessments and responses
        assessments = Assessment.query.filter_by(user_id=user_id).all()
        total_responses = db.session.query(AssessmentResponse)\
            .join(Assessment)\
            .filter(Assessment.user_id == user_id)\
            .count()
        
        # Calculate statistics
        stats = {
            'total_assessments': len(assessments),
            'completed_assessments': len([a for a in assessments if a.is_completed]),
            'total_responses': total_responses,
            'average_progress': sum([a.progress_percentage for a in assessments]) / len(assessments) if assessments else 0,
            'assessment_breakdown': {},
            'response_types': {},
            'completion_timeline': []
        }
        
        # Assessment breakdown by phase
        for assessment in assessments:
            phase_name = assessment.phase_name or assessment.phase_id
            stats['assessment_breakdown'][phase_name] = {
                'progress': assessment.progress_percentage,
                'is_completed': assessment.is_completed,
                'started_at': assessment.started_at.isoformat() if assessment.started_at else None,
                'completed_at': assessment.completed_at.isoformat() if assessment.completed_at else None
            }
        
        # Response types breakdown
        response_types = db.session.query(
            AssessmentResponse.response_type,
            func.count(AssessmentResponse.id).label('count')
        ).join(Assessment)\
         .filter(Assessment.user_id == user_id)\
         .group_by(AssessmentResponse.response_type).all()
        
        for response_type, count in response_types:
            stats['response_types'][response_type] = count
        
        # Completion timeline
        completed_assessments = [a for a in assessments if a.is_completed and a.completed_at]
        stats['completion_timeline'] = [
            {
                'phase_name': a.phase_name,
                'completed_at': a.completed_at.isoformat(),
                'duration_days': (a.completed_at - a.started_at).days if a.started_at else 0
            }
            for a in sorted(completed_assessments, key=lambda x: x.completed_at)
        ]
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Assessment statistics error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def generate_user_insights(assessments, overall_progress):
    """Generate personalized insights based on user progress"""
    insights = []
    
    completed_count = len([a for a in assessments if a.is_completed])
    
    if overall_progress >= 75:
        insights.append({
            'type': 'success',
            'title': 'Excellent Progress!',
            'description': 'You\'re well on your way to completing your entrepreneurial assessment.',
            'action': 'Continue with the remaining phases to complete your journey.',
            'priority': 'high'
        })
    elif overall_progress >= 50:
        insights.append({
            'type': 'info',
            'title': 'Great Momentum!',
            'description': 'You\'ve completed half of your entrepreneurial assessment.',
            'action': 'Keep building on your progress with the implementation phases.',
            'priority': 'medium'
        })
    elif overall_progress >= 25:
        insights.append({
            'type': 'info',
            'title': 'Good Start!',
            'description': 'You\'ve made solid progress on your entrepreneurial journey.',
            'action': 'Continue with the next phase to build momentum.',
            'priority': 'medium'
        })
    else:
        insights.append({
            'type': 'warning',
            'title': 'Ready to Begin?',
            'description': 'Start your entrepreneurial journey with the Self Discovery assessment.',
            'action': 'Complete the foundation phases to unlock advanced features.',
            'priority': 'high'
        })
    
    # Add specific insights based on completed phases
    if completed_count >= 4:
        insights.append({
            'type': 'success',
            'title': 'Foundation Complete!',
            'description': 'You\'ve completed all foundation phases. Ready for implementation!',
            'action': 'Begin testing your business concepts with real market validation.',
            'priority': 'high'
        })
    
    # Add time-based insights
    recent_activity = db.session.query(AssessmentResponse)\
        .join(Assessment)\
        .filter(Assessment.user_id == assessments[0].user_id if assessments else 0)\
        .filter(AssessmentResponse.updated_at >= datetime.utcnow() - timedelta(days=7))\
        .count()
    
    if recent_activity == 0 and assessments:
        insights.append({
            'type': 'reminder',
            'title': 'Keep the Momentum!',
            'description': 'You haven\'t made progress in the last week.',
            'action': 'Continue where you left off to maintain your entrepreneurial journey.',
            'priority': 'medium'
        })
    
    return insights

def calculate_achievements(assessments):
    """Calculate user achievements based on assessment progress"""
    achievements = []
    completed_assessments = [a for a in assessments if a.is_completed]
    completed_count = len(completed_assessments)
    
    # Basic progress achievements
    if completed_count >= 1:
        first_completed = min(completed_assessments, key=lambda x: x.completed_at or x.started_at)
        achievements.append({
            'name': 'First Steps',
            'description': 'Completed your first assessment phase',
            'icon': '🎯',
            'earned_date': (first_completed.completed_at or first_completed.started_at).isoformat(),
            'category': 'progress'
        })
    
    if completed_count >= 4:
        foundation_phases = ['self_discovery', 'idea_discovery', 'market_research', 'business_pillars']
        foundation_completed = [a for a in completed_assessments if a.phase_id in foundation_phases]
        if len(foundation_completed) >= 4:
            latest_foundation = max(foundation_completed, key=lambda x: x.completed_at or x.started_at)
            achievements.append({
                'name': 'Foundation Builder',
                'description': 'Completed all foundation phases',
                'icon': '🏗️',
                'earned_date': (latest_foundation.completed_at or latest_foundation.started_at).isoformat(),
                'category': 'milestone'
            })
    
    if completed_count >= 7:
        latest_completed = max(completed_assessments, key=lambda x: x.completed_at or x.started_at)
        achievements.append({
            'name': 'Journey Complete',
            'description': 'Completed the entire 7-part assessment',
            'icon': '🏆',
            'earned_date': (latest_completed.completed_at or latest_completed.started_at).isoformat(),
            'category': 'completion'
        })
    
    # Specific phase achievements
    phase_achievements = {
        'self_discovery': {'name': 'Self-Aware', 'description': 'Discovered your entrepreneur archetype', 'icon': '🧠'},
        'idea_discovery': {'name': 'Idea Generator', 'description': 'Identified business opportunities', 'icon': '💡'},
        'market_research': {'name': 'Market Analyst', 'description': 'Completed market research and validation', 'icon': '📊'},
        'business_pillars': {'name': 'Strategic Planner', 'description': 'Built comprehensive business plan', 'icon': '📋'},
        'product_concept_testing': {'name': 'Product Tester', 'description': 'Validated product concepts', 'icon': '🧪'},
        'business_development': {'name': 'Business Developer', 'description': 'Mastered strategic decision-making', 'icon': '🚀'},
        'business_prototype_testing': {'name': 'Prototype Master', 'description': 'Completed business model validation', 'icon': '🔬'}
    }
    
    for assessment in completed_assessments:
        if assessment.phase_id in phase_achievements:
            achievement = phase_achievements[assessment.phase_id]
            achievements.append({
                'name': achievement['name'],
                'description': achievement['description'],
                'icon': achievement['icon'],
                'earned_date': (assessment.completed_at or assessment.started_at).isoformat(),
                'category': 'phase'
            })
    
    return achievements

def get_archetype_details(archetype):
    """Get detailed information about entrepreneur archetype"""
    archetype_data = {
        'visionary_builder': {
            'name': 'Visionary Builder',
            'description': 'Focused on creating transformative solutions that change the world',
            'traits': ['Innovation-focused', 'Long-term thinking', 'High risk tolerance', 'Transformative solutions'],
            'business_focus': 'Innovation, disruption, major impact',
            'time_horizon': '10+ years',
            'examples': ['Tech startups', 'Revolutionary products', 'Social movements'],
            'strengths': ['Strategic vision', 'Innovation capability', 'Risk management'],
            'development_areas': ['Execution focus', 'Short-term planning', 'Operational details']
        },
        'practical_problem_solver': {
            'name': 'Practical Problem-Solver',
            'description': 'Identifies problems and creates practical solutions',
            'traits': ['Solution-oriented', 'Practical approach', 'Customer-focused', 'Immediate impact'],
            'business_focus': 'Useful products/services, customer solutions',
            'time_horizon': '3-5 years',
            'examples': ['Service businesses', 'Consulting', 'Improved traditional offerings'],
            'strengths': ['Problem identification', 'Customer empathy', 'Practical solutions'],
            'development_areas': ['Scaling strategies', 'Innovation thinking', 'Long-term vision']
        },
        'lifestyle_freedom_seeker': {
            'name': 'Lifestyle Freedom-Seeker',
            'description': 'Builds businesses that support desired lifestyle',
            'traits': ['Work-life balance', 'Personal freedom', 'Flexible approach', 'Lifestyle alignment'],
            'business_focus': 'Sustainable income, work-life balance',
            'time_horizon': 'Flexible',
            'examples': ['Online businesses', 'Freelancing', 'Location-independent work'],
            'strengths': ['Work-life integration', 'Flexibility', 'Personal motivation'],
            'development_areas': ['Growth strategies', 'Team building', 'Systematic processes']
        },
        'serial_entrepreneur': {
            'name': 'Serial Entrepreneur',
            'description': 'Experienced in building and scaling multiple businesses',
            'traits': ['Experience-driven', 'Network-focused', 'Scaling expertise', 'Pattern recognition'],
            'business_focus': 'Scalable businesses, portfolio approach',
            'time_horizon': '5-10 years per venture',
            'examples': ['Multiple startups', 'Investment portfolio', 'Business acquisitions'],
            'strengths': ['Experience leverage', 'Network utilization', 'Scaling knowledge'],
            'development_areas': ['Fresh perspectives', 'Industry innovation', 'Emerging trends']
        }
    }
    
    return archetype_data.get(archetype, {
        'name': 'Unknown Archetype',
        'description': 'Archetype not yet determined',
        'traits': [],
        'business_focus': 'To be determined',
        'time_horizon': 'Flexible',
        'examples': [],
        'strengths': [],
        'development_areas': []
    })

def generate_recommendations(assessments, profile):
    """Generate personalized recommendations based on user data"""
    recommendations = []
    completed_phases = [a.phase_id for a in assessments if a.is_completed]
    
    # Phase-specific recommendations
    phase_order = ['self_discovery', 'idea_discovery', 'market_research', 'business_pillars', 
                  'product_concept_testing', 'business_development', 'business_prototype_testing']
    
    for phase_id in phase_order:
        if phase_id not in completed_phases:
            phase_recommendations = get_phase_recommendations(phase_id)
            recommendations.extend(phase_recommendations)
            break  # Only recommend the next phase
    
    # Profile-based recommendations
    if profile and profile.entrepreneur_archetype:
        archetype_recommendations = get_archetype_recommendations(profile.entrepreneur_archetype)
        recommendations.extend(archetype_recommendations)
    
    # Progress-based recommendations
    if len(completed_phases) >= 4:
        recommendations.append({
            'type': 'milestone',
            'title': 'Ready for Implementation',
            'description': 'You\'ve completed the foundation. Time to test your concepts!',
            'priority': 'high',
            'estimated_time': '2-4 weeks',
            'category': 'next_step'
        })
    
    # Add learning resources
    recommendations.extend(get_learning_resources(completed_phases, profile))
    
    return recommendations

def get_phase_recommendations(phase_id):
    """Get recommendations for specific assessment phase"""
    phase_recommendations = {
        'self_discovery': [
            {
                'type': 'next_step',
                'title': 'Start with Self-Discovery',
                'description': 'Begin your journey by understanding your entrepreneurial personality and motivations',
                'priority': 'high',
                'estimated_time': '60-90 minutes',
                'category': 'assessment'
            }
        ],
        'idea_discovery': [
            {
                'type': 'next_step',
                'title': 'Explore Business Ideas',
                'description': 'Transform your insights into concrete business opportunities',
                'priority': 'high',
                'estimated_time': '90-120 minutes',
                'category': 'assessment'
            }
        ],
        'market_research': [
            {
                'type': 'next_step',
                'title': 'Validate Your Market',
                'description': 'Research your target market and validate your business concepts',
                'priority': 'high',
                'estimated_time': '2-3 hours',
                'category': 'assessment'
            }
        ],
        'business_pillars': [
            {
                'type': 'next_step',
                'title': 'Build Business Foundation',
                'description': 'Develop the key pillars of your business strategy',
                'priority': 'high',
                'estimated_time': '2-4 hours',
                'category': 'assessment'
            }
        ]
    }
    
    return phase_recommendations.get(phase_id, [])

def get_archetype_recommendations(archetype):
    """Get recommendations specific to entrepreneur archetype"""
    recommendations_map = {
        'visionary_builder': [
            {
                'type': 'resource',
                'title': 'Innovation Resources',
                'description': 'Explore cutting-edge technologies and disruptive business models',
                'priority': 'medium',
                'category': 'learning'
            },
            {
                'type': 'skill',
                'title': 'Execution Focus',
                'description': 'Develop skills in turning vision into actionable plans',
                'priority': 'high',
                'category': 'development'
            }
        ],
        'practical_problem_solver': [
            {
                'type': 'resource',
                'title': 'Customer Research Tools',
                'description': 'Focus on understanding customer pain points and needs',
                'priority': 'medium',
                'category': 'learning'
            },
            {
                'type': 'skill',
                'title': 'Scaling Strategies',
                'description': 'Learn how to scale practical solutions into larger businesses',
                'priority': 'high',
                'category': 'development'
            }
        ],
        'lifestyle_freedom_seeker': [
            {
                'type': 'resource',
                'title': 'Remote Business Models',
                'description': 'Explore business models that support location independence',
                'priority': 'medium',
                'category': 'learning'
            },
            {
                'type': 'skill',
                'title': 'Systematic Processes',
                'description': 'Develop systems that allow business growth without constant oversight',
                'priority': 'high',
                'category': 'development'
            }
        ]
    }
    
    return recommendations_map.get(archetype, [])

def get_learning_resources(completed_phases, profile):
    """Get learning resources based on progress and profile"""
    resources = []
    
    # Basic resources for all users
    if len(completed_phases) >= 2:
        resources.append({
            'type': 'resource',
            'title': 'Business Plan Templates',
            'description': 'Access professional business plan templates and examples',
            'priority': 'low',
            'category': 'tool'
        })
    
    if len(completed_phases) >= 4:
        resources.append({
            'type': 'resource',
            'title': 'Market Validation Toolkit',
            'description': 'Tools and techniques for validating your business concepts',
            'priority': 'medium',
            'category': 'tool'
        })
    
    return resources

