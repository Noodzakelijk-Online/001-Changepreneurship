"""
Mock LLM service for testing consensus flow without real API keys.
Simulates responses from multiple models with realistic variations.
"""
import random
from typing import Optional, Dict, Any


class MockLLMClient:
    """Mock LLM client that returns deterministic but varied responses for testing."""
    
    def __init__(self):
        self.model = "mock-gpt-4o-mini"
        self.call_count = 0
    
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        self.call_count += 1
        
        # Simulate different model "perspectives" based on call order
        if "executive summary" in prompt.lower() or "business readiness" in prompt.lower():
            return self._generate_executive_summary(self.call_count)
        
        # Peer review responses
        if "minority claim" in prompt.lower() or "re-check" in prompt.lower():
            return self._generate_peer_review(prompt, self.call_count)
        
        return self._generate_generic_insight(self.call_count)
    
    def _generate_executive_summary(self, variant: int) -> str:
        """Generate executive summary with slight variations per model."""
        common_findings = [
            "Strong product-market fit evidenced by 85% Sean Ellis score",
            "Excellent traction with 77% weekly active users",
            "Solid revenue foundation with $1.2K MRR from 4 paying customers",
            "Advanced market understanding in project management SaaS space",
            "Visionary leadership profile with 8 years product experience",
        ]
        
        unique_findings = {
            1: [
                "High risk tolerance enabling rapid iteration",
                "Clear competitive moat through AI automation features",
            ],
            2: [
                "Exceptional customer retention (0% churn over 2 months)",
                "Strong network effects from team collaboration features",
            ],
            3: [
                "Underutilized viral growth potential from word-of-mouth",
                "Premium pricing opportunity in enterprise segment",
            ],
        }
        
        # Model 1 finds common + unique 1
        # Model 2 finds common + unique 2
        # Model 3 finds common + unique 3 (minority findings)
        
        model_num = ((variant - 1) % 3) + 1
        findings = common_findings + unique_findings.get(model_num, [])
        
        return "\n".join([f"- {f}" for f in findings])
    
    def _generate_peer_review(self, prompt: str, variant: int) -> str:
        """Generate peer review response for minority claims."""
        # Extract claim from prompt
        if "viral growth" in prompt.lower():
            if variant % 2 == 0:
                return "CONFIRM niche insight: Reviewed user acquisition data. 6 organic referrals in 2 months with zero marketing spend validates viral coefficient >1.0. This is a genuine competitive advantage that initial analysis missed."
            else:
                return "REJECT as hallucination: Cannot find evidence in provided data supporting viral growth claim. The 6 referrals mentioned are insufficient sample size and may be explained by founder network rather than product virality."
        
        if "premium pricing" in prompt.lower():
            if variant % 2 == 1:
                return "CONFIRM niche insight: Re-analyzing customer segments reveals 2 of 4 paying customers are mid-market (50+ employees) paying 3x base price. Clear willingness to pay premium for enterprise features like SSO and advanced permissions."
            else:
                return "REJECT as hallucination: Current pricing is already at market rate for similar tools. No data supports premium tier demand without additional enterprise features that aren't in roadmap."
        
        # Default: random verdict
        if variant % 2 == 0:
            return "CONFIRM niche insight with supporting evidence from detailed assessment responses."
        else:
            return "REJECT as hallucination - claim not substantiated by available data."
    
    def _generate_generic_insight(self, variant: int) -> str:
        """Generic insight generation."""
        insights = [
            "Strong execution capabilities demonstrated",
            "Clear go-to-market strategy identified",
            "Solid financial planning with realistic projections",
        ]
        return insights[variant % len(insights)]
