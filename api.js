/**
 * API Service for Changepreneurship Platform
 * Handles all backend communication with proper session token management
 */

// Get API base URL from environment variable with fallback
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

// Storage keys for session management
const SESSION_TOKEN_KEY = import.meta.env.VITE_SESSION_STORAGE_KEY || 'changepreneurship_session_token'
const USER_DATA_KEY = import.meta.env.VITE_USER_STORAGE_KEY || 'changepreneurship_user_data'

class ApiService {
  constructor() {
    this.sessionToken = localStorage.getItem(SESSION_TOKEN_KEY)
    this.userData = this.getUserData()
  }

  /**
   * Get headers with authentication
   * @returns {Object} Headers object with Content-Type and Authorization
   */
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    }
    
    if (this.sessionToken) {
      headers['Authorization'] = `Bearer ${this.sessionToken}`
    }
    
    return headers
  }

  /**
   * Handle API responses with proper error handling
   * @param {Response} response - Fetch response object
   * @returns {Promise<Object>} Parsed JSON response
   */
  async handleResponse(response) {
    let data
    try {
      data = await response.json()
    } catch (error) {
      throw new Error('Invalid response format from server')
    }

    if (!response.ok) {
      const errorMessage = data.error || data.message || `HTTP ${response.status}: ${response.statusText}`
      throw new Error(errorMessage)
    }

    return data
  }

  /**
   * Store session token and user data
   * @param {string} sessionToken - Session token from backend
   * @param {Object} userData - User data object
   * @param {string} expiresAt - Token expiration timestamp
   */
  setSession(sessionToken, userData, expiresAt) {
    this.sessionToken = sessionToken
    this.userData = userData

    if (sessionToken) {
      localStorage.setItem(SESSION_TOKEN_KEY, sessionToken)
      localStorage.setItem(USER_DATA_KEY, JSON.stringify({
        ...userData,
        expiresAt
      }))
    } else {
      this.clearSession()
    }
  }

  /**
   * Clear session data
   */
  clearSession() {
    this.sessionToken = null
    this.userData = null
    localStorage.removeItem(SESSION_TOKEN_KEY)
    localStorage.removeItem(USER_DATA_KEY)
  }

  /**
   * Get stored user data
   * @returns {Object|null} User data or null if not found
   */
  getUserData() {
    try {
      const stored = localStorage.getItem(USER_DATA_KEY)
      return stored ? JSON.parse(stored) : null
    } catch (error) {
      console.warn('Failed to parse stored user data:', error)
      return null
    }
  }

  /**
   * Check if session is expired
   * @returns {boolean} True if session is expired
   */
  isSessionExpired() {
    if (!this.userData || !this.userData.expiresAt) {
      return true
    }

    const expirationTime = new Date(this.userData.expiresAt).getTime()
    const currentTime = new Date().getTime()
    
    return currentTime >= expirationTime
  }

  /**
   * Check if user is authenticated
   * @returns {boolean} True if user has valid session
   */
  isAuthenticated() {
    return !!(this.sessionToken && !this.isSessionExpired())
  }

  // ==================== AUTHENTICATION METHODS ====================

  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} Registration response
   */
  async register(userData) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(userData)
    })
    
    const data = await this.handleResponse(response)
    
    // Store session token from backend response
    if (data.session_token) {
      this.setSession(data.session_token, data.user, data.expires_at)
    }
    
    return data
  }

  /**
   * Login user
   * @param {Object} credentials - Login credentials
   * @returns {Promise<Object>} Login response
   */
  async login(credentials) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(credentials)
    })
    
    const data = await this.handleResponse(response)
    
    // Store session token from backend response
    if (data.session_token) {
      this.setSession(data.session_token, data.user, data.expires_at)
    }
    
    return data
  }

  /**
   * Logout user
   * @returns {Promise<Object>} Logout response
   */
  async logout() {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: this.getHeaders()
      })
      
      await this.handleResponse(response)
    } catch (error) {
      console.warn('Logout request failed:', error.message)
      // Continue with local cleanup even if server request fails
    } finally {
      this.clearSession()
    }
    
    return { message: 'Logout successful' }
  }

  /**
   * Verify current session
   * @returns {Promise<Object>} Session verification response
   */
  async verifySession() {
    if (!this.sessionToken) {
      throw new Error('No authentication token')
    }

    if (this.isSessionExpired()) {
      this.clearSession()
      throw new Error('Session expired')
    }

    const response = await fetch(`${API_BASE_URL}/auth/verify`, {
      method: 'GET',
      headers: this.getHeaders()
    })
    
    const data = await this.handleResponse(response)
    
    // Update user data if provided
    if (data.user) {
      this.setSession(this.sessionToken, data.user, this.userData?.expiresAt)
    }
    
    return data
  }

  /**
   * Get user profile
   * @returns {Promise<Object>} User profile data
   */
  async getProfile() {
    const response = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: 'GET',
      headers: this.getHeaders()
    })
    
    return this.handleResponse(response)
  }

  // ==================== ASSESSMENT METHODS ====================

  /**
   * Get all assessment phases
   * @returns {Promise<Object>} Assessment phases data
   */
  async getAssessmentPhases() {
    const response = await fetch(`${API_BASE_URL}/assessment/phases`, {
      method: 'GET',
      headers: this.getHeaders()
    })
    
    return this.handleResponse(response)
  }

  /**
   * Start a new assessment phase
   * @param {string} phaseId - Assessment phase identifier
   * @returns {Promise<Object>} Assessment start response
   */
  async startAssessmentPhase(phaseId) {
    const response = await fetch(`${API_BASE_URL}/assessment/start/${phaseId}`, {
      method: 'POST',
      headers: this.getHeaders()
    })
    
    return this.handleResponse(response)
  }

  /**
   * Save assessment response
   * @param {string} assessmentId - Assessment identifier
   * @param {Object} responseData - Response data
   * @returns {Promise<Object>} Save response
   */
  async saveAssessmentResponse(assessmentId, responseData) {
    const response = await fetch(`${API_BASE_URL}/assessment/${assessmentId}/response`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(responseData)
    })
    
    return this.handleResponse(response)
  }

  /**
   * Update assessment progress
   * @param {string} assessmentId - Assessment identifier
   * @param {Object} progressData - Progress data
   * @returns {Promise<Object>} Update response
   */
  async updateAssessmentProgress(assessmentId, progressData) {
    const response = await fetch(`${API_BASE_URL}/assessment/${assessmentId}/progress`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(progressData)
    })
    
    return this.handleResponse(response)
  }

  /**
   * Get assessment responses
   * @param {string} assessmentId - Assessment identifier
   * @returns {Promise<Object>} Assessment responses
   */
  async getAssessmentResponses(assessmentId) {
    const response = await fetch(`${API_BASE_URL}/assessment/${assessmentId}/responses`, {
      method: 'GET',
      headers: this.getHeaders()
    })
    
    return this.handleResponse(response)
  }

  /**
   * Update entrepreneur profile
   * @param {Object} profileData - Profile data
   * @returns {Promise<Object>} Update response
   */
  async updateEntrepreneurProfile(profileData) {
    const response = await fetch(`${API_BASE_URL}/assessment/profile/update`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(profileData)
    })
    
    return this.handleResponse(response)
  }

  // ==================== ANALYTICS METHODS ====================

  /**
   * Get dashboard overview
   * @returns {Promise<Object>} Dashboard data
   */
  async getDashboardOverview() {
    const response = await fetch(`${API_BASE_URL}/analytics/dashboard/overview`, {
      method: 'GET',
      headers: this.getHeaders()
    })
    
    return this.handleResponse(response)
  }

  /**
   * Get progress history
   * @param {number} days - Number of days to retrieve
   * @returns {Promise<Object>} Progress history data
   */
  async getProgressHistory(days = 30) {
    const response = await fetch(`${API_BASE_URL}/analytics/dashboard/progress-history?days=${days}`, {
      method: 'GET',
      headers: this.getHeaders()
    })
    
    return this.handleResponse(response)
  }

  /**
   * Get entrepreneur profile analytics
   * @returns {Promise<Object>} Profile analytics data
   */
  async getEntrepreneurProfileAnalytics() {
    const response = await fetch(`${API_BASE_URL}/analytics/dashboard/entrepreneur-profile`, {
      method: 'GET',
      headers: this.getHeaders()
    })
    
    return this.handleResponse(response)
  }

  /**
   * Get personalized recommendations
   * @returns {Promise<Object>} Recommendations data
   */
  async getRecommendations() {
    const response = await fetch(`${API_BASE_URL}/analytics/dashboard/recommendations`, {
      method: 'GET',
      headers: this.getHeaders()
    })
    
    return this.handleResponse(response)
  }

  /**
   * Get assessment statistics
   * @returns {Promise<Object>} Assessment statistics
   */
  async getAssessmentStatistics() {
    const response = await fetch(`${API_BASE_URL}/analytics/dashboard/assessment-stats`, {
      method: 'GET',
      headers: this.getHeaders()
    })
    
    return this.handleResponse(response)
  }

  // ==================== UTILITY METHODS ====================

  /**
   * Get current user data
   * @returns {Object|null} Current user data
   */
  getCurrentUser() {
    return this.userData
  }

  /**
   * Get current session token
   * @returns {string|null} Current session token
   */
  getSessionToken() {
    return this.sessionToken
  }

  /**
   * Get API base URL
   * @returns {string} API base URL
   */
  getApiBaseUrl() {
    return API_BASE_URL
  }

  /**
   * Check if API is available
   * @returns {Promise<boolean>} True if API is available
   */
  async checkApiHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      return response.ok
    } catch (error) {
      console.warn('API health check failed:', error.message)
      return false
    }
  }
}

// Create and export a singleton instance
const apiService = new ApiService()

// Auto-verify session on initialization if token exists
if (apiService.isAuthenticated()) {
  apiService.verifySession().catch(error => {
    console.warn('Session verification failed on initialization:', error.message)
    apiService.clearSession()
  })
}

export default apiService

