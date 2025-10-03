import React, { createContext, useContext, useReducer, useEffect, useMemo } from 'react'
import AdaptiveAssessmentEngine, { 
  USER_PROFILE_TYPES, 
  ASSESSMENT_PATHS,
  PrePopulationEngine,
  SkipLogicEngine,
  UserProfileDetector,
  QuestionPriorityEngine
} from './AdaptiveAssessmentEngine'

// Enhanced initial state with adaptive features
const initialState = {
  // Core assessment data
  currentPhase: 'self_discovery',
  assessmentData: {
    'self_discovery': {
      completed: false,
      progress: 0,
      responses: {},
      archetype: null,
      insights: {},
      adaptiveProgress: 0,
      skippedQuestions: [],
      prePopulatedAnswers: {}
    },
    'idea_discovery': {
      completed: false,
      progress: 0,
      responses: {},
      opportunities: [],
      selectedIdeas: [],
      adaptiveProgress: 0,
      skippedQuestions: [],
      prePopulatedAnswers: {}
    },
    'market_research': {
      completed: false,
      progress: 0,
      responses: {},
      competitorAnalysis: {},
      marketValidation: {},
      adaptiveProgress: 0,
      skippedQuestions: [],
      prePopulatedAnswers: {}
    },
    'business_pillars': {
      completed: false,
      progress: 0,
      responses: {},
      customerSegment: {},
      businessPlan: {},
      adaptiveProgress: 0,
      skippedQuestions: [],
      prePopulatedAnswers: {}
    },
    'product_concept_testing': {
      completed: false,
      progress: 0,
      responses: {},
      testingResults: {},
      adaptiveProgress: 0,
      skippedQuestions: [],
      prePopulatedAnswers: {}
    },
    'business_development': {
      completed: false,
      progress: 0,
      responses: {},
      developmentPlan: {},
      adaptiveProgress: 0,
      skippedQuestions: [],
      prePopulatedAnswers: {}
    },
    'business_prototype_testing': {
      completed: false,
      progress: 0,
      responses: {},
      prototypeResults: {},
      adaptiveProgress: 0,
      skippedQuestions: [],
      prePopulatedAnswers: {}
    }
  },
  
  // Enhanced user profile with adaptive features
  userProfile: {
    firstName: '',
    lastName: '',
    email: '',
    age: null,
    location: '',
    currentRole: '',
    experience: 0,
    socialMediaConnected: false,
    
    // Adaptive profiling data
    profileType: null,
    assessmentPath: null,
    profileConfidence: 0,
    detectedAt: null,
    profileScores: {}
  },
  
  // Adaptive assessment state
  adaptiveState: {
    engine: null,
    currentPath: null,
    totalQuestionsOriginal: 500,
    totalQuestionsAdaptive: 500,
    estimatedTimeReduction: 0,
    personalizedRecommendations: [],
    nextRecommendedQuestion: null,
    assessmentSummary: null
  },
  
  // Question management
  questionState: {
    currentQuestions: [],
    processedQuestions: [],
    skippedQuestions: [],
    prePopulatedQuestions: [],
    priorityFiltered: false
  }
}

// Enhanced action types
const ACTIONS = {
  // Existing actions
  UPDATE_PHASE: 'UPDATE_PHASE',
  UPDATE_RESPONSE: 'UPDATE_RESPONSE',
  UPDATE_PROGRESS: 'UPDATE_PROGRESS',
  COMPLETE_PHASE: 'COMPLETE_PHASE',
  UPDATE_PROFILE: 'UPDATE_PROFILE',
  CALCULATE_ARCHETYPE: 'CALCULATE_ARCHETYPE',
  SAVE_OPPORTUNITY: 'SAVE_OPPORTUNITY',
  UPDATE_INSIGHTS: 'UPDATE_INSIGHTS',
  RESET_ASSESSMENT: 'RESET_ASSESSMENT',
  
  // New adaptive actions
  DETECT_USER_PROFILE: 'DETECT_USER_PROFILE',
  UPDATE_ADAPTIVE_PATH: 'UPDATE_ADAPTIVE_PATH',
  APPLY_PRE_POPULATION: 'APPLY_PRE_POPULATION',
  UPDATE_SKIP_LOGIC: 'UPDATE_SKIP_LOGIC',
  UPDATE_QUESTION_PRIORITY: 'UPDATE_QUESTION_PRIORITY',
  UPDATE_ADAPTIVE_PROGRESS: 'UPDATE_ADAPTIVE_PROGRESS',
  SET_NEXT_QUESTION: 'SET_NEXT_QUESTION',
  UPDATE_ASSESSMENT_SUMMARY: 'UPDATE_ASSESSMENT_SUMMARY',
  PROCESS_ADAPTIVE_QUESTIONS: 'PROCESS_ADAPTIVE_QUESTIONS'
}

