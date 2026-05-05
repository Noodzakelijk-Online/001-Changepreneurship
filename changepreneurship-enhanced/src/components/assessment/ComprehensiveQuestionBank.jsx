// Comprehensive Question Bank for Changepreneurship Assessment
// This file contains all question data for the complete 7-part assessment framework

export const SELF_DISCOVERY_QUESTIONS = {
  motivation: {
    id: 'motivation',
    code: 1,
    order: 1,
    title: 'Motivation & Drive',
    questions: [
      {
        id: 'primary-motivation',
        code: 1,
        order: 1,
        question: 'What is the main reason you want to start your own business?',
        type: 'multiple-choice',
        required: true,
        options: [
          { value: 'transform-world', label: 'Create something that changes the world', description: 'Build transformative solutions for the future' },
          { value: 'solve-problems', label: 'Solve real problems I see everywhere', description: 'Fix immediate problems with practical solutions' },
          { value: 'lifestyle-freedom', label: 'Have the lifestyle and freedom I want', description: 'Personal freedom and lifestyle alignment' },
          { value: 'financial-security', label: 'Build financial security for my family', description: 'Stable income and asset building' },
          { value: 'social-impact', label: 'Make a positive difference in the world', description: 'Social or environmental impact' },
          { value: 'seize-opportunities', label: 'Capture market opportunities I see', description: 'Seize opportunities for profit' }
        ]
      },
      {
        id: 'success-vision',
        code: 2,
        order: 2,
        question: 'When you imagine your business being successful, what does that look like?',
        type: 'textarea',
        required: true,
        placeholder: 'Describe your vision of success in detail...',
        helpText: 'Think about team size, daily life, impact, working hours, and what success means to you personally.'
      },
      {
        id: 'risk-tolerance',
        code: 3,
        order: 3,
        question: 'How comfortable are you with taking risks?',
        type: 'scale',
        required: true,
        scaleRange: { min: 1, max: 10 },
        scaleLabels: { min: 'Very Risk-Averse', max: 'High Risk Tolerance' },
        helpText: 'Consider both financial and personal risks involved in starting a business.'
      },
      {
        id: 'entrepreneurial-drive',
        code: 4,
        order: 4,
        question: 'What drives you to consider entrepreneurship over traditional employment?',
        type: 'multiple-choice',
        required: true,
        options: [
          { value: 'autonomy', label: 'Need for autonomy and control', description: 'Want to be my own boss' },
          { value: 'creativity', label: 'Creative expression and innovation', description: 'Build something new and unique' },
          { value: 'impact', label: 'Desire to make a bigger impact', description: 'Create meaningful change' },
          { value: 'financial', label: 'Financial independence and wealth', description: 'Build significant wealth' },
          { value: 'flexibility', label: 'Work-life balance and flexibility', description: 'Control my schedule and location' },
          { value: 'legacy', label: 'Building a lasting legacy', description: 'Create something that outlasts me' }
        ]
      },
      {
        id: 'failure-perspective',
        code: 5,
        order: 5,
        question: 'How do you view the possibility of business failure?',
        type: 'multiple-choice',
        required: true,
        options: [
          { value: 'learning', label: 'Learning opportunity and stepping stone', description: 'Failure teaches valuable lessons' },
          { value: 'acceptable-risk', label: 'Acceptable risk for potential rewards', description: 'Worth the risk for success' },
          { value: 'concerning', label: 'Concerning but manageable', description: 'Worried but can handle it' },
          { value: 'devastating', label: 'Potentially devastating outcome', description: 'Would be very difficult to recover' }
        ]
      }
    ]
  },

  'life-impact': {
    id: 'life-impact',
    code: 2,
    order: 2,
    title: 'Life Impact & Support',
    questions: [
      {
        id: 'life-satisfaction',
        code: 1,
        order: 1,
        question: 'Rate your current satisfaction in different life areas',
        type: 'multiple-scale',
        required: true,
        areas: ['Health', 'Money', 'Family', 'Friends', 'Career', 'Growth', 'Recreation', 'Environment'],
        scaleRange: { min: 1, max: 10 }
      },
      {
        id: 'time-commitment',
        code: 2,
        order: 2,
        question: 'How many hours per week are you willing to dedicate to building your business?',
        type: 'multiple-choice',
        required: true,
        options: [
          { value: '10-20', label: '10-20 hours (side project)', description: 'Part-time while keeping current job' },
          { value: '20-40', label: '20-40 hours (significant commitment)', description: 'Major time investment' },
          { value: '40-60', label: '40-60 hours (full-time focus)', description: 'Primary focus and dedication' },
          { value: '60+', label: '60+ hours (all-in commitment)', description: 'Complete dedication to success' }
        ]
      },
      {
        id: 'family-support',
        code: 3,
        order: 3,
        question: 'How supportive is your family/partner of your entrepreneurial goals?',
        type: 'scale',
        required: true,
        scaleRange: { min: 1, max: 10 },
        scaleLabels: { min: 'Not Supportive', max: 'Very Supportive' },
        helpText: 'Consider emotional, financial, and practical support from those closest to you.'
      },
      {
        id: 'stress-management',
        code: 4,
        order: 4,
        question: 'How do you typically handle high-stress situations?',
        type: 'multiple-choice',
        required: true,
        options: [
          { value: 'thrive', label: 'I thrive under pressure', description: 'Stress motivates and energizes me' },
          { value: 'manage-well', label: 'I manage stress effectively', description: 'Have good coping strategies' },
          { value: 'struggle-sometimes', label: 'I struggle sometimes but cope', description: 'Can be challenging but manageable' },
          { value: 'avoid-stress', label: 'I prefer to avoid stressful situations', description: 'Stress negatively impacts my performance' }
        ]
      },
      {
        id: 'work-life-balance',
        code: 5,
        order: 5,
        question: 'What does ideal work-life balance look like for you?',
        type: 'textarea',
        required: true,
        placeholder: 'Describe your ideal balance between work and personal life...',
        helpText: 'Consider family time, hobbies, health, and personal relationships.'
      }
    ]
  },

  values: {
    id: 'values',
    code: 3,
    order: 3,
    title: 'Values & Ethics',
    questions: [
      {
        id: 'top-values',
        code: 1,
        order: 1,
        question: 'Rank these values in order of importance to you',
        type: 'ranking',
        required: true,
        options: [
          { value: 'financial-success', label: 'Financial Success' },
          { value: 'personal-freedom', label: 'Personal Freedom' },
          { value: 'family-time', label: 'Family Time' },
          { value: 'making-difference', label: 'Making a Difference' },
          { value: 'recognition', label: 'Recognition' },
          { value: 'learning', label: 'Learning' },
          { value: 'security', label: 'Security' },
          { value: 'adventure', label: 'Adventure' }
        ]
      },
      {
        id: 'ethical-standards',
        code: 2,
        order: 2,
        question: 'How important are ethical business practices to you?',
        type: 'scale',
        required: true,
        scaleRange: { min: 1, max: 10 },
        scaleLabels: { min: 'Not Important', max: 'Extremely Important' },
        helpText: 'Consider environmental responsibility, fair treatment of employees, and honest business practices.'
      },
      {
        id: 'decision-making-style',
        code: 3,
        order: 3,
        question: 'How do you prefer to make important decisions?',
        type: 'multiple-choice',
        required: true,
        options: [
          { value: 'data-driven', label: 'Based on data and analysis', description: 'Research thoroughly before deciding' },
          { value: 'intuitive', label: 'Trust my gut instincts', description: 'Rely on intuition and experience' },
          { value: 'collaborative', label: 'Seek input from others', description: 'Consult with advisors and team' },
          { value: 'quick-decisive', label: 'Make quick, decisive choices', description: 'Decide fast and adjust as needed' }
        ]
      },
      {
        id: 'money-motivation',
        code: 4,
        order: 4,
        question: 'What role does money play in your motivation to start a business?',
        type: 'multiple-choice',
        required: true,
        options: [
          { value: 'primary', label: 'Primary motivator', description: 'Financial success is the main goal' },
          { value: 'important', label: 'Important but not primary', description: 'Necessary for other goals' },
          { value: 'secondary', label: 'Secondary consideration', description: 'Nice to have but not essential' },
          { value: 'minimal', label: 'Minimal importance', description: 'Not a significant factor' }
        ]
      }
    ]
  },

  vision: {
    id: 'vision',
    code: 4,
    order: 4,
    title: 'Vision & Impact',
    questions: [
      {
        id: 'ten-year-vision',
        code: 1,
        order: 1,
        question: 'Describe your ideal life 10 years from now',
        type: 'textarea',
        required: true,
        placeholder: 'Paint a detailed picture of your future self...',
        helpText: 'Include your age, how you feel, your identity, contributions, achievements, and relationships.'
      },
      {
        id: 'business-size-preference',
        code: 2,
        order: 2,
        question: 'What size business do you envision building?',
        type: 'multiple-choice',
        required: true,
        options: [
          { value: 'solo', label: 'Solo business (just me)', description: 'Freelancer or consultant model' },
          { value: 'small-team', label: 'Small team (2-10 people)', description: 'Boutique or specialized service' },
          { value: 'medium', label: 'Medium business (10-50 people)', description: 'Regional or niche market leader' },
          { value: 'large', label: 'Large company (50+ people)', description: 'Significant market presence' },
          { value: 'enterprise', label: 'Enterprise/Corporation', description: 'Major industry player' }
        ]
      },
      {
        id: 'impact-scope',
        code: 3,
        order: 3,
        question: 'What scope of impact do you want your business to have?',
        type: 'multiple-choice',
        required: true,
        options: [
          { value: 'local', label: 'Local community impact', description: 'Serve my immediate community' },
          { value: 'regional', label: 'Regional or state-wide impact', description: 'Broader geographic reach' },
          { value: 'national', label: 'National market presence', description: 'Country-wide influence' },
          { value: 'global', label: 'Global reach and impact', description: 'International presence' },
          { value: 'industry', label: 'Transform an entire industry', description: 'Revolutionary change' }
        ]
      },
      {
        id: 'legacy-importance',
        code: 4,
        order: 4,
        question: 'How important is leaving a lasting legacy through your business?',
        type: 'scale',
        required: true,
        scaleRange: { min: 1, max: 10 },
        scaleLabels: { min: 'Not Important', max: 'Extremely Important' },
        helpText: 'Consider whether you want your business to outlast you and create lasting change.'
      }
    ]
  },

  confidence: {
    id: 'confidence',
    code: 5,
    order: 5,
    title: 'Confidence & Skills',
    questions: [
      {
        id: 'vision-confidence',
        code: 1,
        order: 1,
        question: 'How confident are you that you can achieve your 10-year vision?',
        type: 'scale',
        required: true,
        scaleRange: { min: 1, max: 10 },
        scaleLabels: { min: 'Not Confident', max: 'Very Confident' }
      },
      {
        id: 'skill-confidence',
        code: 2,
        order: 2,
        question: 'Rate your confidence in these key entrepreneurial skills',
        type: 'multiple-scale',
        required: true,
        areas: ['Leadership', 'Sales', 'Marketing', 'Finance', 'Strategy', 'Operations', 'Technology', 'Networking'],
        scaleRange: { min: 1, max: 10 }
      },
      {
        id: 'learning-approach',
        code: 3,
        order: 3,
        question: 'How do you prefer to learn new skills needed for your business?',
        type: 'multiple-choice',
        required: true,
        options: [
          { value: 'self-taught', label: 'Self-taught through research', description: 'Books, online courses, trial and error' },
          { value: 'mentorship', label: 'Mentorship and coaching', description: 'Learn from experienced entrepreneurs' },
          { value: 'formal-education', label: 'Formal education and training', description: 'Courses, certifications, degrees' },
          { value: 'hands-on', label: 'Hands-on experience', description: 'Learn by doing and making mistakes' }
        ]
      },
      {
        id: 'obstacle-handling',
        code: 4,
        order: 4,
        question: 'When you encounter major obstacles, you typically:',
        type: 'multiple-choice',
        required: true,
        options: [
          { value: 'persist', label: 'Persist until I find a solution', description: 'Never give up, keep trying' },
          { value: 'adapt', label: 'Adapt my approach and pivot', description: 'Flexible and willing to change' },
          { value: 'seek-help', label: 'Seek help and advice', description: 'Leverage others\' expertise' },
          { value: 'step-back', label: 'Step back and reassess', description: 'Take time to think strategically' }
        ]
      }
    ]
  }
};

