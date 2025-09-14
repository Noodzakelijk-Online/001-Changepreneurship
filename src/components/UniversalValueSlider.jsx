import React, { useState, useEffect, useRef } from 'react';
import { Info, TrendingUp, Target, Zap } from 'lucide-react';
import './UniversalValueSlider.css';

const UniversalValueSlider = ({
  label,
  description,
  value = 50,
  onChange,
  min = 1,
  max = 100,
  step = 1,
  showMarkers = true,
  showPercentage = true,
  color = '#ff6b35',
  icon = null,
  helpText = null,
  disabled = false,
  size = 'medium', // 'small', 'medium', 'large'
  orientation = 'horizontal', // 'horizontal', 'vertical'
  showValueInput = true,
  customMarkers = null,
  onFocus = null,
  onBlur = null
}) => {
  const [currentValue, setCurrentValue] = useState(value);
  const [isDragging, setIsDragging] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const sliderRef = useRef(null);
  const thumbRef = useRef(null);

  useEffect(() => {
    setCurrentValue(value);
  }, [value]);

  const handleValueChange = (newValue) => {
    const clampedValue = Math.max(min, Math.min(max, newValue));
    setCurrentValue(clampedValue);
    onChange && onChange(clampedValue);
  };

  const handleSliderChange = (e) => {
    const newValue = parseInt(e.target.value);
    handleValueChange(newValue);
  };

  const handleInputChange = (e) => {
    const newValue = parseInt(e.target.value) || min;
    handleValueChange(newValue);
  };

  const handleMouseDown = () => {
    setIsDragging(true);
    setShowTooltip(true);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setShowTooltip(false);
  };

  const handleFocus = (e) => {
    setShowTooltip(true);
    onFocus && onFocus(e);
  };

  const handleBlur = (e) => {
    setShowTooltip(false);
    onBlur && onBlur(e);
  };

  const getValueLabel = (val) => {
    if (customMarkers) {
      const marker = customMarkers.find(m => m.value === val);
      return marker ? marker.label : val.toString();
    }
    
    // Default value interpretations
    if (val <= 10) return 'Very Low';
    if (val <= 25) return 'Low';
    if (val <= 40) return 'Below Average';
    if (val <= 60) return 'Average';
    if (val <= 75) return 'Above Average';
    if (val <= 90) return 'High';
    return 'Very High';
  };

  const getValueColor = (val) => {
    // Create gradient from red to green based on value
    const percentage = (val - min) / (max - min);
    if (percentage <= 0.2) return '#ef4444'; // Red
    if (percentage <= 0.4) return '#f59e0b'; // Orange
    if (percentage <= 0.6) return '#eab308'; // Yellow
    if (percentage <= 0.8) return '#22c55e'; // Light Green
    return '#16a34a'; // Green
  };

  const renderMarkers = () => {
    if (!showMarkers) return null;

    const markers = customMarkers || [
      { value: 1, label: '1' },
      { value: 25, label: '25' },
      { value: 50, label: '50' },
      { value: 75, label: '75' },
      { value: 100, label: '100' }
    ];

    return (
      <div className="slider-markers">
        {markers.map((marker) => (
          <div
            key={marker.value}
            className="marker"
            style={{
              left: `${((marker.value - min) / (max - min)) * 100}%`
            }}
          >
            <div className="marker-tick"></div>
            <div className="marker-label">{marker.label}</div>
          </div>
        ))}
      </div>
    );
  };

  const renderValueInput = () => {
    if (!showValueInput) return null;

    return (
      <div className="value-input-container">
        <input
          type="number"
          min={min}
          max={max}
          step={step}
          value={currentValue}
          onChange={handleInputChange}
          disabled={disabled}
          className="value-input"
        />
        {showPercentage && <span className="percentage-symbol">%</span>}
      </div>
    );
  };

  const renderTooltip = () => {
    if (!showTooltip) return null;

    return (
      <div
        className="slider-tooltip"
        style={{
          left: `${((currentValue - min) / (max - min)) * 100}%`,
          backgroundColor: color
        }}
      >
        <div className="tooltip-content">
          <span className="tooltip-value">{currentValue}</span>
          <span className="tooltip-label">{getValueLabel(currentValue)}</span>
        </div>
        <div className="tooltip-arrow"></div>
      </div>
    );
  };

  return (
    <div className={`universal-value-slider ${size} ${orientation} ${disabled ? 'disabled' : ''}`}>
      <div className="slider-header">
        <div className="slider-label-container">
          {icon && <div className="slider-icon">{icon}</div>}
          <div className="slider-text">
            <label className="slider-label">{label}</label>
            {description && <p className="slider-description">{description}</p>}
          </div>
        </div>
        
        <div className="slider-value-display">
          <div className="current-value">
            <span className="value-number" style={{ color: getValueColor(currentValue) }}>
              {currentValue}
            </span>
            {showPercentage && <span className="value-unit">%</span>}
          </div>
          <div className="value-interpretation">
            {getValueLabel(currentValue)}
          </div>
        </div>
      </div>

      <div className="slider-container">
        <div className="slider-track-container" ref={sliderRef}>
          <div className="slider-track">
            <div
              className="slider-fill"
              style={{
                width: `${((currentValue - min) / (max - min)) * 100}%`,
                backgroundColor: color
              }}
            ></div>
          </div>
          
          <input
            type="range"
            min={min}
            max={max}
            step={step}
            value={currentValue}
            onChange={handleSliderChange}
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            onFocus={handleFocus}
            onBlur={handleBlur}
            disabled={disabled}
            className="slider-input"
            style={{
              '--slider-color': color,
              '--slider-thumb-color': getValueColor(currentValue)
            }}
            ref={thumbRef}
          />
          
          {renderTooltip()}
        </div>
        
        {renderMarkers()}
      </div>

      <div className="slider-footer">
        {showValueInput && renderValueInput()}
        
        {helpText && (
          <div className="slider-help">
            <Info className="help-icon" />
            <span className="help-text">{helpText}</span>
          </div>
        )}
      </div>
    </div>
  );
};

