import React, { useState, useEffect } from 'react';
import { CheckCircle, Circle, AlertCircle, Info } from 'lucide-react';
import './ConstrainedSelectionQuestion.css';

const ConstrainedSelectionQuestion = ({ 
  question, 
  mainOptions, 
  subOptions, 
  onSelectionChange,
  value = { main: null, sub: [] }
}) => {
  const [selectedMain, setSelectedMain] = useState(value.main);
  const [selectedSub, setSelectedSub] = useState(value.sub || []);
  const [showValidation, setShowValidation] = useState(false);

  useEffect(() => {
    // Notify parent component of changes
    onSelectionChange({
      main: selectedMain,
      sub: selectedSub
    });
  }, [selectedMain, selectedSub, onSelectionChange]);

  const handleMainSelection = (optionId) => {
    if (selectedMain === optionId) {
      // Deselect if clicking the same option
      setSelectedMain(null);
    } else {
      // Select new main reason
      setSelectedMain(optionId);
    }
    setShowValidation(false);
  };

  const handleSubSelection = (optionId) => {
    if (selectedSub.includes(optionId)) {
      // Remove if already selected
      setSelectedSub(prev => prev.filter(id => id !== optionId));
    } else if (selectedSub.length < 2) {
      // Add if under limit
      setSelectedSub(prev => [...prev, optionId]);
    } else {
      // Show validation message if trying to select more than 2
      setShowValidation(true);
      setTimeout(() => setShowValidation(false), 3000);
    }
  };

  const getMainSelectionStatus = () => {
    if (!selectedMain) return 'none';
    return 'selected';
  };

  const getSubSelectionStatus = () => {
    const count = selectedSub.length;
    if (count === 0) return 'none';
    if (count === 1) return 'partial';
    return 'complete';
  };

  const renderSelectionCounter = (current, max, label) => {
    return (
      <div className={`selection-counter ${current === max ? 'complete' : current > 0 ? 'partial' : 'empty'}`}>
        <div className="counter-circle">
          <span className="counter-text">{current}/{max}</span>
        </div>
        <span className="counter-label">{label}</span>
      </div>
    );
  };

  return (
    <div className="constrained-selection-question">
      <div className="question-header">
        <h3 className="question-title">{question}</h3>
        
        <div className="selection-guidance">
          <div className="guidance-info">
            <Info className="info-icon" />
            <span>Select 1 main reason and up to 2 supporting reasons</span>
          </div>
          
          <div className="selection-counters">
            {renderSelectionCounter(selectedMain ? 1 : 0, 1, 'Main Reason')}
            {renderSelectionCounter(selectedSub.length, 2, 'Sub-Reasons')}
          </div>
        </div>

        {showValidation && (
          <div className="validation-message">
            <AlertCircle className="alert-icon" />
            <span>You can only select up to 2 sub-reasons. Please deselect one first.</span>
          </div>
        )}
      </div>

      <div className="selection-sections">
        {/* Main Reason Section */}
        <div className="selection-section main-section">
          <div className="section-header">
            <h4 className="section-title">
              <span className="section-number">1</span>
              Main Reason
            </h4>
            <div className="section-status">
              <div className={`status-indicator ${getMainSelectionStatus()}`}>
                {selectedMain ? (
                  <CheckCircle className="status-icon selected" />
                ) : (
                  <Circle className="status-icon empty" />
                )}
              </div>
              <span className="status-text">
                {selectedMain ? 'Selected' : 'Select 1 option'}
              </span>
            </div>
          </div>

          <div className="options-grid main-options">
            {mainOptions.map((option) => (
              <div
                key={option.id}
                className={`option-card main-option ${selectedMain === option.id ? 'selected' : ''}`}
                onClick={() => handleMainSelection(option.id)}
              >
                <div className="option-selector">
                  {selectedMain === option.id ? (
                    <CheckCircle className="selector-icon selected" />
                  ) : (
                    <Circle className="selector-icon" />
                  )}
                </div>
                
                <div className="option-content">
                  <div className="option-icon">
                    {option.icon}
                  </div>
                  <h5 className="option-title">{option.title}</h5>
                  <p className="option-description">{option.description}</p>
                </div>

                {selectedMain === option.id && (
                  <div className="selection-badge main-badge">
                    <span>Main Reason</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Sub-Reasons Section */}
        <div className="selection-section sub-section">
          <div className="section-header">
            <h4 className="section-title">
              <span className="section-number">2</span>
              Supporting Reasons
            </h4>
            <div className="section-status">
              <div className={`status-indicator ${getSubSelectionStatus()}`}>
                {selectedSub.length === 2 ? (
                  <CheckCircle className="status-icon selected" />
                ) : selectedSub.length === 1 ? (
                  <Circle className="status-icon partial" />
                ) : (
                  <Circle className="status-icon empty" />
                )}
              </div>
              <span className="status-text">
                {selectedSub.length === 0 && 'Select up to 2 options'}
                {selectedSub.length === 1 && 'Select 1 more (optional)'}
                {selectedSub.length === 2 && 'Maximum selected'}
              </span>
            </div>
          </div>

          <div className="options-grid sub-options">
            {subOptions.map((option) => {
              const isSelected = selectedSub.includes(option.id);
              const isDisabled = !isSelected && selectedSub.length >= 2;
              
              return (
                <div
                  key={option.id}
                  className={`option-card sub-option ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}`}
                  onClick={() => !isDisabled && handleSubSelection(option.id)}
                >
                  <div className="option-selector">
                    {isSelected ? (
                      <CheckCircle className="selector-icon selected" />
                    ) : (
                      <Circle className={`selector-icon ${isDisabled ? 'disabled' : ''}`} />
                    )}
                  </div>
                  
                  <div className="option-content">
                    <div className="option-icon">
                      {option.icon}
                    </div>
                    <h5 className="option-title">{option.title}</h5>
                    <p className="option-description">{option.description}</p>
                  </div>

                  {isSelected && (
                    <div className="selection-badge sub-badge">
                      <span>Supporting #{selectedSub.indexOf(option.id) + 1}</span>
                    </div>
                  )}

                  {isDisabled && (
                    <div className="disabled-overlay">
                      <span>Limit reached</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Selection Summary */}
      {(selectedMain || selectedSub.length > 0) && (
        <div className="selection-summary">
          <h4 className="summary-title">Your Selection Summary</h4>
          
          {selectedMain && (
            <div className="summary-item main-summary">
              <div className="summary-badge main">Main</div>
              <span className="summary-text">
                {mainOptions.find(opt => opt.id === selectedMain)?.title}
              </span>
            </div>
          )}

          {selectedSub.map((subId, index) => (
            <div key={subId} className="summary-item sub-summary">
              <div className="summary-badge sub">Sub #{index + 1}</div>
              <span className="summary-text">
                {subOptions.find(opt => opt.id === subId)?.title}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Example usage component
const ExampleConstrainedQuestion = () => {
  const [selection, setSelection] = useState({ main: null, sub: [] });

  const mainOptions = [
    {
      id: 'financial-freedom',
      title: 'Financial Freedom',
      description: 'Build wealth and achieve financial independence',
      icon: '💰'
    },
    {
      id: 'make-impact',
      title: 'Make a Positive Impact',
      description: 'Create meaningful change in the world',
      icon: '🌍'
    },
    {
      id: 'be-own-boss',
      title: 'Be My Own Boss',
      description: 'Have control over my work and decisions',
      icon: '👑'
    },
    {
      id: 'solve-problems',
      title: 'Solve Important Problems',
      description: 'Address challenges that matter to people',
      icon: '🔧'
    }
  ];

  const subOptions = [
    {
      id: 'flexible-schedule',
      title: 'Flexible Schedule',
      description: 'Work when and how I want',
      icon: '⏰'
    },
    {
      id: 'creative-expression',
      title: 'Creative Expression',
      description: 'Express my creativity and ideas',
      icon: '🎨'
    },
    {
      id: 'help-others',
      title: 'Help Others',
      description: 'Make a difference in people\'s lives',
      icon: '🤝'
    },
    {
      id: 'build-legacy',
      title: 'Build a Legacy',
      description: 'Create something that lasts beyond me',
      icon: '🏛️'
    },
    {
      id: 'learn-grow',
      title: 'Learn and Grow',
      description: 'Continuously develop new skills',
      icon: '📚'
    },
    {
      id: 'work-passion',
      title: 'Work on My Passion',
      description: 'Turn what I love into my career',
      icon: '❤️'
    }
  ];

  return (
    <ConstrainedSelectionQuestion
      question="What is your primary motivation for starting a business?"
      mainOptions={mainOptions}
      subOptions={subOptions}
      onSelectionChange={setSelection}
      value={selection}
    />
  );
};

export default ConstrainedSelectionQuestion;
export { ExampleConstrainedQuestion };

