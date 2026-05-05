import React, { useState, useEffect } from 'react'
import AssessmentShell from './AssessmentShell'
import { BarChart3, Users, Globe, Target, Shield, FileText } from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'

const MarketResearchTools = () => {
  const {
    assessmentData,
    updateResponse,
    updateProgress,
    completePhase,
    updatePhase
  } = useAssessment()
  
  const [currentSection, setCurrentSection] = useState('competitive-analysis')
  const [sectionProgress, setSectionProgress] = useState({})
  
  const marketResearchData = assessmentData['market_research'] || {}
  const responses = marketResearchData.responses || {}

  // Assessment sections configuration
  const sections = [
    {
      id: 'competitive-analysis',
      title: 'Competitive Landscape',
      description: 'Analyze your competition and market positioning',
      icon: BarChart3,
      duration: '30-45 minutes',
      questions: competitiveAnalysisQuestions
    },
    {
      id: 'customer-research',
      title: 'Customer Insights',
      description: 'Understand your target customers deeply',
      icon: Users,
      duration: '45-60 minutes',
      questions: customerResearchQuestions
    },
    {
      id: 'stakeholder-mapping',
      title: 'Stakeholder Ecosystem',
      description: 'Map all parties that influence your business',
      icon: Globe,
      duration: '30-40 minutes',
      questions: stakeholderMappingQuestions
    },
    {
      id: 'problem-classification',
      title: 'Problem Analysis',
      description: 'Classify and prioritize the problems you solve',
      icon: Target,
      duration: '25-35 minutes',
      questions: problemClassificationQuestions
    },
    {
      id: 'market-validation',
      title: 'Market Validation',
      description: 'Validate your assumptions with real data',
      icon: Shield,
      duration: '60-90 minutes',
      questions: marketValidationQuestions
    },
    {
      id: 'research-insights',
      title: 'Research Report',
      description: 'Your comprehensive market analysis',
      icon: FileText,
      duration: '10 minutes',
      questions: []
    }
  ]

  // Calculate overall progress
  const calculateOverallProgress = () => {
    const totalSections = sections.length - 1 // Exclude results section
    const completedSections = Object.values(sectionProgress).filter(progress => progress >= 100).length
    return Math.round((completedSections / totalSections) * 100)
  }

  // Calculate section progress
  const calculateSectionProgress = (sectionId) => {
    const section = sections.find(s => s.id === sectionId)
    if (!section || !section.questions) return 0
    
    const sectionResponses = responses[sectionId] || {}
    const answeredQuestions = Object.keys(sectionResponses).length
    const totalQuestions = section.questions.length
    
    return totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0
  }

  // Update section progress when responses change
  useEffect(() => {
    const newProgress = {}
    sections.forEach(section => {
      if (section.questions) {
        newProgress[section.id] = calculateSectionProgress(section.id)
      }
    })
    setSectionProgress(newProgress)
    
    // Update overall progress
    const overallProgress = calculateOverallProgress()
    updateProgress('market_research', overallProgress)
    
    // Complete phase if all sections are done
    if (overallProgress >= 100 && !marketResearchData.completed) {
      completePhase('market_research')
    }
  }, [responses])

  const handleResponse = (sectionId, questionId, answer) => {
    updateResponse('market_research', questionId, answer, sectionId)
    const section = sections.find(s => s.id === sectionId)
    const total = section?.questions?.length || 1
    const updated = { ...(responses[sectionId] || {}), [questionId]: answer }
    const progress = Math.round((Object.keys(updated).length / total) * 100)
    setSectionProgress(prev => ({ ...prev, [sectionId]: progress }))
  }

  return (
    <AssessmentShell
      phaseName="Market Research"
      phaseNumber={3}
      sections={sections}
      currentSection={currentSection}
      onSectionChange={setCurrentSection}
      responses={responses}
      onResponse={handleResponse}
      sectionProgress={sectionProgress}
      completed={Boolean(marketResearchData.completed)}
      onNext={() => completePhase('market_research', () => updatePhase('business_pillars'))}
      nextLabel="Next Phase: Business Pillars"
    />
  )
}
// Question definitions
const competitiveAnalysisQuestions = [
  {
    id: 'competitor-identification',
    question: 'Identify and analyze your key competitors',
    description: 'List companies that offer similar solutions or compete for the same customers',
    type: 'competitor-analysis',
    required: true,
    maxCompetitors: 5,
    helpText: 'Include both direct competitors (same solution) and indirect competitors (different solution, same problem).'
  },
  {
    id: 'competitive-advantage',
    question: 'What will be your unique competitive advantage?',
    type: 'textarea',
    required: true,
    placeholder: 'Describe what will make you different and better than competitors...',
    helpText: 'Think about your unique combination of features, pricing, service, or approach.'
  },
  {
    id: 'market-positioning',
    question: 'How do you want to position yourself in the market?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'premium', label: 'Premium/Luxury', description: 'High quality, high price, exclusive' },
      { value: 'value', label: 'Value Leader', description: 'Best quality for the price' },
      { value: 'cost', label: 'Cost Leader', description: 'Lowest price in market' },
      { value: 'niche', label: 'Niche Specialist', description: 'Focused on specific segment' },
      { value: 'innovation', label: 'Innovation Leader', description: 'First with new solutions' }
    ],
    helpText: 'Your positioning should align with your target customers and competitive advantages.'
  }
]

