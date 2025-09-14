import React, { useState, useEffect } from 'react';
import { Info, Target, TrendingUp, Zap, Users, DollarSign, Clock, Star } from 'lucide-react';
import './ContextualValueSlider.css';

const ContextualValueSlider = ({
  question,
  description,
  value = 50,
  onChange,
  contextType = 'skill', // 'skill', 'frequency', 'agreement', 'importance', 'confidence', 'experience'
  domain = 'general', // 'marketing', 'sales', 'leadership', 'technical', 'financial', etc.
  goalContext = null, // What this relates to entrepreneurially
  examples = null, // Custom examples for scale points
  color = '#ff6b35',
  disabled = false,
  size = 'medium'
}) => {
  const [currentValue, setCurrentValue] = useState(value);
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    setCurrentValue(value);
  }, [value]);

  const handleValueChange = (newValue) => {
    const clampedValue = Math.max(1, Math.min(100, newValue));
    setCurrentValue(clampedValue);
    onChange && onChange(clampedValue);
  };

  // Define contextual scales based on type and domain
  const getContextualScale = () => {
    if (examples) return examples;

    const scales = {
      skill: {
        marketing: {
          1: { label: "Never Done", description: "I've never created marketing content or campaigns" },
          25: { label: "Basic Attempts", description: "I've tried social media posts or simple ads with mixed results" },
          50: { label: "Some Success", description: "I can create content that gets engagement and some leads" },
          75: { label: "Consistent Results", description: "I regularly generate leads and sales through marketing" },
          100: { label: "Expert Level", description: "I can build and scale marketing systems that drive predictable growth" }
        },
        sales: {
          1: { label: "Avoid Selling", description: "I'm uncomfortable with sales conversations and avoid them" },
          25: { label: "Basic Pitches", description: "I can explain my product but struggle to close deals" },
          50: { label: "Some Closes", description: "I close deals occasionally but it feels inconsistent" },
          75: { label: "Reliable Closer", description: "I consistently close qualified prospects and handle objections well" },
          100: { label: "Sales Master", description: "I can sell to anyone and build scalable sales processes" }
        },
        leadership: {
          1: { label: "Prefer Following", description: "I'm most comfortable being told what to do" },
          25: { label: "Occasional Lead", description: "I sometimes take charge in small group situations" },
          50: { label: "Team Contributor", description: "I can lead projects and motivate small teams effectively" },
          75: { label: "Strong Leader", description: "People naturally follow me and I inspire high performance" },
          100: { label: "Visionary Leader", description: "I can build and lead organizations toward ambitious goals" }
        },
        technical: {
          1: { label: "Non-Technical", description: "I avoid technology and need help with basic digital tasks" },
          25: { label: "Basic User", description: "I can use common software but struggle with new tools" },
          50: { label: "Tech Comfortable", description: "I learn new tools quickly and can troubleshoot problems" },
          75: { label: "Tech Savvy", description: "I can implement complex systems and help others with technology" },
          100: { label: "Tech Expert", description: "I can build, customize, and optimize any technology solution" }
        },
        financial: {
          1: { label: "Money Anxious", description: "I avoid financial decisions and don't track money well" },
          25: { label: "Basic Budgeting", description: "I can manage personal finances but struggle with business finance" },
          50: { label: "Financial Aware", description: "I understand key metrics and can read financial statements" },
          75: { label: "Financial Strategist", description: "I can plan budgets, manage cash flow, and make investment decisions" },
          100: { label: "Financial Expert", description: "I can structure complex deals and optimize financial performance" }
        }
      },
      frequency: {
        general: {
          1: { label: "Never", description: "I have never done this" },
          25: { label: "Rarely", description: "I do this a few times per year" },
          50: { label: "Sometimes", description: "I do this monthly or when needed" },
          75: { label: "Often", description: "I do this weekly or multiple times per month" },
          100: { label: "Daily", description: "This is part of my regular routine" }
        }
      },
      experience: {
        general: {
          1: { label: "Complete Beginner", description: "I have no experience with this" },
          25: { label: "Some Exposure", description: "I've been exposed to this but have limited experience" },
          50: { label: "Moderate Experience", description: "I have several years of experience and understand the basics well" },
          75: { label: "Extensive Experience", description: "I have many years of experience and can handle complex situations" },
          100: { label: "Expert Level", description: "I'm recognized as an expert with decades of experience" }
        }
      },
      agreement: {
        general: {
          1: { label: "Strongly Disagree", description: "This completely goes against my beliefs/preferences" },
          25: { label: "Mostly Disagree", description: "I disagree with this in most situations" },
          50: { label: "Neutral/Depends", description: "I'm neutral or it depends on the situation" },
          75: { label: "Mostly Agree", description: "I agree with this in most situations" },
          100: { label: "Strongly Agree", description: "This perfectly aligns with my beliefs/preferences" }
        }
      },
      importance: {
        general: {
          1: { label: "Not Important", description: "This has no impact on my entrepreneurial success" },
          25: { label: "Slightly Important", description: "This might have some minor impact" },
          50: { label: "Moderately Important", description: "This is important but not critical to success" },
          75: { label: "Very Important", description: "This is crucial for entrepreneurial success" },
          100: { label: "Mission Critical", description: "My success absolutely depends on this" }
        }
      },
      confidence: {
        general: {
          1: { label: "No Confidence", description: "I have serious doubts about this" },
          25: { label: "Low Confidence", description: "I'm uncertain and worried about this" },
          50: { label: "Moderate Confidence", description: "I'm somewhat confident but have some concerns" },
          75: { label: "High Confidence", description: "I'm confident this will work out well" },
          100: { label: "Complete Confidence", description: "I'm absolutely certain about this" }
        }
      }
    };

    return scales[contextType]?.[domain] || scales[contextType]?.general || scales.skill.general;
  };

  const getScalePoint = (val) => {
    const scale = getContextualScale();
    
    // Find the closest scale point
    const points = [1, 25, 50, 75, 100];
    const closest = points.reduce((prev, curr) => 
      Math.abs(curr - val) < Math.abs(prev - val) ? curr : prev
    );
    
    return scale[closest] || { label: val.toString(), description: "" };
  };

  const getContextIcon = () => {
    const icons = {
      skill: <Zap className="w-4 h-4" />,
      frequency: <Clock className="w-4 h-4" />,
      experience: <Star className="w-4 h-4" />,
      agreement: <Target className="w-4 h-4" />,
      importance: <TrendingUp className="w-4 h-4" />,
      confidence: <Target className="w-4 h-4" />
    };
    return icons[contextType] || <Info className="w-4 h-4" />;
  };

  const renderScaleReference = () => {
    const scale = getContextualScale();
    const points = [1, 25, 50, 75, 100];
    
    return (
      <div className="scale-reference">
        <h4 className="scale-reference-title">Reference Scale:</h4>
        <div className="scale-points">
          {points.map(point => (
            <div 
              key={point} 
              className={`scale-point ${currentValue >= point - 12 && currentValue <= point + 12 ? 'active' : ''}`}
            >
              <div className="scale-point-value">{point}</div>
              <div className="scale-point-label">{scale[point]?.label}</div>
              <div className="scale-point-description">{scale[point]?.description}</div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderGoalContext = () => {
    if (!goalContext) return null;
    
    return (
      <div className="goal-context">
        <div className="goal-context-header">
          <Target className="w-4 h-4" />
          <span>Why This Matters for Your Success:</span>
        </div>
        <p className="goal-context-text">{goalContext}</p>
      </div>
    );
  };

  const currentPoint = getScalePoint(currentValue);

  return (
    <div className={`contextual-value-slider ${size} ${disabled ? 'disabled' : ''}`}>
      <div className="slider-header">
        <div className="question-section">
          <div className="question-header">
            {getContextIcon()}
            <h3 className="question-text">{question}</h3>
          </div>
          {description && (
            <p className="question-description">{description}</p>
          )}
        </div>
        
        <div className="current-assessment">
          <div className="current-value" style={{ color }}>
            <span className="value-number">{currentValue}</span>
            <span className="value-label">{currentPoint.label}</span>
          </div>
        </div>
      </div>

      {renderGoalContext()}

      <div className="slider-container">
        <div className="slider-track-wrapper">
          <div className="slider-track">
            <div 
              className="slider-fill" 
              style={{ 
                width: `${currentValue}%`,
                backgroundColor: color 
              }}
            />
          </div>
          
          <input
            type="range"
            min="1"
            max="100"
            step="1"
            value={currentValue}
            onChange={(e) => handleValueChange(parseInt(e.target.value))}
            onFocus={() => setShowTooltip(true)}
            onBlur={() => setShowTooltip(false)}
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            disabled={disabled}
            className="slider-input"
            style={{ '--slider-color': color }}
          />
          
          {showTooltip && (
            <div 
              className="slider-tooltip"
              style={{ 
                left: `${currentValue}%`,
                backgroundColor: color 
              }}
            >
              <div className="tooltip-content">
                <div className="tooltip-value">{currentValue}</div>
                <div className="tooltip-label">{currentPoint.label}</div>
              </div>
            </div>
          )}
        </div>

        <div className="scale-markers">
          {[1, 25, 50, 75, 100].map(point => (
            <div 
              key={point}
              className="scale-marker"
              style={{ left: `${point}%` }}
              onClick={() => handleValueChange(point)}
            >
              <div className="marker-line" />
              <div className="marker-value">{point}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="current-interpretation">
        <div className="interpretation-content">
          <h4 className="interpretation-title">Your Selection:</h4>
          <p className="interpretation-description">{currentPoint.description}</p>
        </div>
      </div>

      {renderScaleReference()}
    </div>
  );
};

// Specialized contextual sliders for common use cases
const SkillAssessmentSlider = ({ question, domain, value, onChange, goalContext, ...props }) => (
  <ContextualValueSlider
    question={question}
    contextType="skill"
    domain={domain}
    value={value}
    onChange={onChange}
    goalContext={goalContext}
    color="#8b5cf6"
    {...props}
  />
);

const FrequencySlider = ({ question, value, onChange, goalContext, ...props }) => (
  <ContextualValueSlider
    question={question}
    contextType="frequency"
    value={value}
    onChange={onChange}
    goalContext={goalContext}
    color="#10b981"
    {...props}
  />
);

const ExperienceSlider = ({ question, value, onChange, goalContext, ...props }) => (
  <ContextualValueSlider
    question={question}
    contextType="experience"
    value={value}
    onChange={onChange}
    goalContext={goalContext}
    color="#f59e0b"
    {...props}
  />
);

const AgreementSlider = ({ question, value, onChange, goalContext, ...props }) => (
  <ContextualValueSlider
    question={question}
    contextType="agreement"
    value={value}
    onChange={onChange}
    goalContext={goalContext}
    color="#3b82f6"
    {...props}
  />
);

const ImportanceSlider = ({ question, value, onChange, goalContext, ...props }) => (
  <ContextualValueSlider
    question={question}
    contextType="importance"
    value={value}
    onChange={onChange}
    goalContext={goalContext}
    color="#ef4444"
    {...props}
  />
);

const ConfidenceSlider = ({ question, value, onChange, goalContext, ...props }) => (
  <ContextualValueSlider
    question={question}
    contextType="confidence"
    value={value}
    onChange={onChange}
    goalContext={goalContext}
    color="#06b6d4"
    {...props}
  />
);

// Example usage component
const ContextualSliderExamples = () => {
  const [values, setValues] = useState({
    marketing: 45,
    sales: 30,
    leadership: 65,
    networking: 70,
    importance: 85,
    confidence: 55
  });

  const handleValueChange = (key) => (value) => {
    setValues(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="contextual-slider-examples">
      <h2>Contextual Assessment Examples</h2>
      
      <div className="examples-container">
        <SkillAssessmentSlider
          question="How would you rate your marketing abilities?"
          domain="marketing"
          value={values.marketing}
          onChange={handleValueChange('marketing')}
          goalContext="Strong marketing skills are essential for customer acquisition and business growth. Most successful entrepreneurs either excel at marketing or partner with someone who does."
        />
        
        <SkillAssessmentSlider
          question="How comfortable are you with sales conversations?"
          domain="sales"
          value={values.sales}
          onChange={handleValueChange('sales')}
          goalContext="Sales skills directly impact your ability to generate revenue. Even if you hire salespeople later, understanding sales is crucial for business success."
        />
        
        <SkillAssessmentSlider
          question="How would you describe your leadership capabilities?"
          domain="leadership"
          value={values.leadership}
          onChange={handleValueChange('leadership')}
          goalContext="Leadership skills become increasingly important as your business grows. You'll need to inspire and guide team members toward your vision."
        />
        
        <FrequencySlider
          question="How often do you actively network with other professionals?"
          value={values.networking}
          onChange={handleValueChange('networking')}
          goalContext="Regular networking builds relationships that can lead to partnerships, customers, investors, and valuable advice for your business."
        />
        
        <ImportanceSlider
          question="How important is achieving financial independence to you?"
          value={values.importance}
          onChange={handleValueChange('importance')}
          goalContext="Your motivation level for financial success will influence how much risk you're willing to take and how hard you'll work during difficult periods."
        />
        
        <ConfidenceSlider
          question="How confident are you that your business idea will succeed?"
          value={values.confidence}
          onChange={handleValueChange('confidence')}
          goalContext="Confidence in your idea affects your ability to persist through challenges, attract investors, and convince customers to buy from you."
        />
      </div>
      
      <div className="values-summary">
        <h3>Assessment Summary:</h3>
        <div className="summary-grid">
          {Object.entries(values).map(([key, value]) => (
            <div key={key} className="summary-item">
              <span className="summary-label">{key}:</span>
              <span className="summary-value">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ContextualValueSlider;
export { 
  SkillAssessmentSlider,
  FrequencySlider,
  ExperienceSlider,
  AgreementSlider,
  ImportanceSlider,
  ConfidenceSlider,
  ContextualSliderExamples
};

