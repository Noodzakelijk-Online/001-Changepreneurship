/**
 * Adaptive Assessment Engine for Changepreneurship Platform
 * Implements intelligent question consolidation, pre-population logic, and personalized assessment paths
 */

// User Profile Types for Adaptive Routing
export const USER_PROFILE_TYPES = {
  BEGINNER_ENTREPRENEUR: 'beginner_entrepreneur',
  EXPERIENCED_PROFESSIONAL: 'experienced_professional', 
  SERIAL_ENTREPRENEUR: 'serial_entrepreneur',
  INDUSTRY_SPECIALIST: 'industry_specialist',
  CREATIVE_INNOVATOR: 'creative_innovator'
}

// Assessment Path Configurations
export const ASSESSMENT_PATHS = {
  [USER_PROFILE_TYPES.BEGINNER_ENTREPRENEUR]: {
    name: 'Comprehensive Education Track',
    description: 'Complete assessment with detailed explanations and educational content',
    estimatedTime: '3-4 hours',
    questionCount: 500,
    skipQuestions: [
      'advanced_financial_modeling',
      'complex_market_analysis',
      'scaling_strategies',
      'investor_readiness'
    ],
    addQuestions: [
      'basic_business_concepts',
      'entrepreneurship_fundamentals',
      'risk_education',
      'business_terminology'
    ],
    explanationLevel: 'detailed',
    educationalContent: true
  },
  
  [USER_PROFILE_TYPES.EXPERIENCED_PROFESSIONAL]: {
    name: 'Accelerated Assessment Track',
    description: 'Focused assessment for professionals with leadership experience',
    estimatedTime: '45-60 minutes',
    questionCount: 200,
    skipQuestions: [
      'basic_leadership',
      'fundamental_business_concepts',
      'work_experience_basics',
      'professional_skills_intro'
    ],
    focusAreas: [
      'strategic_thinking',
      'market_opportunity',
      'execution_planning',
      'team_building'
    ],
    explanationLevel: 'concise',
    educationalContent: false
  },
  
  [USER_PROFILE_TYPES.SERIAL_ENTREPRENEUR]: {
    name: 'Expert Validation Track',
    description: 'Rapid assessment focusing on advanced strategies and scaling',
    estimatedTime: '20-30 minutes',
    questionCount: 100,
    skipQuestions: [
      'entrepreneurship_basics',
      'risk_tolerance_intro',
      'business_fundamentals',
      'basic_market_research'
    ],
    focusAreas: [
      'scaling_strategies',
      'advanced_market_dynamics',
      'investor_readiness',
      'portfolio_management'
    ],
    explanationLevel: 'minimal',
    educationalContent: false
  },
  
  [USER_PROFILE_TYPES.INDUSTRY_SPECIALIST]: {
    name: 'Industry-Focused Track',
    description: 'Specialized assessment leveraging deep industry knowledge',
    estimatedTime: '30-45 minutes',
    questionCount: 150,
    prePopulate: [
      'market_knowledge',
      'competitive_landscape',
      'industry_trends',
      'regulatory_environment'
    ],
    focusAreas: [
      'business_model_innovation',
      'market_disruption_potential',
      'industry_transformation'
    ],
    explanationLevel: 'technical',
    educationalContent: false
  },
  
  [USER_PROFILE_TYPES.CREATIVE_INNOVATOR]: {
    name: 'Innovation Track',
    description: 'Creative-focused assessment emphasizing product development',
    estimatedTime: '60-90 minutes',
    questionCount: 250,
    focusAreas: [
      'product_development',
      'design_thinking',
      'user_experience',
      'creative_process'
    ],
    addQuestions: [
      'creative_methodology',
      'innovation_process',
      'design_validation',
      'user_research'
    ],
    explanationLevel: 'visual',
    educationalContent: true
  }
}

