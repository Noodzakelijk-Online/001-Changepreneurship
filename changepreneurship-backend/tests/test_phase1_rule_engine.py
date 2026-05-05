"""
Unit tests for Phase1RuleEngine — Layer 1 Rule Engine.

Tests cover all 6 CEO prototype scenarios (Section 4.5) plus
key threshold invariants and non-compensable rules.

Run: pytest tests/test_phase1_rule_engine.py -v
"""
import pytest
from src.services.phase1_rule_engine import (
    Phase1RuleEngine,
    LEVEL_HEALTHY, LEVEL_OK, LEVEL_WARNING,
    LEVEL_SOFT_BLOCK, LEVEL_HARD_BLOCK, LEVEL_HARD_STOP,
    ROUTE_CONTINUE, ROUTE_STABILIZE, ROUTE_LOW_CAPITAL,
    ROUTE_OPERATIONS_CLEANUP, ROUTE_HARD_STOP,
    ROUTE_DEEP_TECH, ROUTE_IMPACT_SOCIAL,
    ROUTE_DEBT_CONSCIOUS, ROUTE_CORPORATE_TRANSITION,
)


@pytest.fixture
def engine():
    return Phase1RuleEngine()


# ==========================================================================
# CEO SCENARIO A: Overexcited Beginner
# Zero runway, just quit job, high passion
# Expected: Financial Hard Block, all paid actions blocked, FREE actions allowed
# ==========================================================================
class TestScenarioA:
    def test_financial_hard_block(self, engine):
        result = engine.evaluate_financial_readiness(
            runway_months=0,
            income_stable=False,
            debt_pressure_level=2,
            has_dependants=True,
        )
        assert result.level == LEVEL_HARD_BLOCK, "Zero runway must be Hard Block"
        assert len(result.blockers) == 1
        blocker = result.blockers[0]
        assert 'paid_development' in blocker['what_is_blocked']
        assert 'idea_clarification' in blocker['what_is_allowed']
        assert blocker['unlock_condition'] != ''

    def test_full_scenario_a(self, engine):
        responses = {
            'financial_runway_months': 0,
            'income_stable': False,
            'just_quit_job': True,
            'motivation_type': 'PASSION',
            'weekly_available_hours': 40,
            'stress_level': 3,
            'problem_defined': True,
            'target_user_specific': True,
            'value_prop_clear': False,
        }
        result = engine.evaluate_all(responses)

        assert result.overall_level == LEVEL_HARD_BLOCK
        assert result.recommended_route == ROUTE_STABILIZE
        # Paid dev must be blocked
        blocked_names = [b['action'] for b in result.blocked_actions]
        assert 'paid_development' in blocked_names
        # Free actions must be allowed
        assert len(result.allowed_actions) > 0
        # Scenario detected
        assert result.detected_scenario == 'OVEREXCITED_BEGINNER'
        # Founder type A (first-timer, zero runway)
        assert result.founder_type in ('A', 'B', 'C')

    def test_hard_block_not_compensable_by_high_skills(self, engine):
        """Even if skills are excellent, financial Hard Block persists."""
        responses = {
            'financial_runway_months': 0,
            'income_stable': False,
            'domain_skill_level': 5,
            'relevant_experience_years': 15,
            'execution_history': True,
        }
        result = engine.evaluate_all(responses)
        # Overall must still be Hard Block or higher
        assert result.overall_level >= LEVEL_HARD_BLOCK
        assert result.recommended_route != ROUTE_CONTINUE

    def test_hard_block_not_compensable_by_great_idea(self, engine):
        """Financial Hard Block persists even with perfect idea clarity."""
        responses = {
            'financial_runway_months': 0,
            'income_stable': False,
            'problem_defined': True,
            'target_user_specific': True,
            'value_prop_clear': True,
        }
        result = engine.evaluate_all(responses)
        assert result.overall_level >= LEVEL_HARD_BLOCK


