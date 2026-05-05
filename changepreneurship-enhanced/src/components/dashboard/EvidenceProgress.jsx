/**
 * EvidenceProgress — Sprint 6 (S6-04)
 * Shows response count per phase as a lightweight evidence indicator.
 * CEO (Section 2.5): Evidence strength matters — more responses = stronger base.
 */
import React from 'react'
import { MessageSquare } from 'lucide-react'

const EvidenceProgress = ({ phases }) => {
  if (!phases || phases.length === 0) return null

  const phasesWithResponses = phases.filter(p => p.response_count > 0 || p.status === 'IN_PROGRESS')

  if (phasesWithResponses.length === 0) return null

  const maxResponses = Math.max(...phases.map(p => p.response_count || 0), 1)

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4">
      <h3 className="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2">
        <MessageSquare className="w-4 h-4 text-slate-400" />
        Responses by Phase
      </h3>
      <div className="space-y-2.5">
        {phases.map((phase) => {
          const count = phase.response_count || 0
          const pct = Math.round((count / maxResponses) * 100)
          const isActive = phase.status === 'IN_PROGRESS' || phase.status === 'COMPLETED'

          return (
            <div key={phase.id} className="flex items-center gap-3">
              <span className={`text-xs w-32 truncate flex-shrink-0 ${
                isActive ? 'text-slate-700 font-medium' : 'text-slate-400'
              }`}>
                {phase.name}
              </span>
              <div className="flex-1 bg-slate-100 rounded-full h-1.5">
                {count > 0 && (
                  <div
                    className={`h-1.5 rounded-full transition-all duration-500 ${
                      phase.status === 'COMPLETED'   ? 'bg-emerald-500' :
                      phase.status === 'IN_PROGRESS' ? 'bg-indigo-500'  :
                                                       'bg-slate-300'
                    }`}
                    style={{ width: `${pct}%` }}
                  />
                )}
              </div>
              <span className={`text-xs w-10 text-right flex-shrink-0 ${
                isActive ? 'text-slate-600' : 'text-slate-300'
              }`}>
                {count > 0 ? count : '—'}
              </span>
            </div>
          )
        })}
      </div>
      <p className="text-xs text-slate-400 mt-3">Number of submitted responses per phase</p>
    </div>
  )
}

export default EvidenceProgress