// Pre-population Rules Engine
export class PrePopulationEngine {
  static rules = [
    {
      target: 'business_idea_clarity',
      sources: ['has_business_idea', 'idea_development_stage'],
      logic: (sources) => {
        if (sources.has_business_idea === 'yes' && 
            ['detailed', 'validated'].includes(sources.idea_development_stage)) {
          return 'high'
        }
        if (sources.has_business_idea === 'yes' && sources.idea_development_stage === 'basic') {
          return 'medium'
        }
        return 'low'
      },
      confidence: 0.8
    },
    
    {
      target: 'industry_experience_level',
      sources: ['work_history', 'education_background', 'years_in_industry'],
      logic: (sources) => {
        const years = parseInt(sources.years_in_industry) || 0
        if (years >= 10) return 'expert'
        if (years >= 5) return 'experienced'
        if (years >= 2) return 'intermediate'
        return 'beginner'
      },
      confidence: 0.9
    },
    
    {
      target: 'financial_runway_months',
      sources: ['current_savings', 'monthly_expenses', 'current_income'],
      logic: (sources) => {
        const savings = parseFloat(sources.current_savings) || 0
        const expenses = parseFloat(sources.monthly_expenses) || 0
        if (expenses === 0) return 'unknown'
        return Math.floor(savings / expenses)
      },
      confidence: 0.9
    },
    
    {
      target: 'team_building_readiness',
      sources: ['leadership_experience', 'management_background', 'team_size_managed'],
      logic: (sources) => {
        const teamSize = parseInt(sources.team_size_managed) || 0
        const hasLeadership = sources.leadership_experience === 'yes'
        const hasManagement = sources.management_background === 'yes'
        
        if (hasLeadership && hasManagement && teamSize >= 10) return 'expert'
        if (hasLeadership && teamSize >= 5) return 'experienced'
        if (hasLeadership || hasManagement) return 'intermediate'
        return 'beginner'
      },
      confidence: 0.7
    },
    
    {
      target: 'market_research_capability',
      sources: ['analytical_skills', 'research_experience', 'data_comfort'],
      logic: (sources) => {
        const analytical = parseInt(sources.analytical_skills) || 0
        const research = sources.research_experience === 'yes' ? 5 : 0
        const dataComfort = parseInt(sources.data_comfort) || 0
        
        const score = (analytical * 0.4) + (research * 0.3) + (dataComfort * 0.3)
        if (score >= 8) return 'high'
        if (score >= 5) return 'medium'
        return 'low'
      },
      confidence: 0.7
    }
  ]
  
  static applyPrePopulation(responses, targetQuestion) {
    const rule = this.rules.find(r => r.target === targetQuestion)
    if (!rule) return null
    
    const sourceValues = {}
    let hasAllSources = true
    
    for (const source of rule.sources) {
      const value = this.getNestedValue(responses, source)
      if (value === undefined || value === null || value === '') {
        hasAllSources = false
        break
      }
      sourceValues[source] = value
    }
    
    if (!hasAllSources) return null
    
    try {
      const result = rule.logic(sourceValues)
      return {
        value: result,
        confidence: rule.confidence,
        sources: rule.sources
      }
    } catch (error) {
      console.warn(`Pre-population failed for ${targetQuestion}:`, error)
      return null
    }
  }
  
  static getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : undefined
    }, obj)
  }
}

// Skip Logic Engine
export class SkipLogicEngine {
  static rules = [
    {
      condition: (responses) => responses.has_business_idea === 'no',
      skipQuestions: [
        'idea_validation_methods',
        'competitive_analysis_depth',
        'product_development_stage',
        'customer_feedback_collection',
        'mvp_development',
        'market_testing_results'
      ]
    },
    
    {
      condition: (responses) => 
        responses.financial_situation === 'stable' && 
        parseInt(responses.savings_months) >= 12,
      skipQuestions: [
        'financial_stress_management',
        'income_replacement_timeline',
        'emergency_fund_planning',
        'financial_anxiety_questions'
      ]
    },
    
    {
      condition: (responses) => parseInt(responses.industry_experience) >= 5,
      skipQuestions: [
        'industry_basics',
        'market_fundamentals',
        'competitive_landscape_intro',
        'industry_terminology'
      ]
    },
    
    {
      condition: (responses) => responses.team_building_interest === 'solo',
      skipQuestions: [
        'hiring_strategies',
        'team_management_style',
        'delegation_preferences',
        'leadership_development',
        'team_building_questions'
      ]
    },
    
    {
      condition: (responses) => parseInt(responses.technology_comfort) <= 3,
      skipQuestions: [
        'advanced_digital_marketing',
        'automation_strategies',
        'tech_stack_preferences',
        'digital_transformation'
      ]
    },
    
    {
      condition: (responses) => responses.business_scope === 'local',
      skipQuestions: [
        'international_expansion',
        'global_market_analysis',
        'cross_cultural_considerations',
        'international_regulations'
      ]
    }
  ]
  
  static shouldSkipQuestion(questionId, responses) {
    return this.rules.some(rule => {
      try {
        return rule.condition(responses) && rule.skipQuestions.includes(questionId)
      } catch (error) {
        console.warn(`Skip logic evaluation failed for ${questionId}:`, error)
        return false
      }
    })
  }
  
