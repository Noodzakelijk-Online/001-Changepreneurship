import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft, FileText, Lightbulb, Target, DollarSign, TrendingUp, Users, Award, CheckCircle, AlertCircle, Sparkles } from 'lucide-react';
import './ExecutiveSummaryGenerator.css';

const ExecutiveSummaryGenerator = ({ onDataChange, initialData = {} }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [responses, setResponses] = useState(initialData);
  const [generatedContent, setGeneratedContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [completedSections, setCompletedSections] = useState(new Set());

  const questionSections = [
    {
      id: 'problem_solution',
      title: 'Problem & Solution',
      icon: <Lightbulb className="w-5 h-5" />,
      description: 'Define the core problem and your innovative solution',
      questions: [
        {
          id: 'core_problem',
          question: 'What is the main problem your business solves?',
          placeholder: 'Describe the specific challenge your target customers face...',
          type: 'textarea',
          required: true,
          hint: 'Think about daily frustrations, unmet needs, or inefficiencies your customers experience.'
        },
        {
          id: 'solution_description',
          question: 'How does your solution address this problem?',
          placeholder: 'Explain how your product/service solves the problem...',
          type: 'textarea',
          required: true,
          hint: 'Focus on the unique approach and benefits your solution provides.'
        },
        {
          id: 'solution_uniqueness',
          question: 'What makes your solution different from existing alternatives?',
          placeholder: 'Describe your unique approach or innovation...',
          type: 'textarea',
          required: true,
          hint: 'Highlight what sets you apart from competitors or current solutions.'
        }
      ]
    },
    {
      id: 'mission_vision',
      title: 'Mission & Vision',
      icon: <Target className="w-5 h-5" />,
      description: 'Articulate your company\'s purpose and future aspirations',
      questions: [
        {
          id: 'mission_statement',
          question: 'What is your company\'s mission?',
          placeholder: 'Our mission is to...',
          type: 'textarea',
          required: true,
          hint: 'Describe your company\'s purpose and what you aim to achieve for customers.'
        },
        {
          id: 'vision_statement',
          question: 'What is your long-term vision?',
          placeholder: 'We envision a future where...',
          type: 'textarea',
          required: true,
          hint: 'Paint a picture of the positive change you want to create in the world.'
        },
        {
          id: 'core_values',
          question: 'What are your company\'s core values?',
          placeholder: 'Our core values include...',
          type: 'textarea',
          required: true,
          hint: 'List 3-5 fundamental principles that guide your business decisions.'
        }
      ]
    },
    {
      id: 'products_services',
      title: 'Products & Services',
      icon: <Award className="w-5 h-5" />,
      description: 'Outline your key offerings and their benefits',
      questions: [
        {
          id: 'primary_offerings',
          question: 'What are your main products or services?',
          placeholder: 'We offer...',
          type: 'textarea',
          required: true,
          hint: 'Describe your core offerings in simple, customer-friendly terms.'
        },
        {
          id: 'key_features',
          question: 'What are the key features and benefits?',
          placeholder: 'Key features include...',
          type: 'textarea',
          required: true,
          hint: 'Focus on features that directly benefit your customers.'
        },
        {
          id: 'development_stage',
          question: 'What is the current development stage?',
          placeholder: 'Select current stage',
          type: 'select',
          options: [
            'Idea/Concept',
            'Prototype Development',
            'Beta Testing',
            'Market Ready',
            'Launched',
            'Scaling'
          ],
          required: true
        }
      ]
    },
    {
      id: 'market_opportunity',
      title: 'Market & Customers',
      icon: <Users className="w-5 h-5" />,
      description: 'Define your target market and opportunity size',
      questions: [
        {
          id: 'target_market',
          question: 'Who is your primary target market?',
          placeholder: 'Our target customers are...',
          type: 'textarea',
          required: true,
          hint: 'Describe your ideal customers in terms of demographics, needs, and behaviors.'
        },
        {
          id: 'market_size',
          question: 'How large is your target market?',
          placeholder: 'The market size is approximately...',
          type: 'textarea',
          required: true,
          hint: 'Provide estimates of total addressable market (TAM) and your potential share.'
        },
        {
          id: 'competitive_advantage',
          question: 'What are your main competitive advantages?',
          placeholder: 'Our competitive advantages include...',
          type: 'textarea',
          required: true,
          hint: 'Explain what gives you an edge over competitors or alternatives.'
        }
      ]
    },
    {
      id: 'business_model',
      title: 'Business Model',
      icon: <DollarSign className="w-5 h-5" />,
      description: 'Explain how your business generates revenue',
      questions: [
        {
          id: 'revenue_model',
          question: 'How does your business make money?',
          placeholder: 'We generate revenue through...',
          type: 'textarea',
          required: true,
          hint: 'Describe your pricing strategy and revenue streams.'
        },
        {
          id: 'business_location',
          question: 'Where will your business be located?',
          placeholder: 'Our business will be located...',
          type: 'text',
          required: true,
          hint: 'Include physical location and/or online presence.'
        },
        {
          id: 'legal_structure',
          question: 'What is your business legal structure?',
          placeholder: 'Select legal structure',
          type: 'select',
          options: [
            'Sole Proprietorship',
            'Partnership',
            'LLC',
            'Corporation',
            'S-Corporation',
            'Not Yet Decided'
          ],
          required: true
        }
      ]
    },
    {
      id: 'team_management',
      title: 'Team & Management',
      icon: <Users className="w-5 h-5" />,
      description: 'Introduce your key team members and their roles',
      questions: [
        {
          id: 'key_team_members',
          question: 'Who are your key team members?',
          placeholder: 'Our team includes...',
          type: 'textarea',
          required: true,
          hint: 'List founders and key team members with their roles and relevant experience.'
        },
        {
          id: 'team_experience',
          question: 'What relevant experience does your team bring?',
          placeholder: 'Our team has experience in...',
          type: 'textarea',
          required: true,
          hint: 'Highlight industry experience, skills, and achievements that support your venture.'
        },
        {
          id: 'advisory_support',
          question: 'Do you have advisors or mentors?',
          placeholder: 'We are supported by...',
          type: 'textarea',
          required: false,
          hint: 'Mention any advisors, mentors, or board members who provide guidance.'
        }
      ]
    },
    {
      id: 'financial_highlights',
      title: 'Financial Overview',
      icon: <TrendingUp className="w-5 h-5" />,
      description: 'Present key financial projections and requirements',
      questions: [
        {
          id: 'revenue_projections',
          question: 'What are your revenue projections for the next 3 years?',
          placeholder: 'Year 1: $X, Year 2: $Y, Year 3: $Z',
          type: 'textarea',
          required: true,
          hint: 'Provide realistic revenue estimates based on market research and business model.'
        },
        {
          id: 'funding_requirements',
          question: 'How much funding do you need?',
          placeholder: 'We are seeking $X in funding...',
          type: 'textarea',
          required: false,
          hint: 'Specify the amount needed and general use of funds if seeking investment.'
        },
        {
          id: 'break_even_timeline',
          question: 'When do you expect to break even?',
          placeholder: 'We expect to break even by...',
          type: 'text',
          required: true,
          hint: 'Estimate when your revenue will cover all expenses.'
        }
      ]
    },
    {
      id: 'growth_strategy',
      title: 'Growth & Future',
      icon: <TrendingUp className="w-5 h-5" />,
      description: 'Outline your growth plans and future milestones',
      questions: [
        {
          id: 'growth_strategy',
          question: 'What is your growth strategy?',
          placeholder: 'Our growth strategy includes...',
          type: 'textarea',
          required: true,
          hint: 'Describe how you plan to scale your business and expand your market reach.'
        },
        {
          id: 'key_milestones',
          question: 'What are your key milestones for the next year?',
          placeholder: 'Key milestones include...',
          type: 'textarea',
          required: true,
          hint: 'List specific, measurable goals you plan to achieve in the next 12 months.'
        },
        {
          id: 'success_metrics',
          question: 'How will you measure success?',
          placeholder: 'We will measure success by...',
          type: 'textarea',
          required: true,
          hint: 'Define key performance indicators (KPIs) that will track your progress.'
        }
      ]
    }
  ];

  const currentSection = questionSections[currentStep];
  const totalQuestions = questionSections.reduce((sum, section) => sum + section.questions.length, 0);
  const answeredQuestions = Object.keys(responses).length;
  const progressPercentage = (answeredQuestions / totalQuestions) * 100;

  useEffect(() => {
    if (onDataChange) {
      onDataChange(responses);
    }
  }, [responses, onDataChange]);

  const handleInputChange = (questionId, value) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const isSectionComplete = (section) => {
    const requiredQuestions = section.questions.filter(q => q.required);
    return requiredQuestions.every(q => responses[q.id] && responses[q.id].trim() !== '');
  };

  const canProceedToNext = () => {
    return isSectionComplete(currentSection);
  };

  const handleNext = () => {
    if (canProceedToNext() && currentStep < questionSections.length - 1) {
      setCompletedSections(prev => new Set([...prev, currentSection.id]));
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const generateExecutiveSummary = async () => {
    setIsGenerating(true);
    
    // Simulate AI content generation
    setTimeout(() => {
      const content = `
# Executive Summary

## Problem & Solution
${responses.core_problem || 'Problem statement to be defined.'}

Our innovative solution addresses this challenge by ${responses.solution_description || 'providing a unique approach'}. What sets us apart is ${responses.solution_uniqueness || 'our distinctive methodology'}.

## Mission & Vision
**Mission:** ${responses.mission_statement || 'To be defined.'}

**Vision:** ${responses.vision_statement || 'To be defined.'}

**Core Values:** ${responses.core_values || 'To be defined.'}

## Products & Services
We offer ${responses.primary_offerings || 'innovative products and services'} with key features including ${responses.key_features || 'advanced capabilities'}. Our offerings are currently in the ${responses.development_stage || 'development'} stage.

## Market Opportunity
Our target market consists of ${responses.target_market || 'specific customer segments'}. The market opportunity is significant, with ${responses.market_size || 'substantial growth potential'}. Our competitive advantages include ${responses.competitive_advantage || 'unique positioning'}.

## Business Model
We generate revenue through ${responses.revenue_model || 'multiple revenue streams'}. Our business is structured as a ${responses.legal_structure || 'legal entity'} and will be located ${responses.business_location || 'strategically'}.

## Team & Management
Our team includes ${responses.key_team_members || 'experienced professionals'} with relevant experience in ${responses.team_experience || 'key areas'}. ${responses.advisory_support ? `We are supported by ${responses.advisory_support}.` : ''}

## Financial Projections
Revenue projections: ${responses.revenue_projections || 'To be determined based on market analysis.'}
${responses.funding_requirements ? `Funding Requirements: ${responses.funding_requirements}` : ''}
Break-even Timeline: ${responses.break_even_timeline || 'To be determined.'}

## Growth Strategy
Our growth strategy focuses on ${responses.growth_strategy || 'strategic expansion'}. Key milestones for the next year include ${responses.key_milestones || 'specific targets'}. Success will be measured by ${responses.success_metrics || 'key performance indicators'}.

## Conclusion
This executive summary outlines a compelling business opportunity with strong market potential, a capable team, and a clear path to profitability. We are well-positioned to capture market share and deliver value to customers, investors, and stakeholders.
      `;
      
      setGeneratedContent(content);
      setIsGenerating(false);
    }, 2000);
  };

  const renderQuestion = (question) => {
    const value = responses[question.id] || '';
    
    return (
      <div key={question.id} className="question-container">
        <label className="question-label">
          {question.question}
          {question.required && <span className="required-asterisk">*</span>}
        </label>
        
        {question.hint && (
          <p className="question-hint">{question.hint}</p>
        )}
        
        {question.type === 'textarea' ? (
          <textarea
            value={value}
            onChange={(e) => handleInputChange(question.id, e.target.value)}
            placeholder={question.placeholder}
            className="question-textarea"
            rows={4}
          />
        ) : question.type === 'select' ? (
          <select
            value={value}
            onChange={(e) => handleInputChange(question.id, e.target.value)}
            className="question-select"
          >
            <option value="">{question.placeholder}</option>
            {question.options.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        ) : (
          <input
            type="text"
            value={value}
            onChange={(e) => handleInputChange(question.id, e.target.value)}
            placeholder={question.placeholder}
            className="question-input"
          />
        )}
      </div>
    );
  };

  return (
    <div className="executive-summary-generator">
      <div className="generator-header">
        <div className="header-content">
          <FileText className="w-8 h-8 text-orange-500" />
          <div>
            <h1 className="generator-title">Executive Summary Generator</h1>
            <p className="generator-subtitle">
              Create a compelling executive summary that captures the essence of your business
            </p>
          </div>
        </div>
        
        <div className="progress-section">
          <div className="progress-stats">
            <span className="progress-text">
              {answeredQuestions} of {totalQuestions} questions completed
            </span>
            <span className="progress-percentage">{Math.round(progressPercentage)}%</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </div>

      <div className="generator-content">
        <div className="section-navigation">
          {questionSections.map((section, index) => (
            <button
              key={section.id}
              onClick={() => setCurrentStep(index)}
              className={`nav-item ${currentStep === index ? 'active' : ''} ${
                completedSections.has(section.id) ? 'completed' : ''
              }`}
            >
              <div className="nav-icon">
                {completedSections.has(section.id) ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  section.icon
                )}
              </div>
              <div className="nav-content">
                <div className="nav-title">{section.title}</div>
                <div className="nav-description">{section.description}</div>
              </div>
            </button>
          ))}
        </div>

        <div className="question-section">
          <div className="section-header">
            <div className="section-icon">
              {currentSection.icon}
            </div>
            <div>
              <h2 className="section-title">{currentSection.title}</h2>
              <p className="section-description">{currentSection.description}</p>
            </div>
          </div>

          <div className="questions-container">
            {currentSection.questions.map(renderQuestion)}
          </div>

          <div className="navigation-buttons">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 0}
              className="nav-button secondary"
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </button>

            {currentStep === questionSections.length - 1 ? (
              <button
                onClick={generateExecutiveSummary}
                disabled={!canProceedToNext() || isGenerating}
                className="nav-button primary"
              >
                {isGenerating ? (
                  <>
                    <div className="spinner" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Summary
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={handleNext}
                disabled={!canProceedToNext()}
                className="nav-button primary"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </button>
            )}
          </div>

          {!canProceedToNext() && (
            <div className="completion-warning">
              <AlertCircle className="w-4 h-4" />
              Please complete all required fields to continue
            </div>
          )}
        </div>
      </div>

      {generatedContent && (
        <div className="generated-content">
          <div className="content-header">
            <h3 className="content-title">Generated Executive Summary</h3>
            <p className="content-subtitle">
              Review and edit your AI-generated executive summary
            </p>
          </div>
          
          <div className="content-preview">
            <pre className="content-text">{generatedContent}</pre>
          </div>
          
          <div className="content-actions">
            <button className="action-button secondary">
              Edit Content
            </button>
            <button className="action-button primary">
              Export to Business Plan
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExecutiveSummaryGenerator;

