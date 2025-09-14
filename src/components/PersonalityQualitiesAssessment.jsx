import React, { useState, useEffect } from 'react';
import { User, TrendingUp, BarChart3, Eye, CheckCircle, AlertCircle, Star, Target } from 'lucide-react';
import { ContextualValueSlider } from './ContextualValueSlider';
import './PersonalityQualitiesAssessment.css';

const PersonalityQualitiesAssessment = ({ 
  qualities = {}, 
  onQualitiesChange,
  showResults = false 
}) => {
  const [currentQualities, setCurrentQualities] = useState(qualities);
  const [activeCategory, setActiveCategory] = useState('all');
  const [completionStats, setCompletionStats] = useState({});

  // 30 personality qualities from the Dutch exercise
  const personalityQualities = [
    // Core Personality Traits (1-14)
    { id: 'serious', name: 'Is serious', category: 'core', description: 'Approaches situations with gravity and thoughtfulness' },
    { id: 'eager_to_please', name: 'Eager to please others', category: 'social', description: 'Seeks approval and tries to make others happy' },
    { id: 'listens_well', name: 'Listens well', category: 'social', description: 'Pays attention and truly hears what others are saying' },
    { id: 'quick_to_act', name: 'Quick to act without thinking', category: 'decision', description: 'Acts impulsively without considering consequences' },
    { id: 'cheerful', name: 'Is cheerful', category: 'emotional', description: 'Maintains a positive and upbeat attitude' },
    { id: 'sensitive', name: 'Is sensitive', category: 'emotional', description: 'Easily affected by emotions and environmental factors' },
    { id: 'makes_others_comfortable', name: 'Makes others feel comfortable', category: 'social', description: 'Creates a welcoming and relaxed atmosphere for others' },
    { id: 'clear_opinion', name: 'Has a clear opinion', category: 'decision', description: 'Forms and expresses definite viewpoints on matters' },
    { id: 'keeps_agreements', name: 'Keeps agreements', category: 'reliability', description: 'Follows through on commitments and promises' },
    { id: 'thinks_first', name: 'Thinks first, then speaks', category: 'decision', description: 'Considers words carefully before expressing them' },
    { id: 'doesnt_give_up', name: 'Doesn\'t give up easily', category: 'resilience', description: 'Persists through challenges and setbacks' },
    { id: 'gives_up_quickly', name: 'Gives up quickly', category: 'resilience', description: 'Abandons efforts when faced with difficulty' },
    { id: 'thinks_then_acts', name: 'Thinks first, then acts', category: 'decision', description: 'Plans and considers before taking action' },
    { id: 'stands_out_in_group', name: 'Stands out in a group', category: 'social', description: 'Naturally draws attention and stands apart from others' },

    // Extended Qualities (15-30)
    { id: 'tries_new_things', name: 'Tries new things', category: 'growth', description: 'Open to new experiences and willing to experiment' },
    { id: 'has_humor', name: 'Has humor', category: 'emotional', description: 'Uses humor appropriately and makes others laugh' },
    { id: 'solves_problems', name: 'Solves problems independently', category: 'problem_solving', description: 'Tackles challenges without needing help from others' },
    { id: 'not_easily_stressed', name: 'Is not easily stressed', category: 'resilience', description: 'Remains calm under pressure and in difficult situations' },
    { id: 'available_for_others', name: 'Is available for others', category: 'social', description: 'Makes time and effort to help and support others' },
    { id: 'self_confident', name: 'Has self-confidence', category: 'core', description: 'Believes in own abilities and worth' },
    { id: 'keeps_accounting', name: 'Keeps track of things', category: 'organization', description: 'Maintains order and monitors progress systematically' },
    { id: 'knows_strengths', name: 'Knows what they\'re good at', category: 'self_awareness', description: 'Has clear understanding of personal strengths and abilities' },
    { id: 'curious', name: 'Is curious', category: 'growth', description: 'Shows interest in learning and discovering new things' },
    { id: 'ambitious', name: 'Is ambitious', category: 'drive', description: 'Has strong desire to achieve success and advancement' },
    { id: 'innovative_ideas', name: 'Comes up with innovative ideas', category: 'creativity', description: 'Generates original and creative solutions' },
    { id: 'makes_contact_easily', name: 'Makes contact easily', category: 'social', description: 'Naturally connects and communicates with new people' },
    { id: 'talks_well_with_people', name: 'Talks well with people', category: 'social', description: 'Communicates effectively in conversations' },
    { id: 'wants_to_help_world', name: 'Wants to help the world', category: 'purpose', description: 'Motivated by desire to make positive global impact' },
    { id: 'persistent', name: 'Is persistent', category: 'resilience', description: 'Continues efforts despite obstacles or resistance' },
    { id: 'not_strict_with_rules', name: 'Is not strict with rules', category: 'flexibility', description: 'Takes flexible approach to rules and regulations' }
  ];

  const categories = [
    { id: 'all', name: 'All Qualities', icon: <User className="w-4 h-4" />, color: '#6b7280' },
    { id: 'core', name: 'Core Traits', icon: <Star className="w-4 h-4" />, color: '#ff6b35' },
    { id: 'social', name: 'Social Skills', icon: <User className="w-4 h-4" />, color: '#3b82f6' },
    { id: 'decision', name: 'Decision Making', icon: <Target className="w-4 h-4" />, color: '#10b981' },
    { id: 'emotional', name: 'Emotional Intelligence', icon: <Eye className="w-4 h-4" />, color: '#f59e0b' },
    { id: 'resilience', name: 'Resilience', icon: <TrendingUp className="w-4 h-4" />, color: '#8b5cf6' },
    { id: 'growth', name: 'Growth Mindset', icon: <BarChart3 className="w-4 h-4" />, color: '#ef4444' },
    { id: 'reliability', name: 'Reliability', icon: <CheckCircle className="w-4 h-4" />, color: '#22c55e' },
    { id: 'problem_solving', name: 'Problem Solving', icon: <AlertCircle className="w-4 h-4" />, color: '#f97316' },
    { id: 'organization', name: 'Organization', icon: <BarChart3 className="w-4 h-4" />, color: '#06b6d4' },
    { id: 'self_awareness', name: 'Self Awareness', icon: <Eye className="w-4 h-4" />, color: '#84cc16' },
    { id: 'drive', name: 'Drive & Ambition', icon: <TrendingUp className="w-4 h-4" />, color: '#ec4899' },
    { id: 'creativity', name: 'Creativity', icon: <Star className="w-4 h-4" />, color: '#a855f7' },
    { id: 'purpose', name: 'Purpose & Impact', icon: <Target className="w-4 h-4" />, color: '#14b8a6' },
    { id: 'flexibility', name: 'Flexibility', icon: <User className="w-4 h-4" />, color: '#f59e0b' }
  ];

  useEffect(() => {
    calculateCompletionStats();
  }, [currentQualities]);

  const calculateCompletionStats = () => {
    const totalQualities = personalityQualities.length;
    const completedQualities = Object.keys(currentQualities).filter(
      key => currentQualities[key] !== undefined && currentQualities[key] !== null
    ).length;

    const categoryStats = {};
    categories.forEach(category => {
      if (category.id === 'all') return;
      
      const categoryQualities = personalityQualities.filter(q => q.category === category.id);
      const completedInCategory = categoryQualities.filter(q => 
        currentQualities[q.id] !== undefined && currentQualities[q.id] !== null
      ).length;
      
      categoryStats[category.id] = {
        total: categoryQualities.length,
        completed: completedInCategory,
        percentage: categoryQualities.length > 0 ? (completedInCategory / categoryQualities.length) * 100 : 0
      };
    });

    setCompletionStats({
      total: totalQualities,
      completed: completedQualities,
      percentage: (completedQualities / totalQualities) * 100,
      categories: categoryStats
    });
  };

  const handleQualityChange = (qualityId, value) => {
    const updatedQualities = { ...currentQualities, [qualityId]: value };
    setCurrentQualities(updatedQualities);
    onQualitiesChange && onQualitiesChange(updatedQualities);
  };

  const getFilteredQualities = () => {
    if (activeCategory === 'all') {
      return personalityQualities;
    }
    return personalityQualities.filter(quality => quality.category === activeCategory);
  };

  const getCategoryInfo = (categoryId) => {
    return categories.find(cat => cat.id === categoryId) || categories[0];
  };

  const getTopQualities = () => {
    return Object.entries(currentQualities)
      .filter(([_, value]) => value >= 70)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([id, score]) => ({
        ...personalityQualities.find(q => q.id === id),
        score
      }))
      .filter(q => q.name);
  };

  const getPersonalityInsights = () => {
    const topQualities = getTopQualities();
    const insights = [];

    // Leadership insights
    const leadershipQualities = topQualities.filter(q => 
      ['clear_opinion', 'self_confident', 'makes_others_comfortable', 'stands_out_in_group'].includes(q.id)
    );
    if (leadershipQualities.length >= 2) {
      insights.push({
        type: 'leadership',
        title: 'Natural Leadership Potential',
        description: 'Your combination of confidence, clear opinions, and social skills suggests strong leadership capabilities for entrepreneurship.',
        qualities: leadershipQualities.map(q => q.name)
      });
    }

    // Innovation insights
    const innovationQualities = topQualities.filter(q => 
      ['innovative_ideas', 'tries_new_things', 'curious', 'solves_problems'].includes(q.id)
    );
    if (innovationQualities.length >= 2) {
      insights.push({
        type: 'innovation',
        title: 'Innovation & Problem-Solving Strength',
        description: 'Your curiosity, creativity, and problem-solving abilities are ideal for developing innovative business solutions.',
        qualities: innovationQualities.map(q => q.name)
      });
    }

    // Resilience insights
    const resilienceQualities = topQualities.filter(q => 
      ['doesnt_give_up', 'not_easily_stressed', 'persistent', 'thinks_then_acts'].includes(q.id)
    );
    if (resilienceQualities.length >= 2) {
      insights.push({
        type: 'resilience',
        title: 'Entrepreneurial Resilience',
        description: 'Your persistence and stress management abilities will help you navigate the challenges of building a business.',
        qualities: resilienceQualities.map(q => q.name)
      });
    }

    // Social/Team insights
    const socialQualities = topQualities.filter(q => 
      ['listens_well', 'makes_contact_easily', 'talks_well_with_people', 'available_for_others'].includes(q.id)
    );
    if (socialQualities.length >= 2) {
      insights.push({
        type: 'social',
        title: 'Strong Team & Customer Relations',
        description: 'Your social skills and empathy will be valuable for building teams and maintaining customer relationships.',
        qualities: socialQualities.map(q => q.name)
      });
    }

    return insights;
  };

  const renderQualityAssessment = () => (
    <div className="quality-assessment-section">
      <div className="category-filter">
        <div className="filter-buttons">
          {categories.map(category => (
            <button
              key={category.id}
              className={`filter-button ${activeCategory === category.id ? 'active' : ''}`}
              onClick={() => setActiveCategory(category.id)}
              style={{ 
                '--category-color': category.color,
                backgroundColor: activeCategory === category.id ? category.color : 'transparent',
                borderColor: category.color
              }}
            >
              {category.icon}
              <span>{category.name}</span>
              {category.id !== 'all' && completionStats.categories && (
                <div className="completion-badge">
                  {completionStats.categories[category.id]?.completed || 0}/
                  {completionStats.categories[category.id]?.total || 0}
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="qualities-grid">
        {getFilteredQualities().map(quality => {
          const categoryInfo = getCategoryInfo(quality.category);
          return (
            <div key={quality.id} className="quality-item">
              <div className="quality-header">
                <div className="quality-icon" style={{ color: categoryInfo.color }}>
                  {categoryInfo.icon}
                </div>
                <div className="quality-info">
                  <h4 className="quality-name">{quality.name}</h4>
                  <p className="quality-description">{quality.description}</p>
                </div>
              </div>
              
              <div className="quality-slider">
                <ContextualValueSlider
                  question={`How well does "${quality.name}" describe you?`}
                  value={currentQualities[quality.id] || 50}
                  onChange={(value) => handleQualityChange(quality.id, value)}
                  size="small"
                  goalContext={`This quality affects your entrepreneurial approach, decision-making style, and business relationships.`}
                  lowLabel="Not like me at all"
                  highLabel="Perfectly describes me"
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderPersonalityProfile = () => {
    const topQualities = getTopQualities();
    const insights = getPersonalityInsights();

    return (
      <div className="personality-profile-section">
        <div className="profile-header">
          <h3>Your Personality Profile</h3>
          <div className="completion-indicator">
            <div className="completion-circle">
              <div 
                className="completion-fill" 
                style={{ 
                  background: `conic-gradient(#ff6b35 0deg, #ff6b35 ${completionStats.percentage * 3.6}deg, rgba(255,255,255,0.1) ${completionStats.percentage * 3.6}deg, rgba(255,255,255,0.1) 360deg)` 
                }}
              >
                <div className="completion-inner">
                  <span className="completion-text">{Math.round(completionStats.percentage)}%</span>
                </div>
              </div>
            </div>
            <div className="completion-label">
              {completionStats.completed}/{completionStats.total} qualities assessed
            </div>
          </div>
        </div>

        {topQualities.length > 0 && (
          <div className="top-qualities-section">
            <h4>Your Strongest Qualities</h4>
            <div className="top-qualities-grid">
              {topQualities.map((quality, index) => {
                const categoryInfo = getCategoryInfo(quality.category);
                return (
                  <div key={quality.id} className="top-quality-item">
                    <div className="quality-rank">#{index + 1}</div>
                    <div className="quality-content">
                      <div className="quality-icon" style={{ color: categoryInfo.color }}>
                        {categoryInfo.icon}
                      </div>
                      <div className="quality-details">
                        <span className="quality-name">{quality.name}</span>
                        <span className="quality-category">{categoryInfo.name}</span>
                        <div className="quality-bar">
                          <div 
                            className="quality-fill" 
                            style={{ 
                              width: `${quality.score}%`,
                              backgroundColor: categoryInfo.color 
                            }}
                          />
                        </div>
                      </div>
                      <span className="quality-score">{quality.score}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {insights.length > 0 && (
          <div className="personality-insights-section">
            <h4>Entrepreneurial Personality Insights</h4>
            <div className="insights-grid">
              {insights.map((insight, index) => (
                <div key={index} className="insight-card">
                  <div className="insight-header">
                    <div className={`insight-icon ${insight.type}`}>
                      {insight.type === 'leadership' && <Target className="w-5 h-5" />}
                      {insight.type === 'innovation' && <Star className="w-5 h-5" />}
                      {insight.type === 'resilience' && <TrendingUp className="w-5 h-5" />}
                      {insight.type === 'social' && <User className="w-5 h-5" />}
                    </div>
                    <h5>{insight.title}</h5>
                  </div>
                  <p className="insight-description">{insight.description}</p>
                  <div className="insight-qualities">
                    <strong>Based on:</strong> {insight.qualities.join(', ')}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {completionStats.percentage < 100 && (
          <div className="completion-encouragement">
            <AlertCircle className="w-5 h-5" />
            <div>
              <h5>Complete Your Assessment</h5>
              <p>
                You have {completionStats.total - completionStats.completed} qualities left to assess. 
                Complete all assessments for the most accurate personality profile and entrepreneurial insights.
              </p>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="personality-qualities-assessment">
      <div className="assessment-header">
        <h2>Personality Qualities Assessment</h2>
        <p>
          Discover your unique personality profile through this comprehensive assessment of 30 key qualities. 
          Understanding your personality traits helps identify your entrepreneurial strengths and areas for development.
        </p>
      </div>

      <div className="assessment-tabs">
        <div className="tabs-nav">
          <button 
            className={`tab-button ${!showResults ? 'active' : ''}`}
            onClick={() => {/* Toggle assessment view */}}
          >
            <BarChart3 className="w-4 h-4" />
            Assess Qualities
          </button>
          <button 
            className={`tab-button ${showResults ? 'active' : ''}`}
            onClick={() => {/* Toggle results view */}}
          >
            <Eye className="w-4 h-4" />
            Personality Profile
          </button>
        </div>

        <div className="tab-content">
          {!showResults ? renderQualityAssessment() : renderPersonalityProfile()}
        </div>
      </div>
    </div>
  );
};

export default PersonalityQualitiesAssessment;

