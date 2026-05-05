"""
AI Layer 3 Contract — Sprint 5 (S5-01)
=========================================
CEO (Section 7.1): "AI receives a structured input and produces a structured output.
Both are audited. The user can always see what was given to AI and what came back."

Typed input/output dataclasses for all AI calls in the system.
Every AI task must use one of these contracts.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# AI Task Types (CEO Section 7.1)
# ---------------------------------------------------------------------------
AI_TASK_GENERATE_CVC = 'GENERATE_CVC'           # Clarified Venture Concept
AI_TASK_GENERATE_ASSUMPTIONS = 'GENERATE_ASSUMPTIONS'
AI_TASK_GENERATE_PROBLEM_STATEMENT = 'GENERATE_PROBLEM_STATEMENT'
AI_TASK_REENTRY_SUMMARY = 'REENTRY_SUMMARY'
AI_TASK_REROUTE_MESSAGE = 'REROUTE_MESSAGE'
AI_TASK_CONTRADICTION_CHECK = 'CONTRADICTION_CHECK'
AI_TASK_NARRATIVE_PHASE1 = 'NARRATIVE_PHASE1'

ALL_AI_TASKS = {
    AI_TASK_GENERATE_CVC,
    AI_TASK_GENERATE_ASSUMPTIONS,
    AI_TASK_GENERATE_PROBLEM_STATEMENT,
    AI_TASK_REENTRY_SUMMARY,
    AI_TASK_REROUTE_MESSAGE,
    AI_TASK_CONTRADICTION_CHECK,
    AI_TASK_NARRATIVE_PHASE1,
}


# ---------------------------------------------------------------------------
# AI Input Contract
# ---------------------------------------------------------------------------
@dataclass
class AIInputContract:
    task_type: str
    user_id: int
    inputs: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    allowed_output_types: List[str] = field(default_factory=list)
    guardrail_checks: List[str] = field(default_factory=lambda: ['all'])
    max_tokens: int = 800
    temperature: float = 0.3

    def validate(self):
        if self.task_type not in ALL_AI_TASKS:
            raise ValueError(f'Unknown AI task type: {self.task_type}')
        if not self.inputs:
            raise ValueError('AI input contract: inputs cannot be empty')
        if self.max_tokens > 2000:
            raise ValueError('AI input contract: max_tokens must be ≤ 2000')


# ---------------------------------------------------------------------------
# AI Output Contract
# ---------------------------------------------------------------------------
@dataclass
class AIOutputContract:
    task_type: str
    user_id: int
    output: Dict[str, Any]
    confidence_label: str        # SPECULATIVE / LOW / MEDIUM / HIGH / VERIFIED
    confidence_score: float      # 0.0-1.0
    guardrail_passed: bool
    guardrail_flags: List[str] = field(default_factory=list)
    input_summary_hash: str = ''
    model_used: str = ''
    tokens_used: int = 0
    is_cached: bool = False

    def to_audit_dict(self) -> dict:
        """Safe-to-store audit representation (no raw user content)."""
        return {
            'task_type': self.task_type,
            'confidence_label': self.confidence_label,
            'confidence_score': self.confidence_score,
            'guardrail_passed': self.guardrail_passed,
            'guardrail_flags': self.guardrail_flags,
            'model_used': self.model_used,
            'tokens_used': self.tokens_used,
            'input_hash': self.input_summary_hash,
        }


# ---------------------------------------------------------------------------
# Contract builder helpers
# ---------------------------------------------------------------------------
def build_cvc_input(user_id: int, responses: dict) -> AIInputContract:
    return AIInputContract(
        task_type=AI_TASK_GENERATE_CVC,
        user_id=user_id,
        inputs={
            'idea_description': responses.get('idea_description', ''),
            'target_user': responses.get('target_user_description', ''),
            'problem': responses.get('problem_description', ''),
            'value_prop': responses.get('value_prop', ''),
        },
        allowed_output_types=['text', 'structured'],
        max_tokens=600,
    )


def build_assumptions_input(user_id: int, cvc_draft: dict) -> AIInputContract:
    return AIInputContract(
        task_type=AI_TASK_GENERATE_ASSUMPTIONS,
        user_id=user_id,
        inputs={
            'problem_statement': cvc_draft.get('problem_statement', ''),
            'target_user': cvc_draft.get('target_user_hypothesis', ''),
            'value_prop': cvc_draft.get('value_proposition', ''),
        },
        allowed_output_types=['list'],
        guardrail_checks=['ai_is_never_verified_fact'],
        max_tokens=400,
    )