export const SELF_DISCOVERY_NAVIGATION = {
  id: 'self_discovery',
  code: 1,
  order: 1,
  title: 'Self Discovery',
  tabs: [
    {
      id: 'assessment',
      code: 1,
      order: 1,
      title: 'Assessment',
      sectionIds: ['motivation', 'life-impact', 'values', 'vision', 'confidence'],
    },
  ],
};

export const IDEA_DISCOVERY_QUESTIONS = {
  'core-alignment': [
    {
      id: 'business-idea-clarity',
      question: 'How clear is your business idea right now?',
      type: 'multiple-choice',
      required: true,
      options: [
        { value: 'very-clear', label: 'Very clear and specific', description: 'I know exactly what I want to build' },
        { value: 'somewhat-clear', label: 'Somewhat clear with details to work out', description: 'General direction but need specifics' },
        { value: 'general-direction', label: 'General direction only', description: 'Know the industry or problem area' },
        { value: 'exploring', label: 'Still exploring options', description: 'Considering multiple possibilities' },
        { value: 'no-idea', label: 'No specific idea yet', description: 'Starting from scratch' }
      ]
    },
    {
      id: 'idea-description',
      question: 'Describe your current business idea (or the type of business you\'re considering)',
      type: 'textarea',
      required: false,
      placeholder: 'Describe your business concept, target market, and value proposition...',
      helpText: 'If you don\'t have a specific idea yet, describe the industry or problem area you\'re interested in.'
    },
    {
      id: 'passion-alignment',
      question: 'How passionate are you about this business idea/area?',
      type: 'scale',
      required: true,
      scaleRange: { min: 1, max: 10 },
      scaleLabels: { min: 'Not Passionate', max: 'Extremely Passionate' },
      helpText: 'Consider whether you could work on this for years without losing interest.'
    },
    {
      id: 'problem-understanding',
      question: 'How well do you understand the problem your business would solve?',
      type: 'scale',
      required: true,
      scaleRange: { min: 1, max: 10 },
      scaleLabels: { min: 'Poor Understanding', max: 'Deep Understanding' },
      helpText: 'Consider your knowledge of customer pain points and current solutions.'
    }
  ],

  'skills-assessment': [
    {
      id: 'relevant-skills',
      question: 'Rate your current skill level in areas relevant to your business idea',
      type: 'multiple-scale',
      required: true,
      areas: ['Industry Knowledge', 'Technical Skills', 'Business Skills', 'Marketing', 'Sales', 'Finance'],
      scaleRange: { min: 1, max: 10 }
    },
    {
      id: 'skill-gaps',
      question: 'What are the biggest skill gaps you need to address?',
      type: 'textarea',
      required: true,
      placeholder: 'List the key skills you need to develop or hire for...',
      helpText: 'Be honest about areas where you lack expertise.'
    },
    {
      id: 'learning-timeline',
      question: 'How quickly can you learn or acquire the skills you need?',
      type: 'multiple-choice',
      required: true,
      options: [
        { value: '1-3-months', label: '1-3 months', description: 'Quick learner with relevant background' },
        { value: '3-6-months', label: '3-6 months', description: 'Moderate learning curve' },
        { value: '6-12-months', label: '6-12 months', description: 'Significant learning required' },
        { value: '1-2-years', label: '1-2 years', description: 'Major skill development needed' },
        { value: 'hire-others', label: 'Better to hire others', description: 'Focus on my strengths' }
      ]
    }
  ],

  'problem-identification': [
    {
      id: 'target-customer',
      question: 'Who is your target customer?',
      type: 'textarea',
      required: true,
      placeholder: 'Describe your ideal customer in detail...',
      helpText: 'Include demographics, psychographics, behaviors, and specific characteristics.'
    },
    {
      id: 'customer-pain-points',
      question: 'What specific problems do your target customers face?',
      type: 'textarea',
      required: true,
      placeholder: 'List the main pain points and challenges...',
      helpText: 'Focus on problems that are frequent, urgent, and expensive to ignore.'
    },
    {
      id: 'current-solutions',
      question: 'How do customers currently solve these problems?',
      type: 'textarea',
      required: true,
      placeholder: 'Describe existing solutions and their limitations...',
      helpText: 'Include competitors, workarounds, and why current solutions are inadequate.'
    },
    {
      id: 'solution-uniqueness',
      question: 'What makes your solution different or better?',
      type: 'textarea',
      required: true,
      placeholder: 'Explain your unique value proposition...',
      helpText: 'Focus on specific advantages over existing solutions.'
    }
  ],

  'market-promise': [
    {
      id: 'market-size',
      question: 'How large is your target market?',
      type: 'multiple-choice',
      required: true,
      options: [
        { value: 'niche', label: 'Niche market (thousands)', description: 'Specialized, small but profitable' },
        { value: 'medium', label: 'Medium market (hundreds of thousands)', description: 'Regional or segment focus' },
        { value: 'large', label: 'Large market (millions)', description: 'Broad market appeal' },
        { value: 'massive', label: 'Massive market (tens of millions+)', description: 'Global or universal need' },
        { value: 'unknown', label: 'Unknown/need to research', description: 'Haven\'t determined market size yet' }
      ]
    },
    {
      id: 'market-growth',
      question: 'Is your target market growing, stable, or declining?',
      type: 'multiple-choice',
      required: true,
      options: [
        { value: 'rapid-growth', label: 'Rapid growth (10%+ annually)', description: 'Emerging or hot market' },
        { value: 'steady-growth', label: 'Steady growth (3-10% annually)', description: 'Healthy, expanding market' },
        { value: 'stable', label: 'Stable (0-3% growth)', description: 'Mature, consistent market' },
        { value: 'declining', label: 'Declining', description: 'Shrinking market' },
        { value: 'unknown', label: 'Unknown/need to research', description: 'Haven\'t analyzed market trends' }
      ]
    },
    {
      id: 'revenue-potential',
      question: 'What revenue potential do you see for your business?',
      type: 'multiple-choice',
      required: true,
      options: [
        { value: 'lifestyle', label: 'Lifestyle business ($50K-$200K annually)', description: 'Comfortable living for founder' },
        { value: 'small-business', label: 'Small business ($200K-$1M annually)', description: 'Support small team' },
        { value: 'growth-business', label: 'Growth business ($1M-$10M annually)', description: 'Significant market presence' },
        { value: 'large-business', label: 'Large business ($10M+ annually)', description: 'Major market player' },
        { value: 'unknown', label: 'Unknown/need to research', description: 'Haven\'t estimated revenue potential' }
      ]
    }
  ],

  'opportunity-scoring': [
    {
      id: 'timing-assessment',
      question: 'How would you rate the timing for this business opportunity?',
      type: 'scale',
      required: true,
      scaleRange: { min: 1, max: 10 },
      scaleLabels: { min: 'Poor Timing', max: 'Perfect Timing' },
      helpText: 'Consider market trends, technology readiness, and economic conditions.'
    },
    {
      id: 'competition-level',
      question: 'How competitive is this market?',
      type: 'multiple-choice',
      required: true,
      options: [
        { value: 'low', label: 'Low competition', description: 'Few or weak competitors' },
        { value: 'moderate', label: 'Moderate competition', description: 'Some established players' },
        { value: 'high', label: 'High competition', description: 'Many strong competitors' },
        { value: 'intense', label: 'Intense competition', description: 'Saturated market with major players' },
        { value: 'unknown', label: 'Unknown/need to research', description: 'Haven\'t analyzed competition yet' }
      ]
    },
    {
      id: 'barriers-to-entry',
      question: 'What are the main barriers to entering this market?',
      type: 'textarea',
      required: true,
      placeholder: 'List regulatory, financial, technical, or other barriers...',
      helpText: 'Consider capital requirements, regulations, technology needs, and competitive advantages.'
    },
    {
      id: 'success-probability',
      question: 'How would you rate the probability of success for this business idea?',
      type: 'scale',
      required: true,
      scaleRange: { min: 1, max: 10 },
      scaleLabels: { min: 'Low Probability', max: 'High Probability' },
      helpText: 'Consider all factors: market, competition, your skills, timing, and resources.'
    }
  ]
}

