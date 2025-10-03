/**
 * Data-Driven Adaptive Assessment Engine for Changepreneurship Platform
 * Simple approach: More data import = More pre-population = Faster assessment
 */

// Data Sources for Import and Analysis
export const DATA_SOURCES = {
  LINKEDIN: {
    id: 'linkedin',
    name: 'LinkedIn Profile',
    icon: 'linkedin',
    dataTypes: ['work_experience', 'education', 'skills', 'connections', 'industry'],
    prePopulationPotential: 85, // percentage of questions this can help with
    estimatedTimeSaved: 15 // minutes
  },
  
  SOCIAL_MEDIA: {
    id: 'social_media',
    name: 'Social Media Profiles',
    icon: 'share',
    dataTypes: ['interests', 'communication_style', 'network', 'activities'],
    prePopulationPotential: 40,
    estimatedTimeSaved: 8
  },
  
  EMAIL_ANALYSIS: {
    id: 'email',
    name: 'Email Communication',
    icon: 'mail',
    dataTypes: ['communication_patterns', 'business_contacts', 'project_involvement'],
    prePopulationPotential: 30,
    estimatedTimeSaved: 6
  },
  
  CALENDAR_DATA: {
    id: 'calendar',
    name: 'Calendar & Schedule',
    icon: 'calendar',
    dataTypes: ['time_management', 'meeting_patterns', 'availability'],
    prePopulationPotential: 25,
    estimatedTimeSaved: 4
  },
  
  FINANCIAL_DATA: {
    id: 'financial',
    name: 'Financial Information',
    icon: 'dollar-sign',
    dataTypes: ['income', 'expenses', 'savings', 'investments'],
    prePopulationPotential: 60,
    estimatedTimeSaved: 10
  },
  
  RESUME_CV: {
    id: 'resume',
    name: 'Resume/CV Upload',
    icon: 'file-text',
    dataTypes: ['work_history', 'achievements', 'skills', 'education'],
    prePopulationPotential: 70,
    estimatedTimeSaved: 12
  }
}

// Data Import and Pre-population Engine
export class DataImportEngine {
  
  // Calculate total time savings based on connected data sources
  static calculateTimeSavings(connectedSources) {
    return connectedSources.reduce((total, sourceId) => {
      const source = DATA_SOURCES[sourceId]
      return total + (source ? source.estimatedTimeSaved : 0)
    }, 0)
  }
  
  // Calculate pre-population coverage
  static calculatePrePopulationCoverage(connectedSources) {
    if (connectedSources.length === 0) return 0
    
    const totalPotential = connectedSources.reduce((total, sourceId) => {
      const source = DATA_SOURCES[sourceId]
      return total + (source ? source.prePopulationPotential : 0)
    }, 0)
    
    // Cap at 95% (never 100% pre-population)
    return Math.min(95, totalPotential)
  }
  
  // Pre-populate questions based on imported data
  static prePopulateFromData(questionId, importedData) {
    const rules = {
      // Work Experience Questions
      'work_experience_years': {
        source: 'linkedin.work_experience',
        extractor: (data) => data.totalYears,
        confidence: 0.95
      },
      
      'current_job_title': {
        source: 'linkedin.current_position',
        extractor: (data) => data.title,
        confidence: 0.9
      },
      
      'industry_experience': {
        source: 'linkedin.industry',
        extractor: (data) => data.primary,
        confidence: 0.85
      },
      
      'leadership_experience': {
        source: 'linkedin.work_experience',
        extractor: (data) => data.positions.some(p => 
          p.title.toLowerCase().includes('manager') || 
          p.title.toLowerCase().includes('director') ||
          p.title.toLowerCase().includes('lead')
        ) ? 'yes' : 'no',
        confidence: 0.8
      },
      
      // Education Questions
      'education_level': {
        source: 'linkedin.education',
        extractor: (data) => data.highest_degree,
        confidence: 0.95
      },
      
      'business_education': {
        source: 'linkedin.education',
        extractor: (data) => data.degrees.some(d => 
          d.field.toLowerCase().includes('business') ||
          d.field.toLowerCase().includes('mba') ||
          d.field.toLowerCase().includes('management')
        ) ? 'yes' : 'no',
        confidence: 0.9
      },
      
      // Skills Questions
      'technical_skills': {
        source: 'linkedin.skills',
        extractor: (data) => data.technical_skills.join(', '),
        confidence: 0.8
      },
      
      'communication_skills': {
        source: 'social_media.communication_analysis',
        extractor: (data) => data.communication_score,
        confidence: 0.7
      },
      
      // Financial Questions
      'current_income_range': {
        source: 'financial.income',
        extractor: (data) => data.monthly_income_range,
        confidence: 0.9
      },
      
      'savings_amount': {
        source: 'financial.savings',
        extractor: (data) => data.total_savings,
        confidence: 0.95
      },
      
      'monthly_expenses': {
        source: 'financial.expenses',
        extractor: (data) => data.monthly_total,
        confidence: 0.9
      },
      
      // Network Questions
      'professional_network_size': {
        source: 'linkedin.connections',
        extractor: (data) => data.connection_count > 500 ? 'large' : 
                           data.connection_count > 100 ? 'medium' : 'small',
        confidence: 0.8
      },
      
      'industry_contacts': {
        source: 'linkedin.connections',
        extractor: (data) => data.industry_connections,
        confidence: 0.7
      },
      
      // Time Management Questions
      'time_availability': {
        source: 'calendar.analysis',
        extractor: (data) => data.free_hours_per_week,
        confidence: 0.8
      },
      
      'current_commitments': {
        source: 'calendar.analysis',
        extractor: (data) => data.commitment_level,
        confidence: 0.75
      }
    }
    
    const rule = rules[questionId]
    if (!rule) return null
    
    try {
      const sourceData = this.getNestedValue(importedData, rule.source)
      if (!sourceData) return null
      
      const value = rule.extractor(sourceData)
      if (value === null || value === undefined) return null
      
      return {
        value,
        confidence: rule.confidence,
        source: rule.source,
        dataImported: true
      }
    } catch (error) {
      console.warn(`Pre-population failed for ${questionId}:`, error)
      return null
    }
  }
  
