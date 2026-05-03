"""Mentor source routing for Changepreneurship.

This service provides a country-aware source registry and recommendation layer so
Changepreneurship can decide when mentor outreach is the next logical step, which
mentor platform fits the user, and whether the source is suitable for a future
connected-account workflow.

Important: this does not perform real OAuth/API login yet. Many mentor platforms
will not expose public OAuth/API access. The registry therefore distinguishes:

- manual sources: user must copy/paste or apply manually;
- account-ready sources: the app may store a user account reference now;
- future integration candidates: later developer research needed for OAuth/API/RPA.
"""

from typing import Any, Dict, List, Optional

from src.models.mvp_infrastructure import FounderReadinessProfile


MENTOR_SOURCES: List[Dict[str, Any]] = [
    # Global access
    {
        "key": "micromentor",
        "name": "MicroMentor",
        "access_scope": "global",
        "countries": ["global"],
        "regions": ["global"],
        "cost_model": "free",
        "target_audience": ["general_entrepreneurs", "early_founders", "small_business"],
        "best_for": ["early_founder", "mentor_outreach", "general_business", "impact", "local_service"],
        "mentor_types": ["general_business", "startup", "operations", "social_impact", "marketing"],
        "execution_mode": "manual_or_future_integration",
        "connection_status": "future_connection_candidate",
        "account_connection": {
            "supported_now": True,
            "mode": "account_reference_or_manual_session",
            "fields": ["profile_url", "username_or_email", "notes"],
            "future_integration_candidate": True,
        },
        "notes": "Strong default source for free volunteer business mentoring.",
    },
    {
        "key": "adplist",
        "name": "ADPList",
        "access_scope": "global",
        "countries": ["global"],
        "regions": ["global"],
        "cost_model": "free",
        "target_audience": ["tech", "product", "founders", "designers", "business_strategists"],
        "best_for": ["digital_product", "software", "product", "design", "startup", "career_switcher"],
        "mentor_types": ["product", "design", "startup", "marketing", "business_strategy"],
        "execution_mode": "manual",
        "connection_status": "account_reference_supported",
        "account_connection": {
            "supported_now": True,
            "mode": "account_reference_or_booking_link",
            "fields": ["profile_url", "username_or_email", "booking_link", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Useful for product, startup, design, and business-strategy mentoring sessions.",
    },
    {
        "key": "pushfar",
        "name": "PushFar",
        "access_scope": "global",
        "countries": ["global"],
        "regions": ["global"],
        "cost_model": "free_for_individuals",
        "target_audience": ["professionals", "founders", "career_development"],
        "best_for": ["career_switcher", "professional", "general_business", "executive_mentor"],
        "mentor_types": ["career", "business", "executive", "entrepreneurship"],
        "execution_mode": "manual",
        "connection_status": "account_reference_supported",
        "account_connection": {
            "supported_now": True,
            "mode": "account_reference",
            "fields": ["profile_url", "username_or_email", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Good fit for career development, professionals, executives, and entrepreneurs.",
    },
    {
        "key": "gen",
        "name": "Global Entrepreneurship Network (GEN)",
        "access_scope": "global",
        "countries": ["global"],
        "regions": ["global"],
        "cost_model": "free_or_program_based",
        "target_audience": ["global_startups", "ecosystem_builders", "founders"],
        "best_for": ["global_startup", "ecosystem_connection", "local_ecosystem", "mentor_outreach"],
        "mentor_types": ["ecosystem", "startup", "local_leader", "business_strategy"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "account_reference_or_program_link",
            "fields": ["profile_url", "program_link", "country_chapter", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Useful for connecting founders to local entrepreneurship ecosystems and mentors.",
    },
    {
        "key": "cherie_blair_foundation",
        "name": "Cherie Blair Foundation mentoring",
        "access_scope": "global_targeted",
        "countries": ["global", "low_middle_income_countries"],
        "regions": ["global", "emerging_markets"],
        "cost_model": "free_or_supported_program",
        "target_audience": ["female_founders", "women_entrepreneurs"],
        "best_for": ["female_founder", "leadership", "growth", "impact", "emerging_market"],
        "mentor_types": ["women_founders", "leadership", "business_growth"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "application_or_program_reference",
            "fields": ["application_url", "profile_url", "country", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Potential fit for women entrepreneurs, especially in low- and middle-income countries.",
    },

    # North America
    {
        "key": "score",
        "name": "SCORE",
        "access_scope": "country_specific",
        "countries": ["united_states", "usa", "us"],
        "regions": ["north_america", "us", "global_virtual_resources"],
        "cost_model": "free",
        "target_audience": ["us_entrepreneurs", "small_business"],
        "best_for": ["us_business", "small_business", "local_service", "general_business"],
        "mentor_types": ["small_business", "operations", "finance", "marketing", "sales"],
        "execution_mode": "manual",
        "connection_status": "account_reference_supported",
        "account_connection": {
            "supported_now": True,
            "mode": "account_reference_or_mentor_request_link",
            "fields": ["profile_url", "username_or_email", "mentor_request_link", "chapter", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Strong for US-oriented small-business mentoring and online resources.",
    },
    {
        "key": "sbdc",
        "name": "Small Business Development Centers (SBDC)",
        "access_scope": "country_specific",
        "countries": ["united_states", "usa", "us"],
        "regions": ["north_america", "us"],
        "cost_model": "free",
        "target_audience": ["us_small_business", "local_business", "startup"],
        "best_for": ["us_business", "small_business", "local_service", "business_plan", "operations"],
        "mentor_types": ["small_business", "local_business", "finance", "operations", "marketing"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "local_center_reference",
            "fields": ["local_center_url", "advisor_name", "email", "phone", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Localized US business consulting and training; best when US location is known.",
    },
    {
        "key": "futurpreneur_canada",
        "name": "Futurpreneur Canada",
        "access_scope": "country_specific",
        "countries": ["canada", "ca"],
        "regions": ["north_america", "canada"],
        "cost_model": "free_mentoring_with_financing_options",
        "target_audience": ["young_founders", "age_18_39", "canadian_entrepreneurs"],
        "best_for": ["canada", "young_founder", "startup", "financing", "mentor_outreach"],
        "mentor_types": ["startup", "small_business", "finance", "operations"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "application_or_account_reference",
            "fields": ["application_url", "profile_url", "username_or_email", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Best for Canadian founders aged 18-39 who need mentoring and may also need financing support.",
    },
    {
        "key": "weoc",
        "name": "Women’s Enterprise Organizations of Canada (WEOC)",
        "access_scope": "country_specific",
        "countries": ["canada", "ca"],
        "regions": ["north_america", "canada"],
        "cost_model": "free_or_program_based",
        "target_audience": ["female_founders", "women_entrepreneurs", "canadian_entrepreneurs"],
        "best_for": ["canada", "female_founder", "regional_mentorship", "business_guidance"],
        "mentor_types": ["women_founders", "business", "regional_support"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "regional_program_reference",
            "fields": ["organization_url", "program_name", "contact_email", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Useful hub for Canadian women entrepreneurs and regional mentoring organizations.",
    },

    # Europe
    {
        "key": "mentorsme",
        "name": "MentorsMe",
        "access_scope": "country_specific",
        "countries": ["united_kingdom", "uk", "great_britain"],
        "regions": ["europe", "uk"],
        "cost_model": "free_directory_or_program_based",
        "target_audience": ["uk_entrepreneurs", "small_business"],
        "best_for": ["uk_business", "small_business", "mentor_directory", "local_service"],
        "mentor_types": ["small_business", "operations", "business_strategy"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "directory_reference",
            "fields": ["directory_url", "selected_organization", "contact_email", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "UK gateway to vetted business mentoring organizations.",
    },
    {
        "key": "digital_boost",
        "name": "Digital Boost",
        "access_scope": "country_specific",
        "countries": ["united_kingdom", "uk", "great_britain"],
        "regions": ["europe", "uk"],
        "cost_model": "free",
        "target_audience": ["small_business", "charities", "digital_skills"],
        "best_for": ["uk_business", "digital_skills", "marketing", "charity", "small_business"],
        "mentor_types": ["digital", "marketing", "business", "charity_support"],
        "execution_mode": "manual",
        "connection_status": "account_reference_supported",
        "account_connection": {
            "supported_now": True,
            "mode": "account_reference_or_session_link",
            "fields": ["profile_url", "username_or_email", "session_link", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Free 1:1 mentoring for UK small businesses and charities, especially digital topics.",
    },
    {
        "key": "okb",
        "name": "Stichting Ondernemersklankbord (OKB)",
        "access_scope": "country_specific",
        "countries": ["netherlands", "nl", "nederland"],
        "regions": ["europe", "netherlands"],
        "cost_model": "initial_free_then_low_donation_possible",
        "target_audience": ["dutch_entrepreneurs", "sme", "local_business", "self_employed"],
        "best_for": ["netherlands", "local_service", "sme", "side_hustler", "operations", "experienced_professional"],
        "mentor_types": ["sme", "operations", "finance", "business_strategy", "local_business"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "application_or_contact_reference",
            "fields": ["application_url", "contact_person", "email", "phone", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Strong Netherlands-specific business sounding-board option.",
    },
    {
        "key": "erasmus_young_entrepreneurs",
        "name": "Erasmus for Young Entrepreneurs",
        "access_scope": "regional",
        "countries": ["european_union", "eu"],
        "regions": ["europe", "eu"],
        "cost_model": "eu_funded_program",
        "target_audience": ["new_founders", "cross_border_learning", "eu_entrepreneurs"],
        "best_for": ["eu", "new_founder", "cross_border", "host_entrepreneur", "learning_exchange"],
        "mentor_types": ["host_entrepreneur", "business_strategy", "operations", "international"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "program_application_reference",
            "fields": ["application_url", "intermediary_organization", "country", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "EU-funded cross-border mentoring/exchange path for new entrepreneurs.",
    },

    # Asia-Pacific
    {
        "key": "startup_india_mentor_connect",
        "name": "Startup India Mentor Connect",
        "access_scope": "country_specific",
        "countries": ["india", "in"],
        "regions": ["asia_pacific", "india"],
        "cost_model": "free_or_government_program",
        "target_audience": ["registered_startups", "indian_startups"],
        "best_for": ["india", "startup", "registered_startup", "mentor_outreach", "investor_network"],
        "mentor_types": ["startup", "industry_expert", "investor", "alumni"],
        "execution_mode": "manual",
        "connection_status": "account_reference_supported",
        "account_connection": {
            "supported_now": True,
            "mode": "startup_india_account_reference",
            "fields": ["profile_url", "startup_india_id", "username_or_email", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Best for India-based registered startups seeking government ecosystem mentor matching.",
    },
    {
        "key": "byst",
        "name": "Bharatiya Yuva Shakti Trust (BYST)",
        "access_scope": "country_specific",
        "countries": ["india", "in"],
        "regions": ["asia_pacific", "india"],
        "cost_model": "free_or_supported_program",
        "target_audience": ["underprivileged_young_entrepreneurs", "youth_entrepreneurs"],
        "best_for": ["india", "young_founder", "underprivileged_founder", "grassroots_business"],
        "mentor_types": ["grassroots", "small_business", "youth_entrepreneurship"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "program_reference",
            "fields": ["program_url", "local_office", "contact_email", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Strong fit for underprivileged young entrepreneurs in India.",
    },
    {
        "key": "m4g_queensland",
        "name": "Mentoring for Growth (M4G)",
        "access_scope": "state_specific",
        "countries": ["australia", "au"],
        "regions": ["asia_pacific", "australia", "queensland"],
        "cost_model": "free_government_program",
        "target_audience": ["queensland_business", "sme", "growth_business"],
        "best_for": ["australia", "queensland", "growth_challenge", "sme", "expert_panel"],
        "mentor_types": ["business_panel", "growth", "operations", "strategy"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "program_application_reference",
            "fields": ["application_url", "business_location", "contact_email", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Queensland government mentoring panel for business-growth challenges.",
    },
    {
        "key": "business_gov_au_networks",
        "name": "Business.gov.au Networks",
        "access_scope": "country_specific",
        "countries": ["australia", "au"],
        "regions": ["asia_pacific", "australia"],
        "cost_model": "free_directory_or_government_programs",
        "target_audience": ["australian_business", "small_business", "regional_business"],
        "best_for": ["australia", "state_support", "government_advisory", "small_business"],
        "mentor_types": ["government_advisory", "business", "regional_support"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "directory_or_program_reference",
            "fields": ["program_url", "state_or_territory", "contact_email", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "National Australian hub linking to state-funded mentoring and advisory services.",
    },

    # Africa and emerging markets
    {
        "key": "tony_elumelu_foundation",
        "name": "Tony Elumelu Foundation (TEF)",
        "access_scope": "regional",
        "countries": ["africa", "pan_africa"],
        "regions": ["africa", "pan_africa", "emerging_markets"],
        "cost_model": "free_program_with_training_mentorship_and_possible_funding",
        "target_audience": ["african_entrepreneurs", "early_stage_founders"],
        "best_for": ["africa", "training", "mentorship", "funding", "early_stage_startup"],
        "mentor_types": ["startup", "training", "business", "funding_readiness"],
        "execution_mode": "manual",
        "connection_status": "account_reference_supported",
        "account_connection": {
            "supported_now": True,
            "mode": "program_account_or_application_reference",
            "fields": ["profile_url", "application_url", "country", "username_or_email", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Major Pan-African entrepreneurship program with training, mentorship, and funding pathways.",
    },
    {
        "key": "vc4a",
        "name": "VC4A (Venture Capital for Africa)",
        "access_scope": "emerging_markets",
        "countries": ["africa", "latin_america", "latam", "emerging_markets"],
        "regions": ["africa", "latin_america", "emerging_markets"],
        "cost_model": "free_or_program_based",
        "target_audience": ["startup_founders", "africa", "latam", "emerging_markets"],
        "best_for": ["africa", "latam", "startup", "investor_network", "mentor_outreach"],
        "mentor_types": ["startup", "investor", "growth", "fundraising"],
        "execution_mode": "manual",
        "connection_status": "account_reference_supported",
        "account_connection": {
            "supported_now": True,
            "mode": "account_reference_or_profile_url",
            "fields": ["profile_url", "username_or_email", "country", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Startup network for African and emerging-market founders, with mentor and investor exposure.",
    },

    # Additional sources from earlier branch context
    {
        "key": "startup_and_running",
        "name": "Startup and Running",
        "access_scope": "regional_or_virtual",
        "countries": ["netherlands", "europe", "global_virtual_possible"],
        "regions": ["europe", "netherlands", "global_virtual_possible"],
        "cost_model": "free",
        "target_audience": ["early_stage_startup", "cofounder_search", "technical_help"],
        "best_for": ["early_stage_startup", "cofounder_search", "technical_help", "mentor_outreach"],
        "mentor_types": ["startup", "technical", "cofounder", "business"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "profile_or_application_reference",
            "fields": ["profile_url", "application_url", "username_or_email", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Potential fit for early-stage startup mentors, co-founder discovery, and technical help.",
    },
    {
        "key": "ems",
        "name": "Entrepreneur Mentoring Support (EMS)",
        "access_scope": "regional",
        "countries": ["netherlands", "europe", "regional"],
        "regions": ["europe", "netherlands", "regional"],
        "cost_model": "free",
        "target_audience": ["ambitious_startups", "smes", "growth_challenges"],
        "best_for": ["ambitious_startup", "sme", "growth_challenge", "mentor_panel"],
        "mentor_types": ["startup", "sme", "growth", "strategy"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "application_or_program_reference",
            "fields": ["application_url", "program_contact", "country", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Good fit when the user needs confidential sparring with multiple experienced mentors.",
    },
    {
        "key": "growthmentor",
        "name": "GrowthMentor",
        "access_scope": "global",
        "countries": ["global"],
        "regions": ["global"],
        "cost_model": "paid_membership_with_many_free_calls_inside",
        "target_audience": ["growth", "marketing", "saas", "startup"],
        "best_for": ["growth", "marketing", "startup", "saas", "scaling"],
        "mentor_types": ["growth", "marketing", "saas", "startup", "sales"],
        "execution_mode": "manual",
        "connection_status": "account_reference_supported",
        "account_connection": {
            "supported_now": True,
            "mode": "account_reference_or_booking_link",
            "fields": ["profile_url", "username_or_email", "booking_link", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Not fully free, but useful where growth/marketing mentorship is the highest-value next step.",
    },
    {
        "key": "female_ventures",
        "name": "Female Ventures",
        "access_scope": "regional",
        "countries": ["netherlands", "europe"],
        "regions": ["netherlands", "europe"],
        "cost_model": "free_or_program_based",
        "target_audience": ["female_founders", "women_entrepreneurs"],
        "best_for": ["female_founder", "startup", "leadership", "funding"],
        "mentor_types": ["women_founders", "startup", "leadership", "funding"],
        "execution_mode": "manual",
        "connection_status": "manual_source",
        "account_connection": {
            "supported_now": True,
            "mode": "community_or_program_reference",
            "fields": ["profile_url", "program_url", "chapter", "notes"],
            "future_integration_candidate": False,
        },
        "notes": "Potential fit for women founders in the Netherlands/Europe.",
    },
]


COUNTRY_ALIASES = {
    "nl": "netherlands",
    "nederland": "netherlands",
    "the netherlands": "netherlands",
    "usa": "united_states",
    "us": "united_states",
    "u.s.": "united_states",
    "united states of america": "united_states",
    "uk": "united_kingdom",
    "great britain": "united_kingdom",
    "england": "united_kingdom",
    "ca": "canada",
    "in": "india",
    "au": "australia",
    "eu": "european_union",
    "latam": "latin_america",
}


class MentorSourceRouter:
    """Recommends mentor platforms based on country, venture context, and readiness."""

    def list_sources(self, *, country: Optional[str] = None, region: Optional[str] = None) -> List[Dict[str, Any]]:
        if not country and not region:
            return MENTOR_SOURCES
        normalized_country = self._normalize(country)
        normalized_region = self._normalize(region)
        return [
            source for source in MENTOR_SOURCES
            if self._country_or_region_matches(source, normalized_country, normalized_region)
        ]

    def connection_config(self, selected_source_key: str) -> Dict[str, Any]:
        source = self._find_source(selected_source_key) or MENTOR_SOURCES[0]
        return {
            "platform": source["key"],
            "platform_name": source["name"],
            "connection_status": source["connection_status"],
            "execution_mode": source["execution_mode"],
            "account_connection": source.get("account_connection", {}),
            "recommended_external_connection_payload": {
                "platform": source["key"],
                "connection_status": "stub",
                "scope": "mentor_source_reference",
                "permission_level": 1,
            },
        }

    def recommend(
        self,
        *,
        profile: Optional[FounderReadinessProfile] = None,
        country: Optional[str] = None,
        region: Optional[str] = None,
        venture_type: Optional[str] = None,
        founder_type: Optional[str] = None,
        mentor_need: Optional[str] = None,
        female_founder: bool = False,
        age: Optional[int] = None,
        underprivileged_founder: bool = False,
        max_results: int = 5,
    ) -> Dict[str, Any]:
        context = {
            "country": self._normalize(country),
            "region": self._normalize(region),
            "venture_type": self._normalize(venture_type),
            "founder_type": self._normalize(founder_type or getattr(profile, "founder_type", None)),
            "mentor_need": self._normalize(mentor_need),
            "female_founder": female_founder,
            "age": age,
            "underprivileged_founder": underprivileged_founder,
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

            if "global" in source["regions"] or "global" in source["countries"]:
                score += 1
                reasons.append("global access")

            if self._country_or_region_matches(source, context["country"], context["region"]):
                score += 5
                reasons.append("country/region access fit")

            if context["venture_type"] and context["venture_type"] in source["best_for"]:
                score += 3
                reasons.append(f"venture-type fit: {context['venture_type']}")

            if context["mentor_need"] and context["mentor_need"] in source["mentor_types"]:
                score += 3
                reasons.append(f"mentor-need fit: {context['mentor_need']}")

            if context["female_founder"] and "female_founders" in source["target_audience"]:
                score += 4
                reasons.append("female-founder support fit")

            if context["age"] is not None and 18 <= context["age"] <= 39 and source["key"] == "futurpreneur_canada":
                score += 4
                reasons.append("age 18-39 fit for Futurpreneur Canada")

            if context["underprivileged_founder"] and "underprivileged_young_entrepreneurs" in source["target_audience"]:
                score += 4
                reasons.append("underprivileged-founder program fit")

            if support_status in {"weak", "unknown"}:
                score += 2
                reasons.append("support-network gap detected")
            if evidence_status in {"weak", "unknown"} and any(tag in source["best_for"] for tag in ["early_founder", "early_stage_startup", "new_founder"]):
                score += 1
                reasons.append("early validation support fit")
            if idea_status in {"weak", "unknown"} and source["key"] in {"micromentor", "pushfar", "adplist", "gen"}:
                score += 1
                reasons.append("idea-clarification mentoring fit")

            # Low score sources are still returned if max_results is large, but the
            # score/reasons make it clear they are lower confidence.
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
        source = self._find_source(selected_source_key) or MENTOR_SOURCES[0]
        connection = self.connection_config(source["key"])
        return {
            "mentor_source_key": source["key"],
            "mentor_source_name": source["name"],
            "access_scope": source["access_scope"],
            "countries": source["countries"],
            "execution_mode": source["execution_mode"],
            "connection_status": source["connection_status"],
            "account_connection": connection["account_connection"],
            "goal": user_goal or "Ask a relevant mentor for practical feedback on the venture, readiness, and next step.",
            "message_template": (
                "Hello, I am working on an early-stage venture and I am looking for practical mentor feedback. "
                "My current goal is to understand whether my next step is responsible and evidence-based. "
                "Would you be open to a short mentoring conversation?"
            ),
            "notes": source["notes"],
        }

    def _find_source(self, selected_source_key: str) -> Optional[Dict[str, Any]]:
        return next((item for item in MENTOR_SOURCES if item["key"] == selected_source_key), None)

    def _normalize(self, value: Optional[str]) -> str:
        normalized = (value or "").strip().lower().replace(" ", "_").replace("-", "_")
        return COUNTRY_ALIASES.get(normalized, normalized)

    def _country_or_region_matches(self, source: Dict[str, Any], country: str, region: str) -> bool:
        countries = {self._normalize(item) for item in source.get("countries", [])}
        regions = {self._normalize(item) for item in source.get("regions", [])}
        if not country and not region:
            return False
        if country and (country in countries or country in regions):
            return True
        if region and (region in regions or region in countries):
            return True
        if country in {"netherlands", "united_kingdom", "india", "australia", "canada"} and "europe" in regions and country in {"netherlands", "united_kingdom"}:
            return True
        return False