// Additional question banks for other assessment phases would go here
// MARKET_RESEARCH_QUESTIONS, BUSINESS_PILLARS_QUESTIONS, etc.

export const MARKET_RESEARCH_QUESTIONS = {
  'customer-validation': [
    {
      id: 'customer-interviews',
      question: 'Have you conducted interviews with potential customers?',
      type: 'multiple-choice',
      required: true,
      options: [
        { value: 'many', label: 'Yes, many (20+ interviews)', description: 'Extensive customer research' },
        { value: 'some', label: 'Yes, some (5-20 interviews)', description: 'Good initial validation' },
        { value: 'few', label: 'Yes, a few (1-5 interviews)', description: 'Limited customer input' },
        { value: 'none', label: 'No, not yet', description: 'Haven\'t started customer research' }
      ]
    },
    {
      id: 'customer-feedback',
      question: 'What did you learn from customer conversations?',
      type: 'textarea',
      required: false,
      placeholder: 'Summarize key insights from customer feedback...',
      helpText: 'Include pain points, willingness to pay, and solution preferences.'
    }
  ],
  
  'competitive-analysis': [
    {
      id: 'competitor-identification',
      question: 'List your main competitors',
      type: 'textarea',
      required: true,
      placeholder: 'List direct and indirect competitors...',
      helpText: 'Include both direct competitors and alternative solutions customers use.'
    },
    {
      id: 'competitive-advantage',
      question: 'What is your sustainable competitive advantage?',
      type: 'textarea',
      required: true,
      placeholder: 'Describe what makes you different and defensible...',
      helpText: 'Focus on advantages that are difficult for competitors to copy.'
    }
  ]
}

