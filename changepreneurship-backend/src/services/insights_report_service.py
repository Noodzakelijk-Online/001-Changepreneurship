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

SYSTEM_PROMPT = """You are the Changepreneurship AI Analyst. Analyze founder assessment data and return a JSON insights report.

7 phases: Self-Discovery, Passion/Skills/Vision, Strategy, Market Intelligence, Leadership, AI Adoption, Execution.
Scores: 85-100=exceptional, 70-84=strong, 55-69=developing, 40-54=early, <40=not addressed.

Alignment: 3-5 sweet_spots (founder strength + venture strength), 3-4 risk_zones (weakness compounds weakness, include 'action'), 3 untapped_potential entries.
Use HTML in insights: <b>bold</b>, <span class='highlight green'>, <span class='highlight red'>, <span class='highlight purple'>. Insights must be 2-3 specific sentences.

Cards: Each completed phase needs 2-4 cards. Each card needs 'subs' array (2-3 items). For not-started phases: cards=[], score=null, completed=false.
""" + REPORT_SCHEMA


class InsightsReportService:
  """Generate AI-powered full insights report for a user."""

  CACHE_TTL = 3600  # 1 hour
  ENABLE_CACHE = True

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
    cache_key = None

    if self.ENABLE_CACHE:
      cache_key = self._cache_key(user_id, assessment_data)
      cached = self._get_cache(cache_key)
      if cached:
        logger.info(f"[InsightsReport] Cache HIT for user {user_id}")
        cached["_from_cache"] = True
        return cached

      logger.info(f"[InsightsReport] Cache MISS for user {user_id} — calling AI")
    else:
      logger.info(f"[InsightsReport] Cache disabled — generating fresh report for user {user_id}")

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

    if self.ENABLE_CACHE:
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
      f"Total phases: {len(phases)} | Completed: {sum(1 for p in phases if p.get('completed'))}",
      "",
    ]

    for phase in phases:
      pid = phase.get("id", "unknown")
      pname = phase.get("name", pid)
      progress = phase.get("progress", 0)
      completed = phase.get("completed", False)
      lines.append(
        f"Phase '{pid}' ({pname}): {progress:.0f}% {'✓' if completed else '…'}"
      )
      phase_responses = responses.get(pid, [])
      if phase_responses:
        for resp in phase_responses[:4]:  # max 4 responses per phase
          section = resp.get("section_id", "")
          q_text = resp.get("question_text", resp.get("question_id", ""))
          value = resp.get("response_value", "")
          if value is None:
            continue
          val_str = str(value)
          if len(val_str) > 80:
            val_str = val_str[:80] + "…"
          lines.append(f"  [{section}] {q_text[:50]}: {val_str}")
      lines.append("")

    lines.append("Generate the complete AI insights report JSON based on the above.")
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
        temperature=0.3,
        max_tokens=8192,
        timeout=90,
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
    phases_state = [
      {
        "id": p.get("id"),
        "progress": p.get("progress"),
        "done": p.get("completed"),
      }
      for p in assessment_data.get("phases", [])
    ]

    responses_state = {}
    for phase_id, items in (assessment_data.get("responses", {}) or {}).items():
      normalized_items = []
      for item in items or []:
        normalized_items.append({
          "question_id": item.get("question_id"),
          "section_id": item.get("section_id"),
          "response_type": item.get("response_type"),
          "response_value": item.get("response_value"),
        })
      responses_state[phase_id] = sorted(
        normalized_items,
        key=lambda row: (
          str(row.get("question_id") or ""),
          str(row.get("section_id") or ""),
        ),
      )

    state = json.dumps(
      {
        "v": 2,
        "phases": sorted(phases_state, key=lambda p: str(p.get("id") or "")),
        "responses": responses_state,
      },
      sort_keys=True,
      default=str,
    )
    h = hashlib.md5(state.encode()).hexdigest()[:12]
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
          "Motivation", "Personality", "Values", "Self-Awareness",
          "Life Support", "Resources", "Passion", "Skills", "Vision",
          "Leadership", "Team Building", "Culture",
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
          "Market Demand", "Problem-Solution Fit", "Business Model",
          "Strategic Thinking", "Positioning", "Customer Validation",
          "Competitive Analysis", "Market Sizing",
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
