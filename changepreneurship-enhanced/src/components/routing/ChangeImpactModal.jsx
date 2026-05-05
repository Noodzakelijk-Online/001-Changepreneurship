/**
 * ChangeImpactModal — shown when the user changes a field with severity >= 3.
 * Lists all affected outputs and asks for user confirmation.
 */
import { useEffect, useRef } from 'react'

const SEVERITY_META = {
  1: { label: 'Wording Change',       color: 'text-gray-500',  badge: 'bg-gray-100 text-gray-600' },
  2: { label: 'Detail Change',        color: 'text-blue-600',  badge: 'bg-blue-100 text-blue-700' },
  3: { label: 'Assumption Change',    color: 'text-amber-600', badge: 'bg-amber-100 text-amber-700' },
  4: { label: 'Strategic Change',     color: 'text-orange-600',badge: 'bg-orange-100 text-orange-700' },
  5: { label: 'Blocking Change',      color: 'text-red-600',   badge: 'bg-red-100 text-red-700' },
  6: { label: 'Venture Restart',      color: 'text-red-700',   badge: 'bg-red-200 text-red-900' },
}

const STATUS_BADGE = {
  INVALIDATED:   'bg-red-100 text-red-700',
  STALE:         'bg-amber-100 text-amber-700',
  NEEDS_REVIEW:  'bg-yellow-100 text-yellow-700',
  UNCHANGED:     'bg-gray-100 text-gray-500',
}

function formatType(type) {
  return type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

export default function ChangeImpactModal({ impact, fieldLabel, onConfirm, onCancel }) {
  const dialogRef = useRef(null)

  useEffect(() => {
    // Trap focus when modal opens
    dialogRef.current?.focus()
    // Prevent body scroll
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = '' }
  }, [])

  if (!impact) return null

  const meta = SEVERITY_META[impact.severity_level] || SEVERITY_META[3]
  const isRestart = impact.is_venture_restart
  const requiresApproval = impact.requires_user_approval

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40"
      onClick={e => { if (e.target === e.currentTarget) onCancel?.() }}
      role="dialog"
      aria-modal="true"
    >
      <div
        ref={dialogRef}
        tabIndex={-1}
        className="bg-white rounded-xl shadow-2xl w-full max-w-lg outline-none"
      >
        {/* Header */}
        <div className={`px-6 py-4 border-b ${isRestart ? 'bg-red-50 border-red-200' : 'bg-gray-50 border-gray-200'} rounded-t-xl`}>
          <div className="flex items-center gap-3">
            <span className="text-xl">{isRestart ? '⛔' : '⚠'}</span>
            <div>
              <h2 className="text-base font-bold text-gray-900">
                {isRestart ? 'This change restarts your venture analysis' : 'This change has downstream impact'}
              </h2>
              <p className="text-sm text-gray-500">
                You changed: <span className="font-medium text-gray-700">{fieldLabel || impact.changed_field}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-4 space-y-4 max-h-[60vh] overflow-y-auto">
          {/* Severity badge */}
          <div className="flex items-center gap-2">
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${meta.badge}`}>
              Severity {impact.severity_level} — {meta.label}
            </span>
          </div>

          {/* Recommendation */}
          {impact.recommendation && (
            <p className="text-sm text-gray-800">{impact.recommendation}</p>
          )}

          {/* Affected outputs */}
          {impact.affected_outputs?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                Outputs that will be affected
              </p>
              <ul className="space-y-1.5">
                {impact.affected_outputs.map((o, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <span className={`mt-0.5 text-xs font-semibold px-2 py-0.5 rounded-full shrink-0 ${STATUS_BADGE[o.status] || STATUS_BADGE.NEEDS_REVIEW}`}>
                      {o.status}
                    </span>
                    <span className="text-gray-800 font-medium">{formatType(o.output_type)}</span>
                    {o.reason && (
                      <span className="text-gray-500 text-xs">— {o.reason}</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Downstream / sidestream */}
          {impact.downstream_impact?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">
                Downstream ripple
              </p>
              <ul className="list-disc list-inside space-y-0.5">
                {impact.downstream_impact.map((d, i) => (
                  <li key={i} className="text-sm text-gray-700">{d}</li>
                ))}
              </ul>
            </div>
          )}

          {isRestart && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3">
              <p className="text-sm font-semibold text-red-800 mb-1">
                Full venture restart required
              </p>
              <p className="text-sm text-red-700">
                This change is so fundamental that your current analysis, routing, and
                phase progress will be re-calculated from the beginning.
                Your previous data is preserved for reference.
              </p>
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div className="px-6 py-4 border-t border-gray-100 flex flex-col sm:flex-row gap-3 sm:justify-end rounded-b-xl">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            Cancel change
          </button>
          <button
            onClick={onConfirm}
            className={`px-5 py-2 text-sm font-medium text-white rounded-lg transition-colors ${
              isRestart ? 'bg-red-600 hover:bg-red-700' : 'bg-indigo-600 hover:bg-indigo-700'
            }`}
          >
            {requiresApproval
              ? isRestart ? 'Restart analysis' : 'Confirm change'
              : 'Apply change'}
          </button>
        </div>
      </div>
    </div>
  )
}