  static getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : undefined
    }, obj)
  }
}

// Smart Skip Logic (data-driven)
export class DataDrivenSkipLogic {
  static rules = [
    {
      // Skip questions if we already have the data
      condition: (responses, importedData) => {
        return importedData.linkedin && importedData.linkedin.work_experience
      },
      skipQuestions: [
        'work_experience_details',
        'job_responsibilities',
        'career_progression'
      ],
      reason: 'Work experience imported from LinkedIn'
    },
    
    {
      // Skip financial questions if financial data imported
      condition: (responses, importedData) => {
        return importedData.financial && importedData.financial.complete_profile
      },
      skipQuestions: [
        'income_estimation',
        'expense_breakdown',
        'savings_details'
      ],
      reason: 'Financial information imported from connected accounts'
    },
    
    {
      // Skip network questions if social data available
      condition: (responses, importedData) => {
        return importedData.linkedin && importedData.social_media
      },
      skipQuestions: [
        'network_size_estimation',
        'professional_connections',
        'social_influence'
      ],
      reason: 'Network data imported from social profiles'
    }
  ]
  
  static shouldSkipQuestion(questionId, responses, importedData = {}) {
    return this.rules.some(rule => {
      try {
        return rule.condition(responses, importedData) && rule.skipQuestions.includes(questionId)
      } catch (error) {
        return false
      }
    })
  }
}

// Main Data-Driven Adaptive Engine
export class DataDrivenAdaptiveEngine {
  constructor() {
    this.importEngine = DataImportEngine
    this.skipLogic = DataDrivenSkipLogic
  }
  
  // Calculate assessment optimization based on available data
  calculateOptimization(connectedSources, importedData = {}) {
    const timeSaved = DataImportEngine.calculateTimeSavings(connectedSources)
    const prePopulationCoverage = DataImportEngine.calculatePrePopulationCoverage(connectedSources)
    
    // Calculate questions that can be skipped due to imported data
    const skippableQuestions = this.skipLogic.rules.reduce((total, rule) => {
      try {
        return rule.condition({}, importedData) ? total + rule.skipQuestions.length : total
      } catch {
        return total
      }
    }, 0)
    
    return {
      connectedSources: connectedSources.length,
      timeSavedMinutes: timeSaved,
      prePopulationCoverage,
      skippableQuestions,
      totalOptimization: Math.min(90, timeSaved + (prePopulationCoverage * 0.5))
    }
  }
  
  // Process questions with data-driven logic
  processQuestionsWithData(questions, responses, importedData = {}) {
    let processedQuestions = [...questions]
    
    // Apply data-driven skip logic
    processedQuestions = processedQuestions.filter(q => 
      !this.skipLogic.shouldSkipQuestion(q.id, responses, importedData)
    )
    
    // Apply data-driven pre-population
    processedQuestions = processedQuestions.map(q => {
      const prePopulated = this.importEngine.prePopulateFromData(q.id, importedData)
      if (prePopulated) {
        return {
          ...q,
          prePopulated: prePopulated.value,
          prePopulationConfidence: prePopulated.confidence,
          prePopulationSource: prePopulated.source,
          dataImported: true
        }
      }
      return q
    })
    
    return processedQuestions
  }
  
  // Get recommended data sources to connect
  getRecommendedDataSources(currentSources = []) {
    const available = Object.values(DATA_SOURCES).filter(source => 
      !currentSources.includes(source.id)
    )
    
    // Sort by potential impact (time saved + pre-population potential)
    return available.sort((a, b) => {
      const impactA = a.estimatedTimeSaved + (a.prePopulationPotential * 0.1)
      const impactB = b.estimatedTimeSaved + (b.prePopulationPotential * 0.1)
      return impactB - impactA
    })
  }
}

export default DataDrivenAdaptiveEngine

