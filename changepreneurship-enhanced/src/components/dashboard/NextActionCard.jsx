/**
 * NextActionCard — Sprint 6 (S6-04)
 * Most prominent component — shows the single most important next step.
 * CEO (Section 13.1): "Recommended next step is always concrete, not vague."
 */
import React from 'react'
import { ArrowRight, AlertTriangle, Zap, Info, TrendingUp } from 'lucide-react'

const PRIORITY_CONFIG = {
  CRITICAL: {
    bg:     'bg-red-50',
    border: 'border-red-300',
    icon:   AlertTriangle,
    iconBg: 'bg-red-100',
    iconColor: 'text-red-600',
    badge:  'bg-red-100 text-red-700',
    label:  'Critical',
  },
  HIGH: {
    bg:     'bg-indigo-50',
    border: 'border-indigo-300',
    icon:   Zap,
    iconBg: 'bg-indigo-100',
    iconColor: 'text-indigo-600',
    badge:  'bg-indigo-100 text-indigo-700',
    label:  'Next Step',
  },
  MEDIUM: {
    bg:     'bg-amber-50',
    border: 'border-amber-200',
    icon:   TrendingUp,
    iconBg: 'bg-amber-100',
    iconColor: 'text-amber-600',
    badge:  'bg-amber-100 text-amber-700',
    label:  'Recommended',
  },
  NORMAL: {
    bg:     'bg-emerald-50',
    border: 'border-emerald-200',
    icon:   ArrowRight,
    iconBg: 'bg-emerald-100',
    iconColor: 'text-emerald-600',
    badge:  'bg-emerald-100 text-emerald-700',
    label:  'Up Next',
  },
  LOW: {
    bg:     'bg-slate-50',
    border: 'border-slate-200',
    icon:   Info,
    iconBg: 'bg-slate-100',
    iconColor: 'text-slate-500',
    badge:  'bg-slate-100 text-slate-600',
    label:  'Info',
  },
  INFO: {
    bg:     'bg-emerald-50',
    border: 'border-emerald-200',
    icon:   Info,
    iconBg: 'bg-emerald-100',
    iconColor: 'text-emerald-600',
    badge:  'bg-emerald-100 text-emerald-700',
    label:  'Complete',
  },
}

const NextActionCard = ({ action }) => {
  if (!action) return null

  const priority = action.priority || 'NORMAL'
  const cfg = PRIORITY_CONFIG[priority] || PRIORITY_CONFIG.NORMAL
  const Icon = cfg.icon

  return (
    <div className={`rounded-xl border-2 p-5 ${cfg.bg} ${cfg.border}`}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${cfg.iconBg}`}>
          <Icon className={`w-5 h-5 ${cfg.iconColor}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${cfg.badge}`}>
              {cfg.label}
            </span>
            {action.phase_id && (
              <span className="text-xs text-slate-500 capitalize">
                {action.phase_id.replace(/_/g, ' ')}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Action text */}
      <p className="text-base font-semibold text-slate-900 leading-snug mb-2">
        {action.action}
      </p>

      {/* Reason */}
      {action.reason && (
        <p className="text-sm text-slate-600">{action.reason}</p>
      )}
    </div>
  )
}

export default NextActionCard
