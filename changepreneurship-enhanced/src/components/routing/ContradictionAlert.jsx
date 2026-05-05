/**
 * ContradictionAlert — soft warning when contradictory responses are detected.
 * Dismissible for soft/warning levels; non-dismissible for HARD contradictions.
 */
import { useState } from 'react'

const LEVEL_META = {
  1: { label: 'Note',               icon: '💡', bg: 'bg-blue-50',   border: 'border-blue-200',  text: 'text-blue-800',  badge: 'bg-blue-100 text-blue-700'   },
  2: { label: 'Consider reviewing', icon: '🤔', bg: 'bg-yellow-50', border: 'border-yellow-200',text: 'text-yellow-900',badge: 'bg-yellow-100 text-yellow-800' },
  3: { label: 'Soft conflict',      icon: '⚠',  bg: 'bg-orange-50', border: 'border-orange-200',text: 'text-orange-900',badge: 'bg-orange-100 text-orange-700' },
  4: { label: 'Hard conflict',      icon: '🚫', bg: 'bg-red-50',    border: 'border-red-200',   text: 'text-red-900',   badge: 'bg-red-100 text-red-700'      },
}

function ContradictionItem({ contradiction }) {
  const [expanded, setExpanded] = useState(false)
  const meta = LEVEL_META[contradiction.level] || LEVEL_META[2]
  const hasDetails = contradiction.recommendation || contradiction.affected_actions?.length > 0

  return (
    <div className={`rounded-lg border ${meta.border} ${meta.bg}`}>
      <div className="flex items-start justify-between gap-2 px-4 py-3">
        <div className="flex items-start gap-2 flex-1 min-w-0">
          <span className="mt-0.5 shrink-0">{meta.icon}</span>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 mb-0.5 flex-wrap">
              <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${meta.badge}`}>
                {meta.label}
              </span>
              {contradiction.dimension_a && contradiction.dimension_b && (
                <span className="text-xs text-gray-500">
                  {contradiction.dimension_a.replace(/_/g, ' ')} ↔ {contradiction.dimension_b.replace(/_/g, ' ')}
                </span>
              )}
            </div>
            <p className={`text-sm ${meta.text}`}>{contradiction.explanation}</p>
          </div>
        </div>
        {hasDetails && (
          <button
            onClick={() => setExpanded(v => !v)}
            className="shrink-0 text-gray-400 text-xs underline underline-offset-1"
          >
            {expanded ? 'Less' : 'More'}
          </button>
        )}
      </div>

      {expanded && hasDetails && (
        <div className="px-4 pb-3 pt-1 space-y-2 border-t border-gray-100">
          {contradiction.recommendation && (
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">
                Recommendation
              </p>
              <p className="text-sm text-gray-700">{contradiction.recommendation}</p>
            </div>
          )}
          {contradiction.affected_actions?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
                Actions affected
              </p>
              <div className="flex flex-wrap gap-1.5">
                {contradiction.affected_actions.map((a, i) => (
                  <span key={i} className="text-xs px-2 py-0.5 bg-white border border-gray-200 text-gray-600 rounded-full">
                    {a.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function ContradictionAlert({ result, onDismiss }) {
  const [dismissed, setDismissed] = useState(false)

  if (!result || result.contradictions?.length === 0) return null
  if (dismissed) return null

  const isBlocking = result.has_blocking_contradiction
  const maxLevel = result.max_level || 1
  const canDismiss = !isBlocking && maxLevel < 4

  const visibleItems = result.contradictions.slice(0, 5)

  return (
    <div className="mb-5">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-semibold text-gray-700">
          {isBlocking ? 'Conflicting answers detected' : 'Possible conflicts in your answers'}
        </h4>
        {canDismiss && (
          <button
            onClick={() => { setDismissed(true); onDismiss?.() }}
            className="text-xs text-gray-400 underline underline-offset-1"
          >
            Dismiss
          </button>
        )}
      </div>

      {result.summary && (
        <p className="text-xs text-gray-500 mb-2">{result.summary}</p>
      )}

      <div className="space-y-2">
        {visibleItems.map((c, i) => (
          <ContradictionItem key={i} contradiction={c} />
        ))}
      </div>

      {isBlocking && (
        <div className="mt-3 px-4 py-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm font-semibold text-red-800">
            Please resolve the conflicting answers above before continuing.
          </p>
        </div>
      )}
    </div>
  )
}
