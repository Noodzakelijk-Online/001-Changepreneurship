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
  Users,
  DollarSign,
  Target,
  BarChart3,
  Star,
  CheckCircle,
  Plus,
  Trash2,
} from "lucide-react";
import { useAssessment } from "../../contexts/AssessmentContext";

const ProductConceptTesting = () => {
  const { assessmentData, updateAssessmentData, completePhase, updatePhase } = useAssessment();
  const [currentSection, setCurrentSection] = useState(0);

  const [sectionData, setSectionData] = useState({
    marketAcceptability: {
      testDesign: {
        primaryTarget: 70,
        adjacentSegments: 20,
        edgeCases: 10,
        sampleSize: 100,
        testingMethod: "",
        conceptMaterials: [],
      },
      feedbackFramework: {
        effectiveness: "",
        meaning: "",
        usageIntention: "",
        pricingExpectations: "",
        recommendationLikelihood: "",
      },
      crossSegmentValidation: {
        segments: [],
        validationResults: {},
      },
      investmentCriteria: {
        quantitativeThresholds: {
          conceptAppeal: 40,
          purchaseIntent: 30,
          willingnessToPay: "",
          differentiation: 60,
        },
        qualitativeIndicators: [],
        riskFactors: [],
      },
    },
    priceAcceptability: {
      priceTestingDesign: {
        testingMethod: "",
        pricePoints: [],
        testingMaterials: [],
      },
      pricingInsights: {
        bullsEyeTarget: "",
        productPositioning: "",
        optimalPricing: "",
        futureViability: "",
      },
      priceValuePerception: {
        valueAssessment: "",
        behavioralIndicators: [],
        competitiveBenchmarking: "",
      },
      secondaryBenefits: {
        wordOfMouth: [],
        marketingIntelligence: [],
        productDevelopmentInputs: [],
      },
    },
    integratedTesting: {
      testingSequence: {
        phase1: { completed: false, insights: "" },
        phase2: { completed: false, insights: "" },
        phase3: { completed: false, insights: "" },
      },
      methodologySelection: {
        qualitativeMethods: [],
        quantitativeMethods: [],
        behavioralMethods: [],
      },
      actionableResults: {
        decisionCriteria: [],
        segmentedAnalysis: "",
        iterativeImprovement: "",
      },
    },
    resultsAnalysis: {
      dataAnalysis: {
        quantitativeAnalysis: "",
        qualitativeAnalysis: "",
        integratedInsights: "",
      },
      goNoGoDecision: {
        marketDemand: { score: 0, weight: 30 },
        priceAcceptance: { score: 0, weight: 25 },
        competitivePosition: { score: 0, weight: 25 },
        executionFeasibility: { score: 0, weight: 20 },
        overallScore: 0,
        decision: "",
      },
      conceptOptimization: {
        productRefinement: [],
        pricingOptimization: [],
        marketingOptimization: [],
        implementationPlan: "",
      },
    },
  });

  const sections = [
    {
      id: "market-acceptability",
      title: "Market Acceptability Testing",
      description: "Test product concept appeal with diverse customer segments",
      icon: Users,
      duration: "1-2 weeks",
      subsections: [
        {
          id: "test-design",
          title: "Test Design & Sample Selection",
          questions: 8,
        },
        {
          id: "feedback-framework",
          title: "Comprehensive Feedback Framework",
          questions: 12,
        },
        {
          id: "cross-segment",
          title: "Cross-Segment Validation",
          questions: 6,
        },
        {
          id: "investment-criteria",
          title: "Investment Decision Criteria",
          questions: 10,
        },
      ],
    },
    {
      id: "price-acceptability",
      title: "Price Acceptability Testing",
      description: "Optimize pricing strategy through systematic testing",
      icon: DollarSign,
      duration: "1-2 weeks",
      subsections: [
        { id: "price-design", title: "Price Testing Design", questions: 8 },
        {
          id: "pricing-insights",
          title: "Pricing Insights Framework",
          questions: 10,
        },
        { id: "price-value", title: "Price-Value Perception", questions: 8 },
        { id: "secondary-benefits", title: "Secondary Benefits", questions: 6 },
      ],
    },
    {
      id: "integrated-testing",
      title: "Integrated Testing Approach",
      description:
        "Combine product and price testing for comprehensive validation",
      icon: Target,
      duration: "2-3 weeks",
      subsections: [
        {
          id: "testing-sequence",
          title: "Testing Sequence Optimization",
          questions: 6,
        },
        {
          id: "methodology",
          title: "Testing Methodology Selection",
          questions: 8,
        },
        {
          id: "actionable-results",
          title: "Actionable Results Framework",
          questions: 8,
        },
      ],
    },
    {
      id: "results-analysis",
      title: "Results Analysis & Decision Making",
      description:
        "Make evidence-based business decisions using systematic analysis",
      icon: BarChart3,
      duration: "3-4 days",
      subsections: [
        { id: "data-analysis", title: "Data Analysis Framework", questions: 6 },
        { id: "go-no-go", title: "Go/No-Go Decision Matrix", questions: 8 },
        {
          id: "optimization",
          title: "Concept Optimization Framework",
          questions: 10,
        },
      ],
    },
  ];

  // Load existing data (once)
  useEffect(() => {
    const existingData = assessmentData["product_concept_testing"] || {};
    if (Object.keys(existingData).length > 0) {
      setSectionData((prev) => ({ ...prev, ...existingData }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Save data only when changed (prevent update loop)
  const lastSavedRef = useRef("");
  useEffect(() => {
    const serialized = JSON.stringify(sectionData);
    if (serialized !== lastSavedRef.current) {
      updateAssessmentData("product_concept_testing", sectionData);
      lastSavedRef.current = serialized;
    }
  }, [sectionData, updateAssessmentData]);

  // Helpers
  const calculateSectionCompletion = (sectionId) => {
    const section = sections.find((s) => s.id === sectionId);
    if (!section) return 0;
    const totalQuestions = section.subsections.reduce(
      (sum, s) => sum + s.questions,
      0
    );
    const data =
      sectionData[
        sectionId
          .replace(/-([a-z])/g, (_, c) => c.toUpperCase()) // kebab-case → camelCase
          .replace(/-/g, "")
      ] || {};
    const countAnswered = (obj) =>
      Object.values(obj).reduce((count, val) => {
        if (typeof val === "string" && val.trim()) return count + 1;
        if (typeof val === "number" && Number.isFinite(val) && val > 0)
          return count + 1;
        if (Array.isArray(val) && val.length > 0) return count + 1;
        if (val && typeof val === "object") return count + countAnswered(val);
        return count;
      }, 0);
    const answered = countAnswered(data);
    return Math.min((answered / totalQuestions) * 100, 100);
  };

  const overallCompletion =
    sections.reduce((sum, s) => sum + calculateSectionCompletion(s.id), 0) /
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

  // === RENDERERS ===

  const renderMarketAcceptabilitySection = () => {
    const pt = sectionData.marketAcceptability.testDesign.primaryTarget ?? 0;
    const adj =
      sectionData.marketAcceptability.testDesign.adjacentSegments ?? 0;
    const edge = sectionData.marketAcceptability.testDesign.edgeCases ?? 0;

    return (
      <div className="space-y-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Test Design & Sample Selection
            </CardTitle>
            <CardDescription>
              Design your product concept test for maximum learning with diverse
              customer segments
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label>Primary Target Segment (%)</Label>
                <div className="mt-2">
                  <Slider
                    value={[pt]}
                    onValueChange={(v) => {
                      const next = Number(v?.[0] ?? 0);
                      if (next !== pt) {
                        updateSectionData(
                          "marketAcceptability.testDesign.primaryTarget",
                          next
                        );
                      }
                    }}
                    max={100}
                    step={5}
                    className="w-full"
                  />
                  <div className="text-sm text-muted-foreground mt-1">
                    {pt}% - Core customer segment from Part 4
                  </div>
                </div>
              </div>

              <div>
                <Label>Adjacent Segments (%)</Label>
                <div className="mt-2">
                  <Slider
                    value={[adj]}
                    onValueChange={(v) => {
                      const next = Number(v?.[0] ?? 0);
                      if (next !== adj) {
                        updateSectionData(
                          "marketAcceptability.testDesign.adjacentSegments",
                          next
                        );
                      }
                    }}
                    max={50}
                    step={5}
                    className="w-full"
                  />
                  <div className="text-sm text-muted-foreground mt-1">
                    {adj}% - Related segments for expansion
                  </div>
                </div>
              </div>

              <div>
                <Label>Edge Cases (%)</Label>
                <div className="mt-2">
                  <Slider
                    value={[edge]}
                    onValueChange={(v) => {
                      const next = Number(v?.[0] ?? 0);
                      if (next !== edge) {
                        updateSectionData(
                          "marketAcceptability.testDesign.edgeCases",
                          next
                        );
                      }
                    }}
                    max={20}
                    step={5}
                    className="w-full"
                  />
                  <div className="text-sm text-muted-foreground mt-1">
                    {edge}% - Outside typical profile
                  </div>
                </div>
              </div>
            </div>

            <div>
              <Label>Target Sample Size</Label>
              <Input
                type="number"
                placeholder="100-300 participants for statistical validity"
                value={
                  sectionData.marketAcceptability.testDesign.sampleSize ?? 0
                }
                onChange={(e) =>
                  updateSectionData(
                    "marketAcceptability.testDesign.sampleSize",
                    Number(e.target.value) || 0
                  )
                }
                className="mt-2"
              />
            </div>

            <div>
              <Label>Testing Methodology</Label>
              <RadioGroup
                value={
                  sectionData.marketAcceptability.testDesign.testingMethod || ""
                }
                onValueChange={(value) =>
                  updateSectionData(
                    "marketAcceptability.testDesign.testingMethod",
                    value
                  )
                }
                className="mt-2"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="monadic" id="monadic" />
                  <Label htmlFor="monadic">
                    Monadic Testing - Single concept evaluation
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="sequential" id="sequential" />
                  <Label htmlFor="sequential">
                    Sequential Monadic - Multiple concepts in sequence
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="comparative" id="comparative" />
                  <Label htmlFor="comparative">
                    Comparative Testing - Direct concept comparison
                  </Label>
                </div>
              </RadioGroup>
            </div>
          </CardContent>
        </Card>

        {/* Feedback Framework */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5" />
              Comprehensive Feedback Framework
            </CardTitle>
            <CardDescription>
              Systematic approach to gathering valuable customer insights on
              your product concept
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {[
              ["effectiveness", "Product Effectiveness Assessment"],
              ["meaning", "Product Meaning and Relevance"],
              ["usageIntention", "Usage Intention Analysis"],
              ["pricingExpectations", "Pricing Expectations"],
              ["recommendationLikelihood", "Recommendation Likelihood"],
            ].map(([key, label]) => (
              <div key={key}>
                <Label>{label}</Label>
                <Textarea
                  placeholder="Write your plan/notes..."
                  value={
                    sectionData.marketAcceptability.feedbackFramework[key] || ""
                  }
                  onChange={(e) =>
                    updateSectionData(
                      `marketAcceptability.feedbackFramework.${key}`,
                      e.target.value
                    )
                  }
                  className="mt-2 min-h-[100px]"
                />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderPriceAcceptabilitySection = () => (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Price Testing Design Methodology
          </CardTitle>
          <CardDescription>
            Systematic approach to understanding optimal pricing strategy
            through customer testing
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label>Price Testing Approach</Label>
            <RadioGroup
              value={
                sectionData.priceAcceptability.priceTestingDesign
                  .testingMethod || ""
              }
              onValueChange={(value) =>
                updateSectionData(
                  "priceAcceptability.priceTestingDesign.testingMethod",
                  value
                )
              }
              className="mt-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="van-westendorp" id="van-westendorp" />
                <Label htmlFor="van-westendorp">
                  Van Westendorp Price Sensitivity Method
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="sample-sales" id="sample-sales" />
                <Label htmlFor="sample-sales">
                  Sample Sales Testing with Inaugural Price
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="value-bundle" id="value-bundle" />
                <Label htmlFor="value-bundle">Value Bundle Testing</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem
                  value="competitive-price"
                  id="competitive-price"
                />
                <Label htmlFor="competitive-price">
                  Competitive Price Testing
                </Label>
              </div>
            </RadioGroup>
          </div>

          <div>
            <Label>Price Points to Test</Label>
            <div className="mt-2 space-y-2">
              {(
                sectionData.priceAcceptability.priceTestingDesign.pricePoints ||
                []
              ).map((price, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Input
                    type="number"
                    placeholder="Price point"
                    value={price.value ?? ""}
                    onChange={(e) => {
                      const list = [
                        ...(sectionData.priceAcceptability.priceTestingDesign
                          .pricePoints || []),
                      ];
                      list[index] = {
                        ...price,
                        value: Number(e.target.value) || 0,
                      };
                      updateSectionData(
                        "priceAcceptability.priceTestingDesign.pricePoints",
                        list
                      );
                    }}
                    className="flex-1"
                  />
                  <Input
                    placeholder="Description (e.g., Premium, Standard, Budget)"
                    value={price.description ?? ""}
                    onChange={(e) => {
                      const list = [
                        ...(sectionData.priceAcceptability.priceTestingDesign
                          .pricePoints || []),
                      ];
                      list[index] = { ...price, description: e.target.value };
                      updateSectionData(
                        "priceAcceptability.priceTestingDesign.pricePoints",
                        list
                      );
                    }}
                    className="flex-1"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation(); // prevent parent click
                      const list = (
                        sectionData.priceAcceptability.priceTestingDesign
                          .pricePoints || []
                      ).filter((_, i) => i !== index);
                      updateSectionData(
                        "priceAcceptability.priceTestingDesign.pricePoints",
                        list
                      );
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              <Button
                variant="outline"
                onClick={(e) => {
                  e.stopPropagation();
                  const list = [
                    ...(sectionData.priceAcceptability.priceTestingDesign
                      .pricePoints || []),
                    { value: 0, description: "" },
                  ];
                  updateSectionData(
                    "priceAcceptability.priceTestingDesign.pricePoints",
                    list
                  );
                }}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Price Point
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderIntegratedTestingSection = () => (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Testing Sequence Optimization
          </CardTitle>
          <CardDescription>
            Three-phase approach for maximum insight generation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {["phase1", "phase2", "phase3"].map((phase, i) => (
              <Card key={phase} className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold">
                    {i === 0
                      ? "Phase 1: Concept-Only"
                      : i === 1
                      ? "Phase 2: Price Introduction"
                      : "Phase 3: Purchase Simulation"}
                  </h4>
                  <Badge
                    variant={
                      sectionData.integratedTesting.testingSequence[phase]
                        ?.completed
                        ? "default"
                        : "secondary"
                    }
                  >
                    {i === 0 ? "Week 1" : i === 1 ? "Week 2" : "Weeks 2-3"}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  {i === 0
                    ? "Test product concept without price to understand pure product appeal"
                    : i === 1
                    ? "Introduce pricing to understand price-value relationship"
                    : "Simulate actual purchase decisions with real commitment"}
                </p>
                <Textarea
                  placeholder="Document insights..."
                  value={
                    sectionData.integratedTesting.testingSequence[phase]
                      ?.insights || ""
                  }
                  onChange={(e) =>
                    updateSectionData(
                      `integratedTesting.testingSequence.${phase}.insights`,
                      e.target.value
                    )
                  }
                  className="min-h-[80px]"
                />
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderResultsAnalysisSection = () => {
    const md =
      sectionData.resultsAnalysis.goNoGoDecision.marketDemand.score ?? 0;
    const pa =
      sectionData.resultsAnalysis.goNoGoDecision.priceAcceptance.score ?? 0;
    const cp =
      sectionData.resultsAnalysis.goNoGoDecision.competitivePosition.score ?? 0;
    const ef =
      sectionData.resultsAnalysis.goNoGoDecision.executionFeasibility.score ??
      0;

    const overallScore = (md * 0.3 + pa * 0.25 + cp * 0.25 + ef * 0.2).toFixed(
      1
    );

    let decision = "";
    let decisionColor = "";
    if (overallScore >= 7.0) {
      decision = "Strong GO - Proceed with confidence";
      decisionColor = "text-green-600";
    } else if (overallScore >= 5.0) {
      decision = "Conditional GO - Proceed with modifications";
      decisionColor = "text-yellow-600";
    } else {
      decision = "NO GO - Pivot or abandon";
      decisionColor = "text-red-600";
    }

    return (
      <div className="space-y-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Go/No-Go Decision Matrix
            </CardTitle>
            <CardDescription>
              Weighted scoring across key criteria
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                [
                  "Market Demand (30%)",
                  "resultsAnalysis.goNoGoDecision.marketDemand.score",
                  md,
                  10,
                ],
                [
                  "Price Acceptance (25%)",
                  "resultsAnalysis.goNoGoDecision.priceAcceptance.score",
                  pa,
                  10,
                ],
                [
                  "Competitive Position (25%)",
                  "resultsAnalysis.goNoGoDecision.competitivePosition.score",
                  cp,
                  10,
                ],
                [
                  "Execution Feasibility (20%)",
                  "resultsAnalysis.goNoGoDecision.executionFeasibility.score",
                  ef,
                  10,
                ],
              ].map(([label, path, cur, max]) => (
                <div key={path}>
                  <Label>{label}</Label>
                  <div className="mt-2">
                    <Slider
                      value={[cur]}
                      onValueChange={(v) => {
                        const next = Number(v?.[0] ?? 0);
                        if (next !== cur) updateSectionData(path, next);
                      }}
                      max={max}
                      step={0.5}
                      className="w-full"
                    />
                    <div className="text-sm text-muted-foreground mt-1">
                      Score: {cur}/{max}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 bg-muted rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">Overall Decision Score</h4>
                <Badge variant="outline" className="text-lg">
                  {overallScore}/10
                </Badge>
              </div>
              <div className={`font-semibold ${decisionColor}`}>{decision}</div>
              <Progress value={Number(overallScore) * 10} className="mt-2" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderCurrentSection = () => {
    switch (currentSection) {
      case 0:
        return renderMarketAcceptabilitySection();
      case 1:
        return renderPriceAcceptabilitySection();
      case 2:
        return renderIntegratedTestingSection();
      case 3:
        return renderResultsAnalysisSection();
      default:
        return renderMarketAcceptabilitySection();
    }
  };

  return (
    <div className="space-y-6">
      {/* Section Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
            <h3 className="font-semibold">Product Concept Testing Progress</h3>
            <span className="text-sm text-muted-foreground">
              {Math.round(overallCompletion)}% Complete
            </span>
          </div>
          <Progress value={overallCompletion} className="h-2" />
        </CardContent>
      </Card>

      {/* Current Section Content */}
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
              completePhase('product_concept_testing')
              updatePhase('business_development')
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

export default ProductConceptTesting;
