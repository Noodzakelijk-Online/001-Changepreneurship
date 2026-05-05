"""
Phase 7 Business Prototype Testing Service — Sprint 13
=======================================================
CEO mandate: "Does the venture work when real people, money, operations, and constraints are involved?"

6 sections:
  pt-s1-* Traction Evidence
  pt-s2-* Conversion & Sales
  pt-s3-* Delivery & Operations
  pt-s4-* Financial Reality
  pt-s5-* Customer Response
  pt-s6-* Founder Performance

Scale readiness signals: STRONG | MODERATE | WEAK | NONE
Decisions: SCALE_CAREFULLY | FIX_OPERATIONS | REVISE_PRICING | REVISE_CUSTOMER |
           REVISE_PRODUCT | SEEK_FUNDING | REMAIN_STABLE | PIVOT | PAUSE | STOP
"""
from datetime import datetime

# ── Required IDs to unlock submit ────────────────────────────────────────────
REQUIRED_FOR_SUBMIT = {
    'pt-s1-1',   # traction_type
    'pt-s2-1',   # outreach_count
    'pt-s3-1',   # delivery_success
    'pt-s4-1',   # revenue_achieved
    'pt-s5-1',   # customer_satisfaction
}

# ── Scale readiness scoring components ────────────────────────────────────────
def assess_scale_readiness(responses: dict) -> dict:
    """
    Score prototype test responses across 6 components.
    Returns: { signal, score, components, blockers }
    """
    score = 0
    blockers = []
    components = {}

    # 1. Traction (20 pts)
    traction_type = responses.get('pt-s1-1', '')
    traction_count_raw = responses.get('pt-s1-2', '0')
    try:
        traction_count = int(str(traction_count_raw))
    except (ValueError, TypeError):
        traction_count = 0

    if traction_type in ('paying_customers', 'pilot_contracts', 'signed_agreements'):
        t_score = 20
    elif traction_type in ('active_users', 'signups', 'partnerships'):
        t_score = 14
    elif traction_type in ('interest_expressed', 'meetings_held'):
        t_score = 7
    else:
        t_score = 0

    if traction_count >= 3:
        t_score = min(t_score + 5, 20)

    if traction_type == '' or traction_count == 0:
        blockers.append('No meaningful traction evidence recorded')

    components['traction'] = t_score
    score += t_score

    # 2. Conversion & Sales (15 pts)
    outreach_raw = responses.get('pt-s2-1', '0')
    converted_raw = responses.get('pt-s2-2', '0')
    try:
        outreach = max(int(str(outreach_raw)), 1)
        converted = int(str(converted_raw))
    except (ValueError, TypeError):
        outreach = 1
        converted = 0

    conversion_rate = converted / outreach
    if conversion_rate >= 0.20:
        c_score = 15
    elif conversion_rate >= 0.10:
        c_score = 10
    elif conversion_rate >= 0.03:
        c_score = 5
    else:
        c_score = 0
        if converted == 0:
            blockers.append('Zero conversions from outreach — model not validated')

    components['conversion'] = c_score
    score += c_score

    # 3. Delivery & Operations (15 pts)
    delivery_success = responses.get('pt-s3-1', '')
    ops_issues = responses.get('pt-s3-2', '')

    if delivery_success in ('fully_delivered', 'mostly_delivered'):
        d_score = 15
    elif delivery_success == 'partially_delivered':
        d_score = 8
    else:
        d_score = 0
        blockers.append('Delivery not proven — operational risk high')

    if ops_issues and len(str(ops_issues)) > 20:
        d_score = max(d_score - 3, 0)

    components['delivery'] = d_score
    score += d_score

    # 4. Financial Reality (20 pts)
    revenue_achieved = responses.get('pt-s4-1', '')
    costs_vs_plan = responses.get('pt-s4-2', '')

    if revenue_achieved == 'above_plan':
        f_score = 20
    elif revenue_achieved == 'on_plan':
        f_score = 16
    elif revenue_achieved == 'below_plan':
        f_score = 8
    elif revenue_achieved == 'no_revenue_yet':
        f_score = 3
        blockers.append('No revenue yet — financial model unvalidated')
    else:
        f_score = 0

    if costs_vs_plan == 'over_budget':
        f_score = max(f_score - 5, 0)
        blockers.append('Costs exceeded budget — financial model needs revision')

    components['financial_reality'] = f_score
    score += f_score

    # 5. Customer Response (15 pts)
    satisfaction = responses.get('pt-s5-1', '')
    repeat_interest = responses.get('pt-s5-2', '')

    if satisfaction in ('very_satisfied', 'satisfied'):
        s_score = 10
    elif satisfaction == 'neutral':
        s_score = 5
    else:
        s_score = 0
        if satisfaction == 'dissatisfied':
            blockers.append('Customer dissatisfaction — product-market fit issue')

    if repeat_interest in ('yes_repeat_customers', 'yes_referrals'):
        s_score = min(s_score + 5, 15)

    components['customer_response'] = s_score
    score += s_score

    # 6. Founder Performance (15 pts)
    follow_through = responses.get('pt-s6-1', '')
    adaptability = responses.get('pt-s6-2', '')

    if follow_through in ('completed_all', 'completed_most'):
        fp_score = 10
    elif follow_through == 'completed_some':
        fp_score = 5
    else:
        fp_score = 0
        blockers.append('Founder execution gaps detected')

    if adaptability in ('adapted_quickly', 'adapted_with_support'):
        fp_score = min(fp_score + 5, 15)

    components['founder_performance'] = fp_score
    score += fp_score

    # ── Signal classification ─────────────────────────────────────────────────
    if score >= 75:
        signal = 'STRONG'
    elif score >= 50:
        signal = 'MODERATE'
    elif score >= 25:
        signal = 'WEAK'
    else:
        signal = 'NONE'

    return {
        'signal':     signal,
        'score':      score,
        'components': components,
        'blockers':   blockers,
    }


def _decide(assessment: dict, responses: dict) -> str:
    """Map scale readiness to a recommended next decision."""
    signal = assessment['signal']
    score = assessment['score']
    blockers = assessment.get('blockers', [])
    financial = assessment['components'].get('financial_reality', 0)
    delivery = assessment['components'].get('delivery', 0)
    traction = assessment['components'].get('traction', 0)
    customer = assessment['components'].get('customer_response', 0)

    if signal == 'STRONG' and score >= 80:
        return 'SCALE_CAREFULLY'
    if signal == 'STRONG' and score >= 70:
        return 'SEEK_FUNDING'
    if signal == 'MODERATE':
        if delivery < 10:
            return 'FIX_OPERATIONS'
        if financial < 10:
            return 'REVISE_PRICING'
        if customer < 5:
            return 'REVISE_CUSTOMER'
        if traction < 10:
            return 'REVISE_PRODUCT'
        return 'REMAIN_STABLE'
    if signal == 'WEAK':
        if any('delivery' in b.lower() for b in blockers):
            return 'FIX_OPERATIONS'
        if any('financial' in b.lower() or 'revenue' in b.lower() for b in blockers):
            return 'REVISE_PRICING'
        if any('dissatisfaction' in b.lower() for b in blockers):
            return 'PIVOT'
        return 'PAUSE'
    # NONE
    return 'STOP'


def generate_report(venture: dict, responses: dict) -> dict:
    """
    Generate the full Business Prototype Test Report.
    Returns structured dict stored in PrototypeTestResult.result_data.
    """
    assessment = assess_scale_readiness(responses)
    decision = _decide(assessment, responses)
    venture_name = (venture.get('venture_name') or 'Your Venture') if venture else 'Your Venture'

    traction_type = responses.get('pt-s1-1', 'Not specified')
    revenue = responses.get('pt-s4-1', 'Not reported')

    # Build 90-day plan based on decision
    plans = {
        'SCALE_CAREFULLY': [
            'Document repeatable sales/delivery process',
            'Hire or onboard first support resource',
            'Set up basic operational dashboards and metrics',
            'Establish customer success touchpoints',
            'Define growth ceiling before major scaling',
        ],
        'FIX_OPERATIONS': [
            'Map delivery process and identify bottlenecks',
            'Test 3 delivery improvements this week',
            'Set quality threshold before next customer batch',
            'Document operational lessons from current failures',
            'Bring in operational advisor or mentor',
        ],
        'REVISE_PRICING': [
            'Review unit economics — identify margin leak',
            'Test 1-2 alternative pricing models with prospects',
            'Survey customers on willingness to pay',
            'Rebuild financial model with real cost data',
            'Set go/no-go threshold for pricing revision',
        ],
        'REVISE_CUSTOMER': [
            'Review ICP definition using real customer feedback',
            'Run 5 discovery conversations with non-converting prospects',
            'Identify which customer segments actually converted',
            'Revisit Phase 3 market research assumptions',
            'Define revised target customer profile',
        ],
        'REVISE_PRODUCT': [
            'Prioritize top 3 product objections from customers',
            'Build minimum revision scope (what to change)',
            'Run rapid test of revision with 3 existing customers',
            'Update Phase 5 product concept data',
            'Set clear acceptance criteria for the revision',
        ],
        'SEEK_FUNDING': [
            'Prepare traction deck with evidence from prototype phase',
            'Define funding use: operations, growth, or team',
            'Identify 10 target investors, grants, or partners',
            'Build 6-month financial model with funding assumptions',
            'Set pitch-ready milestone: date and criteria',
        ],
        'REMAIN_STABLE': [
            'Identify what is working and protect it',
            'Stabilize delivery and operations',
            'Grow cautiously within current capacity',
            'Collect more evidence before any major moves',
            'Set 3-month review checkpoint',
        ],
        'PIVOT': [
            'Document what the current model proved and failed',
            'Return to Phase 2/3 to revise concept with real evidence',
            'Identify pivot hypothesis: what changes, what stays',
            'Test pivot direction with 3 quick customer conversations',
            'Set pivot validation criteria within 30 days',
        ],
        'PAUSE': [
            'Stop spending without validated return',
            'Review all evidence collected and document lessons',
            'Identify the single biggest unresolved assumption',
            'Plan a structured pause: 2–4 weeks, focused reflection',
            'Set conditions that must be met before resuming',
        ],
        'STOP': [
            'Document all learnings — evidence, decisions, outcomes',
            'Assess what skills and knowledge transfer to next venture',
            'Formally close open commitments (customers, suppliers)',
            'Review financial position and runway',
            'Consider whether an early-stage restart makes sense',
        ],
    }
    next_90_days = plans.get(decision, plans['PAUSE'])

    return {
        'generated_at':   datetime.utcnow().isoformat(),
        'venture_name':   venture_name,
        'phase':          'business_prototype_testing',
        'title':          'Business Prototype Test Report',

        'scale_readiness': assessment['signal'],
        'scale_score':     assessment['score'],
        'decision':        decision,

        'prototype_summary': {
            'traction_type':   traction_type,
            'revenue_status':  revenue,
            'components':      assessment['components'],
            'blockers':        assessment['blockers'],
        },

        'what_worked':      _extract_strengths(assessment),
        'what_broke':       assessment['blockers'],
        'what_must_change': _extract_changes(decision, assessment),

        'operational_lessons': _operational_summary(responses, assessment),
        'financial_reality':   _financial_summary(responses, assessment),
        'founder_analysis':    _founder_summary(responses, assessment),

        'next_90_day_plan': next_90_days,
        'recommended_mode': _mode_label(decision),

        'ready_to_scale': assessment['signal'] in ('STRONG', 'MODERATE') and len(assessment['blockers']) == 0,
    }


