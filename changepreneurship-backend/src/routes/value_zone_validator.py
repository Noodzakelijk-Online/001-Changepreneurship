import flask
from flask import Blueprint, request, jsonify
from datetime import datetime

value_zone_bp = Blueprint('value_zone', __name__)


class ValueZoneValidator:
    def __init__(self):
        self.passion_categories = [
            "Technology & Innovation",
            "Health & Wellness",
            "Education & Learning",
            "Environment & Sustainability",
            "Arts & Creativity",
            "Finance & Investment",
            "Social Impact & Community",
            "Sports & Fitness",
            "Travel & Adventure",
            "Food & Nutrition",
            "Fashion & Beauty",
            "Entertainment & Media",
        ]

        self.skill_categories = [
            "Technical Skills",
            "Creative Skills",
            "Analytical Skills",
            "Communication Skills",
            "Leadership Skills",
            "Sales & Marketing",
            "Financial Management",
            "Operations Management",
            "Product Development",
            "Customer Service",
            "Strategic Planning",
            "Problem Solving",
        ]

        self.market_indicators = {
            "market_size": "Total addressable market size",
            "growth_rate": "Annual market growth rate",
            "competition_level": "Level of competition",
            "customer_willingness": "Customer willingness to pay",
            "market_trends": "Current market trends",
            "barriers_to_entry": "Barriers to market entry",
        }

        self.market_data = {
            "Technology & Innovation": {
                "market_size": 5000000000,
                "growth_rate": 0.15,
                "competition_level": "High",
                "trends": ["AI/ML", "Cloud Computing", "Cybersecurity"],
            },
            "Health & Wellness": {
                "market_size": 4500000000,
                "growth_rate": 0.12,
                "competition_level": "Medium",
                "trends": ["Telemedicine", "Mental Health", "Preventive Care"],
            },
            "Education & Learning": {
                "market_size": 3000000000,
                "growth_rate": 0.10,
                "competition_level": "Medium",
                "trends": ["Online Learning", "Skill Development", "EdTech"],
            },
        }

    def analyze_passions(self, passion_responses):
        """Analyze user's passions and interests"""
        passion_analysis = {
            "primary_passions": self._identify_primary_passions(passion_responses),
            "passion_intensity": self._calculate_passion_intensity(passion_responses),
            "passion_alignment": self._assess_passion_alignment(passion_responses),
            "recommended_focus": self._recommend_passion_focus(passion_responses),
        }

        return passion_analysis

    def _identify_primary_passions(self, responses):
        """Identify the user's primary passion areas"""
        passion_scores = {}

        for category in self.passion_categories:
            score = 0
            category_lower = category.lower()

            for response in responses.values():
                if isinstance(response, str):
                    response_lower = response.lower()
                    if any(
                        word in response_lower for word in category_lower.split()
                    ):
                        score += 1
                elif isinstance(response, (int, float)):
                    if category in responses and response > 7:
                        score += response

            passion_scores[category] = score

        sorted_passions = sorted(
            passion_scores.items(), key=lambda x: x[1], reverse=True
        )
        return [passion[0] for passion in sorted_passions[:3]]

    def _calculate_passion_intensity(self, responses):
        """Calculate overall passion intensity"""
        total_score = 0
        count = 0

        for response in responses.values():
            if isinstance(response, (int, float)):
                total_score += response
                count += 1

        return total_score / count if count > 0 else 0

    def _assess_passion_alignment(self, responses):
        """Assess how well passions align with business potential"""
        alignment_score = 0

        business_keywords = ["solve", "help", "improve", "create", "build", "impact"]

        for response in responses.values():
            if isinstance(response, str):
                for keyword in business_keywords:
                    if keyword.lower() in response.lower():
                        alignment_score += 1

        return min(alignment_score / len(business_keywords), 1.0)

    def _recommend_passion_focus(self, responses):
        """Recommend specific focus areas within passions"""
        recommendations = []
        primary_passions = self._identify_primary_passions(responses)

        focus_map = {
            "Technology & Innovation": [
                "AI/ML applications",
                "Mobile apps",
                "SaaS platforms",
            ],
            "Health & Wellness": [
                "Digital health",
                "Fitness tech",
                "Mental wellness",
            ],
            "Education & Learning": [
                "Online courses",
                "Skill platforms",
                "Educational tools",
            ],
        }

        for passion in primary_passions:
            if passion in focus_map:
                recommendations.extend(focus_map[passion])

        return recommendations[:5]

    def analyze_skills(self, skill_responses, experience_data):
        """Analyze user's skills and capabilities"""
        skill_analysis = {
            "core_skills": self._identify_core_skills(skill_responses),
            "skill_levels": self._assess_skill_levels(skill_responses, experience_data),
            "skill_gaps": self._identify_skill_gaps(skill_responses),
            "skill_development_plan": self._create_skill_development_plan(
                skill_responses
            ),
            "competitive_advantages": self._identify_competitive_advantages(
                skill_responses, experience_data
            ),
        }

        return skill_analysis

    def _identify_core_skills(self, responses):
        """Identify user's core skills"""
        skill_scores = {}

        for skill_category in self.skill_categories:
            score = responses.get(skill_category, 0)
            if isinstance(score, (int, float)) and score >= 7:
                skill_scores[skill_category] = score

        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
        return [skill[0] for skill in sorted_skills]

    def _assess_skill_levels(self, responses, experience_data):
        """Assess skill levels with experience context"""
        skill_levels = {}

        for skill, rating in responses.items():
            if isinstance(rating, (int, float)):
                experience_years = experience_data.get(skill, 0)
                adjusted_rating = min(rating + (experience_years * 0.5), 10)

                if adjusted_rating >= 8:
                    level = "Expert"
                elif adjusted_rating >= 6:
                    level = "Advanced"
                elif adjusted_rating >= 4:
                    level = "Intermediate"
                else:
                    level = "Beginner"

                skill_levels[skill] = {
                    "rating": rating,
                    "experience_years": experience_years,
                    "adjusted_rating": adjusted_rating,
                    "level": level,
                }

        return skill_levels

    def _identify_skill_gaps(self, responses):
        """Identify critical skill gaps for entrepreneurship"""
        essential_skills = [
            "Leadership Skills",
            "Sales & Marketing",
            "Financial Management",
            "Strategic Planning",
            "Communication Skills",
        ]

        gaps = []
        for skill in essential_skills:
            rating = responses.get(skill, 0)
            if rating < 6:
                gaps.append(
                    {
                        "skill": skill,
                        "current_level": rating,
                        "target_level": 7,
                        "priority": "High" if rating < 4 else "Medium",
                    }
                )

        return gaps

    def _create_skill_development_plan(self, responses):
        """Create a personalized skill development plan"""
        gaps = self._identify_skill_gaps(responses)

        development_plan = []
        for gap in gaps:
            plan_item = {
                "skill": gap["skill"],
                "current_level": gap["current_level"],
                "target_level": gap["target_level"],
                "recommended_actions": self._get_skill_development_actions(
                    gap["skill"]
                ),
                "timeline": "3-6 months" if gap["priority"] == "High" else "6-12 months",
                "resources": self._get_skill_resources(gap["skill"]),
            }
            development_plan.append(plan_item)

        return development_plan

    def _get_skill_development_actions(self, skill):
        """Get recommended actions for skill development"""
        action_map = {
            "Leadership Skills": [
                "Take leadership courses",
                "Practice team management",
                "Seek mentorship",
                "Lead volunteer projects",
            ],
            "Sales & Marketing": [
                "Study sales methodologies",
                "Practice pitching",
                "Learn digital marketing",
                "Analyze successful campaigns",
            ],
            "Financial Management": [
                "Learn financial modeling",
                "Study accounting basics",
                "Practice budgeting",
                "Understand investment principles",
            ],
        }

        return action_map.get(
            skill, ["Study fundamentals", "Practice regularly", "Seek feedback"]
        )

    def _get_skill_resources(self, skill):
        """Get recommended resources for skill development"""
        resource_map = {
            "Leadership Skills": [
                "Harvard Business Review Leadership courses",
                "Dale Carnegie Leadership Training",
                "Local leadership workshops",
            ],
            "Sales & Marketing": [
                "HubSpot Academy",
                "Google Digital Marketing courses",
                "Sales training programs",
            ],
            "Financial Management": [
                "Coursera Financial Management courses",
                "Khan Academy Finance",
                "Local business finance workshops",
            ],
        }

        return resource_map.get(skill, ["Online courses", "Books", "Workshops"])

    def _identify_competitive_advantages(self, responses, experience_data):
        """Identify unique competitive advantages from skills"""
        advantages = []

        high_skills = [
            skill
            for skill, rating in responses.items()
            if isinstance(rating, (int, float)) and rating >= 8
        ]

        if len(high_skills) >= 2:
            advantages.append(
                {
                    "type": "Skill Combination",
                    "description": f"Unique combination of {' and '.join(high_skills[:2])}",
                    "strength": "High",
                }
            )

        for skill, rating in responses.items():
            experience_years = experience_data.get(skill, 0)
            if rating >= 9 and experience_years >= 5:
                advantages.append(
                    {
                        "type": "Deep Expertise",
                        "description": f"Expert-level {skill} with {experience_years} years experience",
                        "strength": "Very High",
                    }
                )

        return advantages

    def analyze_market_demand(self, business_ideas, target_markets):
        """Analyze market demand for business ideas"""
        market_analysis = {}

        for idea in business_ideas:
            analysis = {
                "market_size": self._get_market_size(idea, target_markets),
                "growth_rate": self._get_growth_rate(idea),
                "competition_analysis": self._analyze_competition(idea),
                "customer_demand": self._assess_customer_demand(idea),
                "market_trends": self._get_market_trends(idea),
                "opportunity_score": 0,
            }

            analysis["opportunity_score"] = self._calculate_opportunity_score(analysis)
            market_analysis[idea] = analysis

        return market_analysis

    def _get_market_size(self, idea, target_markets):
        """Get market size data for business idea"""
        for market in target_markets:
            if market in self.market_data:
                return self.market_data[market]["market_size"]

        return 1000000000

    def _get_growth_rate(self, idea):
        """Get market growth rate"""
        return 0.08

    def _analyze_competition(self, idea):
        """Analyze competition level"""
        return {
            "level": "Medium",
            "key_competitors": ["Competitor A", "Competitor B"],
            "market_share_distribution": {"Leader": 30, "Others": 70},
            "differentiation_opportunities": [
                "Better UX",
                "Lower cost",
                "Niche focus",
            ],
        }

    def _assess_customer_demand(self, idea):
        """Assess customer demand indicators"""
        return {
            "search_volume": 50000,
            "willingness_to_pay": "High",
            "pain_point_severity": "Medium",
            "current_solutions": "Limited",
        }

    def _get_market_trends(self, idea):
        """Get relevant market trends"""
        return [
            "Digital transformation",
            "Remote work adoption",
            "Sustainability focus",
            "AI integration",
        ]

    def _calculate_opportunity_score(self, analysis):
        """Calculate overall market opportunity score"""
        score = 0

        market_size = analysis["market_size"]
        if market_size > 1000000000:
            score += 3
        elif market_size > 100000000:
            score += 2
        else:
            score += 1

        growth_rate = analysis["growth_rate"]
        if growth_rate > 0.15:
            score += 3
        elif growth_rate > 0.08:
            score += 2
        else:
            score += 1

        competition_level = analysis["competition_analysis"]["level"]
        if competition_level == "Low":
            score += 3
        elif competition_level == "Medium":
            score += 2
        else:
            score += 1

        return min(score, 10)

    def find_value_zone(self, passion_analysis, skill_analysis, market_analysis):
        """Find the intersection of passion, skills, and market demand"""
        value_zones = []

        top_passions = passion_analysis["primary_passions"]
        core_skills = skill_analysis["core_skills"]

        for passion in top_passions:
            for skill in core_skills[:3]:
                matching_opportunities = self._find_matching_opportunities(
                    passion, skill, market_analysis
                )

                if matching_opportunities:
                    value_zone = {
                        "passion": passion,
                        "skill": skill,
                        "opportunities": matching_opportunities,
                        "zone_score": self._calculate_zone_score(
                            passion, skill, matching_opportunities
                        ),
                        "recommended_actions": self._get_zone_recommendations(
                            passion, skill
                        ),
                        "success_probability": self._estimate_success_probability(
                            passion_analysis, skill_analysis, matching_opportunities
                        ),
                    }
                    value_zones.append(value_zone)

        value_zones.sort(key=lambda x: x["zone_score"], reverse=True)

        return value_zones[:5]

    def _find_matching_opportunities(self, passion, skill, market_analysis):
        """Find business opportunities that match passion-skill combination"""
        opportunities = []

        opportunity_map = {
            ("Technology & Innovation", "Technical Skills"): [
                "SaaS platform development",
                "Mobile app creation",
                "AI/ML consulting",
            ],
            ("Health & Wellness", "Communication Skills"): [
                "Health coaching platform",
                "Wellness content creation",
                "Telemedicine services",
            ],
            ("Education & Learning", "Creative Skills"): [
                "Educational content creation",
                "Online course development",
                "Learning app design",
            ],
        }

        key = (passion, skill)
        if key in opportunity_map:
            for opp in opportunity_map[key]:
                if opp in market_analysis:
                    opportunities.append(
                        {"opportunity": opp, "market_data": market_analysis[opp]}
                    )

        return opportunities

    def _calculate_zone_score(self, passion, skill, opportunities):
        """Calculate value zone score"""
        base_score = 5

        if opportunities:
            avg_opportunity_score = sum(
                opp["market_data"]["opportunity_score"] for opp in opportunities
            ) / len(opportunities)
            base_score += avg_opportunity_score / 2

        return min(base_score, 10)

    def _get_zone_recommendations(self, passion, skill):
        """Get recommendations for value zone"""
        return [
            f"Develop expertise in {passion} applications",
            f"Leverage {skill} for competitive advantage",
            "Validate market demand through customer interviews",
            "Build minimum viable product",
            "Network with industry professionals",
        ]

    def _estimate_success_probability(
        self, passion_analysis, skill_analysis, opportunities
    ):
        """Estimate probability of success in this value zone"""
        base_probability = 0.3

        passion_intensity = passion_analysis["passion_intensity"]
        base_probability += (passion_intensity / 10) * 0.2

        if skill_analysis["core_skills"]:
            base_probability += 0.2

        if opportunities:
            avg_market_score = sum(
                opp["market_data"]["opportunity_score"] for opp in opportunities
            ) / len(opportunities)
            base_probability += (avg_market_score / 10) * 0.3

        return min(base_probability, 0.9)