export const BUSINESS_PILLARS_QUESTIONS = {
  'business-model': [
    {
      id: 'revenue-model',
      question: 'How will your business make money?',
      type: 'multiple-choice',
      required: true,
      options: [
        { value: 'product-sales', label: 'Product sales', description: 'Sell physical or digital products' },
        { value: 'service-fees', label: 'Service fees', description: 'Charge for services or consulting' },
        { value: 'subscription', label: 'Subscription model', description: 'Recurring monthly/annual fees' },
        { value: 'marketplace', label: 'Marketplace commission', description: 'Take percentage of transactions' },
        { value: 'advertising', label: 'Advertising revenue', description: 'Monetize through ads' },
        { value: 'freemium', label: 'Freemium model', description: 'Free basic, paid premium features' }
      ]
    },
    {
      id: 'pricing-strategy',
      question: 'What is your pricing strategy?',
      type: 'textarea',
      required: true,
      placeholder: 'Describe your pricing approach and rationale...',
      helpText: 'Include price points, pricing model, and how you determined these prices.'
    }
  ],
  
  'operations': [
    {
      id: 'key-activities',
      question: 'What are the key activities your business must perform?',
      type: 'textarea',
      required: true,
      placeholder: 'List the core activities needed to deliver value...',
      helpText: 'Include production, marketing, sales, customer service, etc.'
    },
    {
      id: 'key-resources',
      question: 'What key resources does your business need?',
      type: 'textarea',
      required: true,
      placeholder: 'List physical, intellectual, human, and financial resources...',
      helpText: 'Include equipment, technology, people, capital, and intellectual property.'
    }
  ]
}


