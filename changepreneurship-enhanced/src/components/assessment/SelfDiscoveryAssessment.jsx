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
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group.jsx";
import { Label } from "@/components/ui/label.jsx";
import { Textarea } from "@/components/ui/textarea.jsx";
import { Slider } from "@/components/ui/slider.jsx";
import DragDropRanking from "@/components/ui/drag-drop-ranking.jsx";
import {
  Heart,
  Target,
  Star,
  Compass,
  Brain,
  TrendingUp,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  AlertCircle,
  Lightbulb,
} from "lucide-react";
import {
  useAssessment,
  ENTREPRENEUR_ARCHETYPES,
} from "../../contexts/AssessmentContext";
import DataImportBanner from "../adaptive/DataImportBanner";
import DataDrivenAdaptiveEngine from "../../contexts/DataDrivenAdaptiveEngine";
import api from "../../services/api.js";

// Question definitions
const motivationQuestions = [
  {
    id: "primary-motivation",
    question: "What is the main reason you want to start your own business?",
    type: "multiple-choice",
    required: true,
    options: [
      {
        value: "transform-world",
        label: "Create something that changes the world",
        description: "Build transformative solutions for the future",
      },
      {
        value: "solve-problems",
        label: "Solve real problems I see everywhere",
        description: "Fix immediate problems with practical solutions",
      },
      {
        value: "lifestyle-freedom",
        label: "Have the lifestyle and freedom I want",
        description: "Personal freedom and lifestyle alignment",
      },
      {
        value: "financial-security",
        label: "Build financial security for my family",
        description: "Stable income and asset building",
      },
      {
        value: "social-impact",
        label: "Make a positive difference in the world",
        description: "Social or environmental impact",
      },
      {
        value: "seize-opportunities",
        label: "Capture market opportunities I see",
        description: "Seize opportunities for profit",
      },
    ],
  },
  {
    id: "success-vision",
    question:
      "When you imagine your business being successful, what does that look like?",
    type: "textarea",
    required: true,
    placeholder: "Describe your vision of success in detail...",
    helpText:
      "Think about team size, daily life, impact, working hours, and what success means to you personally.",
  },
  {
    id: "risk-tolerance",
    question: "How comfortable are you with taking risks?",
    type: "scale",
    required: true,
    scaleRange: { min: 1, max: 10 },
    scaleLabels: { min: "Very Risk-Averse", max: "High Risk Tolerance" },
    helpText:
      "Consider both financial and personal risks involved in starting a business.",
  },
];

const lifeImpactQuestions = [
  {
    id: "life-satisfaction",
    question: "Rate your current satisfaction in different life areas",
    type: "multiple-scale",
    required: true,
    areas: [
      "Health",
      "Money",
      "Family",
      "Friends",
      "Career",
      "Growth",
      "Recreation",
      "Environment",
    ],
    scaleRange: { min: 1, max: 10 },
  },
];

const valuesQuestions = [
  {
    id: "top-values",
    question: "Rank these values in order of importance to you",
    type: "ranking",
    required: true,
    options: [
      { value: "financial-success", label: "Financial Success" },
      { value: "personal-freedom", label: "Personal Freedom" },
      { value: "family-time", label: "Family Time" },
      { value: "making-difference", label: "Making a Difference" },
      { value: "recognition", label: "Recognition" },
      { value: "learning", label: "Learning" },
      { value: "security", label: "Security" },
      { value: "adventure", label: "Adventure" },
    ],
  },
];

const visionQuestions = [
  {
    id: "ten-year-vision",
    question: "Describe your ideal life 10 years from now",
    type: "textarea",
    required: true,
    placeholder: "Paint a detailed picture of your future self...",
    helpText:
      "Include your age, how you feel, your identity, contributions, achievements, and relationships.",
  },
];

const confidenceQuestions = [
  {
    id: "vision-confidence",
    question: "How confident are you that you can achieve your 10-year vision?",
    type: "scale",
    required: true,
    scaleRange: { min: 1, max: 10 },
    scaleLabels: { min: "Not Confident", max: "Very Confident" },
  },
];

