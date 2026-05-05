/**
 * RerouteCard — displays the 5-element CEO reroute message.
 *
 * CEO Section 3.4 required elements:
 *   1. What was detected
 *   2. Why it matters
 *   3. What is blocked
 *   4. What is allowed
 *   5. Unlock condition
 */
import { useState } from 'react'

const CATEGORY_META = {
  FINANCIAL_STABILIZATION: { color: 'amber', icon: '💰', label: 'Financial Stabilisation' },
  STABILIZE:               { color: 'amber', icon: '⚓', label: 'Stabilise First' },
  CLARIFY:                 { color: 'blue',  icon: '🔍', label: 'Clarify Idea' },
  REASSESS:                { color: 'slate', icon: '🔄', label: 'Reassess Situation' },
  CUSTOMER_DISCOVERY:      { color: 'indigo', icon: '👥', label: 'Customer Discovery' },
  OPERATIONS_CLEANUP:      { color: 'orange', icon: '🔧', label: 'Operations Cleanup' },
  BURNOUT_PREVENTION:      { color: 'rose',   icon: '🌿', label: 'Protect Your Energy' },
  REFER:                   { color: 'purple', icon: '🤝', label: 'Seek Support' },
  HARD_ETHICAL_STOP:       { color: 'red',    icon: '⛔', label: 'Hard Stop' },
  PAUSE:                   { color: 'slate',  icon: '⏸',  label: 'Pause & Reflect' },
  FOUNDER_IDEA_MISMATCH:   { color: 'yellow', icon: '🎯', label: 'Founder-Idea Fit' },
}

const COLOR = {
  amber:  { bg: 'bg-amber-50',  border: 'border-amber-200',  icon: 'text-amber-500',  badge: 'bg-amber-100 text-amber-800',  btn: 'bg-amber-600 hover:bg-amber-700' },
  blue:   { bg: 'bg-blue-50',   border: 'border-blue-200',   icon: 'text-blue-500',   badge: 'bg-blue-100 text-blue-800',    btn: 'bg-blue-600 hover:bg-blue-700' },
  slate:  { bg: 'bg-slate-50',  border: 'border-slate-200',  icon: 'text-slate-500',  badge: 'bg-slate-100 text-slate-700',  btn: 'bg-slate-600 hover:bg-slate-700' },
  indigo: { bg: 'bg-indigo-50', border: 'border-indigo-200', icon: 'text-indigo-500', badge: 'bg-indigo-100 text-indigo-800',btn: 'bg-indigo-600 hover:bg-indigo-700' },
  orange: { bg: 'bg-orange-50', border: 'border-orange-200', icon: 'text-orange-500', badge: 'bg-orange-100 text-orange-700',btn: 'bg-orange-600 hover:bg-orange-700' },
  rose:   { bg: 'bg-rose-50',   border: 'border-rose-200',   icon: 'text-rose-500',   badge: 'bg-rose-100 text-rose-700',   btn: 'bg-rose-600 hover:bg-rose-700' },
  purple: { bg: 'bg-purple-50', border: 'border-purple-200', icon: 'text-purple-500', badge: 'bg-purple-100 text-purple-700',btn: 'bg-purple-600 hover:bg-purple-700' },
  red:    { bg: 'bg-red-50',    border: 'border-red-200',    icon: 'text-red-500',    badge: 'bg-red-100 text-red-700',     btn: 'bg-red-600 hover:bg-red-700' },
  yellow: { bg: 'bg-yellow-50', border: 'border-yellow-200', icon: 'text-yellow-600', badge: 'bg-yellow-100 text-yellow-800',btn: 'bg-yellow-600 hover:bg-yellow-700' },
}

export default function RerouteCard({ decision, onContinue }) {
  const [expanded, setExpanded] = useState(false)
  if (!decision?.is_reroute || !decision.reroute_message) return null

  const rm = decision.reroute_message
  const na = decision.next_action
  const meta = CATEGORY_META[decision.category] || { color: 'slate', icon: 'ℹ', label: decision.category }
  const c = COLOR[meta.color] || COLOR['slate']

  return (
    <div className={`rounded-xl border-2 ${c.border} ${c.bg} p-6 mb-6`}>
      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <span className={`text-2xl mt-0.5 shrink-0 ${c.icon}`}>{meta.icon}</span>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${c.badge}`}>
              {meta.label}
            </span>
            <span className="text-xs text-gray-500">Priority {decision.priority_level}</span>
          </div>
          <p className="text-base font-semibold text-gray-900">
            We are redirecting your next step.
          </p>
        </div>
      </div>

      {/* 5-element reroute message */}
      <div className="space-y-3 mb-5">
        {/* 1. Detected */}
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">
            What we detected
          </p>
          <p className="text-sm text-gray-800">{rm.detected}</p>
        </div>

        {/* 2. Why */}
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">
            Why this matters
          </p>
          <p className="text-sm text-gray-800">{rm.why}</p>
        </div>

        {/* 3 + 4. Blocked / Allowed — side by side */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="bg-white rounded-lg border border-red-100 p-3">
            <p className="text-xs font-semibold text-red-500 uppercase tracking-wide mb-1">
              Currently paused
            </p>
            <p className="text-sm text-red-800">{rm.blocked_action}</p>
          </div>
          <div className="bg-white rounded-lg border border-green-100 p-3">
            <p className="text-xs font-semibold text-green-600 uppercase tracking-wide mb-1">
              You can continue with
            </p>
            <p className="text-sm text-green-800">{rm.allowed_action}</p>
          </div>
        </div>

        {/* 5. Unlock condition */}
        <div className="bg-white rounded-lg border border-gray-200 p-3">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">
            How to unlock next stage
          </p>
          <p className="text-sm text-gray-800">{rm.unlock_condition}</p>
        </div>
      </div>

      {/* Recommended next action */}
      {na && (
        <div className="border-t border-gray-200 pt-4 mb-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
            Recommended next step
          </p>
          <p className="text-sm font-medium text-gray-900">{na.description}</p>
          {na.success_criteria && (
            <p className="text-xs text-gray-500 mt-1">
              Success looks like: {na.success_criteria}
            </p>
          )}
          {na.estimated_time && (
            <p className="text-xs text-gray-400 mt-0.5">
              Est. time: {na.estimated_time}
            </p>
          )}
        </div>
      )}

      {/* Full text toggle */}
      {rm.full_text && (
        <div className="mb-4">
          <button
            onClick={() => setExpanded(v => !v)}
            className="text-xs text-gray-400 underline underline-offset-2"
          >
            {expanded ? 'Hide full message' : 'Show full message'}
          </button>
          {expanded && (
            <pre className="mt-2 text-xs text-gray-600 whitespace-pre-wrap font-sans leading-relaxed">
              {rm.full_text}
            </pre>
          )}
        </div>
      )}

      {/* CTA */}
      {onContinue && decision.category !== 'HARD_ETHICAL_STOP' && (
        <button
          onClick={onContinue}
          className={`w-full sm:w-auto px-5 py-2 ${c.btn} text-white text-sm font-medium rounded-lg transition-colors`}
        >
          I understand — continue to allowed actions
        </button>
      )}
    </div>
  )
}
