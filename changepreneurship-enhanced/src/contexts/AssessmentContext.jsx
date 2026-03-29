import React, { createContext, useContext, useReducer, useEffect, useState, useRef } from "react";
import { useAuth } from "./AuthContext.jsx";
import apiService from "../services/api";

// Initial state with all seven assessment phases
const initialState = {
  currentPhase: null,
  assessmentData: {
    "self_discovery": {
      completed: false,
      progress: 0,
      responses: {},
      archetype: null,
      insights: {},
    },
    "idea_discovery": {
      completed: false,
      progress: 0,
      responses: {},
      opportunities: [],
      selectedIdeas: [],
    },
    "market_research": {
      completed: false,
      progress: 0,
      responses: {},
      competitorAnalysis: {},
      marketValidation: {},
      targetMarket: {},
      marketSize: {},
    },
    "business_pillars": {
      completed: false,
      progress: 0,
      responses: {},
      customerSegment: {},
      businessPlan: {},
      valueProposition: {},
      revenueModel: {},
    },
    "product_concept_testing": {
      completed: false,
      progress: 0,
      responses: {},
      conceptTests: [],
      customerFeedback: {},
      productValidation: {},
      pricingStrategy: {},
    },
    "business_development": {
      completed: false,
      progress: 0,
      responses: {},
      strategicDecisions: {},
      resourceAllocation: {},
      partnerships: {},
      growthStrategy: {},
    },
    "business_prototype_testing": {
      completed: false,
      progress: 0,
      responses: {},
      prototypeResults: {},
      marketTesting: {},
      businessModelValidation: {},
      scalingPlan: {},
    },
  },
  userProfile: {
    firstName: "",
    lastName: "",
    email: "",
    age: null,
    location: "",
    currentRole: "",
    experience: 0,
    socialMediaConnected: false,
  },
};

// Action types
const ACTIONS = {
  UPDATE_PHASE: "UPDATE_PHASE",
  UPDATE_RESPONSE: "UPDATE_RESPONSE",
  UPDATE_PROGRESS: "UPDATE_PROGRESS",
  COMPLETE_PHASE: "COMPLETE_PHASE",
  UPDATE_PROFILE: "UPDATE_PROFILE",
  CALCULATE_ARCHETYPE: "CALCULATE_ARCHETYPE",
  SAVE_OPPORTUNITY: "SAVE_OPPORTUNITY",
  UPDATE_INSIGHTS: "UPDATE_INSIGHTS",
  RESET_ASSESSMENT: "RESET_ASSESSMENT",
  BULK_UPDATE_PHASE_DATA: "BULK_UPDATE_PHASE_DATA",
};

