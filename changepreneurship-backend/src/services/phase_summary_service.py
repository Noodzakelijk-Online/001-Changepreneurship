"""
Phase Summary Service
---------------------
Generates a brief AI-powered summary for a single completed assessment phase.
Called immediately after the user completes a phase to show what was discovered.
"""
import os
import json
import logging
import time

from groq import Groq

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schema injected into the system prompt
# ---------------------------------------------------------------------------
PHASE_SUMMARY_SCHEMA = """
Return ONLY a valid JSON object (no markdown fences) with this exact structure:

{
  "score": <int 0-100, quality score based on depth and completeness of responses>,
  "headline": <string, 6-12 words capturing the key theme, e.g. "Strong Technical Foundation with Clear Market Gap">,
  "summary": <string, 2-3 sentences synthesizing what this phase reveals about the founder>,
  "key_findings": [
    <string, specific insight #1 — 1-2 sentences, must be non-generic>,
    <string, specific insight #2 — 1-2 sentences, must be non-generic>,
    <string, specific insight #3 — 1-2 sentences, must be non-generic>
  ],
  "next_focus": <string, 1 sentence: what to prioritize in the next phase or overall>
}
"""

# Phase-specific context for the system prompt
PHASE_CONTEXT = {
    "self_discovery": (
        "Phase 1 — Self-Discovery & Purpose. "
        "Focus on motivation, values, personality, risk tolerance, and entrepreneurial readiness."
    ),
    "idea_discovery": (
        "Phase 2 — Idea Discovery. "
        "Focus on passion-skill alignment, problem identification, value proposition, and target customer clarity."
    ),
    "market_research": (
        "Phase 3 — Market Research. "
        "Focus on competitive landscape, customer research, market size, stakeholder mapping, and validation."
    ),
    "business_pillars": (
        "Phase 4 — Business Pillars Planning. "
        "Focus on customer segmentation, value proposition, business model, financial planning, and go-to-market strategy."
    ),
    "product_concept_testing": (
        "Phase 5 — Product Concept Testing. "
        "Focus on product-market fit, customer feedback, pricing validation, and concept refinement."
    ),
    "business_development": (
        "Phase 6 — Business Development. "
        "Focus on strategic decisions, resource allocation, partnerships, and growth strategy."
    ),
    "business_prototype_testing": (
        "Phase 7 — Business Prototype Testing. "
        "Focus on prototype results, market testing, business model validation, and scaling readiness."
    ),
}


class PhaseSummaryService:
    """Generate a brief AI summary for a single completed assessment phase."""

    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

    def generate_summary(self, phase_id: str, phase_name: str, responses: list) -> dict:
        """
        Generate a phase completion summary.

        Args:
            phase_id:    Phase identifier (e.g. 'self_discovery')
            phase_name:  Human-readable phase name  (e.g. 'Self Discovery')
            responses:   List of AssessmentResponse model objects

        Returns:
            Dict with keys: score, headline, summary, key_findings, next_focus, phase_id
        """
        if not responses:
            return self._fallback_summary(phase_id, phase_name, 0)

        if not self.groq_key:
            logger.warning("[PhaseSummary] No GROQ_API_KEY — returning fallback")
            return self._fallback_summary(phase_id, phase_name, len(responses))

        prompt = self._build_prompt(phase_name, responses)
        return self._call_groq(phase_id, phase_name, prompt, len(responses))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, phase_name: str, responses: list) -> str:
        lines = [
            f"=== {phase_name.upper()} PHASE RESPONSES ===",
            f"Total answers: {len(responses)}",
            "",
        ]
        for r in responses[:25]:  # cap to keep prompt focused
            q = (getattr(r, "question_text", None) or getattr(r, "question_id", "?"))[:100]
            try:
                v = r.get_response_value()
            except Exception:
                v = str(getattr(r, "response_value", "") or "")
            val_str = str(v)[:250] if v is not None else ""
            section = getattr(r, "section_id", "") or ""
            lines.append(f"[{section}] Q: {q} → A: {val_str}")
        lines.append("")
        lines.append(
            f"Analyze these {phase_name} responses and generate the phase summary JSON."
        )
        return "\n".join(lines)

    def _call_groq(
        self, phase_id: str, phase_name: str, prompt: str, response_count: int
    ) -> dict:
        phase_ctx = PHASE_CONTEXT.get(phase_id, f"Phase: {phase_name}")
        system = (
            "You are the Changepreneurship AI Analyst. "
            "Your task is to generate a concise, insightful phase completion summary.\n\n"
            f"Context: {phase_ctx}\n\n"
            "Be specific about what the responses reveal. "
            "Avoid generic statements — reference the actual answers where possible. "
            "Score reflects response depth and quality (0–100).\n\n"
            + PHASE_SUMMARY_SCHEMA
        )
        try:
            client = Groq(api_key=self.groq_key)
            t0 = time.time()
            completion = client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1024,
            )
            elapsed = time.time() - t0
            raw = completion.choices[0].message.content
            logger.info(
                f"[PhaseSummary] Groq {elapsed:.2f}s for phase={phase_id}, "
                f"model={self.groq_model}"
            )
            result = json.loads(raw)
            result["phase_id"] = phase_id
            return result
        except json.JSONDecodeError as e:
            logger.error(f"[PhaseSummary] JSON parse error for {phase_id}: {e}")
            return self._fallback_summary(phase_id, phase_name, response_count)
        except Exception as e:
            logger.error(f"[PhaseSummary] Groq error for {phase_id}: {e}")
            return self._fallback_summary(phase_id, phase_name, response_count)

    def _fallback_summary(
        self, phase_id: str, phase_name: str, response_count: int
    ) -> dict:
        score = min(65, 30 + response_count * 3)
        return {
            "phase_id": phase_id,
            "score": score,
            "headline": f"{phase_name} Completed",
            "summary": (
                f"You've completed the {phase_name} assessment with {response_count} responses. "
                "Your full AI-powered analysis will be available in the Insights Report."
            ),
            "key_findings": [
                "Your responses have been saved and will inform your complete founder profile.",
                "Continue through the remaining phases to unlock deeper analysis.",
                "Access your full AI Insights Report from the dashboard at any time.",
            ],
            "next_focus": (
                "Keep building on your progress — each phase adds depth to your personalised insights."
            ),
        }