const customerResearchQuestions = [
  {
    id: 'primary-persona',
    question: 'Create your primary customer persona',
    description: 'Develop a detailed profile of your most important customer segment',
    type: 'textarea',
    required: true,
    placeholder: 'Name / Role: (e.g. "Emma, 32, Freelance Graphic Designer")\n\nDemographics: age, location, income, education...\n\nGoals & Motivations: what they are trying to achieve...\n\nPains & Frustrations: what holds them back...\n\nHow they currently solve the problem: tools, workarounds...\n\nWhere to find them: channels, communities, platforms...',
    helpText: 'Be as specific as possible. This persona should represent your ideal customer.'
  },
  {
    id: 'customer-journey',
    question: 'Describe your customer\'s journey from problem awareness to purchase',
    type: 'textarea',
    required: true,
    placeholder: 'Walk through the steps: awareness → consideration → decision → purchase → onboarding...',
    helpText: 'Understanding this journey helps you identify touchpoints and optimization opportunities.'
  },
  {
    id: 'customer-validation',
    question: 'How will you validate your customer assumptions?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'interviews', label: 'Customer Interviews', description: 'One-on-one conversations' },
      { value: 'surveys', label: 'Online Surveys', description: 'Structured questionnaires' },
      { value: 'focus-groups', label: 'Focus Groups', description: 'Group discussions' },
      { value: 'mvp-testing', label: 'MVP Testing', description: 'Test with minimal product' },
      { value: 'landing-page', label: 'Landing Page Test', description: 'Measure interest/signups' }
    ],
    helpText: 'Choose methods that will give you reliable data about your target customers.'
  }
]

const stakeholderMappingQuestions = [
  {
    id: 'stakeholder-ecosystem',
    question: 'Map your stakeholder ecosystem',
    description: 'Identify all parties that could influence your business success',
    type: 'stakeholder-map',
    required: true,
    categories: [
      {
        id: 'customers',
        label: 'Customers & Users',
        description: 'Who will use and pay for your solution?',
        placeholder: 'End users, decision makers, influencers...'
      },
      {
        id: 'suppliers',
        label: 'Suppliers & Partners',
        description: 'Who will you depend on for resources or capabilities?',
        placeholder: 'Vendors, technology partners, distributors...'
      },
      {
        id: 'regulators',
        label: 'Regulators & Government',
        description: 'What regulatory bodies or government agencies matter?',
        placeholder: 'Industry regulators, local government, licensing bodies...'
      },
      {
        id: 'community',
        label: 'Community & Society',
        description: 'What communities or social groups are affected?',
        placeholder: 'Local community, industry associations, advocacy groups...'
      },
      {
        id: 'investors',
        label: 'Investors & Financiers',
        description: 'Who might provide funding or financial support?',
        placeholder: 'Angel investors, VCs, banks, grants...'
      }
    ],
    helpText: 'Consider both positive and negative stakeholders. Understanding all parties helps you build better relationships and avoid conflicts.'
  }
]

const problemClassificationQuestions = [
  {
    id: 'problem-type',
    question: 'What type of problem are you primarily solving?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'technical', label: 'Technical Problem', description: 'Clear solution exists, needs implementation' },
      { value: 'adaptive', label: 'Adaptive Challenge', description: 'No clear solution, requires learning and experimentation' },
      { value: 'hybrid', label: 'Hybrid Problem', description: 'Mix of technical and adaptive elements' }
    ],
    helpText: 'Technical problems have known solutions. Adaptive challenges require innovation and learning.'
  },
  {
    id: 'problem-urgency',
    question: 'How urgent is this problem for your customers?',
    type: 'scale',
    required: true,
    scaleRange: { min: 1, max: 10 },
    scaleLabels: { min: 'Nice to Have', max: 'Critical/Urgent' },
    helpText: 'Higher urgency typically means customers are more willing to pay and adopt quickly.'
  },
  {
    id: 'problem-frequency',
    question: 'How frequently do customers experience this problem?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'daily', label: 'Daily', description: 'Multiple times per day or every day' },
      { value: 'weekly', label: 'Weekly', description: 'Several times per week' },
      { value: 'monthly', label: 'Monthly', description: 'Several times per month' },
      { value: 'quarterly', label: 'Quarterly', description: 'A few times per year' },
      { value: 'rare', label: 'Rarely', description: 'Once a year or less' }
    ],
    helpText: 'More frequent problems typically create stronger demand for solutions.'
  }
]

const marketValidationQuestions = [
  {
    id: 'validation-methods',
    question: 'What methods will you use to validate market demand?',
    type: 'textarea',
    required: true,
    placeholder: 'Describe your validation approach: surveys, interviews, pre-orders, pilot programs...',
    helpText: 'Plan specific, measurable ways to test if customers actually want your solution.'
  },
  {
    id: 'success-metrics',
    question: 'What metrics will indicate successful market validation?',
    type: 'textarea',
    required: true,
    placeholder: 'Define specific numbers: X% interest rate, Y pre-orders, Z positive interviews...',
    helpText: 'Set clear, measurable criteria for what constitutes validation success.'
  },
  {
    id: 'validation-timeline',
    question: 'What is your timeline for market validation?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: '1-month', label: '1 Month', description: 'Quick validation with existing resources' },
      { value: '3-months', label: '3 Months', description: 'Thorough validation with some investment' },
      { value: '6-months', label: '6 Months', description: 'Comprehensive validation including pilot' },
      { value: '12-months', label: '12+ Months', description: 'Extended validation with full testing' }
    ],
    helpText: 'Balance thoroughness with speed to market. Longer validation reduces risk but delays launch.'
  }
]

export default MarketResearchTools