  static getSkippedQuestions(responses) {
    const skipped = []
    this.rules.forEach(rule => {
      try {
        if (rule.condition(responses)) {
          skipped.push(...rule.skipQuestions)
        }
      } catch (error) {
        console.warn('Skip logic evaluation failed:', error)
      }
    })
    return [...new Set(skipped)] // Remove duplicates
  }
}

// User Profile Detection Engine
export class UserProfileDetector {
  static detectProfile(responses) {
    const scores = {
      [USER_PROFILE_TYPES.BEGINNER_ENTREPRENEUR]: 0,
      [USER_PROFILE_TYPES.EXPERIENCED_PROFESSIONAL]: 0,
      [USER_PROFILE_TYPES.SERIAL_ENTREPRENEUR]: 0,
      [USER_PROFILE_TYPES.INDUSTRY_SPECIALIST]: 0,
      [USER_PROFILE_TYPES.CREATIVE_INNOVATOR]: 0
    }
    
    // Entrepreneurship experience
    const entrepreneurshipExp = responses.entrepreneurship_experience || 'none'
    if (entrepreneurshipExp === 'none') {
      scores[USER_PROFILE_TYPES.BEGINNER_ENTREPRENEUR] += 3
    }
    
    // Work experience and leadership
    const workExp = parseInt(responses.work_experience) || 0
    const hasLeadership = responses.leadership_roles === 'yes'
    if (workExp >= 5 && hasLeadership) {
      scores[USER_PROFILE_TYPES.EXPERIENCED_PROFESSIONAL] += 3
    }
    
    // Previous businesses
    const previousBusinesses = parseInt(responses.previous_businesses) || 0
    if (previousBusinesses > 0) {
      scores[USER_PROFILE_TYPES.SERIAL_ENTREPRENEUR] += 4
    }
    
    // Industry expertise
    const industryExp = parseInt(responses.industry_experience) || 0
    const domainExpertise = responses.domain_expertise === 'high'
    if (industryExp >= 7 && domainExpertise) {
      scores[USER_PROFILE_TYPES.INDUSTRY_SPECIALIST] += 3
    }
    
    // Creative background
    const creativeBackground = responses.creative_background === 'yes'
    const innovationFocus = responses.innovation_focus === 'high'
    if (creativeBackground || innovationFocus) {
      scores[USER_PROFILE_TYPES.CREATIVE_INNOVATOR] += 3
    }
    
    // Business knowledge level
    const businessKnowledge = parseInt(responses.business_knowledge_level) || 0
    if (businessKnowledge <= 2) {
      scores[USER_PROFILE_TYPES.BEGINNER_ENTREPRENEUR] += 2
    } else if (businessKnowledge >= 8) {
      scores[USER_PROFILE_TYPES.SERIAL_ENTREPRENEUR] += 2
    }
    
    // Find the highest scoring profile
    const topProfile = Object.entries(scores).reduce((a, b) => 
      scores[a[0]] > scores[b[0]] ? a : b
    )[0]
    
    return {
      profileType: topProfile,
      confidence: Math.max(...Object.values(scores)) / 10,
      scores,
      path: ASSESSMENT_PATHS[topProfile]
    }
  }
}

// Question Priority Engine
export class QuestionPriorityEngine {
  static priorities = {
    // Critical questions (Priority 1) - Must ask everyone
    core_motivation: 1,
    risk_tolerance: 1,
    financial_readiness: 1,
    time_commitment: 1,
    business_idea_status: 1,
    support_system: 1,
    entrepreneurship_experience: 1,
    
    // Important questions (Priority 2) - Ask unless clearly irrelevant
    industry_experience: 2,
    leadership_background: 2,
    market_understanding: 2,
    technical_skills: 2,
    networking_ability: 2,
    learning_agility: 2,
    work_experience: 2,
    education_background: 2,
    
    // Nice-to-have questions (Priority 3) - Ask if time permits
    personality_traits: 3,
    communication_style: 3,
    work_preferences: 3,
    lifestyle_factors: 3,
    long_term_vision: 3,
    hobby_interests: 3,
    social_preferences: 3
  }
  
  static getQuestionPriority(questionId) {
    return this.priorities[questionId] || 2 // Default to priority 2
  }
  
  static sortQuestionsByPriority(questions) {
    return questions.sort((a, b) => {
      const priorityA = this.getQuestionPriority(a.id)
      const priorityB = this.getQuestionPriority(b.id)
      return priorityA - priorityB
    })
  }
  
