import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'

export const useAssessmentAPI = () => {
  const { isAuthenticated, apiCall } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Auto-save assessment data to backend
  const saveAssessmentData = async (phaseId, data) => {
    if (!isAuthenticated) {
      // Save to localStorage for non-authenticated users
      const existingData = JSON.parse(localStorage.getItem('changepreneurship-assessment') || '{}')
      const updatedData = {
        ...existingData,
        assessmentData: {
          ...existingData.assessmentData,
          [phaseId]: {
            ...existingData.assessmentData?.[phaseId],
            ...data,
            lastUpdated: new Date().toISOString()
          }
        }
      }
      localStorage.setItem('changepreneurship-assessment', JSON.stringify(updatedData))
      return { success: true, data: null }
    }

    try {
      setLoading(true)
      setError(null)

      // Start assessment phase if not already started
      const startResponse = await apiCall(`/assessment/start/${phaseId}`, {
        method: 'POST'
      })

      let assessmentId
      if (startResponse.success) {
        const startData = startResponse.data
        assessmentId = startData.assessment_id
      } else {
        throw new Error('Failed to start assessment phase')
      }

      // Save responses if provided
      if (data.responses) {
        for (const [section, sectionResponses] of Object.entries(data.responses)) {
          for (const [questionId, response] of Object.entries(sectionResponses)) {
            const responseResult = await apiCall(`/assessment/${assessmentId}/response`, {
              method: 'POST',
              body: JSON.stringify({
                question_id: `${section}_${questionId}`,
                response_data: response,
                response_type: typeof response === 'object' ? 'complex' : 'simple',
                section: section
              })
            })

            if (!responseResult.success) {
              throw new Error('Failed to save response')
            }
          }
        }
      }

      // Update progress and completion status
      const progressResponse = await apiCall(`/assessment/${assessmentId}/progress`, {
        method: 'PUT',
        body: JSON.stringify({
          progress_percentage: data.progress || 0,
          completed: data.completed || false,
          assessment_data: data
        })
      })

      if (!progressResponse.success) {
        throw new Error('Failed to update progress')
      }

      const progressData = progressResponse.data || {}

      return { success: true, data: { assessmentId, ...progressData } }
    } catch (err) {
      setError(err.message)
      console.error('Assessment save error:', err)
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }

  // Load assessment data from backend
  const loadAssessmentData = async () => {
    if (!isAuthenticated) {
      const localData = localStorage.getItem('changepreneurship-assessment')
      return localData ? JSON.parse(localData) : null
    }

    try {
      setLoading(true)
      setError(null)

      const response = await apiCall('/assessment/phases')
      if (response.success) {
        return response.data
      } else {
        throw new Error('Failed to load assessment data')
      }
    } catch (err) {
      setError(err.message)
      console.error('Assessment load error:', err)
      return null
    } finally {
      setLoading(false)
    }
  }

  // Save entrepreneur profile
  const saveProfile = async (profileData) => {
    if (!isAuthenticated) {
      const existingData = JSON.parse(localStorage.getItem('changepreneurship-assessment') || '{}')
      const updatedData = {
        ...existingData,
        userProfile: {
          ...existingData.userProfile,
          ...profileData
        }
      }
      localStorage.setItem('changepreneurship-assessment', JSON.stringify(updatedData))
      return { success: true, data: profileData }
    }

    try {
      setLoading(true)
      setError(null)

      const response = await apiCall('/assessment/profile/update', {
        method: 'PUT',
        body: JSON.stringify(profileData)
      })

      if (response.success) {
        return { success: true, data: response.data }
      } else {
        throw new Error('Failed to save profile')
      }
    } catch (err) {
      setError(err.message)
      console.error('Profile save error:', err)
      return { success: false, error: err.message }
    } finally {
      setLoading(false)
    }
  }

  // Get assessment responses for a specific phase
  
const getAssessmentResponses = async (phaseId) => {
  if (!isAuthenticated) {
    const localData = JSON.parse(localStorage.getItem('changepreneurship-assessment') || '{}')
    return localData.assessmentData?.[phaseId]?.responses || {}
  }

  try {
    setLoading(true)
    setError(null)

    // First get the assessment ID for this phase
    const phasesResponse = await apiCall('/assessment/phases')
    if (!phasesResponse.success) {
      throw new Error('Failed to get assessment phases')
    }

    const phase = phasesResponse.data.phases.find(p => p.id === phaseId)
    if (!phase || !phase.assessment_id) {
      return {}
    }

    const responsesResponse = await apiCall(`/assessment/${phase.assessment_id}/responses`)
    if (responsesResponse.success) {
      const responsesData = responsesResponse.data
      return responsesData.responses || {}
    } else {
      throw new Error('Failed to get assessment responses')
    }
  } catch (err) {
    setError(err.message)
    console.error('Get responses error:', err)
    return {}
  } finally {
    setLoading(false)
  }
}

  // Debounced auto-save function
  const debouncedSave = (() => {
    let timeoutId
    return (phaseId, data, delay = 2000) => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(() => {
        saveAssessmentData(phaseId, data)
      }, delay)
    }
  })()

  return {
    loading,
    error,
    saveAssessmentData,
    loadAssessmentData,
    saveProfile,
    getAssessmentResponses,
    debouncedSave
  }
}