// ── Phase 5: Product Concept Testing ─────────────────────────────────────────
// Section 1: concept-design
export const PCT_SECTION_CONCEPT_DESIGN = [
  {
    id: 'pct-s1-1',
    question: 'Describe your product or service concept in plain language.',
    hint: 'What exactly are you offering? Keep it to 2-3 sentences.',
    type: 'textarea',
    required: true,
  },
  {
    id: 'pct-s1-2',
    question: 'Who is the primary target audience for this concept test?',
    hint: 'Be specific: age, role, situation, or context.',
    type: 'text',
    required: true,
  },
  {
    id: 'pct-s1-3',
    question: 'What is the key value proposition you are testing?',
    hint: 'What specific benefit or outcome does your concept promise?',
    type: 'textarea',
    required: true,
  },
  {
    id: 'pct-s1-4',
    question: 'What would a successful concept test look like to you?',
    hint: 'Define success in concrete terms before you start testing.',
    type: 'textarea',
  },
]

// Section 2: test-methods
export const PCT_SECTION_TEST_METHODS = [
  {
    id: 'pct-s2-1',
    question: 'What testing method(s) did or will you use?',
    hint: 'e.g. user interviews, landing page, mockup, pre-orders, pilot, pricing test, mentor feedback',
    type: 'textarea',
    required: true,
  },
  {
    id: 'pct-s2-2',
    question: 'How many people did you contact or test with?',
    hint: 'Enter 0 if testing is not yet complete.',
    type: 'number',
    required: true,
  },
  {
    id: 'pct-s2-3',
    question: 'How did you find and select your test participants?',
    hint: 'Describe your recruitment method and any potential bias.',
    type: 'textarea',
  },
  {
    id: 'pct-s2-4',
    question: 'What exactly did you present or demonstrate to participants?',
    hint: 'Describe the test scenario — what they saw, heard, or were asked.',
    type: 'textarea',
  },
]

// Section 3: feedback-data
export const PCT_SECTION_FEEDBACK_DATA = [
  {
    id: 'pct-s3-1',
    question: 'Did people clearly understand your concept? Describe their comprehension.',
    hint: 'Did they get it immediately, need explanation, or remain confused?',
    type: 'textarea',
    required: true,
  },
  {
    id: 'pct-s3-2',
    question: 'What was the level of genuine desire or interest?',
    hint: 'Choose the response that best describes the majority reaction.',
    type: 'select',
    required: true,
    options: [
      { value: 'STRONG',   label: 'Strong — multiple people asked to buy, sign up, or commit' },
      { value: 'MODERATE', label: 'Moderate — positive reactions but no concrete action' },
      { value: 'POLITE',   label: 'Polite — friendly feedback but vague or noncommittal' },
      { value: 'CONFUSED', label: 'Confused — people did not understand the concept' },
      { value: 'NEGATIVE', label: 'Negative — rejected, dismissed, or uninterested' },
    ],
  },
  {
    id: 'pct-s3-3',
    question: 'What were the main objections raised?',
    hint: 'e.g. price, timing, complexity, trust, existing alternatives',
    type: 'textarea',
  },
  {
    id: 'pct-s3-4',
    question: 'What conversion signals did you receive?',
    hint: 'e.g. pre-orders, sign-ups, pilot agreements, referrals, donations, bookings',
    type: 'textarea',
  },
  {
    id: 'pct-s3-5',
    question: 'How many people took a concrete action (sign up, pre-order, booking, agreement)?',
    hint: 'Enter 0 if none.',
    type: 'number',
  },
]

// Section 4: evidence-review
export const PCT_SECTION_EVIDENCE_REVIEW = [
  {
    id: 'pct-s4-1',
    question: 'What were the most important positive findings from your testing?',
    hint: 'Specific, honest observations — not just what you hoped to hear.',
    type: 'textarea',
    required: true,
  },
  {
    id: 'pct-s4-2',
    question: 'What concerns, risks, or blockers emerged from the tests?',
    hint: 'Be honest. These will inform whether to proceed, revise, or pivot.',
    type: 'textarea',
  },
  {
    id: 'pct-s4-3',
    question: 'How would you rate the overall strength of your evidence?',
    hint: 'Honest self-assessment of evidence quality.',
    type: 'select',
    required: true,
    options: [
      { value: 'STRONG',    label: 'Strong — multiple concrete commitments or actions' },
      { value: 'MODERATE',  label: 'Moderate — positive signals but no commitments yet' },
      { value: 'WEAK',      label: 'Weak — mostly polite or vague feedback' },
      { value: 'VERY_WEAK', label: 'Very weak — confused, conflicting, or negative responses' },
    ],
  },
  {
    id: 'pct-s4-4',
    question: 'What changes would improve your concept based on this testing?',
    hint: 'Actionable revisions informed by what you heard.',
    type: 'textarea',
  },
]

// Flat list for legacy compatibility
export const PRODUCT_CONCEPT_TESTING_QUESTIONS = [
  ...PCT_SECTION_CONCEPT_DESIGN,
  ...PCT_SECTION_TEST_METHODS,
  ...PCT_SECTION_FEEDBACK_DATA,
  ...PCT_SECTION_EVIDENCE_REVIEW,
];

// ── Phase 6: Business Development ─────────────────────────────────────────────
// Section 1: venture-summary
export const BD_SECTION_VENTURE_SUMMARY = [
  {
    id: 'bd-s1-1',
    question: 'Describe your venture in 2-3 sentences.',
    hint: 'What does it do, who is it for, and why does it exist?',
    type: 'textarea',
    required: true,
  },
  {
    id: 'bd-s1-2',
    question: 'What is your key value proposition?',
    hint: 'What specific outcome or benefit does your customer get?',
    type: 'textarea',
    required: true,
  },
  {
    id: 'bd-s1-3',
    question: 'Who is your primary target customer?',
    hint: 'Be as specific as possible: demographics, role, situation.',
    type: 'text',
  },
  {
    id: 'bd-s1-4',
    question: 'What is your unique competitive advantage?',
    hint: 'What makes this hard to copy or replace?',
    type: 'textarea',
  },
]

// Section 2: financial-model
export const BD_SECTION_FINANCIAL_MODEL = [
  {
    id: 'bd-s2-1',
    question: 'What is your primary revenue model?',
    hint: 'e.g. Subscription, transaction fee, product sales, service fees, grants',
    type: 'text',
    required: true,
  },
  {
    id: 'bd-s2-2',
    question: 'What is your pricing approach?',
    hint: 'Describe your price point(s) and rationale.',
    type: 'textarea',
    required: true,
  },
  {
    id: 'bd-s2-3',
    question: 'What are your main cost assumptions?',
    hint: 'Key monthly costs: infrastructure, people, tools, marketing.',
    type: 'textarea',
  },
  {
    id: 'bd-s2-4',
    question: 'What is your current runway and funding situation?',
    hint: 'How long can you operate? Are you bootstrapped, seeking investment, or grant-funded?',
    type: 'textarea',
  },
]

