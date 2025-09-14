import React, { useState, useEffect } from 'react';
import { 
  Mail, 
  MessageCircle, 
  Instagram, 
  Youtube, 
  FileText, 
  Calendar,
  Music,
  ShoppingCart,
  Activity,
  Shield,
  CheckCircle,
  AlertCircle,
  Clock,
  Zap,
  Brain,
  Heart,
  Target,
  Star,
  TrendingUp,
  Lock,
  Eye,
  EyeOff,
  Settings,
  Download,
  Upload,
  Trash2,
  RefreshCw
} from 'lucide-react';
import './DataConnectionDashboard.css';

const DataConnectionDashboard = () => {
  const [connectedAccounts, setConnectedAccounts] = useState({});
  const [analysisProgress, setAnalysisProgress] = useState({});
  const [personalityInsights, setPersonalityInsights] = useState([]);
  const [privacySettings, setPrivacySettings] = useState({
    dataRetention: '12months',
    insightVisibility: 'private',
    analysisDepth: 'comprehensive'
  });

  const accountTypes = [
    {
      id: 'gmail',
      name: 'Gmail',
      icon: Mail,
      category: 'communication',
      tier: 1,
      description: 'Email communication patterns and professional style',
      dataTypes: ['emails', 'contacts', 'labels'],
      insights: ['Communication style', 'Professional network', 'Response patterns', 'Decision-making style'],
      privacyLevel: 'high',
      estimatedTime: '5-10 minutes',
      dataVolume: 'High'
    },
    {
      id: 'whatsapp',
      name: 'WhatsApp',
      icon: MessageCircle,
      category: 'communication',
      tier: 1,
      description: 'Personal communication and social interaction patterns',
      dataTypes: ['messages', 'groups', 'media'],
      insights: ['Social style', 'Emotional expression', 'Relationship dynamics', 'Humor patterns'],
      privacyLevel: 'high',
      estimatedTime: '3-7 minutes',
      dataVolume: 'High'
    },
    {
      id: 'instagram',
      name: 'Instagram',
      icon: Instagram,
      category: 'social',
      tier: 2,
      description: 'Visual preferences and social media personality',
      dataTypes: ['posts', 'stories', 'comments', 'likes'],
      insights: ['Visual aesthetic', 'Social influence', 'Interest patterns', 'Public persona'],
      privacyLevel: 'medium',
      estimatedTime: '2-5 minutes',
      dataVolume: 'Medium'
    },
    {
      id: 'youtube',
      name: 'YouTube',
      icon: Youtube,
      category: 'content',
      tier: 2,
      description: 'Learning patterns and content preferences',
      dataTypes: ['watch_history', 'comments', 'likes', 'playlists'],
      insights: ['Learning style', 'Interest depth', 'Engagement patterns', 'Knowledge areas'],
      privacyLevel: 'medium',
      estimatedTime: '3-8 minutes',
      dataVolume: 'High'
    },
    {
      id: 'google_drive',
      name: 'Google Drive',
      icon: FileText,
      category: 'productivity',
      tier: 3,
      description: 'Organization style and project patterns',
      dataTypes: ['documents', 'folders', 'sharing', 'activity'],
      insights: ['Organization style', 'Collaboration patterns', 'Project types', 'Work style'],
      privacyLevel: 'high',
      estimatedTime: '2-4 minutes',
      dataVolume: 'Medium'
    },
    {
      id: 'google_calendar',
      name: 'Google Calendar',
      icon: Calendar,
      category: 'productivity',
      tier: 3,
      description: 'Time management and priority patterns',
      dataTypes: ['events', 'meetings', 'recurring', 'availability'],
      insights: ['Time management', 'Priority allocation', 'Planning style', 'Work-life balance'],
      privacyLevel: 'medium',
      estimatedTime: '1-3 minutes',
      dataVolume: 'Low'
    },
    {
      id: 'spotify',
      name: 'Spotify',
      icon: Music,
      category: 'lifestyle',
      tier: 4,
      description: 'Music preferences and mood patterns',
      dataTypes: ['playlists', 'listening_history', 'liked_songs', 'podcasts'],
      insights: ['Personality traits', 'Mood patterns', 'Cultural interests', 'Focus preferences'],
      privacyLevel: 'low',
      estimatedTime: '1-2 minutes',
      dataVolume: 'Medium'
    }
  ];

  const [selectedAccount, setSelectedAccount] = useState(null);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);

  const connectAccount = async (accountId) => {
    // Simulate OAuth flow
    setConnectedAccounts(prev => ({
      ...prev,
      [accountId]: {
        status: 'connecting',
        connectedAt: new Date(),
        dataTypes: accountTypes.find(a => a.id === accountId).dataTypes
      }
    }));

    // Simulate connection process
    setTimeout(() => {
      setConnectedAccounts(prev => ({
        ...prev,
        [accountId]: {
          ...prev[accountId],
          status: 'connected'
        }
      }));
      
      startAnalysis(accountId);
    }, 2000);
  };

  const startAnalysis = (accountId) => {
    const account = accountTypes.find(a => a.id === accountId);
    
    setAnalysisProgress(prev => ({
      ...prev,
      [accountId]: {
        stage: 'data_extraction',
        progress: 0,
        insights: []
      }
    }));

    // Simulate analysis stages
    const stages = [
      { name: 'data_extraction', duration: 3000 },
      { name: 'pattern_analysis', duration: 4000 },
      { name: 'personality_synthesis', duration: 3000 },
      { name: 'insight_generation', duration: 2000 }
    ];

    let currentStage = 0;
    const progressInterval = setInterval(() => {
      setAnalysisProgress(prev => ({
        ...prev,
        [accountId]: {
          ...prev[accountId],
          progress: Math.min(100, prev[accountId].progress + 5)
        }
      }));
    }, 200);

    stages.forEach((stage, index) => {
      setTimeout(() => {
        setAnalysisProgress(prev => ({
          ...prev,
          [accountId]: {
            ...prev[accountId],
            stage: stage.name,
            progress: 0
          }
        }));

        if (index === stages.length - 1) {
          clearInterval(progressInterval);
          completeAnalysis(accountId, account);
        }
      }, stages.slice(0, index).reduce((sum, s) => sum + s.duration, 0));
    });
  };

  const completeAnalysis = (accountId, account) => {
    const newInsights = account.insights.map((insight, index) => ({
      id: `${accountId}_${index}`,
      type: insight.toLowerCase().replace(' ', '_'),
      title: insight,
      description: generateInsightDescription(insight, account.name),
      confidence: Math.floor(Math.random() * 20) + 80,
      source: account.name,
      category: account.category
    }));

    setPersonalityInsights(prev => [...prev, ...newInsights]);
    
    setAnalysisProgress(prev => ({
      ...prev,
      [accountId]: {
        ...prev[accountId],
        stage: 'completed',
        progress: 100
      }
    }));
  };

  const generateInsightDescription = (insight, source) => {
    const descriptions = {
      'Communication style': `Analysis of your ${source} data reveals a ${Math.random() > 0.5 ? 'direct and analytical' : 'warm and collaborative'} communication approach`,
      'Professional network': `Your email patterns show ${Math.random() > 0.5 ? 'strong leadership connections' : 'diverse industry relationships'}`,
      'Social style': `Your messaging patterns indicate ${Math.random() > 0.5 ? 'high social engagement' : 'selective but deep connections'}`,
      'Learning style': `Your content consumption shows ${Math.random() > 0.5 ? 'systematic deep-dive learning' : 'broad exploratory interests'}`,
      'Visual aesthetic': `Your visual content preferences reveal ${Math.random() > 0.5 ? 'minimalist and professional' : 'creative and expressive'} tendencies`,
      'Time management': `Your calendar patterns show ${Math.random() > 0.5 ? 'structured and planned' : 'flexible and adaptive'} time management`
    };
    
    return descriptions[insight] || `Insights about your ${insight.toLowerCase()} patterns from ${source} analysis`;
  };

  const disconnectAccount = (accountId) => {
    setConnectedAccounts(prev => {
      const updated = { ...prev };
      delete updated[accountId];
      return updated;
    });
    
    setAnalysisProgress(prev => {
      const updated = { ...prev };
      delete updated[accountId];
      return updated;
    });

    setPersonalityInsights(prev => 
      prev.filter(insight => !insight.id.startsWith(accountId))
    );
  };

  const getStatusIcon = (accountId) => {
    const connection = connectedAccounts[accountId];
    if (!connection) return null;
    
    switch (connection.status) {
      case 'connecting':
        return <Clock className="status-icon connecting" />;
      case 'connected':
        return <CheckCircle className="status-icon connected" />;
      case 'error':
        return <AlertCircle className="status-icon error" />;
      default:
        return null;
    }
  };

  const getAnalysisStageText = (stage) => {
    const stages = {
      'data_extraction': 'Extracting data...',
      'pattern_analysis': 'Analyzing patterns...',
      'personality_synthesis': 'Synthesizing personality...',
      'insight_generation': 'Generating insights...',
      'completed': 'Analysis complete!'
    };
    return stages[stage] || 'Processing...';
  };

  const getTierColor = (tier) => {
    const colors = {
      1: '#10b981', // Green - High value
      2: '#3b82f6', // Blue - Medium-high value
      3: '#f59e0b', // Orange - Medium value
      4: '#8b5cf6'  // Purple - Lifestyle value
    };
    return colors[tier] || '#6b7280';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'communication': MessageCircle,
      'social': Instagram,
      'content': Youtube,
      'productivity': FileText,
      'lifestyle': Music
    };
    return icons[category] || FileText;
  };

  return (
    <div className="data-connection-dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1>🔗 Connect Your Digital Life</h1>
          <p>Allow our AI to analyze your personal data for hyper-personalized entrepreneurial insights</p>
          
          <div className="connection-stats">
            <div className="stat">
              <span className="stat-number">{Object.keys(connectedAccounts).length}</span>
              <span className="stat-label">Connected Accounts</span>
            </div>
            <div className="stat">
              <span className="stat-number">{personalityInsights.length}</span>
              <span className="stat-label">AI Insights Generated</span>
            </div>
            <div className="stat">
              <span className="stat-number">
                {Object.values(analysisProgress).filter(p => p.stage === 'completed').length}
              </span>
              <span className="stat-label">Analyses Complete</span>
            </div>
          </div>
        </div>

        <div className="privacy-controls-header">
          <button 
            className="privacy-button"
            onClick={() => setShowPrivacyModal(true)}
          >
            <Shield className="icon" />
            Privacy Controls
          </button>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="accounts-section">
          <h2>Available Data Sources</h2>
          <p>Connect your accounts to unlock personalized insights. All data is encrypted and used only for your benefit.</p>
          
          <div className="accounts-grid">
            {accountTypes.map(account => {
              const connection = connectedAccounts[account.id];
              const analysis = analysisProgress[account.id];
              const isConnected = connection?.status === 'connected';
              const isConnecting = connection?.status === 'connecting';
              const isAnalyzing = analysis && analysis.stage !== 'completed';
              
              return (
                <div 
                  key={account.id} 
                  className={`account-card ${isConnected ? 'connected' : ''} ${isConnecting ? 'connecting' : ''}`}
                  onClick={() => setSelectedAccount(account)}
                >
                  <div className="account-header">
                    <div className="account-icon-wrapper">
                      <account.icon 
                        className="account-icon" 
                        style={{ color: getTierColor(account.tier) }}
                      />
                      {getStatusIcon(account.id)}
                    </div>
                    
                    <div className="account-info">
                      <h3>{account.name}</h3>
                      <span className="account-category">{account.category}</span>
                    </div>
                    
                    <div className="tier-badge" style={{ backgroundColor: getTierColor(account.tier) }}>
                      Tier {account.tier}
                    </div>
                  </div>

                  <p className="account-description">{account.description}</p>

                  <div className="account-metrics">
                    <div className="metric">
                      <Clock className="metric-icon" />
                      <span>{account.estimatedTime}</span>
                    </div>
                    <div className="metric">
                      <Activity className="metric-icon" />
                      <span>{account.dataVolume} data</span>
                    </div>
                    <div className="metric">
                      <Shield className="metric-icon" />
                      <span>{account.privacyLevel} privacy</span>
                    </div>
                  </div>

                  {isAnalyzing && (
                    <div className="analysis-progress">
                      <div className="progress-header">
                        <span className="progress-text">
                          {getAnalysisStageText(analysis.stage)}
                        </span>
                        <span className="progress-percentage">{analysis.progress}%</span>
                      </div>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ width: `${analysis.progress}%` }}
                        />
                      </div>
                    </div>
                  )}

                  <div className="account-actions">
                    {!isConnected && !isConnecting && (
                      <button 
                        className="connect-button"
                        onClick={(e) => {
                          e.stopPropagation();
                          connectAccount(account.id);
                        }}
                      >
                        <Zap className="icon" />
                        Connect Account
                      </button>
                    )}
                    
                    {isConnecting && (
                      <button className="connect-button connecting" disabled>
                        <RefreshCw className="icon spinning" />
                        Connecting...
                      </button>
                    )}
                    
                    {isConnected && (
                      <div className="connected-actions">
                        <button className="connected-indicator">
                          <CheckCircle className="icon" />
                          Connected
                        </button>
                        <button 
                          className="disconnect-button"
                          onClick={(e) => {
                            e.stopPropagation();
                            disconnectAccount(account.id);
                          }}
                        >
                          <Trash2 className="icon" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {personalityInsights.length > 0 && (
          <div className="insights-section">
            <h2>🧠 AI-Generated Personality Insights</h2>
            <p>Based on analysis of your connected accounts, here's what our AI discovered about your personality:</p>
            
            <div className="insights-grid">
              {personalityInsights.map(insight => (
                <div key={insight.id} className="insight-card">
                  <div className="insight-header">
                    <div className="insight-icon">
                      <Brain className="icon" />
                    </div>
                    <div className="insight-info">
                      <h4>{insight.title}</h4>
                      <span className="insight-source">From {insight.source}</span>
                    </div>
                    <div className="confidence-badge">
                      {insight.confidence}% confident
                    </div>
                  </div>
                  
                  <p className="insight-description">{insight.description}</p>
                  
                  <div className="insight-actions">
                    <button className="apply-insight-button">
                      <Target className="icon" />
                      Apply to Assessment
                    </button>
                    <button className="insight-details-button">
                      <Eye className="icon" />
                      View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {selectedAccount && (
        <div className="account-modal-overlay" onClick={() => setSelectedAccount(null)}>
          <div className="account-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Connect {selectedAccount.name}</h3>
              <button 
                className="close-button"
                onClick={() => setSelectedAccount(null)}
              >
                ×
              </button>
            </div>
            
            <div className="modal-content">
              <div className="account-details">
                <selectedAccount.icon className="large-icon" />
                <h4>{selectedAccount.name}</h4>
                <p>{selectedAccount.description}</p>
              </div>

              <div className="data-types">
                <h5>Data We'll Analyze:</h5>
                <ul>
                  {selectedAccount.dataTypes.map(type => (
                    <li key={type}>{type.replace('_', ' ').toUpperCase()}</li>
                  ))}
                </ul>
              </div>

              <div className="expected-insights">
                <h5>Expected Insights:</h5>
                <ul>
                  {selectedAccount.insights.map(insight => (
                    <li key={insight}>{insight}</li>
                  ))}
                </ul>
              </div>

              <div className="privacy-info">
                <Shield className="icon" />
                <div>
                  <h5>Privacy & Security</h5>
                  <p>Your data is encrypted, never shared, and used only to generate insights for your entrepreneurial assessment. You can disconnect anytime.</p>
                </div>
              </div>
            </div>

            <div className="modal-actions">
              <button 
                className="cancel-button"
                onClick={() => setSelectedAccount(null)}
              >
                Cancel
              </button>
              <button 
                className="connect-modal-button"
                onClick={() => {
                  connectAccount(selectedAccount.id);
                  setSelectedAccount(null);
                }}
              >
                <Zap className="icon" />
                Connect {selectedAccount.name}
              </button>
            </div>
          </div>
        </div>
      )}

      {showPrivacyModal && (
        <div className="privacy-modal-overlay" onClick={() => setShowPrivacyModal(false)}>
          <div className="privacy-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Privacy & Data Controls</h3>
              <button 
                className="close-button"
                onClick={() => setShowPrivacyModal(false)}
              >
                ×
              </button>
            </div>
            
            <div className="privacy-content">
              <div className="privacy-section">
                <h4>Data Retention</h4>
                <select 
                  value={privacySettings.dataRetention}
                  onChange={e => setPrivacySettings(prev => ({
                    ...prev,
                    dataRetention: e.target.value
                  }))}
                >
                  <option value="3months">3 Months</option>
                  <option value="6months">6 Months</option>
                  <option value="12months">12 Months</option>
                  <option value="indefinite">Until Disconnected</option>
                </select>
              </div>

              <div className="privacy-section">
                <h4>Insight Visibility</h4>
                <select 
                  value={privacySettings.insightVisibility}
                  onChange={e => setPrivacySettings(prev => ({
                    ...prev,
                    insightVisibility: e.target.value
                  }))}
                >
                  <option value="private">Private (Only You)</option>
                  <option value="anonymous">Anonymous Research</option>
                </select>
              </div>

              <div className="privacy-section">
                <h4>Analysis Depth</h4>
                <select 
                  value={privacySettings.analysisDepth}
                  onChange={e => setPrivacySettings(prev => ({
                    ...prev,
                    analysisDepth: e.target.value
                  }))}
                >
                  <option value="basic">Basic Patterns Only</option>
                  <option value="standard">Standard Analysis</option>
                  <option value="comprehensive">Comprehensive Insights</option>
                </select>
              </div>

              <div className="privacy-guarantees">
                <h4>Our Privacy Guarantees</h4>
                <ul>
                  <li>✅ End-to-end encryption for all data</li>
                  <li>✅ No data sharing with third parties</li>
                  <li>✅ You can disconnect and delete anytime</li>
                  <li>✅ GDPR and CCPA compliant</li>
                  <li>✅ Regular security audits</li>
                </ul>
              </div>
            </div>

            <div className="modal-actions">
              <button 
                className="save-privacy-button"
                onClick={() => setShowPrivacyModal(false)}
              >
                Save Settings
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataConnectionDashboard;

