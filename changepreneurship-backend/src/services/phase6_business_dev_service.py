"""
Phase 6 Business Development Service — Sprint 12
=================================================
CEO Section 6: "Can we build the necessary business components so the venture can actually function?"

Responsibilities:
- Assess operational readiness from collected responses
- Generate the Personalized Venture Environment (Phase 6 deliverable)
- Recommend: proceed to prototype / revise components / seek professional support / pause

CEO deliverable components:
  - Venture summary
  - Business plan summary
  - Financial model overview
  - Go-to-market approach
  - Operations plan
  - Risk register
  - 30/60/90-day roadmap
  - Component status list

Phase 6 blocks progress if:
  - critical documents incomplete
  - financial model incoherent
  - legal/tax risk unresolved
  - operations impossible for founder capacity
  - business components contradict earlier evidence
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────

REQUIRED_FOR_SUBMIT = (
    'bd-s1-1',  # venture summary
    'bd-s1-2',  # core value proposition
    'bd-s2-1',  # revenue model
    'bd-s3-1',  # first customer / launch approach
    'bd-s4-1',  # legal / structure decision
)

# Component readiness weights for overall score
COMPONENT_WEIGHTS = {
    'venture_summary':   15,
    'financial_model':   20,
    'go_to_market':      20,
    'operations':        15,
    'legal_compliance':  15,
    'risk_register':     10,
    'roadmap':           5,
}

READINESS_THRESHOLDS = {
    'HIGH':     75,
    'MODERATE': 50,
    'LOW':      25,
}

VALID_DECISIONS = (
    'PROCEED_TO_PROTOTYPE',
    'REVISE_COMPONENTS',
    'SEEK_PROFESSIONAL_SUPPORT',
    'PAUSE_AND_VALIDATE',
)

DECISION_RATIONALE = {
    'PROCEED_TO_PROTOTYPE': (
        'Venture components are sufficiently coherent and complete. '
        'You are ready to begin controlled real-world prototype testing.'
    ),
    'REVISE_COMPONENTS': (
        'Some components are incomplete or contradictory. '
        'Revise the flagged areas before moving to prototype testing.'
    ),
    'SEEK_PROFESSIONAL_SUPPORT': (
        'Legal, financial, or operational gaps require professional input. '
        'Address these with qualified advisors before proceeding.'
    ),
    'PAUSE_AND_VALIDATE': (
        'Core assumptions or components are still unresolved. '
        'Pause and validate key decisions before building further infrastructure.'
    ),
}


class Phase6BusinessDevService:
    """Assesses Phase 6 responses and generates the Personalized Venture Environment."""

    # ── Readiness assessment ─────────────────────────────────────────────────

    def assess_readiness(self, responses: dict) -> dict:
        """
        Score venture readiness from 0-100 across components.

        Returns:
          readiness_score:  0-100
          readiness_level:  HIGH | MODERATE | LOW | CRITICAL
          components:       dict of component_name → {score, status, notes}
          blockers:         list of identified blockers
          recommendation:   short recommendation
        """
        components = {}
        blockers   = []

        # Venture summary (15pts)
        summary_score = 0
        if _filled(responses, 'bd-s1-1'): summary_score += 8
        if _filled(responses, 'bd-s1-2'): summary_score += 7
        components['venture_summary'] = {
            'score': summary_score,
            'max': 15,
            'status': _status(summary_score, 15),
        }
        if summary_score < 8:
            blockers.append('Venture summary incomplete')

        # Financial model (20pts)
        fin_score = 0
        if _filled(responses, 'bd-s2-1'): fin_score += 7
        if _filled(responses, 'bd-s2-2'): fin_score += 7
        if _filled(responses, 'bd-s2-3'): fin_score += 6
        components['financial_model'] = {
            'score': fin_score,
            'max': 20,
            'status': _status(fin_score, 20),
        }
        if fin_score < 7:
            blockers.append('Revenue model not defined')

        # Go-to-market (20pts)
        gtm_score = 0
        if _filled(responses, 'bd-s3-1'): gtm_score += 8
        if _filled(responses, 'bd-s3-2'): gtm_score += 7
        if _filled(responses, 'bd-s3-3'): gtm_score += 5
        components['go_to_market'] = {
            'score': gtm_score,
            'max': 20,
            'status': _status(gtm_score, 20),
        }
        if gtm_score < 8:
            blockers.append('Customer acquisition approach not defined')

        # Operations (15pts)
        ops_score = 0
        if _filled(responses, 'bd-s4-2'): ops_score += 8
        if _filled(responses, 'bd-s4-3'): ops_score += 7
        components['operations'] = {
            'score': ops_score,
            'max': 15,
            'status': _status(ops_score, 15),
        }

        # Legal / compliance (15pts)
        legal_score = 0
        if _filled(responses, 'bd-s4-1'): legal_score += 10
        if _filled(responses, 'bd-s4-4'): legal_score += 5
        components['legal_compliance'] = {
            'score': legal_score,
            'max': 15,
            'status': _status(legal_score, 15),
        }
        legal_text = (responses.get('bd-s4-1') or '').lower()
        if any(w in legal_text for w in ('unresolved', 'unclear', 'unsure', 'unknown', 'no idea')):
            blockers.append('Legal/tax structure unresolved')

        # Risk register (10pts)
        risk_score = 0
        if _filled(responses, 'bd-s5-1'): risk_score += 5
        if _filled(responses, 'bd-s5-2'): risk_score += 5
        components['risk_register'] = {
            'score': risk_score,
            'max': 10,
            'status': _status(risk_score, 10),
        }

        # Roadmap (5pts)
        road_score = 0
        if _filled(responses, 'bd-s5-3'): road_score += 5
        components['roadmap'] = {
            'score': road_score,
            'max': 5,
            'status': _status(road_score, 5),
        }

        total = sum(c['score'] for c in components.values())
        max_total = sum(c['max'] for c in components.values())
        readiness_score = int(total / max_total * 100)

        if readiness_score >= READINESS_THRESHOLDS['HIGH']:
            level = 'HIGH'
        elif readiness_score >= READINESS_THRESHOLDS['MODERATE']:
            level = 'MODERATE'
        elif readiness_score >= READINESS_THRESHOLDS['LOW']:
            level = 'LOW'
        else:
            level = 'CRITICAL'

        return {
            'readiness_score': readiness_score,
            'readiness_level': level,
            'components':      components,
            'blockers':        blockers,
            'recommendation':  self._recommendation(level, blockers),
        }

    # ── Generate deliverable ─────────────────────────────────────────────────

    def generate_environment(self, venture, responses: dict) -> dict:
        """Generate the full Personalized Venture Environment deliverable."""
        readiness = self.assess_readiness(responses)
        decision  = self._decide(readiness['readiness_level'], readiness['blockers'])

        return {
            'venture_summary': {
                'description':       responses.get('bd-s1-1', ''),
                'value_proposition': responses.get('bd-s1-2', ''),
                'target_customer':   responses.get('bd-s1-3', ''),
                'unique_advantage':  responses.get('bd-s1-4', ''),
            },
            'financial_model': {
                'revenue_model':     responses.get('bd-s2-1', ''),
                'pricing_approach':  responses.get('bd-s2-2', ''),
                'cost_assumptions':  responses.get('bd-s2-3', ''),
                'runway_funding':    responses.get('bd-s2-4', ''),
            },
            'go_to_market': {
                'first_customers':   responses.get('bd-s3-1', ''),
                'acquisition_channels': responses.get('bd-s3-2', ''),
                'launch_milestones': responses.get('bd-s3-3', ''),
                'partnerships':      responses.get('bd-s3-4', ''),
            },
            'operations': {
                'legal_structure':   responses.get('bd-s4-1', ''),
                'key_processes':     responses.get('bd-s4-2', ''),
                'tools_systems':     responses.get('bd-s4-3', ''),
                'professional_support': responses.get('bd-s4-4', ''),
            },
            'risk_register': {
                'top_risks':         responses.get('bd-s5-1', ''),
                'mitigation_plan':   responses.get('bd-s5-2', ''),
            },
            'roadmap': {
                'next_30_days':      responses.get('bd-s5-3', ''),
                'next_60_days':      responses.get('bd-s5-4', ''),
                'next_90_days':      responses.get('bd-s5-5', ''),
            },
            'component_status':    readiness['components'],
            'readiness_score':     readiness['readiness_score'],
            'readiness_level':     readiness['readiness_level'],
            'blockers':            readiness['blockers'],
            'decision':            decision,
            'decision_rationale':  DECISION_RATIONALE.get(decision, ''),
            'operational_ready':   decision == 'PROCEED_TO_PROTOTYPE',
            'generated_at':        datetime.utcnow().isoformat(),
        }

    # ── Validate ──────────────────────────────────────────────────────────────

    def validate_for_submit(self, responses: dict) -> tuple[bool, str]:
        for qid in REQUIRED_FOR_SUBMIT:
            val = responses.get(qid, '')
            if not val or (isinstance(val, str) and not val.strip()):
                return False, f"Required question not answered: {qid}"
        return True, ''

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _decide(level: str, blockers: list) -> str:
        if level == 'HIGH' and len(blockers) == 0:
            return 'PROCEED_TO_PROTOTYPE'
        if level in ('HIGH', 'MODERATE') and len(blockers) <= 1:
            return 'REVISE_COMPONENTS'
        legal_issues = any('legal' in b.lower() or 'tax' in b.lower() for b in blockers)
        if legal_issues:
            return 'SEEK_PROFESSIONAL_SUPPORT'
        if level in ('LOW', 'CRITICAL'):
            return 'PAUSE_AND_VALIDATE'
        return 'REVISE_COMPONENTS'

    @staticmethod
    def _recommendation(level: str, blockers: list) -> str:
        if level == 'HIGH' and not blockers:
            return 'Venture infrastructure is ready. Proceed to Prototype Testing.'
        if level == 'HIGH':
            return 'Strong foundation. Address remaining blockers before prototype testing.'
        if level == 'MODERATE':
            return 'Good progress. Fill gaps in financial model and go-to-market before proceeding.'
        if level == 'LOW':
            return 'Several key components missing. Focus on revenue model and first-customer strategy.'
        return 'Critical gaps identified. Pause and address foundational components first.'


# ── Helpers ────────────────────────────────────────────────────────────────

def _filled(responses: dict, key: str) -> bool:
    val = responses.get(key)
    return bool(val and str(val).strip())


def _status(score: int, max_score: int) -> str:
    pct = score / max_score if max_score else 0
    if pct >= 0.9:
        return 'COMPLETE'
    if pct >= 0.5:
        return 'PARTIAL'
    return 'MISSING'
