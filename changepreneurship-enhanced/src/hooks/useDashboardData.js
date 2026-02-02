import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import apiService from '../services/api'

/**
 * Custom hook for fetching all dashboard data
 * Consolidates multiple API calls into a single hook
 */
export const useDashboardData = () => {
  const { user, isAuthenticated } = useAuth()
  const [data, setData] = useState({
    metrics: null,
    profile: null,
    responses: null,
    insights: null,
    progressHistory: null
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchAllData = async () => {
    if (!isAuthenticated || !user?.id) {
      console.log('[useDashboardData] Not authenticated or no user ID', { isAuthenticated, userId: user?.id })
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      console.log('[useDashboardData] Fetching dashboard data for user:', user.id)

      // Fetch all dashboard data in parallel
      const [metricsRes, profileRes, responsesRes, insightsRes, historyRes] = await Promise.allSettled([
        // Analytics dashboard overview
        fetch('/api/analytics/dashboard/overview', {
          headers: apiService.getHeaders()
        }).then(r => {
          console.log('[useDashboardData] Overview response:', r.status, r.ok)
          return r.ok ? r.json() : null
        }),
        
        // Entrepreneur profile
        fetch('/api/analytics/dashboard/entrepreneur-profile', {
          headers: apiService.getHeaders()
        }).then(r => {
          console.log('[useDashboardData] Profile response:', r.status, r.ok)
          return r.ok ? r.json() : null
        }),
        
        // User's assessment responses
        fetch(`/api/assessment/responses/user/${user.id}`, {
          headers: apiService.getHeaders()
        }).then(r => {
          console.log('[useDashboardData] Responses response:', r.status, r.ok)
          return r.ok ? r.json() : null
        }),
        
        // AI executive summary
        fetch('/api/dashboard/executive-summary', {
          headers: apiService.getHeaders()
        }).then(r => {
          console.log('[useDashboardData] Insights response:', r.status, r.ok)
          return r.ok ? r.json() : null
        }),
        
        // Progress history
        fetch('/api/analytics/dashboard/progress-history', {
          headers: apiService.getHeaders()
        }).then(r => {
          console.log('[useDashboardData] History response:', r.status, r.ok)
          return r.ok ? r.json() : null
        })
      ])

      const newData = {
        metrics: metricsRes.status === 'fulfilled' ? metricsRes.value?.data : null,
        profile: profileRes.status === 'fulfilled' ? profileRes.value?.data : null,
        responses: responsesRes.status === 'fulfilled' ? responsesRes.value : null,
        insights: insightsRes.status === 'fulfilled' ? insightsRes.value?.data : null,
        progressHistory: historyRes.status === 'fulfilled' ? historyRes.value?.data : null
      }
      
      console.log('[useDashboardData] Fetched data:', {
        hasMetrics: !!newData.metrics,
        hasProfile: !!newData.profile,
        hasResponses: !!newData.responses,
        hasInsights: !!newData.insights,
        hasHistory: !!newData.progressHistory,
        metricsProgress: newData.metrics?.overall_progress,
        responsesCount: newData.responses?.total_responses,
        insightsScore: newData.insights?.overall_score,
        insightsKeyInsightsCount: newData.insights?.ai_insights?.key_insights?.length,
        insightsRaw: newData.insights
      })

      setData(newData)

    } catch (err) {
      console.error('Dashboard data fetch error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const refresh = () => {
    fetchAllData()
  }

  useEffect(() => {
    fetchAllData()
  }, [isAuthenticated, user?.id])

  return {
    ...data,
    loading,
    error,
    refresh,
    hasData: !!(data.metrics || data.profile || data.responses || data.insights)
  }
}

export default useDashboardData
