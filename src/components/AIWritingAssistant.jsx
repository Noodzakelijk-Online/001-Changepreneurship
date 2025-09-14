import React, { useState, useEffect, useRef, useCallback } from 'react';
import './AIWritingAssistant.css';

const AIWritingAssistant = ({ 
  questionId, 
  questionContext, 
  onTextChange, 
  initialText = '',
  placeholder = "Start typing your response...",
  disabled = false 
}) => {
  const [text, setText] = useState(initialText);
  const [inlineSuggestion, setInlineSuggestion] = useState('');
  const [topicSuggestions, setTopicSuggestions] = useState([]);
  const [audit, setAudit] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showTopicSuggestions, setShowTopicSuggestions] = useState(false);
  const [typingTimer, setTypingTimer] = useState(null);
  const [topicTimer, setTopicTimer] = useState(null);
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  
  const textareaRef = useRef(null);
  const overlayRef = useRef(null);
  
  // Auto-resize textarea
  const adjustTextareaHeight = useCallback(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, []);

  // Handle text changes
  const handleTextChange = (e) => {
    const newText = e.target.value;
    setText(newText);
    setLastActivity(Date.now());
    
    // Clear existing timers
    if (typingTimer) clearTimeout(typingTimer);
    if (suggestionTimerRef.current) clearTimeout(suggestionTimerRef.current);
    
    // Reset suggestions
    setSuggestions([]);
    setShowSuggestions(false);
    
    // Notify parent component
    if (onTextChange) onTextChange(newText);
    
    // Start suggestion timers
    startSuggestionTimers();
    
    // Auto-resize
    setTimeout(adjustTextareaHeight, 0);
  };

  // Start suggestion timers
  const startSuggestionTimers = useCallback(() => {
    // 5-second auto-completion timer
    const completionTimer = setTimeout(() => {
      if (text.trim() && !text.endsWith('.') && !text.endsWith('!') && !text.endsWith('?')) {
        fetchAutoCompletion();
      }
    }, 5000);
    
    // 15-second sentence suggestion timer
    const sentenceTimer = setTimeout(() => {
      if (text.trim()) {
        fetchSentenceSuggestions();
      }
    }, 15000);
    
    setTypingTimer(completionTimer);
    suggestionTimerRef.current = sentenceTimer;
  }, [text]);

  // Fetch auto-completion suggestions
  const fetchAutoCompletion = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/writing-assistance/auto-complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          questionContext: questionContext,
          sessionId: sessionId
        })
      });
      
      const data = await response.json();
      if (data.suggestion && data.suggestion.confidence > 0.3) {
        setSuggestions([{
          type: 'completion',
          content: data.suggestion.content,
          confidence: data.suggestion.confidence,
          reasoning: data.suggestion.reasoning
        }]);
        setShowSuggestions(true);
      }
    } catch (error) {
      console.error('Error fetching auto-completion:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch sentence suggestions
  const fetchSentenceSuggestions = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/writing-assistance/sentence-suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          questionContext: questionContext,
          sessionId: sessionId
        })
      });
      
      const data = await response.json();
      if (data.suggestions && data.suggestions.length > 0) {
        setSuggestions(data.suggestions.filter(s => s.confidence > 0.4));
        setShowSuggestions(true);
      }
    } catch (error) {
      console.error('Error fetching sentence suggestions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Audit paragraph
  const auditParagraph = async (paragraphText) => {
    try {
      const response = await fetch('/api/writing-assistance/audit-paragraph', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: paragraphText,
          questionContext: questionContext
        })
      });
      
      const auditData = await response.json();
      setAudit(auditData);
    } catch (error) {
      console.error('Error auditing paragraph:', error);
    }
  };

  // Handle paragraph completion (double line break)
  useEffect(() => {
    const paragraphs = text.split('\n\n');
    const lastParagraph = paragraphs[paragraphs.length - 1];
    
    // If user just completed a paragraph (double line break)
    if (paragraphs.length > 1 && lastParagraph.trim() === '') {
      const completedParagraph = paragraphs[paragraphs.length - 2];
      if (completedParagraph.trim().length > 50) {
        auditParagraph(completedParagraph);
      }
    }
  }, [text]);

  // Accept suggestion
  const acceptSuggestion = (suggestion) => {
    let newText;
    
    if (suggestion.type === 'completion') {
      // Add completion to current text
      newText = text + suggestion.content;
    } else {
      // Add sentence suggestion as new sentence
      newText = text + (text.endsWith('.') || text.endsWith('!') || text.endsWith('?') ? ' ' : '. ') + suggestion.content;
    }
    
    setText(newText);
    setSuggestions([]);
    setShowSuggestions(false);
    
    if (onTextChange) onTextChange(newText);
    
    // Focus back to textarea
    if (textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.setSelectionRange(newText.length, newText.length);
    }
    
    setTimeout(adjustTextareaHeight, 0);
  };

  // Dismiss suggestions
  const dismissSuggestions = () => {
    setSuggestions([]);
    setShowSuggestions(false);
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e) => {
    // Tab to accept first suggestion
    if (e.key === 'Tab' && suggestions.length > 0 && showSuggestions) {
      e.preventDefault();
      acceptSuggestion(suggestions[0]);
    }
    
    // Escape to dismiss suggestions
    if (e.key === 'Escape' && showSuggestions) {
      e.preventDefault();
      dismissSuggestions();
    }
  };

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      if (typingTimer) clearTimeout(typingTimer);
      if (suggestionTimerRef.current) clearTimeout(suggestionTimerRef.current);
    };
  }, []);

  return (
    <div className="ai-writing-assistant">
      <div className="writing-area">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleTextChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className="writing-textarea"
          rows={4}
        />
        
        {/* Auto-completion suggestion */}
        {showSuggestions && suggestions.length > 0 && suggestions[0].type === 'completion' && (
          <div className="suggestion-overlay completion-suggestion">
            <div className="suggestion-content">
              <span className="suggestion-text">{suggestions[0].content}</span>
              <div className="suggestion-actions">
                <button 
                  className="accept-btn"
                  onClick={() => acceptSuggestion(suggestions[0])}
                  title="Press Tab to accept"
                >
                  ✓ Accept
                </button>
                <button 
                  className="dismiss-btn"
                  onClick={dismissSuggestions}
                  title="Press Escape to dismiss"
                >
                  ✕
                </button>
              </div>
            </div>
            <div className="suggestion-confidence">
              Confidence: {Math.round(suggestions[0].confidence * 100)}%
            </div>
          </div>
        )}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="loading-indicator">
            <div className="loading-spinner"></div>
            <span>AI is thinking...</span>
          </div>
        )}
      </div>

      {/* Sentence suggestions panel */}
      {showSuggestions && suggestions.some(s => s.type === 'sentence') && (
        <div className="suggestions-panel">
          <h4>💡 Consider adding:</h4>
          <div className="suggestions-list">
            {suggestions
              .filter(s => s.type === 'sentence')
              .map((suggestion, index) => (
                <div key={index} className="suggestion-item">
                  <div className="suggestion-header">
                    <span className="suggestion-label">
                      {suggestion.micro_subject ? 
                        suggestion.micro_subject.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) : 
                        'Additional insight'
                      }
                    </span>
                    <span className="suggestion-confidence">
                      {Math.round(suggestion.confidence * 100)}%
                    </span>
                  </div>
                  <p className="suggestion-text">{suggestion.content}</p>
                  <div className="suggestion-actions">
                    <button 
                      className="insert-btn"
                      onClick={() => acceptSuggestion(suggestion)}
                    >
                      Insert
                    </button>
                    <span className="suggestion-reasoning">{suggestion.reasoning}</span>
                  </div>
                </div>
              ))}
          </div>
          <button className="dismiss-all-btn" onClick={dismissSuggestions}>
            Dismiss All
          </button>
        </div>
      )}

      {/* Paragraph audit panel */}
      {audit && (
        <div className="audit-panel">
          <div className="audit-header">
            <h4>📊 Response Quality Analysis</h4>
            <div className="audit-scores">
              <div className="score-item">
                <span className="score-label">Overall</span>
                <span className="score-value">{audit.overall_score}%</span>
              </div>
              <div className="score-item">
                <span className="score-label">Completeness</span>
                <span className="score-value">{Math.round(audit.completeness_score * 100)}%</span>
              </div>
              <div className="score-item">
                <span className="score-label">Words</span>
                <span className="score-value">{audit.word_count}</span>
              </div>
            </div>
          </div>

          <div className="audit-content">
            {/* Good elements */}
            {audit.good_elements && audit.good_elements.length > 0 && (
              <div className="audit-section good-elements">
                <h5>✅ Strengths</h5>
                <ul>
                  {audit.good_elements.map((element, index) => (
                    <li key={index}>{element.message}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Improvements */}
            {audit.improvements && audit.improvements.length > 0 && (
              <div className="audit-section improvements">
                <h5>⚠️ Areas for Improvement</h5>
                <ul>
                  {audit.improvements.map((improvement, index) => (
                    <li key={index}>
                      <div className="improvement-message">{improvement.message}</div>
                      {improvement.suggestion && (
                        <div className="improvement-suggestion">💡 {improvement.suggestion}</div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Missing elements */}
            {audit.missing_elements && audit.missing_elements.length > 0 && (
              <div className="audit-section missing-elements">
                <h5>❌ Missing Elements</h5>
                <ul>
                  {audit.missing_elements.map((missing, index) => (
                    <li key={index}>
                      <div className="missing-message">{missing.message}</div>
                      {missing.suggestion && (
                        <div className="missing-suggestion">💡 {missing.suggestion}</div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <button 
            className="close-audit-btn"
            onClick={() => setAudit(null)}
          >
            Close Analysis
          </button>
        </div>
      )}

      {/* Writing tips */}
      <div className="writing-tips">
        <div className="tip-item">
          <span className="tip-icon">⌨️</span>
          <span className="tip-text">Press <kbd>Tab</kbd> to accept suggestions</span>
        </div>
        <div className="tip-item">
          <span className="tip-icon">⏱️</span>
          <span className="tip-text">AI suggestions appear after 5-15 seconds of inactivity</span>
        </div>
        <div className="tip-item">
          <span className="tip-icon">📝</span>
          <span className="tip-text">Double line break triggers paragraph analysis</span>
        </div>
      </div>
    </div>
  );
};

export default AIWritingAssistant;

