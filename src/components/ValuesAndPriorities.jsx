import React, { useState, useEffect } from 'react';
import { Heart, Users, Target, Globe, Lightbulb, DollarSign, Shield, Star, Compass, BookOpen, Zap, Award } from 'lucide-react';
import { ContextualValueSlider, ImportanceSlider } from './ContextualValueSlider';
import { GmailStyleWritingAssistant } from './GmailStyleWritingAssistant';
import './ValuesAndPriorities.css';

const ValuesAndPriorities = ({ 
  values = {}, 
  reflectiveAnswers = {},
  onValuesChange, 
  onReflectiveAnswersChange 
}) => {
  const [activeTab, setActiveTab] = useState('values-rating');
  const [currentValues, setCurrentValues] = useState(values);
  const [currentAnswers, setCurrentAnswers] = useState(reflectiveAnswers);

  // Comprehensive values list from the Dutch exercise
  const valuesList = [
    // Personal Growth & Character
    { id: 'discipline', name: 'Discipline', category: 'personal', icon: <Target className="w-4 h-4" /> },
    { id: 'plezier', name: 'Pleasure/Fun', category: 'personal', icon: <Heart className="w-4 h-4" /> },
    { id: 'zekerheid', name: 'Security', category: 'personal', icon: <Shield className="w-4 h-4" /> },
    { id: 'kennis', name: 'Knowledge', category: 'personal', icon: <BookOpen className="w-4 h-4" /> },
    { id: 'eerlijkheid', name: 'Honesty', category: 'personal', icon: <Star className="w-4 h-4" /> },
    { id: 'rechtvaardigheid', name: 'Justice', category: 'personal', icon: <Award className="w-4 h-4" /> },
    { id: 'ontspanning', name: 'Relaxation', category: 'personal', icon: <Heart className="w-4 h-4" /> },
    { id: 'wijsheid', name: 'Wisdom', category: 'personal', icon: <Lightbulb className="w-4 h-4" /> },
    { id: 'waardering', name: 'Appreciation', category: 'personal', icon: <Star className="w-4 h-4" /> },
    { id: 'toewijding', name: 'Dedication', category: 'personal', icon: <Target className="w-4 h-4" /> },
    { id: 'moed', name: 'Courage', category: 'personal', icon: <Zap className="w-4 h-4" /> },
    { id: 'macht', name: 'Power', category: 'personal', icon: <Target className="w-4 h-4" /> },
    { id: 'flexibiliteit', name: 'Flexibility', category: 'personal', icon: <Compass className="w-4 h-4" /> },
    { id: 'tolerantie', name: 'Tolerance', category: 'personal', icon: <Heart className="w-4 h-4" /> },
    { id: 'gezondheid', name: 'Health', category: 'personal', icon: <Shield className="w-4 h-4" /> },
    { id: 'afwisseling', name: 'Variety', category: 'personal', icon: <Compass className="w-4 h-4" /> },
    { id: 'humor', name: 'Humor', category: 'personal', icon: <Heart className="w-4 h-4" /> },
    { id: 'verantwoordelijkheid', name: 'Responsibility', category: 'personal', icon: <Target className="w-4 h-4" /> },
    { id: 'integriteit', name: 'Integrity', category: 'personal', icon: <Star className="w-4 h-4" /> },
    { id: 'zelfvertrouwen', name: 'Self-confidence', category: 'personal', icon: <Zap className="w-4 h-4" /> },
    { id: 'liefde', name: 'Love', category: 'personal', icon: <Heart className="w-4 h-4" /> },
    { id: 'vertrouwen', name: 'Trust', category: 'personal', icon: <Shield className="w-4 h-4" /> },
    { id: 'uitdaging', name: 'Challenge', category: 'personal', icon: <Target className="w-4 h-4" /> },
    { id: 'avontuur', name: 'Adventure', category: 'personal', icon: <Compass className="w-4 h-4" /> },
    { id: 'loyaliteit', name: 'Loyalty', category: 'personal', icon: <Heart className="w-4 h-4" /> },
    { id: 'schoonheid', name: 'Beauty', category: 'personal', icon: <Star className="w-4 h-4" /> },
    { id: 'gelijkwaardigheid', name: 'Equality', category: 'personal', icon: <Award className="w-4 h-4" /> },
    { id: 'innerlijke_rust', name: 'Inner Peace', category: 'personal', icon: <Heart className="w-4 h-4" /> },
    { id: 'onafhankelijkheid', name: 'Independence', category: 'personal', icon: <Zap className="w-4 h-4" /> },
    { id: 'zingeving', name: 'Meaning/Purpose', category: 'personal', icon: <Compass className="w-4 h-4" /> },
    { id: 'gehoorzaamheid', name: 'Obedience', category: 'personal', icon: <Target className="w-4 h-4" /> },
    { id: 'vriendschap', name: 'Friendship', category: 'social', icon: <Users className="w-4 h-4" /> },
    { id: 'creativiteit', name: 'Creativity', category: 'personal', icon: <Lightbulb className="w-4 h-4" /> },
    { id: 'zorgzaamheid', name: 'Care/Compassion', category: 'social', icon: <Heart className="w-4 h-4" /> },
    { id: 'eerroud', name: 'Honor', category: 'personal', icon: <Award className="w-4 h-4" /> },
    { id: 'intimiteit', name: 'Intimacy', category: 'personal', icon: <Heart className="w-4 h-4" /> },
    { id: 'openheid', name: 'Openness', category: 'personal', icon: <Compass className="w-4 h-4" /> }
  ];

  // Reflective questions from the exercise
  const reflectiveQuestions = [
    {
      id: 'happiness_source',
      question: 'What makes you happy in life?',
      description: 'Reflect on the activities, experiences, and moments that bring you genuine joy and fulfillment.',
      category: 'personal_fulfillment'
    },
    {
      id: 'family_friends_role',
      question: 'What role do family and friends play in your life?',
      description: 'Consider how your relationships with loved ones influence your decisions and provide meaning.',
      category: 'relationships'
    },
    {
      id: 'work_study_importance',
      question: 'What do you find important about your work or studies? How does satisfaction play a role? What makes it valuable?',
      description: 'Think about what drives you professionally and academically, and what gives your work meaning.',
      category: 'professional_purpose'
    },
    {
      id: 'societal_involvement',
      question: 'To what extent do you feel involved in Dutch society, the EU, and global society?',
      description: 'Reflect on your connection to your local community, country, and the world at large.',
      category: 'social_connection'
    },
    {
      id: 'spiritual_beliefs',
      question: 'How do you think about yourself as a higher power, God, or something that transcends everything? How much influence does this have on your life?',
      description: 'Consider your spiritual or philosophical beliefs and how they guide your decisions and worldview.',
      category: 'spiritual_philosophy'
    }
  ];

  const handleValueChange = (valueId, newValue) => {
    const updatedValues = { ...currentValues, [valueId]: newValue };
    setCurrentValues(updatedValues);
    onValuesChange && onValuesChange(updatedValues);
  };

  const handleReflectiveAnswerChange = (questionId, answer) => {
    const updatedAnswers = { ...currentAnswers, [questionId]: answer };
    setCurrentAnswers(updatedAnswers);
    onReflectiveAnswersChange && onReflectiveAnswersChange(updatedAnswers);
  };

  const getTopValues = () => {
    return Object.entries(currentValues)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([id, score]) => ({
        ...valuesList.find(v => v.id === id),
        score
      }))
      .filter(v => v.name);
  };

  const getCategoryValues = (category) => {
    return valuesList.filter(value => value.category === category);
  };

  const renderValuesRating = () => (
    <div className="values-rating-section">
      <div className="section-header">
        <h3>Rate Your Core Values</h3>
        <p>Rate how important each value is to you personally on a scale of 1-100. This will help identify your core values and priorities.</p>
      </div>

      <div className="values-categories">
        <div className="category-section">
          <h4 className="category-title">
            <Heart className="w-5 h-5" />
            Personal Values & Character
          </h4>
          <div className="values-grid">
            {getCategoryValues('personal').map(value => (
              <div key={value.id} className="value-item">
                <ImportanceSlider
                  question={`How important is ${value.name} to you?`}
                  value={currentValues[value.id] || 50}
                  onChange={(newValue) => handleValueChange(value.id, newValue)}
                  size="small"
                  goalContext={`${value.name} influences your entrepreneurial decisions, leadership style, and business culture.`}
                />
              </div>
            ))}
          </div>
        </div>

        <div className="category-section">
          <h4 className="category-title">
            <Users className="w-5 h-5" />
            Social & Relationship Values
          </h4>
          <div className="values-grid">
            {getCategoryValues('social').map(value => (
              <div key={value.id} className="value-item">
                <ImportanceSlider
                  question={`How important is ${value.name} to you?`}
                  value={currentValues[value.id] || 50}
                  onChange={(newValue) => handleValueChange(value.id, newValue)}
                  size="small"
                  goalContext={`${value.name} affects how you build teams, serve customers, and create business relationships.`}
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="top-values-summary">
        <h4>Your Top 10 Values</h4>
        <div className="top-values-list">
          {getTopValues().map((value, index) => (
            <div key={value.id} className="top-value-item">
              <div className="value-rank">#{index + 1}</div>
              <div className="value-info">
                <div className="value-icon">{value.icon}</div>
                <div className="value-details">
                  <span className="value-name">{value.name}</span>
                  <span className="value-score">{value.score}/100</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderReflectiveQuestions = () => (
    <div className="reflective-questions-section">
      <div className="section-header">
        <h3>Values Reflection Questions</h3>
        <p>Take time to deeply reflect on these questions. Your answers will provide insight into what truly drives and motivates you.</p>
      </div>

      <div className="questions-container">
        {reflectiveQuestions.map(question => (
          <div key={question.id} className="question-container">
            <div className="question-header">
              <h4 className="question-title">{question.question}</h4>
              <p className="question-description">{question.description}</p>
            </div>
            
            <div className="answer-container">
              <GmailStyleWritingAssistant
                placeholder="Take your time to reflect and write a thoughtful response..."
                value={currentAnswers[question.id] || ''}
                onChange={(value) => handleReflectiveAnswerChange(question.id, value)}
                questionContext={question.question}
                expectedLength="paragraph"
                suggestions={true}
                qualityFeedback={true}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderValuesSummary = () => {
    const topValues = getTopValues();
    const completedReflections = Object.values(currentAnswers).filter(answer => 
      answer && answer.trim().length > 50
    ).length;

    return (
      <div className="values-summary-section">
        <div className="section-header">
          <h3>Your Values Profile Summary</h3>
          <p>Based on your ratings and reflections, here's your comprehensive values profile.</p>
        </div>

        <div className="summary-grid">
          <div className="summary-card">
            <h4>Core Values Hierarchy</h4>
            <div className="core-values-list">
              {topValues.slice(0, 5).map((value, index) => (
                <div key={value.id} className="core-value-item">
                  <div className="value-position">#{index + 1}</div>
                  <div className="value-content">
                    <div className="value-icon">{value.icon}</div>
                    <div className="value-info">
                      <span className="value-name">{value.name}</span>
                      <div className="value-bar">
                        <div 
                          className="value-fill" 
                          style={{ width: `${value.score}%` }}
                        ></div>
                      </div>
                    </div>
                    <span className="value-score">{value.score}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="summary-card">
            <h4>Reflection Completion</h4>
            <div className="completion-stats">
              <div className="completion-circle">
                <div className="circle-progress">
                  <span className="progress-text">
                    {completedReflections}/{reflectiveQuestions.length}
                  </span>
                </div>
              </div>
              <p>Deep reflections completed</p>
            </div>
          </div>

          <div className="summary-card">
            <h4>Values-Based Insights</h4>
            <div className="insights-list">
              {topValues.slice(0, 3).map(value => (
                <div key={value.id} className="insight-item">
                  <div className="insight-icon">{value.icon}</div>
                  <div className="insight-text">
                    Your high rating for <strong>{value.name}</strong> suggests you'll thrive in entrepreneurial ventures that align with this value.
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="values-and-priorities">
      <div className="component-header">
        <h2>Values & Priorities Assessment</h2>
        <p>Understanding your core values is essential for entrepreneurial success. Your values guide decision-making, shape company culture, and determine what kind of business you'll be passionate about building.</p>
      </div>

      <div className="tabs-container">
        <div className="tabs-nav">
          <button 
            className={`tab-button ${activeTab === 'values-rating' ? 'active' : ''}`}
            onClick={() => setActiveTab('values-rating')}
          >
            <Target className="w-4 h-4" />
            Rate Your Values
          </button>
          <button 
            className={`tab-button ${activeTab === 'reflective-questions' ? 'active' : ''}`}
            onClick={() => setActiveTab('reflective-questions')}
          >
            <BookOpen className="w-4 h-4" />
            Deep Reflection
          </button>
          <button 
            className={`tab-button ${activeTab === 'summary' ? 'active' : ''}`}
            onClick={() => setActiveTab('summary')}
          >
            <Star className="w-4 h-4" />
            Values Profile
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'values-rating' && renderValuesRating()}
          {activeTab === 'reflective-questions' && renderReflectiveQuestions()}
          {activeTab === 'summary' && renderValuesSummary()}
        </div>
      </div>
    </div>
  );
};

export default ValuesAndPriorities;

