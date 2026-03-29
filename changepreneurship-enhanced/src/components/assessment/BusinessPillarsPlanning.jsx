import React, { useState, useEffect } from 'react'
import AssessmentShell from './AssessmentShell'
import { Users, Star, Building2, Calculator, Settings, Rocket, FileText } from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'

const BusinessPillarsPlanning = () => {
  const {
    assessmentData,
    updateResponse,
    updateProgress,
    completePhase,
    updatePhase
  } = useAssessment()
  
  const [currentSection, setCurrentSection] = useState('customer-segmentation')
  const [sectionProgress, setSectionProgress] = useState({})
  
  const businessPillarsData = assessmentData['business_pillars'] || {}
  const responses = businessPillarsData.responses || {}

  // Assessment sections configuration
  const sections = [
    {
      id: 'customer-segmentation',
      title: 'Customer Segmentation',
      description: 'Define and prioritize your target customer segments',
      icon: Users,
      duration: '45-60 minutes',
      questions: customerSegmentationQuestions
    },
    {
      id: 'value-proposition',
      title: 'Value Proposition',
      description: 'Craft compelling value propositions for each segment',
      icon: Star,
      duration: '30-45 minutes',
      questions: valuePropositionQuestions
    },
    {
      id: 'business-model',
      title: 'Business Model',
      description: 'Design your revenue streams and cost structure',
      icon: Building2,
      duration: '60-90 minutes',
      questions: businessModelQuestions
    },
    {
      id: 'financial-planning',
      title: 'Financial Planning',
      description: 'Project revenues, costs, and funding requirements',
      icon: Calculator,
      duration: '90-120 minutes',
      questions: financialPlanningQuestions
    },
    {
      id: 'operational-strategy',
      title: 'Operations Strategy',
      description: 'Plan your key activities, resources, and partnerships',
      icon: Settings,
      duration: '60-75 minutes',
      questions: operationalStrategyQuestions
    },
    {
      id: 'go-to-market',
      title: 'Go-to-Market Strategy',
      description: 'Plan your launch and customer acquisition strategy',
      icon: Rocket,
      duration: '45-60 minutes',
      questions: goToMarketQuestions
    },
    {
      id: 'business-plan',
      title: 'Business Plan Summary',
      description: 'Your comprehensive business plan overview',
      icon: FileText,
      duration: '15 minutes',
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
    updateProgress('business_pillars', overallProgress)
    
    // Complete phase if all sections are done
    if (overallProgress >= 100 && !businessPillarsData.completed) {
      completePhase('business_pillars')
    }
  }, [responses])

  const handleResponse = (sectionId, questionId, answer) => {
    updateResponse('business_pillars', questionId, answer, sectionId)
    const section = sections.find(s => s.id === sectionId)
    const total = section?.questions?.length || 1
    const updated = { ...(responses[sectionId] || {}), [questionId]: answer }
    const progress = Math.round((Object.keys(updated).length / total) * 100)
    setSectionProgress(prev => ({ ...prev, [sectionId]: progress }))
  }

  return (
    <AssessmentShell
      phaseName="Business Pillars"
      phaseNumber={4}
      sections={sections}
      currentSection={currentSection}
      onSectionChange={setCurrentSection}
      responses={responses}
      onResponse={handleResponse}
      sectionProgress={sectionProgress}
      onNext={() => { completePhase('business_pillars'); updatePhase('product_concept_testing') }}
      nextLabel="Next Phase: Product Concept Testing"
    />
  )
}
// Question definitions
const customerSegmentationQuestions = [
  {
    id: 'target-segments',
    question: 'Define your primary customer segments',
    description: 'Identify and describe the different groups of customers you plan to serve',
    type: 'customer-segments',
    required: true,
    maxSegments: 3,
    helpText: 'Focus on 2-3 segments maximum. Quality over quantity - it\'s better to serve fewer segments well.'
  },
  {
    id: 'segment-priority',
    question: 'Which customer segment will you focus on first, and why?',
    type: 'textarea',
    required: true,
    placeholder: 'Describe the segment you will target first, why it is your top priority, and how accessible they are...',
    helpText: 'Your first segment should have the highest combination of need, willingness to pay, and accessibility.'
  }
]

const valuePropositionQuestions = [
  {
    id: 'value-proposition-canvas',
    question: 'Create your value proposition canvas',
    description: 'Map how your products and services create value for customers',
    type: 'textarea',
    required: true,
    placeholder: 'Products & Services: (what you offer)\n\nGain Creators: (how you create gains for customers)\n\nPain Relievers: (how you relieve customer pains)\n\nCustomer Jobs: (what customers are trying to get done)\n\nCustomer Gains: (outcomes and benefits they want)\n\nCustomer Pains: (frustrations, obstacles, risks they face)',
    helpText: 'Focus on the fit between what customers want and what you offer. Be specific and concrete.'
  },
  {
    id: 'unique-selling-proposition',
    question: 'What is your unique selling proposition (USP)?',
    type: 'textarea',
    required: true,
    placeholder: 'In one clear sentence, what makes you uniquely valuable to customers?',
    helpText: 'Your USP should be clear, specific, and differentiate you from competitors.'
  }
]

