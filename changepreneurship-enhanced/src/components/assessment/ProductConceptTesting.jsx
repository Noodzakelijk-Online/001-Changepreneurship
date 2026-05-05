import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import AssessmentShell from './AssessmentShell'
import {
  Lightbulb, Users, ClipboardList, BarChart2,
  CheckCircle2, Edit3, ArrowRight, Loader2, AlertTriangle,
} from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'
import apiService from '../../services/api'
import {
  PCT_SECTION_CONCEPT_DESIGN,
  PCT_SECTION_TEST_METHODS,
  PCT_SECTION_FEEDBACK_DATA,
  PCT_SECTION_EVIDENCE_REVIEW,
} from './ComprehensiveQuestionBank.jsx'

const SECTIONS = [
  {
    id: 'concept-design',
    title: 'Concept Design',
    description: 'Define what you are testing and who you are testing with',
    icon: Lightbulb,
    questions: PCT_SECTION_CONCEPT_DESIGN,
  },
  {
    id: 'test-methods',
    title: 'Test Methods',
    description: 'How you conducted the concept test',
    icon: Users,
    questions: PCT_SECTION_TEST_METHODS,
  },
  {
    id: 'feedback-data',
    title: 'Feedback & Data',
    description: 'What you heard and what happened',
    icon: ClipboardList,
    questions: PCT_SECTION_FEEDBACK_DATA,
  },
  {
    id: 'evidence-review',
    title: 'Evidence Review',
    description: 'Assess the strength of your evidence and next steps',
    icon: BarChart2,
    questions: PCT_SECTION_EVIDENCE_REVIEW,
  },
  {
    id: 'test-result',
    title: 'Test Result',
    description: 'Your Product Concept Test Result',
    icon: CheckCircle2,
    questions: [],
  },
]

const SECTION_IDS_ACTIVE = SECTIONS.filter(s => s.questions.length > 0).map(s => s.id)

const ProductConceptTesting = () => {
  const navigate = useNavigate()
  const { assessmentData, updateResponse, updateProgress } = useAssessment()

  const [currentSection, setCurrentSection] = useState(SECTION_IDS_ACTIVE[0])
  const [sectionProgress, setSectionProgress] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [result, setResult] = useState(null)

  const phaseData  = assessmentData['product_concept_testing'] || {}
  const responses  = phaseData.responses || {}

  // ── Progress calculation ───────────────────────────────────────────────

  const calcSectionProgress = (sectionId) => {
    const section = SECTIONS.find(s => s.id === sectionId)
    if (!section || !section.questions.length) return 0
    const sectionResponses = responses[sectionId] || {}
    const answered = Object.keys(sectionResponses).length
    return Math.round((answered / section.questions.length) * 100)
  }

  const calcOverall = () => {
    const total = SECTION_IDS_ACTIVE.length
    const done  = SECTION_IDS_ACTIVE.filter(id => calcSectionProgress(id) >= 100).length
    return Math.round((done / total) * 100)
  }

  // On mount: load existing result if phase was already submitted
  useEffect(() => {
    apiService.request('/v1/phase5/result').then(res => {
      if (res.success && res.data?.adoption_signal) setResult(res.data)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    const progress = {}
    SECTION_IDS_ACTIVE.forEach(id => { progress[id] = calcSectionProgress(id) })
    setSectionProgress(progress)
    updateProgress('product_concept_testing', calcOverall())
  }, [phaseData])

  // ── Handlers ──────────────────────────────────────────────────────────

  const handleResponse = (sectionId, questionId, answer) => {
    updateResponse('product_concept_testing', questionId, answer, sectionId)
    const section = SECTIONS.find(s => s.id === sectionId)
    const total = section?.questions?.length || 1
    const updated = { ...(responses[sectionId] || {}), [questionId]: answer }
    const pct = Math.round((Object.keys(updated).length / total) * 100)
    setSectionProgress(prev => ({ ...prev, [sectionId]: pct }))

    // Sync flat responses to Phase 5 API (fire-and-forget)
    const flatResponses = _flatten({ ...responses, [sectionId]: updated })
    apiService.request('/v1/phase5/concept-tests', {
      method: 'PATCH',
      body: JSON.stringify({ responses: flatResponses }),
    }).catch(() => {})
  }

  const isResultsSection = currentSection === 'test-result'
  const allSectionsDone  = SECTION_IDS_ACTIVE.every(id =>
    (sectionProgress[id] ?? 0) >= 100
  )

  if (result) {
    const isReady = result.ready_for_business_dev
    return (
      <div className="min-h-full bg-[#0a0a0f] px-4 py-8 max-w-3xl mx-auto space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-indigo-500/10 flex items-center justify-center">
            <BarChart2 className="h-4 w-4 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Product Concept Test Result</h1>
            <p className="text-xs text-slate-400">Phase 5 complete</p>
          </div>
        </div>
        <div className={`rounded-xl border p-5 ${isReady ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-yellow-500/10 border-yellow-500/20'}`}>
          <p className={`text-xl font-bold mb-1 ${isReady ? 'text-emerald-400' : 'text-yellow-400'}`}>
            {isReady ? 'Ready for Business Development' : 'Needs Revision'}
          </p>
          <p className="text-sm text-slate-400">Adoption signal: {result.adoption_signal} · Decision: {result.decision}</p>
          {result.summary && <p className="text-sm text-slate-300 mt-2">{result.summary}</p>}
        </div>
        {result.blockers?.length > 0 && (
          <div className="rounded-xl border border-orange-500/10 bg-orange-500/5 p-4">
            <h3 className="text-xs font-semibold text-orange-400 uppercase tracking-wider mb-2">Issues to resolve</h3>
            <ul className="space-y-1">{result.blockers.map((b, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <AlertTriangle className="h-3.5 w-3.5 text-orange-400 shrink-0 mt-0.5" />{b}
              </li>
            ))}</ul>
          </div>
        )}
        <button
          onClick={() => navigate('/assessment/business-development')}
          className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          Continue to Business Development <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    )
  }

  return (
    <AssessmentShell
      phaseName="Product Concept Testing"
      phaseNumber={5}
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
          const res = await apiService.request('/v1/phase5/submit', { method: 'POST', body: '{}' })
          setResult(res.data || {})
        } catch (err) {
          setSubmitError(err.message || 'Failed to generate result — try again')
        } finally {
          setSubmitting(false)
        }
      }}
      nextLabel={submitting ? 'Generating Result…' : 'Generate Concept Test Result'}
    >
      {/* Completion view — shown when user lands on the test-result section */}
      <div className="flex flex-col items-center gap-6 py-8 text-center">
        <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
          <CheckCircle2 className="h-8 w-8 text-emerald-400" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white mb-2">Concept Testing Complete</h2>
          <p className="text-sm text-gray-400 max-w-md">
            All 4 sections answered. Click below to generate your Product Concept Test Result
            and move to Business Development.
          </p>
        </div>
        {submitError && (
          <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 w-full max-w-lg">
            <AlertTriangle className="h-4 w-4 shrink-0" />{submitError}
          </div>
        )}

        {/* Section review grid */}
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

// Flatten section-keyed responses to flat question_id → answer dict
function _flatten(sectioned) {
  const flat = {}
  Object.values(sectioned).forEach(sectionAnswers => {
    if (sectionAnswers && typeof sectionAnswers === 'object') {
      Object.assign(flat, sectionAnswers)
    }
  })
  return flat
}

export default ProductConceptTesting
