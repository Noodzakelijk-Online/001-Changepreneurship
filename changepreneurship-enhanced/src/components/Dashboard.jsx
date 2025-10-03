import React, { useState, useEffect } from 'react';
import AIRecommendations from './AIRecommendations';
import PrinciplesSearch from './PrinciplesSearch';
import './Dashboard.css';

const Dashboard = ({ user = null, assessmentResults = null }) => {
  const [activeTab, setActiveTab] = useState('recommendations');
  const [userStage, setUserStage] = useState(null);
  const [focusAreas, setFocusAreas] = useState([]);

  useEffect(() => {
    if (assessmentResults) {
      const stage = determineUserStage(assessmentResults);
      setUserStage(stage);

      const areas = determineFocusAreas(assessmentResults);
      setFocusAreas(areas);
    }
  }, [assessmentResults]);

  const determineUserStage = (results) => {
    if (!results || !results.scores) return 'ideation';

    const scores = results.scores;
    const totalScore = Object.values(scores).reduce((sum, score) => sum + score, 0);
    const averageScore = totalScore / Object.keys(scores).length;

    if (averageScore < 30) return 'ideation';
    if (averageScore < 50) return 'validation';
    if (averageScore < 70) return 'early_stage';
    if (averageScore < 85) return 'growth';
    return 'scaling';
  };

  const determineFocusAreas = (results) => {
    if (!results || !results.scores) return [];

    const scores = results.scores;
    const sortedAreas = Object.entries(scores)
      .sort(([,a], [,b]) => a - b)
      .slice(0, 3)
      .map(([area]) => area);

    const areaMapping = {
      'idea_validation': 'customer_validation',
      'market_research': 'market_analysis',
      'business_model': 'business_model',
      'team_building': 'team_building',
      'funding': 'fundraising',
      'product_development': 'product_development',
      'marketing': 'marketing',
      'sales': 'sales',
      'operations': 'operations',
      'leadership': 'leadership'
    };

    return sortedAreas.map(area => areaMapping[area] || area).filter(Boolean);
  };

  const formatStage = (stage) => {
    if (!stage) return 'Getting Started';
    return stage.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getStageDescription = (stage) => {
    const descriptions = {
      'ideation': "You're in the idea generation and opportunity recognition phase.",
      'validation': "You're validating your business concept and testing assumptions.",
      'early_stage': "You're building your MVP and finding product-market fit.",
      'growth': "You're scaling your business and optimizing operations.",
      'scaling': "You're expanding rapidly and building sustainable systems."
    };
    return descriptions[stage] || 'Welcome to your entrepreneurship journey!';
  };

  const tabs = [
    { id: 'recommendations', label: '🎯 Personalized Recommendations', icon: '🎯' },
    { id: 'explore', label: '🔍 Explore All Principles', icon: '🔍' },
    { id: 'progress', label: '📊 Your Progress', icon: '📊' }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
      <div className="welcome-section">
        <h1>Welcome back{user?.name ? `, ${user.name}` : ''}! 👋</h1>
        <div className="user-status">
          <div className="current-stage">
            <span className="stage-label">Current Stage:</span>
            <span className="stage-value">{formatStage(userStage)}</span>
          </div>
          <p className="stage-description">{getStageDescription(userStage)}</p>
        </div>
      </div>

      {focusAreas.length > 0 && (
        <div className="focus-areas">
          <h3>🎯 Your Focus Areas:</h3>
          <div className="focus-tags">
            {focusAreas.map((area, index) => (
              <span key={index} className="focus-tag">
                {area.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </span>
            ))}
          </div>
        </div>
      )}
      </div>

      <div className="dashboard-navigation">
        <div className="tab-buttons">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="dashboard-content">
        {activeTab === 'recommendations' && (
          <div className="recommendations-tab">
            <AIRecommendations
              userStage={userStage}
              focusAreas={focusAreas}
              limit={8}
              title="🤖 Personalized Recommendations for You"
            />
            {userStage && (
              <AIRecommendations
                stage={userStage}
                limit={5}
                title={`📈 Essential Principles for ${formatStage(userStage)} Stage`}
              />
            )}
          </div>
        )}

        {activeTab === 'explore' && (
          <div className="explore-tab">
            <PrinciplesSearch />
          </div>
        )}

        {activeTab === 'progress' && (
          <div className="progress-tab">
            <div className="progress-content">
              <h3>📊 Your Entrepreneurship Journey</h3>

              {assessmentResults ? (
                <div className="assessment-summary">
                  <div className="overall-score">
                    <h4>Overall Readiness Score</h4>
                    <div className="score-circle">
                      <span className="score-value">
                        {Math.round(Object.values(assessmentResults.scores || {}).reduce((sum, score) => sum + score, 0) / Object.keys(assessmentResults.scores || {}).length)}%
                      </span>
                    </div>
                  </div>

                  <div className="area-scores">
                    <h4>Area Breakdown</h4>
                    <div className="scores-grid">
                      {Object.entries(assessmentResults.scores || {}).map(([area, score]) => (
                        <div key={area} className="score-item">
                          <span className="area-name">
                            {area.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </span>
                          <div className="score-bar">
                            <div 
                              className="score-fill" 
                              style={{ width: `${score}%` }}
                            ></div>
                          </div>
                          <span className="score-number">{score}%</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="next-steps">
                    <h4>🎯 Recommended Next Steps</h4>
                    <AIRecommendations
                      focusAreas={focusAreas.slice(0, 2)}
                      limit={3}
                      title="Priority Actions Based on Your Assessment"
                    />
                  </div>
                </div>
              ) : (
                <div className="no-assessment">
                  <p>Take an assessment to see your progress and get personalized recommendations!</p>
                  <button className="cta-button">
                    📝 Take Assessment
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
