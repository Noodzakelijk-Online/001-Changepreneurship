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
      
      // Normalize phase names from backend to frontend format
      // Backend uses "Self Discovery Assessment", frontend uses "self_discovery"
      const phaseNameToId = {
        'Self Discovery Assessment': 'self_discovery',
        'Idea Discovery Assessment': 'idea_discovery',
        'Market Research': 'market_research',
        'Business Pillars Planning': 'business_pillars',
        'Product Concept Testing': 'product_concept_testing',
        'Business Development': 'business_development',
        'Business Prototype Testing': 'business_prototype_testing',
        // Also support backend by_phase keys without " Assessment" suffix
        'Self Discovery': 'self_discovery',
        'Idea Discovery': 'idea_discovery'
      }

      // Normalize backend by_phase keys to frontend phase IDs
      if (newData.responses?.by_phase) {
        console.log('[useDashboardData] Backend by_phase keys:', Object.keys(newData.responses.by_phase))
        const normalizedByPhase = {}
        Object.entries(newData.responses.by_phase).forEach(([backendPhaseName, responses]) => {
          const frontendPhaseId = phaseNameToId[backendPhaseName] || backendPhaseName.toLowerCase().replace(/\s+/g, '_')
          normalizedByPhase[frontendPhaseId] = responses
        })
        newData.responses.by_phase = normalizedByPhase
        console.log('[useDashboardData] Normalized by_phase keys:', Object.keys(normalizedByPhase))
      }
      
      console.log('[useDashboardData] Fetched data:', {
        hasMetrics: !!newData.metrics,
        hasProfile: !!newData.profile,
        hasResponses: !!newData.responses,
        hasInsights: !!newData.insights,
        hasHistory: !!newData.progressHistory,
        metricsProgress: newData.metrics?.overall_progress,
        responsesCount: newData.responses?.total_responses,
        responsesByPhase: newData.responses?.by_phase ? Object.keys(newData.responses.by_phase) : [],
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
