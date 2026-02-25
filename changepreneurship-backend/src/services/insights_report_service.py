"""
AI Insights Report Service
--------------------------
Generates the full Entrepreneur + Venture AI report by:
  1. Collecting all assessment responses for the user (all 7 phases)
  2. Building a rich structured prompt
  3. Calling Groq (llama-3.3-70b-versatile) in JSON mode — AI consensus
  4. Returning the full report dict
  5. Caching the result in Redis (TTL 3600s)
"""
import os
import json
import hashlib
import logging
import time
from typing import Optional

from groq import Groq

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# JSON schema description injected into the system prompt
# ---------------------------------------------------------------------------
REPORT_SCHEMA = """
Return ONLY a valid JSON object (no markdown fences) that strictly follows this schema:

{
  "entrepreneur": {
    "score": <int 0-100>,
    "archetype": <string, e.g. "Visionary Builder">,
    "tagline": <string, e.g. "The Passionate Disruptor">,
    "summary": <string, 2-3 sentences about the founder>,
    "radar": {
      "Motivation": <int>, "Personality": <int>, "Values": <int>,
      "Self-Awareness": <int>, "Life Support": <int>, "Resources": <int>,
      "Passion": <int>, "Skills": <int>, "Vision": <int>,
      "Leadership": <int>, "Team Building": <int>, "Culture": <int>
    },
    "dimensions": [
      {
        "name": <string>,
        "score": <int>,
        "description": <string, 1-2 sentences>,
        "subs": [ {"name": <string>, "score": <int>} ]
      }
    ],
    "phases": [
      {
        "id": <string, e.g. "self-discovery">,
        "title": <string, e.g. "Phase 1: Self-Discovery & Purpose">,
        "icon": <single emoji>,
        "score": <int>,
        "completed": <bool>,
        "cards": [
          {
            "name": <string>,
            "score": <int>,
            "description": <string, 1-2 sentences>,
            "subs": [ {"name": <string>, "score": <int>} ]
          }
        ]
      }
    ],
    "strengths": [ {"name": <string>, "score": <int>} ],
    "growth_areas": [ {"name": <string>, "score": <int>} ],
    "recent_activity": [
      {
        "type": <one of: "completed","progress","unlocked">,
        "icon": <one of: "✓","◐","★">,
        "color": <one of: "green","orange","purple">,
        "text": <string, short activity label, may use <b> tags for phase/strength name>
      }
    ]
  },
  "venture": {
    "score": <int 0-100>,
    "idea_name": <string>,
    "tagline": <string>,
    "summary": <string, 2-3 sentences about the venture>,
    "radar": {
      "Market Demand": <int>, "Problem-Solution Fit": <int>,
      "Business Model": <int>, "Strategic Thinking": <int>,
      "Positioning": <int>, "Customer Validation": <int>,
      "Competitive Analysis": <int>, "Market Sizing": <int>
    },
    "dimensions": [
      {
        "name": <string>,
        "score": <int>,
        "description": <string>,
        "subs": [ {"name": <string>, "score": <int>} ]
      }
    ],
    "phases": [
      {
        "id": <string>,
        "title": <string>,
        "icon": <emoji>,
        "score": <int or null if not started>,
        "completed": <bool>,
        "cards": [
          {
            "name": <string>,
            "score": <int>,
            "description": <string>,
            "subs": [ {"name": <string>, "score": <int>} ]
          }
        ]
      }
    ],
    "validation_pct": <int 0-100>,
    "runway_months": <int, estimated months of financial runway>,
    "months_to_profit": <int, estimated months until profitable>,
    "interviews_done": <int, number of customer interviews completed>,
    "interviews_target": 20,
    "competitors_validated": <int, number of competitors thoroughly analyzed>,
    "competitors_target": 5,
    "heatmap": {
      "Strategic":  [<int 0-100 for Business Model>,<int for Strategic Thinking>,<int for Market Demand>,<int for Customer Validation>,<int for Competitive Analysis>,<int for Market Sizing>],
      "Behavioral": [<int 0-100 for Business Model>,<int for Strategic Thinking>,<int for Market Demand>,<int for Customer Validation>,<int for Competitive Analysis>,<int for Market Sizing>],
      "Predictive": [<int 0-100 for Business Model>,<int for Strategic Thinking>,<int for Market Demand>,<int for Customer Validation>,<int for Competitive Analysis>,<int for Market Sizing>]
    }
  },
  "alignment": {
    "score": <int 0-100>,
    "combined_score": <int 0-100>,
    "sweet_spots": [
      {
        "ent_dim": <string, exact entrepreneur dimension name>,
        "ent_score": <int>,
        "ven_dim": <string, exact venture dimension name>,
        "ven_score": <int>,
        "relation": <one of: "Reinforces","Anchors","Differentiates","Informs","Enables">,
        "insight": <string, 2-3 sentences with specific stats/numbers. Use <b> for key phrases. Use <span class='highlight green'>text</span> for positive outcomes, <span class='highlight purple'>text</span> for strategic advantages>
      }
    ],
    "risk_zones": [
      {
        "ent_dim": <string>,
        "ent_score": <int>,
        "ven_dim": <string>,
        "ven_score": <string or int>,
        "relation": <one of: "Critical Gap","Compounding","Bottleneck","Limiting">,
        "insight": <string, 2-3 sentences naming the exact risk. Use <b> for key phrases. Use <span class='highlight red'>text</span> for danger signals>,
        "action": <string, specific actionable step, 5-10 words>
      }
    ],
    "untapped_potential": [
      {
        "strength_dim": <string>,
        "strength_score": <int>,
        "gap_dim": <string>,
        "gap_score": <string or int>,
        "relation": "Can Boost",
        "insight": <string, 2-3 sentences. Include <span class='highlight purple'>Estimated impact: +X to Y score</span> or unlock message>
      }
    ]
  },
  "readiness": {
    "entrepreneur_target": 75,
    "venture_target": 70,
    "alignment_target": 60,
    "unlocked": <bool>,
    "unlock_message": <string>
  }
}
"""

