const SEVERITY_STYLES = {
  3: { border: 'border-orange-200', bg: 'bg-orange-50', badge: 'bg-orange-100 text-orange-700', icon: '⚠' },
  4: { border: 'border-red-200', bg: 'bg-red-50', badge: 'bg-red-100 text-red-700', icon: '🚫' },
  5: { border: 'border-red-300', bg: 'bg-red-100', badge: 'bg-red-200 text-red-900', icon: '⛔' },
}

const DEFAULT_STYLE = { border: 'border-gray-200', bg: 'bg-gray-50', badge: 'bg-gray-100 text-gray-700', icon: 'ℹ' }

const SEVERITY_LABELS = {
  3: 'Soft Block',
  4: 'Hard Block',
  5: 'Hard Stop',
}

const DIM_LABELS = {
  financial_readiness: 'Financial Readiness',
  time_capacity: 'Time & Capacity',
  personal_stability: 'Personal Stability',
  idea_clarity: 'Idea Clarity',
  skills_experience: 'Skills & Experience',
  legal_employment: 'Legal & Employment',
  health_energy: 'Health & Energy',
  founder_idea_fit: 'Founder–Idea Fit',
}

export default function BlockerCard({ blocker }) {
  if (!blocker) return null

  const style = SEVERITY_STYLES[blocker.severity] || DEFAULT_STYLE
  const severityLabel = SEVERITY_LABELS[blocker.severity] || 'Notice'
  const dimLabel = DIM_LABELS[blocker.dimension] || blocker.dimension

  const blockedList = Array.isArray(blocker.what_is_blocked)
    ? blocker.what_is_blocked.filter(a => a !== 'all_platform_activities' && a !== 'all_active_building_tasks')
    : []
  const allowedList = Array.isArray(blocker.what_is_allowed)
    ? blocker.what_is_allowed
    : []

  function formatAction(action) {
    return action.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
  }

  return (
    <div className={`rounded-xl border ${style.border} ${style.bg} p-5 mb-4`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-lg" role="img" aria-label={severityLabel}>{style.icon}</span>
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{dimLabel}</p>
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${style.badge}`}>
              {severityLabel}
            </span>
          </div>
        </div>
      </div>

      {/* Reason */}
      <p className="text-sm text-gray-800 leading-relaxed mb-3">{blocker.reason}</p>

      {/* Blocked actions */}
      {blockedList.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Temporarily unavailable</p>
          <div className="flex flex-wrap gap-1.5">
            {blockedList.map((action, i) => (
              <span key={i} className="text-xs px-2 py-0.5 bg-white border border-red-200 text-red-700 rounded-full">
                {formatAction(action)}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Allowed actions */}
      {allowedList.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Available to you now</p>
          <div className="flex flex-wrap gap-1.5">
            {allowedList.map((action, i) => (
              <span key={i} className="text-xs px-2 py-0.5 bg-white border border-green-200 text-green-700 rounded-full">
                {formatAction(action)}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Unlock condition */}
      {blocker.unlock_condition && (
        <div className="border-t border-gray-200 pt-3 mt-3">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">How to unlock</p>
          <p className="text-sm text-gray-700">{blocker.unlock_condition}</p>
        </div>
      )}
    </div>
  )
}
