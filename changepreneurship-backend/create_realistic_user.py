"""
Generate a new realistic test user with complete assessment data.
Creates: Marcus Rodriguez - E-commerce Sustainability Platform Founder
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.assessment import db, User, Assessment, AssessmentResponse
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_marcus_rodriguez():
    """Create Marcus Rodriguez - Complete E-commerce founder profile"""
    
    with app.app_context():
        # Check if user exists
        existing = User.query.filter_by(username='marcus_rodriguez').first()
        if existing:
            print(f"User already exists: ID {existing.id}")
            return existing.id
        
        # Create user
        user = User(
            username='marcus_rodriguez',
            email='marcus.rodriguez@greenloop.co',
            password_hash=generate_password_hash('test123'),
            created_at=datetime.utcnow() - timedelta(days=45)
        )
        db.session.add(user)
        db.session.flush()
        user_id = user.id
        
        print(f"[OK] Created user: marcus_rodriguez (ID: {user_id})")
        
        # Assessment 1: Self Discovery
        assessment1 = Assessment(
            user_id=user_id,
            phase_id='self_discovery',
            phase_name='Self Discovery Assessment',
            progress_percentage=100.0,
            is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=44),
            completed_at=datetime.utcnow() - timedelta(days=42)
        )
        db.session.add(assessment1)
        db.session.flush()
        
        responses1 = [
            AssessmentResponse(
                assessment_id=assessment1.id,
                section_id='personal_strengths',
                question_id='core_strengths',
                question_text='What are your top 3 professional strengths?',
                response_type='text',
                response_value='Supply chain optimization - 6 years managing logistics for retail companies with $50M+ annual revenue. Sustainability expertise - Deep knowledge of circular economy principles, carbon accounting, and ESG frameworks. E-commerce operations - Built and scaled 2 marketplace platforms from 0 to $5M GMV as Head of Operations.'
            ),
            AssessmentResponse(
                assessment_id=assessment1.id,
                section_id='personal_strengths',
                question_id='technical_skills',
                question_text='Rate your technical proficiency',
                response_type='scale',
                response_value='3'
            ),
            AssessmentResponse(
                assessment_id=assessment1.id,
                section_id='entrepreneurial_motivation',
                question_id='why_entrepreneur',
                question_text='Why do you want to become an entrepreneur?',
                response_type='text',
                response_value='The fashion and consumer goods industries generate 92 million tons of textile waste annually. Having worked in supply chain for 6 years, I witnessed perfectly good returned items being landfilled because reverse logistics are broken. I want to build GreenLoop - a B2B SaaS platform that helps e-commerce brands turn returns into revenue through resale, donation, and recycling partnerships. This combines my logistics expertise with my passion for sustainability.'
            ),
            AssessmentResponse(
                assessment_id=assessment1.id,
                section_id='entrepreneurial_motivation',
                question_id='risk_tolerance',
                question_text='How comfortable are you with financial risk?',
                response_type='scale',
                response_value='3'
            ),
            AssessmentResponse(
                assessment_id=assessment1.id,
                section_id='entrepreneurial_motivation',
                question_id='backup_plan',
                question_text='Do you have a financial safety net?',
                response_type='text',
                response_value='Moderate safety net - 12 months emergency fund saved ($60K). No debt. Still working full-time while building MVP nights/weekends. Plan to go full-time when I hit $5K MRR or secure pre-seed funding. Spouse is supportive but concerned, so maintaining income is important for family stability.'
            ),
            AssessmentResponse(
                assessment_id=assessment1.id,
                section_id='work_style',
                question_id='work_ethic',
                question_text='Describe your typical work schedule and habits',
                response_type='text',
                response_value='Balancing full-time job + startup is intense. Corporate job 9-6 PM, then startup work 8-11 PM weeknights (15 hours/week) and Saturdays 9 AM-4 PM (7 hours). Total ~22 hours/week on GreenLoop. Sundays reserved for family. I batch tasks - Mondays/Wednesdays for customer calls, Tuesdays/Thursdays for product development, Fridays for partnerships. Sleep 7 hours minimum to avoid burnout.'
            ),
            AssessmentResponse(
                assessment_id=assessment1.id,
                section_id='work_style',
                question_id='stress_management',
                question_text='How do you handle high-pressure situations?',
                response_type='scale',
                response_value='4'
            ),
            AssessmentResponse(
                assessment_id=assessment1.id,
                section_id='decision_making',
                question_id='decision_style',
                question_text='How do you typically make important decisions?',
                response_type='text',
                response_value='Collaborative but decisive. I research options thoroughly (industry reports, competitor analysis, expert calls), discuss with 2-3 trusted advisors including my technical co-founder, then make final call within 1 week max. I trust data but also rely on 6 years of supply chain intuition. Document decisions in Notion to learn from outcomes. Recent example: chose Shopify app route over standalone SaaS after interviewing 8 potential customers.'
            ),
            AssessmentResponse(
                assessment_id=assessment1.id,
                section_id='leadership',
                question_id='team_management',
                question_text='Describe your leadership experience',
                response_type='text',
                response_value='Managed operations teams of 12-20 people for 4 years. Led warehouse optimization project that reduced costs 23% ($1.2M savings). My leadership style: clear KPIs, weekly check-ins, empowering team to solve problems. Built culture of continuous improvement. Promoted 5 team members during my tenure. Received "Leader of the Year" award in 2023 at my company.'
            ),
            AssessmentResponse(
                assessment_id=assessment1.id,
                section_id='network',
                question_id='professional_network',
                question_text='Describe your professional network',
                response_type='text',
                response_value='Strong in supply chain/logistics space: 20+ connections at major e-commerce brands (Shopify merchants, DTC brands), 12 former colleagues at 3PLs and fulfillment centers. Growing sustainability network through EcoSummit and Circular Economy conferences (50+ contacts). LinkedIn: 800 connections, 45% in e-commerce/logistics. Recently joined Climate Tech founders Slack (350 members). Weakness: limited VC network, working on this.'
            ),
            AssessmentResponse(
                assessment_id=assessment1.id,
                section_id='learning_mindset',
                question_id='learning_approach',
                question_text='How do you approach learning new skills?',
                response_type='text',
                response_value='Learning by doing + structured courses. Currently: SaaS metrics & unit economics (Reforge course), no-code development (building MVP in Bubble.io), carbon accounting (Climate tech certification). I learn best through projects - built 3 internal tools at my job to understand tech better. Allocate $200/month and 4 hours/week for learning. Document learnings in personal wiki.'
            ),
            AssessmentResponse(
                assessment_id=assessment1.id,
                section_id='commitment',
                question_id='time_commitment',
                question_text='How many hours per week can you commit?',
                response_type='scale',
                response_value='3'
            ),
        ]
        
        for r in responses1:
            db.session.add(r)
        
        # Assessment 2: Idea Discovery
        assessment2 = Assessment(
            user_id=user_id,
            phase_id='idea_discovery',
            phase_name='Idea Discovery Assessment',
            progress_percentage=100.0,
            is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=40),
            completed_at=datetime.utcnow() - timedelta(days=38)
        )
        db.session.add(assessment2)
        db.session.flush()
        
        responses2 = [
            AssessmentResponse(
                assessment_id=assessment2.id,
                section_id='problem_definition',
                question_id='problem_statement',
                question_text='What problem are you solving?',
                response_type='text',
                response_value='E-commerce brands lose $550B annually to returns (10-30% return rate online vs 8% in-store). Most returned items are in perfect condition but brands lack infrastructure to resell them profitably. Current options: (1) Liquidate at 10-20 cents on dollar (2) Landfill (3) Manual resale (too labor intensive). Result: massive waste + lost revenue. GreenLoop automates the entire reverse supply chain - grading, refurbishing, listing on resale channels, donation tax receipts, recycling partnerships.'
            ),
            AssessmentResponse(
                assessment_id=assessment2.id,
                section_id='problem_definition',
                question_id='target_audience',
                question_text='Who experiences this problem most acutely?',
                response_type='text',
                response_value='Primary: Mid-size DTC e-commerce brands ($5M-$100M revenue) selling apparel, electronics, or home goods. High return rates (15-30%), sustainability-focused brand identity, 50-500 employees. Secondary: Shopify Plus merchants, Amazon 3P sellers with brand stores. They have volume to justify solution but lack enterprise resources for custom systems. NOT targeting: Marketplaces (Amazon/eBay) - they have internal solutions. Small sellers (<$1M) - insufficient volume. Mega-retailers - require enterprise contracts.'
            ),
            AssessmentResponse(
                assessment_id=assessment2.id,
                section_id='solution',
                question_id='solution_description',
                question_text='Describe your solution',
                response_type='text',
                response_value='GreenLoop is a Shopify app + API that automates return monetization: (1) Customer returns item → our algorithm grades condition (A/B/C) via photos + questionnaire (2) Route optimal path: Grade A → resell on brand outlet or Poshmark/eBay, Grade B → donate to verified charity (tax deduction), Grade C → recycle via certified partners (3) Dashboard shows revenue recovered, CO2 saved, items diverted from landfill (4) White-label customer portal - brands can offer store credit for sustainable return options. Tech: Computer vision for grading, API integrations to resale platforms, logistics partnerships for pickup/processing.'
            ),
            AssessmentResponse(
                assessment_id=assessment2.id,
                section_id='solution',
                question_id='unique_value_prop',
                question_text='What makes your solution unique?',
                response_type='text',
                response_value='3 key differentiators: (1) Automation - competitors (Optoro, Returnly) require manual processes. We use AI grading + automated routing = 10x faster. (2) Multi-channel resale - we list on 5 platforms simultaneously (eBay, Poshmark, Mercari, brand outlet, B2B wholesale) vs competitors use 1-2. Increases recovery rate 35%. (3) Sustainability reporting - auto-generated ESG reports showing CO2 impact, waste diversion, donation value. Critical for brands with sustainability commitments. No competitor offers this.'
            ),
            AssessmentResponse(
                assessment_id=assessment2.id,
                section_id='validation',
                question_id='customer_interviews',
                question_text='How many potential customers have you interviewed?',
                response_type='text',
                response_value='Interviewed 23 e-commerce brands (15 apparel, 5 electronics, 3 home goods). Key insights: (1) 19/23 said returns are "top 3 operational headaches" (2) Average brand liquidates returns for $0.15 per dollar - massive pain (3) 14/23 actively looking for solution NOW (4) Willingness to pay: $200-800/month base + % of recovered revenue (5) Must integrate with Shopify, NetSuite, or Salesforce (6) Biggest concern: customer experience during returns process. Used insights to pivot from B2C app to B2B SaaS focus.'
            ),
            AssessmentResponse(
                assessment_id=assessment2.id,
                section_id='validation',
                question_id='early_traction',
                question_text='Do you have any early traction?',
                response_type='text',
                response_value='Yes - MVP launched 6 weeks ago: (1) 3 pilot customers (apparel brands with $8M, $12M, $22M revenue) testing free for 90 days (2) Processed 147 returns so far, recovered $6,200 vs $1,100 they would have gotten liquidating (5.6x improvement) (3) 2 brands already committed to paid plans starting next month ($400-600/month) (4) 8 more brands on waitlist from referrals (5) Featured in Shopify App Store "Sustainability" category (6) No paid marketing yet - all organic/referral growth.'
            ),
            AssessmentResponse(
                assessment_id=assessment2.id,
                section_id='market',
                question_id='market_size',
                question_text='Estimate your market size',
                response_type='text',
                response_value='TAM (Total Addressable Market): $550B annual e-commerce returns globally. SAM (Serviceable Available Market): $85B - mid-size e-commerce brands ($5M-$100M revenue) in US/EU with high return rates. Approx 45,000 businesses. SOM (Serviceable Obtainable Market): $850M - capturing 1% of SAM in 5 years. Initial focus: 2,500 Shopify Plus merchants with sustainability focus, average $15M revenue, 20% return rate = $3M returns/year per merchant. If we capture 5% recovery improvement, that is $150K/year value per customer.'
            ),
            AssessmentResponse(
                assessment_id=assessment2.id,
                section_id='market',
                question_id='competitors',
                question_text='Who are your main competitors?',
                response_type='text',
                response_value='Direct: (1) Optoro (enterprise, slow, expensive >$50K/year) - weakness: no SMB solution (2) Returnly (returns software, no resale automation) - weakness: brands still handle resale manually (3) Loop Returns (Shopify app, basic) - weakness: no automated grading/routing. Indirect: (1) Liquidation.com, B-Stock (auction platforms) - brands get pennies on dollar (2) In-house solutions (large retailers only) - too expensive for mid-market. Our advantage: We are the ONLY automated, multi-channel solution for mid-market with <$1K/month pricing + sustainability reporting.'
            ),
            AssessmentResponse(
                assessment_id=assessment2.id,
                section_id='business_model',
                question_id='revenue_model',
                question_text='How will you make money?',
                response_type='text',
                response_value='Hybrid pricing model: (1) SaaS subscription: $400-$1,200/month based on return volume tiers (<500, 500-2000, 2000+ returns/month) (2) Revenue share: 15% of value recovered from resale (incentive alignment - we win when brands win) (3) Transaction fees: $2 per return processed (covers logistics coordination costs). Target customer: 1,000 returns/month → $600 SaaS + $900 rev share + $2,000 transaction fees = $3,500/month = $42K/year ARPA. Unit economics: Gross margin 75%, CAC $4,500, LTV $126K (3 year avg), LTV:CAC = 28:1.'
            ),
            AssessmentResponse(
                assessment_id=assessment2.id,
                section_id='business_model',
                question_id='pricing_validation',
                question_text='Have you validated your pricing?',
                response_type='text',
                response_value='Yes, tested 3 pricing models with 15 potential customers: (1) Pure subscription ($800/month flat) - 6/15 said too expensive without seeing ROI first (2) Pure revenue share (25%) - 9/15 said percentage too high, worried about costs (3) Hybrid model (SaaS + 15% rev share) - 13/15 said "fair and aligned with our interests". Chose hybrid. Van Westendorp analysis showed $400-$800 optimal for base SaaS tier. Currently testing $600 base with pilot customers - no pushback so far. Planning $400/$600/$1,200 tiered structure at launch.'
            ),
        ]
        
        for r in responses2:
            db.session.add(r)
        
        # Assessment 3: Market Research
        assessment3 = Assessment(
            user_id=user_id,
            phase_id='market_research',
            phase_name='Market Research',
            progress_percentage=100.0,
            is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=35),
            completed_at=datetime.utcnow() - timedelta(days=33)
        )
        db.session.add(assessment3)
        db.session.flush()
        
        responses3 = [
            AssessmentResponse(
                assessment_id=assessment3.id,
                section_id='customer_segments',
                question_id='primary_segment',
                question_text='Describe your primary customer segment',
                response_type='text',
                response_value='Mid-size DTC apparel brands ($10M-$50M annual revenue). Persona: Director of Operations or Sustainability Manager, age 32-45, college educated. Psychographics: Sustainability-focused, data-driven, overwhelmed by returns logistics. Pain: Losing $800K-$2M/year on returns, pressure from exec team to reduce waste. They have tried liquidation (poor economics) and manual resale (too labor intensive). Decision process: 3-6 month sales cycle, need CFO approval for annual contracts, require ROI proof (pilot period essential).'
            ),
            AssessmentResponse(
                assessment_id=assessment3.id,
                section_id='customer_research',
                question_id='research_methods',
                question_text='What research methods have you used?',
                response_type='text',
                response_value='Multi-method approach: (1) Surveys - 47 responses from Shopify merchants (via Facebook groups) about returns pain points (2) In-depth interviews - 23 video calls with target customers (45-60 min each) (3) Industry reports - analyzed 8 research reports on e-commerce returns, circular economy, resale trends (4) Competitive analysis - signed up for 6 competitor products, mapped features/pricing (5) LinkedIn outreach - cold messaged 50 ops leaders, 18% response rate (6) Shadowing - spent 2 days at a 3PL facility watching returns processing firsthand. Learnings drove product roadmap.'
            ),
            AssessmentResponse(
                assessment_id=assessment3.id,
                section_id='market_trends',
                question_id='industry_trends',
                question_text='What market trends support your business?',
                response_type='text',
                response_value='5 major tailwinds: (1) Returns crisis - e-commerce returns up 70% since 2019, now $550B annually (2) Sustainability mandates - EU regulations requiring brands to report waste, circular economy adoption growing (3) Resale boom - secondhand market projected to hit $350B by 2027 (ThredUp report), consumers increasingly buying used (4) Shopify ecosystem - 1.7M merchants, strong app marketplace, high willingness to pay for add-ons (5) ESG investing - brands need sustainability metrics to attract capital, consumers demand transparency. Perfect storm of regulatory pressure + consumer demand + economic incentive.'
            ),
            AssessmentResponse(
                assessment_id=assessment3.id,
                section_id='competitive_analysis',
                question_id='competitive_advantage',
                question_text='What is your sustainable competitive advantage?',
                response_type='text',
                response_value='3-part moat: (1) Network effects - more resale channel partnerships = better pricing = more customers = more negotiating power for better partnerships (flywheel) (2) Data moat - proprietary AI grading algorithm improves with every return processed, currently 147 returns analyzed, targeting 10K+ for production-grade accuracy (3) Integration complexity - once integrated into Shopify + NetSuite + logistics stack, high switching costs. Defensibility timeline: Years 1-2 = speed/execution, Years 3-5 = network + data moat becomes meaningful. Not relying on patents (too easy to design around in software).'
            ),
            AssessmentResponse(
                assessment_id=assessment3.id,
                section_id='go_to_market',
                question_id='customer_acquisition',
                question_text='How will you acquire customers?',
                response_type='text',
                response_value='Phased GTM strategy: Phase 1 (Months 0-6): Outbound - LinkedIn/email to 500 target brands, goal 20 pilots, convert 8 to paid ($400/mo avg). Phase 2 (Months 6-12): Shopify App Store SEO + content marketing (blog, case studies), goal 15 organic installs/month. Phase 3 (Months 12-18): Partnerships with 3PLs and sustainability consultants (referral fees), conferences (eTail, ShopTalk). Phase 4 (Months 18-24): Paid ads (Google, LinkedIn) once CAC/LTV proven. Budget: $2K/month marketing in Year 1, scale to $15K/month Year 2. CAC target: <$4,000 (payback <12 months).'
            ),
            AssessmentResponse(
                assessment_id=assessment3.id,
                section_id='market_validation',
                question_id='pmf_signals',
                question_text='What evidence do you have of product-market fit?',
                response_type='text',
                response_value='Early signals (not full PMF yet): (1) 2 of 3 pilot customers already committed to paying next month (67% conversion before even asking) (2) 8 brands on waitlist from referrals (organic demand) (3) Pilot customers using product 3-5x per week (solid engagement) (4) "This is exactly what we needed" feedback from 2 customers (5) One customer asked if they can invest in seed round. Gaps before declaring PMF: Need 10+ paying customers with 6+ month retention, >40% on Sean Ellis test ("very disappointed" if product disappeared), $10K+ MRR. Currently at pre-PMF but strong early validation.'
            ),
        ]
        
        for r in responses3:
            db.session.add(r)
        
        # Assessment 4: Business Pillars Planning
        assessment4 = Assessment(
            user_id=user_id,
            phase_id='business_pillars',
            phase_name='Business Pillars Planning',
            progress_percentage=100.0,
            is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=30),
            completed_at=datetime.utcnow() - timedelta(days=27)
        )
        db.session.add(assessment4)
        db.session.flush()
        
        responses4 = [
            AssessmentResponse(
                assessment_id=assessment4.id,
                section_id='vision_mission',
                question_id='company_vision',
                question_text='What is your company vision?',
                response_type='text',
                response_value='Vision: Make every e-commerce return a sustainability win. Mission: Empower brands to turn returns from waste into revenue while drastically reducing environmental impact. By 2030, we aim to divert 100 million items from landfills and help 10,000 e-commerce brands build circular business models. Core values: (1) Planet-first - sustainability is not a marketing gimmick, it is our north star (2) Merchant success - we win when our customers recover more value (3) Radical transparency - open data on impact metrics (4) Operational excellence - logistics is hard, we sweat the details.'
            ),
            AssessmentResponse(
                assessment_id=assessment4.id,
                section_id='product_strategy',
                question_id='product_roadmap',
                question_text='Outline your 12-month product roadmap',
                response_type='text',
                response_value='Q1 2026: (1) Launch Shopify app v1.0 - automated grading, eBay/Poshmark integration (2) Onboard 10 paying customers. Q2: (3) Add donation partnerships with 3 charities, tax receipt automation (4) Build analytics dashboard - CO2 saved, revenue recovered, waste diverted (5) Reach 30 customers, $18K MRR. Q3: (6) Launch API for custom integrations (NetSuite, Salesforce) (7) Add B2B wholesale channel for bulk resale (8) Computer vision v2 - improve grading accuracy to 92%. Q4: (9) White-label customer portal for branded returns experience (10) International expansion (UK market) (11) 75 customers, $45K MRR. Tech stack: Bubble.io (MVP), migrating to Next.js + Python in Q3.'
            ),
            AssessmentResponse(
                assessment_id=assessment4.id,
                section_id='financial_planning',
                question_id='startup_costs',
                question_text='What are your estimated startup costs?',
                response_type='text',
                response_value='Total capital needed to reach profitability: $380K. Breakdown: (1) Product development - $120K (engineer contractor 6 months @ $15K/mo, design $10K, no-code tools $2K) (2) Operations - $80K (founder salary $3K/mo x 12, co-founder $2K/mo x 12, office/coworking $500/mo) (3) Marketing/sales - $65K ($2K/mo ads, $15K conferences, $20K content, $10K tools) (4) Logistics partnerships - $40K (integration fees, pilot programs with 3PLs) (5) Legal/admin - $25K (incorporation, contracts, accounting, insurance) (6) Buffer - $50K (20% contingency). Runway: 18 months to $20K MRR (break-even).'
            ),
            AssessmentResponse(
                assessment_id=assessment4.id,
                section_id='financial_planning',
                question_id='revenue_forecast',
                question_text='Project your revenue for the next 3 years',
                response_type='text',
                response_value='Conservative projections: Year 1 (2026) - 45 customers by EOY, avg $650/mo ARPA, $294K revenue ($24.5K MRR exit rate), -$110K profit (investment phase). Year 2 (2027) - 180 customers, $850 ARPA (pricing power + upsells), $1.83M revenue, $420K profit (23% margin). Year 3 (2028) - 420 customers, $1,100 ARPA, $5.54M revenue, $1.94M profit (35% margin). Assumptions: 15% monthly churn, 8 new customers/month organic growth, CAC $4,500, gross margin 75%, 2 sales hires in Year 2. Sensitivity: If achieve only 60% of targets, still hit $3.3M Year 3 revenue. Upside: Enterprise contracts could 2x these numbers.'
            ),
            AssessmentResponse(
                assessment_id=assessment4.id,
                section_id='team_structure',
                question_id='founding_team',
                question_text='Describe your founding team',
                response_type='text',
                response_value='2-person founding team: (1) Me (Marcus Rodriguez) - CEO, Supply Chain/Ops expert, 6 years logistics experience, domain expertise in returns, customer-facing role. Equity: 60%. (2) Technical co-founder (Jamie Lee) - CTO, full-stack engineer, 5 years at SaaS startups, built MVP, handles all product/engineering. Equity: 40%. Gap: No sales/marketing expert - plan to hire VP Sales in Year 2 at $120K + equity (2-3%). Skills balance: I bring industry knowledge + ops, Jamie brings technical execution. Both first-time founders (risk) but deep domain expertise (strength). Cap table: 100% founders, no investors yet, 15% reserved for ESOP.'
            ),
            AssessmentResponse(
                assessment_id=assessment4.id,
                section_id='operations',
                question_id='key_processes',
                question_text='What are your key operational processes?',
                response_type='text',
                response_value='5 core processes: (1) Customer onboarding - 2-week integration (Shopify app install, logistics partner setup, grading criteria customization, team training) (2) Returns processing - customer initiates return → grading questionnaire → routing decision → logistics coordination → resale listing (3) Quality assurance - spot-check 10% of gradings for accuracy, customer feedback loop (4) Financial reconciliation - monthly reports on revenue recovered, platform fees, payouts to brands (5) Customer success - weekly check-ins first month, then monthly, quarterly business reviews. Tools: Notion (docs), Slack (comms), Stripe (billing), Intercom (support), Metabase (analytics). Goal: automate 80% of operations by Year 2.'
            ),
            AssessmentResponse(
                assessment_id=assessment4.id,
                section_id='risk_management',
                question_id='key_risks',
                question_text='What are your biggest risks and mitigation strategies?',
                response_type='text',
                response_value='Top 5 risks + mitigation: (1) Low resale recovery rates - if items sell for less than expected, economics break. Mitigation: Multi-channel strategy (5 platforms), manual override option, transparent pricing. (2) Logistics complexity - returns processing is operationally hard. Mitigation: Partnership with established 3PL (InReturn, ReverseLogix), not building warehouses. (3) Customer acquisition cost too high - if CAC >$6K, unit economics fail. Mitigation: Shopify App Store organic channel, focus on referrals, content marketing. (4) Competition from Shopify or Amazon - big tech could build this feature. Mitigation: Speed, niche focus (sustainability angle), deep integrations. (5) Regulatory changes - new e-waste laws could impact model. Mitigation: Stay ahead of regulations, build compliance features, diversify geographies.'
            ),
            AssessmentResponse(
                assessment_id=assessment4.id,
                section_id='milestones',
                question_id='key_milestones',
                question_text='What are your key milestones for the next 12 months?',
                response_type='text',
                response_value='Month 3: 10 paying customers, $6K MRR, Shopify app live. Month 6: 25 customers, $16K MRR, case study published, fundraising started. Month 9: 50 customers, $32K MRR, $400K pre-seed closed, first sales hire. Month 12: 75 customers, $48K MRR, API launched, break-even month achieved. Success metrics: (1) Revenue - hit $45K+ MRR (2) Retention - <10% monthly churn (3) NPS - >50 (4) Processing volume - 25K returns/month across customer base (5) Impact - 200K items diverted from landfill, 500 tons CO2 saved. De-risk signal: If hit $25K MRR by Month 6, high confidence in model.'
            ),
            AssessmentResponse(
                assessment_id=assessment4.id,
                section_id='funding_strategy',
                question_id='funding_plan',
                question_text='What is your funding strategy?',
                response_type='text',
                response_value='Phased funding approach: (1) Pre-revenue (current) - $80K invested (my $50K savings + co-founder $30K) building MVP, running pilots. (2) Pre-seed ($400K at $2.5M post, Q2 2026) - when hit $10K MRR, 3 pilot → paid conversions. Use: 12 month runway, hire engineer, marketing. Targeting: climate tech angels, Shopify ecosystem funds. (3) Seed ($2M at $10M post, Q1 2027) - when hit $40K MRR, proven unit economics, 60+ customers. Use: scale sales (hire 3 AEs), expand product, international. Targeting: Series A funds doing seed extensions. Ideal: Bootstrap to $10K MRR, minimize dilution. If revenue growth slower than expected, may do $250K bridge round from angels.'
            ),
        ]
        
        for r in responses4:
            db.session.add(r)
        
        # Remaining assessments (5, 6, 7) - shorter for brevity
        # Assessment 5: Product Concept Testing
        assessment5 = Assessment(
            user_id=user_id,
            phase_id='product_concept',
            phase_name='Product Concept Testing',
            progress_percentage=100.0,
            is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=24),
            completed_at=datetime.utcnow() - timedelta(days=22)
        )
        db.session.add(assessment5)
        db.session.flush()
        
        responses5 = [
            AssessmentResponse(
                assessment_id=assessment5.id,
                section_id='mvp',
                question_id='mvp_features',
                question_text='What features are in your MVP?',
                response_type='text',
                response_value='Core MVP features: (1) Shopify app integration for automatic return data sync (2) Condition grading wizard (photo upload + questionnaire) (3) Automated routing to 2 resale channels (eBay, Poshmark) (4) Basic dashboard showing processed returns, revenue recovered (5) Email notifications for status updates. Deliberately excluded from MVP: computer vision grading (too complex), donation partnerships (nice-to-have), white-label portal (premium feature), API access (enterprise only). MVP took 8 weeks to build with no-code tools (Bubble.io + Zapier), cost $2K. Focus: Validate core workflow, not perfect automation.'
            ),
            AssessmentResponse(
                assessment_id=assessment5.id,
                section_id='user_testing',
                question_id='testing_results',
                question_text='What feedback have you received from user testing?',
                response_type='text',
                response_value='Tested with 5 beta users (3 weeks): Positive: "Way easier than liquidation" (4/5), "Love seeing sustainability metrics" (3/5), "Saved us 10 hours/week" (2/5). Critical: "Grading takes too long - 5 min per item" (3/5) - added auto-fill feature. "Need more resale channels" (4/5) - added Mercari + brand outlet. "Dashboard is confusing" (2/5) - simplified to 3 key metrics. Surprise insight: 2 users asked for donation option for unsellable items - we had not planned this, now building in Q2. Overall NPS from beta: 60 (good for MVP). Key learning: Brands care more about time savings than max revenue recovery.'
            ),
            AssessmentResponse(
                assessment_id=assessment5.id,
                section_id='iterations',
                question_id='product_iterations',
                question_text='How have you iterated based on feedback?',
                response_type='text',
                response_value='3 major pivots from feedback: (1) B2C → B2B focus (originally planned consumer app, discovered B2B pays more and has bigger pain) (2) Manual grading → Semi-automated (users hated full manual, full auto was not accurate enough, hybrid approach solved both) (3) Percentage pricing → Hybrid model (customers resisted pure rev share, hybrid SaaS + rev share aligned incentives better). Minor iterations: Added bulk actions, simplified onboarding from 45 min to 15 min, changed dashboard from 12 metrics to 3 core KPIs. Process: Weekly user calls → Notion feedback log → prioritize top 3 pain points → ship fix in 1-2 weeks → validate with users. Shipped 18 updates in 6 weeks of beta.'
            ),
            AssessmentResponse(
                assessment_id=assessment5.id,
                section_id='metrics',
                question_id='success_metrics',
                question_text='What metrics define product success?',
                response_type='text',
                response_value='North Star Metric: Revenue recovered per return (target: $18 avg, currently $14.50 in beta). Supporting metrics: (1) Activation - % of installs that process first return within 7 days (target 70%, current 65%) (2) Engagement - returns processed per customer per month (target 150+, current 120) (3) Retention - monthly active customers (target >85%, too early to measure) (4) Quality - resale success rate (% of items that sell within 60 days, target 75%, current 68%) (5) NPS (target 50+, current 60). Track weekly in Metabase dashboard. If revenue/return drops below $12, model breaks - trigger for investigation.'
            ),
            AssessmentResponse(
                assessment_id=assessment5.id,
                section_id='scalability',
                question_id='scale_readiness',
                question_text='How ready is your product to scale?',
                response_type='text',
                response_value='Current state: MVP can handle 50 customers, 10K returns/month before breaking. Not ready to scale yet. Bottlenecks: (1) No-code infrastructure (Bubble.io) - max 50K API calls/month, need rewrite to Next.js by Month 9 (2) Manual customer onboarding - takes 3 hours per customer, need self-serve flow (3) Single logistics partner - need 2-3 partners for redundancy (4) No monitoring/alerting - built basic Sentry integration. To scale to 200 customers: (1) Migrate to code-based stack ($40K eng cost) (2) Build self-serve onboarding (3) Add 2 more logistics partners (4) Implement robust error handling. Timeline: 6 months to be scale-ready. Strategy: Grow slowly to 30 customers while building scalable foundation.'
            ),
        ]
        
        for r in responses5:
            db.session.add(r)
        
        # Assessment 6: Business Development
        assessment6 = Assessment(
            user_id=user_id,
            phase_id='business_development',
            phase_name='Business Development',
            progress_percentage=100.0,
            is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=18),
            completed_at=datetime.utcnow() - timedelta(days=16)
        )
        db.session.add(assessment6)
        db.session.flush()
        
        responses6 = [
            AssessmentResponse(
                assessment_id=assessment6.id,
                section_id='partnerships',
                question_id='key_partnerships',
                question_text='What strategic partnerships are critical?',
                response_type='text',
                response_value='3 critical partnership categories: (1) Logistics/3PL - partnered with InReturn (3PL specializing in returns), they provide warehouse space and processing labor, we pay per-item fee ($3.50/return). Key for scaling without physical infrastructure. (2) Resale platforms - eBay (API partnership pending, currently manual), Poshmark (strategic partnership - they want sustainability angle for PR), Mercari (evaluating). (3) Sustainability orgs - in talks with Textile Exchange and Ellen MacArthur Foundation for credibility/certification. Future: Payment processors (Stripe partnership for faster onboarding), Shopify (goal: featured app status in 6 months).'
            ),
            AssessmentResponse(
                assessment_id=assessment6.id,
                section_id='sales_strategy',
                question_id='sales_process',
                question_text='Describe your sales process',
                response_type='text',
                response_value='Early-stage sales process (pre-scalable): (1) Outbound prospecting - LinkedIn search for "Director of Operations" at Shopify brands, cold email with personalized video (Loom) showing their returns data estimated savings, 8% reply rate (2) Discovery call - 30 min needs assessment, pain point validation, ROI calculator walkthrough (3) Pilot proposal - free 90-day trial processing 50-200 returns, weekly check-ins (4) Conversion - at day 60, present results + pricing, 67% conversion so far (2/3 pilots). Avg sales cycle: 8 weeks prospect → close. Bottleneck: Currently just me doing sales 10 hrs/week. Plan: Hire SDR at $50K in Month 9 to scale outbound, hire AE in Month 15.'
            ),
            AssessmentResponse(
                assessment_id=assessment6.id,
                section_id='customer_success',
                question_id='retention_strategy',
                question_text='How will you retain customers?',
                response_type='text',
                response_value='Retention strategy (targeting <10% monthly churn): (1) Onboarding excellence - dedicated 2-week onboarding with weekly calls, custom grading criteria setup, team training (2) Proactive success management - monthly business reviews showing ROI (revenue recovered, CO2 impact, time saved), quarterly strategy sessions (3) Product stickiness - deep Shopify integration makes switching painful, white-label portal creates customer lock-in (4) Continuous value add - quarterly feature releases based on feedback, annual benchmarking reports (5) Community building - customer Slack channel for peer learning, quarterly sustainability summits. Early signal: 2/3 pilot customers already asking about annual contracts (better pricing) - strong retention indicator.'
            ),
            AssessmentResponse(
                assessment_id=assessment6.id,
                section_id='channels',
                question_id='distribution_channels',
                question_text='What distribution channels will you use?',
                response_type='text',
                response_value='Multi-channel GTM strategy: (1) Shopify App Store (organic) - optimizing for "returns", "sustainability", "resale" keywords, goal 500 installs/month by Year 2. Currently 12 installs (just launched). (2) Direct outbound sales - LinkedIn + email, targeting 100 prospects/month, 8% reply rate, hiring SDR to scale this. (3) Content marketing - blog (SEO for "e-commerce returns solutions"), case studies, sustainability reports. Goal 5K organic visits/month by Year 1 end. (4) Partnerships/referrals - 3PL partners refer customers (10% rev share), sustainability consultants (affiliate program). (5) Conferences - eTailWest, ShopTalk (Year 2 budget). Focus first 6 months: Outbound + Shopify App Store (80% of pipeline).'
            ),
            AssessmentResponse(
                assessment_id=assessment6.id,
                section_id='brand_positioning',
                question_id='brand_strategy',
                question_text='How will you position your brand?',
                response_type='text',
                response_value='Brand positioning: "The sustainability-first returns solution for conscious e-commerce brands." Target psychographic: Mission-driven brand operators who care about planet AND profit. Not competing on price or features alone - positioning on values alignment + impact. Messaging pillars: (1) Turn waste into worth - every return is revenue opportunity (2) Planet-positive operations - CO2 tracking, landfill diversion metrics (3) Built by logistics experts - credibility through founder story (4) For brands who give a damn - attract sustainability-focused customers. Tone: Professional but purpose-driven, data-backed but optimistic. Inspiration: Patagonia (values-first), Stripe (developer-friendly clarity), Shopify (merchant success obsession). Visual identity: Earth tones (green/brown), circular design motifs.'
            ),
            AssessmentResponse(
                assessment_id=assessment6.id,
                section_id='marketing_budget',
                question_id='marketing_plan',
                question_text='What is your marketing budget and plan?',
                response_type='text',
                response_value='Year 1 marketing budget: $24K total ($2K/month). Allocation: (1) Content creation - $8K (freelance writers $500/mo, design $200/mo) - 2 blog posts/week, 1 case study/month (2) Paid ads - $6K (LinkedIn ads $500/mo starting Month 6 once PMF validated) (3) Tools - $4K (HubSpot $400/mo, Ahrefs $100/mo, Canva $15/mo) (4) Events/sponsorships - $4K (sustainability conference booth, podcast sponsorships) (5) PR - $2K (press release distribution, journalist outreach). Channels: Focus 70% on content SEO (high ROI, long-term compounding), 20% on community building (Slack, Reddit), 10% testing paid. Goal: 30% of customers from organic by end of Year 1. CAC target: <$4K blended across all channels.'
            ),
        ]
        
        for r in responses6:
            db.session.add(r)
        
        # Assessment 7: Business Prototype Testing
        assessment7 = Assessment(
            user_id=user_id,
            phase_id='prototype_testing',
            phase_name='Business Prototype Testing',
            progress_percentage=100.0,
            is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=12),
            completed_at=datetime.utcnow() - timedelta(days=10)
        )
        db.session.add(assessment7)
        db.session.flush()
        
        responses7 = [
            AssessmentResponse(
                assessment_id=assessment7.id,
                section_id='pilot_results',
                question_id='pilot_performance',
                question_text='What results have you achieved from pilots?',
                response_type='text',
                response_value='3 pilot customers, 90-day test period (Weeks 1-12): Customer A (apparel, $8M revenue): 58 returns processed, $2,340 recovered vs $580 liquidation value (4x improvement), 12 hours saved/month. Committed to $400/mo plan. Customer B (electronics, $12M revenue): 47 returns, $2,890 recovered vs $720 (4.2x), 8 hours saved. Committed to $600/mo plan. Customer C (home goods, $22M revenue): 42 returns, $980 recovered vs $310 (3.2x lower due to bulky items), 6 hours saved. Still evaluating (logistics challenges). Aggregate: 147 returns, $6,210 total recovered, avg $42/return vs $11 liquidation baseline (3.8x improvement). Success rate: 67% items sold within 60 days. Key learning: Apparel/electronics work great, home goods need different routing logic (bulkier = higher logistics costs).'
            ),
            AssessmentResponse(
                assessment_id=assessment7.id,
                section_id='unit_economics',
                question_id='economics_validation',
                question_text='Have you validated your unit economics?',
                response_type='text',
                response_value='Unit economics per customer (based on 3 pilots): ARPA: $550/month (avg of $400/$600 tiers). Gross margin: 72% ($396 gross profit per customer/month). Costs: 3PL processing $3.50/return x 50 returns = $175, platform fees (Shopify, resale channels) $45, hosting/tools $30, support time 2 hours @ $50/hr = $100. Total COGS: $350. CAC: $4,500 (current, target $3,500 at scale via organic channels). LTV: $550 x 36 months x 72% margin x 80% retention = $11,404. LTV:CAC ratio: 2.5:1 (healthy is >3:1, need improvement). Payback period: 8 months (target <12 months). Path to improve: (1) Increase ARPA to $750 via upsells (2) Reduce CAC via Shopify App Store organic (3) Improve retention to 85%+ → LTV:CAC of 4:1.'
            ),
            AssessmentResponse(
                assessment_id=assessment7.id,
                section_id='challenges',
                question_id='key_challenges',
                question_text='What challenges have you encountered?',
                response_type='text',
                response_value='Top 5 challenges: (1) Logistics complexity - coordinating pickup, processing, and shipping across multiple channels is hard. Returns come in waves (post-holiday spike), hard to predict capacity needs. Mitigation: Building 2nd 3PL partnership for redundancy. (2) Resale unpredictability - some items sit for 45+ days, tying up capital. Mitigation: Dynamic pricing algorithm, faster liquidation option for slow movers. (3) Customer education - brands do not understand circular economy concepts, need hand-holding. Mitigation: Better onboarding content, video tutorials. (4) Technical debt - no-code stack breaking at 150 returns/month, need rewrite. Mitigation: Fundraising to hire engineer. (5) Sales bandwidth - I am doing everything (CEO, sales, support), cannot scale. Mitigation: Hiring SDR in 3 months. Biggest surprise: Customers care MORE about sustainability metrics than we expected - doubling down on impact reporting.'
            ),
            AssessmentResponse(
                assessment_id=assessment7.id,
                section_id='learnings',
                question_id='key_learnings',
                question_text='What are your key learnings so far?',
                response_type='text',
                response_value='10 critical learnings: (1) Sustainability sells - customers will pay premium for planet-positive solutions (2) Pilot length matters - 90 days is minimum to see ROI, 60 days too short (3) Apparel > electronics > home goods for return value recovery (4) Brands want time savings as much as revenue recovery (5) Integration ease is make-or-break - Shopify app install must be <10 min (6) Pricing: Hybrid model (SaaS + rev share) aligns incentives better than pure subscription (7) Network effects are real - more resale channels = better outcomes (8) Customer success is critical - weekly check-ins during first month prevent churn (9) Impact metrics (CO2, waste) are powerful sales tools (10) Niche positioning (sustainability) attracts better customers than generic "returns software". Mindset shift: This is not just a SaaS play, it is a logistics/sustainability play with software enabling it.'
            ),
            AssessmentResponse(
                assessment_id=assessment7.id,
                section_id='next_steps',
                question_id='immediate_priorities',
                question_text='What are your immediate next steps?',
                response_type='text',
                response_value='Next 90 days priorities: (1) Convert 2 pilot customers to paid (done - both signed!) and onboard them fully (2) Sign 8 new customers via outbound sales (pipeline: 15 qualified leads) to hit $6K MRR (3) Ship v1.1 with donation feature and improved dashboard (4 weeks of dev) (4) Finalize 2nd logistics partnership (InReturn backup) for capacity (5) Start fundraising conversations - target 5 angel meetings, 3 climate tech funds (6) Hire part-time SDR to scale outbound ($3K/month contractor) (7) Launch content marketing - publish 8 blog posts, 2 case studies (8) Get first testimonial/review on Shopify App Store (social proof). Success criteria for 90 days: $8K MRR, 12 paying customers, $300K pre-seed term sheet, NPS >60, <5% churn. De-risk signals: If hit $10K MRR in 90 days, we have product-market fit.'
            ),
            AssessmentResponse(
                assessment_id=assessment7.id,
                section_id='growth_trajectory',
                question_id='growth_plan',
                question_text='What is your growth trajectory?',
                response_type='text',
                response_value='Growth plan (conservative, bottoms-up): Month 3: 10 customers, $6K MRR (recent: 2 paid conversions). Month 6: 25 customers, $16K MRR (+5 net new/month via outbound + Shopify App Store). Month 9: 45 customers, $29K MRR (SDR hired, scaling outbound to 8 new/month). Month 12: 75 customers, $48K MRR (first sales hire, content marketing driving 30% organic). Month 18: 140 customers, $105K MRR (Shopify App Store momentum, partnerships kicking in). Month 24: 250 customers, $212K MRR (paid ads, enterprise deals starting). Assumptions: 12% monthly churn (improving to 8% by Month 12), $650 ARPA (growing to $850 via upsells), 60% gross margin scaling to 75%. Challenges: Sales hiring, product scalability, maintaining quality at volume. Confidence level: 70% we hit Month 12 target, 50% we hit Month 24 (many unknowns).'
            ),
        ]
        
        for r in responses7:
            db.session.add(r)
        
        # Commit all
        db.session.commit()
        
        print(f"\n[SUCCESS] Created Marcus Rodriguez with 7 complete assessments!")
        print(f"\n[ASSESSMENTS] Summary:")
        print(f"   - Self Discovery: 12 responses")
        print(f"   - Idea Discovery: 10 responses")
        print(f"   - Market Research: 6 responses")
        print(f"   - Business Pillars: 9 responses")
        print(f"   - Product Concept Testing: 5 responses")
        print(f"   - Business Development: 6 responses")
        print(f"   - Business Prototype Testing: 6 responses")
        print(f"   TOTAL: 54 responses (100% completion)")
        
        print(f"\n[CREDENTIALS] Login Info:")
        print(f"   Username: marcus_rodriguez")
        print(f"   Email: marcus.rodriguez@greenloop.co")
        print(f"   Password: test123")
        print(f"   User ID: {user_id}")
        
        print(f"\n[BUSINESS] Profile:")
        print(f"   Company: GreenLoop (E-commerce Returns Sustainability Platform)")
        print(f"   Stage: MVP with 3 pilot customers, 2 converting to paid")
        print(f"   Traction: $6.2K recovered from 147 returns, $6K MRR target Month 3")
        print(f"   Founder: 6 years supply chain/logistics, sustainability expert")
        
        return user_id

if __name__ == '__main__':
    create_marcus_rodriguez()