// Reducer
function assessmentReducer(state, action) {
  switch (action.type) {
    case ACTIONS.UPDATE_PHASE:
      return { ...state, currentPhase: action.payload };

    case ACTIONS.UPDATE_RESPONSE: {
      const { phase, questionId, answer, section } = action.payload;
      if (!state.assessmentData[phase]) {
        console.warn(
          `Phase '${phase}' does not exist. Creating default structure.`
        );
        return {
          ...state,
          assessmentData: {
            ...state.assessmentData,
            [phase]: {
              completed: false,
              progress: 0,
              responses: { [section || "general"]: { [questionId]: answer } },
            },
          },
        };
      }
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          [phase]: {
            ...state.assessmentData[phase],
            responses: {
              ...state.assessmentData[phase].responses,
              [section || "general"]: {
                ...state.assessmentData[phase].responses[section || "general"],
                [questionId]: answer,
              },
            },
          },
        },
      };
    }

    case ACTIONS.UPDATE_PROGRESS: {
      const { phase: progressPhase, progress } = action.payload;
      if (!state.assessmentData[progressPhase]) return state;
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          [progressPhase]: {
            ...state.assessmentData[progressPhase],
            progress,
          },
        },
      };
    }

    case ACTIONS.COMPLETE_PHASE: {
      const phaseToComplete = action.payload;
      if (!state.assessmentData[phaseToComplete]) return state;
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          [phaseToComplete]: {
            ...state.assessmentData[phaseToComplete],
            completed: true,
            progress: 100,
          },
        },
      };
    }

    case ACTIONS.UPDATE_PROFILE:
      return {
        ...state,
        userProfile: { ...state.userProfile, ...action.payload },
      };

    case ACTIONS.CALCULATE_ARCHETYPE:
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          "self_discovery": {
            ...state.assessmentData["self_discovery"],
            archetype: action.payload.archetype,
            insights: action.payload.insights,
          },
        },
      };

    case ACTIONS.SAVE_OPPORTUNITY:
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          "idea_discovery": {
            ...state.assessmentData["idea_discovery"],
            opportunities: [
              ...state.assessmentData["idea_discovery"].opportunities,
              action.payload,
            ],
          },
        },
      };

    case ACTIONS.UPDATE_INSIGHTS: {
      const { phase, insights } = action.payload;
      if (!state.assessmentData[phase]) return state;
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          [phase]: {
            ...state.assessmentData[phase],
            insights: {
              ...state.assessmentData[phase].insights,
              ...insights,
            },
          },
        },
      };
    }

    case ACTIONS.BULK_UPDATE_PHASE_DATA: {
      const { phase, data } = action.payload;
      const currentPhaseData = state.assessmentData[phase] || {
        completed: false,
        progress: 0,
        responses: {},
      };
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          [phase]: {
            ...currentPhaseData,
            ...data,
          },
        },
      };
    }

    case ACTIONS.RESET_ASSESSMENT:
      return initialState;

    default:
      return state;
  }
}

// Archetypes (condensed; same as previous file)
export const ENTREPRENEUR_ARCHETYPES = {
  "visionary-builder": {
    name: "Visionary Builder",
    description: "I want to create something that changes the world",
    traits: [
      "Innovation-focused",
      "Long-term thinking",
      "High risk tolerance",
      "Transformative solutions",
    ],
    businessFocus: "Innovation, disruption, major impact",
    timeHorizon: "10+ years",
    examples: ["Tech startups", "Revolutionary products", "Social movements"],
  },
  "practical-problem-solver": {
    name: "Practical Problem-Solver",
    description: "I see problems everywhere and know how to fix them",
    traits: [
      "Solution-oriented",
      "Practical approach",
      "Customer-focused",
      "Immediate impact",
    ],
    businessFocus: "Useful products/services, customer solutions",
    timeHorizon: "3-5 years",
    examples: [
      "Service businesses",
      "Consulting",
      "Improved traditional offerings",
    ],
  },
  "lifestyle-freedom-seeker": {
    name: "Lifestyle Freedom-Seeker",
    description: "I want a business that gives me the life I want",
    traits: [
      "Work-life balance",
      "Personal freedom",
      "Flexible approach",
      "Lifestyle alignment",
    ],
    businessFocus: "Sustainable income, work-life balance",
    timeHorizon: "Flexible",
    examples: ["Online businesses", "Freelancing", "Location-independent work"],
  },
  "security-focused-builder": {
    name: "Security-Focused Builder",
    description: "I want to build something stable for my family's future",
    traits: [
      "Risk-averse",
      "Family-focused",
      "Steady growth",
      "Financial security",
    ],
    businessFocus: "Stable income, asset building, predictable growth",
    timeHorizon: "Long-term (steady growth)",
    examples: [
      "Traditional businesses",
      "Franchises",
      "Established industries",
    ],
  },
  "purpose-driven-changemaker": {
    name: "Purpose-Driven Changemaker",
    description: "My business must make a positive difference in the world",
    traits: [
      "Mission-driven",
      "Social impact",
      "Community-focused",
      "Values-based",
    ],
    businessFocus: "Social value creation, community benefit",
    timeHorizon: "Long-term (mission-focused)",
    examples: ["Social enterprises", "B Corps", "Mission-driven companies"],
  },
  "opportunistic-entrepreneur": {
    name: "Opportunistic Entrepreneur",
    description: "I spot opportunities and move fast to capture them",
    traits: [
      "Market-responsive",
      "Quick decision-making",
      "Profit-focused",
      "Adaptable",
    ],
    businessFocus: "Market responsiveness, competitive advantage",
    timeHorizon: "Short to medium-term",
    examples: ["Trading", "Trend-based businesses", "Multiple ventures"],
  },
};

