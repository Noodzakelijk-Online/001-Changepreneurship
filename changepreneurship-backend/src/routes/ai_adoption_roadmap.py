from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
import json
import uuid

ai_adoption_bp = Blueprint('ai_adoption', __name__)


class AIAdoptionRoadmap:
    def __init__(self):
        self.ai_categories = {
            "automation": {
                "name": "Process Automation",
                "description": "Automate repetitive tasks and workflows",
                "examples": [
                    "Customer service chatbots",
                    "Invoice processing",
                    "Data entry automation",
                ],
                "complexity": "Low",
                "roi_timeline": "3-6 months",
            },
            "analytics": {
                "name": "Data Analytics & Insights",
                "description": "Extract insights from business data",
                "examples": [
                    "Customer behavior analysis",
                    "Sales forecasting",
                    "Market trend analysis",
                ],
                "complexity": "Medium",
                "roi_timeline": "6-12 months",
            },
            "personalization": {
                "name": "Personalization & Recommendations",
                "description": "Deliver personalized experiences to customers",
                "examples": [
                    "Product recommendations",
                    "Content personalization",
                    "Dynamic pricing",
                ],
                "complexity": "Medium",
                "roi_timeline": "6-18 months",
            },
            "prediction": {
                "name": "Predictive Analytics",
                "description": "Predict future outcomes and trends",
                "examples": [
                    "Demand forecasting",
                    "Risk assessment",
                    "Maintenance prediction",
                ],
                "complexity": "High",
                "roi_timeline": "12-24 months",
            },
            "generation": {
                "name": "Content & Code Generation",
                "description": "Generate content, code, and creative assets",
                "examples": [
                    "Marketing copy",
                    "Code generation",
                    "Design assets",
                ],
                "complexity": "Medium",
                "roi_timeline": "3-9 months",
            },
            "optimization": {
                "name": "Business Optimization",
                "description": "Optimize business processes and decisions",
                "examples": [
                    "Supply chain optimization",
                    "Resource allocation",
                    "Pricing optimization",
                ],
                "complexity": "High",
                "roi_timeline": "12-36 months",
            },
        }

        self.industry_ai_opportunities = {
            "E-commerce": {
                "high_impact": ["personalization", "analytics", "automation"],
                "medium_impact": ["prediction", "generation"],
                "low_impact": ["optimization"],
            },
            "Healthcare": {
                "high_impact": ["prediction", "analytics", "automation"],
                "medium_impact": ["personalization", "optimization"],
                "low_impact": ["generation"],
            },
            "Education": {
                "high_impact": ["personalization", "generation", "analytics"],
                "medium_impact": ["automation", "prediction"],
                "low_impact": ["optimization"],
            },
            "Finance": {
                "high_impact": ["prediction", "analytics", "automation"],
                "medium_impact": ["optimization", "personalization"],
                "low_impact": ["generation"],
            },
            "Manufacturing": {
                "high_impact": ["optimization", "prediction", "automation"],
                "medium_impact": ["analytics"],
                "low_impact": ["personalization", "generation"],
            },
            "Retail": {
                "high_impact": ["personalization", "analytics", "prediction"],
                "medium_impact": ["automation", "generation"],
                "low_impact": ["optimization"],
            },
        }

        self.ai_vendors = {
            "automation": [
                {"name": "UiPath", "type": "RPA", "complexity": "Medium", "cost": "$$"},
                {
                    "name": "Zapier",
                    "type": "Workflow",
                    "complexity": "Low",
                    "cost": " $",
                },
                {
                    "name": "Microsoft Power Automate",
                    "type": "Workflow",
                    "complexity": "Low",
                    "cost": "$",
                },
            ],
            "analytics": [
                {"name": "Tableau", "type": "BI", "complexity": "Medium", "cost": "$$$"},
                {
                    "name": "Google Analytics Intelligence",
                    "type": "Web Analytics",
                    "complexity": "Low",
                    "cost": "$",
                },
                {
                    "name": "IBM Watson Analytics",
                    "type": "Advanced Analytics",
                    "complexity": "High",
                    "cost": "$$$",
                },
            ],
            "generation": [
                {"name": "OpenAI GPT", "type": "Text Generation", "complexity": "Low", "cost": "$$"},
                {
                    "name": "Jasper AI",
                    "type": "Marketing Content",
                    "complexity": "Low",
                    "cost": "$$",
                },
                {
                    "name": "GitHub Copilot",
                    "type": "Code Generation",
                    "complexity": "Medium",
                    "cost": "$",
                },
            ],
        }

        self.data_strategy_components = {
            "collection": {
                "name": "Data Collection",
                "description": "Systematic gathering of relevant business data",
                "key_areas": [
                    "Customer data",
                    "Operational data",
                    "Market data",
                    "Financial data",
                ],
            },
            "storage": {
                "name": "Data Storage & Management",
                "description": "Secure and scalable data storage solutions",
                "key_areas": [
                    "Cloud storage",
                    "Data warehousing",
                    "Data lakes",
                    "Security protocols",
                ],
            },
            "processing": {
                "name": "Data Processing & Cleaning",
                "description": "Preparing data for analysis and AI applications",
                "key_areas": [
                    "Data cleaning",
                    "ETL processes",
                    "Data validation",
                    "Quality assurance",
                ],
            },
            "analysis": {
                "name": "Data Analysis & Insights",
                "description": "Extracting actionable insights from data",
                "key_areas": [
                    "Statistical analysis",
                    "Machine learning",
                    "Visualization",
                    "Reporting",
                ],
            },
            "governance": {
                "name": "Data Governance",
                "description": "Policies and procedures for data management",
                "key_areas": [
                    "Privacy compliance",
                    "Access controls",
                    "Data lineage",
                    "Audit trails",
                ],
            },
        }

    def assess_ai_readiness(self, business_profile):
        """Assess business readiness for AI adoption"""
        readiness_score = 0
        readiness_factors = {}

        data_score = self._assess_data_readiness(business_profile.get('data_status', {}))
        readiness_factors['data_readiness'] = data_score
        readiness_score += data_score * 0.3

        tech_score = self._assess_technical_infrastructure(
            business_profile.get('tech_infrastructure', {})
        )
        readiness_factors['technical_infrastructure'] = tech_score
        readiness_score += tech_score * 0.25

        team_score = self._assess_team_capabilities(business_profile.get('team_skills', {}))
        readiness_factors['team_capabilities'] = team_score
        readiness_score += team_score * 0.2

        financial_score = self._assess_financial_readiness(
            business_profile.get('financial_status', {})
        )
        readiness_factors['financial_readiness'] = financial_score
        readiness_score += financial_score * 0.15

        strategic_score = self._assess_strategic_alignment(
            business_profile.get('business_goals', {})
        )
        readiness_factors['strategic_alignment'] = strategic_score
        readiness_score += strategic_score * 0.1

        readiness_assessment = {
            "overall_score": round(readiness_score, 2),
            "readiness_level": self._determine_readiness_level(readiness_score),
            "factor_scores": readiness_factors,
            "recommendations": self._generate_readiness_recommendations(
                readiness_factors
            ),
            "next_steps": self._suggest_readiness_next_steps(readiness_score),
        }

        return readiness_assessment

    def _assess_data_readiness(self, data_status):
        score = 0
        if data_status.get('has_customer_data', False):
            score += 2
        if data_status.get('has_operational_data', False):
            score += 2
        if data_status.get('has_financial_data', False):
            score += 1

        data_quality = data_status.get('data_quality', 'poor')
        if data_quality == 'excellent':
            score += 3
        elif data_quality == 'good':
            score += 2
        elif data_quality == 'fair':
            score += 1

        if data_status.get('has_data_warehouse', False):
            score += 2

        return min(score, 10)

    def _assess_technical_infrastructure(self, tech_infrastructure):
        score = 0

        cloud_level = tech_infrastructure.get('cloud_adoption', 'none')
        if cloud_level == 'full':
            score += 3
        elif cloud_level == 'partial':
            score += 2
        elif cloud_level == 'basic':
            score += 1

        if tech_infrastructure.get('has_apis', False):
            score += 2

        integration_level = tech_infrastructure.get('integration_capabilities', 'low')
        if integration_level == 'high':
            score += 3
        elif integration_level == 'medium':
            score += 2
        elif integration_level == 'low':
            score += 1

        if tech_infrastructure.get('has_security_protocols', False):
            score += 2

        return min(score, 10)

    def _assess_team_capabilities(self, team_skills):
        score = 0
        if team_skills.get('has_data_scientists', False):
            score += 3
        if team_skills.get('has_developers', False):
            score += 2
        if team_skills.get('has_analysts', False):
            score += 2

        ai_literacy = team_skills.get('ai_literacy_level', 'low')
        if ai_literacy == 'high':
            score += 3
        elif ai_literacy == 'medium':
            score += 2
        elif ai_literacy == 'low':
            score += 1

        return min(score, 10)

    def _assess_financial_readiness(self, financial_status):
        score = 0

        ai_budget = financial_status.get('ai_budget', 0)
        if ai_budget >= 100000:
            score += 4
        elif ai_budget >= 50000:
            score += 3
        elif ai_budget >= 10000:
            score += 2
        elif ai_budget > 0:
            score += 1

        revenue_stability = financial_status.get('revenue_stability', 'unstable')
        if revenue_stability == 'stable':
            score += 3
        elif revenue_stability == 'growing':
            score += 4
        elif revenue_stability == 'declining':
            score += 1

        roi_timeline = financial_status.get('expected_roi_timeline', 'long')
        if roi_timeline == 'short':
            score += 2
        elif roi_timeline == 'medium':
            score += 3

        return min(score, 10)

    def _assess_strategic_alignment(self, business_goals):
        score = 5
        ai_aligned_goals = [
            'efficiency_improvement',
            'customer_experience_enhancement',
            'data_driven_decisions',
            'automation',
            'innovation',
        ]
        for goal in ai_aligned_goals:
            if business_goals.get(goal, False):
                score += 1
        return min(score, 10)

    def _determine_readiness_level(self, score):
        if score >= 8:
            return "High - Ready for advanced AI implementation"
        elif score >= 6:
            return "Medium - Ready for basic AI implementation with preparation"
        elif score >= 4:
            return "Low - Significant preparation needed before AI adoption"
        else:
            return "Not Ready - Focus on foundational capabilities first"

    def _generate_readiness_recommendations(self, factor_scores):
        recommendations = []
        if factor_scores['data_readiness'] < 6:
            recommendations.append("Improve data collection and quality processes")
        if factor_scores['technical_infrastructure'] < 6:
            recommendations.append("Upgrade technical infrastructure and cloud capabilities")
        if factor_scores['team_capabilities'] < 6:
            recommendations.append("Invest in team training and AI literacy")
        if factor_scores['financial_readiness'] < 6:
            recommendations.append("Secure adequate budget for AI initiatives")
        if factor_scores['strategic_alignment'] < 6:
            recommendations.append("Align AI strategy with business objectives")
        return recommendations

    def _suggest_readiness_next_steps(self, score):
        if score >= 8:
            return [
                "Begin with pilot AI projects",
                "Identify high-impact use cases",
                "Select AI vendors and partners",
                "Develop implementation timeline",
            ]
        elif score >= 6:
            return [
                "Address identified readiness gaps",
                "Start with low-complexity AI solutions",
                "Build internal AI capabilities",
                "Create AI governance framework",
            ]
        elif score >= 4:
            return [
                "Focus on data infrastructure development",
                "Invest in team training",
                "Establish data governance policies",
                "Build foundational technical capabilities",
            ]
        else:
            return [
                "Develop basic data collection processes",
                "Improve technical infrastructure",
                "Build team capabilities",
                "Secure necessary funding",
            ]

    def identify_ai_opportunities(self, business_profile, industry):
        opportunities = []
        industry_opps = self.industry_ai_opportunities.get(industry, {})
        for ai_category in industry_opps.get('high_impact', []):
            if ai_category in self.ai_categories:
                opportunity = self._create_opportunity(ai_category, 'High', business_profile)
                opportunities.append(opportunity)
        for ai_category in industry_opps.get('medium_impact', []):
            if ai_category in self.ai_categories:
                opportunity = self._create_opportunity(ai_category, 'Medium', business_profile)
                opportunities.append(opportunity)
        custom_opps = self._identify_custom_opportunities(business_profile)
        opportunities.extend(custom_opps)
        opportunities.sort(key=lambda x: (x['impact_score'], x['feasibility_score']), reverse=True)
        return opportunities[:10]

    def _create_opportunity(self, ai_category, impact_level, business_profile):
        category_info = self.ai_categories[ai_category]
        opportunity = {
            "id": str(uuid.uuid4()),
            "category": ai_category,
            "name": category_info["name"],
            "description": category_info["description"],
            "examples": category_info["examples"],
            "impact_level": impact_level,
            "impact_score": self._calculate_impact_score(impact_level),
            "feasibility_score": self._calculate_feasibility_score(
                category_info, business_profile
            ),
            "complexity": category_info["complexity"],
            "roi_timeline": category_info["roi_timeline"],
            "estimated_cost": self._estimate_implementation_cost(
                ai_category, business_profile
            ),
            "potential_benefits": self._identify_potential_benefits(
                ai_category, business_profile
            ),
            "implementation_steps": self._generate_implementation_steps(ai_category),
            "success_metrics": self._define_success_metrics(ai_category),
        }
        return opportunity

    def _calculate_impact_score(self, impact_level):
        impact_scores = {"High": 9, "Medium": 6, "Low": 3}
        return impact_scores.get(impact_level, 5)

    def _calculate_feasibility_score(self, category_info, business_profile):
        """Calculate feasibility score based on complexity and business readiness"""
        complexity_scores = {"Low": 8, "Medium": 6, "High": 4}
        base_score = complexity_scores.get(category_info["complexity"], 5)
        if business_profile.get('tech_readiness', 0) > 7:
            base_score += 1
        if business_profile.get('team_readiness', 0) > 7:
            base_score += 1
        return min(base_score, 10)

    def _estimate_implementation_cost(self, ai_category, business_profile):
        """Estimate implementation cost"""
        base_costs = {
            "automation": {"small": 5000, "medium": 25000, "large": 100000},
            "analytics": {"small": 10000, "medium": 50000, "large": 200000},
            "personalization": {"small": 15000, "medium": 75000, "large": 300000},
            "prediction": {"small": 20000, "medium": 100000, "large": 500000},
            "generation": {"small": 3000, "medium": 15000, "large": 75000},
            "optimization": {"small": 25000, "medium": 125000, "large": 600000},
        }
        business_size = business_profile.get('size', 'small')
        return base_costs.get(ai_category, {}).get(business_size, 10000)

    def _identify_potential_benefits(self, ai_category, business_profile):
        """Identify potential benefits for AI category"""
        benefit_map = {
            "automation": [
                "Reduced operational costs",
                "Improved efficiency",
                "Fewer human errors",
                "24/7 availability",
            ],
            "analytics": [
                "Better decision making",
                "Improved customer insights",
                "Optimized operations",
                "Competitive advantage",
            ],
            "personalization": [
                "Increased customer satisfaction",
                "Higher conversion rates",
                "Improved customer retention",
                "Enhanced user experience",
            ],
            "prediction": [
                "Better planning and forecasting",
                "Risk mitigation",
                "Optimized resource allocation",
                "Proactive problem solving",
            ],
            "generation": [
                "Faster content creation",
                "Consistent quality",
                "Reduced creative costs",
                "Scalable content production",
            ],
            "optimization": [
                "Improved efficiency",
                "Cost reduction",
                "Better resource utilization",
                "Enhanced performance",
            ],
        }
        return benefit_map.get(ai_category, ["Improved business performance"])

    def _generate_implementation_steps(self, ai_category):
        """Generate implementation steps for AI category"""
        return [
            "Define specific use cases and requirements",
            "Evaluate and select appropriate AI tools/vendors",
            "Prepare data and infrastructure",
            "Develop pilot implementation",
            "Test and validate results",
            "Scale successful implementations",
            "Monitor and optimize performance",
        ]

    def _define_success_metrics(self, ai_category):
        """Define success metrics for AI category"""
        metric_map = {
            "automation": ["Process completion time", "Error reduction rate", "Cost savings"],
            "analytics": ["Decision accuracy", "Insight generation rate", "Business impact"],
            "personalization": ["Engagement rate", "Conversion rate", "Customer satisfaction"],
            "prediction": ["Prediction accuracy", "Planning effectiveness", "Risk reduction"],
            "generation": ["Content quality score", "Production speed", "Cost per asset"],
            "optimization": ["Efficiency improvement", "Cost reduction", "Performance gains"],
        }
        return metric_map.get(ai_category, ["ROI", "User satisfaction", "Performance improvement"])

    def _identify_custom_opportunities(self, business_profile):
        """Identify custom AI opportunities based on specific business needs"""
        custom_opportunities = []
        pain_points = business_profile.get('pain_points', [])
        pain_point_ai_map = {
            "manual_processes": "automation",
            "poor_customer_insights": "analytics",
            "low_engagement": "personalization",
            "unpredictable_demand": "prediction",
            "content_creation_bottleneck": "generation",
            "inefficient_operations": "optimization",
        }
        for pain_point in pain_points:
            if pain_point in pain_point_ai_map:
                ai_category = pain_point_ai_map[pain_point]
                opportunity = self._create_opportunity(ai_category, 'High', business_profile)
                opportunity['custom_reason'] = f"Addresses specific pain point: {pain_point}"
                custom_opportunities.append(opportunity)
        return custom_opportunities

    def create_implementation_roadmap(self, selected_opportunities, business_constraints):
        """Create implementation roadmap for selected AI opportunities"""
        roadmap = {
            "phases": [],
            "timeline": self._calculate_total_timeline(selected_opportunities),
            "total_investment": self._calculate_total_investment(selected_opportunities),
            "expected_roi": self._calculate_expected_roi(selected_opportunities),
            "risk_assessment": self._assess_implementation_risks(selected_opportunities),
            "success_factors": self._identify_success_factors(selected_opportunities),
        }
        phases = self._organize_into_phases(selected_opportunities, business_constraints)
        roadmap["phases"] = phases
        return roadmap

    def _organize_into_phases(self, opportunities, constraints):
        """Organize opportunities into implementation phases"""
        sorted_opps = sorted(
            opportunities,
            key=lambda x: (x['feasibility_score'], x['impact_score']),
            reverse=True,
        )
        phases = []
        current_phase = 1
        phase_budget = constraints.get('phase_budget', 50000)
        phase_duration = constraints.get('phase_duration_months', 6)
        current_phase_opps = []
        current_phase_cost = 0
        for opp in sorted_opps:
            opp_cost = opp['estimated_cost']
            if current_phase_cost + opp_cost <= phase_budget and len(current_phase_opps) < 3:
                current_phase_opps.append(opp)
                current_phase_cost += opp_cost
            else:
                if current_phase_opps:
                    phase = self._create_phase(current_phase, current_phase_opps, phase_duration)
                    phases.append(phase)
                    current_phase += 1
                current_phase_opps = [opp]
                current_phase_cost = opp_cost
        if current_phase_opps:
            phase = self._create_phase(current_phase, current_phase_opps, phase_duration)
            phases.append(phase)
        return phases

    def _create_phase(self, phase_number, opportunities, duration_months):
        """Create implementation phase"""
        phase = {
            "phase_number": phase_number,
            "name": f"Phase {phase_number}: AI Implementation",
            "duration_months": duration_months,
            "opportunities": opportunities,
            "total_cost": sum(opp['estimated_cost'] for opp in opportunities),
            "key_milestones": self._generate_phase_milestones(opportunities),
            "dependencies": self._identify_phase_dependencies(opportunities),
            "risks": self._identify_phase_risks(opportunities),
            "success_criteria": self._define_phase_success_criteria(opportunities),
        }
        return phase

    def _generate_phase_milestones(self, opportunities):
        """Generate key milestones for phase"""
        milestones = []
        for i, opp in enumerate(opportunities, 1):
            milestones.extend([
                f"Month {i}: Complete {opp['name']} requirements analysis",
                f"Month {i+1}: Begin {opp['name']} implementation",
                f"Month {i+2}: Complete {opp['name']} pilot testing",
            ])
        return milestones[:6]

    def _identify_phase_dependencies(self, opportunities):
        """Identify dependencies between opportunities in phase"""
        dependencies = []
        basic_categories = ['automation', 'analytics']
        advanced_categories = ['prediction', 'optimization']
        basic_in_phase = any(opp['category'] in basic_categories for opp in opportunities)
        advanced_in_phase = any(opp['category'] in advanced_categories for opp in opportunities)
        if basic_in_phase and advanced_in_phase:
            dependencies.append("Complete basic automation and analytics before advanced AI")
        return dependencies

    def _identify_phase_risks(self, opportunities):
        """Identify risks for implementation phase"""
        risks = []
        high_complexity_count = sum(1 for opp in opportunities if opp['complexity'] == 'High')
        if high_complexity_count > 1:
            risks.append("Multiple high-complexity implementations may strain resources")
        total_cost = sum(opp['estimated_cost'] for opp in opportunities)
        if total_cost > 100000:
            risks.append("High investment amount increases financial risk")
        return risks

    def _define_phase_success_criteria(self, opportunities):
        """Define success criteria for phase"""
        criteria = []
        for opp in opportunities:
            criteria.extend([
                f"Successful deployment of {opp['name']}",
                f"Achievement of defined metrics for {opp['name']}",
            ])
        criteria.append("Phase completed within budget and timeline")
        criteria.append("Team successfully trained on new AI tools")
        return criteria[:5]

    def _calculate_total_timeline(self, opportunities):
        """Calculate total implementation timeline"""
        total_months = 0
        for opp in opportunities:
            if opp['complexity'] == 'High':
                total_months += 6
            elif opp['complexity'] == 'Medium':
                total_months += 4
            else:
                total_months += 2
        parallel_factor = 0.7
        return int(total_months * parallel_factor)

    def _calculate_total_investment(self, opportunities):
        """Calculate total investment required"""
        return sum(opp['estimated_cost'] for opp in opportunities)

    def _calculate_expected_roi(self, opportunities):
        """Calculate expected ROI"""
        total_investment = self._calculate_total_investment(opportunities)
        annual_benefits = 0
        for opp in opportunities:
            if opp['category'] == 'automation':
                annual_benefits += total_investment * 0.3
            elif opp['category'] == 'analytics':
                annual_benefits += total_investment * 0.25
            else:
                annual_benefits += total_investment * 0.2
        roi_percentage = (
            (annual_benefits / total_investment) * 100 if total_investment > 0 else 0
        )
        return {
            "annual_benefits": annual_benefits,
            "roi_percentage": round(roi_percentage, 1),
            "payback_period_months": round(
                (total_investment / (annual_benefits / 12)), 1
            )
            if annual_benefits > 0
            else 0,
        }

    def _assess_implementation_risks(self, opportunities):
        """Assess implementation risks"""
        risks = {
            "technical_risks": [],
            "financial_risks": [],
            "operational_risks": [],
            "strategic_risks": [],
        }
        high_complexity_count = sum(
            1 for opp in opportunities if opp['complexity'] == 'High'
        )
        if high_complexity_count > 2:
            risks["technical_risks"].append(
                "Multiple complex implementations may exceed technical capacity"
            )
        total_cost = self._calculate_total_investment(opportunities)
        if total_cost > 500000:
            risks["financial_risks"].append(
                "High investment amount poses significant financial risk"
            )
        if len(opportunities) > 5:
            risks["operational_risks"].append(
                "Too many simultaneous changes may disrupt operations"
            )
        if any(opp['impact_level'] == 'Low' for opp in opportunities):
            risks["strategic_risks"].append(
                "Some low-impact initiatives may not deliver expected value"
            )
        return risks

    def _identify_success_factors(self, opportunities):
        """Identify critical success factors"""
        return [
            "Strong leadership commitment and support",
            "Adequate technical infrastructure and data quality",
            "Skilled team with AI literacy",
            "Clear success metrics and monitoring",
            "Effective change management",
            "Continuous learning and adaptation",
            "Strong vendor partnerships",
            "Adequate budget and resource allocation",
        ]