// Enhanced reducer with adaptive logic
function enhancedAssessmentReducer(state, action) {
  switch (action.type) {
    case ACTIONS.UPDATE_PHASE:
      return {
        ...state,
        currentPhase: action.payload
      }

    case ACTIONS.UPDATE_RESPONSE:
      const { phase, questionId, answer, section } = action.payload
      const newState = {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          [phase]: {
            ...state.assessmentData[phase],
            responses: {
              ...state.assessmentData[phase].responses,
              [section || 'general']: {
                ...state.assessmentData[phase].responses[section || 'general'],
                [questionId]: answer
              }
            }
          }
        }
      }
      
      // Trigger adaptive processing after response update
      return newState

    case ACTIONS.UPDATE_PROGRESS:
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          [action.payload.phase]: {
            ...state.assessmentData[action.payload.phase],
            progress: action.payload.progress
          }
        }
      }

    case ACTIONS.UPDATE_ADAPTIVE_PROGRESS:
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          [action.payload.phase]: {
            ...state.assessmentData[action.payload.phase],
            adaptiveProgress: action.payload.adaptiveProgress,
            skippedQuestions: action.payload.skippedQuestions || [],
            prePopulatedAnswers: action.payload.prePopulatedAnswers || {}
          }
        }
      }

    case ACTIONS.COMPLETE_PHASE:
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          [action.payload]: {
            ...state.assessmentData[action.payload],
            completed: true,
            progress: 100,
            adaptiveProgress: 100
          }
        }
      }

    case ACTIONS.UPDATE_PROFILE:
      return {
        ...state,
        userProfile: {
          ...state.userProfile,
          ...action.payload
        }
      }

    case ACTIONS.DETECT_USER_PROFILE:
      return {
        ...state,
        userProfile: {
          ...state.userProfile,
          profileType: action.payload.profileType,
          profileConfidence: action.payload.confidence,
          detectedAt: new Date().toISOString(),
          profileScores: action.payload.scores
        },
        adaptiveState: {
          ...state.adaptiveState,
          currentPath: action.payload.path
        }
      }

    case ACTIONS.UPDATE_ADAPTIVE_PATH:
      return {
        ...state,
        adaptiveState: {
          ...state.adaptiveState,
          currentPath: action.payload.path,
          totalQuestionsAdaptive: action.payload.questionCount,
          estimatedTimeReduction: action.payload.timeReduction
        }
      }

    case ACTIONS.APPLY_PRE_POPULATION:
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          [action.payload.phase]: {
            ...state.assessmentData[action.payload.phase],
            prePopulatedAnswers: {
              ...state.assessmentData[action.payload.phase].prePopulatedAnswers,
              ...action.payload.prePopulatedAnswers
            }
          }
        }
      }

    case ACTIONS.UPDATE_SKIP_LOGIC:
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          [action.payload.phase]: {
            ...state.assessmentData[action.payload.phase],
            skippedQuestions: action.payload.skippedQuestions
          }
        }
      }

    case ACTIONS.PROCESS_ADAPTIVE_QUESTIONS:
      return {
        ...state,
        questionState: {
          ...state.questionState,
          currentQuestions: action.payload.originalQuestions,
          processedQuestions: action.payload.processedQuestions,
          skippedQuestions: action.payload.skippedQuestions,
          prePopulatedQuestions: action.payload.prePopulatedQuestions,
          priorityFiltered: action.payload.priorityFiltered
        }
      }

    case ACTIONS.SET_NEXT_QUESTION:
      return {
        ...state,
        adaptiveState: {
          ...state.adaptiveState,
          nextRecommendedQuestion: action.payload
        }
      }

    case ACTIONS.UPDATE_ASSESSMENT_SUMMARY:
      return {
        ...state,
        adaptiveState: {
          ...state.adaptiveState,
          assessmentSummary: action.payload,
          personalizedRecommendations: action.payload.recommendations
        }
      }

    case ACTIONS.CALCULATE_ARCHETYPE:
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          'self_discovery': {
            ...state.assessmentData['self_discovery'],
            archetype: action.payload.archetype,
            insights: action.payload.insights
          }
        }
      }

    case ACTIONS.SAVE_OPPORTUNITY:
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          'idea_discovery': {
            ...state.assessmentData['idea_discovery'],
            opportunities: [...state.assessmentData['idea_discovery'].opportunities, action.payload]
          }
        }
      }

    case ACTIONS.UPDATE_INSIGHTS:
      return {
        ...state,
        assessmentData: {
          ...state.assessmentData,
          [action.payload.phase]: {
            ...state.assessmentData[action.payload.phase],
            insights: {
              ...state.assessmentData[action.payload.phase].insights,
              ...action.payload.insights
            }
          }
        }
      }

    case ACTIONS.RESET_ASSESSMENT:
      return initialState

    default:
      return state
  }
}

