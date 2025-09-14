import React, { useState, useEffect } from 'react';
import { User, Heart, Target, BarChart3, Clock, CheckCircle, ArrowRight, ArrowLeft } from 'lucide-react';
import { MaslowAssessment } from './MaslowAssessment';
import { ComprehensiveIkigaiSystem } from './ComprehensiveIkigaiSystem';
import { PersonalityQualitiesAssessment } from './PersonalityQualitiesAssessment';
import { ValuesAndPriorities } from './ValuesAndPriorities';
import { LifeImpactTimeline } from './LifeImpactTimeline';
import { DataConnectionDashboard } from './DataConnectionDashboard';
import './EnhancedSelfDiscoveryPhase.css';

const EnhancedSelfDiscoveryPhase = ({ 
  userData = {}, 
  onUserDataChange,
  onPhaseComplete 
}) => {
  const [activeSubsection, setActiveSubsection] = useState('maslow-assessment');
  const [assessmentData, setAssessmentData] = useState({
    maslowLevel: userData.maslowLevel || null,
    ikigaiScores: userData.ikigaiScores || { heart: 0, body: 0, mind: 0, soul: 0 },
    personalityQualities: userData.personalityQualities || {},
    values: userData.values || {},
    reflectiveAnswers: userData.reflectiveAnswers || {},
    lifeEvents: userData.lifeEvents || [],
    connectedAccounts: userData.connectedAccounts || {},
    ...userData
  });
  const [completionStats, setCompletionStats] = useState({});

  // Self-discovery subsections with enhanced assessments
  const subsections = [
    {
      id: 'maslow-assessment',
      title: 'Life Foundation Assessment',
      description: 'Understand your current life situation and needs hierarchy',
      icon: <Target className="w-5 h-5" />,
      color: '#ff6b35',
      estimatedTime: '10-15 min',
      component: 'maslow'
    },
    {
      id: 'data-integration',
      title: 'Personal Data Integration',
      description: 'Connect your digital accounts for AI-powered personality insights',
      icon: <BarChart3 className="w-5 h-5" />,
      color: '#3b82f6',
      estimatedTime: '5-10 min',
      component: 'data'
    },
    {
      id: 'personality-assessment',
      title: 'Personality Profile',
      description: 'Comprehensive assessment of your personality qualities and traits',
      icon: <User className="w-5 h-5" />,
      color: '#10b981',
      estimatedTime: '15-20 min',
      component: 'personality'
    },
    {
      id: 'values-priorities',
      title: 'Values & Priorities',
      description: 'Discover your core values and life priorities through deep reflection',
      icon: <Heart className="w-5 h-5" />,
      color: '#f59e0b',
      estimatedTime: '20-25 min',
      component: 'values'
    },
    {
      id: 'life-impact-timeline',
      title: 'Life Impact Assessment',
      description: 'Map significant life events that shaped your entrepreneurial mindset',
      icon: <Clock className="w-5 h-5" />,
      color: '#8b5cf6',
      estimatedTime: '15-20 min',
      component: 'timeline'
    },
    {
      id: 'ikigai-synthesis',
      title: 'Entrepreneurial Ikigai',
      description: 'Synthesize all assessments into your unique entrepreneurial profile',
      icon: <CheckCircle className="w-5 h-5" />,
      color: '#ef4444',
      estimatedTime: '10-15 min',
      component: 'ikigai'
    }
  ];

  useEffect(() => {
    calculateCompletionStats();
  }, [assessmentData]);

  const calculateCompletionStats = () => {
    const stats = {};
    
    // Maslow Assessment
    stats.maslow = {
      completed: assessmentData.maslowLevel !== null,
      percentage: assessmentData.maslowLevel !== null ? 100 : 0
    };

    // Data Integration
    const connectedCount = Object.keys(assessmentData.connectedAccounts).length;
    stats.data = {
      completed: connectedCount > 0,
      percentage: Math.min((connectedCount / 5) * 100, 100) // Up to 5 major connections
    };

    // Personality Assessment
    const personalityCount = Object.keys(assessmentData.personalityQualities).length;
    stats.personality = {
      completed: personalityCount >= 20, // At least 20 out of 30 qualities
      percentage: Math.min((personalityCount / 30) * 100, 100)
    };

    // Values & Priorities
    const valuesCount = Object.keys(assessmentData.values).length;
    const reflectionCount = Object.keys(assessmentData.reflectiveAnswers).filter(
      key => assessmentData.reflectiveAnswers[key] && assessmentData.reflectiveAnswers[key].length > 50
    ).length;
    const valuesPercentage = Math.min((valuesCount / 36) * 100, 100); // 36 core values
    const reflectionPercentage = Math.min((reflectionCount / 5) * 100, 100); // 5 reflection questions
    stats.values = {
      completed: valuesPercentage >= 70 && reflectionPercentage >= 80,
      percentage: (valuesPercentage + reflectionPercentage) / 2
    };

    // Life Impact Timeline
    const eventsCount = assessmentData.lifeEvents.length;
    stats.timeline = {
      completed: eventsCount >= 5, // At least 5 significant events
      percentage: Math.min((eventsCount / 10) * 100, 100) // Up to 10 events for 100%
    };

    // Ikigai Synthesis
    const ikigaiSum = Object.values(assessmentData.ikigaiScores).reduce((sum, score) => sum + score, 0);
    const ikigaiAverage = ikigaiSum / 4;
    stats.ikigai = {
      completed: ikigaiAverage >= 60, // Average score of 60+
      percentage: Math.min(ikigaiAverage, 100)
    };

    // Overall completion
    const overallPercentage = Object.values(stats).reduce((sum, stat) => sum + stat.percentage, 0) / 6;
    const completedSections = Object.values(stats).filter(stat => stat.completed).length;
    
    stats.overall = {
      completed: completedSections >= 5, // At least 5 out of 6 sections
      percentage: overallPercentage,
      completedSections,
      totalSections: 6
    };

    setCompletionStats(stats);
  };

  const handleDataChange = (section, data) => {
    const updatedData = { ...assessmentData, ...data };
    setAssessmentData(updatedData);
    onUserDataChange && onUserDataChange(updatedData);
  };

  const getCurrentSubsection = () => {
    return subsections.find(section => section.id === activeSubsection);
  };

  const getNextSubsection = () => {
    const currentIndex = subsections.findIndex(section => section.id === activeSubsection);
    return currentIndex < subsections.length - 1 ? subsections[currentIndex + 1] : null;
  };

  const getPreviousSubsection = () => {
    const currentIndex = subsections.findIndex(section => section.id === activeSubsection);
    return currentIndex > 0 ? subsections[currentIndex - 1] : null;
  };

  const navigateToNext = () => {
    const next = getNextSubsection();
    if (next) {
      setActiveSubsection(next.id);
    } else if (completionStats.overall?.completed) {
      onPhaseComplete && onPhaseComplete(assessmentData);
    }
  };

  const navigateToPrevious = () => {
    const previous = getPreviousSubsection();
    if (previous) {
      setActiveSubsection(previous.id);
    }
  };

  const renderSubsectionContent = () => {
    const currentSection = getCurrentSubsection();
    
    switch (currentSection.component) {
      case 'maslow':
        return (
          <MaslowAssessment
            currentLevel={assessmentData.maslowLevel}
            onLevelChange={(level) => handleDataChange('maslow', { maslowLevel: level })}
            contextualQuestions={true}
          />
        );
      
      case 'data':
        return (
          <DataConnectionDashboard
            connectedAccounts={assessmentData.connectedAccounts}
            onAccountsChange={(accounts) => handleDataChange('data', { connectedAccounts: accounts })}
            personalityInsights={assessmentData.aiPersonalityInsights}
            onInsightsChange={(insights) => handleDataChange('data', { aiPersonalityInsights: insights })}
          />
        );
      
      case 'personality':
        return (
          <PersonalityQualitiesAssessment
            qualities={assessmentData.personalityQualities}
            onQualitiesChange={(qualities) => handleDataChange('personality', { personalityQualities: qualities })}
            showResults={completionStats.personality?.percentage >= 70}
          />
        );
      
      case 'values':
        return (
          <ValuesAndPriorities
            values={assessmentData.values}
            reflectiveAnswers={assessmentData.reflectiveAnswers}
            onValuesChange={(values) => handleDataChange('values', { values })}
            onReflectiveAnswersChange={(answers) => handleDataChange('values', { reflectiveAnswers: answers })}
          />
        );
      
      case 'timeline':
        return (
          <LifeImpactTimeline
            events={assessmentData.lifeEvents}
            onEventsChange={(events) => handleDataChange('timeline', { lifeEvents: events })}
            timelineStart={new Date().getFullYear() - 40}
            timelineEnd={new Date().getFullYear() + 5}
          />
        );
      
      case 'ikigai':
        return (
          <ComprehensiveIkigaiSystem
            assessmentData={assessmentData}
            ikigaiScores={assessmentData.ikigaiScores}
            onScoresChange={(scores) => handleDataChange('ikigai', { ikigaiScores: scores })}
            showAntiIkigai={true}
            showIntermediateStates={true}
          />
        );
      
      default:
        return <div>Section not found</div>;
    }
  };

  const renderProgressOverview = () => (
    <div className="progress-overview">
      <div className="overview-header">
        <h3>Self-Discovery Progress</h3>
        <div className="overall-progress">
          <div className="progress-circle">
            <div 
              className="progress-fill"
              style={{
                background: `conic-gradient(#ff6b35 0deg, #ff6b35 ${(completionStats.overall?.percentage || 0) * 3.6}deg, rgba(255,255,255,0.1) ${(completionStats.overall?.percentage || 0) * 3.6}deg, rgba(255,255,255,0.1) 360deg)`
              }}
            >
              <div className="progress-inner">
                <span className="progress-text">{Math.round(completionStats.overall?.percentage || 0)}%</span>
              </div>
            </div>
          </div>
          <div className="progress-label">
            {completionStats.overall?.completedSections || 0}/{completionStats.overall?.totalSections || 6} sections complete
          </div>
        </div>
      </div>

      <div className="sections-grid">
        {subsections.map(section => {
          const sectionStats = completionStats[section.component] || { completed: false, percentage: 0 };
          return (
            <div
              key={section.id}
              className={`section-card ${activeSubsection === section.id ? 'active' : ''} ${sectionStats.completed ? 'completed' : ''}`}
              onClick={() => setActiveSubsection(section.id)}
              style={{ '--section-color': section.color }}
            >
              <div className="section-header">
                <div className="section-icon" style={{ color: section.color }}>
                  {section.icon}
                </div>
                <div className="section-status">
                  {sectionStats.completed && <CheckCircle className="w-4 h-4 text-green-400" />}
                </div>
              </div>
              
              <div className="section-content">
                <h4 className="section-title">{section.title}</h4>
                <p className="section-description">{section.description}</p>
                <div className="section-meta">
                  <span className="estimated-time">{section.estimatedTime}</span>
                  <div className="section-progress">
                    <div 
                      className="progress-bar"
                      style={{ 
                        width: `${sectionStats.percentage}%`,
                        backgroundColor: section.color
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const currentSection = getCurrentSubsection();
  const nextSection = getNextSubsection();
  const previousSection = getPreviousSubsection();
  const currentStats = completionStats[currentSection?.component] || { completed: false, percentage: 0 };

  return (
    <div className="enhanced-self-discovery-phase">
      <div className="phase-header">
        <h1>Self-Discovery Phase</h1>
        <p>
          Embark on a comprehensive journey of self-discovery designed specifically for aspiring entrepreneurs. 
          This multi-dimensional assessment combines psychology, personal values, life experiences, and AI insights 
          to create your unique entrepreneurial profile.
        </p>
      </div>

      <div className="phase-layout">
        <div className="sidebar">
          {renderProgressOverview()}
        </div>

        <div className="main-content">
          <div className="content-header">
            <div className="section-info">
              <div className="section-icon" style={{ color: currentSection?.color }}>
                {currentSection?.icon}
              </div>
              <div className="section-details">
                <h2>{currentSection?.title}</h2>
                <p>{currentSection?.description}</p>
                <div className="section-meta">
                  <span className="time-estimate">⏱️ {currentSection?.estimatedTime}</span>
                  <div className="completion-indicator">
                    <span className="completion-text">
                      {Math.round(currentStats.percentage)}% Complete
                    </span>
                    <div className="completion-bar">
                      <div 
                        className="completion-fill"
                        style={{ 
                          width: `${currentStats.percentage}%`,
                          backgroundColor: currentSection?.color
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="section-content">
            {renderSubsectionContent()}
          </div>

          <div className="navigation-controls">
            <button
              className="nav-button previous"
              onClick={navigateToPrevious}
              disabled={!previousSection}
            >
              <ArrowLeft className="w-4 h-4" />
              {previousSection ? `Previous: ${previousSection.title}` : 'Previous'}
            </button>

            <div className="section-indicator">
              {subsections.map((section, index) => (
                <div
                  key={section.id}
                  className={`indicator-dot ${activeSubsection === section.id ? 'active' : ''} ${completionStats[section.component]?.completed ? 'completed' : ''}`}
                  style={{ '--dot-color': section.color }}
                  onClick={() => setActiveSubsection(section.id)}
                />
              ))}
            </div>

            <button
              className="nav-button next"
              onClick={navigateToNext}
              disabled={!nextSection && !completionStats.overall?.completed}
            >
              {nextSection ? `Next: ${nextSection.title}` : completionStats.overall?.completed ? 'Complete Phase' : 'Next'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedSelfDiscoveryPhase;

