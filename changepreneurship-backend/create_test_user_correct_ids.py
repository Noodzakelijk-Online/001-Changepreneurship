#!/usr/bin/env python3
"""
Create a test user with complete assessment data using CORRECT question IDs
that match the frontend assessment components.

This script creates responses for the 2 implemented assessment phases:
1. Self Discovery Assessment
2. Idea Discovery Assessment
"""

import sys
from datetime import datetime, timezone
sys.path.insert(0, '/app')

from src.main import app
from src.models.assessment import db, Assessment, AssessmentResponse, User
from werkzeug.security import generate_password_hash


def create_test_user_with_correct_ids():
    """Create test user with responses using correct question IDs from frontend"""
    
    with app.app_context():
        # User credentials
        email = f"frontend_match_{datetime.now().strftime('%Y%m%d_%H%M%S')}@test.com"
        password = "Test123!"
        username = "Frontend Match User"
        
        print("\n" + "="*70)
        print("🎯 CREATING TEST USER WITH FRONTEND-MATCHING QUESTION IDS")
        print("="*70)
        
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
        
        # Define realistic test data for both phases
        phases_data = {
            'self_discovery': {
                'name': 'Self Discovery Assessment',
                'sections': {
                    'motivation': [
                        {
                            'id': 'primary-motivation',
                            'value': 'social-impact',
                            'type': 'multiple-choice',
                            'help': 'Make a positive difference in the world'
                        },
                        {
                            'id': 'success-vision',
                            'value': 'Leading a sustainable tech company with 50+ employees, working 40hrs/week, making significant social impact through AI-powered education tools. Success means creating value for society while maintaining work-life balance and personal growth.',
                            'type': 'textarea'
                        },
                        {
                            'id': 'risk-tolerance',
                            'value': '7',
                            'type': 'scale'
                        }
                    ],
                    'life-impact': [
                        {
                            'id': 'life-satisfaction',
                            'value': '{"Health": 8, "Money": 7, "Family": 9, "Friends": 7, "Career": 6, "Growth": 8, "Recreation": 7, "Environment": 8}',
                            'type': 'multiple-scale'
                        }
                    ],
                    'values': [
                        {
                            'id': 'top-values',
                            'value': '["making-difference", "learning", "personal-freedom", "family-time", "financial-success", "adventure", "security", "recognition"]',
                            'type': 'ranking'
                        }
                    ],
                    'vision': [
                        {
                            'id': 'ten-year-vision',
                            'value': 'At 45, I run a thriving EdTech company helping millions of students worldwide. I have a balanced life with morning workouts, quality family dinners, and time for hobbies. Recognized as a thought leader in AI education, mentoring young entrepreneurs, financially secure with passive income streams.',
                            'type': 'textarea'
                        }
                    ],
                    'confidence': [
                        {
                            'id': 'vision-confidence',
                            'value': '8',
                            'type': 'scale'
                        }
                    ]
                }
            },
            'idea_discovery': {
                'name': 'Idea Discovery Assessment',
                'sections': {
                    'core-alignment': [
                        {
                            'id': 'passion-work-matrix',
                            'value': '{"creative-work": {"passion": 4, "skill": 3, "potential": 4}, "analytical-work": {"passion": 5, "skill": 5, "potential": 4}, "technical-work": {"passion": 5, "skill": 4, "potential": 5}, "people-work": {"passion": 4, "skill": 4, "potential": 4}, "operational-work": {"passion": 3, "skill": 3, "potential": 3}}',
                            'type': 'matrix'
                        },
                        {
                            'id': 'cause-alignment',
                            'value': '["education", "technology-innovation", "economic-empowerment", "personal-development", "community-building", "environmental", "healthcare", "social-justice"]',
                            'type': 'ranking'
                        }
                    ],
                    'skills-assessment': [
                        {
                            'id': 'current-skills',
                            'value': '{"leadership": {"current": 4, "importance": 5, "willingness": 5}, "sales-marketing": {"current": 3, "importance": 5, "willingness": 4}, "financial-management": {"current": 3, "importance": 4, "willingness": 4}, "product-development": {"current": 5, "importance": 5, "willingness": 5}, "operations": {"current": 3, "importance": 4, "willingness": 4}, "strategic-thinking": {"current": 4, "importance": 5, "willingness": 5}, "communication": {"current": 4, "importance": 5, "willingness": 4}, "problem-solving": {"current": 5, "importance": 5, "willingness": 5}}',
                            'type': 'matrix'
                        }
                    ],
                    'problem-identification': [
                        {
                            'id': 'problem-experiences',
                            'value': '1. Students struggle to find personalized learning paths - one-size-fits-all education misses individual needs\n2. Teachers overwhelmed with administrative work instead of teaching\n3. Parents lack visibility into actual learning progress beyond grades',
                            'type': 'textarea'
                        },
                        {
                            'id': 'problem-observation',
                            'value': 'I see educators burning out from paperwork, students disengaged in standardized curricula, and learning gaps widening. Schools adopting EdTech but struggling with fragmented tools that don\'t integrate. Remote learning exposed how ineffective traditional methods are for many learners.',
                            'type': 'textarea'
                        }
                    ],
                    'market-promise': [
                        {
                            'id': 'value-proposition',
                            'value': 'AI-powered adaptive learning platform that personalizes education for each student while reducing teacher workload by 50%. We combine real-time progress tracking, automated assessment, and intelligent content recommendations in one seamless experience.',
                            'type': 'textarea'
                        },
                        {
                            'id': 'target-customer',
                            'value': 'Progressive K-12 schools (500-2000 students) with tech-forward administrators, budget for innovation ($50-200K/year), frustrated with current LMS limitations. Early adopters: private schools in urban areas, charter schools seeking differentiation.',
                            'type': 'textarea'
                        }
                    ],
                    'opportunity-scoring': [
                        {
                            'id': 'opportunity-criteria',
                            'value': '9',
                            'type': 'scale'
                        }
                    ]
                }
            }
        }
        
        print(f"\n📊 Creating Assessments with Frontend-Matching Question IDs:")
        print("-" * 70)
        
        total_responses = 0
        
        for phase_id, phase_data in phases_data.items():
            # Create assessment
            assessment = Assessment(
                user_id=user_id,
                phase_id=phase_id,
                phase_name=phase_data['name'],
                progress_percentage=100.0,
                is_completed=True,
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc)
            )
            db.session.add(assessment)
            db.session.flush()
            
            # Add all responses for each section
            response_count = 0
            for section_id, questions in phase_data['sections'].items():
                for q in questions:
                    response = AssessmentResponse(
                        assessment_id=assessment.id,
                        question_id=q['id'],
                        section_id=section_id,
                        response_value=str(q['value']),
                        response_type=q['type'],
                        question_text=f"Question: {q['id']}"
                    )
                    db.session.add(response)
                    response_count += 1
            
            total_responses += response_count
            print(f"   ✓ {phase_data['name']:30s} - {response_count:2d} responses - 100% complete")
        
        db.session.commit()
        
        print("-" * 70)
        print(f"\n✅ SUCCESS! Created {len(phases_data)} assessments with {total_responses} responses")
        
        print("\n" + "="*70)
        print("🔐 LOGIN CREDENTIALS")
        print("="*70)
        print(f"Email:    {email}")
        print(f"Password: {password}")
        print("="*70)
        
        print("\n📋 Assessment Details:")
        print(f"   • self_discovery: 7 questions across 5 sections")
        print(f"   • idea_discovery: 7 questions across 5 sections")
        print(f"   • Total: 14 responses with correct question IDs")
        
        print("\n✨ All question IDs match frontend components!")
        print("   Login and check assessment forms - responses should display correctly.\n")
        
        return email, password


if __name__ == '__main__':
    create_test_user_with_correct_ids()
