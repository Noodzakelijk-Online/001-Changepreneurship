#!/usr/bin/env python3
"""
Create a complete test user with all 7 assessment phases fully completed.
"""
import sys
import os
from datetime import datetime
import requests
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import app
from src.models.assessment import db, Assessment, AssessmentResponse, User
from werkzeug.security import generate_password_hash

def create_complete_user():
    """Create test user with all 7 phases completed"""
    # User credentials
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    email = f"complete_{timestamp}@test.com"
    password = "Test123!"
    username = f"complete_{timestamp}"
    
    print("\n" + "="*70)
    print("🚀 CREATING COMPLETE TEST USER")
    print("="*70)
    
    # Create user directly in database
    with app.app_context():
        print("\n📝 Creating user in database...")
        
        user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        user_id = user.id
        
        print(f"\n✅ User Created:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Username: {username}")
        print(f"   User ID: {user_id}")
        
        # All 7 phases with their questions
        phases_data = {
            'self_discovery': {
                'name': 'Self Discovery',
                'questions': [
                    {'id': 'primary-motivation', 'section': 'motivation', 'value': 'Building lasting impact and creating meaningful change', 'type': 'text'},
                    {'id': 'success-vision', 'section': 'motivation', 'value': 'Leading a sustainable business that transforms industries', 'type': 'text'},
                    {'id': 'risk-tolerance', 'section': 'motivation', 'value': '8', 'type': 'scale'},
                    {'id': 'life-satisfaction', 'section': 'life-impact', 'value': '9', 'type': 'scale'},
                    {'id': 'work-life-balance', 'section': 'life-impact', 'value': 'Highly important - want to maintain balance', 'type': 'text'},
                    {'id': 'top-values', 'section': 'values', 'value': 'Integrity,Innovation,Impact,Excellence', 'type': 'multi-select'},
                    {'id': 'core-beliefs', 'section': 'values', 'value': 'Creating value for society while achieving personal growth', 'type': 'text'},
                    {'id': 'ten-year-vision', 'section': 'vision', 'value': 'Leading a global tech company with positive social impact', 'type': 'text'},
                    {'id': 'vision-confidence', 'section': 'confidence', 'value': '9', 'type': 'scale'},
                    {'id': 'entrepreneurial-drive', 'section': 'motivation', 'value': 'autonomy', 'type': 'multiple-choice'},
                    {'id': 'failure-perspective', 'section': 'motivation', 'value': 'learning', 'type': 'multiple-choice'},
                    {'id': 'family-support', 'section': 'life-impact', 'value': '8', 'type': 'scale'},
                    {'id': 'time-commitment', 'section': 'life-impact', 'value': '40-60', 'type': 'multiple-choice'},
                    {'id': 'stress-management', 'section': 'life-impact', 'value': 'manage-well', 'type': 'multiple-choice'},
                    {'id': 'decision-making-style', 'section': 'values', 'value': 'data-driven', 'type': 'multiple-choice'},
                ]
            },
            'idea_discovery': {
                'name': 'Idea Discovery',
                'questions': [
                    {'id': 'problem-statement', 'section': 'problem', 'value': 'Small businesses struggle with digital transformation due to complexity and cost', 'type': 'text'},
                    {'id': 'target-customer', 'section': 'problem', 'value': 'SMBs with 10-100 employees in traditional industries', 'type': 'text'},
                    {'id': 'solution-overview', 'section': 'solution', 'value': 'AI-powered platform that simplifies digital tools into one intuitive system', 'type': 'text'},
                    {'id': 'unique-value', 'section': 'solution', 'value': 'No-code setup, AI guidance, affordable pricing, integrated ecosystem', 'type': 'text'},
                    {'id': 'competitive-advantage', 'section': 'differentiation', 'value': 'AI-driven personalization and seamless integration across all business functions', 'type': 'text'},
                    {'id': 'innovation-level', 'section': 'differentiation', 'value': '8', 'type': 'scale'},
                    {'id': 'problem-experience', 'section': 'problem', 'value': 'Worked in SMB for 5 years, saw the struggles daily', 'type': 'textarea'},
                    {'id': 'problem-frequency', 'section': 'problem', 'value': 'Daily - businesses lose customers due to complexity', 'type': 'text'},
                    {'id': 'customer-pain-points', 'section': 'problem', 'value': 'Manual processes, expensive tools, steep learning curves, poor support', 'type': 'textarea'},
                    {'id': 'key-features', 'section': 'solution', 'value': 'AI automation, mobile-first, one-click integrations, predictive analytics', 'type': 'text'},
                ]
            },
            'market_research': {
                'name': 'Market Research',
                'questions': [
                    {'id': 'market-size', 'section': 'market', 'value': 'TAM: $50B, SAM: $15B, SOM: $500M', 'type': 'text'},
                    {'id': 'growth-rate', 'section': 'market', 'value': '15-20% annually in SMB digital transformation segment', 'type': 'text'},
                    {'id': 'customer-segments', 'section': 'customers', 'value': 'Retail, Healthcare, Professional Services, Manufacturing SMBs', 'type': 'text'},
                    {'id': 'pain-points', 'section': 'customers', 'value': 'Tech overwhelm, budget constraints, integration challenges, training needs', 'type': 'text'},
                    {'id': 'competitors', 'section': 'competition', 'value': 'Salesforce (too complex), Zoho (limited AI), monday.com (no industry focus)', 'type': 'text'},
                    {'id': 'competitive-gaps', 'section': 'competition', 'value': 'No competitor offers AI-guided simplicity with deep industry customization', 'type': 'text'},
                    {'id': 'market-growth', 'section': 'market', 'value': '14% CAGR in SMB CRM, 28% in AI-CRM subsegment', 'type': 'text'},
                    {'id': 'barriers-to-entry', 'section': 'market', 'value': 'Technology complexity (moderate), customer trust (high), integration requirements', 'type': 'textarea'},
                    {'id': 'distribution-channels', 'section': 'strategy', 'value': 'Direct website sales, app marketplaces, partnership channel, reseller network', 'type': 'text'},
                ]
            },
            'business_pillars': {
                'name': 'Business Pillars',
                'questions': [
                    {'id': 'business-model', 'section': 'model', 'value': 'SaaS with tiered pricing + professional services revenue', 'type': 'text'},
                    {'id': 'revenue-streams', 'section': 'model', 'value': 'Subscriptions (70%), Implementation (20%), Training (10%)', 'type': 'text'},
                    {'id': 'pricing-strategy', 'section': 'model', 'value': '$99-$499/month based on users and features, annual discounts', 'type': 'text'},
                    {'id': 'key-resources', 'section': 'operations', 'value': 'AI/ML engineers, industry specialists, customer success team, cloud infrastructure', 'type': 'text'},
                    {'id': 'key-partnerships', 'section': 'operations', 'value': 'Cloud providers (AWS/Azure), Industry associations, Implementation partners', 'type': 'text'},
                    {'id': 'cost-structure', 'section': 'operations', 'value': 'R&D (40%), Sales/Marketing (30%), Cloud costs (15%), Operations (15%)', 'type': 'text'},
                    {'id': 'operational-processes', 'section': 'operations', 'value': 'Agile 2-week sprints, weekly customer calls, monthly OKRs, daily standups', 'type': 'textarea'},
                    {'id': 'scalability-plan', 'section': 'operations', 'value': 'Cloud auto-scaling, self-service onboarding, knowledge base, automated support', 'type': 'text'},
                    {'id': 'legal-structure', 'section': 'legal', 'value': 'Delaware C-Corp, 60/40 founder split with 4-year vesting, 10% option pool', 'type': 'text'},
                    {'id': 'ip-protection', 'section': 'legal', 'value': 'Trademark registered, patent pending for AI algorithms, GDPR + SOC2 compliance', 'type': 'textarea'},
                ]
            },
            'product_concept_testing': {
                'name': 'Product Concept Testing',
                'questions': [
                    {'id': 'mvp-features', 'section': 'product', 'value': 'CRM, Project Management, AI Assistant, Basic Analytics, Mobile App', 'type': 'text'},
                    {'id': 'development-timeline', 'section': 'product', 'value': '6 months to beta, 9 months to v1.0 launch', 'type': 'text'},
                    {'id': 'testing-approach', 'section': 'validation', 'value': 'Beta with 50 SMBs, iterative feedback, A/B testing key features', 'type': 'text'},
                    {'id': 'success-metrics', 'section': 'validation', 'value': 'NPS >50, Daily active usage >60%, Feature adoption >70%, Churn <5%', 'type': 'text'},
                    {'id': 'iteration-plan', 'section': 'validation', 'value': '2-week sprints with customer feedback loops and monthly feature releases', 'type': 'text'},
                    {'id': 'pain-point-validation', 'section': 'validation', 'value': 'Users confirmed: manual data entry biggest pain (92%), missed follow-ups (78%), lack of insights (65%)', 'type': 'textarea'},
                    {'id': 'willingness-to-pay', 'section': 'validation', 'value': '73% would pay $50-100/mo/user, 12 out of 15 committed to beta', 'type': 'text'},
                    {'id': 'feature-prioritization', 'section': 'validation', 'value': 'P0: Email sync, contacts; P1: AI suggestions, pipeline; P2: Reporting, mobile', 'type': 'text'},
                ]
            },
            'business_development': {
                'name': 'Business Development',
                'questions': [
                    {'id': 'team-structure', 'section': 'team', 'value': 'CEO, CTO, VP Product, VP Sales, 15 engineers, 8 sales/CS', 'type': 'text'},
                    {'id': 'hiring-plan', 'section': 'team', 'value': 'Q1-Q2: 5 engineers, 3 sales. Q3-Q4: 3 engineers, 2 CS, 1 marketing', 'type': 'text'},
                    {'id': 'funding-needed', 'section': 'funding', 'value': '$2.5M seed round for 18-month runway', 'type': 'text'},
                    {'id': 'use-of-funds', 'section': 'funding', 'value': 'Product dev (50%), Sales/Marketing (30%), Operations (20%)', 'type': 'text'},
                    {'id': 'milestone-timeline', 'section': 'milestones', 'value': 'M3: Beta launch, M6: 100 customers, M12: $500K ARR, M18: Break-even', 'type': 'text'},
                    {'id': 'skill-gaps', 'section': 'team', 'value': 'Need: Enterprise sales leader, AI/ML specialist, DevOps engineer, CS manager', 'type': 'text'},
                    {'id': 'customer-retention', 'section': 'execution', 'value': 'Onboarding program, quarterly reviews, dedicated CSM for 10+ users, community forum', 'type': 'textarea'},
                    {'id': 'risk-mitigation', 'section': 'execution', 'value': 'Technical: Modular architecture; Market: Early validation; Financial: Lean ops, milestone-based hiring', 'type': 'textarea'},
                ]
            },
            'business_prototype_testing': {
                'name': 'Business Prototype Testing',
                'questions': [
                    {'id': 'pilot-program', 'section': 'testing', 'value': 'Pilot with 10 paying customers over 3 months to validate product-market fit', 'type': 'text'},
                    {'id': 'success-criteria', 'section': 'testing', 'value': 'Customer satisfaction >8/10, usage frequency >3x/week, feature adoption >60%, referral rate >20%, churn <10%', 'type': 'text'},
                    {'id': 'pilot-timeline', 'section': 'testing', 'value': '3 months from MVP launch, with 2-week iteration cycles', 'type': 'text'},
                    {'id': 'feedback-collection', 'section': 'testing', 'value': 'Weekly check-ins, bi-weekly surveys, end-of-pilot interviews, usage analytics dashboard', 'type': 'text'},
                    {'id': 'pilot-learnings', 'section': 'testing', 'value': 'Onboarding takes 2-3 weeks (expected 1 week), email integration most valuable feature, mobile app critical for field teams', 'type': 'textarea'},
                    {'id': 'scale-readiness', 'section': 'testing', 'value': 'Infrastructure can handle 100x growth, support processes documented, sales playbook validated, pricing confirmed', 'type': 'text'},
                    {'id': 'beta-conversion-rate', 'section': 'testing', 'value': '80% of beta users converted to paying customers after 3-month trial', 'type': 'text'},
                    {'id': 'product-market-fit-score', 'section': 'testing', 'value': 'PMF survey: 78% would be very disappointed without product (>40% threshold)', 'type': 'text'},
                ]
            }
        }
        
        print(f"\n📊 Creating Assessments for 7 Phases:")
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
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            db.session.add(assessment)
            db.session.flush()
            
            # Add all responses
            response_count = 0
            for q in phase_data['questions']:
                response = AssessmentResponse(
                    assessment_id=assessment.id,
                    question_id=q['id'],
                    section_id=q['section'],
                    response_value=str(q['value']),
                    response_type=q['type'],
                    question_text=f"Question: {q['id']}"
                )
                db.session.add(response)
                response_count += 1
            
            total_responses += response_count
            print(f"   ✓ {phase_data['name']:25s} - {response_count:2d} responses - 100% complete")
        
        db.session.commit()
        
        print("-" * 70)
        print(f"\n✅ COMPLETE! Created {len(phases_data)} assessments with {total_responses} responses")
        
        print("\n" + "="*70)
        print("🎯 LOGIN CREDENTIALS")
        print("="*70)
        print(f"Email:    {email}")
        print(f"Password: {password}")
        print("="*70)
        
        print("\n📈 Assessment Status:")
        print(f"   Total Phases: 7/7 (100%)")
        print(f"   All phases marked as completed ✓")
        print(f"   Total responses: {total_responses}")
        
        return email, password

if __name__ == '__main__':
    create_complete_user()
