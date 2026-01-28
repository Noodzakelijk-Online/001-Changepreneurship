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
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)

      // Fetch all dashboard data in parallel
      const [metricsRes, profileRes, responsesRes, insightsRes, historyRes] = await Promise.allSettled([
        // Analytics dashboard overview
        fetch('/api/analytics/dashboard/overview', {
          headers: apiService.getHeaders()
        }).then(r => r.ok ? r.json() : null),
        
        // Entrepreneur profile
        fetch('/api/analytics/dashboard/entrepreneur-profile', {
          headers: apiService.getHeaders()
        }).then(r => r.ok ? r.json() : null),
        
        // User's assessment responses
        fetch(`/api/assessment/responses/user/${user.id}`, {
          headers: apiService.getHeaders()
        }).then(r => r.ok ? r.json() : null),
        
        // AI executive summary
        fetch('/api/dashboard/executive-summary', {
          headers: apiService.getHeaders()
        }).then(r => r.ok ? r.json() : null),
        
        // Progress history
        fetch('/api/analytics/dashboard/progress-history', {
          headers: apiService.getHeaders()
        }).then(r => r.ok ? r.json() : null)
      ])

      setData({
        metrics: metricsRes.status === 'fulfilled' ? metricsRes.value?.data : null,
        profile: profileRes.status === 'fulfilled' ? profileRes.value?.data : null,
        responses: responsesRes.status === 'fulfilled' ? responsesRes.value : null,
        insights: insightsRes.status === 'fulfilled' ? insightsRes.value?.data : null,
        progressHistory: historyRes.status === 'fulfilled' ? historyRes.value?.data : null
      })

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
