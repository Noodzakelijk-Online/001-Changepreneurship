import React, { useState, useEffect, useRef, useCallback } from 'react';
import './GmailStyleWritingAssistant.css';

const GmailStyleWritingAssistant = ({ 
  questionId, 
  questionContext, 
  onTextChange, 
  initialText = '',
  placeholder = "Start typing your response...",
  disabled = false,
  className = ''
}) => {
  const [text, setText] = useState(initialText);
  const [inlineSuggestion, setInlineSuggestion] = useState('');
  const [topicSuggestions, setTopicSuggestions] = useState([]);
  const [audit, setAudit] = useState(null);
  const [showTopicSuggestions, setShowTopicSuggestions] = useState(false);
  const [typingTimer, setTypingTimer] = useState(null);
  const [topicTimer, setTopicTimer] = useState(null);
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  
  const textareaRef = useRef(null);
  const overlayRef = useRef(null);
  const containerRef = useRef(null);

  // Auto-resize textarea
  const adjustTextareaHeight = useCallback(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
      
      // Sync overlay height
      if (overlayRef.current) {
        overlayRef.current.style.height = textareaRef.current.style.height;
      }
    }
  }, []);

  // Handle text changes
  const handleTextChange = (e) => {
    const newText = e.target.value;
    setText(newText);
    
    // Clear existing timers
    if (typingTimer) clearTimeout(typingTimer);
    if (topicTimer) clearTimeout(topicTimer);
    
    // Clear suggestions when typing
    setInlineSuggestion('');
    setTopicSuggestions([]);
    setShowTopicSuggestions(false);
    
    // Notify parent component
    if (onTextChange) onTextChange(newText);
    
    // Start suggestion timers
    startSuggestionTimers(newText);
    
    // Auto-resize
    setTimeout(adjustTextareaHeight, 0);
  };

  // Start suggestion timers
  const startSuggestionTimers = useCallback((currentText) => {
    // 5-second inline suggestion timer
    const inlineTimer = setTimeout(() => {
      if (currentText.trim() && !currentText.endsWith('.') && !currentText.endsWith('!') && !currentText.endsWith('?')) {
        fetchInlineSuggestion(currentText);
      }
    }, 5000);
    
    // 15-second topic suggestion timer
    const topicTimerRef = setTimeout(() => {
      if (currentText.trim()) {
        fetchTopicSuggestions(currentText);
      }
    }, 15000);
    
    setTypingTimer(inlineTimer);
    setTopicTimer(topicTimerRef);
  }, []);

  // Fetch inline suggestion (Gmail-style)
  const fetchInlineSuggestion = async (currentText) => {
    try {
      const response = await fetch('/api/writing-assistance/auto-complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: currentText,
          questionContext: questionContext,
          sessionId: sessionId
        })
      });
      
      const data = await response.json();
      if (data.suggestion && data.suggestion.confidence > 0.3) {
        setInlineSuggestion(data.suggestion.content);
      }
    } catch (error) {
      console.error('Error fetching inline suggestion:', error);
    }
  };

  // Fetch topic suggestions
  const fetchTopicSuggestions = async (currentText) => {
    try {
      const response = await fetch('/api/writing-assistance/sentence-suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: currentText,
          questionContext: questionContext,
          sessionId: sessionId
        })
      });
      
      const data = await response.json();
      if (data.suggestions && data.suggestions.length > 0) {
        setTopicSuggestions(data.suggestions.filter(s => s.confidence > 0.4));
        setShowTopicSuggestions(true);
      }
    } catch (error) {
      console.error('Error fetching topic suggestions:', error);
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

  // Accept inline suggestion (Tab key)
  const acceptInlineSuggestion = () => {
    if (inlineSuggestion) {
      const newText = text + inlineSuggestion;
      setText(newText);
      setInlineSuggestion('');
      
      if (onTextChange) onTextChange(newText);
      
      // Focus back to textarea
      if (textareaRef.current) {
        textareaRef.current.focus();
        textareaRef.current.setSelectionRange(newText.length, newText.length);
      }
      
      setTimeout(adjustTextareaHeight, 0);
    }
  };

  // Accept topic suggestion
  const acceptTopicSuggestion = (suggestion) => {
    const newText = text + (text.endsWith('.') || text.endsWith('!') || text.endsWith('?') ? ' ' : '. ') + suggestion.content;
    setText(newText);
    
    // Remove accepted suggestion from list
    setTopicSuggestions(prev => prev.filter(s => s !== suggestion));
    
    if (onTextChange) onTextChange(newText);
    
    // Focus back to textarea
    if (textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.setSelectionRange(newText.length, newText.length);
    }
    
    setTimeout(adjustTextareaHeight, 0);
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e) => {
    // Tab to accept inline suggestion
    if (e.key === 'Tab' && inlineSuggestion) {
      e.preventDefault();
      acceptInlineSuggestion();
    }
    
    // Escape to dismiss all suggestions
    if (e.key === 'Escape') {
      e.preventDefault();
      setInlineSuggestion('');
      setTopicSuggestions([]);
      setShowTopicSuggestions(false);
    }
  };

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      if (typingTimer) clearTimeout(typingTimer);
      if (topicTimer) clearTimeout(topicTimer);
    };
  }, [typingTimer, topicTimer]);

  // Sync scroll between textarea and overlay
  const handleScroll = () => {
    if (textareaRef.current && overlayRef.current) {
      overlayRef.current.scrollTop = textareaRef.current.scrollTop;
      overlayRef.current.scrollLeft = textareaRef.current.scrollLeft;
    }
  };

  return (
    <div className={`gmail-writing-assistant ${className}`} ref={containerRef}>
      <div className="writing-container">
        {/* Overlay for inline suggestions */}
        <div 
          ref={overlayRef}
          className="suggestion-overlay"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            pointerEvents: 'none',
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            overflow: 'hidden',
            padding: textareaRef.current?.style.padding || '1rem',
            border: '2px solid transparent',
            fontSize: '16px',
            lineHeight: '1.6',
            fontFamily: 'inherit',
            color: 'transparent'
          }}
        >
          {text}
          {inlineSuggestion && (
            <span className="inline-suggestion">
              {inlineSuggestion}
            </span>
          )}
        </div>

        {/* Main textarea */}
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleTextChange}
          onKeyDown={handleKeyDown}
          onScroll={handleScroll}
          placeholder={placeholder}
          disabled={disabled}
          className="writing-textarea"
          rows={4}
          style={{
            position: 'relative',
            background: 'transparent',
            zIndex: 1
          }}
        />
      </div>

      {/* Topic suggestions panel */}
      {showTopicSuggestions && topicSuggestions.length > 0 && (
        <div className="topic-suggestions-panel">
          <div className="suggestions-header">
            <h4>💡 Consider adding these topics:</h4>
            <button 
              className="dismiss-btn"
              onClick={() => setShowTopicSuggestions(false)}
              title="Press Escape to dismiss"
            >
              ✕
            </button>
          </div>
          <div className="suggestions-list">
            {topicSuggestions.map((suggestion, index) => (
              <div key={index} className="topic-suggestion-item">
                <div className="suggestion-content">
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
                      className="add-btn"
                      onClick={() => acceptTopicSuggestion(suggestion)}
                    >
                      Add to response
                    </button>
                    <span className="suggestion-reasoning">{suggestion.reasoning}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
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
                <span className="score-label">Complete</span>
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
          <span className="tip-text">Press <kbd>Tab</kbd> to accept gray suggestions</span>
        </div>
        <div className="tip-item">
          <span className="tip-icon">⏱️</span>
          <span className="tip-text">Pause 5s for inline suggestions, 15s for topic ideas</span>
        </div>
        <div className="tip-item">
          <span className="tip-icon">📝</span>
          <span className="tip-text">Double line break triggers quality analysis</span>
        </div>
      </div>
    </div>
  );
};

export default GmailStyleWritingAssistant;

