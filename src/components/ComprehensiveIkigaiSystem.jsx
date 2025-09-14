import React, { useState, useEffect } from 'react';
import EnhancedIkigaiAssessment from './EnhancedIkigaiAssessment';
import AntiIkigaiDetection from './AntiIkigaiDetection';
import GmailStyleWritingAssistant from './GmailStyleWritingAssistant';
import './ComprehensiveIkigaiSystem.css';

const ComprehensiveIkigaiSystem = ({ 
  responses = {},
  onScoreUpdate,
  onStateChange 
}) => {
  const [ikigaiScores, setIkigaiScores] = useState({
    heart: 0,
    body: 0,
    mind: 0,
    soul: 0
  });
  
  const [currentIkigaiState, setCurrentIkigaiState] = useState(null);
  const [antiIkigaiState, setAntiIkigaiState] = useState(null);
  const [overallAssessment, setOverallAssessment] = useState('exploring');
  const [recommendations, setRecommendations] = useState([]);

  // Calculate Ikigai scores based on responses
  useEffect(() => {
    calculateIkigaiScores();
  }, [responses]);

  const calculateIkigaiScores = () => {
    // Heart Score (What You Love) - Passion indicators
    const passionKeywords = [
      'love', 'passion', 'excited', 'energized', 'enjoy', 'fulfilling',
      'meaningful', 'inspiring', 'motivating', 'dream', 'vision'
    ];
    
    // Body Score (What You Can Be Paid For) - Market viability
    const marketKeywords = [
      'customers', 'market', 'demand', 'revenue', 'profit', 'business model',
      'pricing', 'sales', 'monetize', 'value proposition', 'competitive advantage'
    ];
    
    // Mind Score (What You Are Good At) - Skills and competencies
    const skillsKeywords = [
      'skilled', 'experienced', 'expert', 'competent', 'talented', 'capable',
      'knowledge', 'expertise', 'proficient', 'accomplished', 'qualified'
    ];
    
    // Soul Score (What The World Needs) - Purpose and impact
    const purposeKeywords = [
      'impact', 'help', 'solve', 'improve', 'change', 'benefit', 'serve',
      'contribute', 'difference', 'purpose', 'mission', 'social', 'community'
    ];

    let heartScore = 0;
    let bodyScore = 0;
    let mindScore = 0;
    let soulScore = 0;

    // Analyze all responses
    Object.values(responses).forEach(response => {
      if (typeof response === 'string') {
        const lowerResponse = response.toLowerCase();
        const wordCount = response.split(' ').length;
        
        // Calculate base scores from keyword matches
        passionKeywords.forEach(keyword => {
          if (lowerResponse.includes(keyword)) {
            heartScore += Math.min(wordCount * 0.5, 10);
          }
        });
        
        marketKeywords.forEach(keyword => {
          if (lowerResponse.includes(keyword)) {
            bodyScore += Math.min(wordCount * 0.5, 10);
          }
        });
        
        skillsKeywords.forEach(keyword => {
          if (lowerResponse.includes(keyword)) {
            mindScore += Math.min(wordCount * 0.5, 10);
          }
        });
        
        purposeKeywords.forEach(keyword => {
          if (lowerResponse.includes(keyword)) {
            soulScore += Math.min(wordCount * 0.5, 10);
          }
        });
        
        // Bonus for detailed responses (length and depth)
        if (wordCount > 50) {
          const depthBonus = Math.min((wordCount - 50) * 0.2, 15);
          
          // Distribute depth bonus based on content
          if (lowerResponse.includes('passion') || lowerResponse.includes('love')) {
            heartScore += depthBonus;
          }
          if (lowerResponse.includes('market') || lowerResponse.includes('customer')) {
            bodyScore += depthBonus;
          }
          if (lowerResponse.includes('skill') || lowerResponse.includes('experience')) {
            mindScore += depthBonus;
          }
          if (lowerResponse.includes('impact') || lowerResponse.includes('help')) {
            soulScore += depthBonus;
          }
        }
      }
    });

    // Cap scores at 100 and ensure minimum progression
    heartScore = Math.min(Math.max(heartScore, Object.keys(responses).length * 2), 100);
    bodyScore = Math.min(Math.max(bodyScore, Object.keys(responses).length * 2), 100);
    mindScore = Math.min(Math.max(mindScore, Object.keys(responses).length * 2), 100);
    soulScore = Math.min(Math.max(soulScore, Object.keys(responses).length * 2), 100);

    const newScores = {
      heart: Math.round(heartScore),
      body: Math.round(bodyScore),
      mind: Math.round(mindScore),
      soul: Math.round(soulScore)
    };

    setIkigaiScores(newScores);
    
    if (onScoreUpdate) {
      onScoreUpdate(newScores);
    }
  };

  const handleIkigaiStateChange = (stateData) => {
    setCurrentIkigaiState(stateData);
    updateOverallAssessment(stateData, antiIkigaiState);
  };

  const handleAntiIkigaiDetected = (antiStateData) => {
    setAntiIkigaiState(antiStateData);
    updateOverallAssessment(currentIkigaiState, antiStateData);
  };

  const updateOverallAssessment = (ikigaiState, antiState) => {
    let assessment = 'exploring';
    let recs = [];

    // Determine overall assessment based on both positive and negative indicators
    if (antiState && antiState.riskLevel === 'critical') {
      assessment = 'critical_risk';
      recs = [
        '🚨 Immediate intervention required to avoid toxic entrepreneurial patterns',
        '🔄 Consider taking a break to reassess your motivations and values',
        '👥 Seek mentorship or counseling to realign with healthy entrepreneurship'
      ];
    } else if (antiState && antiState.riskLevel === 'high') {
      assessment = 'high_risk';
      recs = [
        '⚠️ Significant course correction needed to avoid unhealthy patterns',
        '🎯 Focus on rediscovering your genuine passions and purpose',
        '🤝 Prioritize relationships and collaborative success over individual gain'
      ];
    } else if (ikigaiState && ikigaiState.state === 'ikigai') {
      assessment = 'ikigai_achieved';
      recs = [
        '🎉 Congratulations! You have achieved entrepreneurial Ikigai',
        '🔄 Focus on maintaining balance across all four dimensions',
        '🌱 Consider mentoring others on their entrepreneurial journey'
      ];
    } else if (ikigaiState && ['passion', 'mission', 'profession', 'vocation'].includes(ikigaiState.state)) {
      assessment = 'intermediate_state';
      recs = ikigaiState.recommendations || [];
    } else {
      assessment = 'developing';
      recs = [
        '🌱 Continue developing all four Ikigai dimensions',
        '📝 Provide more detailed responses to improve your assessment',
        '🎯 Focus on areas where you scored lowest'
      ];
    }

    setOverallAssessment(assessment);
    setRecommendations(recs);

    if (onStateChange) {
      onStateChange({
        overall: assessment,
        ikigai: ikigaiState,
        antiIkigai: antiState,
        recommendations: recs
      });
    }
  };

  const getOverallStatusColor = () => {
    switch (overallAssessment) {
      case 'ikigai_achieved': return '#38a169';
      case 'intermediate_state': return '#ed8936';
      case 'developing': return '#3182ce';
      case 'high_risk': return '#dd6b20';
      case 'critical_risk': return '#e53e3e';
      default: return '#718096';
    }
  };

  const getOverallStatusIcon = () => {
    switch (overallAssessment) {
      case 'ikigai_achieved': return '🎯';
      case 'intermediate_state': return '⚡';
      case 'developing': return '🌱';
      case 'high_risk': return '⚠️';
      case 'critical_risk': return '🚨';
      default: return '🧭';
    }
  };

  return (
    <div className="comprehensive-ikigai-system">
      {/* Overall Status Header */}
      <div className="overall-status" style={{ borderColor: getOverallStatusColor() }}>
        <div className="status-header">
          <span className="status-icon">{getOverallStatusIcon()}</span>
          <div className="status-info">
            <h2 style={{ color: getOverallStatusColor() }}>
              Entrepreneurial Assessment Status
            </h2>
            <p className="status-description">
              {overallAssessment === 'ikigai_achieved' && 'You have achieved your entrepreneurial Ikigai!'}
              {overallAssessment === 'intermediate_state' && 'You\'re in an intermediate Ikigai state - almost there!'}
              {overallAssessment === 'developing' && 'You\'re developing your entrepreneurial profile'}
              {overallAssessment === 'high_risk' && 'Warning: High risk of unhealthy entrepreneurial patterns'}
              {overallAssessment === 'critical_risk' && 'Critical: Immediate attention required'}
              {overallAssessment === 'exploring' && 'Exploring your entrepreneurial potential'}
            </p>
          </div>
        </div>
        
        {recommendations.length > 0 && (
          <div className="overall-recommendations">
            <h4>Key Recommendations:</h4>
            <ul>
              {recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Enhanced Ikigai Assessment */}
      <div className="ikigai-section">
        <h3>🎯 Positive Ikigai Assessment</h3>
        <EnhancedIkigaiAssessment
          heartScore={ikigaiScores.heart}
          bodyScore={ikigaiScores.body}
          mindScore={ikigaiScores.mind}
          soulScore={ikigaiScores.soul}
          onStateChange={handleIkigaiStateChange}
        />
      </div>

      {/* Anti-Ikigai Detection */}
      <div className="anti-ikigai-section">
        <h3>⚠️ Anti-Ikigai Risk Assessment</h3>
        <AntiIkigaiDetection
          responses={responses}
          heartScore={ikigaiScores.heart}
          bodyScore={ikigaiScores.body}
          mindScore={ikigaiScores.mind}
          soulScore={ikigaiScores.soul}
          onAntiIkigaiDetected={handleAntiIkigaiDetected}
        />
      </div>

      {/* Ikigai Balance Visualization */}
      <div className="ikigai-balance">
        <h3>⚖️ Ikigai Balance Overview</h3>
        <div className="balance-chart">
          <div className="balance-item positive">
            <h4>Positive Ikigai</h4>
            <div className="balance-score">
              {Math.round((ikigaiScores.heart + ikigaiScores.body + ikigaiScores.mind + ikigaiScores.soul) / 4)}%
            </div>
            <p>Love + Skills + Market + Purpose</p>
          </div>
          
          <div className="balance-vs">VS</div>
          
          <div className="balance-item negative">
            <h4>Anti-Ikigai Risk</h4>
            <div className="balance-score risk">
              {antiIkigaiState ? 
                (antiIkigaiState.riskLevel === 'critical' ? '90%' :
                 antiIkigaiState.riskLevel === 'high' ? '70%' :
                 antiIkigaiState.riskLevel === 'medium' ? '40%' : '20%') : '0%'}
            </div>
            <p>Power + Skills + Money + Endurance</p>
          </div>
        </div>
        
        <div className="balance-guidance">
          <div className="guidance-item">
            <span className="guidance-icon">💡</span>
            <p>
              <strong>Healthy Balance:</strong> High positive Ikigai scores with low Anti-Ikigai risk indicate 
              a sustainable and fulfilling entrepreneurial path.
            </p>
          </div>
          
          <div className="guidance-item">
            <span className="guidance-icon">⚠️</span>
            <p>
              <strong>Warning Signs:</strong> High Anti-Ikigai risk combined with low positive scores 
              suggests potential burnout and ethical compromises.
            </p>
          </div>
          
          <div className="guidance-item">
            <span className="guidance-icon">🎯</span>
            <p>
              <strong>Optimal State:</strong> Achieve 80%+ in all positive Ikigai dimensions while 
              maintaining Anti-Ikigai risk below 30%.
            </p>
          </div>
        </div>
      </div>

      {/* Action Plan */}
      <div className="action-plan">
        <h3>📋 Personalized Action Plan</h3>
        <div className="action-categories">
          <div className="action-category strengthen">
            <h4>🚀 Strengthen</h4>
            <ul>
              {ikigaiScores.heart < 70 && <li>Explore and develop your passions</li>}
              {ikigaiScores.body < 70 && <li>Research market opportunities and revenue models</li>}
              {ikigaiScores.mind < 70 && <li>Develop relevant skills and expertise</li>}
              {ikigaiScores.soul < 70 && <li>Define your purpose and intended impact</li>}
            </ul>
          </div>
          
          <div className="action-category maintain">
            <h4>✅ Maintain</h4>
            <ul>
              {ikigaiScores.heart >= 70 && <li>Continue nurturing your passion</li>}
              {ikigaiScores.body >= 70 && <li>Keep validating market demand</li>}
              {ikigaiScores.mind >= 70 && <li>Stay current with your skills</li>}
              {ikigaiScores.soul >= 70 && <li>Remain focused on your purpose</li>}
            </ul>
          </div>
          
          <div className="action-category avoid">
            <h4>🚫 Avoid</h4>
            <ul>
              {antiIkigaiState && antiIkigaiState.riskLevel !== 'low' && (
                antiIkigaiState.warnings.map((warning, index) => (
                  <li key={index}>{warning.replace(/^[🚨⚠️💡🎯]+\s*/, '')}</li>
                ))
              )}
              <li>Making decisions based solely on money or power</li>
              <li>Ignoring your personal values and ethics</li>
              <li>Pursuing opportunities that drain your energy</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComprehensiveIkigaiSystem;

