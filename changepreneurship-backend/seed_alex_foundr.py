"""
seed_alex_foundr.py
====================
Creates alex_foundr with ALL 7 phases completed, a full venture record,
all phase deliverables, and all 7 phase gates unlocked/completed.

Run inside the running backend container:
    docker exec changepreneurship-backend python seed_alex_foundr.py

Credentials:
    username:  alex_foundr
    email:     alex@changepreneurship.app
    password:  AlexFounder2025!
    token:     alex-foundr-demo-token-2025
"""
import os, sys
from datetime import datetime, timedelta, date

sys.path.insert(0, os.path.dirname(__file__))

from werkzeug.security import generate_password_hash

USERNAME       = "alex_foundr"
EMAIL          = "alex@changepreneurship.app"
PASSWORD       = "AlexFounder2025!"
SESSION_TOKEN  = "alex-foundr-demo-token-2025"
SESSION_DAYS   = 365


def run():
    from src.main import app
    from sqlalchemy import text

    with app.app_context():
        from src.models.assessment import db, User, UserSession, Assessment, AssessmentResponse, EntrepreneurProfile
        from src.models.venture_record import VentureRecord, EvidenceItem
        from src.models.founder_profile import FounderReadinessProfile, PhaseGate, initialize_phase_gates
        from src.models.market_research import CompetitorEntry, MarketContext, MarketValidityReport
        from src.models.business_pillars import BusinessPillarsData, BusinessPillarsBlueprint
        from src.models.concept_testing import ConceptTestData, ConceptTestResult
        from src.models.business_development import BusinessDevData, VentureEnvironment
        from src.models.prototype_testing import PrototypeTestData, PrototypeTestResult

        # ── 0. Wipe existing user ──────────────────────────────────────────────
        existing = User.query.filter(
            (User.username == USERNAME) | (User.email == EMAIL)
        ).first()

        if existing:
            uid = existing.id
            print(f"[seed] Wiping existing user id={uid}")
            # Delete in FK dependency order (no cascades in SQLite)
            with db.engine.connect() as conn:
                conn.execute(text("DELETE FROM assessment_response WHERE assessment_id IN (SELECT id FROM assessment WHERE user_id=:u)"), {"u": uid})
                conn.execute(text("DELETE FROM assessment WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM entrepreneur_profile WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM evidence_item WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM competitor_entry WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM market_context WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM market_validity_report WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM business_pillars_data WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM business_pillars_blueprint WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM concept_test_data WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM concept_test_result WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM business_dev_data WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM venture_environment WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM prototype_test_data WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM prototype_test_result WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM founder_readiness_profile WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM phase_gate WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM user_action WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM user_session WHERE user_id=:u"), {"u": uid})
                conn.execute(text("DELETE FROM venture_record WHERE user_id=:u"), {"u": uid})
                conn.execute(text('DELETE FROM "user" WHERE id=:u'), {"u": uid})
                conn.commit()
            print("[seed] Wipe done.")

        # ── 1. Create user ─────────────────────────────────────────────────────
        user = User(
            username=USERNAME,
            email=EMAIL,
            password_hash=generate_password_hash(PASSWORD),
        )
        db.session.add(user)
        db.session.flush()
        uid = user.id
        print(f"[seed] Created user id={uid}")

        # EntrepreneurProfile (basic)
        db.session.add(EntrepreneurProfile(user_id=uid))

        # Session
        stale = UserSession.query.filter_by(session_token=SESSION_TOKEN).first()
        if stale:
            db.session.delete(stale)
        db.session.add(UserSession(
            user_id=uid,
            session_token=SESSION_TOKEN,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=SESSION_DAYS),
        ))

        # ── 2. Venture Record ──────────────────────────────────────────────────
        venture = VentureRecord(
            user_id=uid,
            is_active=True,
            status='CLARIFIED',
            venture_type='FORPROFIT',
            idea_raw='A SaaS platform that automates invoice generation and payment follow-up for freelancers',
            idea_clarified='FreelanceFlow — automated invoicing, payment reminders, and cash-flow forecasting for solo freelancers who hate admin work',
            problem_statement='Freelancers lose 5-8 hours per month on invoicing and chasing payments, which reduces billable hours and creates unpredictable cash flow',
            target_user_hypothesis='Solo freelancers aged 25-40 in design, writing, and consulting who earn €2k-8k/month and currently use spreadsheets or nothing',
            value_proposition='FreelanceFlow sends invoices automatically at project completion, sends 3 smart reminders, and shows a 90-day cash-flow forecast — saving 6 hours/month per user',
            founder_motivation_summary='Alex has been a freelancer for 3 years and personally lost €4,200 in unpaid invoices. The problem is lived, not assumed.',
            assumptions=[
                {'id': 'a1', 'text': 'Freelancers will pay €19/month to save 6h of admin', 'tested': True, 'result': 'CONFIRMED'},
                {'id': 'a2', 'text': 'Stripe integration is sufficient — no bank API needed', 'tested': True, 'result': 'CONFIRMED'},
                {'id': 'a3', 'text': 'Email reminders reduce late payments by >40%', 'tested': True, 'result': 'CONFIRMED'},
                {'id': 'a4', 'text': 'B2B agencies will buy team licenses at €49/month', 'tested': False, 'result': None},
            ],
            open_questions=[
                {'id': 'q1', 'text': 'Will freelancers trust automated reminders without manual override?'},
                {'id': 'q2', 'text': 'GDPR compliance requirements for storing client payment data?'},
            ],
        )
        db.session.add(venture)
        db.session.flush()
        vid = venture.id
        print(f"[seed] Created venture id={vid}")

        # ── 3. Evidence Items ──────────────────────────────────────────────────
        evidence = [
            EvidenceItem(user_id=uid, venture_id=vid, evidence_type='USER_INTERVIEW',
                         strength='STRONG', is_validated=True,
                         description='12 in-depth interviews with freelancers (30-60 min each). All 12 confirmed invoicing/chasing is top-3 pain point.',
                         source='User interviews — Feb 2026', evidence_date=date(2026, 2, 15),
                         affects_dimensions=['market_validity', 'founder_market_fit']),
            EvidenceItem(user_id=uid, venture_id=vid, evidence_type='PAYMENT',
                         strength='STRONG', is_validated=True,
                         description='8 users pre-paid €19/month for early access before any product existed.',
                         source='Stripe pre-sales — Mar 2026', evidence_date=date(2026, 3, 1),
                         affects_dimensions=['market_validity', 'business_model']),
            EvidenceItem(user_id=uid, venture_id=vid, evidence_type='SURVEY',
                         strength='MODERATE', is_validated=True,
                         description='Survey of 84 freelancers: 67% spend 4+ hours/month on invoicing. 51% said they would pay for automation.',
                         source='Typeform survey — Jan 2026', evidence_date=date(2026, 1, 20),
                         affects_dimensions=['market_validity']),
            EvidenceItem(user_id=uid, venture_id=vid, evidence_type='PROTOTYPE_TEST',
                         strength='STRONG', is_validated=True,
                         description='6 beta users tested MVP for 4 weeks. Average 5.8h saved per month. NPS 72.',
                         source='MVP beta test — Apr 2026', evidence_date=date(2026, 4, 10),
                         affects_dimensions=['market_validity', 'business_model', 'founder_market_fit']),
            EvidenceItem(user_id=uid, venture_id=vid, evidence_type='EXPERT_OPINION',
                         strength='MODERATE', is_validated=False,
                         description='Spoke with 2 accountants who said their freelancer clients frequently ask for automated invoicing solutions.',
                         source='Expert conversations — Feb 2026', evidence_date=date(2026, 2, 28),
                         affects_dimensions=['market_validity']),
        ]
        for e in evidence:
            db.session.add(e)

        # ── 4. Founder Readiness Profile (Phase 1 result) ─────────────────────
        frp = FounderReadinessProfile(
            user_id=uid, version=1, is_latest=True,
            # Dimensions (score 0-100, level 0=Healthy…5=HardStop)
            financial_readiness_score=78,  financial_readiness_level=1,
            time_capacity_score=70,        time_capacity_level=1,
            personal_stability_score=82,   personal_stability_level=0,
            motivation_quality_score=91,   motivation_quality_level=0,
            skills_experience_score=85,    skills_experience_level=0,
            founder_idea_fit_score=88,     founder_idea_fit_level=0,
            founder_market_fit_score=86,   founder_market_fit_level=0,
            idea_clarity_score=80,         idea_clarity_level=0,
            market_validity_score=83,      market_validity_level=0,
            business_model_score=75,       business_model_level=1,
            legal_employment_score=90,     legal_employment_level=0,
            health_energy_score=80,        health_energy_level=0,
            network_mentorship_score=65,   network_mentorship_level=2,
            overall_readiness_level=1,
            recommended_route='ACCELERATE',
            founder_type='A',
            detected_scenario='EXPERIENCED_PROFESSIONAL',
            active_blockers=[],
            compensation_rules_applied=['STRONG_MISSION_OFFSETS_LOW_NETWORK'],
            burnout_signal=False,
            overload_signal=False,
            ai_narrative=(
                "Alex demonstrates strong founder-market fit built on lived experience rather than assumption. "
                "The combination of genuine pain (lost €4,200 to unpaid invoices), specific target user "
                "knowledge, and early pre-sales evidence places this venture in an accelerated readiness state. "
                "The primary watch area is network and mentorship — Alex should actively seek one advisor "
                "with SaaS go-to-market experience in the next 60 days. Financial runway of 14 months "
                "provides adequate buffer for the first product cycle."
            ),
            ai_confidence='HIGH',
        )
        db.session.add(frp)

        # ── 5. Phase Gates ─────────────────────────────────────────────────────
        db.session.flush()  # ensure frp is written before gates
        initialize_phase_gates(uid)
        db.session.flush()

        all_gates = PhaseGate.query.filter_by(user_id=uid).all()
        for g in all_gates:
            if g.phase_number == 1:
                g.status = 'COMPLETED'
                g.completed_at = datetime.utcnow() - timedelta(days=45)
            elif g.phase_number == 2:
                g.status = 'COMPLETED'
                g.completed_at = datetime.utcnow() - timedelta(days=35)
            elif g.phase_number == 3:
                g.status = 'COMPLETED'
                g.completed_at = datetime.utcnow() - timedelta(days=25)
            elif g.phase_number == 4:
                g.status = 'COMPLETED'
                g.completed_at = datetime.utcnow() - timedelta(days=15)
            elif g.phase_number == 5:
                g.status = 'COMPLETED'
                g.completed_at = datetime.utcnow() - timedelta(days=8)
            elif g.phase_number == 6:
                g.status = 'COMPLETED'
                g.completed_at = datetime.utcnow() - timedelta(days=3)
            elif g.phase_number == 7:
                g.status = 'IN_PROGRESS'
        print(f"[seed] Phase gates configured")

        # ── 6. Assessment records (all 7 phases completed) ────────────────────
        phase_configs = [
            ('self_discovery',       'Self Discovery Assessment',         45),
            ('idea_discovery',       'Idea Discovery Assessment',          35),
            ('market_research',      'Market Research',                    25),
            ('business_pillars',     'Business Pillars Planning',          15),
            ('product_concept_testing', 'Product Concept Testing',          8),
            ('business_development', 'Business Development',                3),
            ('prototype_testing',    'Business Prototype Testing',          0),
        ]

        for phase_id, phase_name, days_ago in phase_configs:
            a = Assessment(
                user_id=uid,
                phase_id=phase_id,
                phase_name=phase_name,
                is_completed=True,
                progress_percentage=100.0,
                completed_at=datetime.utcnow() - timedelta(days=days_ago),
            )
            db.session.add(a)

        print(f"[seed] Assessment records created")

        # ── 7. Market Research data ────────────────────────────────────────────
        db.session.add(CompetitorEntry(
            user_id=uid, venture_id=vid,
            name='FreshBooks', description='Established invoicing for small businesses',
            strengths='Brand recognition, accountant integrations', weaknesses='Too complex for solo freelancers, €25+/month',
            positioning='SMB accounting platform', is_direct=False,
        ))
        db.session.add(CompetitorEntry(
            user_id=uid, venture_id=vid,
            name='Wave', description='Free invoicing with payment processing',
            strengths='Free tier, simple UI', weaknesses='No automation, US-centric, slow support',
            positioning='Free tool for micro-businesses', is_direct=True,
        ))
        db.session.add(CompetitorEntry(
            user_id=uid, venture_id=vid,
            name='Invoice Ninja', description='Open source invoicing tool',
            strengths='Flexible, self-hostable', weaknesses='Complex setup, no smart reminders, no forecasting',
            positioning='Technical freelancer tool', is_direct=True,
        ))

        db.session.add(MarketContext(
            user_id=uid, venture_id=vid,
            target_segment='Solo freelancers 25-40 in design/writing/consulting, EU+UK, earning €2k-8k/month',
            pain_intensity='HIGH',
            willingness_to_pay=True,
            estimated_price_range='€15-25/month',
            market_timing='Strong: freelancer economy growing 15%/year; GDPR + late payment regulation increasing compliance burden',
            market_size_note='~4M solo freelancers in EU earning above €20k/year. TAM €720M at €15/month. SAM (reachable in 2 years) ~€18M.',
        ))

        db.session.add(MarketValidityReport(
            user_id=uid, venture_id=vid,
            report_data={
                'verdict': 'VALID',
                'confidence': 'HIGH',
                'evidence_quality_score': 84,
                'evidence_breakdown': {'STRONG': 3, 'MODERATE': 2, 'WEAK': 0, 'BELIEF': 0},
                'market_size': 'addressable',
                'competition_intensity': 'MODERATE',
                'timing': 'GOOD',
                'summary': 'Market shows strong demand signals from 12 user interviews, 84-person survey, and 8 pre-sales. Competitive gap exists in smart automation layer.',
                'risks': ['Stripe dependency', 'EU payment regulation changes'],
                'opportunities': ['Agency tier upsell', 'Accountant referral channel'],
            }
        ))
        print(f"[seed] Market research data created")

        # ── 8. Business Pillars ────────────────────────────────────────────────
        pillars_data = BusinessPillarsData(
            user_id=uid, venture_id=vid, completed=True,
            pillars={
                'value_proposition': 'Saves 6h/month of admin. Predictable cash flow. Zero invoices slip through.',
                'customer_structure': 'Solo freelancers (B2C) primary. Agency teams (B2B) secondary from month 6.',
                'revenue_model': '€19/month solo plan. €49/month team plan (5 seats). Annual discount 20%.',
                'cost_structure': 'Stripe fees (2.9%), hosting €80/month, support 0.5 FTE. COGS per user ~€2.10.',
                'delivery_model': 'Web SaaS. API integrations: Stripe, PayPal, Wise. Email + Slack notifications.',
                'positioning': 'The only invoicing tool built specifically for EU solo freelancers with smart reminders built in.',
                'operations': 'Alex (product+engineering) + 1 part-time designer. Customer support async via Intercom.',
                'legal_structure': 'Estonian e-Residency OÜ. VAT registered EU. DPA signed with Stripe.',
                'metrics': 'MRR, churn, invoices sent/month, avg days to payment, NPS.',
                'strategic_risks': 'Stripe dependency. Wave adds reminder feature. Regulatory change in EU late payment directive.',
            }
        )
        db.session.add(pillars_data)

        db.session.add(BusinessPillarsBlueprint(
            user_id=uid, venture_id=vid,
            coherence_score=88,
            ready_for_concept_testing=True,
            blueprint_data={
                'summary': 'FreelanceFlow has a coherent and internally consistent business model. Revenue model aligns with target user willingness-to-pay. Cost structure is lean and achievable at €19/month price point.',
                'strengths': ['Clear ICP', 'Validated WTP', 'Low COGS', 'Single-channel focus'],
                'gaps': ['Team pricing not yet validated', 'No accounting integration yet'],
                'recommended_next': 'Move to Phase 5 concept testing with existing beta cohort.',
            }
        ))
        print(f"[seed] Business pillars created")

        # ── 9. Concept Testing ────────────────────────────────────────────────
        concept_data = ConceptTestData(
            user_id=uid, venture_id=vid, completed=True,
            responses={
                'concept_clarity': 'yes_fully',
                'problem_resonance': 5,
                'solution_appeal': 5,
                'price_reaction': 'acceptable',
                'buy_intent': 'definitely',
                'alternatives_used': 'spreadsheet_and_email',
                'switch_barrier': 'low',
                'top_feature': 'smart_reminders',
                'interview_count': 12,
                'positive_reactions': 10,
                'neutral_reactions': 2,
                'negative_reactions': 0,
                'testimonial': '"I would have paid double just to stop chasing invoices." — User 4',
            }
        )
        db.session.add(concept_data)

        db.session.add(ConceptTestResult(
            user_id=uid, venture_id=vid,
            adoption_signal='STRONG',
            decision='PROCEED',
            ready_for_business_dev=True,
            result_data={
                'adoption_score': 91,
                'signal': 'STRONG',
                'decision': 'PROCEED',
                'summary': '10/12 tested users expressed strong buy intent. Price accepted without objection at €19/month. Primary value driver: automated reminders, not invoicing.',
                'key_insight': 'Users care more about "getting paid without asking" than "creating invoices faster". Reframe messaging.',
                'risks': ['Users want bank integration (low priority now)', 'Some want recurring invoice templates'],
            }
        ))
        print(f"[seed] Concept testing created")

        # ── 10. Business Development ─────────────────────────────────────────
        biz_dev_data = BusinessDevData(
            user_id=uid, venture_id=vid, completed=True,
            responses={
                'team_status': 'solo_with_contractors',
                'product_stage': 'mvp_live',
                'revenue_status': 'pre_revenue',
                'sales_channel': 'direct_to_user',
                'customer_acquisition': 'content_seo',
                'support_model': 'async_intercom',
                'legal_status': 'registered',
                'financial_controls': 'basic_bookkeeping',
                'growth_plan': '100 users in 90 days via freelancer communities',
                'biggest_operational_risk': 'Alex is single point of failure',
            }
        )
        db.session.add(biz_dev_data)

        db.session.add(VentureEnvironment(
            user_id=uid, venture_id=vid,
            readiness_score=82,
            operational_ready=True,
            decision='PROCEED_TO_PROTOTYPE',
            environment_data={
                'summary': 'FreelanceFlow has a functional MVP, legal entity, and defined customer acquisition strategy. Single-founder risk is the primary operational concern.',
                'components_ready': ['Legal entity', 'Stripe integration', 'MVP product', 'Support channel', 'Basic financial controls'],
                'components_missing': ['Second team member', 'SEO content pipeline', 'Referral program'],
                'next_sprint': 'Launch to 30 paying users. Build referral loop. Hire first contractor (developer).',
            }
        ))
        print(f"[seed] Business development created")

        # ── 11. Prototype Testing ─────────────────────────────────────────────
        proto_data = PrototypeTestData(
            user_id=uid, venture_id=vid, completed=True,
            responses={
                'paying_users': 8,
                'mrr': 152,
                'churn_month1': 0,
                'nps': 72,
                'avg_days_to_payment': 4.2,
                'support_tickets_per_user': 0.3,
                'manual_interventions': 2,
                'top_support_reason': 'invoice PDF formatting',
                'unit_economics': 'cac_30_ltv_340',
                'biggest_operational_surprise': 'Users want to customize reminder tone/language',
            }
        )
        db.session.add(proto_data)

        db.session.add(PrototypeTestResult(
            user_id=uid, venture_id=vid,
            scale_readiness='STRONG',
            scale_score=84,
            decision='SCALE_CAREFULLY',
            ready_to_scale=True,
            result_data={
                'summary': '8 paying users, €152 MRR, 0 churn in month 1, NPS 72. Unit economics strong: CAC €30, LTV €340 (projected). Core product-market fit confirmed.',
                'scale_blockers': ['Single engineer (Alex)', 'No automated onboarding', 'No SEO pipeline yet'],
                'scale_enablers': ['Strong NPS', 'Low support load', 'Clear ICP', 'Pre-validated pricing'],
                'next_milestone': 'Reach €2,000 MRR (105 users) within 90 days.',
                'funding_note': 'Bootstrapping viable to €5k MRR. At that point, €50k angel raise becomes de-risked.',
            }
        ))
        print(f"[seed] Prototype testing created")

        # ── 12. Final commit ──────────────────────────────────────────────────
        db.session.commit()

        print()
        print("=" * 55)
        print(" alex_foundr seed complete")
        print("=" * 55)
        print(f"  Username : {USERNAME}")
        print(f"  Email    : {EMAIL}")
        print(f"  Password : {PASSWORD}")
        print(f"  Token    : {SESSION_TOKEN}")
        print(f"  User id  : {uid}")
        print(f"  Venture  : FreelanceFlow (id={vid})")
        print(f"  FRP      : route=ACCELERATE, level=1")
        print(f"  Gates    : Ph1-Ph6 COMPLETED, Ph7 IN_PROGRESS")
        print("=" * 55)


if __name__ == "__main__":
    run()
