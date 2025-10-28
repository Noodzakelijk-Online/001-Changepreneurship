"""
Test Data Creation for Executive Summary Dashboard
Creates sample assessment data to demonstrate AI functionality
"""
import json
from datetime import datetime, timedelta
from ..models.assessment import db, User, Assessment, AssessmentResponse

class TestDataGenerator:
    """
    Generates comprehensive test data for dashboard testing
    """
    
    def __init__(self, session=None):
        self.session = session or db.session
    
    def create_test_user(self, username='executive_test_user'):
        """
        Create a test user with comprehensive assessment data
        """
        try:
            # Check if user already exists
            existing_user = self.session.query(User).filter_by(username=username).first()
            if existing_user:
                print(f"Test user {username} already exists, updating data...")
                return existing_user
            
            # Create new test user (let DB assign auto-increment ID)
            test_user = User(
                username=username,
                email='executive.test@changepreneurship.com',
                password_hash='test_hash'
            )
            
            self.session.add(test_user)
            self.session.commit()
            
            print(f"Created test user: {username} (ID: {test_user.id})")
            return test_user
            
        except Exception as e:
            print(f"Error creating test user: {str(e)}")
            self.session.rollback()
            return None
    
    def create_comprehensive_assessments(self, user_id):
        """
        Create comprehensive assessment data across all phases
        """
        try:
            # Assessment phases with realistic completion levels
            assessment_phases = [
                {
                    'phase_name': 'Self Discovery Assessment',
                    'progress_percentage': 95,
                    'response_count': 12
                },
                {
                    'phase_name': 'Idea Discovery Assessment', 
                    'progress_percentage': 87,
                    'response_count': 10
                },
                {
                    'phase_name': 'Market Research',
                    'progress_percentage': 78,
                    'response_count': 9
                },
                {
                    'phase_name': 'Business Pillars Planning',
                    'progress_percentage': 92,
                    'response_count': 15
                },
                {
                    'phase_name': 'Product Concept Testing',
                    'progress_percentage': 83,
                    'response_count': 8
                },
                {
                    'phase_name': 'Business Development',
                    'progress_percentage': 76,
                    'response_count': 11
                },
                {
                    'phase_name': 'Business Prototype Testing',
                    'progress_percentage': 69,
                    'response_count': 7
                }
            ]
            
            created_assessments = []
            
            for i, phase_data in enumerate(assessment_phases):
                # Check if assessment already exists
                existing_assessment = self.session.query(Assessment).filter_by(
                    user_id=user_id,
                    phase_name=phase_data['phase_name']
                ).first()
                
                if existing_assessment:
                    # Update existing assessment
                    existing_assessment.progress_percentage = phase_data['progress_percentage']
                    assessment = existing_assessment
                else:
                    # Create new assessment
                    assessment = Assessment(
                        user_id=user_id,
                        phase_id=phase_data['phase_name'].lower().replace(' ', '_'),
                        phase_name=phase_data['phase_name'],
                        progress_percentage=phase_data['progress_percentage']
                    )
                    self.session.add(assessment)
                
                self.session.commit()
                
                # Create or update responses
                self._create_assessment_responses(
                    assessment.id, 
                    phase_data['response_count'],
                    phase_data['phase_name']
                )
                
                created_assessments.append(assessment)
                print(f"Created/updated assessment: {phase_data['phase_name']}")
            
            return created_assessments
            
        except Exception as e:
            print(f"Error creating assessments: {str(e)}")
            self.session.rollback()
            return []
    
    def _create_assessment_responses(self, assessment_id, response_count, phase_name):
        """
        Create realistic assessment responses for testing
        """
        try:
            # Clear existing responses
            existing_responses = self.session.query(AssessmentResponse).filter_by(
                assessment_id=assessment_id
            ).all()
            
            for response in existing_responses:
                self.session.delete(response)
            
            # Response templates based on phase
            response_templates = self._get_response_templates(phase_name)
            
            for i in range(response_count):
                template = response_templates[i % len(response_templates)]
                
                response = AssessmentResponse(
                    assessment_id=assessment_id,
                    question_id=f"{phase_name.lower().replace(' ', '_')}_q{i+1}",
                    response_value=template['value'],
                    response_type=template['type'],
                    created_at=datetime.utcnow() - timedelta(days=i)
                )
                
                self.session.add(response)
            
            self.session.commit()
            print(f"Created {response_count} responses for {phase_name}")
            
        except Exception as e:
            print(f"Error creating responses: {str(e)}")
            self.session.rollback()
    
    def _get_response_templates(self, phase_name):
        """
        Get realistic response templates for each assessment phase
        """
        templates = {
            'Self Discovery Assessment': [
                {'value': 'Highly motivated entrepreneur with 5+ years experience', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'Technology,Innovation,Leadership', 'type': 'multiple_choice'},
                {'value': 'Building scalable tech solutions for businesses', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Strong analytical and strategic thinking abilities', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'Team leadership,Product development,Market analysis', 'type': 'multiple_choice'},
                {'value': 'Creating innovative solutions that solve real problems', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'High risk tolerance with calculated decision making', 'type': 'text'},
                {'value': '4', 'type': 'scale'}
            ],
            'Idea Discovery Assessment': [
                {'value': 'AI-powered business analytics platform for SMEs', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Small and medium enterprises lacking data insights', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'High market demand with limited affordable solutions', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Subscription-based SaaS model with tiered pricing', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'Advanced AI algorithms and intuitive dashboard design', 'type': 'text'},
                {'value': '5', 'type': 'scale'}
            ],
            'Market Research': [
                {'value': '$2.5B global business analytics market segment', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Tableau, Power BI, Looker - but complex and expensive', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'SMEs (50-500 employees) in tech, retail, finance sectors', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': '15% annual growth rate in SME analytics adoption', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'Price-sensitive customers need simplified solutions', 'type': 'text'}
            ],
            'Business Pillars Planning': [
                {'value': 'Democratizing business intelligence for SMEs globally', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Lean startup with agile development methodology', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': '$50K-200K monthly recurring revenue by year 2', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Strategic partnerships with cloud providers and consultants', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'Customer success team and automated onboarding', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Data security, GDPR compliance, 99.9% uptime SLA', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'Series A funding target: $2M for team and technology', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Break-even by month 18 with 40% gross margins', 'type': 'text'},
                {'value': '4', 'type': 'scale'}
            ],
            'Product Concept Testing': [
                {'value': 'MVP tested with 25 SME customers, 85% satisfaction', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': '$99-299 monthly tiers based on data volume and features', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Intuitive drag-drop interface with pre-built templates', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'Real-time dashboards, predictive analytics, custom reports', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': '92% users find value within first 30 days', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'Integration with 50+ popular business tools via APIs', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Mobile app and white-label options planned for Q3', 'type': 'text'},
                {'value': '4', 'type': 'scale'}
            ],
            'Business Development': [
                {'value': 'Digital marketing, partner channels, inside sales team', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': '$120 customer acquisition cost, $2,400 lifetime value', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': '5-person core team: CEO, CTO, 2 developers, 1 marketer', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'Milestone-based development with quarterly OKRs', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Market saturation and increasing competition risks', 'type': 'text'},
                {'value': '3', 'type': 'scale'},
                {'value': 'Diversification strategy and strong customer retention focus', 'type': 'text'},
                {'value': '4', 'type': 'scale'}
            ],
            'Business Prototype Testing': [
                {'value': 'Beta platform deployed on AWS with 50 test users', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': '78% user engagement rate, 15% churn monthly', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'A/B testing on pricing and feature combinations', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Positive feedback on ease of use and actionable insights', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'Scaling infrastructure and adding advanced AI features', 'type': 'text'},
                {'value': '5', 'type': 'scale'},
                {'value': 'Partnership discussions with 3 major consulting firms', 'type': 'text'},
                {'value': '4', 'type': 'scale'},
                {'value': 'Go-to-market launch planned for Q2 next year', 'type': 'text'},
                {'value': '5', 'type': 'scale'}
            ]
        }
        
        return templates.get(phase_name, [
            {'value': 'Sample response for testing', 'type': 'text'},
            {'value': '4', 'type': 'scale'}
        ])
    
    def create_complete_test_scenario(self):
        """
        Create complete test scenario with user and assessments
        """
        try:
            print("Creating comprehensive test data for Executive Summary Dashboard...")
            
            # Create test user
            test_user = self.create_test_user('executive_test_user')
            if not test_user:
                return False
            
            # Create comprehensive assessments
            assessments = self.create_comprehensive_assessments(test_user.id)
            if not assessments:
                return False
            
            print(f"✅ Successfully created test scenario:")
            print(f"   - User: {test_user.username} (ID: {test_user.id})")
            print(f"   - Assessments: {len(assessments)}")
            print(f"   - Total responses: {sum(len(a.responses) for a in assessments) if hasattr(assessments[0], 'responses') else 'N/A'}")
            print(f"   - Average completion: {sum(a.progress_percentage for a in assessments) / len(assessments):.1f}%")
            
            return test_user.id  # Return user ID for dashboard testing
            
        except Exception as e:
            print(f"Error creating complete test scenario: {str(e)}")
            return False
    
    def cleanup_test_data(self, username='executive_test_user'):
        """
        Clean up test data
        """
        try:
            # Delete user and all related data (cascade)
            test_user = self.session.query(User).filter_by(username=username).first()
            if test_user:
                self.session.delete(test_user)
                self.session.commit()
                print(f"✅ Cleaned up test data for user: {username}")
                return True
            else:
                print(f"No test user found: {username}")
                return False
                
        except Exception as e:
            print(f"Error cleaning up test data: {str(e)}")
            self.session.rollback()
            return False