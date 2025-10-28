import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Brain, Target, TrendingUp, AlertCircle, CheckCircle, ArrowRight, Award, Shield } from 'lucide-react';
import './AIRecommendationsReal.css';

const AIRecommendationsReal = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchRecommendations();
  }, [user]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Use test user for demo
      const userId = user?.id || 3;
      const response = await fetch(`http://localhost:5000/api/ai/recommendations/${userId}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }
      
      const result = await response.json();
      setData(result.data);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getProbabilityColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 65) return 'good';
    if (score >= 50) return 'moderate';
    return 'needs-improvement';
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      'Critical': 'critical',
      'High': 'high',
      'Medium': 'medium',
      'Low': 'low'
    };
    return colors[priority] || 'medium';
  };

  if (loading) {
    return (
      <div className="ai-recommendations-real">
        <div className="loading-state">
          <Brain className="loading-icon" />
          <p>AI analyzing your assessment data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ai-recommendations-real">
        <div className="error-state">
          <AlertCircle size={48} />
          <h3>Unable to Load Recommendations</h3>
          <p>{error}</p>
          <button onClick={fetchRecommendations} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const { founder_profile, success_probability, strengths, gaps, recommendations, next_steps, risks, ai_confidence } = data;

  return (
    <div className="ai-recommendations-real">
      {/* Header */}
      <div className="recommendations-header">
        <div className="header-content">
          <div className="header-title">
            <Brain className="header-icon" />
            <div>
              <h1>AI-Driven Recommendations</h1>
              <p>Personalized insights based on your assessment responses</p>
            </div>
          </div>
          <div className="ai-confidence-badge">
            <span className="confidence-label">AI Confidence</span>
            <span className="confidence-value">{ai_confidence}%</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="recommendations-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'recommendations' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendations')}
        >
          Recommendations
        </button>
        <button 
          className={`tab ${activeTab === 'action-plan' ? 'active' : ''}`}
          onClick={() => setActiveTab('action-plan')}
        >
          Action Plan
        </button>
        <button 
          className={`tab ${activeTab === 'risks' ? 'active' : ''}`}
          onClick={() => setActiveTab('risks')}
        >
          Risk Assessment
        </button>
      </div>

      {/* Content */}
      <div className="recommendations-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {/* Founder Profile */}
            <div className="profile-card">
              <div className="card-header">
                <Award className="card-icon" />
                <h2>Your Founder Profile</h2>
              </div>
              <div className="profile-details">
                <div className="profile-item">
                  <span className="profile-label">Archetype</span>
                  <span className="profile-value archetype">{founder_profile.archetype}</span>
                </div>
                <div className="profile-item">
                  <span className="profile-label">Risk Tolerance</span>
                  <span className="profile-value">{founder_profile.risk_tolerance}</span>
                </div>
                <div className="profile-item">
                  <span className="profile-label">Readiness Level</span>
                  <span className="profile-value">{founder_profile.readiness_level}</span>
                </div>
                <div className="profile-item">
                  <span className="profile-label">Motivation Type</span>
                  <span className="profile-value">{founder_profile.motivation_type}</span>
                </div>
              </div>
            </div>

            {/* Success Probability */}
            <div className="probability-card">
              <div className="card-header">
                <TrendingUp className="card-icon" />
                <h2>Success Probability</h2>
              </div>
              <div className="probability-content">
                <div className={`probability-score ${getProbabilityColor(success_probability.score)}`}>
                  <div className="score-circle">
                    <span className="score-number">{success_probability.score}%</span>
                  </div>
                  <p className="score-category">{success_probability.category}</p>
                </div>
                <div className="probability-factors">
                  <h3>Contributing Factors</h3>
                  {success_probability.factors && Object.entries(success_probability.factors).map(([key, value]) => (
                    <div key={key} className="factor-item">
                      <span className="factor-label">{key.replace(/_/g, ' ')}</span>
                      <div className="factor-bar">
                        <div 
                          className="factor-fill" 
                          style={{ width: `${(value / 20) * 100}%` }}
                        />
                      </div>
                      <span className="factor-value">+{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Strengths */}
            <div className="strengths-card">
              <div className="card-header">
                <CheckCircle className="card-icon success" />
                <h2>Your Strengths</h2>
              </div>
              <div className="strengths-grid">
                {strengths.length > 0 ? (
                  strengths.map((strength, index) => (
                    <div key={index} className="strength-item">
                      <div className="strength-header">
                        <h3>{strength.title}</h3>
                        <span className={`impact-badge ${strength.impact.toLowerCase()}`}>
                          {strength.impact} Impact
                        </span>
                      </div>
                      <p>{strength.description}</p>
                    </div>
                  ))
                ) : (
                  <p className="no-data">Complete more assessments to identify your strengths</p>
                )}
              </div>
            </div>

            {/* Gaps */}
            <div className="gaps-card">
              <div className="card-header">
                <AlertCircle className="card-icon warning" />
                <h2>Areas for Improvement</h2>
              </div>
              <div className="gaps-list">
                {gaps.length > 0 ? (
                  gaps.map((gap, index) => (
                    <div key={index} className="gap-item">
                      <div className="gap-header">
                        <h3>{gap.title}</h3>
                        <span className={`priority-badge ${getPriorityBadge(gap.priority)}`}>
                          {gap.priority}
                        </span>
                      </div>
                      <p>{gap.description}</p>
                    </div>
                  ))
                ) : (
                  <p className="no-data">Great! No major gaps identified</p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="recommendations-tab">
            <div className="recommendations-list">
              {recommendations.length > 0 ? (
                recommendations.map((rec, index) => (
                  <div key={index} className="recommendation-card">
                    <div className="recommendation-header">
                      <div className="rec-title-section">
                        <span className="rec-category">{rec.category}</span>
                        <h3>{rec.title}</h3>
                      </div>
                      <div className="rec-meta">
                        <span className={`priority-badge ${getPriorityBadge(rec.priority)}`}>
                          {rec.priority}
                        </span>
                        <span className="timeframe">{rec.timeframe}</span>
                      </div>
                    </div>
                    <p className="rec-description">{rec.description}</p>
                    {rec.resources && rec.resources.length > 0 && (
                      <div className="rec-resources">
                        <strong>Resources:</strong>
                        <ul>
                          {rec.resources.map((resource, idx) => (
                            <li key={idx}>{resource}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="no-recommendations">
                  <Target size={48} />
                  <h3>Complete Assessments to Get Recommendations</h3>
                  <p>Start with the Self Discovery Assessment to receive personalized recommendations</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'action-plan' && (
          <div className="action-plan-tab">
            <div className="next-steps-card">
              <div className="card-header">
                <Target className="card-icon" />
                <h2>Your Action Plan</h2>
              </div>
              <div className="steps-timeline">
                {next_steps.length > 0 ? (
                  next_steps.map((step, index) => (
                    <div key={index} className="step-item">
                      <div className="step-number">{step.step_number}</div>
                      <div className="step-content">
                        <h3>{step.action}</h3>
                        <p>{step.description}</p>
                        <div className="step-meta">
                          <span className="step-time">⏱ {step.estimated_time}</span>
                          <span className={`step-status ${step.status}`}>
                            {step.status}
                          </span>
                        </div>
                      </div>
                      {index < next_steps.length - 1 && (
                        <ArrowRight className="step-arrow" />
                      )}
                    </div>
                  ))
                ) : (
                  <p className="no-data">No action steps available yet</p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'risks' && (
          <div className="risks-tab">
            <div className="risks-card">
              <div className="card-header">
                <Shield className="card-icon" />
                <h2>Risk Assessment</h2>
              </div>
              <div className="risks-list">
                {risks.length > 0 ? (
                  risks.map((risk, index) => (
                    <div key={index} className="risk-item">
                      <div className="risk-header">
                        <div>
                          <span className="risk-category">{risk.category}</span>
                          <h3>{risk.title}</h3>
                        </div>
                        <span className={`severity-badge ${risk.severity.toLowerCase()}`}>
                          {risk.severity}
                        </span>
                      </div>
                      <p className="risk-description">{risk.description}</p>
                      <div className="risk-mitigation">
                        <strong>Mitigation Strategy:</strong>
                        <p>{risk.mitigation}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="no-risks">
                    <CheckCircle size={48} className="success" />
                    <h3>No Major Risks Identified</h3>
                    <p>Your assessment data shows good preparation</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Data Source Attribution */}
      <div className="data-attribution">
        <p>
          💡 These recommendations are generated by AI analysis of your assessment responses. 
          Data confidence: <strong>{ai_confidence}%</strong>
        </p>
      </div>
    </div>
  );
};

export default AIRecommendationsReal;
