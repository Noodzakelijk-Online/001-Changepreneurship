import React, { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button.jsx";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card.jsx";
import { Progress } from "@/components/ui/progress.jsx";
import { Badge } from "@/components/ui/badge.jsx";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs.jsx";
import { Input } from "@/components/ui/input.jsx";
import { Label } from "@/components/ui/label.jsx";
import { Textarea } from "@/components/ui/textarea.jsx";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group.jsx";
import { Slider } from "@/components/ui/slider.jsx";
import {
  Settings,
  Target,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Plus,
  Trash2,
  BarChart3,
  Star,
  Users,
  DollarSign,
  Building,
  Zap,
  ArrowRight,
} from "lucide-react";
import { useAssessment } from "../../contexts/AssessmentContext";

const BusinessDevelopmentDecisionMaking = () => {
  const { assessmentData, updateAssessmentData, completePhase, updatePhase } = useAssessment();
  const [currentSection, setCurrentSection] = useState(0);
  const [sectionData, setSectionData] = useState({
    strategicDecisionMatrix: {
      opportunityMapping: {
        serviceOpportunities: [],
        productOpportunities: [],
        hybridOpportunities: [],
      },
      marketStrategies: {
        existingProductExistingMarket: {
          selected: false,
          description: "",
          riskLevel: 1,
          timeframe: "",
        },
        existingProductNewMarket: {
          selected: false,
          description: "",
          riskLevel: 3,
          timeframe: "",
        },
        newProductExistingMarket: {
          selected: false,
          description: "",
          riskLevel: 3,
          timeframe: "",
        },
        newProductNewMarket: {
          selected: false,
          description: "",
          riskLevel: 5,
          timeframe: "",
        },
      },
      opportunityPrioritization: {
        criteria: [
          { name: "Market Size", weight: 20, description: "" },
          { name: "Competition Level", weight: 15, description: "" },
          { name: "Resource Requirements", weight: 25, description: "" },
          { name: "Time to Market", weight: 15, description: "" },
          { name: "Profit Potential", weight: 25, description: "" },
        ],
        opportunities: [],
      },
    },
    resourceOpportunityAlignment: {
      currentResources: {
        human: { available: [], description: "", adequacy: 5 },
        financial: { available: "", description: "", adequacy: 5 },
        physical: { available: [], description: "", adequacy: 5 },
        intangible: { available: [], description: "", adequacy: 5 },
      },
      acquirableResources: {
        human: { acquirable: [], timeline: "", cost: "", feasibility: 5 },
        financial: { acquirable: "", timeline: "", cost: "", feasibility: 5 },
        physical: { acquirable: [], timeline: "", cost: "", feasibility: 5 },
        intangible: { acquirable: [], timeline: "", cost: "", feasibility: 5 },
      },
      opportunityClassification: {
        perfectFit: [],
        stretch: [],
        aspirational: [],
      },
      resourceGapAnalysis: {
        criticalGaps: [],
        mitigationStrategies: [],
        alternativeApproaches: [],
      },
    },
    marketEntryFramework: {
      strategySelection: {
        selectedStrategy: "",
        rationale: "",
        riskAssessment: 5,
        expectedTimeline: "",
      },
      tacticalImplementation: {
        phase1: {
          activities: [],
          timeline: "",
          resources: [],
          success_metrics: [],
        },
        phase2: {
          activities: [],
          timeline: "",
          resources: [],
          success_metrics: [],
        },
        phase3: {
          activities: [],
          timeline: "",
          resources: [],
          success_metrics: [],
        },
      },
      sequencingOptimization: {
        primaryOpportunity: "",
        secondaryOpportunities: [],
        contingencyPlans: [],
        pivotTriggers: [],
      },
    },
  });

  const sections = [
    {
      id: "strategic-decision-matrix",
      title: "Strategic Business Decision Matrix",
      description: "Map and evaluate all possible business opportunities",
      icon: Target,
      duration: "3-4 days",
      subsections: [
        {
          id: "opportunity-mapping",
          title: "Comprehensive Opportunity Mapping",
          questions: 12,
        },
        {
          id: "market-strategies",
          title: "Market Strategy Selection Matrix",
          questions: 8,
        },
        {
          id: "opportunity-prioritization",
          title: "Opportunity Prioritization Scorecard",
          questions: 10,
        },
      ],
    },
    {
      id: "resource-opportunity-alignment",
      title: "Resource-Opportunity Alignment",
      description:
        "Align opportunities with available and acquirable resources",
      icon: Settings,
      duration: "2-3 days",
      subsections: [
        {
          id: "current-resources",
          title: "Current Resource Inventory",
          questions: 8,
        },
        {
          id: "acquirable-resources",
          title: "Acquirable Resource Assessment",
          questions: 8,
        },
        {
          id: "opportunity-classification",
          title: "Opportunity Classification Framework",
          questions: 6,
        },
        {
          id: "resource-gap-analysis",
          title: "Resource Gap Analysis",
          questions: 8,
        },
      ],
    },
    {
      id: "market-entry-framework",
      title: "Strategic Market Entry Framework",
      description: "Choose optimal market entry strategy for each opportunity",
      icon: TrendingUp,
      duration: "2-3 days",
      subsections: [
        {
          id: "strategy-selection",
          title: "Market Entry Strategy Selection",
          questions: 6,
        },
        {
          id: "tactical-implementation",
          title: "Tactical Implementation Planning",
          questions: 12,
        },
        {
          id: "sequencing-optimization",
          title: "Sequencing and Timing Optimization",
          questions: 8,
        },
      ],
    },
  ];

  // Load existing data
  useEffect(() => {
    const existing = assessmentData["business_development"] || {};
    if (Object.keys(existing).length > 0) {
      setSectionData((prev) => ({ ...prev, ...existing }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Save only when changed (prevent loop)
  const lastSavedRef = useRef("");
  useEffect(() => {
    const serialized = JSON.stringify(sectionData);
    if (serialized !== lastSavedRef.current) {
      updateAssessmentData("business_development", sectionData);
      lastSavedRef.current = serialized;
    }
  }, [sectionData, updateAssessmentData]);

  // Completion
  const calculateSectionCompletion = (sectionId) => {
    const section = sections.find((s) => s.id === sectionId);
    if (!section) return 0;
    const total = section.subsections.reduce(
      (sum, sub) => sum + sub.questions,
      0
    );
    const sectionKey = sectionId.replace(/-([a-z])/g, (_, c) =>
      c.toUpperCase()
    );
    const data = sectionData[sectionKey] || {};
    const count = (obj) =>
      Object.values(obj).reduce((acc, v) => {
        if (typeof v === "string" && v.trim()) return acc + 1;
        if (typeof v === "number" && Number.isFinite(v) && v > 0)
          return acc + 1;
        if (Array.isArray(v) && v.length > 0) return acc + 1;
        if (v && typeof v === "object") return acc + count(v);
        return acc;
      }, 0);
    const answered = count(data);
    return Math.min((answered / total) * 100, 100);
  };
  const overallCompletion =
    sections.reduce((s, sec) => s + calculateSectionCompletion(sec.id), 0) /
    sections.length;

  const updateSectionData = (path, value) => {
    setSectionData((prev) => {
      const next = { ...prev };
      const keys = path.split(".");
      let cur = next;
      for (let i = 0; i < keys.length - 1; i++) {
        if (!cur[keys[i]]) cur[keys[i]] = {};
        cur = cur[keys[i]];
      }
      cur[keys[keys.length - 1]] = value;
      return next;
    });
  };

  const addOpportunity = (type) => {
    const newOpp = {
      id: Date.now(),
      title: "",
      description: "",
      marketSize: "",
      competition: "",
      resources: "",
      timeline: "",
      profitPotential: "",
    };
    const curr =
      sectionData.strategicDecisionMatrix.opportunityMapping[type] || [];
    updateSectionData(`strategicDecisionMatrix.opportunityMapping.${type}`, [
      ...curr,
      newOpp,
    ]);
  };
  const removeOpportunity = (type, id) => {
    const curr =
      sectionData.strategicDecisionMatrix.opportunityMapping[type] || [];
    const filtered = curr.filter((opp) => opp.id !== id);
    updateSectionData(
      `strategicDecisionMatrix.opportunityMapping.${type}`,
      filtered
    );
  };
  const updateOpportunity = (type, id, field, value) => {
    const curr =
      sectionData.strategicDecisionMatrix.opportunityMapping[type] || [];
    const updated = curr.map((opp) =>
      opp.id === id ? { ...opp, [field]: value } : opp
    );
    updateSectionData(
      `strategicDecisionMatrix.opportunityMapping.${type}`,
      updated
    );
  };

  const renderStrategicDecisionMatrixSection = () => (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Comprehensive Opportunity Mapping
          </CardTitle>
          <CardDescription>
            Map all possible business opportunities
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="service" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="service">Service Opportunities</TabsTrigger>
              <TabsTrigger value="product">Product Opportunities</TabsTrigger>
              <TabsTrigger value="hybrid">Hybrid Opportunities</TabsTrigger>
            </TabsList>

            {["service", "product", "hybrid"].map((type) => {
              const key = `${type}Opportunities`;
              const list =
                sectionData.strategicDecisionMatrix.opportunityMapping[key] ||
                [];
              return (
                <TabsContent key={type} value={type} className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h4 className="font-semibold capitalize">
                      {type} Opportunities
                    </h4>
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        addOpportunity(key);
                      }}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add {type.charAt(0).toUpperCase() + type.slice(1)}{" "}
                      Opportunity
                    </Button>
                  </div>

                  {list.map((opportunity, index) => (
                    <Card key={opportunity.id} className="p-4">
                      <div className="flex justify-between items-start mb-4">
                        <h5 className="font-medium">
                          Opportunity #{index + 1}
                        </h5>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            removeOpportunity(key, opportunity.id);
                          }}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label>Opportunity Title</Label>
                          <Input
                            placeholder="Brief, descriptive title"
                            value={opportunity.title || ""}
                            onChange={(e) =>
                              updateOpportunity(
                                key,
                                opportunity.id,
                                "title",
                                e.target.value
                              )
                            }
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <Label>Market Size Estimate</Label>
                          <Input
                            placeholder="e.g., $50M TAM, 10K potential customers"
                            value={opportunity.marketSize || ""}
                            onChange={(e) =>
                              updateOpportunity(
                                key,
                                opportunity.id,
                                "marketSize",
                                e.target.value
                              )
                            }
                            className="mt-1"
                          />
                        </div>
                        <div className="md:col-span-2">
                          <Label>Opportunity Description</Label>
                          <Textarea
                            placeholder="Detailed description..."
                            value={opportunity.description || ""}
                            onChange={(e) =>
                              updateOpportunity(
                                key,
                                opportunity.id,
                                "description",
                                e.target.value
                              )
                            }
                            className="mt-1 min-h-[80px]"
                          />
                        </div>
                        <div>
                          <Label>Competition Level</Label>
                          <Input
                            placeholder="High/Medium/Low with key competitors"
                            value={opportunity.competition || ""}
                            onChange={(e) =>
                              updateOpportunity(
                                key,
                                opportunity.id,
                                "competition",
                                e.target.value
                              )
                            }
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <Label>Resource Requirements</Label>
                          <Input
                            placeholder="Key resources needed"
                            value={opportunity.resources || ""}
                            onChange={(e) =>
                              updateOpportunity(
                                key,
                                opportunity.id,
                                "resources",
                                e.target.value
                              )
                            }
                            className="mt-1"
                          />
                        </div>
                      </div>
                    </Card>
                  ))}

                  {list.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <Building className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No {type} opportunities added yet.</p>
                    </div>
                  )}
                </TabsContent>
              );
            })}
          </Tabs>
        </CardContent>
      </Card>

      {/* Market Strategy Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Market Strategy Selection Matrix
          </CardTitle>
          <CardDescription>
            Choose your market entry approach (Ansoff Matrix)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              {
                key: "existingProductExistingMarket",
                title: "Market Penetration",
                subtitle: "Existing Product → Existing Market",
                description:
                  "Grow market share with current products in current markets",
                riskLevel: 1,
                examples: "Marketing, CS improvements, pricing",
              },
              {
                key: "existingProductNewMarket",
                title: "Market Development",
                subtitle: "Existing Product → New Market",
                description: "Enter new markets/segments with current products",
                riskLevel: 3,
                examples: "Geography, new segments, new channels",
              },
              {
                key: "newProductExistingMarket",
                title: "Product Development",
                subtitle: "New Product → Existing Market",
                description: "Develop new products for current customers",
                riskLevel: 3,
                examples: "Line extensions, new features",
              },
              {
                key: "newProductNewMarket",
                title: "Diversification",
                subtitle: "New Product → New Market",
                description: "New business in new markets",
                riskLevel: 5,
                examples: "Unrelated diversification, acquisitions",
              },
            ].map((strategy) => {
              const selected =
                sectionData.strategicDecisionMatrix.marketStrategies[
                  strategy.key
                ]?.selected || false;
              return (
                <Card
                  key={strategy.key}
                  className={`p-4 ${selected ? "ring-2 ring-primary" : ""}`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h4 className="font-semibold">{strategy.title}</h4>
                      <p className="text-sm text-muted-foreground">
                        {strategy.subtitle}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge
                        variant={
                          strategy.riskLevel <= 2
                            ? "default"
                            : strategy.riskLevel <= 3
                            ? "secondary"
                            : "destructive"
                        }
                      >
                        Risk: {strategy.riskLevel}/5
                      </Badge>
                      <input
                        type="checkbox"
                        checked={selected}
                        onChange={(e) =>
                          updateSectionData(
                            `strategicDecisionMatrix.marketStrategies.${strategy.key}.selected`,
                            e.target.checked
                          )
                        }
                        className="w-4 h-4"
                      />
                    </div>
                  </div>

                  <p className="text-sm text-muted-foreground mb-3">
                    {strategy.description}
                  </p>
                  <p className="text-xs text-muted-foreground mb-3">
                    Examples: {strategy.examples}
                  </p>

                  {selected && (
                    <div className="space-y-3 mt-4 pt-4 border-t">
                      <div>
                        <Label className="text-xs">Strategy Description</Label>
                        <Textarea
                          placeholder="Describe how you'll implement this strategy..."
                          value={
                            sectionData.strategicDecisionMatrix
                              .marketStrategies[strategy.key]?.description || ""
                          }
                          onChange={(e) =>
                            updateSectionData(
                              `strategicDecisionMatrix.marketStrategies.${strategy.key}.description`,
                              e.target.value
                            )
                          }
                          className="mt-1 min-h-[60px]"
                        />
                      </div>
                      <div>
                        <Label className="text-xs">Expected Timeframe</Label>
                        <Input
                          placeholder="e.g., 6-12 months"
                          value={
                            sectionData.strategicDecisionMatrix
                              .marketStrategies[strategy.key]?.timeframe || ""
                          }
                          onChange={(e) =>
                            updateSectionData(
                              `strategicDecisionMatrix.marketStrategies.${strategy.key}.timeframe`,
                              e.target.value
                            )
                          }
                          className="mt-1"
                        />
                      </div>
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderResourceOpportunityAlignmentSection = () => (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Current Resource Inventory
          </CardTitle>
          <CardDescription>Assess your current resources</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              { key: "human", title: "Human Resources", icon: Users },
              {
                key: "financial",
                title: "Financial Resources",
                icon: DollarSign,
              },
              { key: "physical", title: "Physical Resources", icon: Building },
              { key: "intangible", title: "Intangible Resources", icon: Zap },
            ].map((resource) => {
              const Icon = resource.icon;
              const adequacy =
                sectionData.resourceOpportunityAlignment.currentResources[
                  resource.key
                ]?.adequacy ?? 5;
              return (
                <Card key={resource.key} className="p-4">
                  <div className="flex items-center gap-2 mb-4">
                    <Icon className="h-5 w-5 text-primary" />
                    <h4 className="font-semibold">{resource.title}</h4>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm">Available Resources</Label>
                      <Textarea
                        placeholder="Describe resources..."
                        value={
                          sectionData.resourceOpportunityAlignment
                            .currentResources[resource.key]?.description || ""
                        }
                        onChange={(e) =>
                          updateSectionData(
                            `resourceOpportunityAlignment.currentResources.${resource.key}.description`,
                            e.target.value
                          )
                        }
                        className="mt-1 min-h-[80px]"
                      />
                    </div>

                    <div>
                      <Label className="text-sm">
                        Resource Adequacy (1-10)
                      </Label>
                      <div className="mt-2">
                        <Slider
                          value={[adequacy]}
                          onValueChange={(v) => {
                            const next = Number(v?.[0] ?? 0);
                            if (next !== adequacy) {
                              updateSectionData(
                                `resourceOpportunityAlignment.currentResources.${resource.key}.adequacy`,
                                next
                              );
                            }
                          }}
                          max={10}
                          step={1}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-muted-foreground mt-1">
                          <span>Insufficient</span>
                          <span>{adequacy}/10</span>
                          <span>Excellent</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Opportunity Classification */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Opportunity Classification Framework
          </CardTitle>
          <CardDescription>Classify opportunities by fit</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { key: "perfectFit", title: "Perfect Fit", icon: CheckCircle },
              { key: "stretch", title: "Stretch", icon: AlertCircle },
              { key: "aspirational", title: "Aspirational", icon: Star },
            ].map((cat) => {
              const Icon = cat.icon;
              const value = (
                sectionData.resourceOpportunityAlignment
                  .opportunityClassification[cat.key] || []
              ).join("\n");
              return (
                <Card key={cat.key} className="p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Icon className="h-5 w-5 text-primary" />
                    <h4 className="font-semibold">{cat.title}</h4>
                  </div>
                  <Textarea
                    placeholder={`List ${cat.title.toLowerCase()} opportunities...`}
                    value={value}
                    onChange={(e) =>
                      updateSectionData(
                        `resourceOpportunityAlignment.opportunityClassification.${cat.key}`,
                        e.target.value.split("\n").filter(Boolean)
                      )
                    }
                    className="min-h-[100px]"
                  />
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderMarketEntryFrameworkSection = () => {
    const risk =
      sectionData.marketEntryFramework.strategySelection.riskAssessment ?? 5;
    return (
      <div className="space-y-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Market Entry Strategy Selection
            </CardTitle>
            <CardDescription>Choose your primary strategy</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <Label>Selected Primary Strategy</Label>
              <RadioGroup
                value={
                  sectionData.marketEntryFramework.strategySelection
                    .selectedStrategy || ""
                }
                onValueChange={(value) =>
                  updateSectionData(
                    "marketEntryFramework.strategySelection.selectedStrategy",
                    value
                  )
                }
                className="mt-2"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem
                    value="market-penetration"
                    id="market-penetration"
                  />
                  <Label htmlFor="market-penetration">Market Penetration</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem
                    value="market-development"
                    id="market-development"
                  />
                  <Label htmlFor="market-development">Market Development</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem
                    value="product-development"
                    id="product-development"
                  />
                  <Label htmlFor="product-development">
                    Product Development
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem
                    value="diversification"
                    id="diversification"
                  />
                  <Label htmlFor="diversification">Diversification</Label>
                </div>
              </RadioGroup>
            </div>

            <div>
              <Label>Strategy Rationale</Label>
              <Textarea
                placeholder="Explain why this strategy is optimal..."
                value={
                  sectionData.marketEntryFramework.strategySelection
                    .rationale || ""
                }
                onChange={(e) =>
                  updateSectionData(
                    "marketEntryFramework.strategySelection.rationale",
                    e.target.value
                  )
                }
                className="mt-2 min-h-[100px]"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Risk Assessment (1-10)</Label>
                <div className="mt-2">
                  <Slider
                    value={[risk]}
                    onValueChange={(v) => {
                      const next = Number(v?.[0] ?? 0);
                      if (next !== risk)
                        updateSectionData(
                          "marketEntryFramework.strategySelection.riskAssessment",
                          next
                        );
                    }}
                    max={10}
                    step={1}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground mt-1">
                    <span>Low Risk</span>
                    <span>{risk}/10</span>
                    <span>High Risk</span>
                  </div>
                </div>
              </div>

              <div>
                <Label>Expected Timeline</Label>
                <Input
                  placeholder="e.g., 6-18 months"
                  value={
                    sectionData.marketEntryFramework.strategySelection
                      .expectedTimeline || ""
                  }
                  onChange={(e) =>
                    updateSectionData(
                      "marketEntryFramework.strategySelection.expectedTimeline",
                      e.target.value
                    )
                  }
                  className="mt-2"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tactical Implementation */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ArrowRight className="h-5 w-5" />
              Tactical Implementation Planning
            </CardTitle>
            <CardDescription>
              Break down your strategy into phases
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                {
                  key: "phase1",
                  title: "Phase 1: Foundation",
                  desc: "Initial setup and preparation",
                },
                {
                  key: "phase2",
                  title: "Phase 2: Launch",
                  desc: "Market entry & acquisition",
                },
                {
                  key: "phase3",
                  title: "Phase 3: Growth",
                  desc: "Scaling & optimization",
                },
              ].map((phase) => {
                const act = (
                  sectionData.marketEntryFramework.tacticalImplementation[
                    phase.key
                  ]?.activities || []
                ).join("\n");
                const metrics = (
                  sectionData.marketEntryFramework.tacticalImplementation[
                    phase.key
                  ]?.success_metrics || []
                ).join("\n");
                return (
                  <Card key={phase.key} className="p-4">
                    <h4 className="font-semibold mb-2">{phase.title}</h4>
                    <p className="text-sm text-muted-foreground mb-4">
                      {phase.desc}
                    </p>

                    <div className="space-y-3">
                      <div>
                        <Label className="text-xs">Key Activities</Label>
                        <Textarea
                          placeholder="List main activities..."
                          value={act}
                          onChange={(e) =>
                            updateSectionData(
                              `marketEntryFramework.tacticalImplementation.${phase.key}.activities`,
                              e.target.value.split("\n").filter(Boolean)
                            )
                          }
                          className="mt-1 min-h-[60px]"
                        />
                      </div>
                      <div>
                        <Label className="text-xs">Timeline</Label>
                        <Input
                          placeholder="e.g., Months 1-3"
                          value={
                            sectionData.marketEntryFramework
                              .tacticalImplementation[phase.key]?.timeline || ""
                          }
                          onChange={(e) =>
                            updateSectionData(
                              `marketEntryFramework.tacticalImplementation.${phase.key}.timeline`,
                              e.target.value
                            )
                          }
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <Label className="text-xs">Success Metrics</Label>
                        <Textarea
                          placeholder="How will you measure success?"
                          value={metrics}
                          onChange={(e) =>
                            updateSectionData(
                              `marketEntryFramework.tacticalImplementation.${phase.key}.success_metrics`,
                              e.target.value.split("\n").filter(Boolean)
                            )
                          }
                          className="mt-1 min-h-[40px]"
                        />
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderCurrentSection = () => {
    switch (currentSection) {
      case 0:
        return renderStrategicDecisionMatrixSection();
      case 1:
        return renderResourceOpportunityAlignmentSection();
      case 2:
        return renderMarketEntryFrameworkSection();
      default:
        return renderStrategicDecisionMatrixSection();
    }
  };

  return (
    <div className="space-y-6">
      {/* Section Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {sections.map((section, index) => {
          const Icon = section.icon;
          const completion = calculateSectionCompletion(section.id);
          const isActive = currentSection === index;
          return (
            <Card
              key={section.id}
              className={`cursor-pointer transition-all duration-300 ${
                isActive ? "ring-2 ring-primary" : "hover:shadow-lg"
              }`}
              onClick={() => setCurrentSection(index)}
            >
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <Icon className="h-5 w-5 text-primary" />
                  {completion === 100 && (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  )}
                </div>
                <h3 className="font-semibold text-sm mb-1">{section.title}</h3>
                <p className="text-xs text-muted-foreground mb-2">
                  {section.description}
                </p>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span>{Math.round(completion)}% complete</span>
                    <Badge variant="secondary" className="text-xs">
                      {section.duration}
                    </Badge>
                  </div>
                  <Progress value={completion} className="h-1" />
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Overall Progress */}
      <Card>
        <CardContent className="p-4">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">
              Business Development & Decision Making Progress
            </h3>
            <span className="text-sm text-muted-foreground">
              {Math.round(overallCompletion)}% Complete
            </span>
          </div>
          <Progress value={overallCompletion} className="h-2" />
        </CardContent>
      </Card>

      {/* Current Section */}
      <div>{renderCurrentSection()}</div>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={() => setCurrentSection(Math.max(0, currentSection - 1))}
          disabled={currentSection === 0}
        >
          Previous Section
        </Button>
        {currentSection === sections.length - 1 ? (
          <Button
            onClick={() => {
              completePhase('business_development')
              updatePhase('business_prototype_testing')
            }}
          >
            Next Phase
          </Button>
        ) : (
          <Button
            onClick={() =>
              setCurrentSection(Math.min(sections.length - 1, currentSection + 1))
            }
          >
            Next Section
          </Button>
        )}
      </div>
    </div>
  );
};

export default BusinessDevelopmentDecisionMaking;