  static filterQuestionsByPriority(questions, maxPriority = 3) {
    return questions.filter(q => this.getQuestionPriority(q.id) <= maxPriority)
  }
}

// Main Adaptive Assessment Engine
export class AdaptiveAssessmentEngine {
  constructor() {
    this.prePopulationEngine = PrePopulationEngine
    this.skipLogicEngine = SkipLogicEngine
    this.profileDetector = UserProfileDetector
    this.priorityEngine = QuestionPriorityEngine
  }
  
  // Get personalized assessment path for user
  getPersonalizedPath(responses) {
    const profile = this.profileDetector.detectProfile(responses)
    return profile
  }
  
  // Process questions for adaptive assessment
  processQuestions(questions, responses, userProfile) {
    let processedQuestions = [...questions]
    
    // Apply skip logic
    processedQuestions = processedQuestions.filter(q => 
      !this.skipLogicEngine.shouldSkipQuestion(q.id, responses)
    )
    
    // Apply priority filtering based on user profile
    if (userProfile && userProfile.path) {
      const maxPriority = userProfile.path.questionCount <= 150 ? 2 : 3
      processedQuestions = this.priorityEngine.filterQuestionsByPriority(
        processedQuestions, 
        maxPriority
      )
    }
    
    // Sort by priority
    processedQuestions = this.priorityEngine.sortQuestionsByPriority(processedQuestions)
    
    // Apply pre-population
    processedQuestions = processedQuestions.map(q => {
      const prePopulated = this.prePopulationEngine.applyPrePopulation(responses, q.id)
      if (prePopulated) {
        return {
          ...q,
          prePopulated: prePopulated.value,
          prePopulationConfidence: prePopulated.confidence,
          prePopulationSources: prePopulated.sources
        }
      }
      return q
    })
    
    return processedQuestions
  }
  
  // Calculate assessment progress with adaptive logic
  calculateAdaptiveProgress(responses, totalQuestions, userProfile) {
    const skippedQuestions = this.skipLogicEngine.getSkippedQuestions(responses)
    const effectiveTotal = totalQuestions - skippedQuestions.length
    const answeredQuestions = Object.keys(responses).length
    
    return Math.min(100, Math.round((answeredQuestions / effectiveTotal) * 100))
  }
  
  // Get next recommended question
  getNextQuestion(questions, responses, userProfile) {
    const processedQuestions = this.processQuestions(questions, responses, userProfile)
    const unansweredQuestions = processedQuestions.filter(q => 
      !responses[q.id] && !q.prePopulated
    )
    
    return unansweredQuestions.length > 0 ? unansweredQuestions[0] : null
  }
  
  // Generate assessment summary with adaptive insights
  generateAssessmentSummary(responses, userProfile) {
    const skippedQuestions = this.skipLogicEngine.getSkippedQuestions(responses)
    const prePopulatedCount = Object.keys(responses).filter(key => 
      this.prePopulationEngine.applyPrePopulation(responses, key)
    ).length
    
    return {
      userProfile: userProfile,
      totalResponses: Object.keys(responses).length,
      skippedQuestions: skippedQuestions.length,
      prePopulatedAnswers: prePopulatedCount,
      timeEstimate: userProfile?.path?.estimatedTime || 'Unknown',
      completionPercentage: this.calculateAdaptiveProgress(responses, 500, userProfile),
      recommendations: this.generatePersonalizedRecommendations(responses, userProfile)
    }
  }
  
  // Generate personalized recommendations
  generatePersonalizedRecommendations(responses, userProfile) {
    const recommendations = []
    
    if (userProfile?.profileType === USER_PROFILE_TYPES.BEGINNER_ENTREPRENEUR) {
      recommendations.push(
        'Consider taking an entrepreneurship course to build foundational knowledge',
        'Start with a small, low-risk business idea to gain experience',
        'Find a mentor or join an entrepreneur support group'
      )
    } else if (userProfile?.profileType === USER_PROFILE_TYPES.EXPERIENCED_PROFESSIONAL) {
      recommendations.push(
        'Leverage your professional network for business opportunities',
        'Consider consulting in your area of expertise as a starting point',
        'Focus on market validation before leaving your current role'
      )
    } else if (userProfile?.profileType === USER_PROFILE_TYPES.SERIAL_ENTREPRENEUR) {
      recommendations.push(
        'Explore opportunities for scaling or portfolio expansion',
        'Consider angel investing or mentoring other entrepreneurs',
        'Focus on systems and processes for efficient business management'
      )
    }
    
    return recommendations
  }
}

export default AdaptiveAssessmentEngine