# ==========================================================================
# CEO SCENARIO B: Experienced Professional
# Good savings, domain expertise, weak network, tendency to over-analyse
# Expected: Continue route, note on external validation needed
# ==========================================================================
class TestScenarioB:
    def test_experienced_professional_route(self, engine):
        responses = {
            'financial_runway_months': 18,
            'income_stable': True,
            'weekly_available_hours': 15,
            'stress_level': 2,
            'domain_skill_level': 5,
            'relevant_experience_years': 12,
            'execution_history': True,
            'corporate_background': True,
            'has_validated_with_real_customers': False,
            'problem_defined': True,
            'target_user_specific': True,
            'value_prop_clear': True,
            'motivation_type': 'MISSION',
            'mission_clarity': 4,
        }
        result = engine.evaluate_all(responses)
        # Should not be blocked — good financial, good skills
        assert result.overall_level <= LEVEL_WARNING
        assert result.recommended_route in (ROUTE_CONTINUE, ROUTE_CORPORATE_TRANSITION)
        assert result.detected_scenario == 'EXPERIENCED_PROFESSIONAL'

    def test_no_hard_block_with_good_runway(self, engine):
        fin = engine.evaluate_financial_readiness(
            runway_months=18,
            income_stable=True,
            debt_pressure_level=0,
        )
        assert fin.level <= LEVEL_OK


# ==========================================================================
# CEO SCENARIO C: Failed Founder — Debt-Conscious Restart
# Prior failure, debt, resilience present
# Expected: Debt-conscious restart route, block new debt/high-risk spending
# ==========================================================================
class TestScenarioC:
    def test_failed_founder_route(self, engine):
        responses = {
            'financial_runway_months': 3,
            'income_stable': False,
            'high_debt': True,
            'debt_pressure_level': 4,
            'had_previous_failed_venture': True,
            'has_debt': True,
            'weekly_available_hours': 20,
            'stress_level': 3,
            'motivation_type': 'MISSION',
            'problem_defined': True,
            'target_user_specific': True,
            'value_prop_clear': True,
        }
        result = engine.evaluate_all(responses)
        # Debt + short runway = Soft Block minimum
        assert result.overall_level >= LEVEL_SOFT_BLOCK
        assert result.detected_scenario == 'FAILED_FOUNDER_RESTART'
        assert result.recommended_route == ROUTE_DEBT_CONSCIOUS

    def test_high_debt_no_income_is_hard_block(self, engine):
        fin = engine.evaluate_financial_readiness(
            runway_months=2,
            income_stable=False,
            debt_pressure_level=5,
            high_debt=True,
        )
        assert fin.level == LEVEL_HARD_BLOCK


# ==========================================================================
# CEO SCENARIO D: Deep-Tech Innovator
# High technical skill, no commercial experience, university IP risk
# Expected: Deep-tech route, customer translation, legal IP check
# ==========================================================================
class TestScenarioD:
    def test_deep_tech_route(self, engine):
        responses = {
            'financial_runway_months': 24,  # PhD grant funding
            'income_stable': True,
            'weekly_available_hours': 30,
            'stress_level': 1,
            'domain_skill_level': 5,
            'relevant_experience_years': 8,
            'execution_history': True,
            'venture_type': 'DEEP_TECH',
            'has_commercial_experience': False,
            'employer_ip_risk': False,  # checked, cleared
            'problem_defined': True,
            'target_user_specific': True,
            'value_prop_clear': False,  # Not commercialised yet
            'motivation_type': 'MISSION',
        }
        result = engine.evaluate_all(responses)
        assert result.detected_scenario == 'DEEP_TECH_INNOVATOR'
        assert result.recommended_route == ROUTE_DEEP_TECH

    def test_employer_ip_risk_hard_block(self, engine):
        legal = engine.evaluate_legal_employment(employer_ip_risk=True)
        assert legal.level == LEVEL_HARD_BLOCK
        assert len(legal.blockers) == 1
        assert 'product_development' in legal.blockers[0]['what_is_blocked']

    def test_legal_has_priority_over_financial(self, engine):
        """Legal block (priority 1) must dominate even if financial is fine."""
        responses = {
            'financial_runway_months': 24,
            'income_stable': True,
            'illegal_venture': True,  # Hard Stop
        }
        result = engine.evaluate_all(responses)
        assert result.overall_level == LEVEL_HARD_STOP
        assert result.recommended_route == ROUTE_HARD_STOP


