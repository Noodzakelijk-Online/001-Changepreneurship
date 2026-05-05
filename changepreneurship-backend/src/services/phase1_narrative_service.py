"""
Phase 1 Narrative Service — Layer 3 (AI Reasoning)
====================================================
Generates a human-readable narrative that EXPLAINS the Layer 1
rule decisions. AI never overrides routing decisions — it only
explains and contextualises them.

Invariants:
  - Receives typed FounderReadinessProfile (not raw text)
  - Guardrails enforced before returning to caller
  - Fallback template used when AI unavailable
  - All outputs labelled with confidence level
  - NEVER says "great idea!" when hard blockers active
"""
import os
import json
import logging
from typing import Optional

from src.services.phase1_rule_engine import (
    Phase1Result,
    LEVEL_HARD_BLOCK, LEVEL_HARD_STOP, LEVEL_SOFT_BLOCK, LEVEL_WARNING,
    ROUTE_STABILIZE, ROUTE_LOW_CAPITAL, ROUTE_OPERATIONS_CLEANUP,
    ROUTE_HARD_STOP, ROUTE_IMPACT_SOCIAL, ROUTE_DEEP_TECH,
    ROUTE_DEBT_CONSCIOUS, ROUTE_CORPORATE_TRANSITION,
)

logger = logging.getLogger(__name__)

# Route → human-readable next-step explanation
_ROUTE_EXPLANATIONS = {
    ROUTE_STABILIZE: (
        "Your most important next step is to stabilise your situation before "
        "investing more energy into the venture. This is not a rejection — it "
        "is the most honest path to sustainable building."
    ),
    ROUTE_LOW_CAPITAL: (
        "A low-capital path is recommended. You can make real progress through "
        "conversations, research, and planning — none of which require spending money."
    ),
    ROUTE_OPERATIONS_CLEANUP: (
        "You already have something real. The priority now is building the systems "
        "and capacity that let you sustain and grow it without burning out."
    ),
    ROUTE_HARD_STOP: (
        "The platform has detected a situation that prevents safe guidance right now. "
        "Please review the details below and return when your situation changes."
    ),
    ROUTE_IMPACT_SOCIAL: (
        "An impact or social enterprise path is well-suited to your situation. "
        "Let us make sure your funding model is as strong as your mission."
    ),
    ROUTE_DEEP_TECH: (
        "Your technical strength is real. The priority now is translating it into "
        "commercial language — who needs this, why, and what they will pay."
    ),
    ROUTE_DEBT_CONSCIOUS: (
        "A debt-conscious restart path is recommended. You have experience and "
        "resilience. The goal is to use both without adding new financial risk."
    ),
    ROUTE_CORPORATE_TRANSITION: (
        "Your professional background is a genuine asset. The key is moving "
        "from analysis to validation — real conversations with potential customers."
    ),
    'CONTINUE': (
        "Your foundation looks solid. The next step is to deepen your idea and "
        "start gathering real-world validation."
    ),
}

# Scenario → insight note
_SCENARIO_NOTES = {
    'OVEREXCITED_BEGINNER': (
        "Your energy is clear, and that matters. The risk is that urgency leads to "
        "spending before the idea is proven. The free path is not a lesser path — "
        "it is the smarter one at this stage."
    ),
    'ACCIDENTAL_ENTREPRENEUR': (
        "You have already done the hardest thing: found people who pay you. "
        "The challenge now is building systems that let you do this sustainably."
    ),
    'DEEP_TECH_INNOVATOR': (
        "Technical depth is rare and valuable. The gap to fill is commercial translation — "
        "connecting the technology to a specific person with a specific pain."
    ),
    'IMPACT_VISIONARY': (
        "A strong mission is a real competitive advantage. To protect it long-term, "
        "your funding model needs to be as clear as your purpose."
    ),
    'FAILED_FOUNDER_RESTART': (
        "Having failed before and still choosing to build again takes real resilience. "
        "The goal is to apply what you learned — especially around costs and validation."
    ),
    'EXPERIENCED_PROFESSIONAL': (
        "Your domain knowledge is a strong foundation. The next challenge is external "
        "validation — testing your assumptions with real people, not just your network."
    ),
}