@ai_adoption_bp.route('/assess-readiness', methods=['POST'])
def assess_readiness():
    try:
        data = request.get_json()
        business_profile = data.get('business_profile', {})

        roadmap = AIAdoptionRoadmap()
        assessment = roadmap.assess_ai_readiness(business_profile)

        session['ai_readiness'] = assessment

        return jsonify({"success": True, "data": assessment})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@ai_adoption_bp.route('/identify-opportunities', methods=['POST'])
def identify_opportunities():
    try:
        data = request.get_json()
        business_profile = data.get('business_profile', {})
        industry = data.get('industry', 'General')

        roadmap = AIAdoptionRoadmap()
        opportunities = roadmap.identify_ai_opportunities(business_profile, industry)

        session['ai_opportunities'] = opportunities

        return jsonify({"success": True, "data": opportunities})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@ai_adoption_bp.route('/create-roadmap', methods=['POST'])
def create_roadmap():
    try:
        data = request.get_json()
        selected_opportunities = data.get('selected_opportunities', [])
        business_constraints = data.get('business_constraints', {})

        roadmap_tool = AIAdoptionRoadmap()
        roadmap = roadmap_tool.create_implementation_roadmap(selected_opportunities, business_constraints)

        session['ai_roadmap'] = roadmap

        return jsonify({"success": True, "data": roadmap})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@ai_adoption_bp.route('/complete-analysis', methods=['GET'])
def get_complete_analysis():
    try:
        complete_analysis = {
            "readiness_assessment": session.get('ai_readiness'),
            "opportunities": session.get('ai_opportunities'),
            "implementation_roadmap": session.get('ai_roadmap'),
            "analysis_date": datetime.now().isoformat(),
        }

        return jsonify({"success": True, "data": complete_analysis})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
