"""
Phase 4 Business Pillars Service — Sprint 10
=============================================
CEO Section 4: "Can this idea become a coherent business?"

Responsibilities:
- Validate pillar inputs
- Assess coherence of the business model
- Generate Business Pillars Blueprint (the Phase 4 deliverable)
- Recommend: proceed / revise / more validation needed

CEO pillars:
  1. value_proposition       — what value is created and for whom
  2. customer_structure      — who uses / pays / funds / benefits
  3. revenue_model           — how money flows
  4. cost_structure          — main costs, fixed/variable, margins
  5. delivery_model          — how solution is delivered
  6. market_positioning      — differentiation
  7. operations              — key processes, resources, people
  8. legal_structure         — permits, regulations, form
  9. success_metrics         — KPIs
 10. strategic_risks         — what could break the model

Phase 4 blocks progress if:
  - no credible revenue or funding logic
  - costs make model unsustainable
  - user cannot identify who pays or funds
  - legal structure unclear in regulated area
  - operations too complex for capacity
  - model contradicts market evidence
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Pillar keys ───────────────────────────────────────────────────────────
PILLAR_KEYS = (
    'value_proposition',
    'customer_structure',
    'revenue_model',
    'cost_structure',
    'delivery_model',
    'market_positioning',
    'operations',
    'legal_structure',
    'success_metrics',
    'strategic_risks',
)

# Minimum pillars that must be non-empty to generate a blueprint
MIN_PILLARS_FOR_BLUEPRINT = 5

# Minimum pillars for a "coherent" assessment
MIN_COHERENT_PILLARS = 7

VALID_REVENUE_MODELS = (
    'SUBSCRIPTION', 'TRANSACTION', 'PRODUCT_SALES', 'SERVICE_FEES',
    'ADVERTISING', 'FREEMIUM', 'GRANT', 'DONATION', 'HYBRID', 'OTHER',
)
VALID_LEGAL_STRUCTURES = (
    'SOLE_TRADER', 'PARTNERSHIP', 'LTD', 'LLC', 'NONPROFIT',
    'SOCIAL_ENTERPRISE', 'COOPERATIVE', 'UNDECIDED', 'OTHER',
)


class Phase4PillarsService:
    """Core Phase 4 logic — stateless, all data via arguments."""

    # ───────────────────────────────────────────────────────────────────────
    # 1. Coherence assessment
    # ───────────────────────────────────────────────────────────────────────

    def assess_coherence(self, pillars: dict) -> dict:
        """
        Given a dict of {pillar_key: text}, return:
          {coherence_score: 0-100, gaps: [...], is_coherent: bool,
           recommendation: str, filled_count: int}

        CEO: Phase 4 blocks progress if there is no credible revenue/funding logic,
        or if costs make the model unsustainable.
        """
        if not pillars:
            return {
                'coherence_score': 0,
                'is_coherent': False,
                'filled_count': 0,
                'gaps': list(PILLAR_KEYS),
                'recommendation': 'START_FILLING_PILLARS',
                'critical_missing': [],
            }

        filled = [k for k in PILLAR_KEYS if (pillars.get(k) or '').strip()]
        filled_count = len(filled)
        missing = [k for k in PILLAR_KEYS if k not in filled]

        # Critical pillars — must be present to pass
        critical = ('value_proposition', 'customer_structure', 'revenue_model', 'cost_structure')
        critical_missing = [k for k in critical if k not in filled]

        # Score: base on % filled, bonus for critical pillars
        base_score = int(filled_count / len(PILLAR_KEYS) * 80)
        critical_bonus = int((len(critical) - len(critical_missing)) / len(critical) * 20)
        coherence_score = base_score + critical_bonus

        is_coherent = (
            filled_count >= MIN_COHERENT_PILLARS
            and len(critical_missing) == 0
        )

        if is_coherent:
            recommendation = 'PROCEED_TO_PHASE5'
        elif filled_count >= MIN_PILLARS_FOR_BLUEPRINT and len(critical_missing) == 0:
            recommendation = 'COMPLETE_REMAINING_PILLARS'
        elif critical_missing:
            recommendation = 'FILL_CRITICAL_PILLARS_FIRST'
        else:
            recommendation = 'START_FILLING_PILLARS'

        return {
            'coherence_score': coherence_score,
            'is_coherent': is_coherent,
            'filled_count': filled_count,
            'gaps': missing,
            'critical_missing': critical_missing,
            'recommendation': recommendation,
        }

    # ───────────────────────────────────────────────────────────────────────
    # 2. Generate Business Pillars Blueprint
    # ───────────────────────────────────────────────────────────────────────

    def generate_blueprint(
        self,
        venture_record,          # VentureRecord ORM object
        pillars: dict,           # {pillar_key: text}
        market_data: dict | None,  # MarketContext.to_dict() or None
        mvr: dict | None,          # MarketValidityReport report_data or None
    ) -> dict:
        """
        CEO: "At the end of Phase 4, the user receives a Business Pillars Blueprint."

        The blueprint includes:
          venture model summary, customer/beneficiary/funder map,
          value proposition, business/funding model, pricing/funding assumptions,
          cost and margin logic, delivery model, legal/ethical notes,
          core metrics, operational requirements, major risks,
          required business components for Phase 6,
          recommendation for concept testing.
        """
        coherence = self.assess_coherence(pillars)
        ready_for_phase5 = coherence['is_coherent']

        # Derive pricing note from market_data
        pricing_note = ''
        if market_data:
            wtp = market_data.get('willingness_to_pay', False)
            price_range = market_data.get('estimated_price_range', '')
            if wtp and price_range:
                pricing_note = f'WTP confirmed. Estimated price range: {price_range}.'
            elif wtp:
                pricing_note = 'Willingness to pay confirmed — price range not yet specified.'
            else:
                pricing_note = 'Willingness to pay not yet confirmed — test pricing assumptions in Phase 5.'

        # MVP requirement gaps
        phase6_components_needed = []
        if not (pillars.get('delivery_model') or '').strip():
            phase6_components_needed.append('Delivery model definition')
        if not (pillars.get('operations') or '').strip():
            phase6_components_needed.append('Operational plan')
        if not (pillars.get('legal_structure') or '').strip():
            phase6_components_needed.append('Legal/organisational form decision')
        if not (pillars.get('success_metrics') or '').strip():
            phase6_components_needed.append('KPIs and success metrics')

        # Evidence context from MVR
        market_validity_note = ''
        if mvr:
            score = mvr.get('validity_score', 0)
            rec = mvr.get('final_recommendation', '')
            if score >= 70:
                market_validity_note = f'Strong market validation (score {score}/100). Ready to proceed.'
            elif score >= 45:
                market_validity_note = f'Partial validation (score {score}/100). Phase 5 should address gaps.'
            else:
                market_validity_note = (
                    f'Weak market validation (score {score}/100, {rec}). '
                    'Revisit Phase 3 evidence before finalising pillars.'
                )

        return {
            'generated_at': datetime.utcnow().isoformat(),
            'venture_id': venture_record.id if venture_record else None,

            # Pillar content (pass-through with labelling)
            'venture_model_summary': pillars.get('value_proposition', ''),
            'customer_funder_map': pillars.get('customer_structure', ''),
            'value_proposition': pillars.get('value_proposition', ''),
            'business_model': pillars.get('revenue_model', ''),
            'pricing_funding_assumptions': pricing_note,
            'cost_margin_logic': pillars.get('cost_structure', ''),
            'delivery_model': pillars.get('delivery_model', ''),
            'legal_ethical_notes': pillars.get('legal_structure', ''),
            'core_metrics': pillars.get('success_metrics', ''),
            'operational_requirements': pillars.get('operations', ''),
            'major_risks': pillars.get('strategic_risks', ''),
            'market_positioning': pillars.get('market_positioning', ''),

            # Assessment
            'coherence_score': coherence['coherence_score'],
            'is_coherent': coherence['is_coherent'],
            'coherence_gaps': coherence['gaps'],
            'market_validity_context': market_validity_note,

            # Phase 6 readiness
            'required_for_phase6': phase6_components_needed,
            'recommendation_for_concept_testing': (
                'Proceed to Phase 5 — Product Concept Testing'
                if ready_for_phase5
                else 'Complete remaining business pillars before concept testing'
            ),
            'ready_for_concept_testing': ready_for_phase5,
        }

    # ───────────────────────────────────────────────────────────────────────
    # 3. Validate a single pillar update
    # ───────────────────────────────────────────────────────────────────────

    def validate_pillar_update(self, key: str, value: str) -> tuple[bool, str]:
        """Light validation before saving a pillar value."""
        if key not in PILLAR_KEYS:
            return False, f'Unknown pillar key: {key}. Must be one of: {list(PILLAR_KEYS)}'
        if not isinstance(value, str):
            return False, 'Pillar value must be a string'
        if len(value) > 5000:
            return False, f'Pillar value too long (max 5000 chars)'
        return True, ''
