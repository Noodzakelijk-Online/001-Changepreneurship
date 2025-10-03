/**
 * Simplified Adaptive Assessment Engine for Changepreneurship Platform
 * Focuses on core adaptive features without complex user archetypes
 */

// Simple Experience Levels (instead of complex archetypes)
export const EXPERIENCE_LEVELS = {
  BEGINNER: 'beginner',
  INTERMEDIATE: 'intermediate', 
  EXPERIENCED: 'experienced'
}

// Simplified Assessment Configuration
export const ASSESSMENT_CONFIG = {
  [EXPERIENCE_LEVELS.BEGINNER]: {
    name: 'Comprehensive Track',
    description: 'Full assessment with explanations and guidance',
    estimatedTime: '45-60 minutes',
    questionCount: 250,
    explanationLevel: 'detailed',
    showEducationalContent: true
  },
  
  [EXPERIENCE_LEVELS.INTERMEDIATE]: {
    name: 'Focused Track', 
    description: 'Streamlined assessment for those with some business knowledge',
    estimatedTime: '30-45 minutes',
    questionCount: 180,
    explanationLevel: 'moderate',
    showEducationalContent: false
  },
  
  [EXPERIENCE_LEVELS.EXPERIENCED]: {
    name: 'Expert Track',
    description: 'Rapid assessment for experienced entrepreneurs',
    estimatedTime: '15-30 minutes', 
    questionCount: 120,
    explanationLevel: 'minimal',
    showEducationalContent: false
  }
}

// Pre-population Rules (simplified)
export class SimplePrePopulationEngine {
  static rules = [
    {
      // If someone has a clear business idea, pre-populate idea clarity as high
      target: 'business_idea_clarity',
      condition: (responses) => responses.has_business_idea === 'yes',
      value: 'high',
      confidence: 0.8
    },
    
    {
      // If someone has 5+ years work experience, pre-populate professional readiness
      target: 'professional_readiness',
      condition: (responses) => parseInt(responses.work_experience_years) >= 5,
      value: 'high',
      confidence: 0.9
    },
    
    {
      // If someone has managed teams, pre-populate leadership capability
      target: 'leadership_capability',
      condition: (responses) => responses.has_managed_teams === 'yes',
      value: 'experienced',
      confidence: 0.8
    },
    
    {
      // If someone has stable income and savings, pre-populate financial readiness
      target: 'financial_readiness',
      condition: (responses) => 
        responses.employment_status === 'employed' && 
        parseInt(responses.savings_months) >= 6,
      value: 'stable',
      confidence: 0.9
    },
    
    {
      // If someone has industry experience, pre-populate market knowledge
      target: 'market_knowledge',
      condition: (responses) => parseInt(responses.industry_experience_years) >= 3,
      value: 'good',
      confidence: 0.7
    }
  ]
  
  static getPrePopulatedValue(questionId, responses) {
    const rule = this.rules.find(r => r.target === questionId)
    if (!rule) return null
    
    try {
      if (rule.condition(responses)) {
        return {
          value: rule.value,
          confidence: rule.confidence,
          reason: `Auto-filled based on your previous responses`
        }
      }
    } catch (error) {
      console.warn(`Pre-population failed for ${questionId}:`, error)
    }
    
    return null
  }
}

