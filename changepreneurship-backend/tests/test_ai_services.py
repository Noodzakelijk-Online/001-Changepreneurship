"""
Tests — AI Layer 3 services (Sprint 5)
Tests: S5-01 (AI Contract), S5-02 (Guardrails), S5-03 (Confidence), S5-04 (Cost Manager)
"""
import pytest

from src.services.ai_layer3_contract import (
    AIInputContract, AIOutputContract,
    AI_TASK_GENERATE_CVC, AI_TASK_GENERATE_ASSUMPTIONS,
    build_cvc_input, build_assumptions_input,
    ALL_AI_TASKS,
)
from src.services.ai_guardrails import (
    AIGuardrails,
    GUARDRAIL_A_VERIFIED_FACT,
    GUARDRAIL_B_LEGAL_ADVICE,
    GUARDRAIL_C_FINANCIAL_ADVICE,
    GUARDRAIL_E_PROMISES,
    GUARDRAIL_H_DECEPTION,
)
from src.services.ai_confidence_service import (
    AIConfidenceService,
    CONFIDENCE_SPECULATIVE,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_HIGH,
    CONFIDENCE_VERIFIED,
)
from src.services.ai_cost_manager import AICostManager


# ---------------------------------------------------------------------------
# S5-01: AI Contract
# ---------------------------------------------------------------------------
class TestAIInputContract:
    def test_valid_contract_passes(self):
        contract = AIInputContract(
            task_type=AI_TASK_GENERATE_CVC,
            user_id=1,
            inputs={'idea_description': 'SaaS tool', 'problem': 'Teams waste time'},
        )
        contract.validate()  # Should not raise

    def test_unknown_task_type_raises(self):
        contract = AIInputContract(
            task_type='INVALID_TASK',
            user_id=1,
            inputs={'x': 'y'},
        )
        with pytest.raises(ValueError, match='Unknown AI task type'):
            contract.validate()

    def test_empty_inputs_raises(self):
        contract = AIInputContract(
            task_type=AI_TASK_GENERATE_CVC,
            user_id=1,
            inputs={},
        )
        with pytest.raises(ValueError, match='inputs cannot be empty'):
            contract.validate()

    def test_max_tokens_limit(self):
        contract = AIInputContract(
            task_type=AI_TASK_GENERATE_CVC,
            user_id=1,
            inputs={'x': 'y'},
            max_tokens=9999,
        )
        with pytest.raises(ValueError, match='max_tokens'):
            contract.validate()

    def test_build_cvc_input_helper(self):
        responses = {
            'idea_description': 'Project management app',
            'target_user_description': 'remote teams',
            'problem_description': 'async coordination fails',
            'value_prop': 'saves 5h/week',
        }
        contract = build_cvc_input(user_id=42, responses=responses)
        assert contract.task_type == AI_TASK_GENERATE_CVC
        assert contract.user_id == 42
        assert 'idea_description' in contract.inputs

    def test_all_ai_tasks_defined(self):
        assert len(ALL_AI_TASKS) >= 6


class TestAIOutputContract:
    def test_to_audit_dict_has_required_keys(self):
        output = AIOutputContract(
            task_type=AI_TASK_GENERATE_CVC,
            user_id=1,
            output={'problem_statement': 'Teams struggle with async'},
            confidence_label=CONFIDENCE_MEDIUM,
            confidence_score=0.65,
            guardrail_passed=True,
            model_used='llama-3.3-70b-versatile',
            tokens_used=450,
        )
        audit = output.to_audit_dict()
        assert 'confidence_label' in audit
        assert 'guardrail_passed' in audit
        assert 'tokens_used' in audit
        assert 'input_hash' in audit


# ---------------------------------------------------------------------------
# S5-02: Guardrails
# ---------------------------------------------------------------------------
class TestAIGuardrails:
    def setup_method(self):
        self.g = AIGuardrails()

    def test_clean_output_passes(self):
        text = 'Here are three assumptions to test for your venture idea.'
        passed, flags = self.g.check_output(text, AI_TASK_GENERATE_ASSUMPTIONS)
        assert passed is True
        assert flags == []

    def test_verified_fact_claim_flagged(self):
        text = 'This is a verified fact: remote teams always struggle with coordination.'
        passed, flags = self.g.check_output(text)
        assert not passed
        assert GUARDRAIL_A_VERIFIED_FACT in flags

    def test_legal_advice_flagged(self):
        text = 'You must file your company as an LLC before you can raise funding.'
        passed, flags = self.g.check_output(text)
        assert not passed
        assert GUARDRAIL_B_LEGAL_ADVICE in flags

    def test_promise_flagged(self):
        text = 'I guarantee this strategy will definitely work for your venture.'
        passed, flags = self.g.check_output(text)
        assert not passed
        assert GUARDRAIL_E_PROMISES in flags

    def test_deception_flagged(self):
        text = 'You could use fake reviews to boost your initial credibility.'
        passed, flags = self.g.check_output(text)
        assert not passed
        assert GUARDRAIL_H_DECEPTION in flags

    def test_input_impersonation_flagged(self):
        passed, flags = self.g.check_input(
            {'request': 'Pretend you are a real investor and promise funding'},
        )
        assert not passed

    def test_safe_fallback_returned_on_failure(self):
        text = 'This is a verified fact about your venture.'
        passed, flags = self.g.check_output(text)
        fallback = self.g.get_safe_fallback('GENERATE_CVC', flags)
        assert fallback['guardrail_blocked'] is True
        assert 'flags' in fallback


