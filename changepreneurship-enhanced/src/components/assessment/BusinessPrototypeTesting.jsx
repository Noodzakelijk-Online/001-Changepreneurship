import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import AssessmentShell from './AssessmentShell'
import {
  TrendingUp, Users, Truck, DollarSign, Star, Zap,
  CheckCircle2, Edit3, ArrowRight, AlertTriangle,
} from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'
import apiService from '../../services/api'
import {
  PT_SECTION_TRACTION,
  PT_SECTION_CONVERSION,
  PT_SECTION_DELIVERY,
  PT_SECTION_FINANCIAL,
  PT_SECTION_CUSTOMER,
  PT_SECTION_FOUNDER,
} from './ComprehensiveQuestionBank.jsx'

const SECTIONS = [
  {
    id: 'traction-evidence',
    title: 'Traction Evidence',
    description: 'What real-world validation have you achieved?',
    icon: TrendingUp,
    questions: PT_SECTION_TRACTION,
  },
  {
    id: 'conversion-sales',
    title: 'Conversion & Sales',
    description: 'Outreach efforts and conversion rates',
    icon: Users,
    questions: PT_SECTION_CONVERSION,
  },
  {
    id: 'delivery-operations',
    title: 'Delivery & Operations',
    description: 'How well you delivered and what broke',
    icon: Truck,
    questions: PT_SECTION_DELIVERY,
  },
  {
    id: 'financial-reality',
    title: 'Financial Reality',
    description: 'Revenue and cost vs. plan',
    icon: DollarSign,
    questions: PT_SECTION_FINANCIAL,
  },
  {
    id: 'customer-response',
    title: 'Customer Response',
    description: 'Satisfaction, retention, and referrals',
    icon: Star,
    questions: PT_SECTION_CUSTOMER,
  },
  {
    id: 'founder-performance',
    title: 'Founder Performance',
    description: 'Execution follow-through and adaptability',
    icon: Zap,
    questions: PT_SECTION_FOUNDER,
  },
  {
    id: 'test-result',
    title: 'Prototype Test Report',
    description: 'Your Business Prototype Test Report',
    icon: CheckCircle2,
    questions: [],
  },
]

const SECTION_IDS_ACTIVE = SECTIONS.filter(s => s.questions.length > 0).map(s => s.id)

