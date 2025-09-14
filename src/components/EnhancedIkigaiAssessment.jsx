import React, { useState, useEffect } from 'react';
import './EnhancedIkigaiAssessment.css';

const EnhancedIkigaiAssessment = ({ 
  heartScore = 0, 
  bodyScore = 0, 
  mindScore = 0, 
  soulScore = 0,
  onStateChange 
}) => {
  const [currentState, setCurrentState] = useState('incomplete');
  const [stateDescription, setStateDescription] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [overallProgress, setOverallProgress] = useState(0);

  // Calculate current Ikigai state based on scores
  useEffect(() => {
    const scores = { heart: heartScore, body: bodyScore, mind: mindScore, soul: soulScore };
    const threshold = 70; // Minimum score to be considered "achieved"
    const achieved = Object.entries(scores).filter(([_, score]) => score >= threshold);
    
    // Calculate overall progress
    const progress = (heartScore + bodyScore + mindScore + soulScore) / 4;
    setOverallProgress(progress);
    
    // Determine current state
    let state, description, recs;
    
    if (achieved.length === 4) {
      // Full Ikigai achieved
      state = 'ikigai';
      description = 'Congratulations! You have achieved your entrepreneurial Ikigai - the perfect intersection of what you love, what you\'re good at, what the world needs, and what you can be paid for.';
      recs = [
        'Focus on maintaining balance across all four dimensions',
        'Consider mentoring others on their entrepreneurial journey',
        'Continuously evolve your business to stay aligned with your Ikigai'
      ];
    } else if (achieved.length === 3) {
      // One dimension missing - identify which one
      const missing = Object.entries(scores).find(([_, score]) => score < threshold)[0];
      
      switch (missing) {
        case 'heart':
          state = 'profession_vocation_mission';
          description = 'You have skills, market demand, and purpose, but lack passion. You may feel successful but unfulfilled.';
          recs = [
            'Explore what truly excites you about your work',
            'Find ways to incorporate your personal interests',
            'Consider pivoting to align with your passions'
          ];
          break;
        case 'body':
          state = 'passion_mission_profession';
          description = 'You have passion, skills, and purpose, but struggle with monetization. You may feel fulfilled but financially insecure.';
          recs = [
            'Develop a clear revenue model',
            'Research market demand for your solution',
            'Consider different pricing strategies'
          ];
          break;
        case 'mind':
          state = 'passion_mission_vocation';
          description = 'You have passion, purpose, and market demand, but lack the necessary skills. You may feel motivated but inadequate.';
          recs = [
            'Identify specific skill gaps',
            'Invest in learning and development',
            'Consider partnering with skilled individuals'
          ];
          break;
        case 'soul':
          state = 'passion_profession_vocation';
          description = 'You have passion, skills, and market demand, but lack meaningful purpose. You may feel successful but empty.';
          recs = [
            'Define the impact you want to make',
            'Research social and environmental needs',
            'Align your business with a greater purpose'
          ];
          break;
      }
    } else if (achieved.length === 2) {
      // Two dimensions achieved - identify the intersection
      const achievedKeys = achieved.map(([key, _]) => key).sort();
      
      if (achievedKeys.includes('heart') && achievedKeys.includes('mind')) {
        state = 'passion';
        description = 'You have PASSION - you love what you do and you\'re good at it. However, you may feel satisfied but not making a difference, and struggling financially.';
        recs = [
          'Research market needs that align with your passion',
          'Develop a business model around your skills',
          'Find ways to create meaningful impact'
        ];
      } else if (achievedKeys.includes('heart') && achievedKeys.includes('soul')) {
        state = 'mission';
        description = 'You have MISSION - you love what you do and it serves the world. You feel delight and fulfillment but may lack wealth and confidence in your abilities.';
        recs = [
          'Develop the skills needed to execute your mission',
          'Create a sustainable revenue model',
          'Build confidence through small wins'
        ];
      } else if (achievedKeys.includes('mind') && achievedKeys.includes('body')) {
        state = 'profession';
        description = 'You have PROFESSION - you\'re skilled and well-paid. You feel comfortable and secure but may sense something is missing - passion and purpose.';
        recs = [
          'Explore what truly motivates you',
          'Find ways to make a meaningful impact',
          'Consider how to align your work with your values'
        ];
      } else if (achievedKeys.includes('soul') && achievedKeys.includes('body')) {
        state = 'vocation';
        description = 'You have VOCATION - your work serves the world and pays well. You enjoy wealth and impact but may lack self-belief and passion.';
        recs = [
          'Develop skills to increase confidence',
          'Find personal connection to your work',
          'Build on your strengths and achievements'
        ];
      } else {
        // Other combinations
        state = 'developing';
        description = 'You\'re developing multiple dimensions of your entrepreneurial journey. Keep building on your strengths while addressing gaps.';
        recs = [
          'Focus on the dimensions where you\'re strongest',
          'Gradually work on weaker areas',
          'Seek mentorship and guidance'
        ];
      }
    } else if (achieved.length === 1) {
      // Only one dimension achieved
      const achievedKey = achieved[0][0];
      state = 'emerging';
      
      switch (achievedKey) {
        case 'heart':
          description = 'You have strong passion but need to develop skills, find market demand, and create meaningful impact.';
          break;
        case 'body':
          description = 'You understand market demand but need to develop passion, skills, and purpose.';
          break;
        case 'mind':
          description = 'You have strong skills but need to find passion, market demand, and meaningful purpose.';
          break;
        case 'soul':
          description = 'You have a clear sense of purpose but need to develop passion, skills, and market viability.';
          break;
      }
      
      recs = [
        'Build on your existing strength',
        'Gradually develop the other three dimensions',
        'Take time for self-reflection and exploration'
      ];
    } else {
      // No dimensions achieved yet
      state = 'exploring';
      description = 'You\'re at the beginning of your entrepreneurial journey. This is an exciting time of exploration and discovery.';
      recs = [
        'Take time to explore your interests and passions',
        'Assess your current skills and identify areas for growth',
        'Research market opportunities and social needs',
        'Start with small experiments and projects'
      ];
    }
    
    setCurrentState(state);
    setStateDescription(description);
    setRecommendations(recs);
    
    if (onStateChange) {
      onStateChange({
        state,
        description,
        recommendations: recs,
        progress,
        achievedDimensions: achieved.length
      });
    }
  }, [heartScore, bodyScore, mindScore, soulScore, onStateChange]);

  // Get state color based on current state
  const getStateColor = () => {
    switch (currentState) {
      case 'ikigai': return '#38a169'; // Green
      case 'passion': return '#e53e3e'; // Red-pink
      case 'mission': return '#d69e2e'; // Orange-yellow  
      case 'profession': return '#3182ce'; // Blue
      case 'vocation': return '#805ad5'; // Purple
      case 'developing': return '#ed8936'; // Orange
      case 'emerging': return '#38b2ac'; // Teal
      case 'exploring': return '#718096'; // Gray
      default: return '#a0aec0';
    }
  };

  // Get state icon
  const getStateIcon = () => {
    switch (currentState) {
      case 'ikigai': return '🎯';
      case 'passion': return '❤️';
      case 'mission': return '🌟';
      case 'profession': return '💼';
      case 'vocation': return '🎭';
      case 'developing': return '🌱';
      case 'emerging': return '🌅';
      case 'exploring': return '🧭';
      default: return '📍';
    }
  };

  return (
    <div className="enhanced-ikigai-assessment">
      {/* Overall Progress */}
      <div className="ikigai-progress">
        <div className="progress-header">
          <h3>Your Entrepreneurial Ikigai Journey</h3>
          <span className="progress-percentage">{Math.round(overallProgress)}%</span>
        </div>
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ 
              width: `${overallProgress}%`,
              backgroundColor: getStateColor()
            }}
          ></div>
        </div>
      </div>

      {/* Four Ikigai Dimensions */}
      <div className="ikigai-dimensions">
        <div className="dimension heart">
          <div className="dimension-icon">❤️</div>
          <div className="dimension-info">
            <h4>Heart</h4>
            <p>What You Love</p>
            <div className="dimension-score">
              <div 
                className="score-fill"
                style={{ height: `${heartScore}%` }}
              ></div>
              <span className="score-text">{heartScore}%</span>
            </div>
          </div>
        </div>

        <div className="dimension body">
          <div className="dimension-icon">⚡</div>
          <div className="dimension-info">
            <h4>Body</h4>
            <p>What You Can Be Paid For</p>
            <div className="dimension-score">
              <div 
                className="score-fill"
                style={{ height: `${bodyScore}%` }}
              ></div>
              <span className="score-text">{bodyScore}%</span>
            </div>
          </div>
        </div>

        <div className="dimension mind">
          <div className="dimension-icon">🧠</div>
          <div className="dimension-info">
            <h4>Mind</h4>
            <p>What You Are Good At</p>
            <div className="dimension-score">
              <div 
                className="score-fill"
                style={{ height: `${mindScore}%` }}
              ></div>
              <span className="score-text">{mindScore}%</span>
            </div>
          </div>
        </div>

        <div className="dimension soul">
          <div className="dimension-icon">⭐</div>
          <div className="dimension-info">
            <h4>Soul</h4>
            <p>What The World Needs</p>
            <div className="dimension-score">
              <div 
                className="score-fill"
                style={{ height: `${soulScore}%` }}
              ></div>
              <span className="score-text">{soulScore}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Current State Analysis */}
      <div className="current-state" style={{ borderColor: getStateColor() }}>
        <div className="state-header">
          <span className="state-icon">{getStateIcon()}</span>
          <h3 className="state-title" style={{ color: getStateColor() }}>
            {currentState === 'ikigai' ? 'Entrepreneurial Ikigai Achieved!' :
             currentState === 'passion' ? 'You Have Passion' :
             currentState === 'mission' ? 'You Have Mission' :
             currentState === 'profession' ? 'You Have Profession' :
             currentState === 'vocation' ? 'You Have Vocation' :
             currentState === 'developing' ? 'Developing Multiple Dimensions' :
             currentState === 'emerging' ? 'Emerging Entrepreneur' :
             'Exploring Your Path'}
          </h3>
        </div>
        
        <p className="state-description">{stateDescription}</p>
        
        {recommendations.length > 0 && (
          <div className="recommendations">
            <h4>Next Steps:</h4>
            <ul>
              {recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Ikigai States Guide */}
      <div className="ikigai-states-guide">
        <h4>Understanding Your Ikigai Journey</h4>
        <div className="states-grid">
          <div className="state-card passion-card">
            <div className="state-card-header">
              <span className="state-card-icon">❤️🧠</span>
              <h5>Passion</h5>
            </div>
            <p>Love + Skills</p>
            <small>Satisfaction but not making a difference</small>
          </div>
          
          <div className="state-card mission-card">
            <div className="state-card-header">
              <span className="state-card-icon">❤️⭐</span>
              <h5>Mission</h5>
            </div>
            <p>Love + World Needs</p>
            <small>Delight and fulfillment but lack of wealth</small>
          </div>
          
          <div className="state-card profession-card">
            <div className="state-card-header">
              <span className="state-card-icon">🧠⚡</span>
              <h5>Profession</h5>
            </div>
            <p>Skills + Paid For</p>
            <small>Comfortable/secure but something is missing</small>
          </div>
          
          <div className="state-card vocation-card">
            <div className="state-card-header">
              <span className="state-card-icon">⭐⚡</span>
              <h5>Vocation</h5>
            </div>
            <p>World Needs + Paid For</p>
            <small>Enjoyment and wealth but lack of self belief</small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedIkigaiAssessment;

