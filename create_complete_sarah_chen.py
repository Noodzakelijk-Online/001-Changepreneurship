#!/usr/bin/env python3
"""Create sarah_chen_founder test user with 100% COMPLETE assessment data."""
import sys
import os
sys.path.insert(0, '/app')

from src.main import app, db
from src.models.assessment import User, Assessment, AssessmentResponse, EntrepreneurProfile, UserSession
from werkzeug.security import generate_password_hash
from datetime import datetime

with app.app_context():
    print("🔍 Checking for existing user...")
    
    # Delete existing user completely
    existing = User.query.filter_by(username='sarah_chen_founder').first()
    if existing:
        print(f"   Found existing user ID: {existing.id}")
        # Delete all related data (explicit order to avoid FK constraints)
        UserSession.query.filter_by(user_id=existing.id).delete()
        assessments = Assessment.query.filter_by(user_id=existing.id).all()
        for assessment in assessments:
            AssessmentResponse.query.filter_by(assessment_id=assessment.id).delete()
            db.session.delete(assessment)
        EntrepreneurProfile.query.filter_by(user_id=existing.id).delete()
        db.session.delete(existing)
        db.session.commit()
        print("   ✓ Deleted existing user and all data")
    
    print("\n👤 Creating new user...")
    # Create user
    user = User(
        username='sarah_chen_founder',
        email='sarah.chen@techstartup.com',
        password_hash=generate_password_hash('Test1234!')
    )
    db.session.add(user)
    db.session.commit()
    print(f"   ✓ User created (ID: {user.id})")
    
    # Profile will be auto-created via assessments
    
    total_responses = 0
    
    # ============================================================================
    # 1. SELF DISCOVERY ASSESSMENT (100% complete)
    # ============================================================================
    print("\n📝 Creating Self Discovery Assessment...")
    self_disc = Assessment(
        user_id=user.id,
        phase_id='self_discovery',
        phase_name='Self Discovery Assessment',
        is_completed=True,
        progress_percentage=100,
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    db.session.add(self_disc)
    db.session.commit()
    
    self_disc_responses = [
        # Motivation section
        ('core_motivation', 'SD_Q001', 'What is your primary motivation for starting a business?', 'multiple_choice', 'financial_independence'),
        ('core_motivation', 'SD_Q002', 'How important is work-life balance to you?', 'scale', '8'),
        ('core_motivation', 'SD_Q003', 'What drives your daily actions?', 'text', 'Creating innovative AI solutions that automate repetitive tasks and empower people to focus on creative work'),
        
        # Vision section
        ('vision', 'SD_Q004', 'Where do you see yourself in 10 years?', 'text', 'Leading a successful AI company with 500+ employees, revolutionizing how businesses operate with autonomous agents'),
        ('vision', 'SD_Q005', 'What does success look like to you?', 'text', 'Building a billion-dollar company that genuinely improves productivity and creates meaningful employment'),
        ('vision', 'SD_Q006', 'How confident are you in achieving your vision?', 'scale', '9'),
        
        # Risk tolerance
        ('risk_tolerance', 'SD_Q007', 'How comfortable are you with financial uncertainty?', 'scale', '7'),
        ('risk_tolerance', 'SD_Q008', 'Would you invest your savings into your startup?', 'multiple_choice', 'yes_significant_portion'),
        ('risk_tolerance', 'SD_Q009', 'How do you handle failure?', 'text', 'I view failure as a learning opportunity and quickly pivot to new approaches'),
        
        # Values and strengths
        ('values', 'SD_Q010', 'What are your top 3 values?', 'multiple_choice', '["innovation", "integrity", "impact"]'),
        ('strengths', 'SD_Q011', 'What are your greatest strengths?', 'text', 'Technical expertise in AI/ML, strategic thinking, team leadership, and rapid execution'),
        ('strengths', 'SD_Q012', 'What skills do you need to develop?', 'text', 'Financial management, sales negotiation, and scaling operations'),
    ]
    
    for section, qid, qtext, rtype, val in self_disc_responses:
        resp = AssessmentResponse(
            assessment_id=self_disc.id,
            section_id=section,
            question_id=qid,
            question_text=qtext,
            response_type=rtype,
            response_value=val
        )
        db.session.add(resp)
        total_responses += 1
    
    db.session.commit()
    print(f"   ✓ Added {len(self_disc_responses)} responses")
    
    # ============================================================================
    # 2. IDEA DISCOVERY ASSESSMENT (100% complete)
    # ============================================================================
    print("\n📝 Creating Idea Discovery Assessment...")
    idea_disc = Assessment(
        user_id=user.id,
        phase_id='idea_discovery',
        phase_name='Idea Discovery Assessment',
        is_completed=True,
        progress_percentage=100,
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    db.session.add(idea_disc)
    db.session.commit()
    
    idea_disc_responses = [
        # Problem identification
        ('problem', 'ID_Q001', 'What problem are you solving?', 'text', 'Businesses waste 40% of employee time on repetitive tasks like data entry, scheduling, and basic customer support'),
        ('problem', 'ID_Q002', 'Who experiences this problem?', 'text', 'SMBs and enterprise teams in operations, customer service, and administration'),
        ('problem', 'ID_Q003', 'How painful is this problem (1-10)?', 'scale', '9'),
        ('problem', 'ID_Q004', 'How are people solving it today?', 'text', 'Manual work, basic automation scripts, expensive enterprise RPA solutions, or offshore teams'),
        
        # Solution vision
        ('solution', 'ID_Q005', 'What is your solution?', 'text', 'AI-powered autonomous agents that learn company workflows and automate complex multi-step tasks'),
        ('solution', 'ID_Q006', 'What makes your solution unique?', 'text', 'Natural language training, cross-platform integration, and continuous learning from user feedback'),
        ('solution', 'ID_Q007', 'Why now? Why is timing right?', 'text', 'LLM breakthroughs, API economy maturity, and remote work increasing demand for automation'),
        
        # Market opportunity
        ('market', 'ID_Q008', 'How big is your target market?', 'text', '$50B automation market growing 25% annually, targeting 10M SMBs initially'),
        ('market', 'ID_Q009', 'Who are your first customers?', 'text', 'Digital marketing agencies, SaaS companies, and e-commerce businesses with 10-500 employees'),
        ('market', 'ID_Q010', 'What would they pay?', 'text', '$200-2000/month per agent depending on complexity and ROI'),
        
        # Validation
        ('validation', 'ID_Q011', 'Have you talked to potential customers?', 'multiple_choice', 'yes_extensive'),
        ('validation', 'ID_Q012', 'What feedback did you receive?', 'text', '15 companies expressed interest, 3 agreed to pilot, main concern is integration complexity'),
        ('validation', 'ID_Q013', 'Do you have any early traction?', 'text', '2 paying beta customers, $5K MRR, 30% month-over-month growth'),
    ]
    
    for section, qid, qtext, rtype, val in idea_disc_responses:
        resp = AssessmentResponse(
            assessment_id=idea_disc.id,
            section_id=section,
            question_id=qid,
            question_text=qtext,
            response_type=rtype,
            response_value=val
        )
        db.session.add(resp)
        total_responses += 1
    
    db.session.commit()
    print(f"   ✓ Added {len(idea_disc_responses)} responses")
    
    # ============================================================================
    # 3. MARKET RESEARCH (100% complete)
    # ============================================================================
    print("\n📝 Creating Market Research Assessment...")
    market_research = Assessment(
        user_id=user.id,
        phase_id='market_research',
        phase_name='Market Research',
        is_completed=True,
        progress_percentage=100,
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    db.session.add(market_research)
    db.session.commit()
    
    market_research_responses = [
        ('market_size', 'MR_Q001', 'What is your Total Addressable Market (TAM)?', 'text', '$50B global business automation market'),
        ('market_size', 'MR_Q002', 'What is your Serviceable Addressable Market (SAM)?', 'text', '$8B AI-powered automation for SMBs in US/EU'),
        ('market_size', 'MR_Q003', 'What is your Serviceable Obtainable Market (SOM)?', 'text', '$200M targeting marketing agencies and SaaS companies in year 1-3'),
        
        ('competition', 'MR_Q004', 'Who are your top 3 competitors?', 'text', 'Zapier (workflow automation), UiPath (RPA), Make.com (integration platform)'),
        ('competition', 'MR_Q005', 'What is your competitive advantage?', 'text', 'Natural language interface, lower technical barriers, AI learning vs fixed workflows'),
        ('competition', 'MR_Q006', 'How do you differentiate?', 'text', 'No-code AI training, autonomous decision-making, and continuous improvement'),
        
        ('customer_segments', 'MR_Q007', 'Who is your ideal customer?', 'text', 'Digital agencies with 20-100 employees spending 30+ hours/week on repetitive client tasks'),
        ('customer_segments', 'MR_Q008', 'What are their key pain points?', 'text', 'High labor costs, talent shortage, scalability challenges, human error in routine tasks'),
        ('customer_segments', 'MR_Q009', 'How do they make buying decisions?', 'text', 'ROI-driven, 30-day trials, operations manager champions, C-suite approval for $10K+ ARR'),
    ]
    
    for section, qid, qtext, rtype, val in market_research_responses:
        resp = AssessmentResponse(
            assessment_id=market_research.id,
            section_id=section,
            question_id=qid,
            question_text=qtext,
            response_type=rtype,
            response_value=val
        )
        db.session.add(resp)
        total_responses += 1
    
    db.session.commit()
    print(f"   ✓ Added {len(market_research_responses)} responses")
    
    # ============================================================================
    # 4. PRODUCT CONCEPT TESTING (100% complete)
    # ============================================================================
    print("\n📝 Creating Product Concept Testing Assessment...")
    product_concept = Assessment(
        user_id=user.id,
        phase_id='product_concept_testing',
        phase_name='Product Concept Testing',
        is_completed=True,
        progress_percentage=100,
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    db.session.add(product_concept)
    db.session.commit()
    
    product_concept_responses = [
        ('concept', 'PC_Q001', 'Describe your product concept', 'text', 'AI Agent Platform: Users describe tasks in plain English, agents learn workflows by observation, execute autonomously with 95%+ accuracy'),
        ('concept', 'PC_Q002', 'What is your Minimum Viable Product (MVP)?', 'text', 'Single-agent system for email management and CRM data entry with Zapier/Slack integration'),
        ('concept', 'PC_Q003', 'What features are must-haves?', 'text', 'Natural language training, error detection, audit logs, rollback capability, API integrations'),
        
        ('testing', 'PC_Q004', 'Have you tested your concept?', 'multiple_choice', 'yes_with_prototype'),
        ('testing', 'PC_Q005', 'What was the feedback?', 'text', '8/10 testers understood value immediately, 6/10 completed setup in under 30 minutes, main request: more integrations'),
        ('testing', 'PC_Q006', 'Would customers pay for this?', 'text', 'Yes - 12 of 15 prospects agreed to $299/month for 2 agents after demo'),
        
        ('positioning', 'PC_Q007', 'How do you position your product?', 'text', 'The AI teammate that learns your workflow - no coding, no complex rules, just tell it what to do'),
        ('positioning', 'PC_Q008', 'What is your pricing strategy?', 'text', 'Per-agent subscription: $199 starter, $499 professional, $999 enterprise with custom integrations'),
    ]
    
    for section, qid, qtext, rtype, val in product_concept_responses:
        resp = AssessmentResponse(
            assessment_id=product_concept.id,
            section_id=section,
            question_id=qid,
            question_text=qtext,
            response_type=rtype,
            response_value=val
        )
        db.session.add(resp)
        total_responses += 1
    
    db.session.commit()
    print(f"   ✓ Added {len(product_concept_responses)} responses")
    
    # ============================================================================
    # 5. BUSINESS PILLARS PLANNING (100% complete)
    # ============================================================================
    print("\n📝 Creating Business Pillars Planning Assessment...")
    business_pillars = Assessment(
        user_id=user.id,
        phase_id='business_pillars',
        phase_name='Business Pillars Planning',
        is_completed=True,
        progress_percentage=100,
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    db.session.add(business_pillars)
    db.session.commit()
    
    business_pillars_responses = [
        # Business model
        ('business_model', 'BP_Q001', 'What is your business model?', 'text', 'SaaS subscription with per-agent pricing, implementation services, and premium support tiers'),
        ('business_model', 'BP_Q002', 'What are your revenue streams?', 'text', 'Monthly subscriptions (80%), annual contracts (15%), professional services (5%)'),
        ('business_model', 'BP_Q003', 'What are your key metrics?', 'text', 'MRR, CAC, LTV, churn rate, agents per customer, automation success rate'),
        
        # Go-to-market
        ('gtm_strategy', 'BP_Q004', 'What is your go-to-market strategy?', 'text', 'Product-led growth: free tier → self-serve upgrade → sales for enterprise'),
        ('gtm_strategy', 'BP_Q005', 'What are your customer acquisition channels?', 'text', 'Content marketing, SEO, product hunt, partnerships with agency platforms, webinars'),
        ('gtm_strategy', 'BP_Q006', 'What is your sales process?', 'text', '14-day free trial → automated onboarding → usage-based upgrade prompts → sales call at $500/mo threshold'),
        
        # Operations
        ('operations', 'BP_Q007', 'What is your organizational structure?', 'text', 'Founder/CEO, CTO, 2 engineers, 1 product designer, 1 customer success, 1 sales - total 7 people'),
        ('operations', 'BP_Q008', 'What are your key partnerships?', 'text', 'OpenAI/Anthropic for LLMs, Zapier for integrations, AWS for infrastructure'),
        ('operations', 'BP_Q009', 'What are your resource needs?', 'text', '$1.5M seed round for 18-month runway: 60% engineering, 20% marketing, 20% operations'),
    ]
    
    for section, qid, qtext, rtype, val in business_pillars_responses:
        resp = AssessmentResponse(
            assessment_id=business_pillars.id,
            section_id=section,
            question_id=qid,
            question_text=qtext,
            response_type=rtype,
            response_value=val
        )
        db.session.add(resp)
        total_responses += 1
    
    db.session.commit()
    print(f"   ✓ Added {len(business_pillars_responses)} responses")
    
    # ============================================================================
    # 6. BUSINESS DEVELOPMENT (100% complete)
    # ============================================================================
    print("\n📝 Creating Business Development Assessment...")
    business_dev = Assessment(
        user_id=user.id,
        phase_id='business_development',
        phase_name='Business Development',
        is_completed=True,
        progress_percentage=100,
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    db.session.add(business_dev)
    db.session.commit()
    
    business_dev_responses = [
        ('roadmap', 'BD_Q001', 'What is your 12-month roadmap?', 'text', 'Q1: Launch beta, 50 users. Q2: Public launch, 500 users. Q3: Enterprise features. Q4: Series A raise at $10M ARR'),
        ('roadmap', 'BD_Q002', 'What are your key milestones?', 'text', '$10K MRR (Month 3), $50K MRR (Month 6), $100K MRR (Month 9), 1000 active agents (Month 12)'),
        ('roadmap', 'BD_Q003', 'What are your success metrics?', 'text', '40% MoM growth, <5% monthly churn, >$2K LTV/CAC ratio, 70% automation success rate'),
        
        ('funding', 'BD_Q004', 'What is your funding strategy?', 'text', 'Bootstrap to $10K MRR, raise $1.5M seed at $8M valuation, Series A at $30M valuation'),
        ('funding', 'BD_Q005', 'How will you use funding?', 'text', '60% product development (4 engineers), 25% sales/marketing (2 people + campaigns), 15% operations'),
        
        ('scaling', 'BD_Q006', 'How will you scale?', 'text', 'Hire 1 engineer per $50K MRR, expand integrations from 10 to 100, build reseller channel'),
        ('scaling', 'BD_Q007', 'What are your biggest risks?', 'text', 'LLM cost increases, competitor with more funding, low adoption due to change management resistance'),
    ]
    
    for section, qid, qtext, rtype, val in business_dev_responses:
        resp = AssessmentResponse(
            assessment_id=business_dev.id,
            section_id=section,
            question_id=qid,
            question_text=qtext,
            response_type=rtype,
            response_value=val
        )
        db.session.add(resp)
        total_responses += 1
    
    db.session.commit()
    print(f"   ✓ Added {len(business_dev_responses)} responses")
    
    # ============================================================================
    # 7. BUSINESS PROTOTYPE TESTING (100% complete)
    # ============================================================================
    print("\n📝 Creating Business Prototype Testing Assessment...")
    prototype_test = Assessment(
        user_id=user.id,
        phase_id='business_prototype_testing',
        phase_name='Business Prototype Testing',
        is_completed=True,
        progress_percentage=100,
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    db.session.add(prototype_test)
    db.session.commit()
    
    prototype_test_responses = [
        ('prototype', 'BPT_Q001', 'What is your current prototype stage?', 'text', 'Working beta with 25 active users, 3 paying customers, processing 500+ tasks/day'),
        ('prototype', 'BPT_Q002', 'What features have you tested?', 'text', 'Email triage, CRM updates, data extraction, scheduling, Slack notifications, basic analytics'),
        ('prototype', 'BPT_Q003', 'What were the results?', 'text', '92% task completion rate, 4.2/5 user satisfaction, avg 15 hours saved per user per week'),
        
        ('iteration', 'BPT_Q004', 'What changes did you make based on feedback?', 'text', 'Added audit logs, improved error messages, built rollback feature, simplified initial setup from 2 hours to 20 min'),
        ('iteration', 'BPT_Q005', 'What did you learn?', 'text', 'Users need hand-holding for first agent, prefer templates over blank slate, require proof of accuracy before trusting'),
        
        ('validation', 'BPT_Q006', 'Would users recommend your product?', 'text', 'NPS score: 65 (18 promoters, 4 passives, 3 detractors out of 25 users)'),
        ('validation', 'BPT_Q007', 'What is your retention rate?', 'text', '88% Week 1 → Week 4 retention, 100% of paying customers renewed first month'),
    ]
    
    for section, qid, qtext, rtype, val in prototype_test_responses:
        resp = AssessmentResponse(
            assessment_id=prototype_test.id,
            section_id=section,
            question_id=qid,
            question_text=qtext,
            response_type=rtype,
            response_value=val
        )
        db.session.add(resp)
        total_responses += 1
    
    db.session.commit()
    print(f"   ✓ Added {len(prototype_test_responses)} responses")
    
    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    db.session.commit()
    
    print("\n" + "="*60)
    print("✅ 100% COMPLETE USER CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"\n👤 User Details:")
    print(f"   Username: sarah_chen_founder")
    print(f"   Password: Test1234!")
    print(f"   Email: sarah.chen@techstartup.com")
    print(f"   User ID: {user.id}")
    
    print(f"\n📊 Assessment Summary:")
    assessments = Assessment.query.filter_by(user_id=user.id).all()
    for assessment in assessments:
        response_count = AssessmentResponse.query.filter_by(assessment_id=assessment.id).count()
        print(f"   ✓ {assessment.phase_name}: {response_count} responses ({assessment.progress_percentage}% complete)")
    
    print(f"\n📈 Total Statistics:")
    print(f"   Total Assessments: {len(assessments)}")
    print(f"   Total Responses: {total_responses}")
    print(f"   Completion Rate: 100%")
    
    print(f"\n🎯 Ready for FULL AI Analysis!")
    print(f"   All 7 assessment phases completed")
    print(f"   Realistic startup scenario (AI agent platform)")
    print(f"   Comprehensive business data for Groq AI insights\n")