def _extract_strengths(assessment: dict) -> list:
    strengths = []
    c = assessment['components']
    if c.get('traction', 0) >= 14:
        strengths.append('Strong traction evidence collected')
    if c.get('conversion', 0) >= 10:
        strengths.append('Healthy conversion rate from outreach')
    if c.get('delivery', 0) >= 12:
        strengths.append('Delivery process proved viable')
    if c.get('financial_reality', 0) >= 14:
        strengths.append('Revenue matching or exceeding plan')
    if c.get('customer_response', 0) >= 10:
        strengths.append('Positive customer response and repeat interest')
    if c.get('founder_performance', 0) >= 12:
        strengths.append('Founder demonstrated strong execution and adaptability')
    if not strengths:
        strengths.append('Prototype phase completed — real-world evidence collected')
    return strengths


def _extract_changes(decision: str, assessment: dict) -> list:
    changes_map = {
        'SCALE_CAREFULLY': ['Monitor unit economics at scale', 'Build team capacity before scaling'],
        'FIX_OPERATIONS': ['Delivery process must be redesigned', 'Operational capacity needs reinforcement'],
        'REVISE_PRICING': ['Pricing model does not reflect real costs/value', 'Financial model requires rebuilding'],
        'REVISE_CUSTOMER': ['Target customer segment needs redefinition', 'ICP must be validated with evidence'],
        'REVISE_PRODUCT': ['Product/service must address key objections', 'Core value proposition needs clarification'],
        'SEEK_FUNDING': ['Build pitch materials with traction evidence', 'Define funding strategy and targets'],
        'REMAIN_STABLE': ['Avoid premature scaling', 'Focus on consistency and quality'],
        'PIVOT': ['Core model does not work — fundamental revision required', 'Return to discovery/validation phases'],
        'PAUSE': ['Unresolved assumptions must be addressed before continuing', 'Avoid further spend without validation'],
        'STOP': ['Venture model is not viable in current form', 'Preserve learnings for future ventures'],
    }
    return changes_map.get(decision, ['Review all components and set clear next steps'])


def _operational_summary(responses: dict, assessment: dict) -> dict:
    return {
        'delivery_status':   responses.get('pt-s3-1', 'Not reported'),
        'operational_issues': responses.get('pt-s3-2', 'None reported'),
        'delivery_score':    assessment['components'].get('delivery', 0),
        'assessment':        'Viable' if assessment['components'].get('delivery', 0) >= 12 else 'Needs work',
    }


def _financial_summary(responses: dict, assessment: dict) -> dict:
    return {
        'revenue_vs_plan': responses.get('pt-s4-1', 'Not reported'),
        'costs_vs_plan':   responses.get('pt-s4-2', 'Not reported'),
        'financial_score': assessment['components'].get('financial_reality', 0),
        'assessment':      'Validated' if assessment['components'].get('financial_reality', 0) >= 14 else 'Unvalidated',
    }


def _founder_summary(responses: dict, assessment: dict) -> dict:
    return {
        'follow_through': responses.get('pt-s6-1', 'Not reported'),
        'adaptability':   responses.get('pt-s6-2', 'Not reported'),
        'fp_score':       assessment['components'].get('founder_performance', 0),
        'assessment':     'Strong executor' if assessment['components'].get('founder_performance', 0) >= 12
                          else 'Execution gaps identified',
    }


def _mode_label(decision: str) -> str:
    labels = {
        'SCALE_CAREFULLY':  'Controlled growth',
        'FIX_OPERATIONS':   'Operations fix before growth',
        'REVISE_PRICING':   'Pricing/financial revision',
        'REVISE_CUSTOMER':  'Customer segment revision',
        'REVISE_PRODUCT':   'Product/service revision',
        'SEEK_FUNDING':     'Funding',
        'REMAIN_STABLE':    'Stable operation',
        'PIVOT':            'Pivot',
        'PAUSE':            'Structured pause',
        'STOP':             'Stop',
    }
    return labels.get(decision, 'Review')


def validate_for_submit(responses: dict) -> tuple:
    """Returns (is_valid: bool, message: str)."""
    missing = [qid for qid in REQUIRED_FOR_SUBMIT if not responses.get(qid)]
    if missing:
        return False, f"Missing required responses: {', '.join(missing)}"
    return True, 'OK'
