from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
import uuid

mind_mapping_bp = Blueprint('mind_mapping', __name__)


class MindMappingTool:
    def __init__(self):
        self.business_model_elements = {
            "core": {
                "value_proposition": "What unique value do you provide?",
                "target_customer": "Who is your ideal customer?",
                "problem_solution": "What problem are you solving?",
            },
            "operations": {
                "key_activities": "What key activities does your business require?",
                "key_resources": "What key resources do you need?",
                "key_partnerships": "Who are your key partners?",
            },
            "financial": {
                "revenue_streams": "How will you make money?",
                "cost_structure": "What are your main costs?",
                "pricing_strategy": "How will you price your offering?",
            },
            "market": {
                "market_size": "How big is your market?",
                "competition": "Who are your competitors?",
                "marketing_channels": "How will you reach customers?",
            },
            "team": {
                "team_structure": "What team do you need?",
                "advisors": "Who will advise you?",
                "culture": "What culture will you build?",
            },
            "growth": {
                "scaling_strategy": "How will you scale?",
                "expansion_plans": "Where will you expand?",
                "exit_strategy": "What's your exit strategy?",
            },
        }

        self.ai_suggestions = {
            "value_proposition": [
                "Consider the jobs-to-be-done framework",
                "Focus on emotional and functional benefits",
                "Quantify the value you provide",
                "Test with real customers early",
            ],
            "target_customer": [
                "Create detailed customer personas",
                "Identify early adopters vs mainstream market",
                "Consider customer lifetime value",
                "Map the customer journey",
            ],
            "revenue_streams": [
                "Consider recurring revenue models",
                "Explore multiple revenue streams",
                "Think about pricing psychology",
                "Plan for revenue diversification",
            ],
        }

        self.scenario_templates = {
            "conservative": {
                "growth_rate": 0.1,
                "market_penetration": 0.01,
                "risk_level": "low",
            },
            "optimistic": {
                "growth_rate": 0.3,
                "market_penetration": 0.05,
                "risk_level": "medium",
            },
            "aggressive": {
                "growth_rate": 0.5,
                "market_penetration": 0.1,
                "risk_level": "high",
            },
        }

    def create_mind_map(self, user_id, business_idea):
        """Create a new mind map for business strategy development"""
        mind_map_id = str(uuid.uuid4())

        mind_map = {
            "id": mind_map_id,
            "user_id": user_id,
            "business_idea": business_idea,
            "created_at": datetime.now().isoformat(),
            "nodes": self._initialize_nodes(),
            "connections": [],
            "scenarios": {},
            "ai_insights": [],
            "completion_status": self._initialize_completion_status(),
        }

        return mind_map

    def _initialize_nodes(self):
        """Initialize mind map nodes with business model elements"""
        nodes = {}
        node_id = 1

        for category, elements in self.business_model_elements.items():
            category_node = {
                "id": f"category_{node_id}",
                "type": "category",
                "label": category.replace("_", " ").title(),
                "category": category,
                "position": self._calculate_position(category, node_id),
                "completed": False,
                "children": [],
            }

            node_id += 1
            child_nodes = []

            for element_key, element_question in elements.items():
                element_node = {
                    "id": f"element_{node_id}",
                    "type": "element",
                    "label": element_key.replace("_", " ").title(),
                    "question": element_question,
                    "answer": "",
                    "position": self._calculate_child_position(
                        category, element_key, node_id
                    ),
                    "completed": False,
                    "parent": category_node["id"],
                }
                child_nodes.append(element_node["id"])
                nodes[element_node["id"]] = element_node
                node_id += 1

            category_node["children"] = child_nodes
            nodes[category_node["id"]] = category_node

        return nodes

    def _calculate_position(self, category, node_id):
        """Calculate position for category nodes in circular layout"""
        positions = {
            "core": {"x": 400, "y": 300},
            "operations": {"x": 200, "y": 150},
            "financial": {"x": 600, "y": 150},
            "market": {"x": 700, "y": 300},
            "team": {"x": 600, "y": 450},
            "growth": {"x": 200, "y": 450},
        }
        return positions.get(category, {"x": 400, "y": 300})

    def _calculate_child_position(self, category, element, node_id):
        """Calculate position for child nodes around parent"""
        base_positions = self._calculate_position(category, 0)
        offset = (node_id % 4) * 50
        return {
            "x": base_positions["x"] + offset,
            "y": base_positions["y"] + offset,
        }

    def _initialize_completion_status(self):
        """Initialize completion tracking"""
        return {
            "core": 0,
            "operations": 0,
            "financial": 0,
            "market": 0,
            "team": 0,
            "growth": 0,
            "overall": 0,
        }

    def update_node(self, mind_map_id, node_id, data):
        """Update a specific node in the mind map"""
        update_result = {
            "node_id": node_id,
            "updated_data": data,
            "ai_suggestions": self._get_ai_suggestions(node_id, data),
            "related_nodes": self._find_related_nodes(node_id, data),
            "completion_impact": self._calculate_completion_impact(node_id, data),
        }

        return update_result

    def _get_ai_suggestions(self, node_id, data):
        """Get AI-powered suggestions for node improvement"""
        element_type = data.get('label', '').lower().replace(' ', '_')

        suggestions = self.ai_suggestions.get(element_type, [])

        if data.get('answer'):
            content_suggestions = self._analyze_content_for_suggestions(data['answer'])
            suggestions.extend(content_suggestions)

        return suggestions[:5]

    def _analyze_content_for_suggestions(self, content):
        """Analyze content and provide contextual suggestions"""
        suggestions = []
        content_lower = content.lower()

        if len(content.split()) < 10:
            suggestions.append(
                "Consider providing more detail to strengthen this element"
            )

        if "customer" in content_lower and "pain" not in content_lower:
            suggestions.append(
                "Consider explicitly mentioning customer pain points"
            )

        if "revenue" in content_lower and "$" not in content:
            suggestions.append(
                "Consider adding specific financial projections"
            )

        if "competition" in content_lower and "advantage" not in content_lower:
            suggestions.append("Highlight your competitive advantages")

        return suggestions

    def _find_related_nodes(self, node_id, data):
        """Find nodes that should be connected based on content"""
        related_nodes = []
        content = data.get('answer', '').lower()

        relationship_map = {
            "customer": ["target_customer", "marketing_channels", "value_proposition"],
            "revenue": ["revenue_streams", "pricing_strategy", "cost_structure"],
            "team": ["team_structure", "key_activities", "culture"],
            "technology": ["key_resources", "key_activities", "scaling_strategy"],
        }

        for keyword, related_elements in relationship_map.items():
            if keyword in content:
                related_nodes.extend(related_elements)

        return list(set(related_nodes))

    def _calculate_completion_impact(self, node_id, data):
        """Calculate how this update impacts overall completion"""
        if data.get('answer') and len(data['answer'].strip()) > 0:
            return {
                "completed": True,
                "quality_score": len(data['answer'].split()) / 10,
            }
        return {"completed": False, "quality_score": 0}

    def create_connection(self, mind_map_id, source_node, target_node, connection_type, description):
        """Create a connection between two nodes"""
        connection = {
            "id": str(uuid.uuid4()),
            "source": source_node,
            "target": target_node,
            "type": connection_type,
            "description": description,
            "strength": self._calculate_connection_strength(source_node, target_node),
            "created_at": datetime.now().isoformat(),
        }

        return connection

    def _calculate_connection_strength(self, source_node, target_node):
        """Calculate the strength of connection between nodes"""
        return 0.7

    def create_scenario(self, mind_map_id, scenario_name, scenario_type="custom"):
        """Create a new business scenario"""
        scenario_id = str(uuid.uuid4())

        if scenario_type in self.scenario_templates:
            template = self.scenario_templates[scenario_type]
        else:
            template = self.scenario_templates["conservative"]

        scenario = {
            "id": scenario_id,
            "name": scenario_name,
            "type": scenario_type,
            "parameters": template.copy(),
            "projections": self._calculate_projections(template),
            "risks": self._identify_risks(template),
            "opportunities": self._identify_opportunities(template),
            "created_at": datetime.now().isoformat(),
        }

        return scenario

    def _calculate_projections(self, template):
        """Calculate financial and growth projections"""
        growth_rate = template["growth_rate"]
        market_penetration = template["market_penetration"]

        projections = {
            "year_1": {
                "revenue": 100000 * market_penetration,
                "customers": 1000 * market_penetration,
                "market_share": market_penetration,
            },
            "year_3": {
                "revenue": 100000 * market_penetration * (1 + growth_rate) ** 3,
                "customers": 1000 * market_penetration * (1 + growth_rate) ** 3,
                "market_share": market_penetration * (1 + growth_rate) ** 3,
            },
            "year_5": {
                "revenue": 100000 * market_penetration * (1 + growth_rate) ** 5,
                "customers": 1000 * market_penetration * (1 + growth_rate) ** 5,
                "market_share": market_penetration * (1 + growth_rate) ** 5,
            },
        }

        return projections

    def _identify_risks(self, template):
        """Identify risks based on scenario parameters"""
        risk_level = template["risk_level"]

        risk_map = {
            "low": [
                "Market saturation",
                "Slow customer adoption",
                "Operational inefficiencies",
            ],
            "medium": [
                "Competitive pressure",
                "Technology disruption",
                "Regulatory changes",
                "Funding challenges",
            ],
            "high": [
                "Market volatility",
                "Execution risks",
                "Team scalability",
                "Cash flow management",
                "Product-market fit",
            ],
        }

        return risk_map.get(risk_level, risk_map["medium"])

    def _identify_opportunities(self, template):
        """Identify opportunities based on scenario parameters"""
        growth_rate = template["growth_rate"]

        if growth_rate > 0.4:
            return [
                "Rapid market expansion",
                "Strategic partnerships",
                "International expansion",
                "Product line extension",
            ]
        elif growth_rate > 0.2:
            return [
                "Market leadership",
                "Operational optimization",
                "Customer retention",
                "Technology advancement",
            ]
        else:
            return [
                "Steady growth",
                "Market consolidation",
                "Efficiency improvements",
                "Sustainable practices",
            ]

    def export_business_plan(self, mind_map_id):
        """Export mind map as traditional business plan"""
        business_plan = {
            "executive_summary": self._generate_executive_summary(),
            "company_description": self._generate_company_description(),
            "market_analysis": self._generate_market_analysis(),
            "organization_management": self._generate_organization_section(),
            "service_product_line": self._generate_product_section(),
            "marketing_sales": self._generate_marketing_section(),
            "funding_request": self._generate_funding_section(),
            "financial_projections": self._generate_financial_section(),
            "appendix": self._generate_appendix(),
        }

        return business_plan

    def _generate_executive_summary(self):
        """Generate executive summary from mind map data"""
        return {
            "content": "Executive summary generated from mind map analysis",
            "key_points": [
                "Business opportunity",
                "Competitive advantage",
                "Financial highlights",
                "Funding requirements",
            ],
        }

    def _generate_company_description(self):
        """Generate company description section"""
        return {
            "content": "Company description based on core value proposition",
            "sections": ["Mission", "Vision", "Values", "Legal Structure"],
        }

    def _generate_market_analysis(self):
        """Generate market analysis section"""
        return {
            "content": "Market analysis from market research nodes",
            "sections": ["Industry Overview", "Target Market", "Competition", "Market Trends"],
        }

    def _generate_organization_section(self):
        """Generate organization and management section"""
        return {
            "content": "Organization structure from team nodes",
            "sections": ["Organizational Structure", "Management Team", "Advisory Board", "Personnel Plan"],
        }

    def _generate_product_section(self):
        """Generate product/service section"""
        return {
            "content": "Product description from value proposition nodes",
            "sections": ["Product Description", "Features", "Benefits", "Development Timeline"],
        }

    def _generate_marketing_section(self):
        """Generate marketing and sales section"""
        return {
            "content": "Marketing strategy from marketing channel nodes",
            "sections": ["Marketing Strategy", "Sales Strategy", "Pricing", "Customer Acquisition"],
        }

    def _generate_funding_section(self):
        """Generate funding request section"""
        return {
            "content": "Funding requirements from financial nodes",
            "sections": ["Funding Requirements", "Use of Funds", "Exit Strategy", "Return on Investment"],
        }

    def _generate_financial_section(self):
        """Generate financial projections section"""
        return {
            "content": "Financial projections from scenario analysis",
            "sections": ["Revenue Projections", "Expense Projections", "Cash Flow", "Break-even Analysis"],
        }

    def _generate_appendix(self):
        """Generate appendix section"""
        return {
            "content": "Supporting documents and detailed analysis",
            "sections": ["Market Research", "Financial Details", "Technical Specifications", "Legal Documents"],
        }


