import React, { useState, useEffect } from 'react';
import './MaslowAssessment.css';

const MaslowAssessment = ({ 
  onLevelDetermined,
  onScoreUpdate,
  responses = {}
}) => {
  const [currentLevel, setCurrentLevel] = useState(null);
  const [levelScores, setLevelScores] = useState({
    physiological: 0,
    safety: 0,
    belonging: 0,
    esteem: 0,
    cognitive: 0,
    aesthetic: 0,
    selfActualization: 0,
    transcendence: 0
  });
  const [dominantNeed, setDominantNeed] = useState(null);
  const [entrepreneurialReadiness, setEntrepreneurialReadiness] = useState('exploring');

  const maslowLevels = [
    {
      id: 'physiological',
      level: 1,
      name: 'Physiological Needs',
      icon: '🍽️',
      color: '#48bb78',
      description: 'Food, water, shelter, sleep, clothing, reproduction',
      entrepreneurialContext: 'Survival-driven entrepreneurship',
      questions: [
        'Do you have consistent access to food, water, and shelter?',
        'Are your basic living expenses covered?',
        'Do you have a safe place to sleep every night?'
      ],
      entrepreneurialQuestions: [
        'Are you considering entrepreneurship primarily to meet basic survival needs?',
        'Do you have enough financial stability to take entrepreneurial risks?',
        'Can you afford to potentially lose income while building a business?'
      ],
      indicators: {
        fulfilled: ['stable housing', 'regular meals', 'adequate sleep', 'basic healthcare'],
        unfulfilled: ['food insecurity', 'housing instability', 'sleep deprivation', 'health issues']
      }
    },
    {
      id: 'safety',
      level: 2,
      name: 'Safety Needs',
      icon: '🛡️',
      color: '#ed8936',
      description: 'Security, employment, health, property, stability',
      entrepreneurialContext: 'Security-seeking entrepreneurship',
      questions: [
        'Do you feel secure in your current living situation?',
        'Do you have stable employment or income?',
        'Do you have health insurance and emergency savings?'
      ],
      entrepreneurialQuestions: [
        'Are you pursuing entrepreneurship to create more financial security?',
        'Do you have a financial safety net to support your entrepreneurial journey?',
        'How important is predictable income versus entrepreneurial freedom to you?'
      ],
      indicators: {
        fulfilled: ['job security', 'health insurance', 'emergency fund', 'stable environment'],
        unfulfilled: ['job insecurity', 'financial stress', 'health concerns', 'unstable environment']
      }
    },
    {
      id: 'belonging',
      level: 3,
      name: 'Love and Belonging',
      icon: '❤️',
      color: '#4299e1',
      description: 'Friendship, intimacy, family, connection',
      entrepreneurialContext: 'Community-building entrepreneurship',
      questions: [
        'Do you have meaningful relationships and social connections?',
        'Do you feel loved and accepted by others?',
        'Are you part of communities that matter to you?'
      ],
      entrepreneurialQuestions: [
        'Do you want to build a business that creates community and connection?',
        'How important is it that your entrepreneurial venture aligns with your relationships?',
        'Are you seeking entrepreneurship to find your tribe or professional community?'
      ],
      indicators: {
        fulfilled: ['close relationships', 'social support', 'sense of belonging', 'intimate connections'],
        unfulfilled: ['loneliness', 'social isolation', 'relationship conflicts', 'lack of community']
      }
    },
    {
      id: 'esteem',
      level: 4,
      name: 'Esteem Needs',
      icon: '🏆',
      color: '#805ad5',
      description: 'Respect, recognition, prestige, freedom, achievement',
      entrepreneurialContext: 'Achievement-oriented entrepreneurship',
      questions: [
        'Do you feel respected and valued by others?',
        'Are you confident in your abilities and achievements?',
        'Do you have a sense of personal accomplishment?'
      ],
      entrepreneurialQuestions: [
        'Are you pursuing entrepreneurship to gain recognition and respect?',
        'How important is professional achievement and status to your entrepreneurial goals?',
        'Do you want to be known as a successful entrepreneur in your field?'
      ],
      indicators: {
        fulfilled: ['self-confidence', 'recognition', 'achievement', 'respect from others'],
        unfulfilled: ['low self-esteem', 'lack of recognition', 'feeling undervalued', 'imposter syndrome']
      }
    },
    {
      id: 'cognitive',
      level: 5,
      name: 'Cognitive Needs',
      icon: '🧠',
      color: '#38b2ac',
      description: 'Knowledge, self-awareness, understanding, learning',
      entrepreneurialContext: 'Knowledge-driven entrepreneurship',
      questions: [
        'Do you have a strong desire to learn and understand?',
        'Are you curious about how things work and why?',
        'Do you seek knowledge and intellectual stimulation?'
      ],
      entrepreneurialQuestions: [
        'Are you drawn to entrepreneurship as a learning and growth opportunity?',
        'Do you want to solve complex problems through your business?',
        'Is intellectual challenge and continuous learning important to your entrepreneurial vision?'
      ],
      indicators: {
        fulfilled: ['love of learning', 'intellectual curiosity', 'problem-solving', 'continuous growth'],
        unfulfilled: ['intellectual stagnation', 'lack of challenge', 'limited learning opportunities']
      }
    },
    {
      id: 'aesthetic',
      level: 6,
      name: 'Aesthetic Needs',
      icon: '🎨',
      color: '#ed64a6',
      description: 'Search for beauty, balance, form, creativity',
      entrepreneurialContext: 'Creative and design-focused entrepreneurship',
      questions: [
        'Do you appreciate and seek beauty in your environment?',
        'Are you drawn to creative expression and artistic pursuits?',
        'Do you value harmony, balance, and aesthetic experiences?'
      ],
      entrepreneurialQuestions: [
        'Do you want to create something beautiful or aesthetically pleasing through entrepreneurship?',
        'Is creative expression and artistic vision central to your business idea?',
        'Are you motivated by the desire to bring more beauty into the world?'
      ],
      indicators: {
        fulfilled: ['creative expression', 'aesthetic appreciation', 'artistic pursuits', 'beautiful environment'],
        unfulfilled: ['creative blocks', 'ugly surroundings', 'lack of artistic outlet', 'aesthetic dissatisfaction']
      }
    },
    {
      id: 'selfActualization',
      level: 7,
      name: 'Self-Actualization',
      icon: '🌟',
      color: '#f56565',
      description: 'Personal growth, fulfillment, realizing potential',
      entrepreneurialContext: 'Purpose-driven entrepreneurship',
      questions: [
        'Are you becoming the person you want to be?',
        'Do you feel you\'re fulfilling your potential?',
        'Are you living authentically according to your values?'
      ],
      entrepreneurialQuestions: [
        'Is entrepreneurship a path to becoming your authentic self?',
        'Do you see your business as an expression of your highest potential?',
        'Are you driven by personal fulfillment rather than external validation?'
      ],
      indicators: {
        fulfilled: ['personal growth', 'authentic living', 'fulfilling potential', 'inner satisfaction'],
        unfulfilled: ['feeling stuck', 'not living authentically', 'unfulfilled potential', 'existential dissatisfaction']
      }
    },
    {
      id: 'transcendence',
      level: 8,
      name: 'Transcendence',
      icon: '🕊️',
      color: '#9f7aea',
      description: 'Helping others to self-actualize, spiritual connection',
      entrepreneurialContext: 'Legacy and impact-focused entrepreneurship',
      questions: [
        'Do you feel called to help others reach their potential?',
        'Are you motivated by something greater than yourself?',
        'Do you seek to make a lasting positive impact on the world?'
      ],
      entrepreneurialQuestions: [
        'Do you want your business to help others achieve their full potential?',
        'Is creating a positive legacy more important than personal gain?',
        'Are you driven by a sense of service to humanity or a higher purpose?'
      ],
      indicators: {
        fulfilled: ['helping others grow', 'spiritual connection', 'legacy focus', 'service orientation'],
        unfulfilled: ['self-centered focus', 'lack of meaning', 'no sense of higher purpose']
      }
    }
  ];

  useEffect(() => {
    assessMaslowLevel();
  }, [responses]);

  const assessMaslowLevel = () => {
    const scores = {};
    
    // Calculate scores for each level based on responses
    maslowLevels.forEach(level => {
      let score = 0;
      let responseCount = 0;
      
      // Analyze responses for indicators of this level
      Object.values(responses).forEach(response => {
        if (typeof response === 'string') {
          const lowerResponse = response.toLowerCase();
          
          // Check for fulfilled indicators
          level.indicators.fulfilled.forEach(indicator => {
            if (lowerResponse.includes(indicator.toLowerCase())) {
              score += 20;
              responseCount++;
            }
          });
          
          // Check for unfulfilled indicators (negative score)
          level.indicators.unfulfilled.forEach(indicator => {
            if (lowerResponse.includes(indicator.toLowerCase())) {
              score -= 15;
              responseCount++;
            }
          });
          
          // Level-specific keyword analysis
          if (level.id === 'physiological') {
            const keywords = ['food', 'shelter', 'sleep', 'health', 'basic needs', 'survival'];
            keywords.forEach(keyword => {
              if (lowerResponse.includes(keyword)) {
                score += 10;
                responseCount++;
              }
            });
          } else if (level.id === 'safety') {
            const keywords = ['security', 'stable', 'safe', 'insurance', 'savings', 'job'];
            keywords.forEach(keyword => {
              if (lowerResponse.includes(keyword)) {
                score += 10;
                responseCount++;
              }
            });
          } else if (level.id === 'belonging') {
            const keywords = ['family', 'friends', 'community', 'love', 'relationship', 'connection'];
            keywords.forEach(keyword => {
              if (lowerResponse.includes(keyword)) {
                score += 10;
                responseCount++;
              }
            });
          } else if (level.id === 'esteem') {
            const keywords = ['respect', 'recognition', 'achievement', 'success', 'confidence', 'pride'];
            keywords.forEach(keyword => {
              if (lowerResponse.includes(keyword)) {
                score += 10;
                responseCount++;
              }
            });
          } else if (level.id === 'cognitive') {
            const keywords = ['learn', 'knowledge', 'understand', 'curious', 'research', 'study'];
            keywords.forEach(keyword => {
              if (lowerResponse.includes(keyword)) {
                score += 10;
                responseCount++;
              }
            });
          } else if (level.id === 'aesthetic') {
            const keywords = ['beautiful', 'creative', 'art', 'design', 'aesthetic', 'harmony'];
            keywords.forEach(keyword => {
              if (lowerResponse.includes(keyword)) {
                score += 10;
                responseCount++;
              }
            });
          } else if (level.id === 'selfActualization') {
            const keywords = ['potential', 'growth', 'authentic', 'fulfillment', 'purpose', 'meaning'];
            keywords.forEach(keyword => {
              if (lowerResponse.includes(keyword)) {
                score += 10;
                responseCount++;
              }
            });
          } else if (level.id === 'transcendence') {
            const keywords = ['help others', 'legacy', 'impact', 'service', 'spiritual', 'humanity'];
            keywords.forEach(keyword => {
              if (lowerResponse.includes(keyword)) {
                score += 10;
                responseCount++;
              }
            });
          }
        }
      });
      
      // Normalize score (0-100)
      scores[level.id] = Math.max(0, Math.min(100, score + (Object.keys(responses).length * 5)));
    });
    
    setLevelScores(scores);
    
    // Determine current dominant level
    const sortedLevels = Object.entries(scores)
      .sort(([,a], [,b]) => b - a)
      .map(([levelId, score]) => ({ levelId, score }));
    
    const dominantLevelId = sortedLevels[0].levelId;
    const dominantLevelData = maslowLevels.find(l => l.id === dominantLevelId);
    
    setCurrentLevel(dominantLevelData);
    setDominantNeed(dominantLevelId);
    
    // Determine entrepreneurial readiness based on Maslow level
    let readiness = 'exploring';
    if (dominantLevelData.level <= 2) {
      readiness = 'survival_focused';
    } else if (dominantLevelData.level <= 4) {
      readiness = 'security_seeking';
    } else if (dominantLevelData.level <= 6) {
      readiness = 'growth_oriented';
    } else {
      readiness = 'purpose_driven';
    }
    
    setEntrepreneurialReadiness(readiness);
    
    if (onLevelDetermined) {
      onLevelDetermined({
        currentLevel: dominantLevelData,
        scores: scores,
        readiness: readiness,
        recommendations: getRecommendations(dominantLevelData, scores)
      });
    }
    
    if (onScoreUpdate) {
      onScoreUpdate(scores);
    }
  };

  const getRecommendations = (currentLevel, scores) => {
    const recommendations = [];
    
    if (currentLevel.level <= 2) {
      recommendations.push('🏠 Focus on stabilizing your basic needs before pursuing high-risk entrepreneurship');
      recommendations.push('💰 Consider low-risk, immediate income-generating opportunities');
      recommendations.push('🤝 Look for entrepreneurship programs that provide basic support and resources');
    } else if (currentLevel.level <= 4) {
      recommendations.push('📊 Develop a solid business plan with financial projections');
      recommendations.push('🛡️ Build an emergency fund before taking entrepreneurial risks');
      recommendations.push('🎯 Focus on proven business models with predictable outcomes');
    } else if (currentLevel.level <= 6) {
      recommendations.push('🚀 You\'re ready for innovative and creative entrepreneurial ventures');
      recommendations.push('🌱 Focus on personal growth and learning through entrepreneurship');
      recommendations.push('🎨 Consider businesses that allow for creative expression and problem-solving');
    } else {
      recommendations.push('🌍 Focus on creating meaningful impact and helping others');
      recommendations.push('🕊️ Consider social entrepreneurship or mission-driven businesses');
      recommendations.push('📚 Think about creating a lasting legacy through your entrepreneurial work');
    }
    
    return recommendations;
  };

  const getReadinessColor = () => {
    switch (entrepreneurialReadiness) {
      case 'survival_focused': return '#e53e3e';
      case 'security_seeking': return '#dd6b20';
      case 'growth_oriented': return '#38a169';
      case 'purpose_driven': return '#805ad5';
      default: return '#4299e1';
    }
  };

  const getReadinessDescription = () => {
    switch (entrepreneurialReadiness) {
      case 'survival_focused': 
        return 'Your entrepreneurial motivation is primarily driven by survival needs. Focus on stable, low-risk opportunities.';
      case 'security_seeking': 
        return 'You seek entrepreneurship for security and stability. Consider proven business models with predictable returns.';
      case 'growth_oriented': 
        return 'You\'re motivated by personal growth and creative expression. You\'re ready for innovative ventures.';
      case 'purpose_driven': 
        return 'You\'re driven by higher purpose and impact. Focus on meaningful, legacy-building entrepreneurship.';
      default: 
        return 'Continue exploring to better understand your entrepreneurial motivations.';
    }
  };

  return (
    <div className="maslow-assessment">
      <div className="assessment-header">
        <h2>🏔️ Maslow Hierarchy Assessment</h2>
        <p>Understanding your current needs level to guide your entrepreneurial journey</p>
      </div>

      {/* Current Level Display */}
      {currentLevel && (
        <div className="current-level" style={{ borderColor: currentLevel.color }}>
          <div className="level-header">
            <span className="level-icon">{currentLevel.icon}</span>
            <div className="level-info">
              <h3 style={{ color: currentLevel.color }}>
                Your Dominant Need: {currentLevel.name}
              </h3>
              <p>{currentLevel.description}</p>
            </div>
          </div>
          
          <div className="entrepreneurial-context">
            <h4>Entrepreneurial Context:</h4>
            <p>{currentLevel.entrepreneurialContext}</p>
          </div>
        </div>
      )}

      {/* Entrepreneurial Readiness */}
      <div className="readiness-assessment" style={{ borderColor: getReadinessColor() }}>
        <h3 style={{ color: getReadinessColor() }}>
          Entrepreneurial Readiness: {entrepreneurialReadiness.replace('_', ' ').toUpperCase()}
        </h3>
        <p>{getReadinessDescription()}</p>
      </div>

      {/* Maslow Pyramid Visualization */}
      <div className="maslow-pyramid">
        <h3>Your Maslow Profile</h3>
        <div className="pyramid-levels">
          {maslowLevels.slice().reverse().map((level, index) => (
            <div 
              key={level.id}
              className={`pyramid-level ${dominantNeed === level.id ? 'dominant' : ''}`}
              style={{ 
                backgroundColor: level.color,
                opacity: levelScores[level.id] / 100,
                width: `${90 - (index * 8)}%`
              }}
            >
              <div className="level-content">
                <span className="level-icon">{level.icon}</span>
                <span className="level-name">{level.name}</span>
                <span className="level-score">{Math.round(levelScores[level.id])}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Detailed Level Scores */}
      <div className="level-scores">
        <h3>Detailed Assessment</h3>
        <div className="scores-grid">
          {maslowLevels.map(level => (
            <div key={level.id} className="score-card">
              <div className="score-header">
                <span className="score-icon">{level.icon}</span>
                <h4>{level.name}</h4>
              </div>
              
              <div className="score-bar">
                <div 
                  className="score-fill"
                  style={{ 
                    width: `${levelScores[level.id]}%`,
                    backgroundColor: level.color
                  }}
                ></div>
              </div>
              
              <div className="score-value">
                {Math.round(levelScores[level.id])}%
              </div>
              
              <p className="score-description">{level.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {currentLevel && (
        <div className="recommendations">
          <h3>Personalized Recommendations</h3>
          <div className="recommendations-list">
            {getRecommendations(currentLevel, levelScores).map((rec, index) => (
              <div key={index} className="recommendation-item">
                <p>{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Next Steps */}
      <div className="next-steps">
        <h3>Next Steps in Your Entrepreneurial Journey</h3>
        <div className="steps-grid">
          <div className="step-card immediate">
            <h4>🎯 Immediate Focus</h4>
            <p>
              {currentLevel && currentLevel.level <= 2 
                ? 'Stabilize your basic needs and build a financial foundation'
                : currentLevel && currentLevel.level <= 4
                ? 'Create security through planning and risk management'
                : currentLevel && currentLevel.level <= 6
                ? 'Pursue growth-oriented and creative opportunities'
                : 'Focus on impact and legacy-building ventures'
              }
            </p>
          </div>
          
          <div className="step-card development">
            <h4>🌱 Development Areas</h4>
            <p>
              Work on strengthening lower-level needs while exploring higher-level motivations 
              to create a solid foundation for entrepreneurial success.
            </p>
          </div>
          
          <div className="step-card long-term">
            <h4>🚀 Long-term Vision</h4>
            <p>
              As you progress through the hierarchy, your entrepreneurial motivations will evolve. 
              Stay flexible and adapt your business approach accordingly.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MaslowAssessment;

