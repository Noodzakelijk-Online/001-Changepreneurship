import React, { useState, useEffect } from 'react';
import { useAssessment } from '../contexts/AssessmentContext';
import { 
  User, 
  Lightbulb, 
  Search, 
  Building, 
  TestTube, 
  Settings, 
  Rocket,
  ChevronDown,
  ChevronRight,
  CheckCircle,
  Clock,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react';
import { Progress } from './ui/progress';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

// Import individual assessment components
import SelfDiscoveryAssessment from './assessment/SelfDiscoveryAssessment';
import IdeaDiscoveryAssessment from './assessment/IdeaDiscoveryAssessment';
import MarketResearchTools from './assessment/MarketResearchTools';
import BusinessPillarsPlanning from './assessment/BusinessPillarsPlanning';
import ProductConceptTesting from './assessment/ProductConceptTesting';
import BusinessDevelopmentDecisionMaking from './assessment/BusinessDevelopmentDecisionMaking';
import BusinessPrototypeTesting from './assessment/BusinessPrototypeTesting';

import './ExpandablePhaseInterface.css';

const ExpandablePhaseInterface = () => {
  const { assessmentData, updateAssessmentData, currentPhase, updatePhase } = useAssessment();
  const [expandedPhase, setExpandedPhase] = useState(null);
  const [phaseProgress, setPhaseProgress] = useState({});

  const phases = [
    {
      id: 'self-discovery',
      title: 'Self Discovery',
      description: 'Understand your entrepreneurial personality and motivations',
      icon: User,
      duration: '60-90 min',
      category: 'Foundation',
      color: '#ff6b35', // Orange
      questions: 25,
      component: SelfDiscoveryAssessment
    },
    {
      id: 'idea-discovery',
      title: 'Idea Discovery',
      description: 'Identify and validate your business ideas',
      icon: Lightbulb,
      duration: '90-120 min',
      category: 'Foundation',
      color: '#3b82f6', // Light Blue
      questions: 30,
      component: IdeaDiscoveryAssessment
    },
    {
      id: 'market-research',
      title: 'Market Research',
      description: 'Analyze your market and competition',
      icon: Search,
      duration: '2-3 weeks',
      category: 'Foundation',
      color: '#10b981', // Green
      questions: 35,
      component: MarketResearchTools
    },
    {
      id: 'business-pillars',
      title: 'Business Pillars',
      description: 'Build your comprehensive business plan',
      icon: Building,
      duration: '1-2 weeks',
      category: 'Foundation',
      color: '#8b5cf6', // Purple
      questions: 40,
      component: BusinessPillarsPlanning
    },
    {
      id: 'product-concept-testing',
      title: 'Product Concept Testing',
      description: 'Test and validate your product concepts',
      icon: TestTube,
      duration: '3-4 days',
      category: 'Implementation',
      color: '#f59e0b', // Yellow/Ocher
      questions: 20,
      component: ProductConceptTesting
    },
    {
      id: 'business-development',
      title: 'Business Development',
      description: 'Make strategic decisions and align resources',
      icon: Settings,
      duration: '1-2 weeks',
      category: 'Implementation',
      color: '#1e40af', // Dark Blue
      questions: 28,
      component: BusinessDevelopmentDecisionMaking
    },
    {
      id: 'business-prototype-testing',
      title: 'Business Prototype Testing',
      description: 'Test your complete business model',
      icon: Rocket,
      duration: '2-4 weeks',
      category: 'Implementation',
      color: '#ef4444', // Red
      questions: 32,
      component: BusinessPrototypeTesting
    }
  ];

  useEffect(() => {
    // Calculate progress for each phase
    const progress = {};
    phases.forEach(phase => {
      const phaseData = assessmentData[phase.id] || {};
      const answeredQuestions = Object.keys(phaseData).filter(key => 
        phaseData[key] && phaseData[key] !== ''
      ).length;
      progress[phase.id] = Math.round((answeredQuestions / phase.questions) * 100);
    });
    setPhaseProgress(progress);
  }, [assessmentData]);

  const handlePhaseClick = (phaseId) => {
    if (expandedPhase === phaseId) {
      setExpandedPhase(null);
    } else {
      setExpandedPhase(phaseId);
      updatePhase(phaseId);
    }
  };

  const getPhaseStatus = (phaseId) => {
    const progress = phaseProgress[phaseId] || 0;
    if (progress === 100) return 'completed';
    if (progress > 0) return 'in-progress';
    return 'not-started';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="status-icon completed" />;
      case 'in-progress':
        return <Clock className="status-icon in-progress" />;
      default:
        return <Play className="status-icon not-started" />;
    }
  };

  const getStatusText = (status, progress) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'in-progress':
        return `${progress}% Complete`;
      default:
        return 'Not Started';
    }
  };

  const renderPhaseComponent = (phase) => {
    const Component = phase.component;
    return (
      <div className="phase-content-wrapper">
        <div className="phase-content-header">
          <div className="phase-content-info">
            <h2>{phase.title}</h2>
            <p>{phase.description}</p>
            <div className="phase-meta">
              <span className="duration">⏱️ {phase.duration}</span>
              <span className="questions">📝 {phase.questions} questions</span>
              <span className="category">📂 {phase.category}</span>
            </div>
          </div>
          <div className="phase-actions">
            <Button 
              variant="outline" 
              onClick={() => setExpandedPhase(null)}
              className="collapse-button"
            >
              Collapse Phase
            </Button>
            <Button 
              onClick={() => {
                // Reset phase progress
                const resetData = { ...assessmentData };
                delete resetData[phase.id];
                updateAssessmentData(resetData);
              }}
              variant="outline"
              className="reset-button"
            >
              <RotateCcw className="w-4 h-4" />
              Reset Phase
            </Button>
          </div>
        </div>
        
        <div className="phase-component">
          <Component />
        </div>
      </div>
    );
  };

  return (
    <div className="expandable-phase-interface">
      <div className="interface-header">
        <h1>🚀 Entrepreneurship Assessment Journey</h1>
        <p>Complete your entrepreneurial self-discovery through our comprehensive 7-phase framework</p>
      </div>

      <div className="phases-container">
        {phases.map((phase, index) => {
          const isExpanded = expandedPhase === phase.id;
          const status = getPhaseStatus(phase.id);
          const progress = phaseProgress[phase.id] || 0;
          const IconComponent = phase.icon;

          return (
            <div 
              key={phase.id} 
              className={`phase-card ${isExpanded ? 'expanded' : ''} ${status}`}
              style={{
                '--phase-color': phase.color,
                '--phase-color-light': phase.color + '20',
                '--phase-color-dark': phase.color + 'dd'
              }}
            >
              <div 
                className="phase-header"
                onClick={() => handlePhaseClick(phase.id)}
              >
                <div className="phase-number">
                  {index + 1}
                </div>
                
                <div className="phase-icon">
                  <IconComponent className="icon" />
                </div>
                
                <div className="phase-info">
                  <div className="phase-title-row">
                    <h3 className="phase-title">{phase.title}</h3>
                    <div className="phase-status">
                      {getStatusIcon(status)}
                      <span className="status-text">
                        {getStatusText(status, progress)}
                      </span>
                    </div>
                  </div>
                  
                  <p className="phase-description">{phase.description}</p>
                  
                  <div className="phase-details">
                    <div className="phase-meta-info">
                      <span className="duration">⏱️ {phase.duration}</span>
                      <span className="questions">📝 {phase.questions} questions</span>
                      <span className="category">📂 {phase.category}</span>
                    </div>
                    
                    <div className="phase-progress">
                      <div className="progress-info">
                        <span className="progress-label">Progress</span>
                        <span className="progress-percentage">{progress}%</span>
                      </div>
                      <Progress 
                        value={progress} 
                        className="progress-bar"
                        style={{
                          '--progress-color': phase.color
                        }}
                      />
                    </div>
                  </div>
                </div>
                
                <div className="expand-indicator">
                  {isExpanded ? (
                    <ChevronDown className="chevron expanded" />
                  ) : (
                    <ChevronRight className="chevron" />
                  )}
                </div>
              </div>

              {isExpanded && (
                <div className="phase-expanded-content">
                  <div className="expansion-flow"></div>
                  {renderPhaseComponent(phase)}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="overall-progress">
        <Card>
          <CardHeader>
            <CardTitle>Overall Assessment Progress</CardTitle>
            <CardDescription>
              Your journey through the 7-phase entrepreneurship framework
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overall-stats">
              <div className="stat">
                <div className="stat-number">
                  {phases.filter(p => getPhaseStatus(p.id) === 'completed').length}
                </div>
                <div className="stat-label">Phases Completed</div>
              </div>
              <div className="stat">
                <div className="stat-number">
                  {phases.filter(p => getPhaseStatus(p.id) === 'in-progress').length}
                </div>
                <div className="stat-label">In Progress</div>
              </div>
              <div className="stat">
                <div className="stat-number">
                  {Math.round(
                    Object.values(phaseProgress).reduce((sum, progress) => sum + progress, 0) / phases.length
                  )}%
                </div>
                <div className="stat-label">Overall Progress</div>
              </div>
            </div>
            
            <div className="phase-overview">
              {phases.map(phase => {
                const progress = phaseProgress[phase.id] || 0;
                const status = getPhaseStatus(phase.id);
                
                return (
                  <div key={phase.id} className="phase-overview-item">
                    <div className="phase-overview-info">
                      <span className="phase-name">{phase.title}</span>
                      <span className="phase-progress-text">{progress}%</span>
                    </div>
                    <Progress 
                      value={progress} 
                      className="phase-overview-progress"
                      style={{ '--progress-color': phase.color }}
                    />
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ExpandablePhaseInterface;

