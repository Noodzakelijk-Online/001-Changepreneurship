/**
 * Phase1Form — Entrepreneur Discovery
 *
 * Dark-themed multi-step form that:
 *  1. Collects venture context + founder readiness data
 *  2. POSTs to /api/v1/phase1/submit → creates FounderReadinessProfile
 *  3. Calls completePhase('self_discovery') to mark assessment done
 *  4. Shows the resulting route recommendation + readiness summary
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle, ArrowRight, ChevronRight, AlertTriangle } from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'
import apiService from '../../services/api'

// ─── Step definitions ──────────────────────────────────────────────────────────

const STEPS = [
  {
    id: 'idea',
    title: "What are you trying to build or explore?",
    description: "Describe the idea, problem, or area you are exploring. It is okay if it is still vague.",
    field: 'idea_description',
    type: 'textarea',
    placeholder: "E.g. An app to help freelancers manage invoices automatically, without needing an accountant...",
  },
  {
    id: 'motivation',
    title: "Why does this matter to you personally?",
    description: "Be honest — your reasons do not need to sound impressive.",
    field: 'motivation_raw',
    type: 'textarea',
    placeholder: "E.g. I lost my job and need income. / I genuinely believe this problem is underserved...",
  },
  {
    id: 'target_user',
    title: "Who do you think this is for?",
    description: "Describe the specific type of person you imagine using or buying this.",
    field: 'target_user_description',
    type: 'textarea',
    placeholder: "E.g. Freelance designers in their 30s who work solo and hate admin...",
  },
  {
    id: 'time',
    title: "How many hours per week can you realistically commit?",
    description: "Think about a normal week — not your best-case week.",
    field: 'weekly_available_hours',
    type: 'slider',
    min: 0,
    max: 80,
    step: 1,
    suffix: 'h',
    hint: null,
  },
  {
    id: 'financial',
    title: "Do you have financial runway?",
    description: "Roughly how many months could you cover your basic costs if this earns nothing?",
    field: 'financial_runway_months',
    type: 'slider',
    min: 0,
    max: 36,
    step: 1,
    suffix: 'mo',
    hint: "We ask this to give you honest guidance. Low runway does not stop you — it shapes which path is safest.",
    additionalFields: [
      { field: 'income_stable', label: "I have a stable income source right now", type: 'checkbox' },
    ],
  },
  {
    id: 'validation',
    title: "Have you spoken to real people who have this problem?",
    description: "This means conversations, not surveys or internet research.",
    field: 'has_spoken_to_users',
    type: 'radio',
    options: [
      { value: 'yes_multiple', label: 'Yes — I have spoken to multiple people in depth' },
      { value: 'yes_briefly', label: 'Yes — I have had some conversations' },
      { value: 'no_but_know_them', label: 'Not yet — but I know people who have this problem' },
      { value: 'no', label: 'Not yet' },
    ],
  },
  {
    id: 'legal',
    title: "Any legal or employment restrictions?",
    description: "These questions help us give you accurate guidance — not to disqualify you.",
    field: 'legal_acknowledgement',
    type: 'checklist',
    hint: "Honest answers let us guide you correctly. None of these are automatic disqualifiers, but some require legal advice first.",
    options: [
      { field: 'has_non_compete', label: 'I have a non-compete agreement with a current or former employer' },
      { field: 'employer_ip_risk', label: "I am building this using my employer's tools, time, or data" },
      { field: 'immigration_restriction', label: 'My visa or immigration status may restrict self-employment' },
      { field: 'illegal_venture', label: 'The venture involves activities that may be illegal in my country' },
    ],
  },
  {
    id: 'fears',
    title: "What are you most afraid could go wrong?",
    description: "This helps us understand your risk tolerance. There are no wrong answers.",
    field: 'primary_fear',
    type: 'textarea',
    placeholder: "E.g. Running out of money / Embarrassing myself / Not being taken seriously...",
  },
]

// ─── Inference helpers ─────────────────────────────────────────────────────────

function inferMotivationType(raw) {
  if (!raw) return 'MIXED'
  const lower = raw.toLowerCase()
  if (lower.includes('lost') || lower.includes('fired') || lower.includes('laid off')) return 'ESCAPIST'
  if (lower.includes('money') || lower.includes('income') || lower.includes('rich')) return 'FINANCIAL_ONLY'
  if (lower.includes('impact') || lower.includes('help people') || lower.includes('social')) return 'IMPACT'
  if (lower.includes('passionate') || lower.includes('love')) return 'PASSION'
  if (lower.includes('believe') || lower.includes('mission')) return 'MISSION'
  return 'MIXED'
}

function inferTargetUserSpecific(desc) {
  if (!desc) return false
  const broad = ['everyone', 'anyone', 'all people', 'everybody', 'any person', 'all businesses']
  return !broad.some(p => desc.toLowerCase().includes(p)) && desc.trim().length > 15
}

// ─── Route colours ─────────────────────────────────────────────────────────────

const ROUTE_STYLE = {
  CONTINUE: { bar: 'bg-emerald-500', badge: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' },
  PAUSE:    { bar: 'bg-yellow-500',  badge: 'bg-yellow-500/15  text-yellow-300  border-yellow-500/30'  },
  STOP:     { bar: 'bg-red-500',     badge: 'bg-red-500/15     text-red-300     border-red-500/30'     },
  PIVOT:    { bar: 'bg-orange-500',  badge: 'bg-orange-500/15  text-orange-300  border-orange-500/30'  },
}

// ─── Result screen ─────────────────────────────────────────────────────────────

function ResultScreen({ result, onContinue }) {
  const route = result?.recommended_route || 'CONTINUE'
  const style = ROUTE_STYLE[route] || ROUTE_STYLE.CONTINUE
  const matrix = result?.founder_matrix || {}
  const dims = matrix.dimensions || {}
  const recommendation = matrix.operating_recommendation || ''

  const DIM_LABELS = {
    financial_readiness: 'Financial Readiness',
    motivation_quality: 'Motivation Quality',
    time_capacity: 'Time Capacity',
    founder_market_fit: 'Founder–Market Fit',
    legal_employment: 'Legal & Employment',
  }

  const STATUS_COLORS = {
    'Strong':      'text-emerald-400',
    'Adequate':    'text-sky-400',
    'Watch':       'text-yellow-400',
    'Soft Block':  'text-orange-400',
    'Hard Block':  'text-red-400',
    'Hard Stop':   'text-red-500',
  }

  const keyDims = Object.entries(DIM_LABELS)
    .map(([k, label]) => ({ key: k, label, ...dims[k] }))
    .filter(d => d.status_label)

  return (
    <div className="max-w-2xl mx-auto px-4 py-10 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-emerald-500/10 mb-2">
          <CheckCircle className="w-8 h-8 text-emerald-400" />
        </div>
        <h1 className="text-2xl font-bold text-white">Analysis Complete</h1>
        <p className="text-gray-400 text-sm">Your founder profile has been created.</p>
      </div>

      {/* Route banner */}
      <div className={`rounded-xl border p-5 ${style.badge}`}>
        <div className="flex items-center gap-3 mb-2">
          <span className={`text-xs font-bold uppercase tracking-widest px-2 py-0.5 rounded border ${style.badge}`}>
            {route}
          </span>
          <span className="text-white font-semibold text-sm">Recommended Path</span>
        </div>
        {recommendation && (
          <p className="text-sm leading-relaxed opacity-90">{recommendation}</p>
        )}
      </div>

      {/* Dimension snapshot */}
      {keyDims.length > 0 && (
        <div className="bg-white/3 border border-white/5 rounded-xl p-5 space-y-3">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Founder Health Snapshot</h3>
          {keyDims.map(d => (
            <div key={d.key} className="flex items-center justify-between">
              <span className="text-sm text-gray-300">{d.label}</span>
              <span className={`text-xs font-medium ${STATUS_COLORS[d.status_label] || 'text-gray-400'}`}>
                {d.status_label}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Pattern tags */}
      {matrix.pattern_tags?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {matrix.pattern_tags.map((tag, i) => {
            const isWarning = /risk|constraint|watch|gap|needed/i.test(tag)
            return (
              <span
                key={i}
                className={`text-xs px-2 py-0.5 rounded-full border font-medium ${
                  isWarning
                    ? 'bg-orange-500/10 text-orange-300 border-orange-500/20'
                    : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
                }`}
              >
                {tag}
              </span>
            )
          })}
        </div>
      )}

      {/* CTA */}
      <div className="space-y-3">
        <button
          onClick={onContinue}
          className="w-full flex items-center justify-center gap-2 py-3.5 px-6 bg-cyan-500 hover:bg-cyan-400 text-black font-bold rounded-xl transition-colors text-sm"
        >
          Continue to Phase 2: Idea Discovery
          <ArrowRight className="w-4 h-4" />
        </button>
        <p className="text-center text-xs text-gray-600">Phase 2 is now unlocked in your dashboard</p>
      </div>
    </div>
  )
}

// ─── Main component ────────────────────────────────────────────────────────────

export default function Phase1Form({ onSubmitSuccess }) {
  const navigate = useNavigate()
  const { completePhase } = useAssessment()

  const [step, setStep] = useState(0)
  const [formData, setFormData] = useState({
    weekly_available_hours: 10,
    financial_runway_months: 6,
    income_stable: false,
    has_non_compete: false,
    employer_ip_risk: false,
    immigration_restriction: false,
    illegal_venture: false,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const current = STEPS[step]
  const totalSteps = STEPS.length
  const progressPct = Math.round(((step + 1) / totalSteps) * 100)

  function handleChange(field, value) {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  function canProceed() {
    if (current.type === 'textarea') {
      return (formData[current.field] || '').trim().length >= 5
    }
    if (current.type === 'radio') {
      return Boolean(formData[current.field])
    }
    return true
  }

  async function handleSubmit() {
    setLoading(true)
    setError(null)

    const payload = {
      ...formData,
      motivation_type: inferMotivationType(formData.motivation_raw),
      target_user_specific: inferTargetUserSpecific(formData.target_user_description),
      problem_defined: Boolean(formData.idea_description && formData.idea_description.trim().length > 20),
      weekly_available_hours: Number(formData.weekly_available_hours),
      financial_runway_months: Number(formData.financial_runway_months),
      income_stable: Boolean(formData.income_stable),
      has_non_compete: Boolean(formData.has_non_compete),
      employer_ip_risk: Boolean(formData.employer_ip_risk),
      immigration_restriction: Boolean(formData.immigration_restriction),
      illegal_venture: Boolean(formData.illegal_venture),
      paying_customers_exist: false,
      stress_level: 2,
      burnout_signals: [],
      life_chaos_signals: [],
      energy_level: 4,
    }

    try {
      const res = await apiService.request('/v1/phase1/submit', {
        method: 'POST',
        body: JSON.stringify(payload),
      })

      if (!res.success) {
        throw new Error(res.error || 'Server error')
      }

      const data = res.data

      // Mark assessment complete in AssessmentContext (updates sidebar + progress)
      try {
        await completePhase('self_discovery')
      } catch (_e) {
        // Non-blocking — FRP was created, assessment marking is secondary
      }

      if (onSubmitSuccess) {
        onSubmitSuccess(data)
      } else {
        setResult(data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // ── Result screen ──────────────────────────────────────────────────────────
  if (result) {
    return (
      <ResultScreen
        result={result}
        onContinue={() => navigate('/dashboard')}
      />
    )
  }

  // ── Form ───────────────────────────────────────────────────────────────────
  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Entrepreneur Discovery</h1>
        <p className="text-gray-400 text-sm">
          Answer honestly — this shapes your recommended path. Step {step + 1} of {totalSteps}.
        </p>
      </div>

      {/* Progress bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs text-gray-500">
          <span>{current.title.split(' ').slice(0, 4).join(' ')}…</span>
          <span>{progressPct}%</span>
        </div>
        <div className="w-full bg-white/5 rounded-full h-1.5">
          <div
            className="bg-cyan-500 h-1.5 rounded-full transition-all duration-300"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      {/* Step card */}
      <div className="bg-white/3 border border-white/8 rounded-2xl p-6 space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-white mb-1">{current.title}</h2>
          <p className="text-gray-400 text-sm">{current.description}</p>
        </div>

        {/* Hint box */}
        {current.hint && (
          <div className="flex gap-2 bg-cyan-500/5 border border-cyan-500/15 rounded-lg px-4 py-3 text-sm text-cyan-200/80">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-cyan-400" />
            <span>{current.hint}</span>
          </div>
        )}

        {/* ── Textarea ── */}
        {current.type === 'textarea' && (
          <textarea
            rows={4}
            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 resize-none transition-colors"
            placeholder={current.placeholder}
            value={formData[current.field] || ''}
            onChange={e => handleChange(current.field, e.target.value)}
          />
        )}

        {/* ── Slider ── */}
        {current.type === 'slider' && (
          <div className="space-y-3">
            <div className="flex items-center gap-4">
              <input
                type="range"
                min={current.min}
                max={current.max}
                step={current.step}
                value={formData[current.field] ?? current.min}
                onChange={e => handleChange(current.field, Number(e.target.value))}
                className="flex-1 accent-cyan-500"
              />
              <span className="text-2xl font-bold text-cyan-400 w-16 text-right tabular-nums">
                {formData[current.field] ?? current.min}
                <span className="text-sm font-normal text-gray-500 ml-0.5">{current.suffix}</span>
              </span>
            </div>
            {current.additionalFields?.map(af => (
              <label key={af.field} className="flex items-center gap-3 cursor-pointer mt-1 select-none">
                <input
                  type="checkbox"
                  checked={Boolean(formData[af.field])}
                  onChange={e => handleChange(af.field, e.target.checked)}
                  className="w-4 h-4 accent-cyan-500 rounded"
                />
                <span className="text-sm text-gray-300">{af.label}</span>
              </label>
            ))}
          </div>
        )}

        {/* ── Radio ── */}
        {current.type === 'radio' && (
          <div className="space-y-2">
            {current.options.map(opt => {
              const selected = formData[current.field] === opt.value
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => handleChange(current.field, opt.value)}
                  className={`w-full flex items-center gap-3 p-3.5 rounded-xl border text-left transition-all duration-150 text-sm ${
                    selected
                      ? 'border-cyan-500/50 bg-cyan-500/8 text-white'
                      : 'border-white/8 bg-black/20 text-gray-400 hover:border-white/15 hover:text-gray-300'
                  }`}
                >
                  <div className={`w-4 h-4 rounded-full shrink-0 border-2 flex items-center justify-center ${
                    selected ? 'border-cyan-500 bg-cyan-500' : 'border-gray-600'
                  }`}>
                    {selected && <div className="w-1.5 h-1.5 rounded-full bg-black" />}
                  </div>
                  {opt.label}
                </button>
              )
            })}
          </div>
        )}

        {/* ── Checklist ── */}
        {current.type === 'checklist' && (
          <div className="space-y-2">
            {current.options.map(opt => (
              <label
                key={opt.field}
                className="flex items-start gap-3 cursor-pointer p-3.5 rounded-xl border border-white/8 bg-black/20 hover:border-white/15 transition-colors select-none"
              >
                <input
                  type="checkbox"
                  checked={Boolean(formData[opt.field])}
                  onChange={e => handleChange(opt.field, e.target.checked)}
                  className="mt-0.5 w-4 h-4 accent-cyan-500 rounded shrink-0"
                />
                <span className="text-sm text-gray-300">{opt.label}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="flex gap-2 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-sm text-red-300">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between pt-1">
        <button
          onClick={() => setStep(s => s - 1)}
          disabled={step === 0}
          className="px-4 py-2 text-sm text-gray-500 hover:text-gray-300 disabled:opacity-0 disabled:pointer-events-none transition-colors"
        >
          ← Back
        </button>

        {step < totalSteps - 1 ? (
          <button
            onClick={() => setStep(s => s + 1)}
            disabled={!canProceed()}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-black text-sm font-semibold rounded-xl disabled:opacity-30 disabled:pointer-events-none transition-colors"
          >
            Continue
            <ChevronRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={loading || !canProceed()}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-black text-sm font-semibold rounded-xl disabled:opacity-30 disabled:pointer-events-none transition-colors"
          >
            {loading ? (
              <>
                <span className="inline-block animate-spin w-4 h-4 border-2 border-black/30 border-t-black rounded-full" />
                Analysing...
              </>
            ) : (
              <>
                See My Results
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        )}
      </div>
    </div>
  )
}