// Enhanced Entrepreneur Archetypes with adaptive features
export const ENHANCED_ENTREPRENEUR_ARCHETYPES = {
  'visionary-builder': {
    name: 'Visionary Builder',
    description: 'I want to create something that changes the world',
    traits: ['Innovation-focused', 'Long-term thinking', 'High risk tolerance', 'Transformative solutions'],
    businessFocus: 'Innovation, disruption, major impact',
    timeHorizon: '10+ years',
    examples: ['Tech startups', 'Revolutionary products', 'Social movements'],
    adaptiveQuestions: ['scaling_strategies', 'innovation_methodology', 'disruptive_technology'],
    skipQuestions: ['basic_business_concepts', 'risk_aversion_questions']
  },
  'practical-problem-solver': {
    name: 'Practical Problem-Solver',
    description: 'I see problems everywhere and know how to fix them',
    traits: ['Solution-oriented', 'Practical approach', 'Customer-focused', 'Immediate impact'],
    businessFocus: 'Useful products/services, customer solutions',
    timeHorizon: '3-5 years',
    examples: ['Service businesses', 'Consulting', 'Improved traditional offerings'],
    adaptiveQuestions: ['customer_research', 'solution_validation', 'market_fit'],
    skipQuestions: ['long_term_vision', 'disruptive_innovation']
  },
  'lifestyle-freedom-seeker': {
    name: 'Lifestyle Freedom-Seeker',
    description: 'I want a business that gives me the life I want',
    traits: ['Work-life balance', 'Personal freedom', 'Flexible approach', 'Lifestyle alignment'],
    businessFocus: 'Sustainable income, work-life balance',
    timeHorizon: 'Flexible',
    examples: ['Online businesses', 'Freelancing', 'Location-independent work'],
    adaptiveQuestions: ['lifestyle_design', 'passive_income', 'location_independence'],
    skipQuestions: ['team_building', 'scaling_strategies', 'investor_relations']
  },
  'security-focused-builder': {
    name: 'Security-Focused Builder',
    description: 'I want to build something stable for my family\'s future',
    traits: ['Risk-averse', 'Family-focused', 'Steady growth', 'Financial security'],
    businessFocus: 'Stable income, asset building, predictable growth',
    timeHorizon: 'Long-term (steady growth)',
    examples: ['Traditional businesses', 'Franchises', 'Established industries'],
    adaptiveQuestions: ['financial_planning', 'risk_management', 'stable_revenue'],
    skipQuestions: ['high_risk_ventures', 'disruptive_innovation', 'rapid_scaling']
  },
  'purpose-driven-changemaker': {
    name: 'Purpose-Driven Changemaker',
    description: 'My business must make a positive difference in the world',
    traits: ['Mission-driven', 'Social impact', 'Community-focused', 'Values-based'],
    businessFocus: 'Social value creation, community benefit',
    timeHorizon: 'Long-term (mission-focused)',
    examples: ['Social enterprises', 'B Corps', 'Mission-driven companies'],
    adaptiveQuestions: ['social_impact', 'mission_alignment', 'stakeholder_value'],
    skipQuestions: ['profit_maximization', 'competitive_advantage']
  },
  'opportunistic-entrepreneur': {
    name: 'Opportunistic Entrepreneur',
    description: 'I spot opportunities and move fast to capture them',
    traits: ['Market-responsive', 'Quick decision-making', 'Profit-focused', 'Adaptable'],
    businessFocus: 'Market responsiveness, competitive advantage',
    timeHorizon: 'Short to medium-term',
    examples: ['Trading', 'Trend-based businesses', 'Multiple ventures'],
    adaptiveQuestions: ['market_timing', 'opportunity_recognition', 'rapid_execution'],
    skipQuestions: ['long_term_planning', 'mission_driven_questions']
  }
}

