import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import AssessmentShell from './AssessmentShell'
import { Users, Star, Building2, Calculator, Settings, Rocket, FileText, CheckCircle2, ArrowRight, Edit3, Loader2, AlertTriangle } from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'
import apiService from '../../services/api'

const BusinessPillarsPlanning = () => {
  const navigate = useNavigate()
  const {
    assessmentData,
    updateResponse,
    updateProgress,
  } = useAssessment()

  const [currentSection, setCurrentSection] = useState('customer-segmentation')
  const [sectionProgress, setSectionProgress] = useState({})
  const [blueprint, setBlueprint] = useState(null)   // set → show result screen
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')

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

  // On mount: load existing blueprint if phase was already submitted
  useEffect(() => {
    apiService.request('/v1/phase4/blueprint').then(res => {
      if (res.success && res.data?.blueprint) setBlueprint(res.data.blueprint)
    }).catch(() => {})
  }, [])

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

    // Sync section responses to Phase 4 API (fire-and-forget, don't block UI)
    const allResponses = { ...responses, [sectionId]: updated }
    apiService.request('/v1/phase4/pillars', {
      method: 'PATCH',
      body: JSON.stringify({
        section_responses: allResponses,
        ...mapSectionsToPillars(allResponses),
      }),
    }).catch(() => {}) // silent fail — AssessmentContext handles primary persistence
  }

  // Map section question answers to Phase 4 pillar keys for the backend
  function mapSectionsToPillars(r) {
    const vp = r['value-proposition'] || {}
    const bm = r['business-model'] || {}
    const fp = r['financial-planning'] || {}
    const ops = r['operational-strategy'] || {}
    const gtm = r['go-to-market'] || {}
    const cs = r['customer-segmentation'] || {}

    const pillars = {}
    const vp_canvas = vp['value-proposition-canvas'] || vp['unique-selling-proposition'] || ''
    if (vp_canvas) pillars['value_proposition'] = vp_canvas

    const seg = cs['target-segments'] ? JSON.stringify(cs['target-segments']) : cs['segment-priority'] || ''
    if (seg) pillars['customer_structure'] = seg

    if (bm['revenue-model']) pillars['revenue_model'] = String(bm['revenue-model'])
    if (bm['business-model-canvas']) pillars['operations'] = bm['business-model-canvas']

    const costs = fp['financial-projections'] || ''
    if (costs) pillars['cost_structure'] = costs

    const ops_text = ops['key-resources']
      ? `Resources: ${JSON.stringify(ops['key-resources'])}\nPartnerships: ${ops['key-partnerships'] || ''}`
      : ops['key-partnerships'] || ''
    if (ops_text) pillars['delivery_model'] = ops_text

    const positioning = gtm['customer-acquisition'] || gtm['marketing-channels'] || ''
    if (positioning) pillars['market_positioning'] = String(positioning)

    return pillars
  }

  // Show Blueprint result screen after successful submit
  if (blueprint) {
    return <BlueprintScreen blueprint={blueprint} onContinue={() => navigate('/assessment/product-concept')} />
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
      completed={Boolean(businessPillarsData?.completed)}
      onNext={async () => {
        setSubmitting(true)
        setSubmitError('')
        try {
          const res = await apiService.request('/v1/phase4/submit', { method: 'POST', body: '{}' })
          setBlueprint(res.data?.blueprint || {})
        } catch (err) {
          setSubmitError(err.message || 'Failed to generate blueprint — try again')
        } finally {
          setSubmitting(false)
        }
      }}
      nextLabel={submitting ? 'Generating Blueprint…' : 'Generate Business Pillars Blueprint'}
    >
      {/* Completion view shown when user reaches the "Business Plan Summary" section */}
      <div className="flex flex-col items-center gap-6 py-8 text-center">
        <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
          <CheckCircle2 className="h-8 w-8 text-emerald-400" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white mb-2">Business Pillars Defined</h2>
          <p className="text-sm text-gray-400 max-w-md">
            All 6 sections complete. Your venture architecture is ready. Click below to generate
            your Business Pillars Blueprint and move to Product Concept Testing.
          </p>
        </div>

        {submitError && (
          <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 w-full max-w-md">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {submitError}
          </div>
        )}

        {/* Section summary */}
        <div className="w-full max-w-md grid grid-cols-2 gap-2 text-left">
          {sections.filter(s => s.questions?.length > 0).map(s => {
            const progress = sectionProgress[s.id] || 0
            const Icon = s.icon
            return (
              <button
                key={s.id}
                type="button"
                onClick={() => setCurrentSection(s.id)}
                className="flex items-center gap-2 px-3 py-2 rounded-xl border border-gray-800 bg-gray-900/40 hover:bg-gray-800/60 transition-colors group"
              >
                <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 ${
                  progress >= 100 ? 'bg-emerald-500/10' : 'bg-gray-800'
                }`}>
                  <Icon className={`h-3.5 w-3.5 ${progress >= 100 ? 'text-emerald-400' : 'text-gray-500'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-gray-300 truncate">{s.title}</p>
                  <p className="text-[10px] text-gray-600">{progress >= 100 ? 'Complete' : `${progress}%`}</p>
                </div>
                <Edit3 className="h-3 w-3 text-gray-700 group-hover:text-gray-400 flex-shrink-0" />
              </button>
            )
          })}
        </div>

        <p className="text-xs text-gray-600 flex items-center gap-1.5">
          <Edit3 className="h-3 w-3" />
          Click any section above to review or update your answers
        </p>
      </div>
    </AssessmentShell>
  )
}