# ==========================================================================
# CEO SCENARIO E: Impact Visionary
# Strong mission, social/non-profit, vague funding model
# Expected: Impact/Social enterprise route
# ==========================================================================
class TestScenarioE:
    def test_impact_visionary_route(self, engine):
        responses = {
            'financial_runway_months': 6,
            'income_stable': True,
            'weekly_available_hours': 20,
            'motivation_type': 'IMPACT',
            'venture_type': 'SOCIAL',
            'funding_model_clear': False,
            'problem_defined': True,
            'target_user_specific': True,
            'value_prop_clear': True,
            'mission_clarity': 5,
        }
        result = engine.evaluate_all(responses)
        assert result.detected_scenario == 'IMPACT_VISIONARY'
        assert result.recommended_route == ROUTE_IMPACT_SOCIAL

    def test_no_market_demand_never_compensable(self, engine):
        """Idea with 'everyone is my customer' = hard block, passion doesn't compensate."""
        responses = {
            'target_user_specific': False,  # everyone
            'motivation_type': 'IMPACT',
            'mission_clarity': 5,
            'financial_runway_months': 24,
        }
        result = engine.evaluate_all(responses)
        assert result.idea_clarity.level == LEVEL_HARD_BLOCK

    def test_high_motivation_does_not_unblock_idea_clarity(self, engine):
        idea = engine.evaluate_idea_clarity(
            problem_defined=False,
            target_user_specific=True,
            value_prop_clear=True,
        )
        assert idea.level == LEVEL_HARD_BLOCK


# ==========================================================================
# CEO SCENARIO F: Accidental Entrepreneur
# 80h/week, paying customers, no systems
# Expected: Operations Cleanup route, new expansion BLOCKED
# ==========================================================================
class TestScenarioF:
    def test_operations_cleanup_route(self, engine):
        responses = {
            'financial_runway_months': 12,
            'income_stable': True,
            'weekly_available_hours': 80,
            'paying_customers_exist': True,
            'stress_level': 4,
            'burnout_signals': ['extreme_urgency', 'inability_to_complete_tasks'],
            'problem_defined': True,
            'target_user_specific': True,
            'value_prop_clear': True,
        }
        result = engine.evaluate_all(responses)
        assert result.overload_signal is True
        assert result.recommended_route == ROUTE_OPERATIONS_CLEANUP
        assert result.detected_scenario == 'ACCIDENTAL_ENTREPRENEUR'

    def test_overload_blocks_new_initiatives(self, engine):
        time = engine.evaluate_time_capacity(
            weekly_available_hours=80,
            schedule_flexibility=3,
            paying_customers_exist=True,
        )
        assert time.level == LEVEL_HARD_BLOCK
        assert len(time.blockers) > 0
        blocked = time.blockers[0]['what_is_blocked']
        assert 'new_market_expansion' in blocked

    def test_market_research_skip_for_ops_cleanup(self, engine):
        """In ops cleanup route, new expansion is blocked, ops priority."""
        responses = {
            'weekly_available_hours': 80,
            'paying_customers_exist': True,
            'financial_runway_months': 12,
            'income_stable': True,
        }
        result = engine.evaluate_all(responses)
        blocked = [b['action'] for b in result.blocked_actions]
        assert 'new_market_expansion' in blocked


