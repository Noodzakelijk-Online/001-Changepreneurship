import React, { useState, useEffect } from "react";
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
  Rocket,
  Users,
  DollarSign,
  Target,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Plus,
  Trash2,
  BarChart3,
  PieChart,
  Lightbulb,
  Star,
  MessageSquare,
  Package,
  Globe,
  Zap,
  Heart,
  Brain,
  Eye,
  ThumbsUp,
  ShoppingCart,
  Megaphone,
} from "lucide-react";
import { useAssessment } from "../../contexts/AssessmentContext";

const BusinessPrototypeTesting = () => {
  const { assessmentData, updateAssessmentData, completePhase, updatePhase } = useAssessment();
  const [currentSection, setCurrentSection] = useState(0);
  const [sectionData, setSectionData] = useState({
    customerValueProposition: {
      cvpDevelopment: {
        customerJobs: [],
        painPoints: [],
        gains: [],
        products: [],
        painRelievers: [],
        gainCreators: [],
        uniqueSellingProposition: "",
      },
      messageTestingFramework: {
        primaryMessage: "",
        alternativeMessages: [],
        testingMethods: [],
        targetAudiences: [],
        messagingChannels: [],
      },
      touchpointConsistency: {
        touchpoints: [],
        consistencyChecklist: [],
        brandGuidelines: "",
      },
    },
    productDevelopmentReadiness: {
      productReadinessChecklist: {
        coreFeatures: [],
        qualityStandards: [],
        userExperience: [],
        technicalRequirements: [],
        complianceRequirements: [],
      },
      productIdentityPackaging: {
        brandIdentity: "",
        visualDesign: "",
        packaging: "",
        userInterface: "",
        customerExperience: "",
      },
      qualityAssuranceScalability: {
        qualityProcesses: [],
        scalabilityPlan: "",
        operationalReadiness: [],
        supplyChainReadiness: "",
      },
    },
    consumerSampleBaseFeedback: {
      customerSampleStrategy: {
        sampleSize: 50,
        selectionCriteria: "",
        recruitmentMethod: "",
        incentiveStructure: "",
        testingEnvironment: "",
      },
      thinkFeelDoFramework: {
        thinkQuestions: [],
        feelQuestions: [],
        doQuestions: [],
        feedbackCollection: "",
        analysisMethod: "",
      },
      feedbackAnalysisAction: {
        quantitativeAnalysis: "",
        qualitativeInsights: "",
        actionPriorities: [],
        productIterations: [],
        implementationPlan: "",
      },
    },
    marketingSalesOptimization: {
      customerPurchaseFunnel: {
        awareness: { tactics: [], metrics: [], optimization: "" },
        interest: { tactics: [], metrics: [], optimization: "" },
        consideration: { tactics: [], metrics: [], optimization: "" },
        purchase: { tactics: [], metrics: [], optimization: "" },
        retention: { tactics: [], metrics: [], optimization: "" },
      },
      channelTestingOptimization: {
        digitalChannels: [],
        traditionalChannels: [],
        partnerChannels: [],
        channelPerformance: [],
        optimizationStrategy: "",
      },
      communicationDevelopment: {
        keyMessages: [],
        contentStrategy: "",
        competitivePositioning: "",
        brandVoice: "",
        communicationCalendar: "",
      },
    },
    pricingStrategyTesting: {
      pricingStrategyDevelopment: {
        pricingModel: "",
        pricePoints: [],
        valueJustification: "",
        competitivePricing: "",
        pricingPsychology: "",
      },
      marketPricingValidation: {
        testingMethods: [],
        priceElasticity: "",
        customerWillingness: "",
        competitiveResponse: "",
        revenueProjections: "",
      },
      revenueModelOptimization: {
        revenueStreams: [],
        monetizationStrategy: "",
        scalingStrategy: "",
        profitabilityAnalysis: "",
        financialProjections: "",
      },
    },
  });

  const sections = [
    {
      id: "customer-value-proposition",
      title: "Customer Value Proposition Development",
      description: "Create and validate compelling value proposition",
      icon: Target,
      duration: "3-4 days",
      subsections: [
        {
          id: "cvp-development",
          title: "Value Proposition Canvas Development",
          questions: 10,
        },
        {
          id: "message-testing",
          title: "Message Testing Framework",
          questions: 8,
        },
        {
          id: "touchpoint-consistency",
          title: "Multi-Touchpoint Consistency",
          questions: 6,
        },
      ],
    },
    {
      id: "product-development-readiness",
      title: "Product Development & Market Readiness",
      description: "Prepare market-ready product that delivers on promises",
      icon: Package,
      duration: "1-2 weeks",
      subsections: [
        {
          id: "product-readiness",
          title: "Product Readiness Checklist",
          questions: 12,
        },
        {
          id: "product-identity",
          title: "Product Identity & Packaging",
          questions: 8,
        },
        {
          id: "quality-scalability",
          title: "Quality Assurance & Scalability",
          questions: 8,
        },
      ],
    },
    {
      id: "consumer-sample-feedback",
      title: "Consumer Sample Base & Feedback",
      description: "Build systematic customer testing group",
      icon: Users,
      duration: "2-3 days",
      subsections: [
        {
          id: "customer-sample",
          title: "Customer Sample Selection Strategy",
          questions: 8,
        },
        {
          id: "think-feel-do",
          title: "Think-Feel-Do Feedback Framework",
          questions: 10,
        },
        {
          id: "feedback-analysis",
          title: "Feedback Analysis & Action Planning",
          questions: 8,
        },
      ],
    },
    {
      id: "marketing-sales-optimization",
      title: "Marketing & Sales Channel Optimization",
      description: "Test and optimize marketing and sales channels",
      icon: Megaphone,
      duration: "1-2 weeks",
      subsections: [
        {
          id: "purchase-funnel",
          title: "Customer Purchase Funnel Framework",
          questions: 15,
        },
        {
          id: "channel-testing",
          title: "Multi-Channel Testing & Optimization",
          questions: 10,
        },
        {
          id: "communication-development",
          title: "Communication Development",
          questions: 8,
        },
      ],
    },
    {
      id: "pricing-strategy-testing",
      title: "Pricing Strategy & Market Testing",
      description: "Develop and validate optimal pricing strategy",
      icon: DollarSign,
      duration: "3-4 days",
      subsections: [
        {
          id: "pricing-development",
          title: "Comprehensive Pricing Strategy",
          questions: 8,
        },
        {
          id: "market-validation",
          title: "Market Pricing Validation",
          questions: 8,
        },
        {
          id: "revenue-optimization",
          title: "Revenue Model Optimization",
          questions: 8,
        },
      ],
    },
  ];

  // Load existing data
  useEffect(() => {
    const existingData = assessmentData["business_prototype_testing"] || {};
    if (Object.keys(existingData).length > 0) {
      setSectionData({ ...sectionData, ...existingData });
    }
  }, []);

  // Save data when it changes
  useEffect(() => {
    updateAssessmentData("business_prototype_testing", sectionData);
  }, [sectionData]);

  // Calculate completion percentage
  const calculateSectionCompletion = (sectionId) => {
    const section = sections.find((s) => s.id === sectionId);
    if (!section) return 0;

    let totalQuestions = section.subsections.reduce(
      (sum, sub) => sum + sub.questions,
      0
    );
    let answeredQuestions = 0;

    // Count answered questions based on section data
    const sectionKey = sectionId.replace(/-([a-z])/g, (g) =>
      g[1].toUpperCase()
    );
    const data = sectionData[sectionKey] || {};

    // Simple completion check - count non-empty values
    const countAnswered = (obj) => {
      let count = 0;
      Object.values(obj).forEach((value) => {
        if (typeof value === "string" && value.trim()) count++;
        else if (typeof value === "number" && value > 0) count++;
        else if (Array.isArray(value) && value.length > 0) count++;
        else if (typeof value === "object" && value !== null) {
          count += countAnswered(value);
        }
      });
      return count;
    };

    answeredQuestions = countAnswered(data);
    return Math.min((answeredQuestions / totalQuestions) * 100, 100);
  };

  const overallCompletion =
    sections.reduce(
      (sum, section) => sum + calculateSectionCompletion(section.id),
      0
    ) / sections.length;

  const updateSectionData = (path, value) => {
    setSectionData((prev) => {
      const newData = { ...prev };
      const keys = path.split(".");
      let current = newData;

      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {};
        current = current[keys[i]];
      }

      current[keys[keys.length - 1]] = value;
      return newData;
    });
  };

  const addArrayItem = (path, item) => {
    const currentArray =
      path.split(".").reduce((obj, key) => obj?.[key], sectionData) || [];
    updateSectionData(path, [...currentArray, item]);
  };

  const removeArrayItem = (path, index) => {
    const currentArray =
      path.split(".").reduce((obj, key) => obj?.[key], sectionData) || [];
    const newArray = currentArray.filter((_, i) => i !== index);
    updateSectionData(path, newArray);
  };

  const renderCustomerValuePropositionSection = () => (
    <div className="space-y-8">
      {/* Value Proposition Canvas Development */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Value Proposition Canvas Development
          </CardTitle>
          <CardDescription>
            Create a comprehensive value proposition using the proven canvas
            framework
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Customer Profile */}
            <div className="space-y-6">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <Users className="h-5 w-5" />
                Customer Profile
              </h4>

              <div>
                <Label className="flex items-center gap-2">
                  <Brain className="h-4 w-4" />
                  Customer Jobs (What customers are trying to get done)
                </Label>
                <div className="mt-2 space-y-2">
                  {(
                    sectionData.customerValueProposition.cvpDevelopment
                      .customerJobs || []
                  ).map((job, index) => (
                    <div key={index} className="flex gap-2">
                      <Input
                        placeholder="e.g., Save time on daily tasks"
                        value={job}
                        onChange={(e) => {
                          const newJobs = [
                            ...(sectionData.customerValueProposition
                              .cvpDevelopment.customerJobs || []),
                          ];
                          newJobs[index] = e.target.value;
                          updateSectionData(
                            "customerValueProposition.cvpDevelopment.customerJobs",
                            newJobs
                          );
                        }}
                        className="flex-1"
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          removeArrayItem(
                            "customerValueProposition.cvpDevelopment.customerJobs",
                            index
                          )
                        }
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                  <Button
                    variant="outline"
                    onClick={() =>
                      addArrayItem(
                        "customerValueProposition.cvpDevelopment.customerJobs",
                        ""
                      )
                    }
                    className="w-full"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Customer Job
                  </Button>
                </div>
              </div>

              <div>
                <Label className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Pain Points (What frustrates customers)
                </Label>
                <div className="mt-2 space-y-2">
                  {(
                    sectionData.customerValueProposition.cvpDevelopment
                      .painPoints || []
                  ).map((pain, index) => (
                    <div key={index} className="flex gap-2">
                      <Input
                        placeholder="e.g., Current solutions are too expensive"
                        value={pain}
                        onChange={(e) => {
                          const newPains = [
                            ...(sectionData.customerValueProposition
                              .cvpDevelopment.painPoints || []),
                          ];
                          newPains[index] = e.target.value;
                          updateSectionData(
                            "customerValueProposition.cvpDevelopment.painPoints",
                            newPains
                          );
                        }}
                        className="flex-1"
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          removeArrayItem(
                            "customerValueProposition.cvpDevelopment.painPoints",
                            index
                          )
                        }
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                  <Button
                    variant="outline"
                    onClick={() =>
                      addArrayItem(
                        "customerValueProposition.cvpDevelopment.painPoints",
                        ""
                      )
                    }
                    className="w-full"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Pain Point
                  </Button>
                </div>
              </div>

              <div>
                <Label className="flex items-center gap-2">
                  <Star className="h-4 w-4" />
                  Desired Gains (What customers want to achieve)
                </Label>
                <div className="mt-2 space-y-2">
                  {(
                    sectionData.customerValueProposition.cvpDevelopment.gains ||
                    []
                  ).map((gain, index) => (
                    <div key={index} className="flex gap-2">
                      <Input
                        placeholder="e.g., Increase productivity by 50%"
                        value={gain}
                        onChange={(e) => {
                          const newGains = [
                            ...(sectionData.customerValueProposition
                              .cvpDevelopment.gains || []),
                          ];
                          newGains[index] = e.target.value;
                          updateSectionData(
                            "customerValueProposition.cvpDevelopment.gains",
                            newGains
                          );
                        }}
                        className="flex-1"
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          removeArrayItem(
                            "customerValueProposition.cvpDevelopment.gains",
                            index
                          )
                        }
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                  <Button
                    variant="outline"
                    onClick={() =>
                      addArrayItem(
                        "customerValueProposition.cvpDevelopment.gains",
                        ""
                      )
                    }
                    className="w-full"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Desired Gain
                  </Button>
                </div>
              </div>
            </div>

            {/* Value Map */}
            <div className="space-y-6">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <Package className="h-5 w-5" />
                Value Map
              </h4>

              <div>
                <Label className="flex items-center gap-2">
                  <Package className="h-4 w-4" />
                  Products & Services
                </Label>
                <div className="mt-2 space-y-2">
                  {(
                    sectionData.customerValueProposition.cvpDevelopment
                      .products || []
                  ).map((product, index) => (
                    <div key={index} className="flex gap-2">
                      <Input
                        placeholder="e.g., AI-powered task automation tool"
                        value={product}
                        onChange={(e) => {
                          const newProducts = [
                            ...(sectionData.customerValueProposition
                              .cvpDevelopment.products || []),
                          ];
                          newProducts[index] = e.target.value;
                          updateSectionData(
                            "customerValueProposition.cvpDevelopment.products",
                            newProducts
                          );
                        }}
                        className="flex-1"
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          removeArrayItem(
                            "customerValueProposition.cvpDevelopment.products",
                            index
                          )
                        }
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                  <Button
                    variant="outline"
                    onClick={() =>
                      addArrayItem(
                        "customerValueProposition.cvpDevelopment.products",
                        ""
                      )
                    }
                    className="w-full"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Product/Service
                  </Button>
                </div>
              </div>

              <div>
                <Label className="flex items-center gap-2">
                  <Zap className="h-4 w-4" />
                  Pain Relievers (How you solve customer problems)
                </Label>
                <div className="mt-2 space-y-2">
                  {(
                    sectionData.customerValueProposition.cvpDevelopment
                      .painRelievers || []
                  ).map((reliever, index) => (
                    <div key={index} className="flex gap-2">
                      <Input
                        placeholder="e.g., 90% cost reduction compared to alternatives"
                        value={reliever}
                        onChange={(e) => {
                          const newRelievers = [
                            ...(sectionData.customerValueProposition
                              .cvpDevelopment.painRelievers || []),
                          ];
                          newRelievers[index] = e.target.value;
                          updateSectionData(
                            "customerValueProposition.cvpDevelopment.painRelievers",
                            newRelievers
                          );
                        }}
                        className="flex-1"
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          removeArrayItem(
                            "customerValueProposition.cvpDevelopment.painRelievers",
                            index
                          )
                        }
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                  <Button
                    variant="outline"
                    onClick={() =>
                      addArrayItem(
                        "customerValueProposition.cvpDevelopment.painRelievers",
                        ""
                      )
                    }
                    className="w-full"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Pain Reliever
                  </Button>
                </div>
              </div>

              <div>
                <Label className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  Gain Creators (How you create customer value)
                </Label>
                <div className="mt-2 space-y-2">
                  {(
                    sectionData.customerValueProposition.cvpDevelopment
                      .gainCreators || []
                  ).map((creator, index) => (
                    <div key={index} className="flex gap-2">
                      <Input
                        placeholder="e.g., Increase team productivity by 3x"
                        value={creator}
                        onChange={(e) => {
                          const newCreators = [
                            ...(sectionData.customerValueProposition
                              .cvpDevelopment.gainCreators || []),
                          ];
                          newCreators[index] = e.target.value;
                          updateSectionData(
                            "customerValueProposition.cvpDevelopment.gainCreators",
                            newCreators
                          );
                        }}
                        className="flex-1"
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          removeArrayItem(
                            "customerValueProposition.cvpDevelopment.gainCreators",
                            index
                          )
                        }
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                  <Button
                    variant="outline"
                    onClick={() =>
                      addArrayItem(
                        "customerValueProposition.cvpDevelopment.gainCreators",
                        ""
                      )
                    }
                    className="w-full"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Gain Creator
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Unique Selling Proposition */}
          <div className="mt-8 pt-8 border-t">
            <Label>Unique Selling Proposition (USP)</Label>
            <Textarea
              placeholder="Based on your value proposition canvas, craft a clear, compelling USP that differentiates you from competitors..."
              value={
                sectionData.customerValueProposition.cvpDevelopment
                  .uniqueSellingProposition
              }
              onChange={(e) =>
                updateSectionData(
                  "customerValueProposition.cvpDevelopment.uniqueSellingProposition",
                  e.target.value
                )
              }
              className="mt-2 min-h-[100px]"
            />
          </div>
        </CardContent>
      </Card>

      {/* Message Testing Framework */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Message Testing Framework
          </CardTitle>
          <CardDescription>
            Test and optimize your value proposition messaging with target
            audiences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label>Primary Value Message</Label>
            <Textarea
              placeholder="Your main value proposition message to test with customers..."
              value={
                sectionData.customerValueProposition.messageTestingFramework
                  .primaryMessage
              }
              onChange={(e) =>
                updateSectionData(
                  "customerValueProposition.messageTestingFramework.primaryMessage",
                  e.target.value
                )
              }
              className="mt-2 min-h-[80px]"
            />
          </div>

          <div>
            <Label>Alternative Messages for A/B Testing</Label>
            <div className="mt-2 space-y-2">
              {(
                sectionData.customerValueProposition.messageTestingFramework
                  .alternativeMessages || []
              ).map((message, index) => (
                <div key={index} className="flex gap-2">
                  <Textarea
                    placeholder="Alternative value proposition message..."
                    value={message}
                    onChange={(e) => {
                      const newMessages = [
                        ...(sectionData.customerValueProposition
                          .messageTestingFramework.alternativeMessages || []),
                      ];
                      newMessages[index] = e.target.value;
                      updateSectionData(
                        "customerValueProposition.messageTestingFramework.alternativeMessages",
                        newMessages
                      );
                    }}
                    className="flex-1 min-h-[60px]"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      removeArrayItem(
                        "customerValueProposition.messageTestingFramework.alternativeMessages",
                        index
                      )
                    }
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              <Button
                variant="outline"
                onClick={() =>
                  addArrayItem(
                    "customerValueProposition.messageTestingFramework.alternativeMessages",
                    ""
                  )
                }
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Alternative Message
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Testing Methods</Label>
              <div className="mt-2 space-y-2">
                {[
                  "Landing Page A/B Tests",
                  "Email Campaign Tests",
                  "Social Media Ad Tests",
                  "Survey Testing",
                  "Focus Groups",
                  "Customer Interviews",
                ].map((method) => (
                  <div key={method} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={method}
                      checked={(
                        sectionData.customerValueProposition
                          .messageTestingFramework.testingMethods || []
                      ).includes(method)}
                      onChange={(e) => {
                        const currentMethods =
                          sectionData.customerValueProposition
                            .messageTestingFramework.testingMethods || [];
                        if (e.target.checked) {
                          updateSectionData(
                            "customerValueProposition.messageTestingFramework.testingMethods",
                            [...currentMethods, method]
                          );
                        } else {
                          updateSectionData(
                            "customerValueProposition.messageTestingFramework.testingMethods",
                            currentMethods.filter((m) => m !== method)
                          );
                        }
                      }}
                      className="w-4 h-4"
                    />
                    <Label htmlFor={method} className="text-sm">
                      {method}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <Label>Target Audiences for Testing</Label>
              <div className="mt-2 space-y-2">
                {(
                  sectionData.customerValueProposition.messageTestingFramework
                    .targetAudiences || []
                ).map((audience, index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      placeholder="e.g., Small business owners, 25-45, tech-savvy"
                      value={audience}
                      onChange={(e) => {
                        const newAudiences = [
                          ...(sectionData.customerValueProposition
                            .messageTestingFramework.targetAudiences || []),
                        ];
                        newAudiences[index] = e.target.value;
                        updateSectionData(
                          "customerValueProposition.messageTestingFramework.targetAudiences",
                          newAudiences
                        );
                      }}
                      className="flex-1"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        removeArrayItem(
                          "customerValueProposition.messageTestingFramework.targetAudiences",
                          index
                        )
                      }
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                <Button
                  variant="outline"
                  onClick={() =>
                    addArrayItem(
                      "customerValueProposition.messageTestingFramework.targetAudiences",
                      ""
                    )
                  }
                  className="w-full"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Target Audience
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderProductDevelopmentReadinessSection = () => (
    <div className="space-y-8">
      {/* Product Readiness Checklist */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Product Readiness Checklist
          </CardTitle>
          <CardDescription>
            Ensure your product is ready for market with comprehensive quality
            standards
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="core-features" className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="core-features">Core Features</TabsTrigger>
              <TabsTrigger value="quality">Quality</TabsTrigger>
              <TabsTrigger value="ux">User Experience</TabsTrigger>
              <TabsTrigger value="technical">Technical</TabsTrigger>
              <TabsTrigger value="compliance">Compliance</TabsTrigger>
            </TabsList>

            {[
              {
                key: "coreFeatures",
                value: "core-features",
                title: "Core Features Checklist",
                items: [
                  "All promised features are implemented and functional",
                  "Features solve the core customer problems identified",
                  "Feature performance meets or exceeds expectations",
                  "Features are intuitive and easy to use",
                  "Integration between features works seamlessly",
                ],
              },
              {
                key: "qualityStandards",
                value: "quality",
                title: "Quality Standards Checklist",
                items: [
                  "Product meets industry quality standards",
                  "Comprehensive testing completed (unit, integration, user)",
                  "Bug tracking and resolution process in place",
                  "Performance benchmarks met under expected load",
                  "Security vulnerabilities addressed and tested",
                ],
              },
              {
                key: "userExperience",
                value: "ux",
                title: "User Experience Checklist",
                items: [
                  "User interface is intuitive and accessible",
                  "User journey is smooth and logical",
                  "Onboarding process is clear and helpful",
                  "Help documentation and support are available",
                  "User feedback mechanisms are implemented",
                ],
              },
              {
                key: "technicalRequirements",
                value: "technical",
                title: "Technical Requirements Checklist",
                items: [
                  "System architecture supports expected user load",
                  "Data backup and recovery systems in place",
                  "Monitoring and alerting systems configured",
                  "API documentation complete and tested",
                  "Deployment and rollback procedures documented",
                ],
              },
              {
                key: "complianceRequirements",
                value: "compliance",
                title: "Compliance Requirements Checklist",
                items: [
                  "Legal and regulatory requirements met",
                  "Privacy policy and terms of service complete",
                  "Data protection and GDPR compliance verified",
                  "Industry-specific certifications obtained",
                  "Intellectual property protections in place",
                ],
              },
            ].map((category) => (
              <TabsContent
                key={category.value}
                value={category.value}
                className="space-y-4"
              >
                <h4 className="font-semibold">{category.title}</h4>
                <div className="space-y-3">
                  {category.items.map((item, index) => (
                    <div
                      key={index}
                      className="flex items-start space-x-3 p-3 border rounded-lg"
                    >
                      <input
                        type="checkbox"
                        id={`${category.key}-${index}`}
                        checked={(
                          sectionData.productDevelopmentReadiness
                            .productReadinessChecklist[category.key] || []
                        ).includes(item)}
                        onChange={(e) => {
                          const currentItems =
                            sectionData.productDevelopmentReadiness
                              .productReadinessChecklist[category.key] || [];
                          if (e.target.checked) {
                            updateSectionData(
                              `productDevelopmentReadiness.productReadinessChecklist.${category.key}`,
                              [...currentItems, item]
                            );
                          } else {
                            updateSectionData(
                              `productDevelopmentReadiness.productReadinessChecklist.${category.key}`,
                              currentItems.filter((i) => i !== item)
                            );
                          }
                        }}
                        className="w-5 h-5 mt-0.5"
                      />
                      <Label
                        htmlFor={`${category.key}-${index}`}
                        className="text-sm flex-1"
                      >
                        {item}
                      </Label>
                    </div>
                  ))}
                </div>

                <div className="mt-4">
                  <Label className="text-sm font-medium">
                    Additional {category.title.replace(" Checklist", "")} Items
                  </Label>
                  <div className="mt-2 space-y-2">
                    {(
                      sectionData.productDevelopmentReadiness
                        .productReadinessChecklist[category.key] || []
                    )
                      .filter((item) => !category.items.includes(item))
                      .map((customItem, index) => (
                        <div key={index} className="flex gap-2">
                          <Input
                            value={customItem}
                            onChange={(e) => {
                              const currentItems =
                                sectionData.productDevelopmentReadiness
                                  .productReadinessChecklist[category.key] ||
                                [];
                              const standardItems = category.items;
                              const customItems = currentItems.filter(
                                (item) => !standardItems.includes(item)
                              );
                              customItems[index] = e.target.value;
                              updateSectionData(
                                `productDevelopmentReadiness.productReadinessChecklist.${category.key}`,
                                [
                                  ...standardItems.filter((item) =>
                                    currentItems.includes(item)
                                  ),
                                  ...customItems,
                                ]
                              );
                            }}
                            className="flex-1"
                          />
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              const currentItems =
                                sectionData.productDevelopmentReadiness
                                  .productReadinessChecklist[category.key] ||
                                [];
                              const standardItems = category.items;
                              const customItems = currentItems.filter(
                                (item) => !standardItems.includes(item)
                              );
                              customItems.splice(index, 1);
                              updateSectionData(
                                `productDevelopmentReadiness.productReadinessChecklist.${category.key}`,
                                [
                                  ...standardItems.filter((item) =>
                                    currentItems.includes(item)
                                  ),
                                  ...customItems,
                                ]
                              );
                            }}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    <Button
                      variant="outline"
                      onClick={() => {
                        const currentItems =
                          sectionData.productDevelopmentReadiness
                            .productReadinessChecklist[category.key] || [];
                        updateSectionData(
                          `productDevelopmentReadiness.productReadinessChecklist.${category.key}`,
                          [...currentItems, ""]
                        );
                      }}
                      className="w-full"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add Custom Item
                    </Button>
                  </div>
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );

  const renderConsumerSampleFeedbackSection = () => (
    <div className="space-y-8">
      {/* Customer Sample Selection Strategy */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Customer Sample Selection Strategy
          </CardTitle>
          <CardDescription>
            Build a representative customer testing group for meaningful
            feedback
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label>Target Sample Size</Label>
              <div className="mt-2">
                <Slider
                  value={[
                    sectionData.consumerSampleBaseFeedback
                      .customerSampleStrategy.sampleSize,
                  ]}
                  onValueChange={(value) =>
                    updateSectionData(
                      "consumerSampleBaseFeedback.customerSampleStrategy.sampleSize",
                      value[0]
                    )
                  }
                  min={20}
                  max={200}
                  step={10}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>20 participants</span>
                  <span>
                    {
                      sectionData.consumerSampleBaseFeedback
                        .customerSampleStrategy.sampleSize
                    }{" "}
                    participants
                  </span>
                  <span>200 participants</span>
                </div>
              </div>
            </div>

            <div>
              <Label>Recruitment Method</Label>
              <RadioGroup
                value={
                  sectionData.consumerSampleBaseFeedback.customerSampleStrategy
                    .recruitmentMethod
                }
                onValueChange={(value) =>
                  updateSectionData(
                    "consumerSampleBaseFeedback.customerSampleStrategy.recruitmentMethod",
                    value
                  )
                }
                className="mt-2"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem
                    value="existing-network"
                    id="existing-network"
                  />
                  <Label htmlFor="existing-network">
                    Existing Network & Customers
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="social-media" id="social-media" />
                  <Label htmlFor="social-media">Social Media Recruitment</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem
                    value="professional-service"
                    id="professional-service"
                  />
                  <Label htmlFor="professional-service">
                    Professional Research Service
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="partnerships" id="partnerships" />
                  <Label htmlFor="partnerships">
                    Partner Organization Referrals
                  </Label>
                </div>
              </RadioGroup>
            </div>
          </div>

          <div>
            <Label>Selection Criteria</Label>
            <Textarea
              placeholder="Define specific criteria for participant selection (demographics, behavior, experience level, etc.)..."
              value={
                sectionData.consumerSampleBaseFeedback.customerSampleStrategy
                  .selectionCriteria
              }
              onChange={(e) =>
                updateSectionData(
                  "consumerSampleBaseFeedback.customerSampleStrategy.selectionCriteria",
                  e.target.value
                )
              }
              className="mt-2 min-h-[100px]"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Incentive Structure</Label>
              <Input
                placeholder="e.g., $50 gift card, free product trial, discount"
                value={
                  sectionData.consumerSampleBaseFeedback.customerSampleStrategy
                    .incentiveStructure
                }
                onChange={(e) =>
                  updateSectionData(
                    "consumerSampleBaseFeedback.customerSampleStrategy.incentiveStructure",
                    e.target.value
                  )
                }
                className="mt-2"
              />
            </div>

            <div>
              <Label>Testing Environment</Label>
              <RadioGroup
                value={
                  sectionData.consumerSampleBaseFeedback.customerSampleStrategy
                    .testingEnvironment
                }
                onValueChange={(value) =>
                  updateSectionData(
                    "consumerSampleBaseFeedback.customerSampleStrategy.testingEnvironment",
                    value
                  )
                }
                className="mt-2"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="remote" id="remote" />
                  <Label htmlFor="remote">Remote Testing</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="in-person" id="in-person" />
                  <Label htmlFor="in-person">In-Person Testing</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="hybrid" id="hybrid" />
                  <Label htmlFor="hybrid">Hybrid Approach</Label>
                </div>
              </RadioGroup>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Think-Feel-Do Feedback Framework */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Think-Feel-Do Feedback Framework
          </CardTitle>
          <CardDescription>
            Comprehensive feedback collection using the proven Think-Feel-Do
            methodology
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {[
              {
                key: "thinkQuestions",
                title: "THINK Questions",
                subtitle: "Cognitive responses and understanding",
                icon: Brain,
                color: "border-blue-500",
                bgColor: "bg-blue-50 dark:bg-blue-950",
                examples: [
                  "What is your first impression of this product?",
                  "How well does this solve your problem?",
                  "What questions do you have about this product?",
                  "How does this compare to current solutions?",
                  "What would make this more valuable to you?",
                ],
              },
              {
                key: "feelQuestions",
                title: "FEEL Questions",
                subtitle: "Emotional responses and reactions",
                icon: Heart,
                color: "border-red-500",
                bgColor: "bg-red-50 dark:bg-red-950",
                examples: [
                  "How does this product make you feel?",
                  "What excites you most about this?",
                  "What concerns or worries do you have?",
                  "How confident would you feel using this?",
                  "What emotions does the brand evoke?",
                ],
              },
              {
                key: "doQuestions",
                title: "DO Questions",
                subtitle: "Behavioral intentions and actions",
                icon: Zap,
                color: "border-green-500",
                bgColor: "bg-green-50 dark:bg-green-950",
                examples: [
                  "Would you purchase this product?",
                  "When would you use this product?",
                  "Who would you recommend this to?",
                  "What would prevent you from buying?",
                  "What actions would you take next?",
                ],
              },
            ].map((category) => {
              const Icon = category.icon;
              return (
                <Card
                  key={category.key}
                  className={`p-4 ${category.color} ${category.bgColor}`}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <Icon className="h-5 w-5" />
                    <div>
                      <h4 className="font-semibold">{category.title}</h4>
                      <p className="text-xs text-muted-foreground">
                        {category.subtitle}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <Label className="text-xs">Example Questions:</Label>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      {category.examples.map((example, index) => (
                        <li key={index}>• {example}</li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <Label className="text-xs">Your Custom Questions:</Label>
                    <div className="mt-2 space-y-2">
                      {(
                        sectionData.consumerSampleBaseFeedback
                          .thinkFeelDoFramework[category.key] || []
                      ).map((question, index) => (
                        <div key={index} className="flex gap-2">
                          <Input
                            placeholder="Add your custom question..."
                            value={question}
                            onChange={(e) => {
                              const newQuestions = [
                                ...(sectionData.consumerSampleBaseFeedback
                                  .thinkFeelDoFramework[category.key] || []),
                              ];
                              newQuestions[index] = e.target.value;
                              updateSectionData(
                                `consumerSampleBaseFeedback.thinkFeelDoFramework.${category.key}`,
                                newQuestions
                              );
                            }}
                            className="flex-1 text-xs"
                          />
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              removeArrayItem(
                                `consumerSampleBaseFeedback.thinkFeelDoFramework.${category.key}`,
                                index
                              )
                            }
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      ))}
                      <Button
                        variant="outline"
                        onClick={() =>
                          addArrayItem(
                            `consumerSampleBaseFeedback.thinkFeelDoFramework.${category.key}`,
                            ""
                          )
                        }
                        className="w-full"
                        size="sm"
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        Add Question
                      </Button>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Feedback Collection Method</Label>
              <RadioGroup
                value={
                  sectionData.consumerSampleBaseFeedback.thinkFeelDoFramework
                    .feedbackCollection
                }
                onValueChange={(value) =>
                  updateSectionData(
                    "consumerSampleBaseFeedback.thinkFeelDoFramework.feedbackCollection",
                    value
                  )
                }
                className="mt-2"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem
                    value="structured-interviews"
                    id="structured-interviews"
                  />
                  <Label htmlFor="structured-interviews">
                    Structured Interviews
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="online-surveys" id="online-surveys" />
                  <Label htmlFor="online-surveys">Online Surveys</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="focus-groups" id="focus-groups" />
                  <Label htmlFor="focus-groups">Focus Groups</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="user-testing" id="user-testing" />
                  <Label htmlFor="user-testing">User Testing Sessions</Label>
                </div>
              </RadioGroup>
            </div>

            <div>
              <Label>Analysis Method</Label>
              <Textarea
                placeholder="Describe how you'll analyze and synthesize the Think-Feel-Do feedback..."
                value={
                  sectionData.consumerSampleBaseFeedback.thinkFeelDoFramework
                    .analysisMethod
                }
                onChange={(e) =>
                  updateSectionData(
                    "consumerSampleBaseFeedback.thinkFeelDoFramework.analysisMethod",
                    e.target.value
                  )
                }
                className="mt-2 min-h-[100px]"
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderMarketingSalesOptimizationSection = () => (
    <div className="space-y-8">
      {/* Customer Purchase Funnel Framework */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Customer Purchase Funnel Framework
          </CardTitle>
          <CardDescription>
            Optimize each stage of the customer journey from awareness to
            retention
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {[
              {
                key: "awareness",
                title: "Awareness Stage",
                description: "How customers discover your solution",
                icon: Eye,
                color: "border-blue-500",
              },
              {
                key: "interest",
                title: "Interest Stage",
                description: "How customers engage with your content",
                icon: Heart,
                color: "border-green-500",
              },
              {
                key: "consideration",
                title: "Consideration Stage",
                description: "How customers evaluate your solution",
                icon: Brain,
                color: "border-yellow-500",
              },
              {
                key: "purchase",
                title: "Purchase Stage",
                description: "How customers make buying decisions",
                icon: ShoppingCart,
                color: "border-orange-500",
              },
              {
                key: "retention",
                title: "Retention Stage",
                description: "How customers become loyal advocates",
                icon: ThumbsUp,
                color: "border-purple-500",
              },
            ].map((stage) => {
              const Icon = stage.icon;
              return (
                <Card key={stage.key} className={`p-4 ${stage.color}`}>
                  <div className="flex items-center gap-2 mb-4">
                    <Icon className="h-5 w-5" />
                    <div>
                      <h4 className="font-semibold">{stage.title}</h4>
                      <p className="text-sm text-muted-foreground">
                        {stage.description}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label className="text-sm">Tactics & Strategies</Label>
                      <div className="mt-2 space-y-2">
                        {(
                          sectionData.marketingSalesOptimization
                            .customerPurchaseFunnel[stage.key]?.tactics || []
                        ).map((tactic, index) => (
                          <div key={index} className="flex gap-2">
                            <Input
                              placeholder="e.g., Content marketing, SEO, paid ads"
                              value={tactic}
                              onChange={(e) => {
                                const newTactics = [
                                  ...(sectionData.marketingSalesOptimization
                                    .customerPurchaseFunnel[stage.key]
                                    ?.tactics || []),
                                ];
                                newTactics[index] = e.target.value;
                                updateSectionData(
                                  `marketingSalesOptimization.customerPurchaseFunnel.${stage.key}.tactics`,
                                  newTactics
                                );
                              }}
                              className="flex-1 text-sm"
                            />
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() =>
                                removeArrayItem(
                                  `marketingSalesOptimization.customerPurchaseFunnel.${stage.key}.tactics`,
                                  index
                                )
                              }
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        ))}
                        <Button
                          variant="outline"
                          onClick={() =>
                            addArrayItem(
                              `marketingSalesOptimization.customerPurchaseFunnel.${stage.key}.tactics`,
                              ""
                            )
                          }
                          className="w-full"
                          size="sm"
                        >
                          <Plus className="h-3 w-3 mr-1" />
                          Add Tactic
                        </Button>
                      </div>
                    </div>

                    <div>
                      <Label className="text-sm">Key Metrics</Label>
                      <div className="mt-2 space-y-2">
                        {(
                          sectionData.marketingSalesOptimization
                            .customerPurchaseFunnel[stage.key]?.metrics || []
                        ).map((metric, index) => (
                          <div key={index} className="flex gap-2">
                            <Input
                              placeholder="e.g., CTR, conversion rate, CAC"
                              value={metric}
                              onChange={(e) => {
                                const newMetrics = [
                                  ...(sectionData.marketingSalesOptimization
                                    .customerPurchaseFunnel[stage.key]
                                    ?.metrics || []),
                                ];
                                newMetrics[index] = e.target.value;
                                updateSectionData(
                                  `marketingSalesOptimization.customerPurchaseFunnel.${stage.key}.metrics`,
                                  newMetrics
                                );
                              }}
                              className="flex-1 text-sm"
                            />
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() =>
                                removeArrayItem(
                                  `marketingSalesOptimization.customerPurchaseFunnel.${stage.key}.metrics`,
                                  index
                                )
                              }
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        ))}
                        <Button
                          variant="outline"
                          onClick={() =>
                            addArrayItem(
                              `marketingSalesOptimization.customerPurchaseFunnel.${stage.key}.metrics`,
                              ""
                            )
                          }
                          className="w-full"
                          size="sm"
                        >
                          <Plus className="h-3 w-3 mr-1" />
                          Add Metric
                        </Button>
                      </div>
                    </div>

                    <div>
                      <Label className="text-sm">Optimization Strategy</Label>
                      <Textarea
                        placeholder="How will you optimize this stage?"
                        value={
                          sectionData.marketingSalesOptimization
                            .customerPurchaseFunnel[stage.key]?.optimization ||
                          ""
                        }
                        onChange={(e) =>
                          updateSectionData(
                            `marketingSalesOptimization.customerPurchaseFunnel.${stage.key}.optimization`,
                            e.target.value
                          )
                        }
                        className="mt-2 min-h-[80px] text-sm"
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

  const renderPricingStrategyTestingSection = () => (
    <div className="space-y-8">
      {/* Comprehensive Pricing Strategy */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Comprehensive Pricing Strategy Development
          </CardTitle>
          <CardDescription>
            Develop and validate your optimal pricing strategy through
            systematic analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label>Primary Pricing Model</Label>
            <RadioGroup
              value={
                sectionData.pricingStrategyTesting.pricingStrategyDevelopment
                  .pricingModel
              }
              onValueChange={(value) =>
                updateSectionData(
                  "pricingStrategyTesting.pricingStrategyDevelopment.pricingModel",
                  value
                )
              }
              className="mt-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="subscription" id="subscription" />
                <Label htmlFor="subscription">
                  Subscription/Recurring Revenue
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="one-time" id="one-time" />
                <Label htmlFor="one-time">One-Time Purchase</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="freemium" id="freemium" />
                <Label htmlFor="freemium">Freemium Model</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="usage-based" id="usage-based" />
                <Label htmlFor="usage-based">Usage-Based Pricing</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="tiered" id="tiered" />
                <Label htmlFor="tiered">Tiered Pricing</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="value-based" id="value-based" />
                <Label htmlFor="value-based">Value-Based Pricing</Label>
              </div>
            </RadioGroup>
          </div>

          <div>
            <Label>Price Points to Test</Label>
            <div className="mt-2 space-y-3">
              {(
                sectionData.pricingStrategyTesting.pricingStrategyDevelopment
                  .pricePoints || []
              ).map((pricePoint, index) => (
                <Card key={index} className="p-4">
                  <div className="flex justify-between items-start mb-3">
                    <h5 className="font-medium">Price Point #{index + 1}</h5>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        removeArrayItem(
                          "pricingStrategyTesting.pricingStrategyDevelopment.pricePoints",
                          index
                        )
                      }
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label className="text-sm">Price</Label>
                      <Input
                        placeholder="$99/month"
                        value={pricePoint.price || ""}
                        onChange={(e) => {
                          const newPricePoints = [
                            ...(sectionData.pricingStrategyTesting
                              .pricingStrategyDevelopment.pricePoints || []),
                          ];
                          newPricePoints[index] = {
                            ...pricePoint,
                            price: e.target.value,
                          };
                          updateSectionData(
                            "pricingStrategyTesting.pricingStrategyDevelopment.pricePoints",
                            newPricePoints
                          );
                        }}
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label className="text-sm">Tier Name</Label>
                      <Input
                        placeholder="Professional, Enterprise, etc."
                        value={pricePoint.tier || ""}
                        onChange={(e) => {
                          const newPricePoints = [
                            ...(sectionData.pricingStrategyTesting
                              .pricingStrategyDevelopment.pricePoints || []),
                          ];
                          newPricePoints[index] = {
                            ...pricePoint,
                            tier: e.target.value,
                          };
                          updateSectionData(
                            "pricingStrategyTesting.pricingStrategyDevelopment.pricePoints",
                            newPricePoints
                          );
                        }}
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label className="text-sm">Target Segment</Label>
                      <Input
                        placeholder="Small businesses, enterprises, etc."
                        value={pricePoint.segment || ""}
                        onChange={(e) => {
                          const newPricePoints = [
                            ...(sectionData.pricingStrategyTesting
                              .pricingStrategyDevelopment.pricePoints || []),
                          ];
                          newPricePoints[index] = {
                            ...pricePoint,
                            segment: e.target.value,
                          };
                          updateSectionData(
                            "pricingStrategyTesting.pricingStrategyDevelopment.pricePoints",
                            newPricePoints
                          );
                        }}
                        className="mt-1"
                      />
                    </div>
                  </div>

                  <div className="mt-3">
                    <Label className="text-sm">Features Included</Label>
                    <Textarea
                      placeholder="List key features and benefits included at this price point..."
                      value={pricePoint.features || ""}
                      onChange={(e) => {
                        const newPricePoints = [
                          ...(sectionData.pricingStrategyTesting
                            .pricingStrategyDevelopment.pricePoints || []),
                        ];
                        newPricePoints[index] = {
                          ...pricePoint,
                          features: e.target.value,
                        };
                        updateSectionData(
                          "pricingStrategyTesting.pricingStrategyDevelopment.pricePoints",
                          newPricePoints
                        );
                      }}
                      className="mt-1 min-h-[60px]"
                    />
                  </div>
                </Card>
              ))}

              <Button
                variant="outline"
                onClick={() =>
                  addArrayItem(
                    "pricingStrategyTesting.pricingStrategyDevelopment.pricePoints",
                    { price: "", tier: "", segment: "", features: "" }
                  )
                }
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Price Point
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Value Justification</Label>
              <Textarea
                placeholder="How do you justify your pricing based on value delivered to customers?"
                value={
                  sectionData.pricingStrategyTesting.pricingStrategyDevelopment
                    .valueJustification
                }
                onChange={(e) =>
                  updateSectionData(
                    "pricingStrategyTesting.pricingStrategyDevelopment.valueJustification",
                    e.target.value
                  )
                }
                className="mt-2 min-h-[100px]"
              />
            </div>

            <div>
              <Label>Competitive Pricing Analysis</Label>
              <Textarea
                placeholder="How does your pricing compare to competitors? What's your competitive advantage?"
                value={
                  sectionData.pricingStrategyTesting.pricingStrategyDevelopment
                    .competitivePricing
                }
                onChange={(e) =>
                  updateSectionData(
                    "pricingStrategyTesting.pricingStrategyDevelopment.competitivePricing",
                    e.target.value
                  )
                }
                className="mt-2 min-h-[100px]"
              />
            </div>
          </div>

          <div>
            <Label>Pricing Psychology & Anchoring</Label>
            <Textarea
              placeholder="What psychological pricing principles will you use? How will you anchor prices and create perceived value?"
              value={
                sectionData.pricingStrategyTesting.pricingStrategyDevelopment
                  .pricingPsychology
              }
              onChange={(e) =>
                updateSectionData(
                  "pricingStrategyTesting.pricingStrategyDevelopment.pricingPsychology",
                  e.target.value
                )
              }
              className="mt-2 min-h-[80px]"
            />
          </div>
        </CardContent>
      </Card>

      {/* Revenue Model Optimization */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Revenue Model Optimization
          </CardTitle>
          <CardDescription>
            Optimize your revenue model for sustainable growth and profitability
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label>Revenue Streams</Label>
            <div className="mt-2 space-y-2">
              {(
                sectionData.pricingStrategyTesting.revenueModelOptimization
                  .revenueStreams || []
              ).map((stream, index) => (
                <Card key={index} className="p-3">
                  <div className="flex justify-between items-start mb-2">
                    <h5 className="font-medium text-sm">
                      Revenue Stream #{index + 1}
                    </h5>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        removeArrayItem(
                          "pricingStrategyTesting.revenueModelOptimization.revenueStreams",
                          index
                        )
                      }
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <Label className="text-xs">Stream Name</Label>
                      <Input
                        placeholder="e.g., Subscription fees, Transaction fees"
                        value={stream.name || ""}
                        onChange={(e) => {
                          const newStreams = [
                            ...(sectionData.pricingStrategyTesting
                              .revenueModelOptimization.revenueStreams || []),
                          ];
                          newStreams[index] = {
                            ...stream,
                            name: e.target.value,
                          };
                          updateSectionData(
                            "pricingStrategyTesting.revenueModelOptimization.revenueStreams",
                            newStreams
                          );
                        }}
                        className="mt-1 text-sm"
                      />
                    </div>
                    <div>
                      <Label className="text-xs">
                        Expected % of Total Revenue
                      </Label>
                      <Input
                        placeholder="e.g., 70%"
                        value={stream.percentage || ""}
                        onChange={(e) => {
                          const newStreams = [
                            ...(sectionData.pricingStrategyTesting
                              .revenueModelOptimization.revenueStreams || []),
                          ];
                          newStreams[index] = {
                            ...stream,
                            percentage: e.target.value,
                          };
                          updateSectionData(
                            "pricingStrategyTesting.revenueModelOptimization.revenueStreams",
                            newStreams
                          );
                        }}
                        className="mt-1 text-sm"
                      />
                    </div>
                  </div>

                  <div className="mt-2">
                    <Label className="text-xs">Description & Strategy</Label>
                    <Textarea
                      placeholder="Describe this revenue stream and how you'll optimize it..."
                      value={stream.description || ""}
                      onChange={(e) => {
                        const newStreams = [
                          ...(sectionData.pricingStrategyTesting
                            .revenueModelOptimization.revenueStreams || []),
                        ];
                        newStreams[index] = {
                          ...stream,
                          description: e.target.value,
                        };
                        updateSectionData(
                          "pricingStrategyTesting.revenueModelOptimization.revenueStreams",
                          newStreams
                        );
                      }}
                      className="mt-1 min-h-[50px] text-sm"
                    />
                  </div>
                </Card>
              ))}

              <Button
                variant="outline"
                onClick={() =>
                  addArrayItem(
                    "pricingStrategyTesting.revenueModelOptimization.revenueStreams",
                    { name: "", percentage: "", description: "" }
                  )
                }
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Revenue Stream
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Monetization Strategy</Label>
              <Textarea
                placeholder="How will you monetize your customer base and maximize lifetime value?"
                value={
                  sectionData.pricingStrategyTesting.revenueModelOptimization
                    .monetizationStrategy
                }
                onChange={(e) =>
                  updateSectionData(
                    "pricingStrategyTesting.revenueModelOptimization.monetizationStrategy",
                    e.target.value
                  )
                }
                className="mt-2 min-h-[100px]"
              />
            </div>

            <div>
              <Label>Scaling Strategy</Label>
              <Textarea
                placeholder="How will your revenue model scale as you grow? What are the key scaling factors?"
                value={
                  sectionData.pricingStrategyTesting.revenueModelOptimization
                    .scalingStrategy
                }
                onChange={(e) =>
                  updateSectionData(
                    "pricingStrategyTesting.revenueModelOptimization.scalingStrategy",
                    e.target.value
                  )
                }
                className="mt-2 min-h-[100px]"
              />
            </div>
          </div>

          <div>
            <Label>Financial Projections & Profitability Analysis</Label>
            <Textarea
              placeholder="Provide 12-24 month revenue projections, break-even analysis, and profitability timeline..."
              value={
                sectionData.pricingStrategyTesting.revenueModelOptimization
                  .financialProjections
              }
              onChange={(e) =>
                updateSectionData(
                  "pricingStrategyTesting.revenueModelOptimization.financialProjections",
                  e.target.value
                )
              }
              className="mt-2 min-h-[120px]"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderCurrentSection = () => {
    switch (currentSection) {
      case 0:
        return renderCustomerValuePropositionSection();
      case 1:
        return renderProductDevelopmentReadinessSection();
      case 2:
        return renderConsumerSampleFeedbackSection();
      case 3:
        return renderMarketingSalesOptimizationSection();
      case 4:
        return renderPricingStrategyTestingSection();
      default:
        return renderCustomerValuePropositionSection();
    }
  };

  return (
    <div className="space-y-6">
      {/* Section Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
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
              Business Prototype Testing Progress
            </h3>
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
              completePhase('business_prototype_testing')
              updatePhase(null)
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

export default BusinessPrototypeTesting;