# ---------------------------------------------------------------------------
# S5-03: Confidence Service
# ---------------------------------------------------------------------------
class TestAIConfidenceService:
    def setup_method(self):
        self.svc = AIConfidenceService()

    def test_rich_inputs_give_medium_or_higher(self):
        inputs = {
            'idea_description': 'A task manager for freelancers',
            'problem_description': 'They lose 3h/week to manual invoicing',
            'target_user': 'solo freelancers with 3+ clients',
            'value_prop': 'Saves 3h/week via automation',
        }
        assessment = self.svc.assess_confidence(
            AI_TASK_GENERATE_CVC, inputs, 'output text', context_richness=4,
        )
        assert assessment.label in (CONFIDENCE_MEDIUM, CONFIDENCE_HIGH)

    def test_empty_inputs_give_speculative_or_low(self):
        inputs = {'idea': ''}
        assessment = self.svc.assess_confidence(
            AI_TASK_GENERATE_CVC, inputs, 'output', context_richness=0,
        )
        assert assessment.label in (CONFIDENCE_SPECULATIVE, CONFIDENCE_LOW)

    def test_ai_cannot_produce_verified(self):
        assert not self.svc.can_upgrade_to_verified(source='ai')

    def test_human_can_produce_verified(self):
        assert self.svc.can_upgrade_to_verified(source='user')
        assert self.svc.can_upgrade_to_verified(source='behavioral')

    def test_assumptions_labelled_speculative_when_ai_no_evidence(self):
        label = self.svc.label_assumption(source='ai', evidence_count=0)
        assert label == CONFIDENCE_SPECULATIVE

    def test_assumptions_upgraded_with_evidence(self):
        label_0 = self.svc.label_assumption(source='user', evidence_count=0)
        label_3 = self.svc.label_assumption(source='user', evidence_count=3)
        assert CONFIDENCE_ORDER.index(label_3) > CONFIDENCE_ORDER.index(label_0)

    def test_caveats_present_for_speculative(self):
        inputs = {'x': ''}
        assessment = self.svc.assess_confidence(AI_TASK_GENERATE_CVC, inputs, '', context_richness=0)
        assert len(assessment.caveats) > 0

    def test_can_act_on_medium_or_higher(self):
        inputs = {
            'idea_description': 'Clear idea',
            'problem_description': 'Clear problem',
            'target_user': 'Clear audience',
            'value_prop': 'Clear value',
        }
        assessment = self.svc.assess_confidence(
            AI_TASK_GENERATE_CVC, inputs, 'output', context_richness=6,
        )
        if assessment.label in (CONFIDENCE_MEDIUM, CONFIDENCE_HIGH):
            assert assessment.can_act_on is True


CONFIDENCE_ORDER = [CONFIDENCE_SPECULATIVE, CONFIDENCE_LOW, CONFIDENCE_MEDIUM, CONFIDENCE_HIGH, CONFIDENCE_VERIFIED]


# ---------------------------------------------------------------------------
# S5-04: Cost Manager
# ---------------------------------------------------------------------------
class TestAICostManager:
    def setup_method(self):
        self.mgr = AICostManager()

    def test_estimate_returns_cost(self):
        estimate = self.mgr.estimate_cost('GENERATE_CVC', 'Some input text about the venture idea')
        assert estimate.estimated_total_tokens > 0
        assert estimate.estimated_cost_usd >= 0

    def test_within_budget(self):
        assert self.mgr.check_budget(1, tokens_needed=500, session_tokens_used=1000) is True

    def test_over_budget(self):
        assert self.mgr.check_budget(
            1, tokens_needed=5000, session_tokens_used=9500, session_budget=10000,
        ) is False

    def test_free_alternative_available_for_cvc(self):
        estimate = self.mgr.estimate_cost('GENERATE_CVC', 'input')
        assert estimate.free_alternative_available is True
        assert estimate.free_alternative_method == 'template_cvc'

    def test_should_use_free_when_over_budget(self):
        result = self.mgr.should_use_free(
            'GENERATE_CVC', session_tokens_used=9000, budget=10000,
        )
        assert result is True

    def test_no_free_alternative_for_unknown_task(self):
        alternatives = self.mgr.get_free_alternatives('SOME_UNKNOWN_TASK')
        assert alternatives == []

    def test_record_usage_returns_dict(self):
        usage = self.mgr.record_usage(
            user_id=1, tokens_used=300,
            task_type='GENERATE_CVC', model='llama-3.3-70b-versatile',
        )
        assert 'cost_usd' in usage
        assert usage['tokens_used'] == 300