# ==========================================================================
# NON-COMPENSABLE RULES (CEO Section 4.4)
# ==========================================================================
class TestNonCompensable:
    def test_illegal_venture_always_hard_stop(self, engine):
        legal = engine.evaluate_legal_employment(illegal_venture=True)
        assert legal.level == LEVEL_HARD_STOP

    def test_immigration_restriction_always_hard_stop(self, engine):
        legal = engine.evaluate_legal_employment(immigration_restriction=True)
        assert legal.level == LEVEL_HARD_STOP

    def test_zero_runway_always_blocks_paid_actions(self, engine):
        fin = engine.evaluate_financial_readiness(
            runway_months=0,
            income_stable=False,
            debt_pressure_level=0,
        )
        assert fin.level == LEVEL_HARD_BLOCK
        blocked = fin.blockers[0]['what_is_blocked']
        assert 'paid_development' in blocked

    def test_acute_crisis_always_stops(self, engine):
        stability = engine.evaluate_personal_stability(
            stress_level=5,
            burnout_signals=[],
            life_chaos_signals=[],
            acute_personal_crisis=True,
        )
        assert stability.level == LEVEL_HARD_STOP

    def test_financial_crisis_combination_is_hard_stop(self, engine):
        """High debt + no income + dependants = Level 5 (not just 4)."""
        fin = engine.evaluate_financial_readiness(
            runway_months=0,
            income_stable=False,
            debt_pressure_level=5,
            has_dependants=True,
            high_debt=True,
        )
        assert fin.level == LEVEL_HARD_STOP


# ==========================================================================
# COMPOSITE SCORING INVARIANTS
# ==========================================================================
class TestCompositeInvariants:
    def test_worst_case_wins_not_average(self, engine):
        """If one dimension is Hard Block, overall must be Hard Block."""
        responses = {
            # Perfect scores everywhere...
            'domain_skill_level': 5,
            'income_stable': True,
            'financial_runway_months': 24,
            'weekly_available_hours': 40,
            'stress_level': 0,
            'burnout_signals': [],
            'life_chaos_signals': [],
            'problem_defined': True,
            'target_user_specific': True,
            'value_prop_clear': True,
            # ...but illegal venture
            'illegal_venture': True,
        }
        result = engine.evaluate_all(responses)
        assert result.overall_level == LEVEL_HARD_STOP, \
            "Hard Stop must propagate regardless of other dimension scores"

    def test_level_5_always_propagates(self, engine):
        """Any single Level 5 dimension = overall Level 5."""
        responses = {
            'acute_personal_crisis': True,
            'financial_runway_months': 100,
            'income_stable': True,
        }
        result = engine.evaluate_all(responses)
        assert result.overall_level == LEVEL_HARD_STOP

    def test_healthy_all_dimensions_gives_continue(self, engine):
        responses = {
            'financial_runway_months': 18,
            'income_stable': True,
            'high_debt': False,
            'weekly_available_hours': 20,
            'stress_level': 1,
            'burnout_signals': [],
            'life_chaos_signals': [],
            'problem_defined': True,
            'target_user_specific': True,
            'value_prop_clear': True,
            'domain_skill_level': 4,
            'relevant_experience_years': 5,
            'execution_history': True,
            'illegal_venture': False,
            'employer_ip_risk': False,
            'energy_level': 4,
            'motivation_type': 'MISSION',
            'mission_clarity': 4,
        }
        result = engine.evaluate_all(responses)
        assert result.overall_level <= LEVEL_OK
        assert result.recommended_route == ROUTE_CONTINUE

    def test_single_soft_block_does_not_stop_all_activity(self, engine):
        """Soft Block allows some actions."""
        responses = {
            'financial_runway_months': 2,  # Soft Block
            'income_stable': False,
        }
        result = engine.evaluate_all(responses)
        assert result.overall_level <= LEVEL_SOFT_BLOCK
        # Must have allowed actions
        assert len(result.allowed_actions) > 0


