/**
 * Phase2Form — Idea Discovery (Sprint 21)
 *
 * Dark-themed multi-step form that:
 *  1. Collects idea clarity data (idea, problem, target user, value prop, use case, context)
 *  2. POSTs to /api/v1/phase2/submit → creates VentureRecord + Clarified Venture Concept
 *  3. Calls completePhase('idea_discovery') to mark assessment done
 *  4. Shows the resulting CVC with clarity score + blockers
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  CheckCircle, ArrowRight, ChevronRight, AlertTriangle, Lightbulb,
} from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'
import apiService from '../../services/api'

// ─── Step definitions ──────────────────────────────────────────────────────────

const STEPS = [
  {
    id: 'idea',
    title: 'What are you trying to build?',
    description: 'Describe the idea, product, or service. A sentence or a paragraph — either is fine.',
    field: 'idea_description',
    placeholder:
      'E.g. A platform that helps restaurant owners track ingredient expiry dates and reduce food waste automatically…',
  },
  {
    id: 'problem',
    title: 'What specific problem does it solve?',
    description: 'Name the problem, who has it, and why current solutions fail them.',
    field: 'problem_description',
    placeholder:
      'E.g. Restaurant owners throw away €400+ of food per week because stock management is manual. Existing software is built for large chains and too expensive for small owners…',
  },
  {
    id: 'target',
    title: 'Who exactly is it for?',
    description:
      'Describe your target user specifically. Avoid "everyone" or "any business" — the more specific, the better.',
    field: 'target_user_description',
    placeholder:
      'E.g. Independent restaurant owners with 5–20 staff in mid-sized European cities who currently manage stock on paper or spreadsheets…',
  },
  {
    id: 'value',
    title: 'What value does it create?',
    description: 'What changes for the user if this works? Focus on outcomes — time saved, money saved, pain removed.',
    field: 'value_prop',
    placeholder:
      'E.g. Restaurant owners save €300–500/month in wasted stock and 3+ hours/week on manual checking, without changing their existing workflow…',
  },
  {
    id: 'usecase',
    title: 'Describe the first use case.',
    description:
      'One scenario: who uses it, when, what happens, and what result they get. This defines the first thing you build.',
    field: 'first_use_case',
    placeholder:
      'E.g. A chef scans incoming deliveries with a phone camera. The app logs expiry dates and sends an alert 2 days before anything expires, so they can run specials on expiring stock…',
  },
  {
    id: 'context',
    title: 'What alternatives exist, and why do you care?',
    description:
      'What do people use today instead of your idea? And why is this personally important to you?',
    field: 'alternatives',
    placeholder:
      'Alternatives: spreadsheets, paper, expensive ERP systems. I care because I watched my uncle lose his restaurant partly due to waste he could not control…',
    additionalTextarea: {
      field: 'motivation',
      label: 'Why does this matter to you personally? (optional)',
      placeholder: 'E.g. I worked in hospitality for 5 years and saw this problem firsthand…',
    },
  },
]

// ─── CVC Result Screen ─────────────────────────────────────────────────────────

function CVCScreen({ result, onContinue }) {
  const score    = result?.clarity_score ?? 0
  const cvc      = result?.cvc
  const blockers = result?.blockers || []
  const hardBlock = blockers.some(b => b.level >= 4)

  const scoreColor = score >= 70 ? 'bg-emerald-500' : score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
  const scoreText  = score >= 70 ? 'text-emerald-400' : score >= 40 ? 'text-yellow-400' : 'text-red-400'

  return (
    <div className="max-w-2xl mx-auto px-4 py-10 space-y-6">

      {/* Header */}
      <div className="text-center space-y-2">
        <div className={`inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-2 ${
          hardBlock ? 'bg-orange-500/10' : 'bg-emerald-500/10'
        }`}>
          {hardBlock
            ? <AlertTriangle className="w-8 h-8 text-orange-400" />
            : <CheckCircle className="w-8 h-8 text-emerald-400" />
          }
        </div>
        <h1 className="text-2xl font-bold text-white">
          {hardBlock ? 'Idea Needs Clarification' : 'Venture Concept Created'}
        </h1>
        <p className="text-gray-400 text-sm">
          {hardBlock
            ? 'Your idea has blockers that must be resolved before continuing to market research.'
            : 'Your Clarified Venture Concept has been saved to your Venture Profile.'
          }
        </p>
      </div>

      {/* Clarity score */}
      <div className="bg-white/[0.03] border border-white/8 rounded-2xl p-5 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-white">Idea Clarity Score</span>
          <span className={`text-2xl font-black tabular-nums ${scoreText}`}>
            {score}
            <span className="text-sm font-normal text-gray-500 ml-0.5">/100</span>
          </span>
        </div>
        <div className="h-2 rounded-full bg-white/5">
          <div
            className={`h-2 rounded-full transition-all ${scoreColor}`}
            style={{ width: `${score}%` }}
          />
        </div>
        <p className="text-xs text-gray-500">
          {score >= 70
            ? 'Idea is clear enough to proceed to market research.'
            : score >= 40
              ? 'Idea is partially clear. Address blockers before building.'
              : 'Idea needs significant clarification before continuing.'}
        </p>
      </div>

      {/* Blockers */}
      {blockers.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-orange-400 uppercase tracking-widest">
            {blockers.length} Blocker{blockers.length > 1 ? 's' : ''} Detected
          </h3>
          {blockers.map((b, i) => (
            <div
              key={i}
              className={`rounded-xl border p-4 space-y-2 ${
                b.level >= 4
                  ? 'border-red-500/30 bg-red-500/5'
                  : 'border-orange-500/25 bg-orange-500/5'
              }`}
            >
              <div className="flex items-start gap-2">
                <AlertTriangle className={`w-4 h-4 shrink-0 mt-0.5 ${b.level >= 4 ? 'text-red-400' : 'text-orange-400'}`} />
                <p className="text-sm text-white font-medium">{b.explanation}</p>
              </div>
              <p className="text-xs text-gray-400 pl-6">
                <span className="font-semibold text-gray-300">To unlock: </span>
                {b.unlock_condition}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* CVC */}
      {cvc && (
        <div className="bg-white/[0.03] border border-white/8 rounded-2xl p-5 space-y-4">
          <h3 className="text-xs font-bold text-yellow-400 uppercase tracking-widest flex items-center gap-2">
            <Lightbulb className="w-3.5 h-3.5" /> Clarified Venture Concept
          </h3>

          {[
            { label: 'Problem Statement',       value: cvc.problem_statement },
            { label: 'Target User Hypothesis',  value: cvc.target_user_hypothesis },
            { label: 'Value Proposition',       value: cvc.value_proposition },
          ].map(({ label, value }) =>
            value ? (
              <div key={label} className="space-y-1">
                <p className="text-[10px] font-bold text-gray-600 uppercase tracking-widest">{label}</p>
                <p className="text-sm text-gray-300 leading-relaxed">{value}</p>
              </div>
            ) : null
          )}

          {cvc.assumptions?.length > 0 && (
            <div className="space-y-1 pt-2 border-t border-white/5">
              <p className="text-[10px] font-bold text-gray-600 uppercase tracking-widest mb-2">
                Initial Assumptions to Test
              </p>
              {cvc.assumptions.map((a, i) => (
                <div key={i} className="flex gap-2 text-xs text-gray-400">
                  <span className="text-gray-600 shrink-0">{i + 1}.</span>
                  <span>{typeof a === 'string' ? a : a.claim}</span>
                </div>
              ))}
            </div>
          )}

          {cvc.open_questions?.length > 0 && (
            <div className="space-y-1 pt-2 border-t border-white/5">
              <p className="text-[10px] font-bold text-gray-600 uppercase tracking-widest mb-2">
                Open Questions
              </p>
              {cvc.open_questions.map((q, i) => (
                <div key={i} className="flex gap-2 text-xs text-gray-400">
                  <span className="text-gray-600 shrink-0">→</span>
                  <span>{typeof q === 'string' ? q : q.question}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* CTA */}
      <button
        onClick={onContinue}
        className="w-full flex items-center justify-center gap-2 py-3 px-6 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-xl transition-colors"
      >
        {hardBlock ? 'Return to Dashboard' : 'View Venture Profile'}
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  )
}

// ─── Main Component ────────────────────────────────────────────────────────────

export default function Phase2Form() {
  const navigate = useNavigate()
  const { completePhase } = useAssessment()

  const [step, setStep]       = useState(0)
  const [formData, setFormData] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)
  const [result, setResult]   = useState(null)

  const current    = STEPS[step]
  const totalSteps = STEPS.length
  const progressPct = Math.round(((step + 1) / totalSteps) * 100)

  function handleChange(field, value) {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  function canProceed() {
    // Last step (context) is optional — always allow proceeding
    if (step === totalSteps - 1) return true
    return (formData[current.field] || '').trim().length >= 10
  }

  async function handleSubmit() {
    setLoading(true)
    setError(null)

    const payload = {
      responses: {
        idea_description:        formData.idea_description || '',
        problem_description:     formData.problem_description || '',
        target_user_description: formData.target_user_description || '',
        value_prop:              formData.value_prop || '',
        first_use_case:          formData.first_use_case || '',
        alternatives:            formData.alternatives || '',
        motivation:              formData.motivation || '',
        has_b2b_element:         false,
        current_phase:           2,
      },
    }

    try {
      const res = await apiService.request('/v1/phase2/submit', {
        method: 'POST',
        body: JSON.stringify(payload),
      })

      if (!res.success) {
        throw new Error(res.error || 'Server error')
      }

      const data = res.data

      // Mark assessment complete in context (updates sidebar progress)
      try {
        await completePhase('idea_discovery')
      } catch (_e) {
        // Non-blocking — VentureRecord was created, assessment marking is secondary
      }

      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // ── Result screen ──────────────────────────────────────────────────────────
  if (result) {
    const hardBlock = (result.blockers || []).some(b => b.level >= 4)
    return (
      <CVCScreen
        result={result}
        onContinue={() => navigate(hardBlock ? '/dashboard' : '/assessment/market-research')}
      />
    )
  }

  // ── Form ───────────────────────────────────────────────────────────────────
  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Idea Discovery</h1>
        <p className="text-gray-400 text-sm">
          Turn your rough idea into a Clarified Venture Concept. Step {step + 1} of {totalSteps}.
        </p>
      </div>

      {/* Progress bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs text-gray-500">
          <span>{current.title.split(' ').slice(0, 5).join(' ')}…</span>
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
      <div className="bg-white/[0.03] border border-white/8 rounded-2xl p-6 space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-white mb-1">{current.title}</h2>
          <p className="text-gray-400 text-sm">{current.description}</p>
        </div>

        <textarea
          rows={5}
          className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 resize-none transition-colors"
          placeholder={current.placeholder}
          value={formData[current.field] || ''}
          onChange={e => handleChange(current.field, e.target.value)}
        />

        {/* Additional textarea for last step */}
        {current.additionalTextarea && (
          <div className="space-y-2 pt-1">
            <label className="text-xs text-gray-500">{current.additionalTextarea.label}</label>
            <textarea
              rows={3}
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 resize-none transition-colors"
              placeholder={current.additionalTextarea.placeholder}
              value={formData[current.additionalTextarea.field] || ''}
              onChange={e => handleChange(current.additionalTextarea.field, e.target.value)}
            />
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
            disabled={loading}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-black text-sm font-semibold rounded-xl disabled:opacity-50 disabled:pointer-events-none transition-colors"
          >
            {loading ? 'Analyzing…' : 'Generate Venture Concept'}
            <ChevronRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  )
}
