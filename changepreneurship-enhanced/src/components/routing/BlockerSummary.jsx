/**
 * BlockerSummary — displays the list of active blockers.
 * Each blocker is collapsible and shows unlock conditions.
 */
import { useState } from 'react'

const SEVERITY_META = {
  3: { label: 'Soft Block', bg: 'bg-orange-50', border: 'border-orange-200', badge: 'bg-orange-100 text-orange-700', icon: '⚠' },
  4: { label: 'Hard Block', bg: 'bg-red-50',    border: 'border-red-200',    badge: 'bg-red-100 text-red-700',    icon: '🚫' },
  5: { label: 'Hard Stop',  bg: 'bg-red-100',   border: 'border-red-300',    badge: 'bg-red-200 text-red-900',   icon: '⛔' },
}
const DEFAULT_META = { label: 'Notice', bg: 'bg-gray-50', border: 'border-gray-200', badge: 'bg-gray-100 text-gray-600', icon: 'ℹ' }

function formatAction(a) {
  return a.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function BlockerItem({ blocker, initialOpen = false }) {
  const [open, setOpen] = useState(initialOpen)
  const severity = blocker.severity || blocker.severity_level || 3
  const meta = SEVERITY_META[severity] || DEFAULT_META

  const blockedActions = blocker.what_is_blocked || (blocker.action ? [blocker.action] : [])
  const allowedActions = blocker.what_is_allowed || blocker.allowed_actions || []
  const unlock = blocker.unlock_condition || blocker.unlock || ''
  const reason = blocker.reason || ''
  const dimension = (blocker.dimension || '').replace(/_/g, ' ')

  return (
    <div className={`rounded-lg border ${meta.border} ${meta.bg} overflow-hidden`}>
      {/* Collapsed header — always visible */}
      <button
        onClick={() => setOpen(v => !v)}
        className="w-full flex items-center justify-between px-4 py-3 text-left"
      >
        <div className="flex items-center gap-2">
          <span>{meta.icon}</span>
          <div>
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full mr-2 ${meta.badge}`}>
              {meta.label}
            </span>
            {dimension && (
              <span className="text-xs text-gray-500">{dimension}</span>
            )}
          </div>
        </div>
        <span className="text-gray-400 text-sm ml-2">{open ? '▲' : '▼'}</span>
      </button>

      {/* Expanded content */}
      {open && (
        <div className="px-4 pb-4 space-y-3 border-t border-gray-100">
          {reason && (
            <p className="text-sm text-gray-800 pt-3">{reason}</p>
          )}

          {blockedActions.filter(a => a !== 'all_platform_activities').length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">
                Unavailable now
              </p>
              <div className="flex flex-wrap gap-1.5">
                {blockedActions.slice(0, 6).map((a, i) => (
                  <span key={i} className="text-xs px-2 py-0.5 bg-white border border-red-200 text-red-700 rounded-full">
                    {formatAction(a)}
                  </span>
                ))}
              </div>
            </div>
          )}

          {allowedActions.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">
                Available now
              </p>
              <div className="flex flex-wrap gap-1.5">
                {allowedActions.slice(0, 6).map((a, i) => (
                  <span key={i} className="text-xs px-2 py-0.5 bg-white border border-green-200 text-green-700 rounded-full">
                    {formatAction(a)}
                  </span>
                ))}
              </div>
            </div>
          )}

          {unlock && (
            <div className="bg-white rounded border border-gray-200 px-3 py-2">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-0.5">
                How to unlock
              </p>
              <p className="text-sm text-gray-800">{unlock}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function BlockerSummary({ blockers = [], title = 'Active Blockers' }) {
  if (!blockers || blockers.length === 0) {
    return (
      <div className="rounded-xl bg-green-50 border border-green-200 px-5 py-4">
        <p className="text-sm font-medium text-green-800">No active blockers — all actions available.</p>
      </div>
    )
  }

  const hardCount = blockers.filter(b => (b.severity || b.severity_level || 0) >= 4).length
  const softCount = blockers.length - hardCount

  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <h3 className="text-base font-semibold text-gray-900">{title}</h3>
        {hardCount > 0 && (
          <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-700">
            {hardCount} hard
          </span>
        )}
        {softCount > 0 && (
          <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-orange-100 text-orange-700">
            {softCount} soft
          </span>
        )}
      </div>

      <div className="space-y-2">
        {/* Hard blocks first */}
        {[...blockers]
          .sort((a, b) => ((b.severity || b.severity_level || 0) - (a.severity || a.severity_level || 0)))
          .map((blocker, i) => (
            <BlockerItem
              key={blocker.id || i}
              blocker={blocker}
              initialOpen={i === 0}
            />
          ))
        }
      </div>
    </div>
  )
}
