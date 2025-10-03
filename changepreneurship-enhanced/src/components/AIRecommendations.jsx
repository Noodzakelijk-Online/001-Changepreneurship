import React, { useState, useEffect } from 'react';
import ApiService from '../services/api';
import './AIRecommendations.css';

const AIRecommendations = ({ 
  userStage = null, 
  focusAreas = [], 
  category = null, 
  stage = null,
  searchQuery = null,
  limit = 5,
  title = "AI-Powered Recommendations"
}) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedCards, setExpandedCards] = useState(new Set());

  useEffect(() => {
    fetchRecommendations();
  }, [userStage, focusAreas, category, stage, searchQuery, limit]);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);

    try {
      let response;

      // Handle search query first
      if (searchQuery) {
        response = await ApiService.searchPrinciples(searchQuery, limit);
      }
      // If we have user stage and focus areas, get personalized recommendations
      else if (userStage || focusAreas.length > 0) {
        response = await ApiService.getRecommendations({
          user_stage: userStage,
          focus_areas: focusAreas,
          limit: limit
        });
      }
      // If we have specific category or stage filters
      else if (category || stage) {
        response = await ApiService.getPrinciples({
          category: category,
          stage: stage,
          limit: limit
        });
      }
      // Default: get general principles
      else {
        response = await ApiService.getPrinciples({ limit: limit });
      }

      if (response.success) {
        setRecommendations(response.data);
      } else {
        setError(response.error || 'Failed to fetch recommendations');
      }
    } catch (err) {
      setError(err.message || 'An error occurred while fetching recommendations');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpanded = (principleId) => {
    const newExpanded = new Set(expandedCards);
    if (newExpanded.has(principleId)) {
      newExpanded.delete(principleId);
    } else {
      newExpanded.add(principleId);
    }
    setExpandedCards(newExpanded);
  };

  const formatCategory = (category) => {
    return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatStage = (stage) => {
    return stage.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return (
      <div className="ai-recommendations">
        <h3>{title}</h3>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading personalized recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ai-recommendations">
        <h3>{title}</h3>
        <div className="error-message">
          <p>⚠️ {error}</p>
          <button onClick={fetchRecommendations} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="ai-recommendations">
        <h3>{title}</h3>
        <div className="no-recommendations">
          <p>No recommendations available at the moment.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-recommendations">
      <h3>{title}</h3>
      <div className="recommendations-grid">
        {recommendations.map((principle) => {
          const isExpanded = expandedCards.has(principle.id);
          
          return (
            <div key={principle.id} className={`recommendation-card ${isExpanded ? 'expanded' : ''}`}>
              <div className="card-header">
                <h4 className="principle-title">{principle.title}</h4>
                <div className="principle-meta">
                  {principle.categories && principle.categories.length > 0 && (
                    <div className="categories">
                      {principle.categories.slice(0, 2).map((cat, index) => (
                        <span key={index} className="category-tag">
                          {formatCategory(cat)}
                        </span>
                      ))}
                    </div>
                  )}
                  {principle.business_stage && principle.business_stage.length > 0 && (
                    <div className="stages">
                      {principle.business_stage.slice(0, 2).map((stage, index) => (
                        <span key={index} className="stage-tag">
                          {formatStage(stage)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="card-content">
                <p className="principle-summary">{principle.short_summary}</p>

                {isExpanded && (
                  <div className="expanded-content">
                    {principle.actionable_steps && principle.actionable_steps.length > 0 && (
                      <div className="actionable-steps">
                        <h5>🎯 Action Steps:</h5>
                        <ul>
                          {principle.actionable_steps.map((step, index) => (
                            <li key={index}>{step}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {principle.common_risks && principle.common_risks.length > 0 && (
                      <div className="common-risks">
                        <h5>⚠️ Common Risks:</h5>
                        <ul>
                          {principle.common_risks.map((risk, index) => (
                            <li key={index}>{risk}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {principle.source && (
                      <div className="source">
                        <h5>📚 Source:</h5>
                        <p>{principle.source}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="card-footer">
                <button 
                  className="expand-button"
                  onClick={() => toggleExpanded(principle.id)}
                >
                  {isExpanded ? 'Show Less' : 'Show More'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="recommendations-footer">
        <p className="powered-by">
          🤖 Powered by comprehensive analysis of 450+ entrepreneurship books
        </p>
      </div>
    </div>
  );
};

export default AIRecommendations;
