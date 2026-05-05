/**
 * PhaseJourneyMap — Sprint 6 (S6-04)
 * Visualises all 7 phases as a horizontal journey map.
 * Status: LOCKED | NOT_STARTED | IN_PROGRESS | COMPLETED
 */
import React from 'react'
import { CheckCircle2, Circle, Lock, PlayCircle } from 'lucide-react'

const STATUS_CONFIG = {
  COMPLETED:   { icon: CheckCircle2, bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400', iconColor: 'text-emerald-500', label: 'Completed' },
  IN_PROGRESS: { icon: PlayCircle,   bg: 'bg-indigo-500/10',  border: 'border-indigo-500/30',  text: 'text-indigo-400',  iconColor: 'text-indigo-500',  label: 'In Progress' },
  NOT_STARTED: { icon: Circle,       bg: 'bg-white/[0.02]',   border: 'border-white/10',        text: 'text-slate-400',   iconColor: 'text-slate-500',   label: 'Not Started' },
  LOCKED:      { icon: Lock,         bg: 'bg-white/[0.01]',   border: 'border-white/5',         text: 'text-slate-600',   iconColor: 'text-slate-700',   label: 'Locked' },
}

const PhaseCard = ({ phase, isLast }) => {
  const cfg = STATUS_CONFIG[phase.status] || STATUS_CONFIG.LOCKED
  const Icon = cfg.icon

  return (
    <div className="flex items-start gap-2 flex-1 min-w-0">
      {/* Phase card */}
      <div className={`flex-1 rounded-lg border p-3 ${cfg.bg} ${cfg.border} transition-all`}>
        <div className="flex items-center gap-2 mb-1">
          <Icon className={`w-4 h-4 flex-shrink-0 ${cfg.iconColor}`} />
          <span className={`text-xs font-semibold ${cfg.text} truncate`}>{phase.name}</span>
        </div>

        {/* Progress bar for in-progress */}
        {phase.status === 'IN_PROGRESS' && (
          <div className="w-full bg-indigo-900/40 rounded-full h-1.5 mt-2">
            <div
              className="bg-indigo-500 h-1.5 rounded-full"
              style={{ width: `${phase.progress_percentage}%` }}
            />
          </div>
        )}

        <div className="mt-1 flex items-center justify-between">
          <span className={`text-xs ${cfg.text} opacity-70`}>{cfg.label}</span>
          {phase.status !== 'LOCKED' && phase.status !== 'NOT_STARTED' && (
            <span className="text-xs text-slate-500">{phase.progress_percentage}%</span>
          )}
        </div>
      </div>

      {/* Connector line */}
      {!isLast && (
        <div className="flex items-center self-stretch pt-4">
          <div className="w-4 h-0.5 bg-white/10 flex-shrink-0" />
        </div>
      )}
    </div>
  )
}

const PhaseJourneyMap = ({ phases }) => {
  if (!phases || phases.length === 0) return null

  return (
    <div>
      {/* Mobile: vertical list */}
      <div className="block sm:hidden space-y-2">
        {phases.map((phase) => (
          <div key={phase.id} className="flex items-center gap-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              STATUS_CONFIG[phase.status]?.bg ?? 'bg-white/[0.02]'
            } ${STATUS_CONFIG[phase.status]?.border ?? 'border-white/10'} border`}>
              <span className={`text-xs font-bold ${STATUS_CONFIG[phase.status]?.text ?? 'text-slate-400'}`}>
                {phase.order}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium truncate ${STATUS_CONFIG[phase.status]?.text ?? 'text-slate-400'}`}>
                {phase.name}
              </p>
              <p className="text-xs text-slate-500">{STATUS_CONFIG[phase.status]?.label}</p>
            </div>
            {phase.status === 'IN_PROGRESS' && (
              <span className="text-xs text-indigo-400 font-semibold">{phase.progress_percentage}%</span>
            )}
          </div>
        ))}
      </div>

      {/* Desktop: horizontal scroll */}
      <div className="hidden sm:flex items-start gap-0 overflow-x-auto pb-2">
        {phases.map((phase, idx) => (
          <PhaseCard key={phase.id} phase={phase} isLast={idx === phases.length - 1} />
        ))}
      </div>
    </div>
  )
}

export default PhaseJourneyMap