const businessModelQuestions = [
  {
    id: 'business-model-canvas',
    question: 'Complete your business model canvas',
    description: 'Design the key components of your business model',
    type: 'textarea',
    required: true,
    placeholder: 'Key Partners: (who you rely on)\n\nKey Activities: (what you do to deliver value)\n\nKey Resources: (assets you need)\n\nValue Propositions: (what you offer each segment)\n\nCustomer Relationships: (how you interact with customers)\n\nChannels: (how you reach customers)\n\nCost Structure: (your main costs)\n\nRevenue Streams: (how you make money)',
    helpText: 'Think about how all the pieces fit together to create and deliver value profitably.'
  },
  {
    id: 'revenue-model',
    question: 'What is your primary revenue model?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'subscription', label: 'Subscription', description: 'Recurring monthly/annual fees' },
      { value: 'transaction', label: 'Transaction-based', description: 'Fee per transaction or sale' },
      { value: 'product-sales', label: 'Product Sales', description: 'One-time product purchases' },
      { value: 'service-fees', label: 'Service Fees', description: 'Fees for professional services' },
      { value: 'advertising', label: 'Advertising', description: 'Revenue from ads or sponsorships' },
      { value: 'freemium', label: 'Freemium', description: 'Free basic, paid premium features' }
    ],
    helpText: 'Choose the model that best aligns with your value proposition and customer preferences.'
  }
]

const financialPlanningQuestions = [
  {
    id: 'financial-projections',
    question: 'Create your financial projections',
    description: 'Project your revenues, costs, and funding requirements',
    type: 'textarea',
    required: true,
    placeholder: 'Year 1 Revenue: €\nYear 1 Costs: €\nYear 1 Net: €\n\nYear 2 Revenue: €\nYear 2 Costs: €\nYear 2 Net: €\n\nYear 3 Revenue: €\nYear 3 Costs: €\nYear 3 Net: €\n\nKey assumptions and notes:',
    helpText: 'Be realistic but optimistic. Base projections on market research and comparable businesses.'
  },
  {
    id: 'funding-strategy',
    question: 'How do you plan to fund your business?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'bootstrap', label: 'Bootstrap', description: 'Self-funded from personal savings' },
      { value: 'friends-family', label: 'Friends & Family', description: 'Funding from personal network' },
      { value: 'angel-investors', label: 'Angel Investors', description: 'Individual investor funding' },
      { value: 'venture-capital', label: 'Venture Capital', description: 'Professional VC funding' },
      { value: 'bank-loan', label: 'Bank Loan', description: 'Traditional debt financing' },
      { value: 'crowdfunding', label: 'Crowdfunding', description: 'Platform-based funding' }
    ],
    helpText: 'Consider your funding needs, timeline, and willingness to give up equity.'
  }
]

const operationalStrategyQuestions = [
  {
    id: 'key-resources',
    question: 'What are your key resources and capabilities?',
    type: 'resource-planning',
    required: true,
    categories: [
      {
        id: 'human-resources',
        label: 'Human Resources',
        description: 'Key team members and skills needed',
        placeholder: 'Founders, employees, advisors, consultants...'
      },
      {
        id: 'physical-resources',
        label: 'Physical Resources',
        description: 'Equipment, facilities, and physical assets',
        placeholder: 'Office space, equipment, inventory, manufacturing...'
      },
      {
        id: 'intellectual-resources',
        label: 'Intellectual Resources',
        description: 'IP, data, and knowledge assets',
        placeholder: 'Patents, trademarks, proprietary data, algorithms...'
      },
      {
        id: 'financial-resources',
        label: 'Financial Resources',
        description: 'Capital and financial assets needed',
        placeholder: 'Startup capital, working capital, credit lines...'
      }
    ],
    helpText: 'Focus on the resources that are most critical to your value proposition and competitive advantage.'
  },
  {
    id: 'key-partnerships',
    question: 'What key partnerships will you need?',
    type: 'textarea',
    required: true,
    placeholder: 'Describe strategic partnerships, suppliers, distributors, or other key relationships...',
    helpText: 'Think about partnerships that can help you access resources, capabilities, or markets more effectively.'
  }
]

const goToMarketQuestions = [
  {
    id: 'customer-acquisition',
    question: 'How will you acquire your first customers?',
    type: 'textarea',
    required: true,
    placeholder: 'Describe your customer acquisition strategy and tactics...',
    helpText: 'Be specific about channels, tactics, and how you\'ll measure success.'
  },
  {
    id: 'marketing-channels',
    question: 'What marketing channels will you use?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'digital-marketing', label: 'Digital Marketing', description: 'SEO, SEM, social media, content' },
      { value: 'direct-sales', label: 'Direct Sales', description: 'Personal selling and relationship building' },
      { value: 'partnerships', label: 'Channel Partners', description: 'Resellers, distributors, affiliates' },
      { value: 'referrals', label: 'Referral Program', description: 'Word-of-mouth and customer referrals' },
      { value: 'events', label: 'Events & Trade Shows', description: 'Industry events and networking' },
      { value: 'pr-media', label: 'PR & Media', description: 'Public relations and media coverage' }
    ],
    helpText: 'Choose channels where your target customers are most active and receptive.'
  },
  {
    id: 'launch-timeline',
    question: 'What is your launch timeline?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: '3-months', label: '3 Months', description: 'Quick launch with MVP' },
      { value: '6-months', label: '6 Months', description: 'Moderate development timeline' },
      { value: '12-months', label: '12 Months', description: 'Comprehensive product development' },
      { value: '18-months', label: '18+ Months', description: 'Complex product or regulatory requirements' }
    ],
    helpText: 'Balance speed to market with product readiness and market preparation.'
  }
]

export default BusinessPillarsPlanning
