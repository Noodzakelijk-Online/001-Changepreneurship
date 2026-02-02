#!/usr/bin/env python3
"""
Create COMPLETE test user with ALL questions from frontend assessment components.

Self Discovery Assessment (5 questions):
- primary-motivation (multiple-choice)
- success-vision (textarea)
- risk-tolerance (scale 1-10)
- life-satisfaction (multiple-scale with 8 areas)
- top-values (ranking of 8 values)
- ten-year-vision (textarea)
- vision-confidence (scale 1-10)

Idea Discovery Assessment (7 questions):
- passion-work-matrix (matrix: 5 rows x 3 columns)
- cause-alignment (ranking of 8 causes)
- current-skills (matrix: 8 rows x 3 columns)
- problem-experiences (textarea)
- problem-observation (textarea)
- value-proposition (textarea)
- target-customer (textarea)
- opportunity-criteria (scale 1-10)
"""

import sys
import json
from datetime import datetime, timezone
sys.path.insert(0, '/app')

from src.main import app
from src.models.assessment import db, Assessment, AssessmentResponse, User
from werkzeug.security import generate_password_hash


def create_complete_test_user():
    """Create test user with ALL questions answered"""
    
    with app.app_context():
        # User credentials
        email = f"complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}@test.com"
        password = "Test123!"
        username = "Complete Test User"
        
        print("\n" + "="*80)
        print("🎯 CREATING COMPLETE TEST USER WITH ALL FRONTEND QUESTIONS")
        print("="*80)
        
        # Create user
        user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.flush()
        user_id = user.id
        
        print(f"\n✅ User Created:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   User ID: {user_id}")
        
        # ==============================================================================
        # SELF DISCOVERY ASSESSMENT - 7 Questions
        # ==============================================================================
        self_discovery_responses = [
            # Motivation section
            {
                'id': 'primary-motivation',
                'section': 'motivation',
                'value': 'social-impact',
                'type': 'multiple-choice'
            },
            {
                'id': 'success-vision',
                'section': 'motivation',
                'value': 'I imagine running a thriving tech company with 50-100 employees, working 40-45 hours per week with flexibility. Success means creating products that genuinely improve people\'s lives while building a sustainable business that provides great careers for my team. I see myself mentoring younger entrepreneurs and giving back to the community.',
                'type': 'textarea'
            },
            {
                'id': 'risk-tolerance',
                'section': 'motivation',
                'value': '7',
                'type': 'scale'
            },
            # Life Impact section
            {
                'id': 'life-satisfaction',
                'section': 'life-impact',
                'value': json.dumps({
                    "Health": 8,
                    "Money": 7,
                    "Family": 9,
                    "Friends": 7,
                    "Career": 6,
                    "Growth": 8,
                    "Recreation": 7,
                    "Environment": 8
                }),
                'type': 'multiple-scale'
            },
            # Values section
            {
                'id': 'top-values',
                'section': 'values',
                'value': json.dumps([
                    {"value": "making-difference", "rank": 1},
                    {"value": "learning", "rank": 2},
                    {"value": "personal-freedom", "rank": 3},
                    {"value": "family-time", "rank": 4},
                    {"value": "financial-success", "rank": 5},
                    {"value": "adventure", "rank": 6},
                    {"value": "security", "rank": 7},
                    {"value": "recognition", "rank": 8}
                ]),
                'type': 'ranking'
            },
            # Vision section
            {
                'id': 'ten-year-vision',
                'section': 'vision',
                'value': 'At age 45, I am leading a profitable EdTech company that has helped over 1 million students learn more effectively. I work from a beautiful office with a talented team of 75 people. My mornings start with exercise, I have dinner with my family most nights, and I mentor 3-4 young entrepreneurs. Financially secure with diversified investments, I contribute to educational nonprofits and speak at conferences about ethical AI in education.',
                'type': 'textarea'
            },
            # Confidence section
            {
                'id': 'vision-confidence',
                'section': 'confidence',
                'value': '8',
                'type': 'scale'
            }
        ]
        
        # ==============================================================================
        # IDEA DISCOVERY ASSESSMENT - 8 Questions
        # ==============================================================================
        idea_discovery_responses = [
            # Core Alignment section
            {
                'id': 'passion-work-matrix',
                'section': 'core-alignment',
                'value': json.dumps({
                    "creative-work": {"passion": 4, "skill": 3, "potential": 4},
                    "analytical-work": {"passion": 5, "skill": 5, "potential": 4},
                    "technical-work": {"passion": 5, "skill": 4, "potential": 5},
                    "people-work": {"passion": 4, "skill": 4, "potential": 4},
                    "operational-work": {"passion": 3, "skill": 3, "potential": 3}
                }),
                'type': 'matrix'
            },
            {
                'id': 'cause-alignment',
                'section': 'core-alignment',
                'value': json.dumps([
                    {"value": "education", "rank": 1},
                    {"value": "technology-innovation", "rank": 2},
                    {"value": "economic-empowerment", "rank": 3},
                    {"value": "personal-development", "rank": 4},
                    {"value": "community-building", "rank": 5},
                    {"value": "environmental", "rank": 6},
                    {"value": "healthcare", "rank": 7},
                    {"value": "social-justice", "rank": 8}
                ]),
                'type': 'ranking'
            },
            # Skills Assessment section
            {
                'id': 'current-skills',
                'section': 'skills-assessment',
                'value': json.dumps({
                    "leadership": {"current": 4, "importance": 5, "willingness": 5},
                    "sales-marketing": {"current": 3, "importance": 5, "willingness": 4},
                    "financial-management": {"current": 3, "importance": 4, "willingness": 4},
                    "product-development": {"current": 5, "importance": 5, "willingness": 5},
                    "operations": {"current": 3, "importance": 4, "willingness": 4},
                    "strategic-thinking": {"current": 4, "importance": 5, "willingness": 5},
                    "communication": {"current": 4, "importance": 5, "willingness": 4},
                    "problem-solving": {"current": 5, "importance": 5, "willingness": 5}
                }),
                'type': 'matrix'
            },
            # Problem Identification section
            {
                'id': 'problem-experiences',
                'section': 'problem-identification',
                'value': '1. Students struggle with one-size-fits-all education that doesn\'t adapt to individual learning styles, leading to frustration and poor outcomes.\n\n2. Teachers spend 60%+ of their time on administrative tasks (grading, attendance, reporting) instead of actually teaching and mentoring students.\n\n3. Parents have no real-time visibility into their child\'s learning progress beyond quarterly report cards, making it hard to provide timely support.',
                'type': 'textarea'
            },
            {
                'id': 'problem-observation',
                'section': 'problem-identification',
                'value': 'I frequently observe educators burning out from overwhelming paperwork and repetitive tasks. Students are disengaged because standardized curricula don\'t match their interests or pace. Schools adopt multiple EdTech tools that don\'t integrate, creating data silos and adding complexity. Remote learning during COVID exposed how traditional teaching methods fail many learners. Learning gaps are widening, especially for students who need different approaches.',
                'type': 'textarea'
            },
            # Market Promise section
            {
                'id': 'value-proposition',
                'section': 'market-promise',
                'value': 'An AI-powered adaptive learning platform that personalizes education for each student while reducing teacher workload by 50%. We combine real-time progress tracking, automated assessment, intelligent content recommendations, and seamless integration with existing school systems - all in one intuitive platform. Unlike fragmented tools, we provide a complete ecosystem that benefits students, teachers, and parents simultaneously.',
                'type': 'textarea'
            },
            {
                'id': 'target-customer',
                'section': 'market-promise',
                'value': 'Progressive K-12 schools with 500-2,000 students, tech-forward administrators who value innovation, and annual budgets of $50K-$200K for educational technology. Primary focus: private schools in urban/suburban areas and charter schools seeking competitive differentiation. Early adopters will be schools frustrated with current LMS limitations and willing to pilot new solutions with 1-2 grades before full rollout.',
                'type': 'textarea'
            },
            # Opportunity Scoring section
            {
                'id': 'opportunity-criteria',
                'section': 'opportunity-scoring',
                'value': '9',
                'type': 'scale'
            }
        ]
        
        # Create Self Discovery Assessment
        self_discovery_assessment = Assessment(
            user_id=user_id,
            phase_id='self_discovery',
            phase_name='Self Discovery Assessment',
            progress_percentage=100.0,
            is_completed=True,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc)
        )
        db.session.add(self_discovery_assessment)
        db.session.flush()
        
        # Add Self Discovery responses
        for resp_data in self_discovery_responses:
            response = AssessmentResponse(
                assessment_id=self_discovery_assessment.id,
                question_id=resp_data['id'],
                section_id=resp_data['section'],
                response_value=str(resp_data['value']),
                response_type=resp_data['type'],
                question_text=f"Question: {resp_data['id']}"
            )
            db.session.add(response)
        
        # Create Idea Discovery Assessment
        idea_discovery_assessment = Assessment(
            user_id=user_id,
            phase_id='idea_discovery',
            phase_name='Idea Discovery Assessment',
            progress_percentage=100.0,
            is_completed=True,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc)
        )
        db.session.add(idea_discovery_assessment)
        db.session.flush()
        
        # Add Idea Discovery responses
        for resp_data in idea_discovery_responses:
            response = AssessmentResponse(
                assessment_id=idea_discovery_assessment.id,
                question_id=resp_data['id'],
                section_id=resp_data['section'],
                response_value=str(resp_data['value']),
                response_type=resp_data['type'],
                question_text=f"Question: {resp_data['id']}"
            )
            db.session.add(response)
        
        db.session.commit()
        
        print("\n" + "-" * 80)
        print("📊 ASSESSMENTS CREATED:")
        print("-" * 80)
        print(f"   ✓ Self Discovery Assessment    - 7 questions across 5 sections - 100%")
        print(f"   ✓ Idea Discovery Assessment    - 8 questions across 5 sections - 100%")
        print("-" * 80)
        
        print("\n" + "="*80)
        print("🔐 LOGIN CREDENTIALS")
        print("="*80)
        print(f"Email:    {email}")
        print(f"Password: {password}")
        print("="*80)
        
        print("\n✨ ALL QUESTION TYPES INCLUDED:")
        print("   • Multiple Choice (primary-motivation)")
        print("   • Textarea (success-vision, ten-year-vision, problem-experiences, etc.)")
        print("   • Scale/Slider (risk-tolerance, vision-confidence, opportunity-criteria)")
        print("   • Multiple Scale (life-satisfaction with 8 areas)")
        print("   • Ranking (top-values, cause-alignment)")
        print("   • Matrix (passion-work-matrix: 5x3, current-skills: 8x3)")
        
        print("\n🎯 TOTAL RESPONSES: 15 (7 + 8)")
        print("   All responses use correct question IDs matching frontend components!")
        print("   Login and verify all form fields display saved data.\n")
        
        return email, password


if __name__ == '__main__':
    create_complete_test_user()