// Phase validation helper
const validatePhase = (phase) => {
  const validPhases = [
    "self_discovery",
    "idea_discovery",
    "market_research",
    "business_pillars",
    "product_concept_testing",
    "business_development",
    "business_prototype_testing",
  ];
  if (!validPhases.includes(phase)) {
    return false;
  }
  return true;
};

// Context
const AssessmentContext = createContext();

export function AssessmentProvider({ children }) {
  const [state, dispatch] = useReducer(assessmentReducer, initialState);
  const { user, isAuthenticated } = useAuth();

  // Phase completion summary panel
  const [phaseSummary, setPhaseSummary] = useState(null); // { phaseId, data } | null
  const phaseSummaryAfterRef = useRef(null); // callback to run when panel is dismissed

  // Load from localStorage on mount
  // REMOVED: localStorage loading - using backend as single source of truth
  // useEffect to load from localStorage has been removed

  // REMOVED: localStorage persistence - using backend as single source of truth  
  // useEffect to save to localStorage has been removed

  // Sync authenticated users with backend data - BACKEND IS SINGLE SOURCE OF TRUTH
  useEffect(() => {
    if (!isAuthenticated || !user?.id) return;
    
    let isCancelled = false;

    const groupResponsesBySection = (responses = []) => {
      return responses.reduce((sections, response) => {
        const sectionKey = response.section_id || "general";
        if (!sections[sectionKey]) sections[sectionKey] = {};
        sections[sectionKey][response.question_id] = response.response_value;
        return sections;
      }, {});
    };

    const assignPhaseData = (phasePayloads) => {
      Object.entries(phasePayloads).forEach(([phase, data]) => {
        dispatch({
          type: ACTIONS.BULK_UPDATE_PHASE_DATA,
          payload: { phase, data },
        });
      });
    };

    const buildPhasePayload = (phaseId, baseData) => ({
      ...initialState.assessmentData[phaseId],
      ...baseData,
    });

    const sarahPhaseMap = {
      "Self Discovery Assessment": "self_discovery",
      "Idea Discovery Assessment": "idea_discovery",
      "Market Research": "market_research",
      "Business Pillars Planning": "business_pillars",
      "Product Concept Testing": "product_concept_testing",
      "Business Development": "business_development",
      "Business Prototype Testing": "business_prototype_testing",
    };

    const hydrateFromCompleteExport = async () => {
      try {
        const response = await fetch(
          `${apiService.getApiBaseUrl()}/dashboard/complete-user/export/${user.id}`,
          { headers: apiService.getHeaders(), credentials: 'include' }
        );
        if (!response.ok) return false;
        const exportData = await response.json();
        if (!exportData?.assessments) return false;

        const payloads = {};
        exportData.assessments.forEach((assessment) => {
          const phaseId = sarahPhaseMap[assessment.phase_name];
          if (!phaseId) return;
          payloads[phaseId] = buildPhasePayload(phaseId, {
            completed: true,
            progress: Math.round(assessment.progress_percentage || 100),
            responses: groupResponsesBySection(assessment.responses),
            completedAt: new Date().toISOString(),
          });
        });

        assignPhaseData(payloads);
        return true;
      } catch (error) {
        console.error("Failed to hydrate from complete user export:", error);
        return false;
      }
    };

    const syncFromServer = async () => {
      try {
        const phasesResult = await apiService.getAssessmentPhases();
        
        if (!phasesResult.success || !phasesResult.data?.phases) {
          if (user.username === "sarah_chen_founder") {
            await hydrateFromCompleteExport();
          }
          return;
        }

        const phasePayloads = {};

        await Promise.all(
          phasesResult.data.phases.map(async (phase) => {
            if (!validatePhase(phase.id)) return;

            const baseData = {
              completed: Boolean(phase.is_completed),
              progress: Math.round(phase.progress_percentage || 0),
              assessmentId: phase.assessment_id,
              startedAt: phase.started_at,
              completedAt: phase.completed_at,
              responses: {},
            };

            if (phase.assessment_id) {
              const responsesResult = await apiService.getAssessmentResponses(
                phase.assessment_id
              );
              
              if (
                responsesResult.success &&
                Array.isArray(responsesResult.data?.responses)
              ) {
                baseData.responses = groupResponsesBySection(
                  responsesResult.data.responses
                );
              }
            }

            phasePayloads[phase.id] = {
              ...buildPhasePayload(phase.id, baseData),
            };
          })
        );

        if (isCancelled) return;

        assignPhaseData(phasePayloads);
      } catch (error) {
        console.error("Failed to sync assessment data from backend:", error);
        if (user?.username === "sarah_chen_founder") {
          await hydrateFromCompleteExport();
        }
      }
    };

    syncFromServer();
    
    return () => {
      isCancelled = true;
    };
  }, [isAuthenticated, user?.id]);

  // Action creators
  const updatePhase = (phase) => {
    if (phase === null) {
      dispatch({ type: ACTIONS.UPDATE_PHASE, payload: null });
    } else if (validatePhase(phase)) {
      dispatch({ type: ACTIONS.UPDATE_PHASE, payload: phase });
    }
  };
  const updateResponse = async (phase, questionId, answer, section = "general") => {
    if (!validatePhase(phase)) return;
    
    // Update local state immediately for responsive UI
    dispatch({
      type: ACTIONS.UPDATE_RESPONSE,
      payload: { phase, questionId, answer, section },
    });

    // Save to backend if authenticated
    if (isAuthenticated && user?.id) {
      try {
        let phaseData = state.assessmentData[phase];
        let assessmentId = phaseData?.assessmentId;
        
        // If no assessment exists for this phase, start it
        if (!assessmentId) {
          const startResult = await apiService.startAssessmentPhase(phase);
          
          if (startResult.success && startResult.data?.assessment) {
            assessmentId = startResult.data.assessment.id;
            
            // Update local state with assessment ID
            dispatch({
              type: ACTIONS.BULK_UPDATE_PHASE_DATA,
              payload: { 
                phase, 
                data: { 
                  ...phaseData,
                  assessmentId,
                  startedAt: new Date().toISOString()
                } 
              },
            });
          } else {
            return;
          }
        }
        
        if (assessmentId) {
          const responseData = {
            question_id: questionId,
            response_value: typeof answer === 'object' ? JSON.stringify(answer) : String(answer),
            section_id: section,
            response_type: typeof answer === 'object' ? 'multiple-scale' : (typeof answer === 'number' ? 'scale' : 'text'),
            question_text: `Question ${questionId}`, // TODO: Get actual question text
          };
          
          const result = await apiService.saveAssessmentResponse(assessmentId, responseData);
          
          if (result.success && result.data?.assessment) {
            dispatch({
              type: ACTIONS.BULK_UPDATE_PHASE_DATA,
              payload: {
                phase,
                data: {
                  ...state.assessmentData[phase],
                  assessmentId: result.data.assessment.id,
                  progress: Math.round(result.data.assessment.progress_percentage || 0),
                  completed: Boolean(result.data.assessment.is_completed),
                  startedAt: result.data.assessment.started_at,
                  completedAt: result.data.assessment.completed_at,
                },
              },
            });
          } else if (!result.success) {
            console.error(`[AssessmentContext] Failed to save response:`, result.error);
          }
        }
      } catch (error) {
        console.error(`[AssessmentContext] Error saving response:`, error);
      }
    }
  };

  const updateProgress = async (phase, progress) => {
    if (!validatePhase(phase)) return;
    if (!isAuthenticated || !user?.id) {
      dispatch({ type: ACTIONS.UPDATE_PROGRESS, payload: { phase, progress } });
    }
  };

  const completePhase = async (phase, afterClose = null) => {
    if (!validatePhase(phase)) return;

    if (!isAuthenticated || !user?.id) {
      dispatch({ type: ACTIONS.COMPLETE_PHASE, payload: phase });
      afterClose?.();
      return;
    }

    const assessmentId = state.assessmentData[phase]?.assessmentId;
    if (!assessmentId) return;

    // If the phase is already marked completed locally, skip the summary panel
    // and just call afterClose (e.g. user clicks Next after auto-complete fires)
    const alreadyCompleted = state.assessmentData[phase]?.completed;

    try {
      const result = await apiService.updateAssessmentProgress(assessmentId, 100, true);
      if (result.success && result.data?.assessment) {
        dispatch({
          type: ACTIONS.BULK_UPDATE_PHASE_DATA,
          payload: {
            phase,
            data: {
              ...state.assessmentData[phase],
              progress: Math.round(result.data.assessment.progress_percentage || 100),
              completed: Boolean(result.data.assessment.is_completed),
              completedAt: result.data.assessment.completed_at,
            },
          },
        });
      }

      if (alreadyCompleted) {
        // Phase was already done — just navigate, no panel
        afterClose?.();
        return;
      }

      // Show the AI phase summary panel (first completion)
      if (afterClose) phaseSummaryAfterRef.current = afterClose;
      setPhaseSummary({ phaseId: phase, data: null }); // null = loading

      try {
        const summaryRes = await apiService.getPhaseAISummary(phase);
        if (summaryRes.success && summaryRes.summary) {
          setPhaseSummary({ phaseId: phase, data: summaryRes.summary });
        }
      } catch (_summaryErr) {
        setPhaseSummary({
          phaseId: phase,
          data: {
            score: 65,
            headline: `${phase.replace(/_/g, ' ')} completed`,
            summary: 'Your responses have been saved. Continue to the next phase.',
            key_findings: [],
            next_focus: '',
          },
        });
      }
    } catch (error) {
      console.error(`[AssessmentContext] Error completing phase:`, error);
      afterClose?.();
    }
  };

  const dismissPhaseSummary = () => {
    const after = phaseSummaryAfterRef.current;
    phaseSummaryAfterRef.current = null;
    setPhaseSummary(null);
    after?.();
  };
  const updateProfile = (profileData) => {
    dispatch({ type: ACTIONS.UPDATE_PROFILE, payload: profileData });
  };
  const saveOpportunity = (opportunity) => {
    dispatch({ type: ACTIONS.SAVE_OPPORTUNITY, payload: opportunity });
  };
  const updateInsights = (phase, insights) => {
    if (validatePhase(phase))
      dispatch({ type: ACTIONS.UPDATE_INSIGHTS, payload: { phase, insights } });
  };
  const updatePhaseData = (phase, data) => {
    if (validatePhase(phase))
      dispatch({
        type: ACTIONS.BULK_UPDATE_PHASE_DATA,
        payload: { phase, data },
      });
  };

  // ✅ Alias for backward compatibility — prevents "updateAssessmentData is not a function" error
  const updateAssessmentData = (phase, data) => {
    updatePhaseData(phase, data);
  };

  // Archetype (condensed to match your file)
  const generateRecommendations = (archetype) => {
    return {
      businessTypes: ENTREPRENEUR_ARCHETYPES[archetype].examples,
      nextSteps: [
        "Complete the Idea Discovery assessment",
        "Research your target market",
        "Validate your business concept",
        "Develop your business plan",
      ],
      resources: [
        "Industry reports and market research",
        "Networking events and entrepreneur meetups",
        "Online courses and educational content",
        "Mentorship and advisory support",
      ],
    };
  };

  const calculateArchetype = (responses) => {
    const scores = {
      "visionary-builder": 0,
      "practical-problem-solver": 0,
      "lifestyle-freedom-seeker": 0,
      "security-focused-builder": 0,
      "purpose-driven-changemaker": 0,
      "opportunistic-entrepreneur": 0,
    };
    const motivation = responses.motivation?.primaryMotivation;
    const values = responses.values?.topValues || [];
    const vision = responses.vision?.timeHorizon;
    const riskTolerance = responses.motivation?.riskTolerance;
    if (motivation === "transform-world") scores["visionary-builder"] += 3;
    if (motivation === "solve-problems")
      scores["practical-problem-solver"] += 3;
    if (motivation === "lifestyle-freedom")
      scores["lifestyle-freedom-seeker"] += 3;
    if (motivation === "financial-security")
      scores["security-focused-builder"] += 3;
    if (motivation === "social-impact")
      scores["purpose-driven-changemaker"] += 3;
    if (motivation === "seize-opportunities")
      scores["opportunistic-entrepreneur"] += 3;
    if (values.includes("innovation")) scores["visionary-builder"] += 2;
    if (values.includes("helping-others"))
      scores["practical-problem-solver"] += 2;
    if (values.includes("freedom")) scores["lifestyle-freedom-seeker"] += 2;
    if (values.includes("security")) scores["security-focused-builder"] += 2;
    if (values.includes("social-impact"))
      scores["purpose-driven-changemaker"] += 2;
    if (values.includes("profit")) scores["opportunistic-entrepreneur"] += 2;
    if (vision === "long-term") {
      scores["visionary-builder"] += 1;
      scores["security-focused-builder"] += 1;
      scores["purpose-driven-changemaker"] += 1;
    }
    if (vision === "short-term") scores["opportunistic-entrepreneur"] += 2;
    if (riskTolerance === "high") {
      scores["visionary-builder"] += 2;
      scores["opportunistic-entrepreneur"] += 2;
    }
    if (riskTolerance === "low") {
      scores["security-focused-builder"] += 2;
      scores["lifestyle-freedom-seeker"] += 1;
    }
    const topArchetype = Object.entries(scores).reduce((a, b) =>
      scores[a[0]] > scores[b[0]] ? a : b
    )[0];
    const insights = {
      scores,
      topArchetype,
      strengths: ENTREPRENEUR_ARCHETYPES[topArchetype].traits,
      recommendations: generateRecommendations(topArchetype, responses),
    };
    dispatch({
      type: ACTIONS.CALCULATE_ARCHETYPE,
      payload: { archetype: topArchetype, insights },
    });
    return { archetype: topArchetype, insights };
  };

  const getPhaseData = (phase) =>
    validatePhase(phase) ? state.assessmentData[phase] || null : null;
  const getAllPhasesCompleted = () =>
    [
      "self_discovery",
      "idea_discovery",
      "market_research",
      "business_pillars",
      "product_concept_testing",
      "business_development",
      "business_prototype_testing",
    ].every((phase) => state.assessmentData[phase]?.completed === true);
  const getOverallProgress = () => {
    const phases = [
      "self_discovery",
      "idea_discovery",
      "market_research",
      "business_pillars",
      "product_concept_testing",
      "business_development",
      "business_prototype_testing",
    ];
    const total = phases.reduce(
      (sum, phase) => sum + (state.assessmentData[phase]?.progress || 0),
      0
    );
    return Math.round(total / phases.length);
  };

  const resetAssessment = () => {
    // Backend will handle data persistence - no localStorage cleanup needed
    return dispatch({ type: ACTIONS.RESET_ASSESSMENT });
  };

  const value = {
    ...state,
    updatePhase,
    updateResponse,
    updateProgress,
    completePhase,
    updateProfile,
    calculateArchetype,
    saveOpportunity,
    updateInsights,
    updatePhaseData,
    updateAssessmentData, // ✅ alias penting
    resetAssessment,
    getPhaseData,
    getAllPhasesCompleted,
    getOverallProgress,
    validatePhase,
    phaseSummary,
    dismissPhaseSummary,
  };

  return (
    <AssessmentContext.Provider value={value}>
      {children}
    </AssessmentContext.Provider>
  );
}

export function useAssessment() {
  const context = useContext(AssessmentContext);
  if (!context)
    throw new Error("useAssessment must be used within an AssessmentProvider");
  return context;
}

export default AssessmentContext;
