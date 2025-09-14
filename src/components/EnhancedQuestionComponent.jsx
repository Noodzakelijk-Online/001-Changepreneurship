import React, { useState, useEffect } from 'react';
import AIWritingAssistant from './AIWritingAssistant';
import './EnhancedQuestionComponent.css';

const EnhancedQuestionComponent = ({ 
  question, 
  onAnswer, 
  currentAnswer = '',
  questionIndex = 0,
  totalQuestions = 1,
  onNext,
  onPrevious,
  isRequired = false
}) => {
  const [answer, setAnswer] = useState(currentAnswer);
  const [isValid, setIsValid] = useState(false);
  const [showValidation, setShowValidation] = useState(false);

  // Determine question context for AI assistance
  const getQuestionContext = (questionText) => {
    const text = questionText.toLowerCase();
    
    if (text.includes('success') && text.includes('business')) {
      return 'business_success_vision';
    } else if (text.includes('passion') || text.includes('love') || text.includes('enjoy')) {
      return 'passion_discovery';
    } else if (text.includes('market') || text.includes('opportunity') || text.includes('customers')) {
      return 'market_opportunity';
    } else if (text.includes('skills') || text.includes('experience') || text.includes('good at')) {
      return 'skills_assessment';
    }
    
    return 'general';
  };

  const questionContext = getQuestionContext(question.text || question.title || '');

  // Validate answer
  useEffect(() => {
    if (isRequired) {
      const wordCount = answer.trim().split(/\s+/).filter(word => word.length > 0).length;
      setIsValid(wordCount >= 10); // Minimum 10 words for required questions
    } else {
      setIsValid(answer.trim().length > 0);
    }
  }, [answer, isRequired]);

  // Handle answer change
  const handleAnswerChange = (newAnswer) => {
    setAnswer(newAnswer);
    if (onAnswer) {
      onAnswer(newAnswer);
    }
  };

  // Handle next button
  const handleNext = () => {
    if (isRequired && !isValid) {
      setShowValidation(true);
      return;
    }
    
    if (onNext) {
      onNext();
    }
  };

  // Handle previous button
  const handlePrevious = () => {
    if (onPrevious) {
      onPrevious();
    }
  };

  // Get question type for styling
  const getQuestionType = () => {
    if (question.type) return question.type;
    if (question.text && question.text.includes('?')) return 'open_ended';
    return 'text';
  };

  const questionType = getQuestionType();

  return (
    <div className="enhanced-question-component">
      {/* Progress indicator */}
      <div className="question-progress">
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${((questionIndex + 1) / totalQuestions) * 100}%` }}
          ></div>
        </div>
        <span className="progress-text">
          Question {questionIndex + 1} of {totalQuestions}
        </span>
      </div>

      {/* Question header */}
      <div className="question-header">
        <div className="question-meta">
          {isRequired && <span className="required-badge">Required</span>}
          <span className="question-type">{questionType.replace('_', ' ')}</span>
        </div>
        
        <h2 className="question-title">
          {question.title || question.text || 'Question'}
        </h2>
        
        {question.description && (
          <p className="question-description">{question.description}</p>
        )}
        
        {question.hint && (
          <div className="question-hint">
            <span className="hint-icon">💡</span>
            <span className="hint-text">{question.hint}</span>
          </div>
        )}
      </div>

      {/* AI-powered writing area */}
      <div className="question-content">
        <AIWritingAssistant
          questionId={question.id || `question_${questionIndex}`}
          questionContext={questionContext}
          onTextChange={handleAnswerChange}
          initialText={answer}
          placeholder={`Share your thoughts about ${question.title || 'this question'}...`}
          disabled={false}
        />
        
        {/* Validation message */}
        {showValidation && !isValid && (
          <div className="validation-message">
            <span className="validation-icon">⚠️</span>
            <span className="validation-text">
              {isRequired 
                ? 'Please provide a more detailed response (at least 10 words)' 
                : 'Please provide an answer to continue'
              }
            </span>
          </div>
        )}
        
        {/* Answer quality indicator */}
        {answer.trim() && (
          <div className="answer-quality">
            <div className="quality-metrics">
              <div className="metric">
                <span className="metric-label">Words:</span>
                <span className="metric-value">
                  {answer.trim().split(/\s+/).filter(word => word.length > 0).length}
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Characters:</span>
                <span className="metric-value">{answer.length}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Quality:</span>
                <span className={`metric-value quality-${isValid ? 'good' : 'needs-improvement'}`}>
                  {isValid ? 'Good' : 'Needs more detail'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation buttons */}
      <div className="question-navigation">
        <button 
          className="nav-button prev-button"
          onClick={handlePrevious}
          disabled={questionIndex === 0}
        >
          ← Previous
        </button>
        
        <div className="nav-center">
          {question.category && (
            <span className="question-category">{question.category}</span>
          )}
        </div>
        
        <button 
          className={`nav-button next-button ${isValid ? 'enabled' : 'disabled'}`}
          onClick={handleNext}
          disabled={isRequired && !isValid}
        >
          {questionIndex === totalQuestions - 1 ? 'Complete' : 'Next'} →
        </button>
      </div>

      {/* Question insights */}
      {questionContext !== 'general' && (
        <div className="question-insights">
          <h4>💡 What makes a great response:</h4>
          <div className="insights-grid">
            {questionContext === 'business_success_vision' && (
              <>
                <div className="insight-item">
                  <span className="insight-icon">👥</span>
                  <span className="insight-text">Team size and structure</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">📅</span>
                  <span className="insight-text">Daily operations and routine</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">💰</span>
                  <span className="insight-text">Financial metrics and goals</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">🌍</span>
                  <span className="insight-text">Market impact and reach</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">⚖️</span>
                  <span className="insight-text">Work-life balance</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">🌱</span>
                  <span className="insight-text">Social and environmental impact</span>
                </div>
              </>
            )}
            
            {questionContext === 'passion_discovery' && (
              <>
                <div className="insight-item">
                  <span className="insight-icon">❤️</span>
                  <span className="insight-text">Personal interests and hobbies</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">⚡</span>
                  <span className="insight-text">Activities that energize you</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">🎯</span>
                  <span className="insight-text">Meaningful and fulfilling work</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">🧭</span>
                  <span className="insight-text">Alignment with personal values</span>
                </div>
              </>
            )}
            
            {questionContext === 'market_opportunity' && (
              <>
                <div className="insight-item">
                  <span className="insight-icon">🎯</span>
                  <span className="insight-text">Target customer segments</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">📊</span>
                  <span className="insight-text">Market size and growth</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">🏆</span>
                  <span className="insight-text">Competitive landscape</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">💎</span>
                  <span className="insight-text">Unique value proposition</span>
                </div>
              </>
            )}
            
            {questionContext === 'skills_assessment' && (
              <>
                <div className="insight-item">
                  <span className="insight-icon">💼</span>
                  <span className="insight-text">Professional experience</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">🎓</span>
                  <span className="insight-text">Educational background</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">🛠️</span>
                  <span className="insight-text">Technical and soft skills</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">🏅</span>
                  <span className="insight-text">Achievements and results</span>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedQuestionComponent;