// Specialized slider variants for common use cases
const ConfidenceSlider = ({ label, value, onChange, ...props }) => (
  <UniversalValueSlider
    label={label}
    value={value}
    onChange={onChange}
    color="#3b82f6"
    icon={<Target className="w-4 h-4" />}
    helpText="Rate your confidence level from 1 (not confident) to 100 (extremely confident)"
    customMarkers={[
      { value: 1, label: 'Not Confident' },
      { value: 25, label: 'Slightly' },
      { value: 50, label: 'Moderate' },
      { value: 75, label: 'Confident' },
      { value: 100, label: 'Extremely' }
    ]}
    {...props}
  />
);

const ImportanceSlider = ({ label, value, onChange, ...props }) => (
  <UniversalValueSlider
    label={label}
    value={value}
    onChange={onChange}
    color="#10b981"
    icon={<TrendingUp className="w-4 h-4" />}
    helpText="Rate importance from 1 (not important) to 100 (extremely important)"
    customMarkers={[
      { value: 1, label: 'Not Important' },
      { value: 25, label: 'Slightly' },
      { value: 50, label: 'Moderate' },
      { value: 75, label: 'Important' },
      { value: 100, label: 'Critical' }
    ]}
    {...props}
  />
);

const SkillLevelSlider = ({ label, value, onChange, ...props }) => (
  <UniversalValueSlider
    label={label}
    value={value}
    onChange={onChange}
    color="#8b5cf6"
    icon={<Zap className="w-4 h-4" />}
    helpText="Rate your skill level from 1 (beginner) to 100 (expert)"
    customMarkers={[
      { value: 1, label: 'Beginner' },
      { value: 25, label: 'Novice' },
      { value: 50, label: 'Intermediate' },
      { value: 75, label: 'Advanced' },
      { value: 100, label: 'Expert' }
    ]}
    {...props}
  />
);

const AgreementSlider = ({ label, value, onChange, ...props }) => (
  <UniversalValueSlider
    label={label}
    value={value}
    onChange={onChange}
    color="#f59e0b"
    helpText="Rate your agreement from 1 (strongly disagree) to 100 (strongly agree)"
    customMarkers={[
      { value: 1, label: 'Strongly Disagree' },
      { value: 25, label: 'Disagree' },
      { value: 50, label: 'Neutral' },
      { value: 75, label: 'Agree' },
      { value: 100, label: 'Strongly Agree' }
    ]}
    {...props}
  />
);

// Example usage component
const SliderExamples = () => {
  const [values, setValues] = useState({
    confidence: 75,
    importance: 60,
    skill: 45,
    agreement: 80,
    custom: 50
  });

  const handleValueChange = (key) => (value) => {
    setValues(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="slider-examples">
      <h2>Universal Value Slider Examples</h2>
      
      <div className="examples-grid">
        <ConfidenceSlider
          label="How confident are you in your business idea?"
          value={values.confidence}
          onChange={handleValueChange('confidence')}
        />
        
        <ImportanceSlider
          label="How important is financial success to you?"
          value={values.importance}
          onChange={handleValueChange('importance')}
        />
        
        <SkillLevelSlider
          label="Rate your marketing skills"
          value={values.skill}
          onChange={handleValueChange('skill')}
        />
        
        <AgreementSlider
          label="I prefer working in teams over working alone"
          value={values.agreement}
          onChange={handleValueChange('agreement')}
        />
        
        <UniversalValueSlider
          label="Custom Slider Example"
          description="This is a custom slider with unique styling"
          value={values.custom}
          onChange={handleValueChange('custom')}
          color="#ef4444"
          size="large"
          helpText="This slider demonstrates custom configuration options"
        />
      </div>
      
      <div className="values-display">
        <h3>Current Values:</h3>
        <pre>{JSON.stringify(values, null, 2)}</pre>
      </div>
    </div>
  );
};

export default UniversalValueSlider;
export { 
  ConfidenceSlider, 
  ImportanceSlider, 
  SkillLevelSlider, 
  AgreementSlider,
  SliderExamples 
};

