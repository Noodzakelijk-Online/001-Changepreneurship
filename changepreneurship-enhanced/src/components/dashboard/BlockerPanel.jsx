/**
 * BlockerPanel — Sprint 6 (S6-04)
 * Displays active (unresolved) blockers prominently.
 * CEO (Section 13.1): "User immediately sees: Your main blocker + how to fix."
 */
import React, { useState } from 'react'
import { AlertTriangle, XCircle, ChevronDown, ChevronUp, ShieldAlert } from 'lucide-react'

const LEVEL_CONFIG = {
  5: { label: 'Hard Stop',   color: 'text-red-800',    bg: 'bg-red-100',    border: 'border-red-400',  icon: XCircle },
  4: { label: 'Hard Block',  color: 'text-red-700',    bg: 'bg-red-50',     border: 'border-red-300',  icon: ShieldAlert },
  3: { label: 'Soft Block',  color: 'text-amber-700',  bg: 'bg-amber-50',   border: 'border-amber-300', icon: AlertTriangle },
  2: { label: 'Warning',     color: 'text-yellow-700', bg: 'bg-yellow-50',  border: 'border-yellow-200', icon: AlertTriangle },
}

const BlockerItem = ({ blocker }) => {
  const [expanded, setExpanded] = useState(blocker.level >= 4)
  const level = blocker.level || 3
  const cfg = LEVEL_CONFIG[level] || LEVEL_CONFIG[3]
  const Icon = cfg.icon

  return (
    <div className={`rounded-lg border p-3 ${cfg.bg} ${cfg.border}`}>
      <button
        className="w-full flex items-center gap-2 text-left"
        onClick={() => setExpanded(e => !e)}
      >
        <Icon className={`w-4 h-4 flex-shrink-0 ${cfg.color}`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-xs font-semibold ${cfg.color}`}>{cfg.label}</span>
            <span className={`text-xs font-medium truncate ${cfg.color}`}>
              {(blocker.type || 'BLOCKER').replace(/_/g, ' ')}
            </span>
          </div>
          {!expanded && blocker.reason && (
            <p className="text-xs text-slate-600 mt-0.5 line-clamp-1">{blocker.reason}</p>
          )}
        </div>
        {expanded
          ? <ChevronUp className="w-4 h-4 text-slate-400 flex-shrink-0" />
          : <ChevronDown className="w-4 h-4 text-slate-400 flex-shrink-0" />
        }
      </button>

      {expanded && (
        <div className="mt-3 space-y-2 pl-6">
          {blocker.reason && (
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-0.5">Why blocked</p>
              <p className="text-sm text-slate-700">{blocker.reason}</p>
            </div>
          )}
          {blocker.unlock_condition && (
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-0.5">How to unlock</p>
              <p className="text-sm text-slate-700 font-medium">{blocker.unlock_condition}</p>
            </div>
          )}
          {blocker.triggered_at && (
            <p className="text-xs text-slate-400">
              Since {new Date(blocker.triggered_at).toLocaleDateString()}
            </p>
          )}
        </div>
      )}
    </div>
  )
}

const BlockerPanel = ({ blockers }) => {
  if (!blockers || blockers.length === 0) return null

  const hardBlockers = blockers.filter(b => b.level >= 4)
  const softBlockers = blockers.filter(b => b.level < 4)

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
        <ShieldAlert className="w-4 h-4 text-red-500" />
        Active Blockers
        <span className="ml-1 text-xs bg-red-100 text-red-700 px-1.5 py-0.5 rounded-full">
          {blockers.length}
        </span>
      </h3>
      {hardBlockers.map(b => (
        <BlockerItem key={b.id} blocker={b} />
      ))}
      {softBlockers.map(b => (
        <BlockerItem key={b.id} blocker={b} />
      ))}
    </div>
  )
}

export default BlockerPanel
