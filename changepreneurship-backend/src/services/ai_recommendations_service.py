"""
AI Recommendations Engine
Generates personalized business recommendations based on user assessment responses
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..models.assessment import db, User, Assessment, AssessmentResponse

class AIRecommendationsEngine:
    """
    Analyzes user assessment data and generates personalized recommendations
    aligned with founder readiness and business success probability
    """
    
    def __init__(self, session=None):
        self.session = session or db.session
    
    def generate_recommendations(self, user_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive AI recommendations for a user
        """
        try:
            # Get user assessment data
            user_data = self._get_user_assessment_data(user_id)
            
            if not user_data:
                return self._generate_onboarding_recommendations()
            
            # Analyze founder profile
            founder_profile = self._analyze_founder_profile(user_data)
            
            # Calculate success probability
            success_probability = self._calculate_success_probability(user_data, founder_profile)
            
            # Generate personalized recommendations
            recommendations = self._generate_personalized_recommendations(
                user_data, founder_profile, success_probability
            )
            
            # Identify strengths and gaps
            strengths = self._identify_strengths(user_data, founder_profile)
            gaps = self._identify_gaps(user_data, founder_profile)
            
            # Generate next steps
            next_steps = self._generate_next_steps(gaps, founder_profile)
            
            # Generate risk assessment
            risks = self._assess_risks(user_data, founder_profile)
            
            return {
                'user_id': user_id,
                'generated_at': datetime.utcnow().isoformat(),
                'founder_profile': founder_profile,
                'success_probability': success_probability,
                'strengths': strengths,
                'gaps': gaps,
                'recommendations': recommendations,
                'next_steps': next_steps,
                'risks': risks,
                'ai_confidence': self._calculate_confidence(user_data)
            }
            
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            return self._generate_onboarding_recommendations()
    
    def _get_user_assessment_data(self, user_id: int) -> Optional[Dict]:
        """
        Retrieve user's assessment data
        """
        try:
            user = self.session.query(User).filter_by(id=user_id).first()
            if not user:
                return None
            
            assessments = self.session.query(Assessment).filter_by(user_id=user_id).all()
            
            user_data = {
                'user_id': user_id,
                'username': user.username,
                'assessments': []
            }
            
            for assessment in assessments:
                responses = self.session.query(AssessmentResponse).filter_by(
                    assessment_id=assessment.id
                ).all()
                
                assessment_data = {
                    'phase_name': assessment.phase_name,
                    'progress': assessment.progress_percentage,
                    'responses': [
                        {
                            'question_id': r.question_id,
                            'value': r.response_value,
                            'type': r.response_type
                        }
                        for r in responses
                    ]
                }
                user_data['assessments'].append(assessment_data)
            
            return user_data
            
        except Exception as e:
            print(f"Error retrieving user data: {str(e)}")
            return None
    
    def _analyze_founder_profile(self, user_data: Dict) -> Dict[str, Any]:
        """
        Analyze founder's profile based on assessment responses
        """
        assessments = user_data.get('assessments', [])
        
        # Initialize profile attributes
        profile = {
            'archetype': 'Unknown',
            'risk_tolerance': 'Medium',
            'readiness_level': 'Early Stage',
            'motivation_type': 'Unknown',
            'strengths': [],
            'experience_level': 'Beginner'
        }
        
        # Analyze Self Discovery Assessment
        self_discovery = next((a for a in assessments if 'Self Discovery' in a['phase_name']), None)
        if self_discovery:
            profile.update(self._analyze_self_discovery(self_discovery))
        
        # Analyze Idea Discovery
        idea_discovery = next((a for a in assessments if 'Idea Discovery' in a['phase_name']), None)
        if idea_discovery:
            profile.update(self._analyze_idea_discovery(idea_discovery))
        
        # Analyze Market Research
        market_research = next((a for a in assessments if 'Market Research' in a['phase_name']), None)
        if market_research:
            profile.update(self._analyze_market_research(market_research))
        
        return profile
    
    def _analyze_self_discovery(self, assessment: Dict) -> Dict:
        """
        Analyze self discovery assessment responses
        """
        responses = assessment.get('responses', [])
        
        # Count scale responses to determine risk tolerance
        scale_scores = [int(r['value']) for r in responses if r['type'] == 'scale' and r['value'].isdigit()]
        avg_score = sum(scale_scores) / len(scale_scores) if scale_scores else 3
        
        # Determine archetype based on responses
        text_responses = [r['value'].lower() for r in responses if r['type'] == 'text']
        
        archetype = 'Innovator'
        if any('technology' in resp or 'innovation' in resp for resp in text_responses):
            archetype = 'Tech Innovator'
        elif any('leadership' in resp or 'team' in resp for resp in text_responses):
            archetype = 'Visionary Leader'
        elif any('analytical' in resp or 'data' in resp for resp in text_responses):
            archetype = 'Strategic Analyst'
        
        risk_tolerance = 'High' if avg_score >= 4 else 'Medium' if avg_score >= 3 else 'Conservative'
        
        return {
            'archetype': archetype,
            'risk_tolerance': risk_tolerance,
            'motivation_type': 'Innovation-Driven' if avg_score >= 4 else 'Stability-Seeking'
        }
    
    def _analyze_idea_discovery(self, assessment: Dict) -> Dict:
        """
        Analyze idea discovery assessment responses
        """
        responses = assessment.get('responses', [])
        
        # Determine if idea is well-defined
        text_responses = [r['value'] for r in responses if r['type'] == 'text']
        
        has_clear_idea = len([r for r in text_responses if len(r) > 50]) >= 3
        
        return {
            'readiness_level': 'Idea Validation Stage' if has_clear_idea else 'Ideation Stage',
            'idea_clarity': 'High' if has_clear_idea else 'Developing'
        }
    
    def _analyze_market_research(self, assessment: Dict) -> Dict:
        """
        Analyze market research assessment responses
        """
        responses = assessment.get('responses', [])
        
        # Check market understanding depth
        detailed_responses = len([r for r in responses if r['type'] == 'text' and len(r['value']) > 100])
        
        return {
            'market_understanding': 'Advanced' if detailed_responses >= 3 else 'Intermediate' if detailed_responses >= 1 else 'Basic',
            'experience_level': 'Intermediate' if detailed_responses >= 2 else 'Beginner'
        }
    
    def _calculate_success_probability(self, user_data: Dict, founder_profile: Dict) -> Dict[str, Any]:
        """
        Calculate AI-driven success probability
        """
        assessments = user_data.get('assessments', [])
        
        # Base score
        base_score = 50
        
        # Assessment completion factor (0-20 points)
        completion_count = len(assessments)
        completion_score = min(20, completion_count * 3)
        
        # Response quality factor (0-15 points)
        total_responses = sum(len(a.get('responses', [])) for a in assessments)
        quality_score = min(15, total_responses // 2)
        
        # Founder readiness factor (0-20 points)
        readiness_map = {
            'Early Stage': 5,
            'Ideation Stage': 10,
            'Idea Validation Stage': 15,
            'Market Entry Stage': 20
        }
        readiness_score = readiness_map.get(founder_profile.get('readiness_level', 'Early Stage'), 5)
        
        # Risk tolerance alignment (0-15 points)
        risk_map = {'High': 15, 'Medium': 10, 'Conservative': 5}
        risk_score = risk_map.get(founder_profile.get('risk_tolerance', 'Medium'), 10)
        
        # Market understanding (0-15 points)
        market_map = {'Advanced': 15, 'Intermediate': 10, 'Basic': 5}
        market_score = market_map.get(founder_profile.get('market_understanding', 'Basic'), 5)
        
        # Calculate total
        total_score = base_score + completion_score + quality_score + readiness_score + risk_score + market_score
        final_probability = min(95, max(35, total_score))
        
        # Determine category
        if final_probability >= 80:
            category = 'High Success Potential'
        elif final_probability >= 65:
            category = 'Strong Foundation'
        elif final_probability >= 50:
            category = 'Growing Potential'
        else:
            category = 'Building Phase'
        
        return {
            'score': final_probability,
            'category': category,
            'factors': {
                'assessment_completion': completion_score,
                'response_quality': quality_score,
                'founder_readiness': readiness_score,
                'risk_alignment': risk_score,
                'market_knowledge': market_score
            }
        }
    
    def _identify_strengths(self, user_data: Dict, founder_profile: Dict) -> List[Dict]:
        """
        Identify user's key strengths
        """
        strengths = []
        
        # Archetype strength
        archetype = founder_profile.get('archetype', 'Unknown')
        if archetype != 'Unknown':
            strengths.append({
                'title': f'{archetype} Profile',
                'description': f'Your {archetype.lower()} profile indicates strong capabilities in innovation and strategic thinking.',
                'impact': 'High',
                'icon': 'brain'
            })
        
        # Risk tolerance
        risk = founder_profile.get('risk_tolerance', 'Medium')
        if risk == 'High':
            strengths.append({
                'title': 'High Risk Tolerance',
                'description': 'Your willingness to take calculated risks is essential for entrepreneurial success.',
                'impact': 'High',
                'icon': 'trending-up'
            })
        
        # Assessment completion
        assessment_count = len(user_data.get('assessments', []))
        if assessment_count >= 5:
            strengths.append({
                'title': 'Comprehensive Assessment',
                'description': f'You\'ve completed {assessment_count} assessments, showing strong commitment to preparation.',
                'impact': 'Medium',
                'icon': 'check-circle'
            })
        
        # Market understanding
        market_level = founder_profile.get('market_understanding', 'Basic')
        if market_level in ['Advanced', 'Intermediate']:
            strengths.append({
                'title': f'{market_level} Market Understanding',
                'description': 'Your market research demonstrates solid understanding of your target audience.',
                'impact': 'High',
                'icon': 'target'
            })
        
        return strengths
    
    def _identify_gaps(self, user_data: Dict, founder_profile: Dict) -> List[Dict]:
        """
        Identify areas for improvement
        """
        gaps = []
        
        assessments = user_data.get('assessments', [])
        phase_names = [a['phase_name'] for a in assessments]
        
        # Check for missing assessments
        required_phases = [
            'Self Discovery Assessment',
            'Idea Discovery Assessment',
            'Market Research',
            'Business Pillars Planning'
        ]
        
        for phase in required_phases:
            if not any(phase in name for name in phase_names):
                gaps.append({
                    'title': f'Complete {phase}',
                    'description': f'This assessment is crucial for validating your entrepreneurial readiness.',
                    'priority': 'High',
                    'icon': 'alert-circle'
                })
        
        # Check readiness level
        if founder_profile.get('readiness_level') == 'Early Stage':
            gaps.append({
                'title': 'Strengthen Business Foundation',
                'description': 'Focus on developing a clear value proposition and market positioning.',
                'priority': 'High',
                'icon': 'build'
            })
        
        # Check market understanding
        if founder_profile.get('market_understanding') == 'Basic':
            gaps.append({
                'title': 'Deepen Market Knowledge',
                'description': 'Conduct more thorough competitive analysis and customer research.',
                'priority': 'Medium',
                'icon': 'search'
            })
        
        return gaps
    
    def _generate_personalized_recommendations(self, user_data: Dict, founder_profile: Dict, success_prob: Dict) -> List[Dict]:
        """
        Generate personalized action recommendations
        """
        recommendations = []
        
        # Based on archetype
        archetype = founder_profile.get('archetype', 'Unknown')
        
        if 'Tech' in archetype or 'Innovator' in archetype:
            recommendations.append({
                'category': 'Product Development',
                'title': 'Leverage Your Technical Expertise',
                'description': 'Focus on building an MVP that showcases your technical innovation. Start with core features that solve a specific problem.',
                'priority': 'High',
                'timeframe': '1-2 months',
                'resources': ['Y Combinator Startup School', 'Lean Startup methodology']
            })
        
        if founder_profile.get('risk_tolerance') == 'Conservative':
            recommendations.append({
                'category': 'Risk Management',
                'title': 'Build Safety Nets',
                'description': 'Given your conservative risk profile, focus on maintaining financial stability while building your business part-time initially.',
                'priority': 'High',
                'timeframe': 'Ongoing',
                'resources': ['Side Hustle strategies', 'Bootstrap funding guides']
            })
        
        # Based on success probability
        if success_prob['score'] < 60:
            recommendations.append({
                'category': 'Founder Readiness',
                'title': 'Strengthen Your Foundation',
                'description': 'Complete remaining assessments to gain deeper insights into your entrepreneurial journey and increase success probability.',
                'priority': 'Critical',
                'timeframe': '2-3 weeks',
                'resources': ['Complete all 7 assessment phases']
            })
        
        # Market-based recommendations
        if founder_profile.get('market_understanding') in ['Basic', 'Intermediate']:
            recommendations.append({
                'category': 'Market Validation',
                'title': 'Conduct Customer Interviews',
                'description': 'Speak with 20-30 potential customers to validate your assumptions and refine your value proposition.',
                'priority': 'High',
                'timeframe': '3-4 weeks',
                'resources': ['The Mom Test by Rob Fitzpatrick', 'Customer discovery templates']
            })
        
        return recommendations
    
    def _generate_next_steps(self, gaps: List[Dict], founder_profile: Dict) -> List[Dict]:
        """
        Generate actionable next steps
        """
        next_steps = []
        
        # Prioritize based on gaps
        for i, gap in enumerate(gaps[:3]):  # Top 3 priorities
            next_steps.append({
                'step_number': i + 1,
                'action': gap['title'],
                'description': gap['description'],
                'estimated_time': '1-2 weeks',
                'status': 'pending'
            })
        
        # Add growth-oriented steps
        next_steps.append({
            'step_number': len(next_steps) + 1,
            'action': 'Review AI Executive Summary',
            'description': 'Analyze your comprehensive business readiness dashboard for detailed insights.',
            'estimated_time': '30 minutes',
            'status': 'recommended'
        })
        
        return next_steps
    
    def _assess_risks(self, user_data: Dict, founder_profile: Dict) -> List[Dict]:
        """
        Assess potential risks
        """
        risks = []
        
        # Assessment completion risk
        assessment_count = len(user_data.get('assessments', []))
        if assessment_count < 4:
            risks.append({
                'category': 'Preparation Risk',
                'title': 'Incomplete Assessment',
                'description': 'Limited assessment data may lead to blind spots in your business planning.',
                'severity': 'Medium',
                'mitigation': 'Complete all 7 assessment phases for comprehensive insights.'
            })
        
        # Market risk
        if founder_profile.get('market_understanding') == 'Basic':
            risks.append({
                'category': 'Market Risk',
                'title': 'Limited Market Knowledge',
                'description': 'Insufficient market research may result in poor product-market fit.',
                'severity': 'High',
                'mitigation': 'Conduct thorough competitive analysis and customer validation.'
            })
        
        # Experience risk
        if founder_profile.get('experience_level') == 'Beginner':
            risks.append({
                'category': 'Experience Gap',
                'title': 'Limited Entrepreneurial Experience',
                'description': 'First-time founders face a steep learning curve.',
                'severity': 'Medium',
                'mitigation': 'Seek mentorship and join entrepreneur communities.'
            })
        
        return risks
    
    def _calculate_confidence(self, user_data: Dict) -> int:
        """
        Calculate AI confidence in recommendations
        """
        assessments = user_data.get('assessments', [])
        total_responses = sum(len(a.get('responses', [])) for a in assessments)
        
        # Base confidence on data quantity and quality
        if total_responses >= 40:
            return 95
        elif total_responses >= 25:
            return 85
        elif total_responses >= 15:
            return 75
        elif total_responses >= 5:
            return 65
        else:
            return 50
    
    def _generate_onboarding_recommendations(self) -> Dict[str, Any]:
        """
        Generate recommendations for users with no assessment data
        """
        return {
            'user_id': None,
            'generated_at': datetime.utcnow().isoformat(),
            'founder_profile': {
                'archetype': 'Not Yet Assessed',
                'readiness_level': 'Pre-Assessment',
                'message': 'Complete assessments to receive personalized AI recommendations'
            },
            'success_probability': {
                'score': 0,
                'category': 'Not Assessed',
                'message': 'Begin your journey by completing the Self Discovery Assessment'
            },
            'strengths': [],
            'gaps': [
                {
                    'title': 'Start Your Assessment Journey',
                    'description': 'Complete the Self Discovery Assessment to unlock personalized AI insights.',
                    'priority': 'Critical',
                    'icon': 'play-circle'
                }
            ],
            'recommendations': [
                {
                    'category': 'Getting Started',
                    'title': 'Begin with Self Discovery',
                    'description': 'Understand your entrepreneurial profile, strengths, and motivations.',
                    'priority': 'Critical',
                    'timeframe': '30-45 minutes',
                    'resources': ['Self Discovery Assessment']
                }
            ],
            'next_steps': [
                {
                    'step_number': 1,
                    'action': 'Complete Self Discovery Assessment',
                    'description': 'Start your entrepreneurial journey with a comprehensive self-assessment.',
                    'estimated_time': '30-45 minutes',
                    'status': 'pending'
                }
            ],
            'risks': [],
            'ai_confidence': 0
        }
