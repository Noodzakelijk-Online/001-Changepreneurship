"""Mentor source routing for Changepreneurship.

This service does not integrate with external mentor platforms yet. It provides a
structured registry and recommendation layer so the AI/product can decide when
mentor outreach is the right next step and which source is most appropriate.

External connection/OAuth/API work can later plug into the selected source.
"""

from typing import Any, Dict, List, Optional

from src.models.mvp_infrastructure import FounderReadinessProfile


MENTOR_SOURCES: List[Dict[str, Any]] = [
    {
        "key": "micromentor",
        "name": "MicroMentor",
        "cost_model": "free",
        "regions": ["global"],
        "best_for": ["early_founder", "mentor_outreach", "general_business", "impact", "local_service"],
        "mentor_types": ["general_business", "startup", "operations", "social_impact", "marketing"],
        "execution_mode": "manual_or_future_integration",
        "connection_status": "future_connection_candidate",
        "notes": "Strong default source for free volunteer business mentoring.",
    },
    {
        "key": "adplist",
        "name": "ADPList",
        "cost_model": "free",
        "regions": ["global"],
        "best_for": ["digital_product", "software", "product", "design", "startup", "career_switcher"],
        "mentor_types": ["product", "design", "startup", "marketing", "business_strategy"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "notes": "Useful for product, startup, design, and business-strategy mentoring sessions.",
    },
    {
        "key": "pushfar",
        "name": "PushFar",
        "cost_model": "free_for_individuals",
        "regions": ["global"],
        "best_for": ["career_switcher", "professional", "general_business", "executive_mentor"],
        "mentor_types": ["career", "business", "executive", "entrepreneurship"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "notes": "Good fit for career development, professionals, executives, and entrepreneurs.",
    },
    {
        "key": "score",
        "name": "SCORE",
        "cost_model": "free",
        "regions": ["us", "global_virtual_resources"],
        "best_for": ["us_business", "small_business", "local_service", "general_business"],
        "mentor_types": ["small_business", "operations", "finance", "marketing", "sales"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "notes": "Strong for US-oriented small-business mentoring and online resources.",
    },
    {
        "key": "okb",
        "name": "Stichting Ondernemersklankbord (OKB)",
        "cost_model": "initial_free_then_low_donation_possible",
        "regions": ["netherlands"],
        "best_for": ["netherlands", "local_service", "sme", "side_hustler", "operations", "experienced_professional"],
        "mentor_types": ["sme", "operations", "finance", "business_strategy", "local_business"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "notes": "Strong Netherlands-specific business sounding-board option.",
    },
    {
        "key": "startup_and_running",
        "name": "Startup and Running",
        "cost_model": "free",
        "regions": ["europe", "netherlands", "global_virtual_possible"],
        "best_for": ["early_stage_startup", "cofounder_search", "technical_help", "mentor_outreach"],
        "mentor_types": ["startup", "technical", "cofounder", "business"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "notes": "Potential fit for early-stage startup mentors, co-founder discovery, and technical help.",
    },
    {
        "key": "ems",
        "name": "Entrepreneur Mentoring Support (EMS)",
        "cost_model": "free",
        "regions": ["europe", "netherlands", "regional"],
        "best_for": ["ambitious_startup", "sme", "growth_challenge", "mentor_panel"],
        "mentor_types": ["startup", "sme", "growth", "strategy"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "notes": "Good fit when the user needs confidential sparring with multiple experienced mentors.",
    },
    {
        "key": "growthmentor",
        "name": "GrowthMentor",
        "cost_model": "paid_membership_with_many_free_calls_inside",
        "regions": ["global"],
        "best_for": ["growth", "marketing", "startup", "saas", "scaling"],
        "mentor_types": ["growth", "marketing", "saas", "startup", "sales"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "notes": "Not fully free, but useful where growth/marketing mentorship is the highest-value next step.",
    },
    {
        "key": "cherie_blair_foundation",
        "name": "Cherie Blair Foundation mentoring",
        "cost_model": "free_or_supported_program",
        "regions": ["global"],
        "best_for": ["female_founder", "leadership", "growth", "impact"],
        "mentor_types": ["women_founders", "leadership", "business_growth"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "notes": "Potential fit for women entrepreneurs seeking structured mentoring support.",
    },
    {
        "key": "female_ventures",
        "name": "Female Ventures",
        "cost_model": "free_or_program_based",
        "regions": ["netherlands", "europe"],
        "best_for": ["female_founder", "startup", "leadership", "funding"],
        "mentor_types": ["women_founders", "startup", "leadership", "funding"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "notes": "Potential fit for women founders in the Netherlands/Europe.",
    },
]


class MentorSourceRouter:
    """Recommends mentor platforms based on venture context and readiness."""

    def list_sources(self) -> List[Dict[str, Any]]:
        return MENTOR_SOURCES

    def recommend(
        self,
        *,
        profile: Optional[FounderReadinessProfile] = None,
        region: Optional[str] = None,
        venture_type: Optional[str] = None,
        founder_type: Optional[str] = None,
        mentor_need: Optional[str] = None,
        female_founder: bool = False,
        max_results: int = 5,
    ) -> Dict[str, Any]:
        context = {
            "region": (region or "").lower(),
            "venture_type": (venture_type or "").lower(),
            "founder_type": (founder_type or getattr(profile, "founder_type", None) or "").lower(),
            "mentor_need": (mentor_need or "").lower(),
            "female_founder": female_founder,
        }

        if profile:
            dims = {name: profile.get_dimension(name) for name in profile.DIMENSIONS}
            support_status = dims.get("support_network", {}).get("status", "unknown")
            evidence_status = dims.get("evidence_discipline", {}).get("status", "unknown")
            idea_status = dims.get("founder_idea_fit", {}).get("status", "unknown")
        else:
            support_status = "unknown"
            evidence_status = "unknown"
            idea_status = "unknown"

        scored = []
        for source in MENTOR_SOURCES:
            score = 0
            reasons = []

            if "global" in source["regions"]:
                score += 1
            if context["region"] and context["region"] in source["regions"]:
                score += 4
                reasons.append(f"regional fit: {context['region']}")
            if context["venture_type"] and context["venture_type"] in source["best_for"]:
                score += 3
                reasons.append(f"venture-type fit: {context['venture_type']}")
            if context["mentor_need"] and context["mentor_need"] in source["mentor_types"]:
                score += 3
                reasons.append(f"mentor-need fit: {context['mentor_need']}")
            if context["female_founder"] and "female_founder" in source["best_for"]:
                score += 4
                reasons.append("female-founder support fit")

            if support_status in {"weak", "unknown"}:
                score += 2
                reasons.append("support-network gap detected")
            if evidence_status in {"weak", "unknown"} and "early_founder" in source["best_for"]:
                score += 1
                reasons.append("early validation support fit")
            if idea_status in {"weak", "unknown"} and source["key"] in {"micromentor", "pushfar", "adplist"}:
                score += 1
                reasons.append("idea-clarification mentoring fit")

            scored.append({**source, "score": score, "reasons": reasons or ["general mentor-source fit"]})

        scored.sort(key=lambda item: item["score"], reverse=True)
        recommendations = scored[:max_results]

        should_route_to_mentor = support_status in {"weak", "unknown"} or context["mentor_need"] != ""
        return {
            "should_route_to_mentor": should_route_to_mentor,
            "route_reason": "Mentor support is recommended because a support-network gap or mentor need was detected." if should_route_to_mentor else "Mentor routing is optional; no urgent support-network gap was detected.",
            "recommendations": recommendations,
            "context": context,
        }

    def outreach_payload(self, *, selected_source_key: str, user_goal: Optional[str] = None) -> Dict[str, Any]:
        source = next((item for item in MENTOR_SOURCES if item["key"] == selected_source_key), None)
        if not source:
            source = MENTOR_SOURCES[0]
        return {
            "mentor_source_key": source["key"],
            "mentor_source_name": source["name"],
            "execution_mode": source["execution_mode"],
            "goal": user_goal or "Ask a relevant mentor for practical feedback on the venture, readiness, and next step.",
            "message_template": (
                "Hello, I am working on an early-stage venture and I am looking for practical mentor feedback. "
                "My current goal is to understand whether my next step is responsible and evidence-based. "
                "Would you be open to a short mentoring conversation?"
            ),
            "notes": source["notes"],
        }
