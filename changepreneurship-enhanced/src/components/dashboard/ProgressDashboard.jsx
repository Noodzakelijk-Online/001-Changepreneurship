/**
 * ProgressDashboard — Sprint 6 (S6-04)
 * Full user progress dashboard.
 * Loads data from GET /api/v1/progress/dashboard
 */
import React, { useState, useEffect, useCallback } from 'react'
import apiService from '../../services/api'
import PhaseJourneyMap from './PhaseJourneyMap'
import NextActionCard from './NextActionCard'
import BlockerPanel from './BlockerPanel'
import EvidenceProgress from './EvidenceProgress'
import { RefreshCw, AlertCircle } from 'lucide-react'

const ProgressDashboard = () => {
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState(null)

  const loadDashboard = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiService.request('/v1/progress/dashboard')
      if (result.success) {
        setDashboard(result.data.dashboard)
      } else {
        setError(result.error || 'Failed to load dashboard')
      }
    } catch (e) {
      setError('Network error — please try again')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadDashboard() }, [loadDashboard])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="flex flex-col items-center gap-3 text-slate-500">
          <RefreshCw className="w-6 h-6 animate-spin" />
          <span className="text-sm">Loading your progress…</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
        <AlertCircle className="w-5 h-5 flex-shrink-0" />
        <span className="text-sm">{error}</span>
        <button
          onClick={loadDashboard}
          className="ml-auto text-xs underline hover:no-underline"
        >Retry</button>
      </div>
    )
  }

  if (!dashboard) return null

  const { stats, recommended_next_action, active_blockers, venture_summary } = dashboard

  return (
    <div className="space-y-6">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Your Progress</h2>
          {venture_summary && (
            <p className="text-sm text-slate-500 mt-0.5">
              {venture_summary.name}
              {venture_summary.venture_type && (
                <span className="ml-2 text-xs bg-slate-100 px-2 py-0.5 rounded-full">
                  {venture_summary.venture_type}
                </span>
              )}
            </p>
          )}
        </div>
        <button
          onClick={loadDashboard}
          className="text-slate-400 hover:text-slate-600 transition-colors"
          title="Refresh dashboard"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Overall progress bar */}
      <div className="bg-white border border-slate-200 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-slate-700">Overall Journey</span>
          <span className="text-sm font-bold text-slate-900">{stats.overall_progress_pct}%</span>
        </div>
        <div className="w-full bg-slate-100 rounded-full h-2">
          <div
            className="bg-indigo-600 h-2 rounded-full transition-all duration-700"
            style={{ width: `${stats.overall_progress_pct}%` }}
          />
        </div>
        <div className="flex gap-4 mt-3 text-xs text-slate-500">
          <span><strong className="text-emerald-600">{stats.completed_phases}</strong> completed</span>
          <span><strong className="text-indigo-600">{stats.in_progress_phases}</strong> in progress</span>
          <span><strong className="text-slate-400">{stats.locked_phases}</strong> locked</span>
        </div>
      </div>

      {/* Recommended next action — most prominent */}
      {recommended_next_action && (
        <NextActionCard action={recommended_next_action} />
      )}

      {/* Active blockers */}
      {active_blockers && active_blockers.length > 0 && (
        <BlockerPanel blockers={active_blockers} />
      )}

      {/* Phase journey map */}
      <PhaseJourneyMap phases={dashboard.phases} />

      {/* Evidence / response progress */}
      <EvidenceProgress phases={dashboard.phases} />
    </div>
  )
}

export default ProgressDashboard