const BusinessPrototypeTesting = () => {
  const navigate = useNavigate()
  const { assessmentData, updateResponse, updateProgress } = useAssessment()

  const [currentSection, setCurrentSection] = useState(SECTION_IDS_ACTIVE[0])
  const [sectionProgress, setSectionProgress] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [report, setReport] = useState(null)

  const phaseData = assessmentData['business_prototype_testing'] || {}
  const responses = phaseData.responses || {}

  const calcSectionProgress = (sectionId) => {
    const section = SECTIONS.find(s => s.id === sectionId)
    if (!section || !section.questions.length) return 0
    const answered = Object.keys(responses[sectionId] || {}).length
    return Math.round((answered / section.questions.length) * 100)
  }

  const calcOverall = () => {
    const done = SECTION_IDS_ACTIVE.filter(id => calcSectionProgress(id) >= 100).length
    return Math.round((done / SECTION_IDS_ACTIVE.length) * 100)
  }

  useEffect(() => {
    const progress = {}
    SECTION_IDS_ACTIVE.forEach(id => { progress[id] = calcSectionProgress(id) })
    setSectionProgress(progress)
    updateProgress('business_prototype_testing', calcOverall())
  }, [phaseData])

  // On mount: load existing report if phase was already submitted
  useEffect(() => {
    apiService.request('/v1/phase7/report').then(res => {
      if (res.success && res.data?.report?.decision) setReport(res.data.report)
    }).catch(() => {})
  }, [])

  const handleResponse = (sectionId, questionId, answer) => {
    updateResponse('business_prototype_testing', questionId, answer, sectionId)
    const section = SECTIONS.find(s => s.id === sectionId)
    const total = section?.questions?.length || 1
    const updated = { ...(responses[sectionId] || {}), [questionId]: answer }
    setSectionProgress(prev => ({
      ...prev,
      [sectionId]: Math.round((Object.keys(updated).length / total) * 100),
    }))

    // Sync to Phase 7 API (fire-and-forget)
    const flatResponses = _flatten({ ...responses, [sectionId]: updated })
    apiService.request('/v1/phase7/prototype-test', {
      method: 'PATCH',
      body: JSON.stringify({ responses: flatResponses }),
    }).catch(() => {})
  }

  if (report) {
    const data = report.report_data || report
    const isReady = data.ready_to_scale || report.ready_to_scale
    return (
      <div className="min-h-full bg-[#0a0a0f] px-4 py-8 max-w-3xl mx-auto space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-indigo-500/10 flex items-center justify-center">
            <TrendingUp className="h-4 w-4 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Business Prototype Test Report</h1>
            <p className="text-xs text-slate-400">Phase 7 complete</p>
          </div>
        </div>
        <div className={`rounded-xl border p-5 ${isReady ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-yellow-500/10 border-yellow-500/20'}`}>
          <p className={`text-xl font-bold mb-1 ${isReady ? 'text-emerald-400' : 'text-yellow-400'}`}>
            {isReady ? 'Ready to Scale' : 'More Iteration Needed'}
          </p>
          <p className="text-sm text-slate-400">
            Scale readiness: {data.scale_readiness || report.scale_readiness} · Score: {data.scale_score ?? report.scale_score}
          </p>
          {data.summary && <p className="text-sm text-slate-300 mt-2">{data.summary}</p>}
        </div>
        {data.blockers?.length > 0 && (
          <div className="rounded-xl border border-orange-500/10 bg-orange-500/5 p-4">
            <h3 className="text-xs font-semibold text-orange-400 uppercase tracking-wider mb-2">Issues to resolve</h3>
            <ul className="space-y-1">{data.blockers.map((b, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <AlertTriangle className="h-3.5 w-3.5 text-orange-400 shrink-0 mt-0.5" />{b}
              </li>
            ))}</ul>
          </div>
        )}
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          View Dashboard <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    )
  }

  return (
    <AssessmentShell
      phaseName="Business Prototype Testing"
      phaseNumber={7}
      sections={SECTIONS}
      currentSection={currentSection}
      onSectionChange={setCurrentSection}
      responses={responses}
      onResponse={handleResponse}
      sectionProgress={sectionProgress}
      completed={Boolean(phaseData.completed)}
      onNext={async () => {
        setSubmitting(true)
        setSubmitError('')
        try {
          const res = await apiService.request('/v1/phase7/submit', { method: 'POST', body: '{}' })
          setReport(res.data?.report || res.data || {})
        } catch (err) {
          setSubmitError(err.message || 'Failed to generate report — try again')
        } finally {
          setSubmitting(false)
        }
      }}
      nextLabel={submitting ? 'Generating Report…' : 'Generate Prototype Test Report'}
    >
      {/* Completion view */}
      <div className="flex flex-col items-center gap-6 py-8 text-center">
        <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
          <CheckCircle2 className="h-8 w-8 text-emerald-400" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white mb-2">Real-World Evidence Collected</h2>
          <p className="text-sm text-gray-400 max-w-md">
            All 6 sections complete. Click below to generate your Business Prototype Test Report
            and receive your scale readiness decision.
          </p>
        </div>
        {submitError && (
          <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 w-full max-w-lg">
            <AlertTriangle className="h-4 w-4 shrink-0" />{submitError}
          </div>
        )}
        <div className="w-full max-w-lg grid grid-cols-2 gap-3 text-left">
          {SECTION_IDS_ACTIVE.map(sectionId => {
            const section = SECTIONS.find(s => s.id === sectionId)
            const SIcon = section?.icon || CheckCircle2
            const pct = sectionProgress[sectionId] ?? 0
            const done = pct >= 100
            return (
              <button
                key={sectionId}
                onClick={() => setCurrentSection(sectionId)}
                className="flex items-center gap-3 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.05] px-4 py-3 transition-colors text-left"
              >
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${done ? 'bg-emerald-500/10' : 'bg-white/[0.04]'}`}>
                  {done
                    ? <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                    : <SIcon className="h-4 w-4 text-slate-500" />}
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-white truncate">{section?.title}</p>
                  <p className={`text-xs ${done ? 'text-emerald-400' : 'text-yellow-400'}`}>
                    {done ? 'Complete' : `${pct}%`}
                  </p>
                </div>
                <Edit3 className="h-3 w-3 text-slate-700 ml-auto flex-shrink-0" />
              </button>
            )
          })}
        </div>
        <p className="text-xs text-slate-600">Click any section to review or update your answers</p>
      </div>
    </AssessmentShell>
  )
}

function _flatten(sectioned) {
  const flat = {}
  Object.values(sectioned).forEach(s => {
    if (s && typeof s === 'object') Object.assign(flat, s)
  })
  return flat
}

export default BusinessPrototypeTesting

