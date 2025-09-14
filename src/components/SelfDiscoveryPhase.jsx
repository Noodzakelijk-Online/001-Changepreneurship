import React, { useState, useEffect } from 'react';
import MaslowAssessment from './MaslowAssessment';
import ComprehensiveIkigaiSystem from './ComprehensiveIkigaiSystem';
import GmailStyleWritingAssistant from './GmailStyleWritingAssistant';
import './SelfDiscoveryPhase.css';

const SelfDiscoveryPhase = ({ 
  onPhaseComplete,
  onProgressUpdate,
  initialResponses = {}
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [responses, setResponses] = useState(initialResponses);
  const [maslowLevel, setMaslowLevel] = useState(null);
  const [ikigaiScores, setIkigaiScores] = useState({});
  const [phaseProgress, setPhaseProgress] = useState(0);
  const [contextualQuestions, setContextualQuestions] = useState([]);

  // Base self-discovery questions that adapt based on Maslow level
  const baseQuestions = [
    {
      id: 'current_situation',
      question: 'Describe your current life situation in detail.',
      category: 'foundation',
      required: true,
      maslowAdaptation: {
        physiological: 'Focus on your basic living situation, income, and daily survival needs.',
        safety: 'Describe your financial security, job stability, and sense of safety.',
        belonging: 'Tell us about your relationships, community connections, and social support.',
        esteem: 'Share your achievements, recognition, and how others perceive you.',
        cognitive: 'Describe your learning journey, intellectual pursuits, and curiosity.',
        aesthetic: 'Tell us about your creative expressions and appreciation for beauty.',
        selfActualization: 'Share how you\'re growing personally and fulfilling your potential.',
        transcendence: 'Describe how you\'re helping others and contributing to something greater.'
      }
    },
    {
      id: 'motivations',
      question: 'What truly motivates you in life?',
      category: 'motivation',
      required: true,
      maslowAdaptation: {
        physiological: 'What drives you to meet your basic needs and survive?',
        safety: 'What motivates you to seek security and stability?',
        belonging: 'What drives your need for connection and relationships?',
        esteem: 'What motivates you to achieve and gain recognition?',
        cognitive: 'What drives your curiosity and desire to learn?',
        aesthetic: 'What motivates your creative and aesthetic pursuits?',
        selfActualization: 'What drives your personal growth and self-fulfillment?',
        transcendence: 'What motivates you to serve others and create lasting impact?'
      }
    },
    {
      id: 'challenges',
      question: 'What are your biggest challenges right now?',
      category: 'challenges',
      required: true,
      maslowAdaptation: {
        physiological: 'What basic needs are you struggling to meet?',
        safety: 'What security concerns keep you up at night?',
        belonging: 'What relationship or social challenges are you facing?',
        esteem: 'What recognition or achievement challenges frustrate you?',
        cognitive: 'What learning or understanding challenges do you face?',
        aesthetic: 'What creative or aesthetic challenges limit your expression?',
        selfActualization: 'What personal growth challenges are holding you back?',
        transcendence: 'What prevents you from making the impact you desire?'
      }
    },
    {
      id: 'values',
      question: 'What are your core values and beliefs?',
      category: 'values',
      required: true,
      maslowAdaptation: {
        physiological: 'What values guide your survival and basic living decisions?',
        safety: 'What values are most important for your security and stability?',
        belonging: 'What values guide your relationships and social connections?',
        esteem: 'What values drive your pursuit of achievement and recognition?',
        cognitive: 'What values guide your learning and intellectual pursuits?',
        aesthetic: 'What values influence your creative and aesthetic choices?',
        selfActualization: 'What values guide your personal growth and authenticity?',
        transcendence: 'What values drive your service to others and higher purpose?'
      }
    },
    {
      id: 'future_vision',
      question: 'How do you envision your ideal future?',
      category: 'vision',
      required: true,
      maslowAdaptation: {
        physiological: 'What would basic security and comfort look like for you?',
        safety: 'What would true financial and personal security mean to you?',
        belonging: 'What would your ideal relationships and community look like?',
        esteem: 'What achievements and recognition would fulfill you?',
        cognitive: 'What knowledge and understanding do you hope to gain?',
        aesthetic: 'What creative and beautiful experiences do you want to create?',
        selfActualization: 'What would it mean to fully realize your potential?',
        transcendence: 'What legacy and impact do you want to leave behind?'
      }
    },
    {
      id: 'entrepreneurial_interest',
      question: 'Why are you interested in entrepreneurship?',
      category: 'entrepreneurship',
      required: true,
      maslowAdaptation: {
        physiological: 'How could entrepreneurship help you meet your basic needs?',
        safety: 'How could entrepreneurship provide you with security and stability?',
        belonging: 'How could entrepreneurship help you build community and connections?',
        esteem: 'How could entrepreneurship bring you achievement and recognition?',
        cognitive: 'How could entrepreneurship satisfy your curiosity and learning desires?',
        aesthetic: 'How could entrepreneurship allow for creative and aesthetic expression?',
        selfActualization: 'How could entrepreneurship help you fulfill your potential?',
        transcendence: 'How could entrepreneurship help you serve others and create impact?'
      }
    }
  ];

  useEffect(() => {
    updateContextualQuestions();
    calculateProgress();
  }, [maslowLevel, responses]);

  const updateContextualQuestions = () => {
    if (!maslowLevel) {
      setContextualQuestions(baseQuestions);
      return;
    }

    const adaptedQuestions = baseQuestions.map(q => ({
      ...q,
      question: q.maslowAdaptation[maslowLevel.id] || q.question,
      context: `Based on your ${maslowLevel.name} focus`,
      guidance: getQuestionGuidance(q.category, maslowLevel)
    }));

    // Add level-specific follow-up questions
    const followUpQuestions = getFollowUpQuestions(maslowLevel);
    
    setContextualQuestions([...adaptedQuestions, ...followUpQuestions]);
  };

  const getQuestionGuidance = (category, level) => {
    const guidance = {
      physiological: {
        foundation: 'Focus on your basic living conditions, health, and daily survival needs.',
        motivation: 'Consider what drives you to secure food, shelter, and basic comfort.',
        challenges: 'Think about immediate survival challenges and resource limitations.',
        values: 'Reflect on values that help you prioritize basic needs and survival.',
        vision: 'Envision a future where your basic needs are consistently met.',
        entrepreneurship: 'Consider how business could provide stable income and resources.'
      },
      safety: {
        foundation: 'Describe your financial situation, job security, and sense of stability.',
        motivation: 'Think about what drives your need for security and predictability.',
        challenges: 'Consider financial stress, job insecurity, or safety concerns.',
        values: 'Reflect on values like security, stability, and risk management.',
        vision: 'Imagine a future with financial security and stable circumstances.',
        entrepreneurship: 'Consider how business could provide long-term security and stability.'
      },
      belonging: {
        foundation: 'Share about your relationships, social connections, and sense of belonging.',
        motivation: 'Consider what drives your need for love, friendship, and community.',
        challenges: 'Think about loneliness, relationship issues, or social isolation.',
        values: 'Reflect on values like love, friendship, loyalty, and community.',
        vision: 'Envision meaningful relationships and strong community connections.',
        entrepreneurship: 'Consider how business could build community and meaningful connections.'
      },
      esteem: {
        foundation: 'Describe your achievements, recognition, and self-confidence.',
        motivation: 'Think about what drives your need for respect and accomplishment.',
        challenges: 'Consider self-doubt, lack of recognition, or achievement struggles.',
        values: 'Reflect on values like excellence, achievement, and recognition.',
        vision: 'Imagine being respected and recognized for your contributions.',
        entrepreneurship: 'Consider how business could bring achievement and professional respect.'
      },
      cognitive: {
        foundation: 'Share your learning journey, intellectual curiosity, and knowledge pursuits.',
        motivation: 'Consider what drives your desire to understand and learn.',
        challenges: 'Think about learning obstacles or intellectual frustrations.',
        values: 'Reflect on values like knowledge, understanding, and intellectual growth.',
        vision: 'Envision continuous learning and intellectual fulfillment.',
        entrepreneurship: 'Consider how business could provide intellectual challenges and growth.'
      },
      aesthetic: {
        foundation: 'Describe your creative expressions and appreciation for beauty.',
        motivation: 'Think about what drives your need for beauty and creative expression.',
        challenges: 'Consider creative blocks or lack of aesthetic fulfillment.',
        values: 'Reflect on values like beauty, creativity, and artistic expression.',
        vision: 'Imagine a life filled with beauty and creative fulfillment.',
        entrepreneurship: 'Consider how business could allow for creative and aesthetic expression.'
      },
      selfActualization: {
        foundation: 'Share how you\'re growing personally and pursuing your potential.',
        motivation: 'Consider what drives your need for personal growth and authenticity.',
        challenges: 'Think about barriers to personal growth or authentic living.',
        values: 'Reflect on values like authenticity, growth, and self-realization.',
        vision: 'Envision fully realizing your unique potential and living authentically.',
        entrepreneurship: 'Consider how business could be an expression of your authentic self.'
      },
      transcendence: {
        foundation: 'Describe how you\'re serving others and contributing to something greater.',
        motivation: 'Think about what drives your desire to help others and create impact.',
        challenges: 'Consider obstacles to making the impact you desire.',
        values: 'Reflect on values like service, legacy, and contribution to humanity.',
        vision: 'Envision the lasting positive impact you want to make on the world.',
        entrepreneurship: 'Consider how business could serve others and create meaningful change.'
      }
    };

    return guidance[level.id]?.[category] || 'Provide detailed, honest responses to help us understand you better.';
  };

  const getFollowUpQuestions = (level) => {
    const followUps = {
      physiological: [
        {
          id: 'basic_needs_stability',
          question: 'How stable is your access to basic necessities like food, housing, and healthcare?',
          category: 'foundation',
          required: false,
          guidance: 'Be honest about your current situation - this helps us recommend appropriate entrepreneurial paths.'
        }
      ],
      safety: [
        {
          id: 'financial_security',
          question: 'What would financial security look like for you specifically?',
          category: 'vision',
          required: false,
          guidance: 'Think about specific numbers, timeframes, and security measures that would make you feel safe.'
        }
      ],
      belonging: [
        {
          id: 'community_building',
          question: 'How important is building community through your work?',
          category: 'entrepreneurship',
          required: false,
          guidance: 'Consider whether you want your business to create connections and bring people together.'
        }
      ],
      esteem: [
        {
          id: 'recognition_goals',
          question: 'What kind of recognition or achievement would be most meaningful to you?',
          category: 'motivation',
          required: false,
          guidance: 'Think about specific achievements, awards, or recognition that would truly fulfill you.'
        }
      ],
      cognitive: [
        {
          id: 'learning_entrepreneurship',
          question: 'What aspects of entrepreneurship are you most curious to learn about?',
          category: 'entrepreneurship',
          required: false,
          guidance: 'Consider which business skills, strategies, or knowledge areas excite your curiosity.'
        }
      ],
      aesthetic: [
        {
          id: 'creative_business',
          question: 'How could your business be a form of creative expression?',
          category: 'entrepreneurship',
          required: false,
          guidance: 'Think about how your business could reflect your aesthetic values and creative vision.'
        }
      ],
      selfActualization: [
        {
          id: 'authentic_business',
          question: 'How would your ideal business reflect your authentic self?',
          category: 'entrepreneurship',
          required: false,
          guidance: 'Consider how your business could be a true expression of who you are at your core.'
        }
      ],
      transcendence: [
        {
          id: 'legacy_impact',
          question: 'What legacy do you want your entrepreneurial work to leave behind?',
          category: 'vision',
          required: false,
          guidance: 'Think about the long-term impact and how you want to be remembered for your contributions.'
        }
      ]
    };

    return followUps[level.id] || [];
  };

  const calculateProgress = () => {
    const totalQuestions = contextualQuestions.length;
    const answeredQuestions = Object.keys(responses).length;
    const progress = totalQuestions > 0 ? (answeredQuestions / totalQuestions) * 100 : 0;
    
    setPhaseProgress(progress);
    
    if (onProgressUpdate) {
      onProgressUpdate({
        phase: 'self-discovery',
        progress: progress,
        maslowLevel: maslowLevel,
        ikigaiScores: ikigaiScores,
        responses: responses
      });
    }
  };

  const handleMaslowLevelDetermined = (levelData) => {
    setMaslowLevel(levelData.currentLevel);
  };

  const handleResponseUpdate = (questionId, response) => {
    const updatedResponses = {
      ...responses,
      [questionId]: response
    };
    setResponses(updatedResponses);
  };

  const handleIkigaiScoreUpdate = (scores) => {
    setIkigaiScores(scores);
  };

  const handleNextStep = () => {
    if (currentStep < contextualQuestions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else if (phaseProgress >= 80) {
      // Phase is complete enough
      if (onPhaseComplete) {
        onPhaseComplete({
          responses: responses,
          maslowLevel: maslowLevel,
          ikigaiScores: ikigaiScores,
          progress: phaseProgress
        });
      }
    }
  };

  const handlePreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const getCurrentQuestion = () => {
    return contextualQuestions[currentStep];
  };

  const isStepComplete = (stepIndex) => {
    const question = contextualQuestions[stepIndex];
    return question && responses[question.id] && responses[question.id].length > 50;
  };

  return (
    <div className="self-discovery-phase">
      <div className="phase-header">
        <h1>🧭 Self-Discovery Phase</h1>
        <p>Understanding yourself through the lens of human needs and entrepreneurial potential</p>
        
        <div className="progress-indicator">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${phaseProgress}%` }}
            ></div>
          </div>
          <span className="progress-text">{Math.round(phaseProgress)}% Complete</span>
        </div>
      </div>

      {/* Maslow Assessment */}
      <div className="assessment-section">
        <MaslowAssessment
          responses={responses}
          onLevelDetermined={handleMaslowLevelDetermined}
          onScoreUpdate={() => {}}
        />
      </div>

      {/* Contextual Questions */}
      {contextualQuestions.length > 0 && (
        <div className="questions-section">
          <div className="question-navigation">
            <div className="question-steps">
              {contextualQuestions.map((_, index) => (
                <div 
                  key={index}
                  className={`step ${index === currentStep ? 'active' : ''} ${isStepComplete(index) ? 'complete' : ''}`}
                  onClick={() => setCurrentStep(index)}
                >
                  {index + 1}
                </div>
              ))}
            </div>
          </div>

          {getCurrentQuestion() && (
            <div className="current-question">
              <div className="question-header">
                <h3>{getCurrentQuestion().question}</h3>
                {getCurrentQuestion().context && (
                  <p className="question-context">{getCurrentQuestion().context}</p>
                )}
                {getCurrentQuestion().guidance && (
                  <div className="question-guidance">
                    <span className="guidance-icon">💡</span>
                    <p>{getCurrentQuestion().guidance}</p>
                  </div>
                )}
              </div>

              <div className="question-input">
                <GmailStyleWritingAssistant
                  questionId={getCurrentQuestion().id}
                  question={getCurrentQuestion().question}
                  context={maslowLevel ? `${maslowLevel.name} focus` : 'General'}
                  initialValue={responses[getCurrentQuestion().id] || ''}
                  onResponseUpdate={(response) => handleResponseUpdate(getCurrentQuestion().id, response)}
                  placeholder="Share your thoughts in detail..."
                />
              </div>

              <div className="question-navigation-buttons">
                <button 
                  onClick={handlePreviousStep}
                  disabled={currentStep === 0}
                  className="nav-button previous"
                >
                  ← Previous
                </button>
                
                <button 
                  onClick={handleNextStep}
                  className="nav-button next"
                  disabled={!responses[getCurrentQuestion().id] || responses[getCurrentQuestion().id].length < 20}
                >
                  {currentStep === contextualQuestions.length - 1 ? 'Complete Phase' : 'Next →'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Ikigai Assessment */}
      {Object.keys(responses).length >= 3 && (
        <div className="ikigai-section">
          <ComprehensiveIkigaiSystem
            responses={responses}
            onScoreUpdate={handleIkigaiScoreUpdate}
            onStateChange={() => {}}
          />
        </div>
      )}

      {/* Phase Summary */}
      {phaseProgress >= 80 && (
        <div className="phase-summary">
          <h3>🎉 Self-Discovery Phase Summary</h3>
          <div className="summary-grid">
            <div className="summary-card maslow">
              <h4>Your Maslow Level</h4>
              {maslowLevel && (
                <div className="maslow-summary">
                  <span className="level-icon">{maslowLevel.icon}</span>
                  <div>
                    <p className="level-name">{maslowLevel.name}</p>
                    <p className="level-context">{maslowLevel.entrepreneurialContext}</p>
                  </div>
                </div>
              )}
            </div>
            
            <div className="summary-card ikigai">
              <h4>Your Ikigai Scores</h4>
              <div className="ikigai-summary">
                <div className="score-item">
                  <span>❤️ Heart:</span>
                  <span>{ikigaiScores.heart || 0}%</span>
                </div>
                <div className="score-item">
                  <span>⚡ Body:</span>
                  <span>{ikigaiScores.body || 0}%</span>
                </div>
                <div className="score-item">
                  <span>🧠 Mind:</span>
                  <span>{ikigaiScores.mind || 0}%</span>
                </div>
                <div className="score-item">
                  <span>⭐ Soul:</span>
                  <span>{ikigaiScores.soul || 0}%</span>
                </div>
              </div>
            </div>
            
            <div className="summary-card responses">
              <h4>Your Responses</h4>
              <p>{Object.keys(responses).length} questions answered</p>
              <p>{Object.values(responses).join(' ').split(' ').length} words shared</p>
              <p>Ready for next phase!</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SelfDiscoveryPhase;

