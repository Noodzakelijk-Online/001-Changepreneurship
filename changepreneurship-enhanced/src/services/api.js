/**
 * API Service for Changepreneurship Platform
 * Handles all backend communication with proper session token management
 */

const RAW_BASE =
  typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL
    ? import.meta.env.VITE_API_BASE_URL.trim()
    : '';
// If no explicit base provided, use relative /api so the Vite dev proxy (vite.config.js) can forward to backend.
const API_BASE_URL = RAW_BASE
  ? RAW_BASE.replace(/\/+$/, '')
  : '/api';

const SESSION_TOKEN_KEY =
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_SESSION_STORAGE_KEY) ||
  'changepreneurship_session_token';
const USER_DATA_KEY =
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_USER_STORAGE_KEY) ||
  'changepreneurship_user_data';

class ApiService {
  constructor() {
    if (typeof window !== 'undefined' && window.localStorage) {
      this.sessionToken = localStorage.getItem(SESSION_TOKEN_KEY);
      this.userData = this.getUserData();
    } else {
      this.sessionToken = null;
      this.userData = null;
    }
  }

  getHeaders() {
    const headers = { "Content-Type": "application/json" };
    if (this.sessionToken)
      headers["Authorization"] = `Bearer ${this.sessionToken}`;
    return headers;
  }

