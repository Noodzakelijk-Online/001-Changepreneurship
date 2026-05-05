"""
Create alex_foundr — full E2E demo user with all 7 phases completed.

Venture: InvoiceFlow — B2B SaaS for freelancer invoice automation
Founder profile: Strong readiness, CONTINUE route

Run inside backend container:
  docker exec changepreneurship-backend python create_alex_foundr.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from src.main import app
from src.models.assessment import db, User, Assessment, AssessmentResponse, UserSession
from src.models.founder_profile import FounderReadinessProfile, PhaseGate, initialize_phase_gates
from src.models.venture_record import VentureRecord, EvidenceItem
from src.models.market_research import CompetitorEntry, MarketContext, MarketValidityReport
from src.models.business_pillars import BusinessPillarsData, BusinessPillarsBlueprint
from src.models.concept_testing import ConceptTestData, ConceptTestResult
from src.models.business_development import BusinessDevData, VentureEnvironment
from src.models.prototype_testing import PrototypeTestData, PrototypeTestResult
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def run():
    with app.app_context():
        # ── Cleanup existing ──────────────────────────────────────────────
        existing = User.query.filter_by(username='alex_foundr').first()
        if existing:
            uid_old = existing.id
            print(f'Removing existing alex_foundr (id={uid_old})')
            from sqlalchemy import text
            with db.engine.connect() as conn:
                with conn.begin():
                    # Delete child rows first (deepest dependencies first)
                    conn.execute(text(
                        'DELETE FROM assessment_response WHERE assessment_id IN '
                        f'(SELECT id FROM assessment WHERE user_id = {uid_old})'
                    ))
                    conn.execute(text(f'DELETE FROM assessment WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM phase_gate WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM founder_readiness_profile WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM prototype_test_result WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM prototype_test_data WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM venture_environment WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM business_dev_data WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM concept_test_result WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM concept_test_data WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM business_pillars_blueprint WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM business_pillars_data WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM market_validity_report WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM market_context WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM competitor_entry WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM evidence_item WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM blocker_event WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM user_action WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM user_session WHERE user_id = {uid_old}'))
                    # entrepreneur_profile may exist
                    try:
                        conn.execute(text(f'DELETE FROM entrepreneur_profile WHERE user_id = {uid_old}'))
                    except Exception:
                        pass
                    conn.execute(text(f'DELETE FROM venture_record WHERE user_id = {uid_old}'))
                    conn.execute(text(f'DELETE FROM "user" WHERE id = {uid_old}'))

        # ── Create user ───────────────────────────────────────────────────
        user = User(
            username='alex_foundr',
            email='alex@invoiceflow.io',
            password_hash=generate_password_hash('Alex2026!'),
            created_at=datetime.utcnow() - timedelta(days=90),
        )
        db.session.add(user)
        db.session.flush()
        uid = user.id
        print(f'[OK] User created: alex_foundr  id={uid}  password=Alex2026!')

        # ── Session token ─────────────────────────────────────────────────
        session = UserSession(
            user_id=uid,
            session_token='alex-demo-token-2026',
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=365),
        )
        db.session.add(session)

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 1 — Self-Discovery + FounderReadinessProfile
        # ═══════════════════════════════════════════════════════════════════
        a1 = Assessment(
            user_id=uid, phase_id='self_discovery',
            phase_name='Self Discovery Assessment',
            progress_percentage=100.0, is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=88),
            completed_at=datetime.utcnow() - timedelta(days=85),
        )
        db.session.add(a1)
        db.session.flush()

        for qid, section, question, value in [
            ('primary_motivation', 'motivation', 'Why do you want to start?',
             'I believe freelancer invoicing is fundamentally broken. I spent 3 years as a freelance designer losing 20% of my time to admin. I want to build a tool that gives that time back.'),
            ('success_vision', 'motivation', 'What does success look like?',
             'InvoiceFlow becomes the default invoicing layer for 50,000 European freelancers within 3 years. €2M ARR, profitable, no VC.'),
            ('core_strengths', 'strengths', 'What are your top strengths?',
             'Product design (8 years), B2B SaaS GTM (3 years at a fintech), customer discovery, copywriting.'),
            ('risk_tolerance', 'readiness', 'Risk tolerance?', '4'),
            ('backup_plan', 'readiness', 'Financial safety net?',
             '14 months runway saved. No dependents. Part-time consulting 2 days/week to extend runway. Wife is supportive and employed.'),
            ('weekly_hours', 'capacity', 'Hours per week available?', '30'),
            ('stress_handling', 'resilience', 'How do you handle stress?',
             'I meditate daily, exercise 4x/week. I have been through a failed startup before — I know the signs of burnout and I protect against it deliberately.'),
            ('primary_fear', 'fears', 'What are you most afraid of?',
             'Building something technically solid that nobody pays for. My biggest fear is beautiful product, no distribution.'),
        ]:
            db.session.add(AssessmentResponse(
                assessment_id=a1.id, section_id=section,
                question_id=qid, question_text=question,
                response_type='text' if len(value) > 3 else 'scale',
                response_value=value,
            ))

        # FounderReadinessProfile
        frp = FounderReadinessProfile(
            user_id=uid, version=1, is_latest=True,
            financial_readiness_score=78, financial_readiness_level=2,
            time_capacity_score=82, time_capacity_level=2,
            personal_stability_score=85, personal_stability_level=2,
            motivation_quality_score=90, motivation_quality_level=1,
            skills_experience_score=88, skills_experience_level=1,
            idea_clarity_score=75, idea_clarity_level=2,
            founder_idea_fit_score=92, founder_idea_fit_level=1,
            strategic_position_score=80, strategic_position_level=2,   # legal_employment
            evidence_quality_score=84, evidence_quality_level=2,        # health_energy
            founder_market_fit_score=89, founder_market_fit_level=1,
            market_validity_score=72, market_validity_level=2,
            business_model_score=70, business_model_level=2,
            network_mentorship_score=65, network_mentorship_level=3,
            overall_readiness_level=2,
            recommended_route='CONTINUE',
            founder_type='A',
            detected_scenario='EXPERIENCED_PROFESSIONAL',
            active_blockers=[],
            compensation_rules_applied=[],
            burnout_signal_detected=False,
            overload_signal_detected=False,
            ai_narrative=(
                'Alex shows strong founder-market fit for InvoiceFlow. 8 years of product design '
                'combined with lived freelancer pain is a rare combination. Financial runway of 14 months '
                'provides adequate time to validate without pressure. The main risk is distribution — '
                'technical skills are strong but a go-to-market co-founder or advisor would reduce risk significantly. '
                'Phase 2 should focus on sharpening the specific customer segment and validating willingness to pay '
                'before any product development begins.'
            ),
        )
        db.session.add(frp)

        # Phase gates
        initialize_phase_gates(uid)
        db.session.flush()

        gate1 = PhaseGate.query.filter_by(user_id=uid, phase_number=1).first()
        if gate1:
            gate1.status = 'IN_PROGRESS'

        print('[OK] Phase 1 complete — FRP created, gates initialized')

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 2 — Idea Discovery + VentureRecord
        # ═══════════════════════════════════════════════════════════════════
        a2 = Assessment(
            user_id=uid, phase_id='idea_discovery',
            phase_name='Idea Discovery',
            progress_percentage=100.0, is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=80),
            completed_at=datetime.utcnow() - timedelta(days=75),
        )
        db.session.add(a2)
        db.session.flush()

        for qid, section, question, value in [
            ('idea_raw', 'idea', 'Describe your idea',
             'InvoiceFlow — automated invoice and payment management for European freelancers. Send invoices, chase payments, handle VAT, connect to bank accounts. No accountant needed for the first €100K.'),
            ('problem_statement', 'idea', 'What problem does it solve?',
             'European freelancers spend 6-10 hours per month on invoicing, payment chasing, and VAT calculation. 40% have at least one unpaid invoice per year. Existing tools are either too complex (QuickBooks) or too basic (Word templates).'),
            ('target_user', 'customer', 'Who is the customer?',
             'Freelance designers, developers, consultants, and coaches in Germany, Netherlands, and UK. B2B work, €2,000–€10,000 monthly revenue. Self-employed, VAT-registered, working alone or with 1-2 contractors.'),
            ('value_proposition', 'value', 'What is your value proposition?',
             'The only invoicing tool that chases late payments automatically, calculates VAT in real-time, and connects to your bank — so you never think about admin again.'),
            ('differentiation', 'competition', 'How is this different?',
             'FreshBooks and Harvest are for teams. Wave is US-focused with no VAT. Bonsai is US-only. Our differentiation: EU VAT native, automatic payment chasing via email+WhatsApp, and bank account reconciliation included in the €15/month base plan.'),
            ('revenue_hypothesis', 'business', 'How will you make money?',
             'SaaS subscription. €15/month solo plan, €35/month with bank connection. Target: 5,000 users = €75K MRR. Year 1 goal: 500 paying users, break even.'),
        ]:
            db.session.add(AssessmentResponse(
                assessment_id=a2.id, section_id=section,
                question_id=qid, question_text=question,
                response_type='text', response_value=value,
            ))

        venture = VentureRecord(
            user_id=uid, version=1, is_active=True,
            idea_raw='InvoiceFlow — automated invoicing for European freelancers',
            idea_clarified=(
                'B2B SaaS platform for European freelancers (designers, developers, consultants) '
                'that automates invoice creation, VAT calculation, payment chasing via email/WhatsApp, '
                'and bank account reconciliation. Replaces manual admin costing 6-10h/month. '
                'Base plan €15/month. Primary markets: Germany, Netherlands, UK.'
            ),
            problem_statement=(
                'Freelancers in Europe spend 6-10 hours/month on invoice admin. '
                '40% have at least 1 unpaid invoice per year. Existing tools are either too complex or not EU-native.'
            ),
            target_user_hypothesis='Freelance designers, developers, consultants in EU earning €2K-€10K/month',
            value_proposition=(
                'The only invoicing tool that chases late payments automatically, '
                'handles EU VAT in real-time, and connects to your bank — '
                'so you never think about admin again.'
            ),
            venture_type='FORPROFIT',
            status='CLARIFIED',
            assumptions=[
                {'id': 'a1', 'text': 'Freelancers will pay €15/month to save 6h/month', 'status': 'VALIDATED', 'evidence_count': 3},
                {'id': 'a2', 'text': 'Automatic payment chasing is the #1 requested feature', 'status': 'VALIDATED', 'evidence_count': 5},
                {'id': 'a3', 'text': 'WhatsApp payment reminders outperform email reminders', 'status': 'TESTING', 'evidence_count': 1},
                {'id': 'a4', 'text': 'Bank connection integration is table stakes by 2025', 'status': 'UNTESTED', 'evidence_count': 0},
                {'id': 'a5', 'text': 'German market is easiest entry due to freelancer density', 'status': 'VALIDATED', 'evidence_count': 2},
            ],
            open_questions=[
                'Should we start with Germany or Netherlands first?',
                'Is WhatsApp business API feasible at €15/month price point?',
                'What is the realistic CAC from SEO vs product-led growth?',
            ],
        )
        db.session.add(venture)
        db.session.flush()
        vid = venture.id

        gate2 = PhaseGate.query.filter_by(user_id=uid, phase_number=2).first()
        if gate2:
            gate2.status = 'IN_PROGRESS'

        print(f'[OK] Phase 2 complete — VentureRecord id={vid}')

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 3 — Market Research
        # ═══════════════════════════════════════════════════════════════════
        a3 = Assessment(
            user_id=uid, phase_id='market_research',
            phase_name='Market Research',
            progress_percentage=100.0, is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=70),
            completed_at=datetime.utcnow() - timedelta(days=55),
        )
        db.session.add(a3)

        # Evidence items
        evidence_items = [
            ('CUSTOMER_INTERVIEW', 'ANECDOTAL',
             '12 customer interviews with freelancers in Germany and NL. '
             '10/12 confirmed they spend 5+ hours/month on invoicing. '
             '8/12 said they would pay €10-€20/month for full automation.',
             'Direct customer interviews', 3),
            ('PAYING_CUSTOMER', 'DEFINITIVE',
             '3 freelancers agreed to pay €15/month for 3-month beta access. '
             'Total: €135 pre-revenue. All 3 are active product testers.',
             'Beta signups with payment', 5),
            ('MARKET_RESEARCH', 'SUGGESTIVE',
             'EU freelancer market: 28M freelancers, 4.3M in DACH+Benelux+UK. '
             'Invoicing software segment €1.2B in Europe growing at 11% CAGR.',
             'Statista + Eurostat data', 4),
            ('EXPERT_INTERVIEW', 'SUGGESTIVE',
             'Spoke with a DATEV accountant partner. Confirmed that 60-70% of '
             'their freelancer clients use Excel or Word for invoicing. Strong pull-through opportunity.',
             'DATEV partner call', 4),
            ('COMPETITOR_GAP', 'SUGGESTIVE',
             'Bonsai, FreshBooks, Harvest: all US-focused. None handle EU VAT natively. '
             'Holvi handles banking but not invoicing automation. Clear gap confirmed.',
             'Competitor product analysis', 3),
            ('FAILED_SALE', 'ANECDOTAL',
             '2 interviewees said they would not switch from their current Excel system '
             'because they fear data loss. Onboarding and data migration must be frictionless.',
             'Interview notes', 2),
        ]
        for etype, strength, desc, source, _q in evidence_items:
            e = EvidenceItem(
                venture_id=vid, user_id=uid,
                evidence_type=etype, strength=strength,
                description=desc, source=source,
                evidence_date=datetime.utcnow() - timedelta(days=60),
            )
            db.session.add(e)

        # Competitors
        for name, desc, strong, weak, pos, direct in [
            ('FreshBooks', 'US invoicing SaaS, SMB-focused',
             'Brand recognition, integrations ecosystem', 'No EU VAT, no WhatsApp, expensive',
             'Full accounting for small teams', True),
            ('Bonsai', 'US-focused freelancer contracts + invoicing',
             'All-in-one (contracts+invoices)', 'US-only, no EU VAT, no bank connection',
             'Contract management first', True),
            ('Holvi', 'EU fintech bank account for freelancers',
             'Real EU bank account, great UX', 'No automated payment chasing, no VAT automation',
             'Banking-first, invoicing secondary', True),
            ('Wave', 'Free US invoicing tool',
             'Free tier, good UX', 'No EU VAT, USD-focused, weak automation',
             'Free alternative, US market', False),
            ('DATEV', 'German accounting software for professionals',
             'Market leader in Germany, tax-compliant', 'Complex, expensive, for accountants not founders',
             'Professional accounting suite', False),
        ]:
            db.session.add(CompetitorEntry(
                user_id=uid, venture_id=vid,
                name=name, description=desc,
                strengths=strong, weaknesses=weak,
                positioning=pos, is_direct=direct,
            ))

        # Market context
        mc = MarketContext(
            user_id=uid, venture_id=vid,
            target_segment='EU freelancers: designers, developers, consultants earning €2K-€10K/month',
            pain_intensity='HIGH',
            willingness_to_pay=True,
            estimated_price_range='€10-€25/month',
            market_timing='Strong: remote work growth post-2020, EU VAT reform forcing compliance, bank-open-data directives (PSD2)',
            market_size_note='4.3M target segment in DACH+Benelux+UK. Even 1% = 43,000 users = €645K MRR at €15/month.',
        )
        db.session.add(mc)

        # Market validity report
        mvr = MarketValidityReport(
            user_id=uid, venture_id=vid,
            report_data={
                'verdict': 'PROCEED',
                'evidence_score': 74,
                'pain_score': 88,
                'market_size_score': 72,
                'competition_gap_score': 81,
                'timing_score': 85,
                'summary': (
                    'InvoiceFlow has strong market evidence. Direct customer interviews, paying beta users, '
                    'confirmed competitor gap in EU VAT automation, and favourable macro timing (PSD2, remote work). '
                    'Main risk: go-to-market — no clear acquisition channel yet beyond warm network.'
                ),
                'strengths': [
                    '3 paying beta customers — strongest possible early evidence',
                    'Clear competitor gap: no EU-native invoicing automation exists',
                    'Strong pain: 10/12 interviewees confirmed 5+ hours/month lost',
                    'Market timing: PSD2 + EU VAT reform creates urgency',
                ],
                'risks': [
                    'CAC unknown — no paid channel tested yet',
                    'WhatsApp business API cost may compress margin at base price',
                    'German market may require DSGVO-specific data handling (adds engineering cost)',
                ],
                'recommended_next': 'Phase 4 Business Pillars — define revenue model, pricing tiers, and cost structure before product development.',
            },
        )
        db.session.add(mvr)

        gate3 = PhaseGate.query.filter_by(user_id=uid, phase_number=3).first()
        if gate3:
            gate3.status = 'IN_PROGRESS'

        print('[OK] Phase 3 complete — Market Validity Report, 6 evidence items, 5 competitors')

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 4 — Business Pillars
        # ═══════════════════════════════════════════════════════════════════
        a4 = Assessment(
            user_id=uid, phase_id='business_pillars',
            phase_name='Business Pillars Planning',
            progress_percentage=100.0, is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=50),
            completed_at=datetime.utcnow() - timedelta(days=42),
        )
        db.session.add(a4)

        pillars_content = {
            'value_proposition': (
                'Automated invoice lifecycle management for EU freelancers. Send → chase → reconcile. '
                'EU VAT included. No accountant needed for first €100K revenue. Save 6-8 hours/month.'
            ),
            'customer_structure': (
                'User = Payer = Solo freelancer (designer/developer/consultant). '
                'B2C acquisition via product-led growth, SEO, freelancer communities. '
                'Target: 500 paying users by month 12.'
            ),
            'revenue_model': 'SUBSCRIPTION',
            'cost_structure': (
                'Phase 1 (0-500 users): Founder + 1 part-time dev. '
                'COGS: Stripe fees 2.9%, WhatsApp Business API €0.005/message, hosting €150/month. '
                'Target gross margin: 82%. Break-even: €4,500 MRR.'
            ),
            'delivery_model': (
                'Web app (React + Python backend). Mobile-first responsive design. '
                'Bank connection via Nordigen/GoCardless Open Banking API. '
                'WhatsApp via Twilio Business API. Hosted on Hetzner EU (DSGVO-compliant).'
            ),
            'market_positioning': (
                'The EU freelancer invoicing tool that actually chases payments for you. '
                'Positioning: we are not accounting software — we are your invoice autopilot. '
                'Primary SEO: "invoice app for freelancers Germany", "automatische Mahnung freiberufler".'
            ),
            'operations': (
                'Solo founder + 1 part-time backend dev. Customer support via Intercom. '
                'Product iterations every 2 weeks. Monthly user interview cadence. '
                'Legal: GmbH registered in Germany, DSGVO-compliant data processing.'
            ),
            'legal_structure': (
                'UG (haftungsbeschränkt) in Germany. VAT-registered. '
                'DSGVO data processing agreement with all sub-processors. '
                'No non-compete with current consulting clients — reviewed by lawyer.'
            ),
            'success_metrics': (
                'Month 6: 100 paying users, €1,500 MRR, NPS > 40. '
                'Month 12: 500 paying users, €7,500 MRR, churn < 5%/month. '
                'Year 2: 2,000 users, €30K MRR, hire 2nd full-time.'
            ),
            'strategic_risks': (
                '1. Distribution: no proven CAC yet — biggest unknown. '
                '2. WhatsApp API costs may be prohibitive at €15 price point — validate before building. '
                '3. FreshBooks may add EU VAT — watch for acquisition of a local player. '
                '4. Regulation: PSD2 requires licensed account information service provider — legal review needed before bank connection launch.'
            ),
        }

        pillars_data = BusinessPillarsData(
            user_id=uid, venture_id=vid,
            pillars=pillars_content, completed=True,
            updated_at=datetime.utcnow() - timedelta(days=42),
        )
        db.session.add(pillars_data)

        blueprint = BusinessPillarsBlueprint(
            user_id=uid, venture_id=vid,
            blueprint_data={
                'summary': 'InvoiceFlow has a coherent SaaS business model with strong unit economics potential.',
                'coherence_score': 84,
                'ready_for_concept_testing': True,
                'pillar_scores': {
                    'value_proposition': 90, 'customer_structure': 85, 'revenue_model': 88,
                    'cost_structure': 80, 'delivery_model': 82, 'market_positioning': 78,
                    'operations': 75, 'legal_structure': 85, 'success_metrics': 82, 'strategic_risks': 80,
                },
                'strengths': [
                    'Clean SaaS revenue model with clear path to €4.5K MRR break-even',
                    'EU-specific positioning creates defensible niche',
                    'Legal structure correctly planned (UG + DSGVO)',
                ],
                'gaps': [
                    'CAC not yet validated — critical before scaling spend',
                    'WhatsApp API cost structure needs to be tested before committing',
                ],
                'recommended_next': 'Phase 5 Concept Testing — validate the specific feature set and pricing with 15+ target users before building.',
            },
            coherence_score=84,
            ready_for_concept_testing=True,
        )
        db.session.add(blueprint)

        gate4 = PhaseGate.query.filter_by(user_id=uid, phase_number=4).first()
        if gate4:
            gate4.status = 'IN_PROGRESS'

        print('[OK] Phase 4 complete — Business Pillars + Blueprint (coherence 84/100)')

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 5 — Concept Testing
        # ═══════════════════════════════════════════════════════════════════
        a5 = Assessment(
            user_id=uid, phase_id='product_concept_testing',
            phase_name='Product Concept Testing',
            progress_percentage=100.0, is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=38),
            completed_at=datetime.utcnow() - timedelta(days=28),
        )
        db.session.add(a5)

        concept_responses = {
            'concept_statement': 'An invoicing tool that sends invoices, chases late payments automatically via email and WhatsApp, calculates EU VAT, and reconciles with your bank account.',
            'test_method': 'Showed Figma prototype to 18 freelancers (Slack communities, personal network) for 30-minute sessions.',
            'participants_count': 18,
            'positive_reactions': 15,
            'would_pay': 13,
            'price_point_test': '€15/month felt right for 11/13 who said yes. 2 said €10 max.',
            'top_requested_feature': 'Automatic payment chasing was mentioned by 14/18 — confirmed as #1 priority.',
            'objections': '3 users worried about DSGVO compliance. 2 users happy with Excel, low pain. 1 said WhatsApp feels unprofessional for B2B invoicing.',
            'key_insight': 'The pain is real and deep for active freelancers with 5+ clients. Under 3 clients, the pain is lower — narrow initial target to high-volume freelancers.',
            'next_iteration': 'Remove WhatsApp from initial pitch. Focus messaging on email chasing + VAT automation. WhatsApp as opt-in premium feature.',
        }

        concept_data = ConceptTestData(
            user_id=uid, venture_id=vid,
            responses=concept_responses, completed=True,
        )
        db.session.add(concept_data)

        concept_result = ConceptTestResult(
            user_id=uid, venture_id=vid,
            result_data={
                'adoption_signal': 'STRONG',
                'decision': 'PROCEED',
                'summary': (
                    '15/18 positive reactions (83%). 13/18 willing to pay (72%). '
                    'Price confirmation at €15. Key insight: narrow to freelancers with 5+ active clients. '
                    'WhatsApp objection noted — move to opt-in.'
                ),
                'participant_count': 18,
                'positive_count': 15,
                'pay_count': 13,
                'concept_score': 81,
                'recommended_next': 'Phase 6 Business Development — define operational structure, tooling, and launch plan.',
            },
            adoption_signal='STRONG',
            decision='PROCEED',
            ready_for_business_dev=True,
        )
        db.session.add(concept_result)

        gate5 = PhaseGate.query.filter_by(user_id=uid, phase_number=5).first()
        if gate5:
            gate5.status = 'IN_PROGRESS'

        print('[OK] Phase 5 complete — Concept Testing (83% positive, STRONG signal)')

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 6 — Business Development
        # ═══════════════════════════════════════════════════════════════════
        a6 = Assessment(
            user_id=uid, phase_id='business_development',
            phase_name='Business Development',
            progress_percentage=100.0, is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=25),
            completed_at=datetime.utcnow() - timedelta(days=15),
        )
        db.session.add(a6)

        biz_dev_responses = {
            'team_status': 'Solo founder. Part-time backend contractor hired for 20h/week at €60/h.',
            'tech_stack': 'React + Vite (frontend), Python Flask (API), PostgreSQL, Stripe, Nordigen Open Banking API, SendGrid.',
            'mvp_scope': (
                'MVP = invoice creation, PDF export, email chasing at 7/14/30 days, '
                'VAT rate calculator for DE/NL/UK. No bank connection in MVP — add in v1.1.'
            ),
            'go_to_market': (
                'Month 1-3: warm network (10 beta users). '
                'Month 3-6: 3 freelancer Slack communities (EU Design Slack, DevBerlin, IndieHackers). '
                'Month 6+: SEO (target: "invoice app freelancer Germany") + Product Hunt launch.'
            ),
            'first_customers': (
                '3 beta users already paying €15/month. '
                'Pipeline: 12 warm contacts who expressed interest after prototype test.'
            ),
            'pricing_finalized': '€15/month Solo (invoicing + email chasing + VAT). €29/month Pro (+ bank connection, WhatsApp opt-in).',
            'support_system': 'Intercom for customer support. Notion for internal docs. Linear for bug tracking.',
            'legal_done': 'UG registered. DSGVO data processing agreements with Stripe, Nordigen, SendGrid signed. Terms + Privacy policy live.',
            'financial_model': (
                'Month 6 target: 100 users = €1,500 MRR. '
                'Break-even: €4,500 MRR (350 users). '
                'Current runway: 14 months × €2,000/month burn = €28K. '
                'Will hit break-even before runway ends at current growth assumption (50 users/month from month 4).'
            ),
        }

        biz_dev_data = BusinessDevData(
            user_id=uid, venture_id=vid,
            responses=biz_dev_responses, completed=True,
        )
        db.session.add(biz_dev_data)

        venture_env = VentureEnvironment(
            user_id=uid, venture_id=vid,
            environment_data={
                'summary': 'InvoiceFlow is operationally ready for a controlled beta launch.',
                'readiness_score': 82,
                'decision': 'PROCEED_TO_PROTOTYPE',
                'systems_ready': ['invoicing', 'payment_chasing', 'vat_calculation', 'stripe', 'legal'],
                'systems_pending': ['bank_connection', 'whatsapp', 'seo_content'],
                'team_gaps': ['Growth/marketing expertise — consider part-time GTM advisor'],
                'immediate_actions': [
                    'Launch to 3 paying beta users this week',
                    'Schedule weekly feedback call with beta users',
                    'Publish first 3 SEO articles (freelancer invoicing Germany)',
                    'Apply to 2 freelancer communities as featured tool',
                ],
            },
            readiness_score=82,
            operational_ready=True,
            decision='PROCEED_TO_PROTOTYPE',
        )
        db.session.add(venture_env)

        gate6 = PhaseGate.query.filter_by(user_id=uid, phase_number=6).first()
        if gate6:
            gate6.status = 'IN_PROGRESS'

        print('[OK] Phase 6 complete — Venture Environment (readiness 82/100)')

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 7 — Prototype Testing
        # ═══════════════════════════════════════════════════════════════════
        a7 = Assessment(
            user_id=uid, phase_id='business_prototype_testing',
            phase_name='Business Prototype Testing',
            progress_percentage=100.0, is_completed=True,
            started_at=datetime.utcnow() - timedelta(days=12),
            completed_at=datetime.utcnow() - timedelta(days=3),
        )
        db.session.add(a7)

        proto_responses = {
            'real_users_tested': '8 paying beta users after 30-day trial period.',
            'revenue_generated': '€375 total in 30 days (8 users × €15 + 3 users on Pro tier at €29). MRR: €315.',
            'retention': '7/8 users renewed for month 2. 1 churned (moved to Bonsai, had US clients).',
            'nps_score': 52,
            'top_user_quote': '"I got my first overdue invoice paid automatically last week — I did nothing. That is literally magic." — Marta K., freelance designer, Berlin.',
            'operational_issues': (
                'PDF export formatting breaks on some VAT edge cases. '
                'Email chasing queue sometimes delayed by 2-3 hours. Fixing in v0.3.'
            ),
            'cac_measurement': 'Current CAC from warm network: ~€0 (referrals). First paid experiment (€100 LinkedIn ad): 3 signups, 1 conversion. CAC = €100. Needs work.',
            'unit_economics': 'LTV at current churn (12.5%): €120. CAC from paid = €100. LTV:CAC = 1.2x. Need to reach 3:1 before scaling spend.',
            'key_learning': 'Product works. Retention works. Distribution is the constraint. Focus next 3 months exclusively on CAC reduction.',
            'scale_readiness': 'Not ready to scale spend. Ready to continue growing organically and test 2 more channels (SEO, freelancer communities).',
        }

        proto_data = PrototypeTestData(
            user_id=uid, venture_id=vid,
            responses=proto_responses, completed=True,
        )
        db.session.add(proto_data)

        proto_result = PrototypeTestResult(
            user_id=uid, venture_id=vid,
            result_data={
                'summary': (
                    '7/8 users retained after 30 days. NPS 52. €315 MRR confirmed. '
                    'Product validated. Unit economics need improvement before scaling. '
                    'CAC from organic: €0. CAC from paid: €100. LTV:CAC = 1.2x.'
                ),
                'scale_readiness': 'MODERATE',
                'scale_score': 71,
                'decision': 'FIX_DISTRIBUTION',
                'key_metrics': {
                    'users': 8,
                    'mrr': 315,
                    'retention_30d': 87.5,
                    'nps': 52,
                    'ltv_cac_ratio': 1.2,
                },
                'recommended_next': (
                    'Validated product, strong retention. '
                    'Constraint is distribution. Test 3 channels: '
                    '(1) SEO for "invoice app freelancer [city]", '
                    '(2) freelancer community partnerships, '
                    '(3) referral program (give 1 month free per referral). '
                    'Return to scale decision at 50 MRR users.'
                ),
            },
            scale_readiness='MODERATE',
            scale_score=71,
            decision='FIX_DISTRIBUTION',
            ready_to_scale=False,
        )
        db.session.add(proto_result)

        gate7 = PhaseGate.query.filter_by(user_id=uid, phase_number=7).first()
        if gate7:
            gate7.status = 'IN_PROGRESS'

        print('[OK] Phase 7 complete — Prototype Test (scale_score 71, FIX_DISTRIBUTION)')

        # ═══════════════════════════════════════════════════════════════════
        # Mark all phase gates COMPLETED (full demo user has done all 7)
        # ═══════════════════════════════════════════════════════════════════
        db.session.flush()
        from datetime import timedelta as td
        for pg in PhaseGate.query.filter_by(user_id=uid).all():
            pg.status = 'COMPLETED'
            # Approximate completion dates spaced out over 90 days
            offset_days = {1: 85, 2: 75, 3: 55, 4: 40, 5: 25, 6: 10, 7: 2}
            pg.completed_at = pg.completed_at or (
                __import__('datetime').datetime.utcnow()
                - td(days=offset_days.get(pg.phase_number, 5))
            )
        print('[OK] All 7 phase gates set to COMPLETED')

        # ═══════════════════════════════════════════════════════════════════
        # Commit everything
        # ═══════════════════════════════════════════════════════════════════
        db.session.commit()

        # Force all assessments to is_completed=True, progress=100 via raw SQL
        # (Some phase-submit routes recalculate progress from response counts)
        from sqlalchemy import text as sqlt
        with db.engine.connect() as conn:
            with conn.begin():
                conn.execute(sqlt(
                    f"UPDATE assessment SET is_completed = TRUE, progress_percentage = 100.0 "
                    f"WHERE user_id = {uid}"
                ))
        print('[OK] Forced all 7 assessments to is_completed=True, progress=100%')

        print()
        print('═' * 60)
        print('alex_foundr created successfully!')
        print('═' * 60)
        print(f'  username : alex_foundr')
        print(f'  password : Alex2026!')
        print(f'  email    : alex@invoiceflow.io')
        print(f'  user_id  : {uid}')
        print(f'  venture  : InvoiceFlow (id={vid})')
        print()
        print('All 7 phases completed:')
        print('  Ph1  Self-Discovery      FRP + Phase Gates initialized')
        print('  Ph2  Idea Discovery      VentureRecord created')
        print('  Ph3  Market Research     MVR + 6 evidence + 5 competitors')
        print('  Ph4  Business Pillars    Blueprint coherence 84/100')
        print('  Ph5  Concept Testing     STRONG signal, 83% positive')
        print('  Ph6  Business Dev        Venture Environment, operational 82/100')
        print('  Ph7  Prototype Testing   315 MRR, NPS 52, FIX_DISTRIBUTION')
        print()
        print('Login at: http://localhost  (or your configured domain)')
        print()


if __name__ == '__main__':
    run()