# ==========================================================================
# INDIVIDUAL DIMENSION THRESHOLD TESTS
# ==========================================================================
class TestFinancialThresholds:
    def test_12_months_runway_stable_is_healthy(self, engine):
        r = engine.evaluate_financial_readiness(12, True, 0)
        assert r.level == LEVEL_HEALTHY

    def test_6_months_is_ok(self, engine):
        r = engine.evaluate_financial_readiness(6, True, 0)
        assert r.level == LEVEL_OK

    def test_3_months_is_warning(self, engine):
        r = engine.evaluate_financial_readiness(4, True, 0)
        assert r.level == LEVEL_WARNING

    def test_2_months_is_soft_block(self, engine):
        r = engine.evaluate_financial_readiness(2, False, 0)
        assert r.level == LEVEL_SOFT_BLOCK

    def test_0_months_is_hard_block(self, engine):
        r = engine.evaluate_financial_readiness(0, False, 0)
        assert r.level == LEVEL_HARD_BLOCK

    def test_all_blockers_have_unlock_conditions(self, engine):
        """Every blocker must have a non-empty unlock_condition."""
        r = engine.evaluate_financial_readiness(0, False, 0)
        for blocker in r.blockers:
            assert blocker.get('unlock_condition'), \
                f"Blocker {blocker['type']} missing unlock_condition"


class TestTimeCapacityThresholds:
    def test_20h_is_healthy(self, engine):
        r = engine.evaluate_time_capacity(20)
        assert r.level == LEVEL_HEALTHY

    def test_10h_is_ok(self, engine):
        r = engine.evaluate_time_capacity(10)
        assert r.level == LEVEL_OK

    def test_6h_is_warning(self, engine):
        r = engine.evaluate_time_capacity(6)
        assert r.level == LEVEL_WARNING

    def test_4h_is_soft_block(self, engine):
        r = engine.evaluate_time_capacity(4)
        assert r.level == LEVEL_SOFT_BLOCK

    def test_1h_is_hard_block(self, engine):
        r = engine.evaluate_time_capacity(1)
        assert r.level == LEVEL_HARD_BLOCK

    def test_80h_with_customers_is_hard_block(self, engine):
        r = engine.evaluate_time_capacity(80, paying_customers_exist=True)
        assert r.level == LEVEL_HARD_BLOCK


class TestIdeaClarityThresholds:
    def test_everyone_is_customer_hard_blocks_market_research(self, engine):
        r = engine.evaluate_idea_clarity(
            problem_defined=True,
            target_user_specific=False,
            value_prop_clear=True,
        )
        assert r.level == LEVEL_HARD_BLOCK
        assert any('market_research' in b['what_is_blocked'] for b in r.blockers)

    def test_no_problem_defined_hard_blocks(self, engine):
        r = engine.evaluate_idea_clarity(
            problem_defined=False,
            target_user_specific=True,
            value_prop_clear=True,
        )
        assert r.level == LEVEL_HARD_BLOCK

    def test_clear_idea_specific_user_is_ok(self, engine):
        r = engine.evaluate_idea_clarity(
            problem_defined=True,
            target_user_specific=True,
            value_prop_clear=True,
        )
        assert r.level <= LEVEL_OK


class TestLegalPriority:
    def test_legal_priority_over_everything(self, engine):
        """Routing priority: legal (1) beats financial (2)."""
        responses = {
            'financial_runway_months': 0,  # Financial Hard Block
            'income_stable': False,
            'employer_ip_risk': True,  # Legal Hard Block too
        }
        result = engine.evaluate_all(responses)
        # Both are hard blocks — overall must be hard block
        assert result.overall_level >= LEVEL_HARD_BLOCK
        # Legal block must be present
        legal_blockers = [
            b for b in result.active_blockers
            if b['dimension'] == 'legal_employment'
        ]
        assert len(legal_blockers) > 0