SYSTEM_PROMPT = """You are the Changepreneurship AI Analyst — an expert business psychologist and venture analyst.
Your job is to analyze a user's full entrepreneurship assessment and generate a comprehensive AI insights report.

The Changepreneurship platform assesses founders across 7 phases:
  Phase 1 — Self-Discovery & Purpose (entrepreneur psyche: motivation, values, self-awareness)
  Phase 2 — Passion, Skills & Vision (entrepreneur capabilities + early venture idea formation)
  Phase 3 — Strategy Development (venture business model and strategic thinking)
  Phase 4 — Market Intelligence (customer validation, competitors, market sizing)
  Phase 5 — Leadership & Culture (team building, culture, delegation)
  Phase 6 — AI & Future-Proofing (technology readiness, AI adoption)
  Phase 7 — Execution & Growth (planning, operations, scaling)

SCORING GUIDANCE:
  - Scores reflect quality of responses, depth of thinking, and readiness level
  - 85-100: Exceptional / investor-ready
  - 70-84: Strong / minor gaps
  - 55-69: Developing / needs focus
  - 40-54: Early stage / significant work needed
  - <40: Not yet addressed

ALIGNMENT GUIDANCE:
  - Sweet Spots: Find at LEAST 3 and up to 5. Where a founder STRENGTH directly reinforces a venture STRENGTH or compensates for a gap. Use verbs: Reinforces / Anchors / Differentiates / Informs / Enables.
  - Risk Zones: Find at LEAST 3 and up to 4. Where a founder WEAKNESS compounds a venture WEAKNESS (these are critical). Use labels: Critical Gap / Compounding / Bottleneck / Limiting. Each risk_zone MUST include a concrete 'action' field.
  - Untapped Potential: Find at LEAST 3. Where an unused founder strength could dramatically improve a venture gap. Always end insight with an estimated score impact using the purple highlight span.

INSIGHT TEXT RULES:
  - Be specific with numbers, percentages, and named dimensions
  - Insights must be 2-3 full sentences — substantive, not generic
  - Use HTML: <b>bold key phrases</b> for emphasis
  - Use <span class='highlight green'>positive callout</span> for wins
  - Use <span class='highlight red'>red warning text</span> for danger signals  
  - Use <span class='highlight purple'>purple text</span> for strategic insights and impact estimates
  - Example: "<b>Your 12-month runway is shorter than the 18 months needed.</b> This creates a <span class='highlight red'>6-month funding gap</span> that must be resolved before launch."

Be specific, honest, and actionable. Scores must be internally consistent.

PHASE CARD GUIDANCE — You MUST generate ALL of these cards for each completed or in-progress phase:

ENTREPRENEUR PHASES:
  Phase 1 (Self-Discovery & Purpose) — Generate ALL 6 cards:
    1. "Motivation & Drive" — subs: ["Core Drivers", "Failure Resilience", "Entrepreneurial Readiness"]
    2. "Personality & Work Style" — subs: ["Risk Tolerance", "Stress Management", "Decision Making"]
    3. "Values & Ethics" — subs: ["Ethical Standards", "Value Alignment"]
    4. "Self-Awareness" — subs: ["Strengths Clarity", "Growth Awareness"]
    5. "Life Impact & Support" — subs: ["Family Support", "Time Commitment", "Work-Life Balance"]
    6. "Resources & Background" — subs: ["Financial Runway", "Industry Experience", "Professional Network", "Prior Entrepreneurship"]

  Phase 2 (Passion, Skills & Vision) — Generate ALL 3 cards:
    1. "Passion Intensity" — subs: ["Domain Passion", "Problem Empathy"]
    2. "Skill Alignment" — subs: ["Technical Skills", "Leadership Skills", "Sales & Communication"]
    3. "Vision Clarity" — subs: ["Long-term Direction", "Articulation"]

  Phase 5 (Leadership & Culture) — Generate ALL 3 cards:
    1. "Leadership Style" — subs: ["Delegation", "Inspiration", "Adaptability"]
    2. "Team Building" — subs: ["Hiring Strategy", "Team Structure"]
    3. "Culture & Communication" — subs: ["Culture Definition", "Communication Style"]

  Phase 6 & Phase 7 — Generate 2-3 cards per phase relevant to the phase topic.

VENTURE PHASES:
  Phase 2 (Market Opportunity) — Generate 2 cards:
    1. "Market Demand Signals" — subs: ["Timing", "Evidence"]
    2. "Problem-Solution Fit" — subs: ["Problem Clarity", "Solution Uniqueness"]

  Phase 3 (Strategy Development) — Generate ALL 3 cards:
    1. "Business Model Design" — subs: ["Revenue Model", "Pricing Strategy", "Key Activities"]
    2. "Strategic Thinking" — subs: ["Scenario Planning", "Adaptability"]
    3. "Competitive Positioning" — subs: ["Differentiation", "Barriers to Entry"]

  Phase 4 (Market Intelligence) — Generate ALL 3 cards:
    1. "Customer Validation" — subs: ["Interviews Completed", "Feedback Quality", "Payment Intent"]
    2. "Competitive Analysis" — subs: ["Direct Competitors", "Indirect Competitors"]
    3. "Market Sizing & Trends" — subs: ["TAM", "SAM", "SAM/SOM Ratio"]

  Phase 5, Phase 6, Phase 7 — Generate 2-3 relevant cards per completed phase.

CRITICAL RULES FOR CARDS:
  - Every card MUST have a 'subs' array with 2-4 entries (NEVER empty or missing)
  - Sub scores must be consistent with the parent card score (±15 range)
  - Card descriptions must be 1-2 specific sentences — NOT generic filler
  - For unlocked/not-started phases: set cards=[] and score=null and completed=false
""" + REPORT_SCHEMA