// Context
const EnhancedAssessmentContext = createContext()

// Provider component with adaptive features
export function EnhancedAssessmentProvider({ children }) {
  const [state, dispatch] = useReducer(enhancedAssessmentReducer, initialState)
  
  // Initialize adaptive assessment engine
  const adaptiveEngine = useMemo(() => new AdaptiveAssessmentEngine(), [])
  
  // Load from localStorage on mount
  useEffect(() => {
    const savedState = localStorage.getItem('changepreneurship-enhanced-assessment')
    if (savedState) {
      try {
        const parsedState = JSON.parse(savedState)
        // Merge with initial state to ensure all properties exist
        Object.keys(parsedState).forEach(key => {
          if (key === 'assessmentData') {
            Object.keys(parsedState.assessmentData).forEach(phase => {
              if (parsedState.assessmentData[phase].responses) {
                Object.keys(parsedState.assessmentData[phase].responses).forEach(section => {
                  Object.keys(parsedState.assessmentData[phase].responses[section]).forEach(questionId => {
                    dispatch({
                      type: ACTIONS.UPDATE_RESPONSE,
                      payload: {
                        phase,
                        section,
                        questionId,
                        answer: parsedState.assessmentData[phase].responses[section][questionId]
                      }
                    })
                  })
                })
              }
            })
          } else if (key === 'userProfile') {
            dispatch({
              type: ACTIONS.UPDATE_PROFILE,
              payload: parsedState[key]
            })
          } else if (key === 'currentPhase') {
            dispatch({
              type: ACTIONS.UPDATE_PHASE,
              payload: parsedState[key]
            })
          }
        })
      } catch (error) {
        console.error('Error loading saved enhanced assessment:', error)
      }
    }
  }, [])

  // Save to localStorage whenever state changes
  useEffect(() => {
    localStorage.setItem('changepreneurship-enhanced-assessment', JSON.stringify(state))
  }, [state])

  // Auto-detect user profile when responses change
  useEffect(() => {
    const allResponses = getAllResponses(state.assessmentData)
    if (Object.keys(allResponses).length >= 5) { // Minimum responses for profile detection
      const profileDetection = adaptiveEngine.profileDetector.detectProfile(allResponses)
      if (profileDetection.profileType !== state.userProfile.profileType) {
        dispatch({
          type: ACTIONS.DETECT_USER_PROFILE,
          payload: profileDetection
        })
      }
    }
  }, [state.assessmentData, adaptiveEngine.profileDetector, state.userProfile.profileType])

  // Helper function to get all responses across phases
  const getAllResponses = (assessmentData) => {
    const allResponses = {}
    Object.keys(assessmentData).forEach(phase => {
      if (assessmentData[phase].responses) {
        Object.keys(assessmentData[phase].responses).forEach(section => {
          Object.assign(allResponses, assessmentData[phase].responses[section])
        })
      }
    })
    return allResponses
  }

  // Enhanced action creators with adaptive features
  const updatePhase = (phase) => {
    dispatch({ type: ACTIONS.UPDATE_PHASE, payload: phase })
  }

  const updateResponse = (phase, questionId, answer, section = 'general') => {
    dispatch({
      type: ACTIONS.UPDATE_RESPONSE,
      payload: { phase, questionId, answer, section }
    })
    
    // Trigger adaptive processing
    setTimeout(() => {
      processAdaptiveLogic(phase)
    }, 100)
  }

  const processAdaptiveLogic = (phase) => {
    const allResponses = getAllResponses(state.assessmentData)
    const userProfile = state.userProfile
    
    // Apply skip logic
    const skippedQuestions = adaptiveEngine.skipLogicEngine.getSkippedQuestions(allResponses)
    
    // Apply pre-population
    const prePopulatedAnswers = {}
    Object.keys(allResponses).forEach(questionId => {
      const prePopulated = adaptiveEngine.prePopulationEngine.applyPrePopulation(allResponses, questionId)
      if (prePopulated) {
        prePopulatedAnswers[questionId] = prePopulated
      }
    })
    
    // Calculate adaptive progress
    const adaptiveProgress = adaptiveEngine.calculateAdaptiveProgress(
      allResponses, 
      state.adaptiveState.totalQuestionsOriginal, 
      userProfile
    )
    
    // Update adaptive state
    dispatch({
      type: ACTIONS.UPDATE_ADAPTIVE_PROGRESS,
      payload: {
        phase,
        adaptiveProgress,
        skippedQuestions,
        prePopulatedAnswers
      }
    })
    
    // Generate assessment summary
    const summary = adaptiveEngine.generateAssessmentSummary(allResponses, userProfile)
    dispatch({
      type: ACTIONS.UPDATE_ASSESSMENT_SUMMARY,
      payload: summary
    })
  }

  const processQuestionsWithAdaptiveLogic = (questions, phase) => {
    const allResponses = getAllResponses(state.assessmentData)
    const userProfile = state.userProfile
    
    const processedQuestions = adaptiveEngine.processQuestions(questions, allResponses, userProfile)
    const skippedQuestions = questions.filter(q => 
      adaptiveEngine.skipLogicEngine.shouldSkipQuestion(q.id, allResponses)
    )
    const prePopulatedQuestions = processedQuestions.filter(q => q.prePopulated)
    
    dispatch({
      type: ACTIONS.PROCESS_ADAPTIVE_QUESTIONS,
      payload: {
        originalQuestions: questions,
        processedQuestions,
        skippedQuestions: skippedQuestions.map(q => q.id),
        prePopulatedQuestions: prePopulatedQuestions.map(q => q.id),
        priorityFiltered: userProfile?.path?.questionCount < 300
      }
    })
    
    return processedQuestions
  }

  const getNextRecommendedQuestion = (questions, phase) => {
    const allResponses = getAllResponses(state.assessmentData)
    const userProfile = state.userProfile
    
    const nextQuestion = adaptiveEngine.getNextQuestion(questions, allResponses, userProfile)
    dispatch({
      type: ACTIONS.SET_NEXT_QUESTION,
      payload: nextQuestion
    })
    
    return nextQuestion
  }

  const updateProgress = (phase, progress) => {
    dispatch({
      type: ACTIONS.UPDATE_PROGRESS,
      payload: { phase, progress }
    })
  }

  const completePhase = (phase) => {
    dispatch({ type: ACTIONS.COMPLETE_PHASE, payload: phase })
  }

  const updateProfile = (profileData) => {
    dispatch({ type: ACTIONS.UPDATE_PROFILE, payload: profileData })
  }

  const calculateArchetype = (responses) => {
    // Enhanced archetype calculation with adaptive features
    const scores = {
      'visionary-builder': 0,
      'practical-problem-solver': 0,
      'lifestyle-freedom-seeker': 0,
      'security-focused-builder': 0,
      'purpose-driven-changemaker': 0,
      'opportunistic-entrepreneur': 0
    }

    // Use adaptive logic for more accurate archetype detection
    const allResponses = getAllResponses(state.assessmentData)
    const profileDetection = adaptiveEngine.profileDetector.detectProfile(allResponses)
    
    // Calculate scores based on responses with adaptive weighting
    const motivation = responses.motivation?.primaryMotivation
    const values = responses.values?.topValues || []
    const vision = responses.vision?.timeHorizon
    const riskTolerance = responses.motivation?.riskTolerance

    // Enhanced scoring logic
    if (motivation === 'transform-world') scores['visionary-builder'] += 3
    if (motivation === 'solve-problems') scores['practical-problem-solver'] += 3
    if (motivation === 'lifestyle-freedom') scores['lifestyle-freedom-seeker'] += 3
    if (motivation === 'financial-security') scores['security-focused-builder'] += 3
    if (motivation === 'social-impact') scores['purpose-driven-changemaker'] += 3
    if (motivation === 'seize-opportunities') scores['opportunistic-entrepreneur'] += 3

    // Apply adaptive profile detection results
    if (profileDetection.profileType) {
      const archetypeMapping = {
        [USER_PROFILE_TYPES.BEGINNER_ENTREPRENEUR]: 'practical-problem-solver',
        [USER_PROFILE_TYPES.EXPERIENCED_PROFESSIONAL]: 'practical-problem-solver',
        [USER_PROFILE_TYPES.SERIAL_ENTREPRENEUR]: 'opportunistic-entrepreneur',
        [USER_PROFILE_TYPES.INDUSTRY_SPECIALIST]: 'visionary-builder',
        [USER_PROFILE_TYPES.CREATIVE_INNOVATOR]: 'visionary-builder'
      }
      
      const suggestedArchetype = archetypeMapping[profileDetection.profileType]
      if (suggestedArchetype) {
        scores[suggestedArchetype] += 2
      }
    }

    // Find the highest scoring archetype
    const topArchetype = Object.entries(scores).reduce((a, b) => 
      scores[a[0]] > scores[b[0]] ? a : b
    )[0]

    const insights = {
      scores,
      topArchetype,
      strengths: ENHANCED_ENTREPRENEUR_ARCHETYPES[topArchetype].traits,
      recommendations: generateEnhancedRecommendations(topArchetype, responses, profileDetection),
      adaptiveProfile: profileDetection
    }

    dispatch({
      type: ACTIONS.CALCULATE_ARCHETYPE,
      payload: { archetype: topArchetype, insights }
    })

    return { archetype: topArchetype, insights }
  }

  const generateEnhancedRecommendations = (archetype, responses, profileDetection) => {
    const archetypeData = ENHANCED_ENTREPRENEUR_ARCHETYPES[archetype]
    const adaptiveRecommendations = adaptiveEngine.generatePersonalizedRecommendations(responses, profileDetection)
    
    return {
      businessTypes: archetypeData.examples,
      nextSteps: [
        'Complete the adaptive assessment path',
        'Focus on your personalized question priorities',
        'Leverage pre-populated insights',
        'Follow your customized roadmap'
      ],
      resources: [
        'Personalized industry reports',
        'Targeted networking opportunities',
        'Customized educational content',
        'Adaptive mentorship matching'
      ],
      adaptiveInsights: adaptiveRecommendations
    }
  }

  const saveOpportunity = (opportunity) => {
    dispatch({ type: ACTIONS.SAVE_OPPORTUNITY, payload: opportunity })
  }

  const updateInsights = (phase, insights) => {
    dispatch({
      type: ACTIONS.UPDATE_INSIGHTS,
      payload: { phase, insights }
    })
  }

  const resetAssessment = () => {
    dispatch({ type: ACTIONS.RESET_ASSESSMENT })
    localStorage.removeItem('changepreneurship-enhanced-assessment')
  }

  // Enhanced value with adaptive features
  const value = {
    ...state,
    
    // Original functions
    updatePhase,
    updateResponse,
    updateProgress,
    completePhase,
    updateProfile,
    calculateArchetype,
    saveOpportunity,
    updateInsights,
    resetAssessment,
    
    // New adaptive functions
    adaptiveEngine,
    processAdaptiveLogic,
    processQuestionsWithAdaptiveLogic,
    getNextRecommendedQuestion,
    getAllResponses: () => getAllResponses(state.assessmentData),
    
    // Adaptive state helpers
    getAdaptiveProgress: (phase) => state.assessmentData[phase]?.adaptiveProgress || 0,
    getSkippedQuestions: (phase) => state.assessmentData[phase]?.skippedQuestions || [],
    getPrePopulatedAnswers: (phase) => state.assessmentData[phase]?.prePopulatedAnswers || {},
    getCurrentPath: () => state.adaptiveState.currentPath,
    getPersonalizedRecommendations: () => state.adaptiveState.personalizedRecommendations,
    getAssessmentSummary: () => state.adaptiveState.assessmentSummary,
    
    // Profile helpers
    getUserProfileType: () => state.userProfile.profileType,
    getProfileConfidence: () => state.userProfile.profileConfidence,
    isProfileDetected: () => !!state.userProfile.profileType
  }

  return (
    <EnhancedAssessmentContext.Provider value={value}>
      {children}
    </EnhancedAssessmentContext.Provider>
  )
}

// Hook to use the enhanced assessment context
export function useEnhancedAssessment() {
  const context = useContext(EnhancedAssessmentContext)
  if (!context) {
    throw new Error('useEnhancedAssessment must be used within an EnhancedAssessmentProvider')
  }
  return context
}

export default EnhancedAssessmentContext

