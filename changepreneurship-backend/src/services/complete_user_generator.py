"""
Complete User Data Generator
Creates a fully populated test user with 100% realistic assessment responses
representing a Tech Startup Founder with strong business acumen
"""
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from ..models.assessment import db, User, Assessment, AssessmentResponse

class CompleteUserGenerator:
    """
    Generates a complete user profile: Sarah Chen - Tech SaaS Founder
    Background: Former Senior Product Manager at tech company, 8 years experience
    Idea: AI-powered project management tool for remote teams
    Stage: Validating MVP with beta customers
    """
    
    def __init__(self, session=None):
        self.session = session or db.session
    
    def create_complete_user(self):
        """
        Create a fully populated test user with 100% completion
        """
        try:
            username = 'sarah_chen_founder'
            
            # Check if user exists
            existing_user = self.session.query(User).filter_by(username=username).first()
            if existing_user:
                print(f"User {username} already exists (ID: {existing_user.id})")
                user_id = existing_user.id
            else:
                # Create new user with properly hashed password
                test_user = User(
                    username=username,
                    email='sarah.chen@techvision.io',
                    password_hash=generate_password_hash('test123')
                )
                self.session.add(test_user)
                self.session.commit()
                user_id = test_user.id
                print(f"✅ Created user: {username} (ID: {user_id})")
            
            # Create all assessments with 100% completion
            self._create_all_assessments(user_id)
            
            return user_id
            
        except Exception as e:
            print(f"❌ Error creating complete user: {str(e)}")
            self.session.rollback()
            return None
    
    def _create_all_assessments(self, user_id):
        """
        Create all 7 assessments with complete, realistic responses
        """
        
        # 1. SELF DISCOVERY ASSESSMENT - 100%
        self._create_self_discovery(user_id)
        
        # 2. IDEA DISCOVERY ASSESSMENT - 100%
        self._create_idea_discovery(user_id)
        
        # 3. MARKET RESEARCH - 100%
        self._create_market_research(user_id)
        
        # 4. BUSINESS PILLARS PLANNING - 100%
        self._create_business_pillars(user_id)
        
        # 5. PRODUCT CONCEPT TESTING - 100%
        self._create_product_concept(user_id)
        
        # 6. BUSINESS DEVELOPMENT - 100%
        self._create_business_development(user_id)
        
        # 7. BUSINESS PROTOTYPE TESTING - 100%
        self._create_prototype_testing(user_id)
    
    def _create_self_discovery(self, user_id):
        """
        Self Discovery Assessment - Understanding founder strengths & motivations
        """
        assessment = self._get_or_create_assessment(
            user_id, 
            'Self Discovery Assessment', 
            100
        )
        
        responses = [
            {
                'section_id': 'personal_strengths',
                'question_id': 'core_strengths',
                'question_text': 'What are your top 3 professional strengths?',
                'response_type': 'text',
                'response_value': 'Strategic thinking and product vision - I excel at seeing the big picture and connecting user needs with technical solutions. Team leadership and mentorship - 8 years managing cross-functional product teams of 10-15 people. Data-driven decision making - Strong analytical skills with experience in SQL, analytics tools, and A/B testing.'
            },
            {
                'section_id': 'personal_strengths',
                'question_id': 'technical_skills',
                'question_text': 'Rate your technical proficiency',
                'response_type': 'scale',
                'response_value': '4'
            },
            {
                'section_id': 'entrepreneurial_motivation',
                'question_id': 'why_entrepreneur',
                'question_text': 'Why do you want to become an entrepreneur?',
                'response_type': 'text',
                'response_value': 'After 8 years in corporate product management, I have identified a persistent pain point that existing solutions fail to address effectively. Remote team collaboration tools lack intelligent automation and proactive insights. I want to build a solution that genuinely helps distributed teams work better. Additionally, I am seeking more autonomy in decision-making and the ability to directly impact user outcomes without corporate bureaucracy.'
            },
            {
                'section_id': 'entrepreneurial_motivation',
                'question_id': 'risk_tolerance',
                'question_text': 'How comfortable are you with financial risk?',
                'response_type': 'scale',
                'response_value': '4'
            },
            {
                'section_id': 'entrepreneurial_motivation',
                'question_id': 'backup_plan',
                'question_text': 'Do you have a financial safety net?',
                'response_type': 'text',
                'response_value': 'Yes - I have 18 months of living expenses saved. My spouse has stable income that covers 60% of household expenses. I am also maintaining part-time consulting work (10 hours/week) that generates $3,000/month to reduce burn rate.'
            },
            {
                'section_id': 'work_style',
                'question_id': 'work_ethic',
                'question_text': 'Describe your typical work schedule and habits',
                'response_type': 'text',
                'response_value': 'Highly structured and disciplined. I wake at 6 AM for deep work sessions (6:30-9:30 AM) on product strategy and coding. Afternoons are for meetings, user interviews, and team collaboration. I maintain strict work-life boundaries - no work after 7 PM or on weekends to prevent burnout, having learned this lesson in my corporate years. I use time-blocking and the Pomodoro technique for focus.'
            },
            {
                'section_id': 'work_style',
                'question_id': 'stress_management',
                'question_text': 'How do you handle high-pressure situations?',
                'response_type': 'scale',
                'response_value': '5'
            },
            {
                'section_id': 'decision_making',
                'question_id': 'decision_style',
                'question_text': 'How do you typically make important decisions?',
                'response_type': 'text',
                'response_value': 'Data-informed but not data-driven to paralysis. I gather quantitative data (analytics, user metrics) and qualitative insights (user interviews, team feedback), then make decisive calls within 48 hours for most decisions. I use a decision journal to track outcomes and improve my judgment over time. For critical decisions (pricing, pivots), I consult 2-3 trusted advisors but ultimately trust my intuition backed by research.'
            },
            {
                'section_id': 'leadership',
                'question_id': 'team_management',
                'question_text': 'Describe your leadership experience',
                'response_type': 'text',
                'response_value': 'Led cross-functional product teams for 5 years. Successfully managed engineers, designers, and marketers through 3 major product launches. My style: clear vision, autonomous execution, weekly 1-on-1s, transparent communication. Built a culture of experimentation where team felt safe to take risks. Received 95%+ positive feedback on leadership in employee surveys.'
            },
            {
                'section_id': 'network',
                'question_id': 'professional_network',
                'question_text': 'Describe your professional network',
                'response_type': 'text',
                'response_value': 'Strong network in tech/SaaS space: 15+ product managers at leading tech companies, 8 engineers who have worked at startups, 5 former colleagues now at VC firms. Active in 3 professional communities (Product Hunt, Indie Hackers, local startup meetup). Mentor 2 junior PMs. LinkedIn network of 1,200+ connections with 60% in tech industry.'
            },
            {
                'section_id': 'learning_mindset',
                'question_id': 'learning_approach',
                'question_text': 'How do you approach learning new skills?',
                'response_type': 'text',
                'response_value': 'Systematic and hands-on. I use the 80/20 principle - learn core concepts quickly through courses/books, then learn by doing real projects. Currently learning: Next.js (building MVP), growth marketing (completed Y Combinator Startup School), and financial modeling. I spend 5 hours/week on structured learning, track progress in Notion, and apply learning immediately to my startup.'
            },
            {
                'section_id': 'commitment',
                'question_id': 'time_commitment',
                'question_text': 'How many hours per week can you commit?',
                'response_type': 'scale',
                'response_value': '5'
            }
        ]
        
        self._create_responses(assessment.id, responses)
        print(f"✅ Self Discovery Assessment: 100% ({len(responses)} responses)")
    
    def _create_idea_discovery(self, user_id):
        """
        Idea Discovery Assessment - Validating the business concept
        """
        assessment = self._get_or_create_assessment(
            user_id,
            'Idea Discovery Assessment',
            100
        )
        
        responses = [
            {
                'section_id': 'problem_definition',
                'question_id': 'core_problem',
                'question_text': 'What problem are you solving?',
                'response_type': 'text',
                'response_value': 'Remote teams waste 15-20 hours per week on communication overhead, status updates, and context switching. Existing project management tools (Asana, Jira, Monday) are passive databases that require constant manual updates. Teams lack proactive insights about blockers, risks, or workload imbalances until it is too late. This leads to missed deadlines, burnout, and poor collaboration quality.'
            },
            {
                'section_id': 'problem_definition',
                'question_id': 'problem_severity',
                'question_text': 'How severe is this problem?',
                'response_type': 'scale',
                'response_value': '5'
            },
            {
                'section_id': 'solution_overview',
                'question_id': 'solution_description',
                'question_text': 'Describe your solution',
                'response_type': 'text',
                'response_value': 'TeamSync AI - An intelligent project management platform that uses AI to automatically track progress, predict delays, and optimize team workload. Key features: (1) Auto-generated standup reports from Slack/GitHub activity, (2) Predictive analytics that flag at-risk projects 2 weeks early, (3) Smart workload balancing that prevents burnout, (4) AI meeting summaries with action items. Think: "Autopilot for remote team coordination"'
            },
            {
                'section_id': 'target_market',
                'question_id': 'target_customer',
                'question_text': 'Who is your target customer?',
                'response_type': 'text',
                'response_value': 'Primary: Engineering and product teams at Series A-C startups (50-250 employees). These teams are too large for informal coordination but too small for enterprise tools. Decision maker: VP of Engineering or Head of Product. Budget authority: $10-30K annual spend. Pain: Rapid team growth causing coordination chaos.'
            },
            {
                'section_id': 'target_market',
                'question_id': 'market_size',
                'question_text': 'Estimate your total addressable market',
                'response_type': 'text',
                'response_value': 'TAM: Project management software market is $6.5B globally. SAM: Remote team collaboration tools for 50-250 person companies = ~$850M. SOM: Target 1% market share in year 3 = $8.5M ARR. Bottoms-up: 50,000 target companies x 10% conversion x $5K ACV = $25M potential. Conservative goal: $2M ARR in year 2.'
            },
            {
                'section_id': 'unique_value',
                'question_id': 'differentiation',
                'question_text': 'What makes your solution unique?',
                'response_type': 'text',
                'response_value': 'Three key differentiators: (1) Proactive AI insights vs passive data entry - we predict problems before they happen, (2) Non-invasive data collection - integrates with existing tools (Slack, GitHub, Notion) without requiring new workflows, (3) Built specifically for remote-first teams - not adapted from in-office paradigms. Our AI model learns each team\'s patterns and provides personalized recommendations.'
            },
            {
                'section_id': 'validation',
                'question_id': 'customer_validation',
                'question_text': 'Have you validated this idea with potential customers?',
                'response_type': 'text',
                'response_value': 'Yes - Conducted 45 customer discovery interviews with engineering leaders. Key findings: 38/45 (84%) confirmed this is a top-3 pain point. 25/45 said they would pay $100/user/month. Built an MVP and ran a 6-week beta with 5 companies (8-20 person teams). Results: 4/5 renewed, average NPS of 72, 15% time savings measured. One beta customer referred us to 3 other companies.'
            },
            {
                'section_id': 'validation',
                'question_id': 'willingness_to_pay',
                'question_text': 'Have customers expressed willingness to pay?',
                'response_type': 'scale',
                'response_value': '5'
            },
            {
                'section_id': 'business_model',
                'question_id': 'revenue_model',
                'question_text': 'How will you make money?',
                'response_type': 'text',
                'response_value': 'SaaS subscription model with three tiers: (1) Starter: $49/user/month for teams up to 10, basic AI features, (2) Professional: $89/user/month for unlimited team size, advanced predictions, integrations, (3) Enterprise: Custom pricing for 100+ users, dedicated support, on-premise options. Freemium option: 3 users free forever to drive viral growth. Target 70% gross margins typical of SaaS.'
            },
            {
                'section_id': 'competitive_landscape',
                'question_id': 'competitors',
                'question_text': 'Who are your main competitors?',
                'response_type': 'text',
                'response_value': 'Direct: Linear (modern project tracking), Height (AI-powered PM tool), Asana (market leader). Indirect: Notion, ClickUp, Monday.com. Our advantage: They focus on task management; we focus on team intelligence. Linear is design-focused but lacks predictive AI. Height has AI but poor integrations. Asana is feature-rich but overwhelming and expensive. We are more automated, simpler, and AI-native.'
            }
        ]
        
        self._create_responses(assessment.id, responses)
        print(f"✅ Idea Discovery Assessment: 100% ({len(responses)} responses)")
    
    def _create_market_research(self, user_id):
        """
        Market Research Assessment - Deep market understanding
        """
        assessment = self._get_or_create_assessment(
            user_id,
            'Market Research',
            100
        )
        
        responses = [
            {
                'section_id': 'market_analysis',
                'question_id': 'market_trends',
                'question_text': 'What are the key market trends?',
                'response_type': 'text',
                'response_value': 'Three macro trends driving our market: (1) Remote work is permanent - 74% of companies plan hybrid/remote forever (Gartner 2024), creating sustained demand for collaboration tools. (2) AI integration in SaaS - Buyers expect AI features; willingness to pay 30% premium for AI-powered tools (McKinsey). (3) Consolidation fatigue - Teams using 10+ tools on average, seeking unified platforms. Project management market growing 12% CAGR through 2028.'
            },
            {
                'section_id': 'customer_research',
                'question_id': 'customer_interviews',
                'question_text': 'How many customer interviews have you conducted?',
                'response_type': 'text',
                'response_value': '45 in-depth interviews (30-45 min each) with engineering leaders, product managers, and CTOs at 30 companies. Interview breakdown: 25 at target customer profile (Series A-C startups), 10 at larger companies (to understand enterprise needs), 10 at smaller startups (<20 people). Also ran 3 customer surveys with 200+ responses. Ongoing: Weekly user interviews with beta customers.'
            },
            {
                'section_id': 'competitive_analysis',
                'question_id': 'competitive_research',
                'question_text': 'Describe your competitive analysis',
                'response_type': 'text',
                'response_value': 'Deep analysis of 12 competitors: Tested all major platforms (Asana, Monday, Jira, Linear, Height, ClickUp, Notion). Created feature comparison matrix across 25 dimensions. Analyzed pricing: Average $15-25/user/month for mid-tier plans. Read 500+ G2/Capterra reviews to identify common complaints: complexity, lack of AI, poor integrations. Interviewed 8 customers who switched from competitors - key reasons: too manual (60%), too expensive (25%), poor UX (15%).'
            },
            {
                'section_id': 'pricing_research',
                'question_id': 'pricing_strategy',
                'question_text': 'What is your pricing research showing?',
                'response_type': 'text',
                'response_value': 'Conducted Van Westendorp pricing study with 50 potential customers. Results: Acceptable range $60-120/user/month, optimal price point $89/user/month. Compared to competitors: Asana $24, Monday $16, Linear $10, Height $15 per user/month. Our premium positioning justified by AI value prop. 68% said they would switch at $89 price point. Planning to start at $49 for early adopter discount, raise to $89 after first 100 customers.'
            },
            {
                'section_id': 'market_positioning',
                'question_id': 'positioning_statement',
                'question_text': 'Write your positioning statement',
                'response_type': 'text',
                'response_value': 'For remote engineering teams at high-growth startups who struggle with coordination overhead, TeamSync AI is an intelligent project management platform that proactively prevents problems before they happen. Unlike traditional PM tools that require constant manual updates, TeamSync automatically tracks progress and predicts issues 2 weeks early, saving teams 15+ hours per week on status meetings and manual coordination.'
            },
            {
                'section_id': 'go_to_market',
                'question_id': 'distribution_channels',
                'question_text': 'What are your primary distribution channels?',
                'response_type': 'text',
                'response_value': 'Multi-channel GTM strategy: (1) Product-led growth - Freemium with viral invite loops, focus on PLG for first 1,000 users, (2) Content marketing - SEO-optimized content for "remote team productivity" keywords, (3) Community building - Active presence in Indie Hackers, Product Hunt, dev communities, (4) Partnerships - Integration partnerships with Slack, GitHub, Notion for co-marketing, (5) Outbound sales - Hire first AE at 100 customers to target Series A+ companies.'
            }
        ]
        
        self._create_responses(assessment.id, responses)
        print(f"✅ Market Research: 100% ({len(responses)} responses)")
    
    def _create_business_pillars(self, user_id):
        """
        Business Pillars Planning - Core business foundation
        """
        assessment = self._get_or_create_assessment(
            user_id,
            'Business Pillars Planning',
            100
        )
        
        responses = [
            {
                'section_id': 'vision_mission',
                'question_id': 'company_vision',
                'question_text': 'What is your company vision?',
                'response_type': 'text',
                'response_value': 'To make remote team collaboration as seamless as in-person by 2030. We envision a future where distributed teams have superpowers - AI handles coordination overhead, allowing humans to focus on creative problem-solving and deep work. Our vision: Every remote team in the world uses AI-powered coordination, reducing meetings by 50% while improving outcomes.'
            },
            {
                'section_id': 'vision_mission',
                'question_id': 'mission_statement',
                'question_text': 'What is your mission statement?',
                'response_type': 'text',
                'response_value': 'TeamSync AI empowers remote teams to work smarter through intelligent automation. We eliminate coordination overhead by proactively identifying blockers, optimizing workloads, and automating status updates - giving teams more time for meaningful work and better work-life balance.'
            },
            {
                'section_id': 'core_values',
                'question_id': 'company_values',
                'question_text': 'What are your core company values?',
                'response_type': 'text',
                'response_value': '1. Radical transparency - Open communication, public roadmap, honest about limitations. 2. Respect time - Build tools that save time, not waste it. No BS meetings or features. 3. AI for good - Use AI to reduce burnout and improve wellbeing, not surveillance. 4. Customer obsession - Ship fast based on feedback, 24-hour support response time. 5. Remote-first culture - Practice what we preach, fully distributed team.'
            },
            {
                'section_id': 'team_structure',
                'question_id': 'founding_team',
                'question_text': 'Describe your founding team',
                'response_type': 'text',
                'response_value': 'Solo founder currently, with 2 advisors. Actively recruiting co-founder: Ideal profile - senior full-stack engineer with ML experience, loves remote work, wants equity over salary. Have 3 strong candidates in pipeline. Until then: Outsourcing development to agency for MVP ($40K), plan to bring first engineer in-house at $50K ARR. Advisory board: Former VP Eng at unicorn, growth marketing expert, angel investor.'
            },
            {
                'section_id': 'team_structure',
                'question_id': 'hiring_plan',
                'question_text': 'What is your hiring plan for the first year?',
                'response_type': 'text',
                'response_value': 'Months 0-6: Solo + freelancers + advisors. Month 6-9: Hire co-founder/CTO (equity heavy, 15-20%, $100K salary). Month 9-12: Hire founding engineer ($120K + 2% equity) and customer success lead ($80K + 1% equity). Year 2: Scale to 8 people - 3 engineers, 1 designer, 1 sales/BD, 1 CS, 1 marketer. Focus: Keep team lean, senior hires, remote-first.'
            },
            {
                'section_id': 'financial_planning',
                'question_id': 'funding_strategy',
                'question_text': 'What is your funding strategy?',
                'response_type': 'text',
                'response_value': 'Bootstrapped to MVP + first 10 paying customers using $50K personal savings + $30K from consulting. Then raise $500K pre-seed from angels/micro-VCs at $3M valuation. Use 18 months of runway to reach $30K MRR ($360K ARR) with strong unit economics. Then raise $2-3M seed at $12-15M valuation. Goal: Be default alive at $100K MRR, raise from position of strength, not desperation.'
            },
            {
                'section_id': 'financial_planning',
                'question_id': 'revenue_projections',
                'question_text': 'Provide your 3-year revenue projections',
                'response_type': 'text',
                'response_value': 'Year 1: $150K ARR (30 customers at $5K ACV, focus on product-market fit). Year 2: $1.2M ARR (150 customers, scale go-to-market, hire first sales rep). Year 3: $5M ARR (500 customers, proven playbook, optimize CAC/LTV). Assumptions: $2K CAC, $10K LTV, 85% gross margin, 5% monthly churn, 110% net revenue retention. Conservative compared to SaaS benchmarks.'
            },
            {
                'section_id': 'product_roadmap',
                'question_id': 'product_vision',
                'question_text': 'What is your product roadmap?',
                'response_type': 'text',
                'response_value': 'Phase 1 (Months 1-6): Core MVP - Slack integration, auto standups, basic task tracking, simple AI predictions. Phase 2 (Months 7-12): Intelligence layer - Advanced AI predictions, workload balancing, GitHub integration, meeting summaries. Phase 3 (Year 2): Platform - API, custom integrations, mobile apps, enterprise features (SSO, RBAC). Phase 4 (Year 3): Ecosystem - App marketplace, AI customization, industry-specific versions.'
            },
            {
                'section_id': 'risk_management',
                'question_id': 'key_risks',
                'question_text': 'What are your top 3 business risks?',
                'response_type': 'text',
                'response_value': '1. AI accuracy - If predictions are wrong, users lose trust. Mitigation: Start with high-confidence predictions only, transparent confidence scores, learn from feedback. 2. Market timing - If remote work declines, market shrinks. Mitigation: Hybrid works too, focus on distributed teams (permanent trend). 3. Competition - Giants (Microsoft, Atlassian) could copy us. Mitigation: Move fast, build network effects, own niche before they notice.'
            }
        ]
        
        self._create_responses(assessment.id, responses)
        print(f"✅ Business Pillars Planning: 100% ({len(responses)} responses)")
    
    def _create_product_concept(self, user_id):
        """
        Product Concept Testing - MVP and product validation
        """
        assessment = self._get_or_create_assessment(
            user_id,
            'Product Concept Testing',
            100
        )
        
        responses = [
            {
                'section_id': 'mvp_definition',
                'question_id': 'core_features',
                'question_text': 'What are your MVP core features?',
                'response_type': 'text',
                'response_value': '1. Slack integration - Auto-sync tasks from Slack threads, no manual entry. 2. AI standup generator - Daily summaries of what each person did (from Slack, GitHub, Notion activity). 3. Risk predictor - Flag projects at risk 2 weeks early with 80%+ accuracy. 4. Simple task board - Kanban view with AI-suggested priorities. 5. Team dashboard - Workload view showing who is overloaded. Tech: Next.js frontend, Python/FastAPI backend, GPT-4 for AI, PostgreSQL + Redis.'
            },
            {
                'section_id': 'mvp_definition',
                'question_id': 'success_metrics',
                'question_text': 'What are your key success metrics?',
                'response_type': 'text',
                'response_value': 'North Star Metric: Time saved per user per week (target: 10+ hours). Supporting metrics: (1) Weekly active users (target: 80% of paid users), (2) AI prediction accuracy (target: 85%), (3) Net Promoter Score (target: 50+), (4) Customer retention (target: 90% monthly), (5) Time to value (target: <5 minutes from signup to first insight). Tracking with Mixpanel + custom analytics.'
            },
            {
                'section_id': 'user_testing',
                'question_id': 'testing_approach',
                'question_text': 'Describe your user testing approach',
                'response_type': 'text',
                'response_value': 'Multi-phase testing: (1) Alpha (completed) - 5 companies, 8-20 people each, 6 weeks, weekly feedback calls, fixed 47 bugs. (2) Beta (current) - 15 companies, structured feedback surveys, NPS tracked, measuring time savings. (3) Early access (next) - 50 companies, self-serve signup, reduce hand-holding, optimize onboarding. Running usability tests with UserTesting.com (10 sessions/month), session recordings with Hotjar.'
            },
            {
                'section_id': 'user_feedback',
                'question_id': 'feedback_summary',
                'question_text': 'Summarize key user feedback',
                'response_type': 'text',
                'response_value': 'Positive: "Finally, a PM tool that works for us, not the other way around" (NPS 9), "The AI predictions are surprisingly accurate" (4/5 teams), "Saved us from missing a deadline" (2 reported instances). Negative: "Wish it integrated with Jira" (60% request), "Learning curve for AI features" (training needed), "Pricing too high for small teams" (added cheaper tier). Overall NPS: 72 (excellent for beta).'
            },
            {
                'section_id': 'iteration_plan',
                'question_id': 'iteration_strategy',
                'question_text': 'How will you iterate based on feedback?',
                'response_type': 'text',
                'response_value': 'Weekly ship cycle: Ship small improvements every Friday. Prioritization framework: P0 (blocks usage) - fix immediately, P1 (top 3 feature requests) - next sprint, P2 (nice-to-have) - backlog. Key planned iterations: (1) Jira integration (top request), (2) Mobile notifications for urgent predictions, (3) Customizable AI sensitivity, (4) Better onboarding (3-minute video + interactive tour). Using Canny for feature voting.'
            }
        ]
        
        self._create_responses(assessment.id, responses)
        print(f"✅ Product Concept Testing: 100% ({len(responses)} responses)")
    
    def _create_business_development(self, user_id):
        """
        Business Development - Growth and sales strategy
        """
        assessment = self._get_or_create_assessment(
            user_id,
            'Business Development',
            100
        )
        
        responses = [
            {
                'section_id': 'growth_strategy',
                'question_id': 'customer_acquisition',
                'question_text': 'What is your customer acquisition strategy?',
                'response_type': 'text',
                'response_value': 'Product-led growth as primary channel: (1) Freemium - 3 users free forever, 80% of new signups start here. (2) Virality - Invite teammates, Slack integration creates awareness. (3) Content - 2 blog posts/week on remote work productivity, 5K organic visitors/month. (4) Community - Active in r/remotework, Indie Hackers, Product Hunt. (5) Partnerships - Co-marketing with Slack, GitHub. Target CAC: $2,000, payback period: 10 months.'
            },
            {
                'section_id': 'growth_strategy',
                'question_id': 'conversion_funnel',
                'question_text': 'Describe your conversion funnel',
                'response_type': 'text',
                'response_value': 'Signup → Activation → Paid: (1) Signup (website, Product Hunt, referral) - 100 signups/week target. (2) Activation (first AI insight within 5 minutes) - 60% activation rate, improving onboarding. (3) Engagement (3+ days usage in first week) - 40% engagement rate. (4) Paid conversion (free → paid after 14-day trial) - 15% conversion target. Current funnel: 100 signups → 60 activated → 24 engaged → 3-4 paid. Optimizing with A/B tests.'
                },
            {
                'section_id': 'sales_strategy',
                'question_id': 'sales_process',
                'question_text': 'What is your sales process?',
                'response_type': 'text',
                'response_value': 'Hybrid self-serve + high-touch: (1) Self-serve for <$10K ACV - Fully automated, credit card signup, no sales call needed. (2) High-touch for >$10K ACV - Sales-assisted for 50+ user deals, custom demos, security reviews, contract negotiations. Sales cycle: 2 weeks (self-serve) to 6 weeks (enterprise). Currently founder-led sales, hiring first AE at 100 customers. Using HubSpot CRM, Calendly for demos.'
            },
            {
                'section_id': 'partnerships',
                'question_id': 'partnership_strategy',
                'question_text': 'What partnerships are you pursuing?',
                'response_type': 'text',
                'response_value': 'Three partnership tiers: (1) Integration partners - Slack (official app directory listing), GitHub (OAuth integration), Notion (API partner). Benefits: Co-marketing, featured placement. (2) Reseller partners - Looking at partnering with Fractional CTO agencies who can recommend us. 20% commission. (3) Strategic partners - Discussing with remote work consultants, productivity coaches who can be affiliates. Target: 5 active partnerships generating 20% of new customers by end of year 1.'
            },
            {
                'section_id': 'retention_strategy',
                'question_id': 'customer_retention',
                'question_text': 'How will you retain customers?',
                'response_type': 'text',
                'response_value': 'Multi-pronged retention strategy: (1) Product stickiness - Daily usage habit through Slack integration, network effects as more team joins. (2) Customer success - Proactive outreach at days 3, 7, 30, quarterly business reviews for large accounts. (3) Continuous value - Ship new features monthly, AI improves with usage. (4) Community - User Slack group, monthly webinars, case studies. Target: 95% monthly retention (typical for SMB SaaS is 90%), <5% annual churn.'
            },
            {
                'section_id': 'expansion_strategy',
                'question_id': 'revenue_expansion',
                'question_text': 'How will you expand revenue per customer?',
                'response_type': 'text',
                'response_value': 'Net Revenue Retention target: 120% through: (1) Seat expansion - Start with 5-user pilot, expand to full team (30-50 users) within 6 months as they see value. (2) Tier upgrades - Free → Starter → Professional. 30% of Starter customers upgrade to Professional for advanced AI. (3) Add-on features - Future premium features: Custom AI models ($500/mo), priority support ($200/mo), advanced analytics ($300/mo). Currently seeing 15% MoM growth from existing customers.'
            }
        ]
        
        self._create_responses(assessment.id, responses)
        print(f"✅ Business Development: 100% ({len(responses)} responses)")
    
    def _create_prototype_testing(self, user_id):
        """
        Business Prototype Testing - Validation and iteration
        """
        assessment = self._get_or_create_assessment(
            user_id,
            'Business Prototype Testing',
            100
        )
        
        responses = [
            {
                'section_id': 'prototype_status',
                'question_id': 'current_status',
                'question_text': 'What is your current prototype status?',
                'response_type': 'text',
                'response_value': 'Functional MVP in production with 15 beta customers (120 total users). Tech stack: Next.js 14, FastAPI Python backend, PostgreSQL, Redis, GPT-4 API, deployed on Railway (frontend) + Render (backend). Core features working: Slack integration (95% uptime), AI standup reports (generated daily for all users), risk predictions (78% accuracy so far), task board. Currently in private beta, planning public launch in 6 weeks.'
            },
            {
                'section_id': 'metrics_tracking',
                'question_id': 'key_metrics',
                'question_text': 'What are your current metrics?',
                'response_type': 'text',
                'response_value': 'Current traction (beta phase): 15 active companies, 120 total users, 92 weekly active users (77% WAU rate - excellent), 4 paying customers ($1,200 MRR), NPS of 72, average 8 hours/week time savings (measured via survey), 85% of teams say they would "very disappointed" if we shut down (strong PMF signal), 6 referrals generated organically, 0 churn so far (only 2 months live). API uptime: 99.2%.'
            },
            {
                'section_id': 'testing_insights',
                'question_id': 'learning_insights',
                'question_text': 'What have you learned from testing?',
                'response_type': 'text',
                'response_value': 'Critical insights: (1) AI accuracy threshold - Users forgive 80% accuracy but abandon at 70%. We are at 78%, need to hit 85%. (2) Onboarding is key - Teams that complete setup in <5 minutes have 3x retention. Added interactive tour. (3) Slack-first works - 90% of engagement happens in Slack, web dashboard is secondary. (4) Pricing learning - $89/user too high for early-stage startups, added $49 tier. (5) Enterprise needs - 2 customers need SOC2, starting compliance process.'
            },
            {
                'section_id': 'validation_evidence',
                'question_id': 'pmf_evidence',
                'question_text': 'What evidence do you have of product-market fit?',
                'response_type': 'text',
                'response_value': 'Strong PMF signals: (1) Sean Ellis test - 85% would be "very disappointed" if product disappeared (>40% = PMF). (2) Organic growth - 6 referrals without asking, 3 companies signed up from word-of-mouth. (3) Paid conversion - 4/15 beta customers started paying before we asked. (4) Usage intensity - 77% weekly active users, typical SaaS is 30-40%. (5) Retention - 0 churn in 2 months. (6) Qualitative - "I cannot imagine going back" feedback from multiple users.'
            },
            {
                'section_id': 'iteration_priorities',
                'question_id': 'next_steps',
                'question_text': 'What are your immediate next steps?',
                'response_type': 'text',
                'response_value': '6-week plan to public launch: Week 1-2: Improve AI accuracy to 85% (retrain model on more data). Week 3: Add Jira integration (top feature request). Week 4: Build self-serve onboarding flow (reduce founder involvement). Week 5: Create pricing page, payment flow (using Stripe), billing dashboard. Week 6: Product Hunt launch, press outreach, scale to 50 customers. Post-launch: Hire co-founder CTO, raise pre-seed round ($500K), scale to $10K MRR in 3 months.'
            },
            {
                'section_id': 'future_vision',
                'question_id': 'scaling_plan',
                'question_text': 'What is your plan to scale from prototype to product?',
                'response_type': 'text',
                'response_value': 'Three-phase scale plan: Phase 1 (Months 1-6, Post-launch): Reach 100 customers ($30K MRR), prove playbook for growth, hire co-founder. Milestones: Product Hunt #1, first $10K MRR month, 500 signups. Phase 2 (Months 7-12, Scale): Raise pre-seed ($500K), hire 2 engineers + 1 CS, reach $100K MRR, 1,000 paying users. Milestones: Break-even unit economics, proven CAC/LTV. Phase 3 (Year 2, Hypergrowth): Raise seed ($2-3M), team of 8, reach $1M ARR. Milestones: Enterprise customers, international expansion, API platform.'
            }
        ]
        
        self._create_responses(assessment.id, responses)
        print(f"✅ Business Prototype Testing: 100% ({len(responses)} responses)")
    
    def _get_or_create_assessment(self, user_id, phase_name, progress):
        """
        Get existing assessment or create new one
        """
        # Map phase names to phase IDs
        phase_id_map = {
            'Self Discovery Assessment': 'self_discovery',
            'Idea Discovery Assessment': 'idea_discovery',
            'Market Research': 'market_research',
            'Business Pillars Planning': 'business_pillars',
            'Product Concept Testing': 'product_concept_testing',
            'Business Development': 'business_development',
            'Business Prototype Testing': 'business_prototype_testing'
        }
        
        phase_id = phase_id_map.get(phase_name, 'self_discovery')
        
        assessment = self.session.query(Assessment).filter_by(
            user_id=user_id,
            phase_name=phase_name
        ).first()
        
        if assessment:
            assessment.progress_percentage = progress
            assessment.updated_at = datetime.utcnow()
        else:
            assessment = Assessment(
                user_id=user_id,
                phase_id=phase_id,
                phase_name=phase_name,
                progress_percentage=progress
            )
            self.session.add(assessment)
        
        self.session.commit()
        return assessment
    
    def _create_responses(self, assessment_id, responses):
        """
        Create or update assessment responses
        """
        for resp_data in responses:
            existing = self.session.query(AssessmentResponse).filter_by(
                assessment_id=assessment_id,
                question_id=resp_data['question_id']
            ).first()
            
            if existing:
                existing.response_value = resp_data['response_value']
                existing.updated_at = datetime.utcnow()
            else:
                response = AssessmentResponse(
                    assessment_id=assessment_id,
                    section_id=resp_data['section_id'],
                    question_id=resp_data['question_id'],
                    question_text=resp_data['question_text'],
                    response_type=resp_data['response_type'],
                    response_value=resp_data['response_value']
                )
                self.session.add(response)
        
        self.session.commit()
    
    def export_to_json(self, user_id, filename='complete_user_data.json'):
        """
        Export user data to JSON file
        """
        try:
            user = self.session.query(User).filter_by(id=user_id).first()
            if not user:
                print(f"❌ User {user_id} not found")
                return None
            
            export_data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'assessments': []
            }
            
            assessments = self.session.query(Assessment).filter_by(user_id=user_id).all()
            
            for assessment in assessments:
                responses = self.session.query(AssessmentResponse).filter_by(
                    assessment_id=assessment.id
                ).all()
                
                assessment_data = {
                    'phase_name': assessment.phase_name,
                    'progress_percentage': assessment.progress_percentage,
                    'responses': [
                        {
                            'section_id': r.section_id,
                            'question_id': r.question_id,
                            'question_text': r.question_text,
                            'response_type': r.response_type,
                            'response_value': r.response_value
                        }
                        for r in responses
                    ]
                }
                export_data['assessments'].append(assessment_data)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Exported to {filename}")
            return export_data
            
        except Exception as e:
            print(f"❌ Export error: {str(e)}")
            return None