// Section 3: go-to-market
export const BD_SECTION_GO_TO_MARKET = [
  {
    id: 'bd-s3-1',
    question: 'How will you acquire your first customers?',
    hint: 'Specific tactics: outreach, referrals, content, events, ads, partnerships.',
    type: 'textarea',
    required: true,
  },
  {
    id: 'bd-s3-2',
    question: 'What are your primary acquisition channels?',
    hint: 'List the 1-3 channels most likely to work for your audience.',
    type: 'textarea',
  },
  {
    id: 'bd-s3-3',
    question: 'What are your key launch milestones in the next 90 days?',
    hint: 'Be specific: dates, targets, actions.',
    type: 'textarea',
  },
  {
    id: 'bd-s3-4',
    question: 'What partnerships or alliances would accelerate your launch?',
    hint: 'Distribution partners, referral sources, integrations, co-marketing.',
    type: 'textarea',
  },
]

// Section 4: operations
export const BD_SECTION_OPERATIONS = [
  {
    id: 'bd-s4-1',
    question: 'What legal structure will you use?',
    hint: 'e.g. Sole trader, Ltd, LLC, non-profit. Describe your decision and timeline.',
    type: 'textarea',
    required: true,
  },
  {
    id: 'bd-s4-2',
    question: 'What are your key operational processes?',
    hint: 'Onboarding, delivery, billing, customer support — how does work actually flow?',
    type: 'textarea',
  },
  {
    id: 'bd-s4-3',
    question: 'What tools and systems will you use?',
    hint: 'CRM, project management, communication, payments, analytics.',
    type: 'textarea',
  },
  {
    id: 'bd-s4-4',
    question: 'What professional support do you need?',
    hint: 'e.g. accountant, lawyer, advisor, technical co-founder.',
    type: 'textarea',
  },
]

// Section 5: risk-roadmap
export const BD_SECTION_RISK_ROADMAP = [
  {
    id: 'bd-s5-1',
    question: 'What are your top 3 risks?',
    hint: 'What could derail the venture in the next 6 months?',
    type: 'textarea',
  },
  {
    id: 'bd-s5-2',
    question: 'How will you mitigate each risk?',
    hint: 'Specific actions or contingencies for each risk.',
    type: 'textarea',
  },
  {
    id: 'bd-s5-3',
    question: 'What will you accomplish in the next 30 days?',
    hint: 'Concrete, measurable outcomes.',
    type: 'textarea',
    required: true,
  },
  {
    id: 'bd-s5-4',
    question: 'What will you accomplish in the next 60 days?',
    hint: 'Building on the 30-day outcomes.',
    type: 'textarea',
  },
  {
    id: 'bd-s5-5',
    question: 'What will you accomplish in the next 90 days?',
    hint: 'End-state for your first quarter of execution.',
    type: 'textarea',
  },
]

export const BUSINESS_DEVELOPMENT_QUESTIONS = [
  ...BD_SECTION_VENTURE_SUMMARY,
  ...BD_SECTION_FINANCIAL_MODEL,
  ...BD_SECTION_GO_TO_MARKET,
  ...BD_SECTION_OPERATIONS,
  ...BD_SECTION_RISK_ROADMAP,
];

// ── Phase 7: Business Prototype Testing ────────────────────────────────────

// Section 1: traction-evidence
export const PT_SECTION_TRACTION = [
  {
    id: 'pt-s1-1',
    question: 'What type of traction have you achieved so far?',
    hint: 'Select the strongest form of real-world validation you have obtained.',
    type: 'select',
    required: true,
    options: [
      { value: 'paying_customers', label: 'Paying customers' },
      { value: 'pilot_contracts', label: 'Signed pilot contracts' },
      { value: 'signed_agreements', label: 'Signed partnership / distribution agreements' },
      { value: 'active_users', label: 'Active users (free or beta)' },
      { value: 'signups', label: 'Signups / waitlist' },
      { value: 'partnerships', label: 'Verbal partnership commitments' },
      { value: 'interest_expressed', label: 'Interest expressed (meetings, emails)' },
      { value: 'meetings_held', label: 'Meetings held only — no commitment' },
      { value: 'none', label: 'No traction yet' },
    ],
  },
  {
    id: 'pt-s1-2',
    question: 'How many people or organisations represent that traction?',
    hint: 'Enter a number. Count only distinct people or organisations.',
    type: 'number',
    required: true,
  },
]

// Section 2: conversion-sales
export const PT_SECTION_CONVERSION = [
  {
    id: 'pt-s2-1',
    question: 'How many people or organisations have you contacted or reached out to?',
    hint: 'Total outreach attempts: emails, calls, messages, meetings initiated.',
    type: 'number',
    required: true,
  },
  {
    id: 'pt-s2-2',
    question: 'How many of those contacts converted to a sale, pilot, or agreement?',
    hint: 'Include any paying customer, signed contract, or active pilot.',
    type: 'number',
    required: true,
  },
]

