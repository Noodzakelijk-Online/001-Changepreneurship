import React, { useState, useEffect } from 'react'
import AssessmentShell from './AssessmentShell'
import { Lightbulb, Target, Star, TrendingUp, Heart, Search } from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'

const IdeaDiscoveryAssessment = () => {
  const {
    assessmentData,
    updateResponse,
    updateProgress,
    completePhase,
    updatePhase
  } = useAssessment()
  
  const [currentSection, setCurrentSection] = useState('core-alignment')
  const [sectionProgress, setSectionProgress] = useState({})
  
  const ideaDiscoveryData = assessmentData['idea_discovery'] || {}
  const responses = ideaDiscoveryData.responses || {}

  // Assessment sections configuration
  const sections = [
    {
      id: 'core-alignment',
      title: 'Core Alignment Matrix',
      description: 'Connect work you love with causes you care about',
      icon: Heart,
      duration: '15-20 minutes',
      questions: coreAlignmentQuestions
    },
    {
      id: 'skills-assessment',
      title: 'Skills & Capabilities',
      description: 'Identify your strengths and development areas',
      icon: Star,
      duration: '20-25 minutes',
      questions: skillsAssessmentQuestions
    },
    {
      id: 'problem-identification',
      title: 'Problem Discovery',
      description: 'Find problems you can solve effectively',
      icon: Search,
      duration: '25-30 minutes',
      questions: problemIdentificationQuestions
    },
    {
      id: 'market-promise',
      title: 'Market Promise',
      description: 'Define what you will deliver to customers',
      icon: Target,
      duration: '20-25 minutes',
      questions: marketPromiseQuestions
    },
    {
      id: 'opportunity-scoring',
      title: 'Opportunity Evaluation',
      description: 'Score and prioritize your business opportunities',
      icon: TrendingUp,
      duration: '15-20 minutes',
      questions: opportunityScoringQuestions
    },
    {
      id: 'results',
      title: 'Your Business Opportunities',
      description: 'Discover your top-ranked business ideas',
      icon: Lightbulb,
      duration: '5 minutes',
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
    updateProgress('idea_discovery', overallProgress)
    
    // Complete phase if all sections are done
    if (overallProgress >= 100 && !ideaDiscoveryData.completed) {
      completePhase('idea_discovery')
    }
  }, [responses])

  const handleResponse = (sectionId, questionId, answer) => {
    updateResponse('idea_discovery', questionId, answer, sectionId)
    const section = sections.find(s => s.id === sectionId)
    const total = section?.questions?.length || 1
    const updated = { ...(responses[sectionId] || {}), [questionId]: answer }
    const progress = Math.round((Object.keys(updated).length / total) * 100)
    setSectionProgress(prev => ({ ...prev, [sectionId]: progress }))
  }

  return (
    <AssessmentShell
      phaseName="Idea Discovery"
      phaseNumber={2}
      sections={sections}
      currentSection={currentSection}
      onSectionChange={setCurrentSection}
      responses={responses}
      onResponse={handleResponse}
      sectionProgress={sectionProgress}
      onNext={() => completePhase('idea_discovery', () => updatePhase('market_research'))}
      nextLabel="Next Phase: Market Research"
    />
  )
}
// Question definitions
const coreAlignmentQuestions = [
  {
    id: 'passion-work-matrix',
    question: 'Rate your passion and skill level for different types of work',
    type: 'matrix',
    required: true,
    rows: [
      { id: 'creative-work', label: 'Creative Work (Design, Writing, Art)' },
      { id: 'analytical-work', label: 'Analytical Work (Data, Research, Strategy)' },
      { id: 'technical-work', label: 'Technical Work (Programming, Engineering)' },
      { id: 'people-work', label: 'People Work (Sales, HR, Consulting)' },
      { id: 'operational-work', label: 'Operational Work (Management, Logistics)' }
    ],
    columns: [
      { id: 'passion', label: 'Passion Level' },
      { id: 'skill', label: 'Current Skill' },
      { id: 'potential', label: 'Growth Potential' }
    ],
    helpText: 'Rate each area from 1 (low) to 5 (high). This helps identify your sweet spot for business opportunities.'
  },
  {
    id: 'cause-alignment',
    question: 'Which causes or missions resonate most strongly with you?',
    type: 'ranking',
    required: true,
    options: [
      { value: 'environmental', label: 'Environmental Sustainability' },
      { value: 'education', label: 'Education & Learning' },
      { value: 'healthcare', label: 'Health & Wellness' },
      { value: 'social-justice', label: 'Social Justice & Equality' },
      { value: 'economic-empowerment', label: 'Economic Empowerment' },
      { value: 'technology-innovation', label: 'Technology Innovation' },
      { value: 'community-building', label: 'Community Building' },
      { value: 'personal-development', label: 'Personal Development' }
    ],
    helpText: 'Rank these causes in order of personal importance. Businesses aligned with your values are more sustainable.'
  }
]

const skillsAssessmentQuestions = [
  {
    id: 'current-skills',
    question: 'Rate your current proficiency in key business skills',
    type: 'matrix',
    required: true,
    rows: [
      { id: 'leadership', label: 'Leadership & Team Management' },
      { id: 'sales-marketing', label: 'Sales & Marketing' },
      { id: 'financial-management', label: 'Financial Management' },
      { id: 'product-development', label: 'Product Development' },
      { id: 'operations', label: 'Operations & Process Management' },
      { id: 'strategic-thinking', label: 'Strategic Thinking' },
      { id: 'communication', label: 'Communication & Presentation' },
      { id: 'problem-solving', label: 'Problem Solving & Innovation' }
    ],
    columns: [
      { id: 'current', label: 'Current Level' },
      { id: 'importance', label: 'Importance for Goals' },
      { id: 'willingness', label: 'Willingness to Develop' }
    ],
    helpText: 'Be honest about your current abilities. This assessment helps identify development priorities.'
  }
]

const problemIdentificationQuestions = [
  {
    id: 'problem-experiences',
    question: 'Describe 3 significant problems you have personally experienced',
    type: 'textarea',
    required: true,
    placeholder: 'Think about frustrations in your daily life, work, or community. What problems do you wish someone would solve?',
    helpText: 'The best business opportunities often come from solving problems you understand deeply.'
  },
  {
    id: 'problem-observation',
    question: 'What problems do you frequently observe others struggling with?',
    type: 'textarea',
    required: true,
    placeholder: 'Consider problems in your industry, community, or social circles...',
    helpText: 'External observation can reveal market opportunities you might not have considered.'
  }
]

const marketPromiseQuestions = [
  {
    id: 'value-proposition',
    question: 'If you started a business today, what unique value would you provide?',
    type: 'textarea',
    required: true,
    placeholder: 'What would make customers choose you over alternatives?',
    helpText: 'Think about your unique combination of skills, experience, and perspective.'
  },
  {
    id: 'target-customer',
    question: 'Who would be your ideal first customers?',
    type: 'textarea',
    required: true,
    placeholder: 'Be specific about demographics, needs, and characteristics...',
    helpText: 'Narrow focus on early customers helps validate and refine your business concept.'
  }
]

const opportunityScoringQuestions = [
  {
    id: 'opportunity-criteria',
    question: 'Rate the importance of these factors for your ideal business opportunity',
    type: 'scale',
    required: true,
    scaleRange: { min: 1, max: 10 },
    scaleLabels: { min: 'Not Important', max: 'Extremely Important' },
    helpText: 'This helps weight your opportunity scores based on your personal priorities.'
  }
]

export default IdeaDiscoveryAssessment
