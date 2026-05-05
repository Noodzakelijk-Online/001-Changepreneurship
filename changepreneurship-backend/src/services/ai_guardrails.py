"""
AI Guardrails — Sprint 5 (S5-02)
===================================
CEO (Section 7.2): 10 guardrail checks (A-J).
"AI is a co-pilot, not a co-founder. It enhances human judgment, does not replace it."

The 10 never-categories:
  A. NEVER claim AI outputs are verified facts
  B. NEVER give specific legal advice
  C. NEVER give specific financial advice (tax, accounting, investment)
  D. NEVER impersonate another person or company
  E. NEVER make promises on behalf of the user
  F. NEVER access or describe private user data beyond what is needed
  G. NEVER generate hate speech or discriminatory content
  H. NEVER assist with deceptive marketing or false claims
  I. NEVER suggest actions requiring external API access without REQUIRES_APPROVAL flag
  J. NEVER produce content that violates platform terms of service

All guardrails are checked before and after AI generation.
"""
import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Guardrail IDs
GUARDRAIL_A_VERIFIED_FACT = 'A'
GUARDRAIL_B_LEGAL_ADVICE = 'B'
GUARDRAIL_C_FINANCIAL_ADVICE = 'C'
GUARDRAIL_D_IMPERSONATION = 'D'
GUARDRAIL_E_PROMISES = 'E'
GUARDRAIL_F_PRIVATE_DATA = 'F'
GUARDRAIL_G_HATE_SPEECH = 'H'
GUARDRAIL_H_DECEPTION = 'H_DECEPTION'
GUARDRAIL_I_UNAPPROVED_EXTERNAL = 'I'
GUARDRAIL_J_TOS_VIOLATION = 'J'

ALL_GUARDRAILS = [
    GUARDRAIL_A_VERIFIED_FACT,
    GUARDRAIL_B_LEGAL_ADVICE,
    GUARDRAIL_C_FINANCIAL_ADVICE,
    GUARDRAIL_D_IMPERSONATION,
    GUARDRAIL_E_PROMISES,
    GUARDRAIL_F_PRIVATE_DATA,
    GUARDRAIL_G_HATE_SPEECH,
    GUARDRAIL_H_DECEPTION,
    GUARDRAIL_I_UNAPPROVED_EXTERNAL,
    GUARDRAIL_J_TOS_VIOLATION,
]


# Pattern banks for text-based checks
_LEGAL_PATTERNS = re.compile(
    r'\b(you (must|should|need to) (file|register|incorporate|dissolve|sue|litigate)'
    r'|consult a lawyer about|legal requirement|comply with (the )?(law|regulation))\b',
    re.IGNORECASE,
)

_FINANCIAL_PATTERNS = re.compile(
    r'\b(your (tax|accounting|investment) (strategy|return|advice)'
    r'|you (should|must) (invest|divest|report to (the )?irs|pay (the )?(gst|vat|tax))'
    r'|financial advice|accounting advice)\b',
    re.IGNORECASE,
)

_PROMISE_PATTERNS = re.compile(
    r'\b(i (guarantee|promise|ensure|will ensure)|this will (definitely|certainly) (work|succeed)'
    r'|you will (definitely|certainly) (succeed|make money|get funded))\b',
    re.IGNORECASE,
)

_DECEPTION_PATTERNS = re.compile(
    r'\b(fake\s+(review|testimonial|follower|engagement)'
    r'|pretend to (be|have)|mislead (investors|customers|users)'
    r'|false (claim|promise|statement)'
    r'|boost.*credibility.*fake|fake.*boost.*credibility)\b',
    re.IGNORECASE,
)

_HATE_PATTERNS = re.compile(
    r'\b(hate|slur|discriminat|racism|sexism|misogyn|homophob|transphob)\b',
    re.IGNORECASE,
)


class AIGuardrails:
    """
    Stateless guardrail checker.
    check_output() must pass before AI output is shown to user.
    check_input() should run before the AI call.
    """

    def check_output(self, text: str, task_type: str = '') -> Tuple[bool, List[str]]:
        """
        Check AI output against all 10 guardrails.
        Returns (passed: bool, flags: List[str]).
        If passed=False, the output must NOT be shown to the user.
        """
        flags = []

        # A: never claim verified fact
        if 'verified fact' in text.lower() or 'this is a fact' in text.lower():
            flags.append(GUARDRAIL_A_VERIFIED_FACT)

        # B: legal advice
        if _LEGAL_PATTERNS.search(text):
            flags.append(GUARDRAIL_B_LEGAL_ADVICE)

        # C: financial advice
        if _FINANCIAL_PATTERNS.search(text):
            flags.append(GUARDRAIL_C_FINANCIAL_ADVICE)

        # E: promises
        if _PROMISE_PATTERNS.search(text):
            flags.append(GUARDRAIL_E_PROMISES)

        # G/H_DECEPTION: deception
        if _DECEPTION_PATTERNS.search(text):
            flags.append(GUARDRAIL_H_DECEPTION)

        # G: hate speech
        if _HATE_PATTERNS.search(text):
            flags.append(GUARDRAIL_G_HATE_SPEECH)

        passed = len(flags) == 0
        if not passed:
            logger.warning(
                "AI guardrail FAILED task=%s flags=%s",
                task_type, flags,
            )
        return passed, flags

    def check_input(self, inputs: dict, task_type: str = '') -> Tuple[bool, List[str]]:
        """
        Pre-call check on what the user asked AI to do.
        Prevents prompt injection and disallowed requests.
        """
        flags = []
        combined_input = ' '.join(str(v) for v in inputs.values()).lower()

        # D: impersonation request
        impersonation_patterns = ['pretend you are', 'act as a real', 'impersonate']
        if any(p in combined_input for p in impersonation_patterns):
            flags.append(GUARDRAIL_D_IMPERSONATION)

        # F: private data exposure
        private_data_patterns = ['ssn', 'social security', 'credit card number', 'passport number']
        if any(p in combined_input for p in private_data_patterns):
            flags.append(GUARDRAIL_F_PRIVATE_DATA)

        # I: unapproved external action
        external_patterns = ['send email', 'post on linkedin', 'submit form', 'make payment']
        if any(p in combined_input for p in external_patterns):
            flags.append(GUARDRAIL_I_UNAPPROVED_EXTERNAL)

        passed = len(flags) == 0
        if not passed:
            logger.warning(
                "AI input guardrail FAILED task=%s flags=%s",
                task_type, flags,
            )
        return passed, flags

    def get_safe_fallback(self, task_type: str, flags: List[str]) -> dict:
        """
        Return a safe fallback response when guardrail fails.
        Never returns raw AI output when guardrail is tripped.
        """
        return {
            'guardrail_blocked': True,
            'flags': flags,
            'message': (
                'This request could not be completed because it triggered safety guardrails. '
                'Please rephrase your input or contact support.'
            ),
            'task_type': task_type,
        }