  async handleResponse(response) {
    let data = null;
    try {
      data = await response.json();
    } catch {
      // ignore parse errors
    }

    // Flatten standard API responses that wrap payloads in a `data` property
    const resultData =
      data && typeof data === "object" && data !== null && "data" in data
        ? data.data
        : data;

    if (!response.ok) {
      const error =
        (data && (data.error || data.message)) ||
        `HTTP ${response.status}: ${response.statusText}`;
      return { success: false, error };
    }
    return { success: true, data: resultData };
  }

  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: this.getHeaders(),
        credentials: 'include',
        ...options,
      });
      return await this.handleResponse(response);
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  setSession(sessionToken, userData, expiresAt) {
    this.sessionToken = sessionToken;
    this.userData = userData;
    if (typeof window !== 'undefined' && window.localStorage) {
      if (sessionToken) {
        localStorage.setItem(SESSION_TOKEN_KEY, sessionToken);
        localStorage.setItem(
          USER_DATA_KEY,
          JSON.stringify({ ...userData, expiresAt })
        );
      } else {
        this.clearSession();
      }
    }
  }

  clearSession() {
    this.sessionToken = null;
    this.userData = null;
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem(SESSION_TOKEN_KEY);
      localStorage.removeItem(USER_DATA_KEY);
    }
  }

  getUserData() {
    if (typeof window === 'undefined' || !window.localStorage) return null;
    try {
      const raw = localStorage.getItem(USER_DATA_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  isSessionExpired() {
    // If no token at all → expired
    if (!this.sessionToken) return true;
    // If token exists but no expiry stored → optimistically assume valid
    if (!this.userData || !this.userData.expiresAt) return false;
    return Date.now() >= new Date(this.userData.expiresAt).getTime();
  }

  isAuthenticated() {
    return !!(this.sessionToken && !this.isSessionExpired());
  }

  async register(userData) {
    const result = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    if (result.success && result.data?.session_token)
      this.setSession(result.data.session_token, result.data.user, result.data.expires_at);
    return result;
  }

  async login(credentials) {
    const result = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    if (result.success && result.data?.session_token) {
      this.setSession(
        result.data.session_token,
        result.data.user,
        result.data.expires_at
      );
    }
    return result;
  }

  async logout() {
    try {
      await this.request('/auth/logout', { method: 'POST' });
    } catch {
      // ignore network errors during logout
    } finally {
      this.clearSession();
    }
    return { message: "Logout successful" };
  }

  async verifySession() {
    if (!this.sessionToken)
      return { success: false, error: "No authentication token" };
    if (this.isSessionExpired()) {
      this.clearSession();
      return { success: false, error: "Session expired" };
    }
    const result = await this.request('/auth/verify');
    if (result.success && result.data?.user)
      this.setSession(
        this.sessionToken,
        result.data.user,
        this.userData?.expiresAt
      );
    return result;
  }

  async getProfile() {
    const res = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    if (res.status === 404) {
      return { success: true, data: { user: null, profile: null } };
    }

    return this.handleResponse(res);
  }

  // ==================== ASSESSMENT METHODS ====================

  async getAssessmentPhases() {
    return this.request('/assessment/phases');
  }

  async startAssessmentPhase(phaseId) {
    return this.request(`/assessment/start/${phaseId}`, { method: 'POST' });
  }

  async saveAssessmentResponse(assessmentId, responseData) {
    return this.request(`/assessment/${assessmentId}/response`, {
      method: 'POST',
      body: JSON.stringify(responseData),
    });
  }

  async updateAssessmentProgress(assessmentId, progressPercentage) {
    return this.request(`/assessment/${assessmentId}/progress`, {
      method: 'PUT',
      body: JSON.stringify({ progress_percentage: progressPercentage }),
    });
  }

  async getAssessmentResponses(assessmentId) {
    return this.request(`/assessment/${assessmentId}/responses`);
  }

  async updateEntrepreneurProfile(profileData) {
    return this.request('/assessment/profile/update', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  // ==================== ANALYTICS METHODS ====================

  /**
   * Get dashboard overview
   * @returns {Promise<Object>} Dashboard data
   */
  async getDashboardOverview() {
    return this.request('/analytics/dashboard/overview');
  }

  /**
   * Get progress history
   * @param {number} days - Number of days to retrieve
   * @returns {Promise<Object>} Progress history data
   */
  async getProgressHistory(days = 30) {
    return this.request(`/analytics/dashboard/progress-history?days=${days}`);
  }

  /**
   * Get entrepreneur profile analytics
   * @returns {Promise<Object>} Profile analytics data
   */
  async getEntrepreneurProfileAnalytics() {
    return this.request('/analytics/dashboard/entrepreneur-profile');
  }

  /**
   * Get personalized principle recommendations
   * @param {Object} data - Recommendation parameters
   */
  async getRecommendations(data) {
    return this.request('/principles/recommendations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Fetch entrepreneurship principles
   * @param {Object} params - Filter options
   * @param {string} [params.category] - Principle category
   * @param {string} [params.stage] - Business stage
   * @param {number} [params.limit] - Max number of results
   * @returns {Promise<Array>} List of principles
   */
  async getPrinciples(params = {}) {
    const query = new URLSearchParams(params).toString();
    const endpoint = query ? `/principles?${query}` : `/principles`;
    return this.request(endpoint);
  }

  /**
   * Get assessment statistics
   * @returns {Promise<Object>} Assessment statistics
   */
  async getAssessmentStatistics() {
    return this.request('/analytics/dashboard/assessment-stats');
  }

  async searchPrinciples(query, limit = 5) {
    return this.getPrinciples({ search: query, limit });
  }

  async getCategories() {
    return this.request('/principles/categories');
  }

  async getStages() {
    return this.request('/principles/stages');
  }

  // ==================== DATA IMPORT METHODS ====================

  /**
   * Upload and parse LinkedIn profile PDF
   * @param {File} file - LinkedIn profile file uploaded by user
   * @returns {Promise<Object>} Parsed LinkedIn data
   */
  async uploadLinkedInData(file) {
    try {
      const formData = new FormData();
      if (file) formData.append('file', file);
      const headers = this.sessionToken
        ? { Authorization: `Bearer ${this.sessionToken}` }
        : {};
      const res = await fetch(`${API_BASE_URL}/data/import/linkedin`, {
        method: 'POST',
        headers,
        body: formData,
      });
      return this.handleResponse(res);
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Upload and parse resume file
   * @param {File} file - Resume file uploaded by user
   * @returns {Promise<Object>} Parsed resume data
   */
  async uploadResume(file) {
    try {
      const formData = new FormData();
      if (file) formData.append('file', file);
      const headers = this.sessionToken
        ? { Authorization: `Bearer ${this.sessionToken}` }
        : {};
      const res = await fetch(`${API_BASE_URL}/data/import/resume`, {
        method: 'POST',
        headers,
        body: formData,
      });
      return this.handleResponse(res);
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Connect financial accounts or upload statements
   * @param {Object} payload - Connection or upload details
   * @returns {Promise<Object>} Parsed financial data
   */
  async connectFinancialAccounts(payload = {}) {
    return this.request('/data/import/financial', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // ==================== UTILITY METHODS ====================

  /**
   * Get current user data
   * @returns {Object|null} Current user data
   */
  getCurrentUser() {
    return this.userData;
  }

  /**
   * Get current session token
   * @returns {string|null} Current session token
   */
  getSessionToken() {
    return this.sessionToken;
  }

  /**
   * Get API base URL
   * @returns {string} API base URL
   */
  getApiBaseUrl() {
    return API_BASE_URL;
  }

  // ==================== AI INSIGHTS REPORT ====================

  /**
   * Get the full AI-powered Entrepreneur + Venture insights report.
   * The backend calls Groq (llama-3.3-70b-versatile) in JSON mode, so every
   * score, insight, sweet-spot and risk-zone is AI-reasoned.
   *
   * @param {boolean} refresh - Force AI regeneration (bypass Redis cache)
   * @returns {Promise<{success: boolean, report: Object}>}
   */
  async getInsightsReport(refresh = false) {
    const qs = refresh ? '?refresh=1' : '';
    const res = await fetch(`${API_BASE_URL}/ai/insights-report${qs}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    return this.handleResponse(res);
  }

  /**
   * Check if API is available
   * @returns {Promise<boolean>} True if API is available
   */
  async checkApiHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      return response.ok;
    } catch (error) {
      console.warn("API health check failed:", error.message);
      return false;
    }
  }
}

// Create and export a singleton instance
const apiService = new ApiService();

// Auto-verify session on initialization if token exists
if (apiService.isAuthenticated()) {
  apiService.verifySession().then((res) => {
    if (!res.success) apiService.clearSession();
  });
}

export default apiService;