// Section 3: delivery-operations
export const PT_SECTION_DELIVERY = [
  {
    id: 'pt-s3-1',
    question: 'How well have you delivered what you promised to customers or pilot users?',
    hint: 'Honest assessment of your actual delivery vs. what was agreed.',
    type: 'select',
    required: true,
    options: [
      { value: 'fully_delivered', label: 'Fully delivered — on time, on spec, no major issues' },
      { value: 'mostly_delivered', label: 'Mostly delivered — minor gaps, resolved quickly' },
      { value: 'partially_delivered', label: 'Partially delivered — significant gaps or delays' },
      { value: 'not_delivered', label: 'Not delivered — commitments not met' },
      { value: 'not_applicable', label: 'Not applicable — no delivery yet' },
    ],
  },
  {
    id: 'pt-s3-2',
    question: 'What operational friction or bottlenecks did you encounter?',
    hint: 'Time, cost, complexity, errors, customer support issues, delivery failures.',
    type: 'textarea',
  },
]

// Section 4: financial-reality
export const PT_SECTION_FINANCIAL = [
  {
    id: 'pt-s4-1',
    question: 'How does your actual revenue compare to your original plan?',
    hint: 'Be honest — this drives the most important decisions.',
    type: 'select',
    required: true,
    options: [
      { value: 'above_plan', label: 'Above plan — exceeded revenue expectations' },
      { value: 'on_plan', label: 'On plan — close to expected revenue' },
      { value: 'below_plan', label: 'Below plan — less than expected' },
      { value: 'no_revenue_yet', label: 'No revenue yet — still pre-revenue' },
    ],
  },
  {
    id: 'pt-s4-2',
    question: 'How do your actual costs compare to your original budget?',
    hint: 'Include time costs, tool costs, service costs, unexpected expenses.',
    type: 'select',
    options: [
      { value: 'under_budget', label: 'Under budget — costs lower than expected' },
      { value: 'on_budget', label: 'On budget — costs as expected' },
      { value: 'over_budget', label: 'Over budget — costs higher than expected' },
      { value: 'no_budget_set', label: 'No budget was set' },
    ],
  },
]

// Section 5: customer-response
export const PT_SECTION_CUSTOMER = [
  {
    id: 'pt-s5-1',
    question: 'How would you describe overall customer or user satisfaction?',
    hint: 'Based on feedback, usage, and direct conversations.',
    type: 'select',
    required: true,
    options: [
      { value: 'very_satisfied', label: 'Very satisfied — strong positive feedback' },
      { value: 'satisfied', label: 'Satisfied — generally positive, minor issues' },
      { value: 'neutral', label: 'Neutral — mixed feedback, unclear signal' },
      { value: 'dissatisfied', label: 'Dissatisfied — negative feedback, complaints' },
      { value: 'no_feedback', label: 'No feedback collected yet' },
    ],
  },
  {
    id: 'pt-s5-2',
    question: 'Have customers shown repeat interest, referrals, or retention?',
    hint: 'Any evidence of customers coming back or recommending you.',
    type: 'select',
    options: [
      { value: 'yes_repeat_customers', label: 'Yes — customers returned or renewed' },
      { value: 'yes_referrals', label: 'Yes — customers referred others' },
      { value: 'yes_both', label: 'Yes — both repeat usage and referrals' },
      { value: 'too_early', label: 'Too early to tell' },
      { value: 'no', label: 'No repeat interest or referrals yet' },
    ],
  },
]

// Section 6: founder-performance
export const PT_SECTION_FOUNDER = [
  {
    id: 'pt-s6-1',
    question: 'How much of your original execution plan did you complete?',
    hint: 'Tasks, commitments, and milestones you set before the prototype phase.',
    type: 'select',
    required: true,
    options: [
      { value: 'completed_all', label: 'Completed all or nearly all planned tasks' },
      { value: 'completed_most', label: 'Completed most — some gaps' },
      { value: 'completed_some', label: 'Completed some — significant gaps' },
      { value: 'completed_little', label: 'Completed little — most tasks not done' },
    ],
  },
  {
    id: 'pt-s6-2',
    question: 'How well did you adapt when things did not go as planned?',
    hint: 'When faced with unexpected problems, what did you do?',
    type: 'select',
    options: [
      { value: 'adapted_quickly', label: 'Adapted quickly and effectively' },
      { value: 'adapted_with_support', label: 'Adapted with mentor or support help' },
      { value: 'slow_to_adapt', label: 'Slow to adapt — took time to change course' },
      { value: 'struggled', label: 'Struggled to adapt — felt stuck' },
    ],
  },
]

export const BUSINESS_PROTOTYPE_TESTING_QUESTIONS = [
  ...PT_SECTION_TRACTION,
  ...PT_SECTION_CONVERSION,
  ...PT_SECTION_DELIVERY,
  ...PT_SECTION_FINANCIAL,
  ...PT_SECTION_CUSTOMER,
  ...PT_SECTION_FOUNDER,
];

