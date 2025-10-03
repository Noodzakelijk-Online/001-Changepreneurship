from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json

purpose_discovery_bp = Blueprint('purpose_discovery', __name__)


class PurposeDiscoveryModule:
    def __init__(self):
        self.five_whys_questions = [
            "What motivates you to start a business?",
            "Why is that important to you?",
            "Why does that matter in your life?",
            "What deeper need does this fulfill?",
            "What is the ultimate impact you want to make?",
        ]

        self.legacy_prompts = [
            "How do you want to be remembered?",
            "What problem in the world keeps you up at night?",
            "If you could solve one major challenge, what would it be?",
            "What would success look like in 20 years?",
            "What legacy do you want to leave behind?",
        ]

        self.impact_categories = [
            "Environmental Impact",
            "Social Impact",
            "Economic Impact",
            "Educational Impact",
            "Health & Wellness Impact",
            "Technology Innovation Impact",
        ]

    def process_five_whys(self, responses):
        """Process the 5 Whys exercise responses and extract core purpose"""
        if len(responses) != 5:
            return {"error": "All 5 questions must be answered"}

        purpose_analysis = {
            "core_motivations": self._extract_motivations(responses),
            "purpose_clarity_score": self._calculate_clarity_score(responses),
            "recommended_focus_areas": self._identify_focus_areas(responses),
            "next_steps": self._generate_next_steps(responses),
        }

        return purpose_analysis

    def _extract_motivations(self, responses):
        """Extract key motivational themes from responses"""
        motivation_keywords = {
            "impact": ["help", "change", "improve", "solve", "impact"],
            "freedom": ["freedom", "independence", "control", "flexibility"],
            "legacy": ["legacy", "remember", "future", "generations"],
            "passion": ["love", "passionate", "excited", "enjoy"],
            "financial": ["money", "financial", "wealth", "income"],
        }

        motivations = {}
        for category, keywords in motivation_keywords.items():
            score = 0
            for response in responses:
                for keyword in keywords:
                    if keyword.lower() in response.lower():
                        score += 1
            motivations[category] = score

        return motivations

    def _calculate_clarity_score(self, responses):
        """Calculate how clear the user's purpose is based on response quality"""
        total_length = sum(len(response.split()) for response in responses)
        specificity_score = min(total_length / 50, 10)

        clarity_indicators = ["because", "specifically", "exactly", "precisely"]
        clarity_bonus = sum(
            1
            for response in responses
            for indicator in clarity_indicators
            if indicator in response.lower()
        )

        return min(specificity_score + clarity_bonus, 10)

    def _identify_focus_areas(self, responses):
        """Identify recommended business focus areas based on responses"""
        focus_areas = []
        combined_text = " ".join(responses).lower()

        area_keywords = {
            "Technology": ["technology", "digital", "software", "app", "platform"],
            "Healthcare": ["health", "medical", "wellness", "care", "treatment"],
            "Education": ["education", "learning", "teaching", "knowledge", "skills"],
            "Environment": ["environment", "green", "sustainable", "climate", "eco"],
            "Social Impact": ["community", "social", "people", "society", "equality"],
        }

        for area, keywords in area_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                focus_areas.append(area)

        return focus_areas[:3]

    def _generate_next_steps(self, responses):
        """Generate personalized next steps based on purpose discovery"""
        return [
            "Refine your purpose statement based on your core motivations",
            "Research successful entrepreneurs in your identified focus areas",
            "Connect with communities aligned with your purpose",
            "Develop a personal mission statement",
            "Identify specific problems you're passionate about solving",
        ]

    def create_legacy_statement(self, legacy_responses, values, vision):
        """Create a personal legacy statement"""
        legacy_statement = {
            "statement": self._generate_legacy_statement(legacy_responses, values, vision),
            "core_values": values,
            "vision": vision,
            "action_items": self._generate_legacy_actions(legacy_responses),
        }
        return legacy_statement

    def _generate_legacy_statement(self, responses, values, vision):
        """Generate a cohesive legacy statement"""
        template = (
            f"I am committed to {vision} by living my values of {', '.join(values)} "
            f"and creating lasting impact through {responses[0]}."
        )
        return template

    def _generate_legacy_actions(self, responses):
        """Generate actionable steps toward legacy goals"""
        return [
            "Define specific metrics for measuring your impact",
            "Identify key stakeholders who will benefit from your work",
            "Create a timeline for achieving your legacy goals",
            "Establish partnerships that align with your mission",
            "Document your journey to inspire others",
        ]

    def visualize_impact(self, impact_areas, scale, timeline):
        """Create impact visualization data"""
        impact_data = {
            "impact_map": self._create_impact_map(impact_areas, scale),
            "timeline_projection": self._create_timeline_projection(timeline),
            "stakeholder_analysis": self._analyze_stakeholders(impact_areas),
            "measurement_framework": self._create_measurement_framework(impact_areas),
        }
        return impact_data

    def _create_impact_map(self, impact_areas, scale):
        """Create a visual map of potential impact"""
        impact_map = {}
        for area in impact_areas:
            impact_map[area] = {
                "potential_reach": scale.get(area, 0),
                "difficulty_level": self._assess_difficulty(area),
                "resource_requirements": self._assess_resources(area),
            }
        return impact_map

    def _create_timeline_projection(self, timeline):
        """Create timeline projections for impact goals"""
        projections = {}
        for milestone, timeframe in timeline.items():
            projections[milestone] = {
                "target_date": timeframe,
                "key_activities": self._generate_activities(milestone),
                "success_metrics": self._define_metrics(milestone),
            }
        return projections

    def _analyze_stakeholders(self, impact_areas):
        """Analyze key stakeholders for each impact area"""
        stakeholder_map = {
            "Environmental Impact": [
                "Environmental groups",
                "Government agencies",
                "Local communities",
            ],
            "Social Impact": [
                "Non-profits",
                "Community leaders",
                "Beneficiary groups",
            ],
            "Economic Impact": [
                "Investors",
                "Employees",
                "Customers",
                "Local economy",
            ],
            "Educational Impact": [
                "Students",
                "Educators",
                "Institutions",
                "Parents",
            ],
            "Health & Wellness Impact": [
                "Patients",
                "Healthcare providers",
                "Insurance companies",
            ],
            "Technology Innovation Impact": [
                "Tech community",
                "Early adopters",
                "Industry partners",
            ],
        }

        relevant_stakeholders = {}
        for area in impact_areas:
            if area in stakeholder_map:
                relevant_stakeholders[area] = stakeholder_map[area]

        return relevant_stakeholders

    def _create_measurement_framework(self, impact_areas):
        """Create framework for measuring impact"""
        metrics = {
            "Environmental Impact": [
                "Carbon footprint reduction",
                "Waste reduction",
                "Energy savings",
            ],
            "Social Impact": [
                "Lives improved",
                "Communities served",
                "Social problems addressed",
            ],
            "Economic Impact": [
                "Jobs created",
                "Revenue generated",
                "Economic growth",
            ],
            "Educational Impact": [
                "Students educated",
                "Skills developed",
                "Knowledge transferred",
            ],
            "Health & Wellness Impact": [
                "Health outcomes improved",
                "Lives saved",
                "Wellness metrics",
            ],
            "Technology Innovation Impact": [
                "Innovations created",
                "Efficiency gains",
                "Problems solved",
            ],
        }

        framework = {}
        for area in impact_areas:
            if area in metrics:
                framework[area] = metrics[area]

        return framework

    def _assess_difficulty(self, area):
        """Assess difficulty level for impact area"""
        difficulty_levels = {
            "Environmental Impact": 8,
            "Social Impact": 7,
            "Economic Impact": 6,
            "Educational Impact": 5,
            "Health & Wellness Impact": 9,
            "Technology Innovation Impact": 7,
        }
        return difficulty_levels.get(area, 5)

    def _assess_resources(self, area):
        """Assess resource requirements for impact area"""
        resource_levels = {
            "Environmental Impact": "High",
            "Social Impact": "Medium",
            "Economic Impact": "High",
            "Educational Impact": "Medium",
            "Health & Wellness Impact": "Very High",
            "Technology Innovation Impact": "High",
        }
        return resource_levels.get(area, "Medium")

    def _generate_activities(self, milestone):
        """Generate key activities for milestone"""
        return [
            f"Research and planning for {milestone}",
            f"Build partnerships for {milestone}",
            f"Develop resources for {milestone}",
            f"Execute strategy for {milestone}",
            f"Measure and optimize {milestone}",
        ]

    def _define_metrics(self, milestone):
        """Define success metrics for milestone"""
        return [
            f"Completion rate for {milestone}",
            f"Quality score for {milestone}",
            f"Impact measurement for {milestone}",
            f"Stakeholder satisfaction for {milestone}",
        ]


