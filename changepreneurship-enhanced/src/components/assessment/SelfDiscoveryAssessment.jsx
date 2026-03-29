import React, { useState, useEffect } from "react";
import {
  Heart,
  Target,
  Star,
  Compass,
  Brain,
  TrendingUp,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import {
  useAssessment,
  ENTREPRENEUR_ARCHETYPES,
} from "../../contexts/AssessmentContext";
import DataImportBanner from "../adaptive/DataImportBanner";
import DataDrivenAdaptiveEngine from "../../contexts/DataDrivenAdaptiveEngine";
import AssessmentShell from "./AssessmentShell";
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

  // Initialize section progress from loaded responses so mini-bars reflect saved state
  useEffect(() => {
    const loaded = {};
    sections.forEach((section) => {
      if (section.id === 'results' || !section.questions?.length) return;
      const saved = (selfDiscoveryData.responses || {})[section.id] || {};
      const answered = Object.keys(saved).length;
      loaded[section.id] = Math.min(100, Math.round((answered / section.questions.length) * 100));
    });
    setSectionProgress(loaded);
  }, [selfDiscoveryData]); // eslint-disable-line react-hooks/exhaustive-deps

  // Handle response updates — signature expected by AssessmentShell: (sectionId, questionId, answer)
  const handleResponse = (sectionId, questionId, answer) => {
    updateResponse("self_discovery", questionId, answer, sectionId);

    const section = sections.find(s => s.id === sectionId);
    const sectionQuestions = section?.questions || [];
    const sectionResponses = responses[sectionId] || {};
    const answeredQuestions = Object.keys({
      ...sectionResponses,
      [questionId]: answer,
    }).length;
    const progress = (answeredQuestions / sectionQuestions.length) * 100;

    setSectionProgress((prev) => ({
      ...prev,
      [sectionId]: progress,
    }));

    const totalSections = sections.filter((s) => s.id !== "results").length;
    const completedSections = Object.values({
      ...sectionProgress,
      [sectionId]: progress,
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

  // Auto-calculate archetype when all core sections are completed and user views results
  useEffect(() => {
    const allCompleted = sections
      .filter((s) => s.id !== 'results')
      .every((s) => sectionProgress[s.id] === 100);

    if (
      allCompleted &&
      currentSection === 'results' &&
      !selfDiscoveryData.archetype
    ) {
      // Transform stored responses to the shape expected by calculateArchetype
      const formatted = {
        motivation: {
          primaryMotivation: responses.motivation?.['primary-motivation'],
          riskTolerance: responses.motivation?.['risk-tolerance'],
        },
        values: {
          topValues: (responses.values?.['top-values'] || []).map((v) => v.value || v),
        },
        vision: {
          // No direct time horizon question in current set; left null for now
          timeHorizon: null,
        },
      };
      try {
        calculateArchetype(formatted);
      } catch (e) {
        // Fail silently; archetype calculation is non-blocking for navigation
        console.warn('Archetype calculation failed:', e);
      }
    }
  }, [sectionProgress, currentSection, selfDiscoveryData.archetype, responses, calculateArchetype, sections]);

  return (
    <>
      {showDataImport && (
        <DataImportBanner
          onDismiss={() => setShowDataImport(false)}
          onOptimize={handleOptimization}
        />
      )}
      <AssessmentShell
        phaseName="Self Discovery"
        phaseNumber={1}
        sections={sections}
        currentSection={currentSection}
        onSectionChange={setCurrentSection}
        responses={responses}
        onResponse={handleResponse}
        sectionProgress={sectionProgress}
        onNext={() => {
          completePhase("self_discovery");
          updatePhase("idea_discovery");
        }}
        nextLabel="Next Phase: Idea Discovery"
      >
        {/* Results panel shown when on 'results' section */}
        <ArchetypeResults
          archetype={selfDiscoveryData.archetype}
          insights={selfDiscoveryData.insights}
        />
      </AssessmentShell>
    </>
  );
};

// ─── Archetype Results ────────────────────────────────────────────────────────
const ArchetypeResults = ({ archetype, insights }) => {
  if (!archetype || !insights) {
    return (
      <div className="text-center py-16">
        <AlertCircle className="h-12 w-12 text-gray-700 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">Complete All Sections First</h3>
        <p className="text-gray-500 text-sm">
          Finish all sections to discover your entrepreneur archetype.
        </p>
      </div>
    );
  }

  const archetypeData = ENTREPRENEUR_ARCHETYPES[archetype];

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-gray-900 to-black border border-cyan-500/30 rounded-2xl p-8 text-center">
        <div className="mx-auto w-16 h-16 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-full flex items-center justify-center mb-6 shadow-lg shadow-cyan-500/30">
          <TrendingUp className="h-8 w-8 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-2">
          {archetypeData?.name || "Unknown Archetype"}
        </h2>
        <p className="text-gray-400 italic">
          "{archetypeData?.description || "No description available"}"
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Key Traits</h4>
          <ul className="space-y-2">
            {(archetypeData?.traits || []).map((trait, index) => (
              <li key={index} className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-emerald-500 flex-shrink-0" />
                <span className="text-sm text-gray-300">{trait}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
          <div>
            <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">Business Focus</h4>
            <p className="text-sm text-gray-300">{archetypeData?.businessFocus || "—"}</p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">Time Horizon</h4>
            <p className="text-sm text-gray-300">{archetypeData?.timeHorizon || "—"}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SelfDiscoveryAssessment;