const SelfDiscoveryAssessment = () => {
  const {
    assessmentData,
    updateResponse,
    updateProgress,
    completePhase,
    updatePhase,
    calculateArchetype,
  } = useAssessment();

  const [currentSection, setCurrentSection] = useState("motivation");
  const [sectionProgress, setSectionProgress] = useState({});
  const [showDataImport, setShowDataImport] = useState(true);
  const [isOptimized, setIsOptimized] = useState(false);
  const [connectedSources, setConnectedSources] = useState([]);

  const selfDiscoveryData = assessmentData["self_discovery"] || {};
  const responses = selfDiscoveryData.responses || {};

  // Assessment sections configuration
  const sections = [
    {
      id: "motivation",
      title: "Core Motivation & Why",
      navLabel: "Core Motivation",
      description: "Understand your fundamental drive for entrepreneurship",
      icon: Heart,
      duration: "10-15 minutes",
      questions: motivationQuestions,
    },
    {
      id: "life-impact",
      title: "Life Impact Assessment",
      navLabel: "Life Impact",
      description: "How entrepreneurship fits into your life priorities",
      icon: Target,
      duration: "15-20 minutes",
      questions: lifeImpactQuestions,
    },
    {
      id: "values",
      title: "Values & Priorities",
      navLabel: "Values & Priorities",
      description: "Identify core values to guide business decisions",
      icon: Star,
      duration: "10-15 minutes",
      questions: valuesQuestions,
    },
    {
      id: "vision",
      title: "Future Vision",
      navLabel: "Future Vision",
      description: "Define your long-term vision and goals",
      icon: Compass,
      duration: "15-20 minutes",
      questions: visionQuestions,
    },
    {
      id: "confidence",
      title: "Belief & Confidence",
      navLabel: "Belief & Confidence",
      description: "Assess your confidence in achieving your vision",
      icon: Brain,
      duration: "10-15 minutes",
      questions: confidenceQuestions,
    },
    {
      id: "results",
      title: "Your Entrepreneur Archetype",
      navLabel: "Archetype Results",
      description: "Discover your unique entrepreneur profile",
      icon: TrendingUp,
      duration: "5 minutes",
      questions: [],
    },
  ];

  const currentSectionIndex = sections.findIndex(
    (s) => s.id === currentSection
  );
  const currentSectionData = sections[currentSectionIndex];
  const CurrentIcon = currentSectionData?.icon;

  // Handle response updates (✅ argument order fix)
  const handleResponse = (questionId, answer) => {
    // updateResponse(phase, questionId, answer, section)
    updateResponse("self_discovery", questionId, answer, currentSection);

    // Update section progress
    const sectionQuestions = currentSectionData.questions;
    const sectionResponses = responses[currentSection] || {};
    const answeredQuestions = Object.keys({
      ...sectionResponses,
      [questionId]: answer,
    }).length;
    const progress = (answeredQuestions / sectionQuestions.length) * 100;

    setSectionProgress((prev) => ({
      ...prev,
      [currentSection]: progress,
    }));

    // Optional: Save progress to context to keep the global tracker accurate
    const totalSections = sections.filter((s) => s.id !== "results").length;
    const completedSections = Object.values({
      ...sectionProgress,
      [currentSection]: progress,
    }).filter((p) => p === 100).length;
    const overall = Math.round((completedSections / totalSections) * 100);
    updateProgress("self_discovery", overall);
  };

  // Handle data import optimization using imported data
  const handleOptimization = async (sources = {}) => {
    setShowDataImport(false);

    const importedData = {};
    const successful = [];

    for (const [source, file] of Object.entries(sources)) {
      try {
        let result;
        if (source === "linkedin" && file)
          result = await api.uploadLinkedInData(file);
        if (source === "resume" && file) result = await api.uploadResume(file);
        if (source === "financial")
          result = await api.connectFinancialAccounts();

        if (result?.success && result.data) {
          importedData[source] = result.data;
          successful.push(source);
        }
      } catch {
        // ignore individual source errors
      }
    }

    const engine = new DataDrivenAdaptiveEngine();
    sections.forEach((section) => {
      section.questions.forEach((q) => {
        const pre = engine.importEngine.prePopulateFromData(
          q.id,
          importedData
        );
        if (pre) {
          updateResponse("self_discovery", q.id, pre.value, section.id);
        }
      });
    });

    setConnectedSources(successful);
    setIsOptimized(true);
  };

  // Navigation
  const nextSection = () => {
    if (currentSectionIndex < sections.length - 1) {
      setCurrentSection(sections[currentSectionIndex + 1].id);
    }
  };

  const previousSection = () => {
    if (currentSectionIndex > 0) {
      setCurrentSection(sections[currentSectionIndex - 1].id);
    }
  };

  // Overall progress 
  const calculateOverallProgress = () => {
    const totalSections = sections.length - 1; // exclude results
    const completedSections = Object.values(sectionProgress).filter(
      (p) => p === 100
    ).length;
    return Math.round((completedSections / totalSections) * 100);
  };

  return (
    <div className="space-y-6">
      {/* Data Import Banner */}
      {showDataImport && (
        <DataImportBanner
          onDismiss={() => setShowDataImport(false)}
          onOptimize={handleOptimization}
        />
      )}

      {/* Optimization Status */}
      {isOptimized && (
        <Card className="border-green-500 bg-green-50 dark:bg-green-950/20">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <div className="font-medium text-green-800 dark:text-green-200">
                  Assessment Optimized
                </div>
                <div className="text-sm text-green-600 dark:text-green-400">
                  {connectedSources.length} data source
                  {connectedSources.length !== 1 ? "s" : ""} connected • Some
                  answers pre-populated
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Progress Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-primary" />
            Self Discovery Assessment
          </CardTitle>
          <CardDescription>
            Understand your entrepreneurial personality and motivations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Section Navigation */}
            <Tabs value={currentSection} onValueChange={setCurrentSection}>
              <TabsList className="grid grid-cols-6 w-full">
                {sections.map((section) => {
                  const IconComponent = section.icon;
                  const isCompleted = sectionProgress[section.id] === 100;
                  return (
                    <TabsTrigger
                      key={section.id}
                      value={section.id}
                      className="flex flex-col items-center gap-1 p-2"
                      title={section.title}
                    >
                      <IconComponent
                        className={`h-4 w-4 ${
                          isCompleted ? "text-green-500" : ""
                        }`}
                      />
                      <span
                        className="text-xs text-center leading-tight max-w-[6rem]"
                        style={{
                          display: "-webkit-box",
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: "vertical",
                          overflow: "hidden",
                        }}
                      >
                        {section.navLabel || section.title}
                      </span>
                      {isCompleted && (
                        <CheckCircle className="h-3 w-3 text-green-500" />
                      )}
                    </TabsTrigger>
                  );
                })}
              </TabsList>
            </Tabs>

            {/* Overall Progress */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Overall Progress</span>
                <Badge variant="outline">{calculateOverallProgress()}%</Badge>
              </div>
              <Progress
                value={calculateOverallProgress()}
                className="flex-1 mx-4"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Current Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {CurrentIcon && <CurrentIcon className="h-5 w-5" />}
            {currentSectionData?.title}
          </CardTitle>
          <CardDescription>{currentSectionData?.description}</CardDescription>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">{currentSectionData?.duration}</Badge>
            <span className="text-sm text-muted-foreground">
              Section {currentSectionIndex + 1} of {sections.length}
            </span>
          </div>
        </CardHeader>
        <CardContent>
          {currentSection === "results" ? (
            <ArchetypeResults
              archetype={selfDiscoveryData.archetype}
              insights={selfDiscoveryData.insights}
            />
          ) : (
            <SectionQuestions
              section={currentSectionData}
              responses={responses[currentSection] || {}}
              onResponse={handleResponse}
            />
          )}
        </CardContent>
      </Card>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={previousSection}
          disabled={currentSectionIndex === 0}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Previous
        </Button>
        {currentSectionIndex === sections.length - 1 ? (
          <Button
            onClick={() => {
              completePhase("self_discovery");
              updatePhase("idea_discovery");
            }}
          >
            Next Phase
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        ) : (
          <Button onClick={nextSection}>
            Next
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        )}
      </div>
    </div>
  );
};

// Section Questions Component
const SectionQuestions = ({ section, responses, onResponse }) => {
  if (!section.questions || section.questions.length === 0) {
    return (
      <div className="text-center text-muted-foreground">
        No questions available for this section.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {section.questions.map((question, index) => (
        <QuestionCard
          key={question.id}
          question={question}
          response={responses[question.id]}
          onResponse={(answer) => onResponse(question.id, answer)}
          questionNumber={index + 1}
          totalQuestions={section.questions.length}
        />
      ))}
    </div>
  );
};

// Individual Question Card Component
const QuestionCard = ({
  question,
  response,
  onResponse,
  questionNumber,
  totalQuestions,
}) => {
  const renderQuestionInput = () => {
    switch (question.type) {
      case "multiple-choice":
        return (
          <RadioGroup value={response || ""} onValueChange={onResponse}>
            {question.options.map((option) => (
              <div key={option.value} className="flex items-center space-x-2">
                <RadioGroupItem value={option.value} id={option.value} />
                <Label htmlFor={option.value} className="flex-1 cursor-pointer">
                  <div>
                    <div className="font-medium">{option.label}</div>
                    {option.description && (
                      <div className="text-sm text-muted-foreground">
                        {option.description}
                      </div>
                    )}
                  </div>
                </Label>
              </div>
            ))}
          </RadioGroup>
        );

      case "scale":
        return (
          <div className="space-y-4">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>{question.scaleLabels?.min || "Low"}</span>
              <span>{question.scaleLabels?.max || "High"}</span>
            </div>
            <Slider
              value={[response ?? question.scaleRange?.min ?? 1]}
              onValueChange={(value) => onResponse(value[0])}
              min={question.scaleRange?.min || 1}
              max={question.scaleRange?.max || 10}
              step={1}
              className="w-full"
            />
            <div className="text-center text-sm font-medium">
              Current value: {response ?? question.scaleRange?.min ?? 1}
            </div>
          </div>
        );

      case "textarea":
        return (
          <Textarea
            value={response || ""}
            onChange={(e) => onResponse(e.target.value)}
            placeholder={question.placeholder || "Enter your response..."}
            rows={4}
            className="w-full"
          />
        );

      case "multiple-scale":
        return (
          <MultipleScaleInput
            areas={question.areas}
            scaleRange={question.scaleRange}
            value={response || {}}
            onChange={onResponse}
          />
        );

      case "ranking":
        return (
          <DragDropRanking
            options={question.options}
            value={response || []}
            onChange={onResponse}
            maxRankings={question.maxRankings}
          />
        );

      default:
        return (
          <div className="text-muted-foreground">
            Unsupported question type: {question.type}
          </div>
        );
    }
  };

  return (
    <Card className="border-l-4 border-l-primary">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="secondary">
                Question {questionNumber} of {totalQuestions}
              </Badge>
              {question.required && (
                <Badge variant="destructive">Required</Badge>
              )}
            </div>
            <CardTitle className="text-lg">{question.question}</CardTitle>
            {question.description && (
              <CardDescription className="mt-2">
                {question.description}
              </CardDescription>
            )}
          </div>
          {response !== undefined && response !== "" && (
            <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
          )}
        </div>
      </CardHeader>
      <CardContent>
        {renderQuestionInput()}
        {question.helpText && (
          <div className="mt-4 p-3 bg-muted rounded-md">
            <div className="flex items-start gap-2">
              <Lightbulb className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
              <p className="text-sm text-muted-foreground">
                {question.helpText}
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Multiple Scale Input Component
const MultipleScaleInput = ({ areas, scaleRange, value, onChange }) => {
  const handleScaleChange = (area, scaleValue) => {
    const newValue = { ...value, [area]: scaleValue };
    onChange(newValue);
  };

  return (
    <div className="space-y-6">
      {areas.map((area) => (
        <div key={area} className="space-y-3">
          <div className="flex justify-between items-center">
            <Label className="font-medium">{area}</Label>
            <span className="text-sm text-muted-foreground">
              {value[area] ?? scaleRange.min}/{scaleRange.max}
            </span>
          </div>
          <Slider
            value={[value[area] ?? scaleRange.min]}
            onValueChange={(newValue) => handleScaleChange(area, newValue[0])}
            min={scaleRange.min}
            max={scaleRange.max}
            step={1}
            className="w-full"
          />
        </div>
      ))}
    </div>
  );
};

// Archetype Results Component
const ArchetypeResults = ({ archetype, insights }) => {
  if (!archetype || !insights) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-lg font-semibold mb-2">
          Complete Assessment to See Results
        </h3>
        <p className="text-muted-foreground">
          Finish all sections to discover your entrepreneur archetype and get
          personalized insights.
        </p>
      </div>
    );
  }

  const archetypeData = ENTREPRENEUR_ARCHETYPES[archetype];

  return (
    <div className="space-y-6">
      {/* Main Archetype Card */}
      <Card className="border-2 border-primary">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
            <TrendingUp className="h-8 w-8 text-primary" />
          </div>
          <CardTitle className="text-2xl">
            {archetypeData?.name || "Unknown Archetype"}
          </CardTitle>
          <CardDescription className="text-lg italic">
            "{archetypeData?.description || "No description available"}"
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-3">Key Traits</h4>
              <ul className="space-y-2">
                {(archetypeData?.traits || []).map((trait, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">{trait}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Business Focus</h4>
              <p className="text-sm text-muted-foreground mb-4">
                {archetypeData?.businessFocus || "No focus defined"}
              </p>
              <h4 className="font-semibold mb-3">Time Horizon</h4>
              <p className="text-sm text-muted-foreground">
                {archetypeData?.timeHorizon || "No time horizon defined"}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SelfDiscoveryAssessment;