class Phase1NarrativeService:
    """
    Generates AI narrative for Phase 1 FounderReadinessProfile.
    Uses Groq (primary) with template fallback.
    """

    def __init__(self):
        self._groq_client = None

    def _get_groq_client(self):
        if self._groq_client is None:
            try:
                from groq import Groq
                self._groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            except Exception:
                pass
        return self._groq_client

    def generate_narrative(
        self,
        result: Phase1Result,
        user_responses: dict,
    ) -> dict:
        """
        Generate narrative for Phase 1 result.

        Returns:
            {
                "founder_readiness_narrative": str,
                "primary_strength": str,
                "primary_risk": str,
                "next_step_explanation": str,
                "what_not_to_do": [str],
                "confidence": str,  # SPECULATIVE|LOW|MEDIUM|HIGH
            }
        """
        # Build structured prompt input for AI
        prompt_context = self._build_prompt_context(result, user_responses)

        # Try AI generation
        ai_output = None
        try:
            ai_output = self._call_groq(prompt_context, result)
        except Exception as exc:
            logger.warning("Phase1 narrative AI call failed: %s — using template", exc)

        # Validate and apply guardrails
        if ai_output:
            ai_output = self._apply_guardrails(ai_output, result)

        if not ai_output:
            ai_output = self._generate_template_narrative(result)

        return ai_output

    def _build_prompt_context(self, result: Phase1Result, responses: dict) -> str:
        idea_desc = responses.get('idea_description', '(not provided)')
        motivation = responses.get('motivation_type', 'MIXED')
        runway = responses.get('financial_runway_months', '?')
        hours = responses.get('weekly_available_hours', '?')
        blockers_summary = '; '.join(
            b.get('reason', '') for b in result.active_blockers[:3]
        ) or 'none'

        return f"""
Founder Assessment Results (Layer 1 Rule Engine output — do NOT change these):
  Overall readiness level: {result.overall_level}/5
  Recommended route: {result.recommended_route}
  Active blockers: {blockers_summary}
  Detected scenario: {result.detected_scenario or 'none'}
  Founder type: {result.founder_type or 'unknown'}
  Financial runway: {runway} months
  Weekly available hours: {hours}
  Motivation type: {motivation}
  Idea description: {idea_desc[:200] if idea_desc else 'not provided'}
""".strip()

    def _call_groq(self, context: str, result: Phase1Result) -> Optional[dict]:
        client = self._get_groq_client()
        if not client:
            return None

        system_prompt = """You are a compassionate, direct venture-building coach.
Your job is to explain a founder's readiness assessment in honest, human language.

STRICT RULES:
1. Never say "great idea!" or "this will work" when hard blockers are active.
2. Never override or soften the routing decision — only explain it.
3. Never guarantee success or give a probability of success.
4. Always disclose uncertainty. Label assumptions as assumptions.
5. Tone: direct, non-shaming, action-oriented. Like a trusted advisor, not a cheerleader.
6. If blockers exist, acknowledge them honestly before discussing strengths.
7. Never encourage quitting a job, taking loans, or making major financial bets.

Return ONLY a valid JSON object (no markdown fences):
{
  "founder_readiness_narrative": "<200-400 word narrative about this specific founder>",
  "primary_strength": "<one sentence about their clearest strength>",
  "primary_risk": "<one sentence about the most important risk to address>",
  "next_step_explanation": "<2-3 sentences explaining the recommended next step>",
  "what_not_to_do": ["<1-3 specific actions to avoid right now>"]
}"""

        user_message = f"""
Please write a personalised Phase 1 readiness narrative for this founder.

{context}

Route explanation to incorporate: {_ROUTE_EXPLANATIONS.get(result.recommended_route, '')}
{"Scenario insight: " + _SCENARIO_NOTES.get(result.detected_scenario, '') if result.detected_scenario else ''}

Remember: if overall_level >= 4, do NOT be encouraging about the venture itself.
Focus on the person and what they CAN do right now.
"""

        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message},
            ],
            temperature=0.4,
            max_tokens=800,
            response_format={'type': 'json_object'},
        )

        raw = response.choices[0].message.content
        return json.loads(raw)

    def _apply_guardrails(self, output: dict, result: Phase1Result) -> Optional[dict]:
        """
        Enforce CEO Section 7.2 guardrails on AI output.
        Returns None if output fails critical checks.
        """
        narrative = output.get('founder_readiness_narrative', '')

        # Guardrail: No guaranteed success language when blocked
        if result.overall_level >= LEVEL_HARD_BLOCK:
            forbidden_phrases = [
                'this will work', 'great idea', 'perfect timing',
                'definitely succeed', 'sure to', 'guaranteed',
            ]
            for phrase in forbidden_phrases:
                if phrase.lower() in narrative.lower():
                    logger.warning(
                        "Guardrail: AI used forbidden phrase '%s' despite Hard Block. "
                        "Falling back to template.", phrase
                    )
                    return None

        # Guardrail: No reckless financial encouragement
        reckless_phrases = ['quit your job', 'take a loan', 'invest everything']
        for phrase in reckless_phrases:
            if phrase.lower() in narrative.lower():
                logger.warning("Guardrail: Reckless financial advice detected. Using template.")
                return None

        # Add confidence label
        if result.overall_level >= LEVEL_HARD_BLOCK:
            output['confidence'] = 'LOW'
        elif result.overall_level >= LEVEL_SOFT_BLOCK:
            output['confidence'] = 'LOW'
        elif result.overall_level >= LEVEL_WARNING:
            output['confidence'] = 'MEDIUM'
        else:
            output['confidence'] = 'MEDIUM'

        return output

    def _generate_template_narrative(self, result: Phase1Result) -> dict:
        """
        Safe fallback template — always accurate, never AI-hallucinated.
        Used when AI is unavailable or fails guardrail checks.
        """
        route_explanation = _ROUTE_EXPLANATIONS.get(
            result.recommended_route,
            "Your next step is to continue through the platform's guided process."
        )
        scenario_note = _SCENARIO_NOTES.get(result.detected_scenario, '')

        blocker_count = len(result.active_blockers)

        if result.overall_level == LEVEL_HARD_STOP:
            narrative = (
                "Based on your answers, the platform has detected a situation that "
                "requires immediate attention before venture-building can safely proceed. "
                "Please review the details below carefully."
            )
            strength = "Your willingness to be honest about your situation is the first step."
            risk = "The current situation poses risks that need to be addressed first."
            what_not_to_do = [
                "Do not make any new financial commitments related to the venture.",
                "Do not quit your current employment or income source.",
            ]
        elif result.overall_level == LEVEL_HARD_BLOCK:
            narrative = (
                f"Your Phase 1 assessment is complete. "
                f"{'There is ' + str(blocker_count) + ' active blocker' if blocker_count == 1 else 'There are ' + str(blocker_count) + ' active blockers'} "
                f"that need to be resolved before you can access certain activities. "
                f"{route_explanation} "
                f"{scenario_note}"
            ).strip()
            strength = "Your motivation and intent to build are clear starting points."
            risk = result.active_blockers[0]['reason'] if result.active_blockers else "Active blockers present."
            what_not_to_do = [
                b.get('what_is_blocked', [''])
                for b in result.active_blockers[:2]
            ]
            what_not_to_do = [
                f"Avoid: {', '.join(w[:2]) if isinstance(w, list) else w}"
                for w in what_not_to_do
            ]
        elif result.overall_level >= LEVEL_SOFT_BLOCK:
            narrative = (
                f"Your Phase 1 assessment shows real potential alongside some constraints. "
                f"{route_explanation} "
                f"{scenario_note}"
            ).strip()
            strength = "You have identified a problem and have some capacity to work on it."
            risk = "Short-term constraints require a focused, low-risk approach."
            what_not_to_do = ["Do not rush into spending before validating your idea for free."]
        else:
            narrative = (
                f"Your foundation looks solid for this stage. "
                f"{route_explanation} "
                f"{scenario_note}"
            ).strip()
            strength = "Your readiness across key dimensions gives you a real foundation to build from."
            risk = "The main risk at this stage is moving to execution without sufficient validation."
            what_not_to_do = [
                "Do not skip customer discovery conversations.",
                "Do not build a full product before validating the core problem.",
            ]

        confidence = 'LOW' if result.overall_level >= LEVEL_HARD_BLOCK else 'MEDIUM'

        return {
            'founder_readiness_narrative': narrative,
            'primary_strength': strength,
            'primary_risk': risk,
            'next_step_explanation': route_explanation,
            'what_not_to_do': what_not_to_do,
            'confidence': confidence,
            'is_template': True,  # Flag for debugging
        }
