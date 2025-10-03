from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
import uuid
from .purpose_discovery import PurposeDiscoveryModule
from .mind_mapping import MindMappingTool
from .value_zone_validator import ValueZoneValidator
from .ai_adoption_roadmap import AIAdoptionRoadmap

enhanced_assessment_bp = Blueprint('enhanced_assessment', __name__)


class EnhancedAssessmentEngine:
    def __init__(self):
        self.purpose_module = PurposeDiscoveryModule()
        self.mind_mapping = MindMappingTool()
        self.value_zone = ValueZoneValidator()
        self.ai_roadmap = AIAdoptionRoadmap()

        self.enhanced_phases = {
            1: {
                "name": "Deep Self Discovery & Purpose",
                "description": "Discover your core purpose, values, and entrepreneurial motivations",
                "modules": ["purpose_discovery", "personality_assessment"],
                "weight": 0.20,
            },
            2: {
                "name": "Value Zone Identification",
                "description": "Find the intersection of your passion, skills, and market demand",
                "modules": ["value_zone_analysis", "skill_assessment"],
                "weight": 0.15,
            },
            3: {
                "name": "Dynamic Strategy Development",
                "description": "Create flexible, adaptive business strategies using mind mapping",
                "modules": ["mind_mapping", "business_model_canvas"],
                "weight": 0.15,
            },
            4: {
                "name": "Enhanced Market Intelligence",
                "description": "Deep market research with AI-powered insights and trend analysis",
                "modules": [
                    "market_research",
                    "competitive_analysis",
                    "trend_analysis",
                ],
                "weight": 0.15,
            },
            5: {
                "name": "Leadership & Culture Development",
                "description": "Build leadership skills and define your company culture",
                "modules": [
                    "leadership_assessment",
                    "culture_builder",
                    "communication_training",
                ],
                "weight": 0.10,
            },
            6: {
                "name": "AI-Powered Future-Proofing",
                "description": "Prepare your business for the AI-driven future",
                "modules": ["ai_adoption_roadmap", "technology_strategy"],
                "weight": 0.15,
            },
            7: {
                "name": "Comprehensive Business Plan & Roadmap",
                "description": "Generate your complete business plan and implementation roadmap",
                "modules": [
                    "business_plan_generation",
                    "implementation_roadmap",
                    "success_metrics",
                ],
                "weight": 0.10,
            },
        }

        self.assessment_criteria = {
            "purpose_clarity": {
                "weight": 0.25,
                "description": "How clear and compelling is your purpose?",
            },
            "market_opportunity": {
                "weight": 0.20,
                "description": "How strong is your market opportunity?",
            },
            "skill_alignment": {
                "weight": 0.15,
                "description": "How well do your skills match your business idea?",
            },
            "strategic_thinking": {
                "weight": 0.15,
                "description": "How strategic and adaptable is your approach?",
            },
            "leadership_readiness": {
                "weight": 0.10,
                "description": "How ready are you to lead and build a team?",
            },
            "future_readiness": {
                "weight": 0.10,
                "description": "How prepared are you for future challenges?",
            },
            "execution_capability": {
                "weight": 0.05,
                "description": "How capable are you of executing your plan?",
            },
        }

    def start_enhanced_assessment(self, user_id, assessment_type="comprehensive"):
        """Start a new enhanced assessment"""
        assessment_id = str(uuid.uuid4())

        assessment = {
            "id": assessment_id,
            "user_id": user_id,
            "type": assessment_type,
            "started_at": datetime.now().isoformat(),
            "current_phase": 1,
            "phase_progress": {phase: 0 for phase in range(1, 8)},
            "phase_results": {},
            "overall_score": 0,
            "recommendations": [],
            "next_steps": [],
            "completion_status": "in_progress",
        }

        return assessment

    def complete_phase(self, assessment_id, phase_number, phase_data):
        """Complete a specific assessment phase"""
        phase_result = {
            "phase_number": phase_number,
            "completed_at": datetime.now().isoformat(),
            "data": phase_data,
            "score": self._calculate_phase_score(phase_number, phase_data),
            "insights": self._generate_phase_insights(phase_number, phase_data),
            "recommendations": self._generate_phase_recommendations(
                phase_number, phase_data
            ),
        }

        return phase_result

    def _calculate_phase_score(self, phase_number, phase_data):
        """Calculate score for a specific phase"""
        if phase_number == 1:
            return self._score_purpose_phase(phase_data)
        elif phase_number == 2:
            return self._score_value_zone_phase(phase_data)
        elif phase_number == 3:
            return self._score_strategy_phase(phase_data)
        elif phase_number == 4:
            return self._score_market_phase(phase_data)
        elif phase_number == 5:
            return self._score_leadership_phase(phase_data)
        elif phase_number == 6:
            return self._score_ai_phase(phase_data)
        elif phase_number == 7:
            return self._score_business_plan_phase(phase_data)
        return 5.0

    def _score_purpose_phase(self, phase_data):
        score = 0
        if 'five_whys_result' in phase_data:
            clarity_score = phase_data['five_whys_result'].get('purpose_clarity_score', 0)
            score += (clarity_score / 10) * 4
        if 'legacy_statement' in phase_data:
            legacy_quality = len(phase_data['legacy_statement'].get('statement', '').split())
            score += min(legacy_quality / 20, 3)
        if 'impact_visualization' in phase_data:
            impact_areas = len(phase_data['impact_visualization'].get('impact_map', {}))
            score += min(impact_areas / 3, 3)
        return min(score, 10)

    def _score_value_zone_phase(self, phase_data):
        score = 0
        if 'passion_analysis' in phase_data:
            passion_intensity = phase_data['passion_analysis'].get('passion_intensity', 0)
            score += (passion_intensity / 10) * 3
        if 'skill_analysis' in phase_data:
            core_skills = len(phase_data['skill_analysis'].get('core_skills', []))
            score += min(core_skills / 5, 3)
        if 'market_analysis' in phase_data:
            avg_opportunity = sum(
                opp.get('opportunity_score', 0) for opp in phase_data['market_analysis'].values()
            ) / max(len(phase_data['market_analysis']), 1)
            score += (avg_opportunity / 10) * 4
        return min(score, 10)

    def _score_strategy_phase(self, phase_data):
        score = 0
        if 'mind_map' in phase_data:
            completed_nodes = sum(
                1
                for node in phase_data['mind_map'].get('nodes', {}).values()
                if node.get('completed', False)
            )
            total_nodes = len(phase_data['mind_map'].get('nodes', {}))
            completion_rate = completed_nodes / max(total_nodes, 1)
            score += completion_rate * 5
        if 'scenarios' in phase_data:
            scenario_count = len(phase_data['scenarios'])
            score += min(scenario_count / 3, 3)
        if 'connections' in phase_data:
            connection_count = len(phase_data['connections'])
            score += min(connection_count / 5, 2)
        return min(score, 10)

    def _score_market_phase(self, phase_data):
        score = 5
        if 'market_size' in phase_data and phase_data['market_size'] > 100000000:
            score += 2
        if 'competitive_analysis' in phase_data:
            competitor_count = len(phase_data['competitive_analysis'].get('competitors', []))
            score += min(competitor_count / 5, 2)
        if 'trend_analysis' in phase_data:
            trend_count = len(phase_data['trend_analysis'].get('trends', []))
            score += min(trend_count / 3, 1)
        return min(score, 10)

    def _score_leadership_phase(self, phase_data):
        score = 0
        if 'leadership_assessment' in phase_data:
            leadership_score = phase_data['leadership_assessment'].get('overall_score', 0)
            score += (leadership_score / 10) * 4
        if 'culture_definition' in phase_data:
            culture_elements = len(phase_data['culture_definition'].get('elements', []))
            score += min(culture_elements / 5, 3)
        if 'communication_assessment' in phase_data:
            comm_score = phase_data['communication_assessment'].get('score', 0)
            score += (comm_score / 10) * 3
        return min(score, 10)

    def _score_ai_phase(self, phase_data):
        score = 0
        if 'ai_readiness' in phase_data:
            readiness_score = phase_data['ai_readiness'].get('overall_score', 0)
            score += (readiness_score / 10) * 4
        if 'ai_opportunities' in phase_data:
            opportunity_count = len(phase_data['ai_opportunities'])
            score += min(opportunity_count / 5, 3)
        if 'ai_roadmap' in phase_data:
            phase_count = len(phase_data['ai_roadmap'].get('phases', []))
            score += min(phase_count / 3, 3)
        return min(score, 10)

    def _score_business_plan_phase(self, phase_data):
        score = 0
        if 'business_plan' in phase_data:
            sections = phase_data['business_plan'].keys()
            completeness = len(sections) / 9
            score += completeness * 5
        if 'financial_projections' in phase_data:
            projection_years = len(phase_data['financial_projections'].get('years', []))
            score += min(projection_years / 5, 3)
        if 'implementation_roadmap' in phase_data:
            milestone_count = len(phase_data['implementation_roadmap'].get('milestones', []))
            score += min(milestone_count / 10, 2)
        return min(score, 10)
    def _generate_phase_insights(self, phase_number, phase_data):
        insights = []
        if phase_number == 1:
            if 'five_whys_result' in phase_data:
                clarity_score = phase_data['five_whys_result'].get('purpose_clarity_score', 0)
                if clarity_score >= 8:
                    insights.append("You have exceptional clarity about your purpose and motivations.")
                elif clarity_score >= 6:
                    insights.append("Your purpose is fairly clear, but could benefit from deeper reflection.")
                else:
                    insights.append("Consider spending more time exploring your deeper motivations.")
        elif phase_number == 2:
            if 'value_zones' in phase_data:
                top_zone = phase_data['value_zones'][0] if phase_data['value_zones'] else None
                if top_zone and top_zone.get('zone_score', 0) >= 8:
                    insights.append(f"Strong alignment found in {top_zone['passion']} + {top_zone['skill']}")
                else:
                    insights.append("Consider developing skills in your passion areas or exploring new passions.")
        elif phase_number == 3:
            if 'mind_map' in phase_data:
                node_count = len(phase_data['mind_map'].get('nodes', {}))
                if node_count >= 20:
                    insights.append("Comprehensive strategy development with detailed business model thinking.")
                else:
                    insights.append("Consider expanding your strategic thinking to cover more business areas.")
        return insights

    def _generate_phase_recommendations(self, phase_number, phase_data):
        recommendations = []
        if phase_number == 1:
            recommendations.extend([
                "Document your purpose statement and refer to it regularly",
                "Share your purpose with trusted advisors for feedback",
                "Align all business decisions with your core purpose",
            ])
        elif phase_number == 2:
            recommendations.extend([
                "Focus on your highest-scoring value zone for initial business development",
                "Develop skills in areas where you have passion but lack expertise",
                "Validate market demand through customer interviews",
            ])
        elif phase_number == 3:
            recommendations.extend([
                "Regularly update your mind map as you learn more about your market",
                "Create multiple scenarios to test strategy flexibility",
                "Share your strategy map with potential customers and advisors",
            ])
        return recommendations

    def calculate_overall_assessment(self, phase_results):
        overall_score = 0
        total_weight = 0
        for phase_num, phase_info in self.enhanced_phases.items():
            if phase_num in phase_results:
                phase_score = phase_results[phase_num].get('score', 0)
                weight = phase_info['weight']
                overall_score += phase_score * weight
                total_weight += weight
        if total_weight > 0:
            overall_score = overall_score / total_weight
        assessment_result = {
            "overall_score": round(overall_score, 2),
            "readiness_level": self._determine_readiness_level(overall_score),
            "strengths": self._identify_strengths(phase_results),
            "areas_for_improvement": self._identify_improvement_areas(phase_results),
            "next_steps": self._generate_next_steps(phase_results, overall_score),
            "success_probability": self._estimate_success_probability(phase_results),
            "recommended_timeline": self._suggest_timeline(phase_results),
            "resource_requirements": self._estimate_resources(phase_results),
        }
        return assessment_result

    def _determine_readiness_level(self, score):
        if score >= 8.5:
            return "Highly Ready - Exceptional entrepreneurial potential"
        elif score >= 7.0:
            return "Ready - Strong foundation for entrepreneurship"
        elif score >= 5.5:
            return "Developing - Good potential with focused development"
        elif score >= 4.0:
            return "Emerging - Significant development needed"
        else:
            return "Early Stage - Foundational work required"

    def _identify_strengths(self, phase_results):
        strengths = []
        for phase_num, result in phase_results.items():
            score = result.get('score', 0)
            phase_name = self.enhanced_phases[phase_num]['name']
            if score >= 8:
                strengths.append(f"Excellent {phase_name.lower()}")
            elif score >= 7:
                strengths.append(f"Strong {phase_name.lower()}")
        return strengths

    def _identify_improvement_areas(self, phase_results):
        improvements = []
        for phase_num, result in phase_results.items():
            score = result.get('score', 0)
            phase_name = self.enhanced_phases[phase_num]['name']
            if score < 5:
                improvements.append(f"Develop {phase_name.lower()}")
            elif score < 7:
                improvements.append(f"Strengthen {phase_name.lower()}")
        return improvements

    def _generate_next_steps(self, phase_results, overall_score):
        next_steps = []
        if overall_score >= 7:
            next_steps.extend([
                "Begin developing your minimum viable product",
                "Start building your founding team",
                "Secure initial funding or bootstrap resources",
                "Validate your business model with real customers",
            ])
        elif overall_score >= 5:
            next_steps.extend([
                "Address identified weaknesses in your assessment",
                "Gain more experience in your target industry",
                "Build a stronger network of mentors and advisors",
                "Develop a detailed learning and development plan",
            ])
        else:
            next_steps.extend([
                "Focus on foundational entrepreneurship education",
                "Gain relevant work experience in your field of interest",
                "Develop core business skills through courses or mentorship",
                "Clarify your purpose and business vision",
            ])
        return next_steps

    def _estimate_success_probability(self, phase_results):
        purpose_score = phase_results.get(1, {}).get('score', 0)
        value_zone_score = phase_results.get(2, {}).get('score', 0)
        strategy_score = phase_results.get(3, {}).get('score', 0)
        market_score = phase_results.get(4, {}).get('score', 0)
        success_factors = [
            (purpose_score, 0.3),
            (value_zone_score, 0.25),
            (strategy_score, 0.25),
            (market_score, 0.2),
        ]
        weighted_score = sum(score * weight for score, weight in success_factors)
        probability = min(weighted_score / 10, 0.9)
        return round(probability, 2)

    def _suggest_timeline(self, phase_results):
        overall_avg = sum(result.get('score', 0) for result in phase_results.values()) / len(phase_results)
        if overall_avg >= 8:
            return "3-6 months to launch"
        elif overall_avg >= 6:
            return "6-12 months to launch"
        elif overall_avg >= 4:
            return "12-18 months to launch"
        else:
            return "18+ months of preparation needed"

    def _estimate_resources(self, phase_results):
        return {
            "financial": "Varies by business model - see detailed financial projections",
            "time": "Expect 20-40 hours per week during development phase",
            "team": "Consider co-founder if leadership score < 7",
            "mentorship": "Highly recommended for first-time entrepreneurs",
            "education": "Additional training recommended in low-scoring areas",
        }