@purpose_discovery_bp.route('/five-whys', methods=['POST'])
def process_five_whys():
    """Process 5 Whys exercise"""
    try:
        data = request.get_json()
        responses = data.get('responses', [])

        module = PurposeDiscoveryModule()
        result = module.process_five_whys(responses)

        session['five_whys_result'] = result

        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@purpose_discovery_bp.route('/legacy-statement', methods=['POST'])
def create_legacy_statement():
    """Create legacy statement"""
    try:
        data = request.get_json()
        legacy_responses = data.get('legacy_responses', [])
        values = data.get('values', [])
        vision = data.get('vision', '')

        module = PurposeDiscoveryModule()
        result = module.create_legacy_statement(legacy_responses, values, vision)

        session['legacy_statement'] = result

        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@purpose_discovery_bp.route('/impact-visualization', methods=['POST'])
def create_impact_visualization():
    """Create impact visualization"""
    try:
        data = request.get_json()
        impact_areas = data.get('impact_areas', [])
        scale = data.get('scale', {})
        timeline = data.get('timeline', {})

        module = PurposeDiscoveryModule()
        result = module.visualize_impact(impact_areas, scale, timeline)

        session['impact_visualization'] = result

        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@purpose_discovery_bp.route('/summary', methods=['GET'])
def get_purpose_summary():
    """Get complete purpose discovery summary"""
    try:
        summary = {
            "five_whys": session.get('five_whys_result'),
            "legacy_statement": session.get('legacy_statement'),
            "impact_visualization": session.get('impact_visualization'),
            "completion_date": datetime.now().isoformat(),
        }

        return jsonify({"success": True, "data": summary})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