// Skip Logic (simplified)
export class SimpleSkipLogicEngine {
  static rules = [
    {
      // Skip idea validation questions if no business idea
      condition: (responses) => responses.has_business_idea === 'no',
      skipQuestions: [
        'idea_validation_methods',
        'competitive_analysis',
        'target_customer_definition',
        'value_proposition_clarity',
        'market_size_estimation'
      ],
      reason: 'No business idea to validate'
    },
    
    {
      // Skip financial stress questions if financially stable
      condition: (responses) => 
        responses.employment_status === 'employed' && 
        parseInt(responses.savings_months) >= 12,
      skipQuestions: [
        'financial_stress_tolerance',
        'income_replacement_concerns',
        'financial_anxiety_management'
      ],
      reason: 'Strong financial position reduces stress concerns'
    },
    
    {
      // Skip team management questions if planning to work solo
      condition: (responses) => responses.business_model_preference === 'solo',
      skipQuestions: [
        'team_building_strategies',
        'hiring_preferences',
        'management_style',
        'delegation_comfort'
      ],
      reason: 'Solo business model doesn\'t require team management'
    },
    
    {
      // Skip advanced tech questions if low tech comfort
      condition: (responses) => parseInt(responses.technology_comfort_level) <= 3,
      skipQuestions: [
        'digital_marketing_automation',
        'tech_stack_preferences',
        'software_development_interest'
      ],
      reason: 'Low technology comfort level'
    },
    
    {
      // Skip investor questions if bootstrap preference
      condition: (responses) => responses.funding_preference === 'bootstrap',
      skipQuestions: [
        'investor_relations',
        'pitch_preparation',
        'equity_sharing_comfort',
        'board_management'
      ],
      reason: 'Bootstrap funding preference excludes investor relations'
    }
  ]
  
  static shouldSkipQuestion(questionId, responses) {
    return this.rules.some(rule => {
      try {
        return rule.condition(responses) && rule.skipQuestions.includes(questionId)
      } catch (error) {
        return false
      }
    })
  }
  
  static getSkipReason(questionId, responses) {
    const rule = this.rules.find(rule => {
      try {
        return rule.condition(responses) && rule.skipQuestions.includes(questionId)
      } catch (error) {
        return false
      }
    })
    return rule ? rule.reason : null
  }
}

// Experience Level Detection (simplified)
export class SimpleExperienceLevelDetector {
  static detectExperienceLevel(responses) {
    let score = 0
    
    // Work experience
    const workYears = parseInt(responses.work_experience_years) || 0
    if (workYears >= 10) score += 3
    else if (workYears >= 5) score += 2
    else if (workYears >= 2) score += 1
    
    // Business knowledge
    const businessKnowledge = parseInt(responses.business_knowledge_level) || 0
    if (businessKnowledge >= 8) score += 3
    else if (businessKnowledge >= 5) score += 2
    else if (businessKnowledge >= 3) score += 1
    
    // Previous business experience
    if (responses.has_started_business === 'yes') score += 2
    if (responses.has_managed_teams === 'yes') score += 1
    if (responses.has_business_education === 'yes') score += 1
    
    // Determine experience level
    if (score >= 7) return EXPERIENCE_LEVELS.EXPERIENCED
    if (score >= 4) return EXPERIENCE_LEVELS.INTERMEDIATE
    return EXPERIENCE_LEVELS.BEGINNER
  }
  
  static getExperienceLevelInfo(level) {
    return ASSESSMENT_CONFIG[level] || ASSESSMENT_CONFIG[EXPERIENCE_LEVELS.BEGINNER]
  }
}

// Question Consolidation Engine (simplified)
export class QuestionConsolidationEngine {
  static consolidationRules = [
    {
      // Consolidate multiple risk tolerance questions into one comprehensive question
      originalQuestions: [
        'financial_risk_comfort',
        'career_risk_tolerance', 
        'investment_risk_appetite',
        'uncertainty_comfort_level'
      ],
      consolidatedQuestion: {
        id: 'overall_risk_tolerance',
        text: 'How would you describe your overall approach to risk in entrepreneurship?',
        type: 'comprehensive_scale',
        subQuestions: [
          'Financial risk (investing money)',
          'Career risk (leaving stable job)',
          'Market risk (uncertain demand)',
          'Personal risk (work-life balance)'
        ],
        estimatedTime: 3 // minutes
      },
      timeSaved: 8 // minutes (was 4 separate questions × 2 minutes each)
    },
    
    {
      // Consolidate motivation questions
      originalQuestions: [
        'primary_motivation',
        'success_definition',
        'personal_fulfillment_factors'
      ],
      consolidatedQuestion: {
        id: 'entrepreneurial_motivation',
        text: 'What drives your interest in entrepreneurship?',
        type: 'multi_select_with_ranking',
        options: [
          'Financial independence',
          'Personal fulfillment',
          'Making an impact',
          'Creative freedom',
          'Building something lasting',
          'Solving problems'
        ],
        estimatedTime: 2
      },
      timeSaved: 4
    },
    
    {
      // Consolidate market understanding questions
      originalQuestions: [
        'target_customer_clarity',
        'market_size_awareness',
        'competitive_landscape_knowledge',
        'industry_trends_understanding'
      ],
      consolidatedQuestion: {
        id: 'market_understanding',
        text: 'How well do you understand your target market?',
        type: 'matrix_rating',
        dimensions: [
          'Target customers',
          'Market size',
          'Competition',
          'Industry trends'
        ],
        estimatedTime: 3
      },
      timeSaved: 6
    }
  ]
  
  static getConsolidatedQuestions() {
    return this.consolidationRules.map(rule => rule.consolidatedQuestion)
  }
  
  static getTotalTimeSaved() {
    return this.consolidationRules.reduce((total, rule) => total + rule.timeSaved, 0)
  }
  
  static getOriginalQuestionCount() {
    return this.consolidationRules.reduce((total, rule) => total + rule.originalQuestions.length, 0)
  }
}

// Main Simplified Adaptive Engine
export class SimplifiedAdaptiveEngine {
  constructor() {
    this.prePopulationEngine = SimplePrePopulationEngine
    this.skipLogicEngine = SimpleSkipLogicEngine
    this.experienceDetector = SimpleExperienceLevelDetector
    this.consolidationEngine = QuestionConsolidationEngine
  }
  
  // Detect user experience level (instead of complex archetypes)
  detectExperienceLevel(responses) {
    const level = this.experienceDetector.detectExperienceLevel(responses)
    const config = this.experienceDetector.getExperienceLevelInfo(level)
    
    return {
      level,
      config,
      confidence: this.calculateConfidence(responses),
      responseCount: Object.keys(responses).length
    }
  }
  
  // Calculate confidence based on number of responses
  calculateConfidence(responses) {
    const responseCount = Object.keys(responses).length
    if (responseCount >= 10) return 0.9
    if (responseCount >= 7) return 0.8
    if (responseCount >= 5) return 0.7
    if (responseCount >= 3) return 0.5
    return 0.3
  }
  
  // Process questions with simplified adaptive logic
  processQuestions(questions, responses) {
    let processedQuestions = [...questions]
    
    // Apply skip logic
    processedQuestions = processedQuestions.filter(q => 
      !this.skipLogicEngine.shouldSkipQuestion(q.id, responses)
    )
    
    // Apply pre-population
    processedQuestions = processedQuestions.map(q => {
      const prePopulated = this.prePopulationEngine.getPrePopulatedValue(q.id, responses)
      if (prePopulated) {
        return {
          ...q,
          prePopulated: prePopulated.value,
          prePopulationConfidence: prePopulated.confidence,
          prePopulationReason: prePopulated.reason
        }
      }
      return q
    })
    
    return processedQuestions
  }
  
  // Get assessment statistics
  getAssessmentStats(responses) {
    const experienceLevel = this.detectExperienceLevel(responses)
    const skippedQuestions = this.skipLogicEngine.rules.reduce((total, rule) => {
      try {
        return rule.condition(responses) ? total + rule.skipQuestions.length : total
      } catch {
        return total
      }
    }, 0)
    
    const prePopulatedQuestions = this.prePopulationEngine.rules.filter(rule => {
      try {
        return rule.condition(responses)
      } catch {
        return false
      }
    }).length
    
    return {
      experienceLevel: experienceLevel.level,
      confidence: experienceLevel.confidence,
      estimatedTime: experienceLevel.config.estimatedTime,
      questionCount: experienceLevel.config.questionCount,
      skippedQuestions,
      prePopulatedQuestions,
      timeSaved: this.consolidationEngine.getTotalTimeSaved(),
      originalQuestions: this.consolidationEngine.getOriginalQuestionCount(),
      consolidatedQuestions: this.consolidationEngine.getConsolidatedQuestions().length
    }
  }
}

export default SimplifiedAdaptiveEngine

