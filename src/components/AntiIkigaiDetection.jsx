import React, { useState, useEffect } from 'react';
import './AntiIkigaiDetection.css';

const AntiIkigaiDetection = ({ 
  responses = {},
  heartScore = 0,
  bodyScore = 0, 
  mindScore = 0,
  soulScore = 0,
  onAntiIkigaiDetected
}) => {
  const [antiIkigaiScores, setAntiIkigaiScores] = useState({
    power: 0,      // What brings power (instead of love)
    skills: 0,     // What you are good at (without purpose)
    money: 0,      // What you can be paid for (without fulfillment)
    endurance: 0   // What you can bear (without passion)
  });
  
  const [antiIkigaiState, setAntiIkigaiState] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const [riskLevel, setRiskLevel] = useState('low');

  // Analyze responses for Anti-Ikigai patterns
  useEffect(() => {
    analyzeAntiIkigaiPatterns();
  }, [responses, heartScore, bodyScore, mindScore, soulScore]);

  const analyzeAntiIkigaiPatterns = () => {
    const powerIndicators = [
      'control', 'dominate', 'power', 'authority', 'influence', 'status',
      'recognition', 'prestige', 'superiority', 'command', 'rule'
    ];
    
    const moneyOnlyIndicators = [
      'money', 'profit', 'wealth', 'rich', 'expensive', 'luxury',
      'financial gain', 'revenue', 'income', 'cash', 'salary'
    ];
    
    const enduranceIndicators = [
      'tolerate', 'bear', 'endure', 'survive', 'cope', 'manage',
      'deal with', 'put up with', 'handle', 'withstand'
    ];
    
    const manipulationIndicators = [
      'manipulate', 'exploit', 'use people', 'take advantage',
      'deceive', 'trick', 'fool', 'mislead'
    ];

    // Calculate Anti-Ikigai scores based on response analysis
    let powerScore = 0;
    let skillsScore = mindScore; // High skills without purpose can be dangerous
    let moneyScore = 0;
    let enduranceScore = 0;

    // Analyze all responses for negative patterns
    Object.values(responses).forEach(response => {
      if (typeof response === 'string') {
        const lowerResponse = response.toLowerCase();
        
        // Power-seeking language
        powerIndicators.forEach(indicator => {
          if (lowerResponse.includes(indicator)) {
            powerScore += 10;
          }
        });
        
        // Money-only focus
        moneyOnlyIndicators.forEach(indicator => {
          if (lowerResponse.includes(indicator)) {
            moneyScore += 10;
          }
        });
        
        // Endurance/tolerance language
        enduranceIndicators.forEach(indicator => {
          if (lowerResponse.includes(indicator)) {
            enduranceScore += 10;
          }
        });
        
        // Manipulation indicators
        manipulationIndicators.forEach(indicator => {
          if (lowerResponse.includes(indicator)) {
            powerScore += 15;
          }
        });
      }
    });

    // Factor in low positive scores as risk indicators
    if (heartScore < 30) powerScore += 20; // Low love → power seeking
    if (soulScore < 30) moneyScore += 20;  // Low purpose → money focus
    if (heartScore < 30) enduranceScore += 15; // Low passion → just enduring
    
    // Cap scores at 100
    powerScore = Math.min(powerScore, 100);
    skillsScore = Math.min(skillsScore, 100);
    moneyScore = Math.min(moneyScore, 100);
    enduranceScore = Math.min(enduranceScore, 100);

    setAntiIkigaiScores({
      power: powerScore,
      skills: skillsScore,
      money: moneyScore,
      endurance: enduranceScore
    });

    // Determine Anti-Ikigai state and warnings
    determineAntiIkigaiState(powerScore, skillsScore, moneyScore, enduranceScore);
  };

  const determineAntiIkigaiState = (power, skills, money, endurance) => {
    const threshold = 60;
    const highScores = [];
    
    if (power >= threshold) highScores.push('power');
    if (skills >= threshold) highScores.push('skills');
    if (money >= threshold) highScores.push('money');
    if (endurance >= threshold) highScores.push('endurance');

    let state = null;
    let currentWarnings = [];
    let risk = 'low';

    if (highScores.length >= 3) {
      // High risk - approaching Anti-Ikigai
      state = 'anti_ikigai';
      risk = 'critical';
      currentWarnings = [
        '🚨 CRITICAL: You are approaching Anti-Ikigai - a toxic entrepreneurial state',
        '⚠️ Your motivations appear driven by power, money, or endurance rather than passion and purpose',
        '🔄 Immediate course correction needed to avoid burnout and ethical compromises'
      ];
    } else if (highScores.length === 2) {
      // Determine specific dangerous intersection
      if (highScores.includes('power') && highScores.includes('skills')) {
        state = 'ambition';
        risk = 'high';
        currentWarnings = [
          '⚠️ AMBITION WARNING: You have power and skills but may lack love and purpose',
          '💡 Risk: Becoming ruthlessly successful but emotionally hollow',
          '🎯 Focus on: What you truly love and how to serve others'
        ];
      } else if (highScores.includes('skills') && highScores.includes('money')) {
        state = 'profession_trap';
        risk = 'high';
        currentWarnings = [
          '⚠️ PROFESSION TRAP: You have skills and money focus but may lack passion',
          '💡 Risk: Financial success without fulfillment or meaning',
          '🎯 Focus on: Finding your passion and creating positive impact'
        ];
      } else if (highScores.includes('money') && highScores.includes('endurance')) {
        state = 'desperation';
        risk = 'high';
        currentWarnings = [
          '⚠️ DESPERATION WARNING: You are focused on money and just enduring',
          '💡 Risk: Surviving financially but not thriving personally',
          '🎯 Focus on: Developing skills and finding what you love'
        ];
      } else if (highScores.includes('power') && highScores.includes('endurance')) {
        state = 'corruption';
        risk = 'critical';
        currentWarnings = [
          '🚨 CORRUPTION RISK: Power-seeking combined with endurance can lead to toxic leadership',
          '💡 Risk: Becoming manipulative and ethically compromised',
          '🎯 Focus on: Developing genuine care for others and meaningful purpose'
        ];
      }
    } else if (highScores.length === 1) {
      // Single dimension warning
      risk = 'medium';
      const dimension = highScores[0];
      
      switch (dimension) {
        case 'power':
          state = 'power_seeking';
          currentWarnings = [
            '⚠️ Power-seeking detected: Be careful not to prioritize control over genuine value creation',
            '💡 Balance with: Love, purpose, and service to others'
          ];
          break;
        case 'money':
          state = 'money_focused';
          currentWarnings = [
            '⚠️ Money-focused approach: Financial success without fulfillment leads to emptiness',
            '💡 Balance with: Passion, skills development, and meaningful impact'
          ];
          break;
        case 'endurance':
          state = 'survival_mode';
          currentWarnings = [
            '⚠️ Survival mode detected: Just enduring without passion leads to burnout',
            '💡 Balance with: Finding what you love and developing your strengths'
          ];
          break;
        case 'skills':
          state = 'skills_without_purpose';
          currentWarnings = [
            '⚠️ Skills without purpose: Technical competence needs direction and meaning',
            '💡 Balance with: Clear purpose and genuine care for impact'
          ];
          break;
      }
    }

    setAntiIkigaiState(state);
    setWarnings(currentWarnings);
    setRiskLevel(risk);

    // Notify parent component
    if (onAntiIkigaiDetected) {
      onAntiIkigaiDetected({
        state,
        warnings: currentWarnings,
        riskLevel: risk,
        scores: { power, skills, money, endurance }
      });
    }
  };

  const getRiskColor = () => {
    switch (riskLevel) {
      case 'critical': return '#e53e3e';
      case 'high': return '#dd6b20';
      case 'medium': return '#d69e2e';
      case 'low': return '#38a169';
      default: return '#718096';
    }
  };

  const getRiskIcon = () => {
    switch (riskLevel) {
      case 'critical': return '🚨';
      case 'high': return '⚠️';
      case 'medium': return '⚡';
      case 'low': return '✅';
      default: return '📊';
    }
  };

  if (riskLevel === 'low' && warnings.length === 0) {
    return (
      <div className="anti-ikigai-detection safe">
        <div className="safe-indicator">
          <span className="safe-icon">✅</span>
          <h3>Healthy Entrepreneurial Path</h3>
          <p>No Anti-Ikigai patterns detected. You're on a positive trajectory!</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`anti-ikigai-detection ${riskLevel}`}>
      {/* Risk Level Indicator */}
      <div className="risk-header" style={{ borderColor: getRiskColor() }}>
        <span className="risk-icon">{getRiskIcon()}</span>
        <div className="risk-info">
          <h3 style={{ color: getRiskColor() }}>
            Anti-Ikigai Risk: {riskLevel.toUpperCase()}
          </h3>
          <p className="risk-description">
            {riskLevel === 'critical' && 'Immediate attention required to avoid toxic entrepreneurial patterns'}
            {riskLevel === 'high' && 'Significant risk of unhealthy entrepreneurial motivations'}
            {riskLevel === 'medium' && 'Some concerning patterns detected - course correction recommended'}
            {riskLevel === 'low' && 'Minor risks identified - stay aware and balanced'}
          </p>
        </div>
      </div>

      {/* Anti-Ikigai Dimensions */}
      <div className="anti-ikigai-dimensions">
        <div className="anti-dimension power">
          <div className="anti-dimension-header">
            <span className="anti-dimension-icon">⚡</span>
            <h4>Power Seeking</h4>
          </div>
          <div className="anti-score-bar">
            <div 
              className="anti-score-fill"
              style={{ 
                width: `${antiIkigaiScores.power}%`,
                backgroundColor: antiIkigaiScores.power > 60 ? '#e53e3e' : '#fed7d7'
              }}
            ></div>
            <span className="anti-score-text">{antiIkigaiScores.power}%</span>
          </div>
          <p className="anti-dimension-description">
            Control and dominance over genuine love and care
          </p>
        </div>

        <div className="anti-dimension skills">
          <div className="anti-dimension-header">
            <span className="anti-dimension-icon">🔧</span>
            <h4>Skills Without Purpose</h4>
          </div>
          <div className="anti-score-bar">
            <div 
              className="anti-score-fill"
              style={{ 
                width: `${antiIkigaiScores.skills}%`,
                backgroundColor: antiIkigaiScores.skills > 60 ? '#dd6b20' : '#feebc8'
              }}
            ></div>
            <span className="anti-score-text">{antiIkigaiScores.skills}%</span>
          </div>
          <p className="anti-dimension-description">
            Technical competence without meaningful direction
          </p>
        </div>

        <div className="anti-dimension money">
          <div className="anti-dimension-header">
            <span className="anti-dimension-icon">💰</span>
            <h4>Money Focus</h4>
          </div>
          <div className="anti-score-bar">
            <div 
              className="anti-score-fill"
              style={{ 
                width: `${antiIkigaiScores.money}%`,
                backgroundColor: antiIkigaiScores.money > 60 ? '#d69e2e' : '#faf089'
              }}
            ></div>
            <span className="anti-score-text">{antiIkigaiScores.money}%</span>
          </div>
          <p className="anti-dimension-description">
            Financial gain without fulfillment or purpose
          </p>
        </div>

        <div className="anti-dimension endurance">
          <div className="anti-dimension-header">
            <span className="anti-dimension-icon">😤</span>
            <h4>Mere Endurance</h4>
          </div>
          <div className="anti-score-bar">
            <div 
              className="anti-score-fill"
              style={{ 
                width: `${antiIkigaiScores.endurance}%`,
                backgroundColor: antiIkigaiScores.endurance > 60 ? '#9f7aea' : '#e9d8fd'
              }}
            ></div>
            <span className="anti-score-text">{antiIkigaiScores.endurance}%</span>
          </div>
          <p className="anti-dimension-description">
            Just surviving and tolerating without passion
          </p>
        </div>
      </div>

      {/* Warnings and Recommendations */}
      {warnings.length > 0 && (
        <div className="warnings-section">
          <h4>⚠️ Warnings & Recommendations</h4>
          <div className="warnings-list">
            {warnings.map((warning, index) => (
              <div key={index} className="warning-item">
                <p>{warning}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Anti-Ikigai States Guide */}
      <div className="anti-ikigai-guide">
        <h4>Understanding Anti-Ikigai Traps</h4>
        <div className="anti-states-grid">
          <div className="anti-state-card ambition">
            <h5>🔥 Ambition</h5>
            <p>Power + Skills</p>
            <small>Ruthlessly successful but emotionally hollow</small>
          </div>
          
          <div className="anti-state-card profession-trap">
            <h5>💼 Profession Trap</h5>
            <p>Skills + Money</p>
            <small>Financial success without fulfillment</small>
          </div>
          
          <div className="anti-state-card desperation">
            <h5>😰 Desperation</h5>
            <p>Money + Endurance</p>
            <small>Surviving financially but not thriving</small>
          </div>
          
          <div className="anti-state-card corruption">
            <h5>☠️ Corruption</h5>
            <p>Power + Endurance</p>
            <small>Toxic leadership and ethical compromise</small>
          </div>
        </div>
      </div>

      {/* Recovery Actions */}
      <div className="recovery-actions">
        <h4>🔄 Path to Recovery</h4>
        <div className="recovery-steps">
          <div className="recovery-step">
            <span className="step-number">1</span>
            <div className="step-content">
              <h5>Reconnect with Purpose</h5>
              <p>Identify what truly matters to you beyond power, money, or survival</p>
            </div>
          </div>
          
          <div className="recovery-step">
            <span className="step-number">2</span>
            <div className="step-content">
              <h5>Rediscover Passion</h5>
              <p>Find what genuinely excites and energizes you</p>
            </div>
          </div>
          
          <div className="recovery-step">
            <span className="step-number">3</span>
            <div className="step-content">
              <h5>Realign Actions</h5>
              <p>Adjust your business approach to serve others, not just yourself</p>
            </div>
          </div>
          
          <div className="recovery-step">
            <span className="step-number">4</span>
            <div className="step-content">
              <h5>Rebuild Relationships</h5>
              <p>Focus on genuine connections and collaborative success</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AntiIkigaiDetection;