// ── Blueprint Result Screen ─────────────────────────────────────────────────
function BlueprintScreen({ blueprint, onContinue }) {
  const readyColor = blueprint.ready_for_concept_testing
    ? 'text-emerald-400'
    : 'text-yellow-400'
  const readyBg = blueprint.ready_for_concept_testing
    ? 'bg-emerald-500/10 border-emerald-500/20'
    : 'bg-yellow-500/10 border-yellow-500/20'

  return (
    <div className="min-h-full bg-[#0a0a0f] px-4 py-8 max-w-3xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-indigo-500/10 flex items-center justify-center">
          <Building2 className="h-4 w-4 text-indigo-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">Business Pillars Blueprint</h1>
          <p className="text-xs text-slate-400">Phase 4 complete — your venture architecture is defined</p>
        </div>
      </div>

      {/* Verdict */}
      <div className={`rounded-xl border p-5 ${readyBg}`}>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-slate-400 uppercase tracking-wider">Overall readiness</span>
          {blueprint.coherence_score != null && (
            <span className="text-xs text-slate-400">Coherence: {blueprint.coherence_score}/100</span>
          )}
        </div>
        <p className={`text-xl font-bold ${readyColor} mb-1`}>
          {blueprint.ready_for_concept_testing ? 'Ready for Concept Testing' : 'Needs Refinement'}
        </p>
        {blueprint.recommendation && (
          <p className="text-sm text-slate-300">{blueprint.recommendation}</p>
        )}
      </div>

      {/* Pillars summary */}
      {blueprint.pillars_summary && Object.keys(blueprint.pillars_summary).length > 0 && (
        <div className="rounded-xl border border-white/5 bg-white/[0.01] p-4 space-y-3">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Venture Architecture</h3>
          {Object.entries(blueprint.pillars_summary).map(([key, val]) => (
            <div key={key} className="text-sm">
              <span className="text-slate-400 capitalize">{key.replace(/_/g, ' ')}: </span>
              <span className="text-slate-200">{typeof val === 'string' ? val : JSON.stringify(val)}</span>
            </div>
          ))}
        </div>
      )}

      {/* Blockers */}
      {blueprint.blockers?.length > 0 && (
        <div className="rounded-xl border border-orange-500/10 bg-orange-500/5 p-4">
          <h3 className="text-xs font-semibold text-orange-400 uppercase tracking-wider mb-2">Issues to resolve</h3>
          <ul className="space-y-1">
            {blueprint.blockers.map((b, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <AlertTriangle className="h-3.5 w-3.5 text-orange-400 shrink-0 mt-0.5" />
                {b}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Required components */}
      {blueprint.required_components_for_phase6?.length > 0 && (
        <div className="rounded-xl border border-white/5 bg-white/[0.01] p-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">What to build next</h3>
          <ul className="space-y-1">
            {blueprint.required_components_for_phase6.map((c, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <ArrowRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                {c}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* CTA */}
      <div className="flex gap-3 pt-2">
        <button
          onClick={onContinue}
          className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          Continue to Concept Testing
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
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