@enhanced_assessment_bp.route('/start', methods=['POST'])
def start_assessment():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        assessment_type = data.get('type', 'comprehensive')

        engine = EnhancedAssessmentEngine()
        assessment = engine.start_enhanced_assessment(user_id, assessment_type)

        session['enhanced_assessment'] = assessment

        return jsonify({"success": True, "data": assessment})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@enhanced_assessment_bp.route('/complete-phase', methods=['POST'])
def complete_phase():
    try:
        data = request.get_json()
        assessment_id = data.get('assessment_id')
        phase_number = data.get('phase_number')
        phase_data = data.get('phase_data', {})

        engine = EnhancedAssessmentEngine()
        phase_result = engine.complete_phase(assessment_id, phase_number, phase_data)

        assessment = session.get('enhanced_assessment', {})
        if 'phase_results' not in assessment:
            assessment['phase_results'] = {}
        assessment['phase_results'][phase_number] = phase_result
        assessment['current_phase'] = phase_number + 1
        session['enhanced_assessment'] = assessment

        return jsonify({"success": True, "data": phase_result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@enhanced_assessment_bp.route('/final-results', methods=['POST'])
def get_final_results():
    try:
        assessment = session.get('enhanced_assessment', {})
        phase_results = assessment.get('phase_results', {})

        engine = EnhancedAssessmentEngine()
        final_results = engine.calculate_overall_assessment(phase_results)

        assessment['final_results'] = final_results
        assessment['completion_status'] = 'completed'
        assessment['completed_at'] = datetime.now().isoformat()
        session['enhanced_assessment'] = assessment

        return jsonify({"success": True, "data": {"assessment": assessment, "final_results": final_results}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@enhanced_assessment_bp.route('/status', methods=['GET'])
def get_assessment_status():
    try:
        assessment = session.get('enhanced_assessment', {})
        return jsonify({"success": True, "data": assessment})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