class InsightsReportService:
    """Generate AI-powered full insights report for a user."""

    CACHE_TTL = 3600  # 1 hour

    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        self._redis = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_report(self, user_id: int, assessment_data: dict) -> dict:
        """
        Build or retrieve the full AI insights report.

        Args:
            user_id: DB user id
            assessment_data: dict with keys:
                'phases'     — list of {id, name, progress, completed}
                'responses'  — dict phase_id → list of response dicts
        Returns:
            Full report dict (see REPORT_SCHEMA above).
        """
        cache_key = self._cache_key(user_id, assessment_data)

        # Try cache first
        cached = self._get_cache(cache_key)
        if cached:
            logger.info(f"[InsightsReport] Cache HIT for user {user_id}")
            cached["_from_cache"] = True
            return cached

        logger.info(f"[InsightsReport] Cache MISS for user {user_id} — calling AI")

        user_prompt = self._build_user_prompt(assessment_data)
        report = self._call_groq(user_prompt)

        # Always stamp metadata
        report["generated_at"] = _now_iso()
        report["consensus"] = {
            "models": [{"model": self.groq_model, "provider": "groq"}],
            "confidence": self._calc_confidence(assessment_data),
            "phases_analyzed": len(assessment_data.get("phases", [])),
            "responses_analyzed": sum(
                len(v) for v in assessment_data.get("responses", {}).values()
            ),
        }

        self._set_cache(cache_key, report)
        return report

    def invalidate_cache(self, user_id: int):
        """Bust all cached reports for this user."""
        redis = self._get_redis()
        if redis:
            pattern = f"insights:report:{user_id}:*"
            for key in redis.scan_iter(pattern):
                redis.delete(key)

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------

    def _build_user_prompt(self, assessment_data: dict) -> str:
        phases = assessment_data.get("phases", [])
        responses = assessment_data.get("responses", {})

        lines = [
            "=== ASSESSMENT OVERVIEW ===",
            f"Total phases tracked: {len(phases)}",
            f"Completed phases: {sum(1 for p in phases if p.get('completed'))}",
            "",
        ]

        for phase in phases:
            pid = phase.get("id", "unknown")
            pname = phase.get("name", pid)
            progress = phase.get("progress", 0)
            completed = phase.get("completed", False)
            lines.append(
                f"Phase '{pid}' — {pname} | Progress: {progress:.0f}% | "
                f"{'Completed' if completed else 'In Progress'}"
            )
            phase_responses = responses.get(pid, [])
            if phase_responses:
                lines.append(f"  Responses ({len(phase_responses)} answers):")
                for resp in phase_responses[:30]:  # cap per phase
                    section = resp.get("section_id", "")
                    q_text = resp.get("question_text", resp.get("question_id", ""))
                    value = resp.get("response_value", "")
                    if value is None:
                        continue
                    # Truncate very long text values
                    val_str = str(value)
                    if len(val_str) > 300:
                        val_str = val_str[:300] + "…"
                    lines.append(f"    [{section}] Q: {q_text[:120]} → A: {val_str}")
            else:
                lines.append("  No responses yet for this phase.")
            lines.append("")

        lines.append(
            "Based on all the above, generate the complete AI insights report JSON."
        )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Groq call
    # ------------------------------------------------------------------

    def _call_groq(self, user_prompt: str) -> dict:
        if not self.groq_key:
            logger.warning("[InsightsReport] No GROQ_API_KEY — using fallback")
            return self._fallback_report()

        try:
            client = Groq(api_key=self.groq_key)
            t0 = time.time()
            completion = client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,    # low temp for consistent scoring
                max_tokens=8192,
            )
            elapsed = time.time() - t0
            raw = completion.choices[0].message.content
            logger.info(
                f"[InsightsReport] Groq response in {elapsed:.2f}s, "
                f"{len(raw)} chars, model={self.groq_model}"
            )
            return json.loads(raw)

        except json.JSONDecodeError as e:
            logger.error(f"[InsightsReport] JSON parse error: {e}")
            return self._fallback_report()
        except Exception as e:
            logger.error(f"[InsightsReport] Groq error: {e}")
            return self._fallback_report()

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def _get_redis(self):
        if self._redis is not None:
            return self._redis
        try:
            import redis as redis_lib
            url = os.getenv("REDIS_URL", "")
            if url:
                self._redis = redis_lib.from_url(url, decode_responses=True)
                self._redis.ping()
                return self._redis
        except Exception as e:
            logger.warning(f"[InsightsReport] Redis unavailable: {e}")
        return None

    def _cache_key(self, user_id: int, assessment_data: dict) -> str:
        # Key includes a hash of phase completion state so cache busts on progress
        state = json.dumps(
            [
                {"id": p.get("id"), "progress": p.get("progress"), "done": p.get("completed")}
                for p in assessment_data.get("phases", [])
            ],
            sort_keys=True,
        )
        h = hashlib.md5(state.encode()).hexdigest()[:8]
        return f"insights:report:{user_id}:{h}"

    def _get_cache(self, key: str) -> Optional[dict]:
        redis = self._get_redis()
        if not redis:
            return None
        try:
            raw = redis.get(key)
            if raw:
                return json.loads(raw)
        except Exception as e:
            logger.warning(f"[InsightsReport] Cache get error: {e}")
        return None

    def _set_cache(self, key: str, data: dict):
        redis = self._get_redis()
        if not redis:
            return
        try:
            redis.setex(key, self.CACHE_TTL, json.dumps(data))
        except Exception as e:
            logger.warning(f"[InsightsReport] Cache set error: {e}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _calc_confidence(assessment_data: dict) -> float:
        phases = assessment_data.get("phases", [])
        if not phases:
            return 0.0
        completed = sum(1 for p in phases if p.get("completed"))
        return round(min(1.0, completed / max(1, len(phases))), 2)

    @staticmethod
    def _fallback_report() -> dict:
        """Minimal safe fallback when AI call fails."""
        return {
            "_fallback": True,
            "entrepreneur": {
                "score": 0,
                "archetype": "Unknown",
                "tagline": "Assessment incomplete",
                "summary": "Complete more assessment phases to generate your AI insights.",
                "radar": {k: 0 for k in [
                    "Motivation","Personality","Values","Self-Awareness",
                    "Life Support","Resources","Passion","Skills","Vision",
                    "Leadership","Team Building","Culture"
                ]},
                "dimensions": [],
                "phases": [],
                "strengths": [],
                "growth_areas": [],
                "recent_activity": [],
            },
            "venture": {
                "score": 0,
                "idea_name": "Not yet defined",
                "tagline": "",
                "summary": "Complete venture phases to generate your AI insights.",
                "radar": {k: 0 for k in [
                    "Market Demand","Problem-Solution Fit","Business Model",
                    "Strategic Thinking","Positioning","Customer Validation",
                    "Competitive Analysis","Market Sizing"
                ]},
                "dimensions": [],
                "phases": [],
                "validation_pct": 0,
                "runway_months": 0,
                "months_to_profit": 0,
                "interviews_done": 0,
                "interviews_target": 20,
                "competitors_validated": 0,
                "competitors_target": 5,
                "heatmap": None,
            },
            "alignment": {
                "score": 0,
                "combined_score": 0,
                "sweet_spots": [],
                "risk_zones": [],
                "untapped_potential": [],
            },
            "readiness": {
                "entrepreneur_target": 75,
                "venture_target": 70,
                "alignment_target": 60,
                "unlocked": False,
                "unlock_message": "Complete your assessment phases to unlock the Business Builder.",
            },
        }


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