@mind_mapping_bp.route('/create', methods=['POST'])
def create_mind_map():
    """Create a new mind map"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        business_idea = data.get('business_idea', '')

        tool = MindMappingTool()
        mind_map = tool.create_mind_map(user_id, business_idea)

        session['current_mind_map'] = mind_map

        return jsonify({"success": True, "data": mind_map})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@mind_mapping_bp.route('/update-node', methods=['POST'])
def update_node():
    """Update a node in the mind map"""
    try:
        data = request.get_json()
        mind_map_id = data.get('mind_map_id')
        node_id = data.get('node_id')
        node_data = data.get('node_data', {})

        tool = MindMappingTool()
        result = tool.update_node(mind_map_id, node_id, node_data)

        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@mind_mapping_bp.route('/create-connection', methods=['POST'])
def create_connection():
    """Create a connection between nodes"""
    try:
        data = request.get_json()
        mind_map_id = data.get('mind_map_id')
        source_node = data.get('source_node')
        target_node = data.get('target_node')
        connection_type = data.get('connection_type', 'related')
        description = data.get('description', '')

        tool = MindMappingTool()
        connection = tool.create_connection(
            mind_map_id, source_node, target_node, connection_type, description
        )

        return jsonify({"success": True, "data": connection})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@mind_mapping_bp.route('/create-scenario', methods=['POST'])
def create_scenario():
    """Create a business scenario"""
    try:
        data = request.get_json()
        mind_map_id = data.get('mind_map_id')
        scenario_name = data.get('scenario_name')
        scenario_type = data.get('scenario_type', 'custom')

        tool = MindMappingTool()
        scenario = tool.create_scenario(mind_map_id, scenario_name, scenario_type)

        return jsonify({"success": True, "data": scenario})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@mind_mapping_bp.route('/export-business-plan', methods=['POST'])
def export_business_plan():
    """Export mind map as business plan"""
    try:
        data = request.get_json()
        mind_map_id = data.get('mind_map_id')

        tool = MindMappingTool()
        business_plan = tool.export_business_plan(mind_map_id)

        return jsonify({"success": True, "data": business_plan})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
