"""
AI Cost Manager — Sprint 5 (S5-04)
======================================
CEO (Section 7.4): "AI costs must be tracked. Free alternatives used when equivalent."

Tracks token usage per user session. Provides cost estimates before calls.
Manages free-tier fallbacks when over budget or when AI is equivalent.

Token pricing (approximate, adjust to actual Groq pricing):
  llama-3.3-70b-versatile: $0.00059 per 1K tokens (input+output combined)
"""
import logging
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger(__name__)

# Token cost per 1K tokens in USD (combined input+output)
COST_PER_1K_TOKENS_USD = 0.00059

# Default session budget (tokens)
DEFAULT_SESSION_BUDGET_TOKENS = 10_000

# Default daily budget (tokens per user)
DEFAULT_DAILY_BUDGET_TOKENS = 50_000

# Free alternative task mappings (task_type → free fallback method name)
FREE_ALTERNATIVES = {
    'GENERATE_CVC': 'template_cvc',
    'GENERATE_ASSUMPTIONS': 'template_assumptions',
    'GENERATE_PROBLEM_STATEMENT': 'template_problem_statement',
    'REROUTE_MESSAGE': 'template_reroute',
    'NARRATIVE_PHASE1': 'template_phase1_narrative',
}


@dataclass
class CostEstimate:
    task_type: str
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_total_tokens: int
    estimated_cost_usd: float
    free_alternative_available: bool
    free_alternative_method: Optional[str]
    recommendation: str  # 'USE_AI' | 'USE_FREE' | 'OVER_BUDGET'


@dataclass
class UsageSummary:
    user_id: int
    session_tokens_used: int
    session_budget: int
    session_remaining: int
    session_cost_usd: float
    over_budget: bool


class AICostManager:
    """
    Stateless cost estimator + budget tracker.
    In production, persist token usage to Redis or DB.
    """

    def estimate_cost(
        self,
        task_type: str,
        input_text: str,
        max_output_tokens: int = 600,
    ) -> CostEstimate:
        """
        Estimate cost before making an AI call.
        Rough rule: 1 token ≈ 4 characters.
        """
        input_tokens = max(len(input_text) // 4, 10)
        total_tokens = input_tokens + max_output_tokens
        cost_usd = total_tokens / 1000 * COST_PER_1K_TOKENS_USD

        free_method = FREE_ALTERNATIVES.get(task_type)
        recommendation = 'USE_AI'
        if free_method:
            recommendation = 'USE_FREE'  # Prefer free if available

        return CostEstimate(
            task_type=task_type,
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=max_output_tokens,
            estimated_total_tokens=total_tokens,
            estimated_cost_usd=round(cost_usd, 6),
            free_alternative_available=bool(free_method),
            free_alternative_method=free_method,
            recommendation=recommendation,
        )

    def check_budget(
        self,
        user_id: int,
        tokens_needed: int,
        session_tokens_used: int = 0,
        session_budget: int = DEFAULT_SESSION_BUDGET_TOKENS,
    ) -> bool:
        """Return True if within budget, False if over."""
        remaining = session_budget - session_tokens_used
        return tokens_needed <= remaining

    def record_usage(
        self,
        user_id: int,
        tokens_used: int,
        task_type: str,
        model: str = 'llama-3.3-70b-versatile',
    ) -> dict:
        """
        Record token usage for a completed AI call.
        In production: store to Redis HINCRBY or DB.
        """
        cost_usd = tokens_used / 1000 * COST_PER_1K_TOKENS_USD
        logger.info(
            "AI usage: user=%s task=%s tokens=%d cost=$%.6f model=%s",
            user_id, task_type, tokens_used, cost_usd, model,
        )
        return {
            'user_id': user_id,
            'tokens_used': tokens_used,
            'cost_usd': round(cost_usd, 6),
            'task_type': task_type,
            'model': model,
        }

    def get_free_alternatives(self, task_type: str) -> List[str]:
        """Return available free alternatives for a given task type."""
        method = FREE_ALTERNATIVES.get(task_type)
        return [method] if method else []

    def should_use_free(
        self,
        task_type: str,
        session_tokens_used: int = 0,
        budget: int = DEFAULT_SESSION_BUDGET_TOKENS,
    ) -> bool:
        """
        Decide whether to use free fallback instead of AI.
        True if: free alternative exists AND (over budget OR free is equivalent).
        """
        if task_type not in FREE_ALTERNATIVES:
            return False
        if session_tokens_used >= budget * 0.8:  # >80% budget used
            return True
        return True  # Default: always prefer free template when available (CEO: cost control)