@value_zone_bp.route('/analyze-passions', methods=['POST'])
def analyze_passions():
    """Analyze user passions"""
    try:
        data = request.get_json()
        passion_responses = data.get('passion_responses', {})

        validator = ValueZoneValidator()
        analysis = validator.analyze_passions(passion_responses)

        flask.session['passion_analysis'] = analysis

        return jsonify({"success": True, "data": analysis})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@value_zone_bp.route('/analyze-skills', methods=['POST'])
def analyze_skills():
    """Analyze user skills"""
    try:
        data = request.get_json()
        skill_responses = data.get('skill_responses', {})
        experience_data = data.get('experience_data', {})

        validator = ValueZoneValidator()
        analysis = validator.analyze_skills(skill_responses, experience_data)

        flask.session['skill_analysis'] = analysis

        return jsonify({"success": True, "data": analysis})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@value_zone_bp.route('/analyze-market', methods=['POST'])
def analyze_market():
    """Analyze market demand"""
    try:
        data = request.get_json()
        business_ideas = data.get('business_ideas', [])
        target_markets = data.get('target_markets', [])

        validator = ValueZoneValidator()
        analysis = validator.analyze_market_demand(business_ideas, target_markets)

        flask.session['market_analysis'] = analysis

        return jsonify({"success": True, "data": analysis})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@value_zone_bp.route('/find-zones', methods=['POST'])
def find_value_zones():
    """Find value zones intersection"""
    try:
        passion_analysis = flask.session.get('passion_analysis')
        skill_analysis = flask.session.get('skill_analysis')
        market_analysis = flask.session.get('market_analysis')

        if not all([passion_analysis, skill_analysis, market_analysis]):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Complete passion, skill, and market analysis required",
                    }
                ),
                400,
            )

        validator = ValueZoneValidator()
        value_zones = validator.find_value_zone(
            passion_analysis, skill_analysis, market_analysis
        )

        flask.session['value_zones'] = value_zones

        return jsonify({"success": True, "data": value_zones})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@value_zone_bp.route('/complete-analysis', methods=['GET'])
def get_complete_analysis():
    """Get complete value zone analysis"""
    try:
        complete_analysis = {
            "passion_analysis": flask.session.get('passion_analysis'),
            "skill_analysis": flask.session.get('skill_analysis'),
            "market_analysis": flask.session.get('market_analysis'),
            "value_zones": flask.session.get('value_zones'),
            "analysis_date": datetime.now().isoformat(),
        }

        return jsonify({"success": True, "data": complete_analysis})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
