import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Slider } from '@/components/ui/slider.jsx'
import { 
  Lightbulb, 
  Target, 
  Star, 
  Compass, 
  Brain, 
  TrendingUp,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  AlertCircle,
  Users,
  Zap,
  Heart,
  Search,
  Building,
  DollarSign
} from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'

const IdeaDiscoveryAssessment = () => {
  const {
    assessmentData,
    updateResponse,
    updateProgress,
    completePhase,
    updatePhase
  } = useAssessment()
  
  const [currentSection, setCurrentSection] = useState('core-alignment')
  const [sectionProgress, setSectionProgress] = useState({})
  
  const ideaDiscoveryData = assessmentData['idea_discovery'] || {}
  const responses = ideaDiscoveryData.responses || {}

  // Assessment sections configuration
  const sections = [
    {
      id: 'core-alignment',
      title: 'Core Alignment Matrix',
      description: 'Connect work you love with causes you care about',
      icon: Heart,
      duration: '15-20 minutes',
      questions: coreAlignmentQuestions
    },
    {
      id: 'skills-assessment',
      title: 'Skills & Capabilities',
      description: 'Identify your strengths and development areas',
      icon: Star,
      duration: '20-25 minutes',
      questions: skillsAssessmentQuestions
    },
    {
      id: 'problem-identification',
      title: 'Problem Discovery',
      description: 'Find problems you can solve effectively',
      icon: Search,
      duration: '25-30 minutes',
      questions: problemIdentificationQuestions
    },
    {
      id: 'market-promise',
      title: 'Market Promise',
      description: 'Define what you will deliver to customers',
      icon: Target,
      duration: '20-25 minutes',
      questions: marketPromiseQuestions
    },
    {
      id: 'opportunity-scoring',
      title: 'Opportunity Evaluation',
      description: 'Score and prioritize your business opportunities',
      icon: TrendingUp,
      duration: '15-20 minutes',
      questions: opportunityScoringQuestions
    },
    {
      id: 'results',
      title: 'Your Business Opportunities',
      description: 'Discover your top-ranked business ideas',
      icon: Lightbulb,
      duration: '5 minutes',
      questions: []
    }
  ]

  // Calculate overall progress
  const calculateOverallProgress = () => {
    const totalSections = sections.length - 1 // Exclude results section
    const completedSections = Object.values(sectionProgress).filter(progress => progress >= 100).length
    return Math.round((completedSections / totalSections) * 100)
  }

  // Calculate section progress
  const calculateSectionProgress = (sectionId) => {
    const section = sections.find(s => s.id === sectionId)
    if (!section || !section.questions) return 0
    
    const sectionResponses = responses[sectionId] || {}
    const answeredQuestions = Object.keys(sectionResponses).length
    const totalQuestions = section.questions.length
    
    return totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0
  }

  // Update section progress when responses change
  useEffect(() => {
    const newProgress = {}
    sections.forEach(section => {
      if (section.questions) {
        newProgress[section.id] = calculateSectionProgress(section.id)
      }
    })
    setSectionProgress(newProgress)
    
    // Update overall progress
    const overallProgress = calculateOverallProgress()
    updateProgress('idea_discovery', overallProgress)
    
    // Complete phase if all sections are done
    if (overallProgress >= 100 && !ideaDiscoveryData.completed) {
      completePhase('idea_discovery')
    }
  }, [responses])

  const handleResponse = (questionId, answer) => {
    updateResponse('idea_discovery', questionId, answer, currentSection)
  }

  const nextSection = () => {
    const currentIndex = sections.findIndex(s => s.id === currentSection)
    if (currentIndex < sections.length - 1) {
      setCurrentSection(sections[currentIndex + 1].id)
    }
  }

  const previousSection = () => {
    const currentIndex = sections.findIndex(s => s.id === currentSection)
    if (currentIndex > 0) {
      setCurrentSection(sections[currentIndex - 1].id)
    }
  }

  const currentSectionData = sections.find(s => s.id === currentSection)
  const currentSectionIndex = sections.findIndex(s => s.id === currentSection)

  return (
    <div className="space-y-6">
      {/* Section Navigation */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
        {sections.map((section, index) => {
          const Icon = section.icon
          const progress = sectionProgress[section.id] || 0
          const isActive = section.id === currentSection
          const isCompleted = progress >= 100
          const isAccessible = index <= currentSectionIndex || isCompleted

          return (
            <Card 
              key={section.id}
              className={`cursor-pointer transition-all duration-200 ${
                isActive ? 'ring-2 ring-primary' : ''
              } ${!isAccessible ? 'opacity-50' : 'hover:shadow-md'}`}
              onClick={() => isAccessible && setCurrentSection(section.id)}
            >
              <CardContent className="p-3 text-center">
                <div className="flex items-center justify-center mb-2">
                  <Icon className="h-5 w-5 text-primary" />
                  {isCompleted && <CheckCircle className="h-4 w-4 text-green-500 ml-1" />}
                </div>
                <h4 className="text-xs font-medium mb-1">{section.title}</h4>
                <Progress value={progress} className="h-1" />
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Current Section Content */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {React.createElement(currentSectionData.icon, { className: "h-6 w-6 text-primary" })}
              <div>
                <CardTitle>{currentSectionData.title}</CardTitle>
                <CardDescription>{currentSectionData.description}</CardDescription>
              </div>
            </div>
            <Badge variant="outline">{currentSectionData.duration}</Badge>
          </div>
          <Progress value={sectionProgress[currentSection] || 0} className="mt-4" />
        </CardHeader>
        <CardContent>
          {currentSection === 'results' ? (
            <OpportunityResults opportunities={ideaDiscoveryData.opportunities} insights={ideaDiscoveryData.insights} />
          ) : (
            <SectionQuestions 
              section={currentSectionData}
              responses={responses[currentSection] || {}}
              onResponse={handleResponse}
            />
          )}
        </CardContent>
      </Card>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={previousSection}
          disabled={currentSectionIndex === 0}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Previous
        </Button>
        {currentSectionIndex === sections.length - 1 ? (
          <Button
            onClick={() => {
              completePhase("idea_discovery");
              updatePhase("market_research");
            }}
          >
            Next Phase
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        ) : (
          <Button onClick={nextSection}>
            Next
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        )}
      </div>
    </div>
  )
}

// Section Questions Component
const SectionQuestions = ({ section, responses, onResponse }) => {
  if (!section.questions || section.questions.length === 0) {
    return <div className="text-center text-muted-foreground">No questions available for this section.</div>
  }

  return (
    <div className="space-y-8">
      {section.questions.map((question, index) => (
        <QuestionCard 
          key={question.id}
          question={question}
          response={responses[question.id]}
          onResponse={(answer) => onResponse(question.id, answer)}
          questionNumber={index + 1}
          totalQuestions={section.questions.length}
        />
      ))}
    </div>
  )
}

// Individual Question Card Component
const QuestionCard = ({ question, response, onResponse, questionNumber, totalQuestions }) => {
  const renderQuestionInput = () => {
    switch (question.type) {
      case 'multiple-choice':
        return (
          <RadioGroup value={response || ''} onValueChange={onResponse}>
            {question.options.map((option) => (
              <div key={option.value} className="flex items-center space-x-2">
                <RadioGroupItem value={option.value} id={option.value} />
                <Label htmlFor={option.value} className="flex-1 cursor-pointer">
                  <div>
                    <div className="font-medium">{option.label}</div>
                    {option.description && (
                      <div className="text-sm text-muted-foreground">{option.description}</div>
                    )}
                  </div>
                </Label>
              </div>
            ))}
          </RadioGroup>
        )

      case 'scale':
        return (
          <div className="space-y-4">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>{question.scaleLabels?.min || 'Low'}</span>
              <span>{question.scaleLabels?.max || 'High'}</span>
            </div>
            <Slider
              value={[response || question.scaleRange?.min || 1]}
              onValueChange={(value) => onResponse(value[0])}
              min={question.scaleRange?.min || 1}
              max={question.scaleRange?.max || 10}
              step={1}
              className="w-full"
            />
            <div className="text-center text-sm font-medium">
              Current value: {response || question.scaleRange?.min || 1}
            </div>
          </div>
        )

      case 'textarea':
        return (
          <Textarea
            value={response || ''}
            onChange={(e) => onResponse(e.target.value)}
            placeholder={question.placeholder || 'Enter your response...'}
            rows={4}
            className="w-full"
          />
        )

      case 'matrix':
        return (
          <MatrixInput 
            rows={question.rows}
            columns={question.columns}
            value={response || {}}
            onChange={onResponse}
          />
        )

      case 'ranking':
        return (
          <RankingInput 
            options={question.options}
            value={response || []}
            onChange={onResponse}
          />
        )

      default:
        return <div className="text-muted-foreground">Unsupported question type</div>
    }
  }

  return (
    <Card className="border-l-4 border-l-primary">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="secondary">Question {questionNumber} of {totalQuestions}</Badge>
              {question.required && <Badge variant="destructive">Required</Badge>}
            </div>
            <CardTitle className="text-lg">{question.question}</CardTitle>
            {question.description && (
              <CardDescription className="mt-2">{question.description}</CardDescription>
            )}
          </div>
          {response && <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />}
        </div>
      </CardHeader>
      <CardContent>
        {renderQuestionInput()}
        {question.helpText && (
          <div className="mt-4 p-3 bg-muted rounded-md">
            <div className="flex items-start gap-2">
              <Lightbulb className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
              <p className="text-sm text-muted-foreground">{question.helpText}</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Matrix Input Component
const MatrixInput = ({ rows, columns, value, onChange }) => {
  const handleCellChange = (rowId, columnId, cellValue) => {
    const newValue = { ...value }
    if (!newValue[rowId]) newValue[rowId] = {}
    newValue[rowId][columnId] = cellValue
    onChange(newValue)
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="p-2 text-left"></th>
            {columns.map(column => (
              <th key={column.id} className="p-2 text-center text-sm font-medium">
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr key={row.id} className="border-t">
              <td className="p-2 font-medium text-sm">{row.label}</td>
              {columns.map(column => (
                <td key={column.id} className="p-2 text-center">
                  <Slider
                    value={[value[row.id]?.[column.id] || 1]}
                    onValueChange={(val) => handleCellChange(row.id, column.id, val[0])}
                    min={1}
                    max={5}
                    step={1}
                    className="w-20"
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// Ranking Input Component
const RankingInput = ({ options, value, onChange }) => {
  const [rankings, setRankings] = useState(value || [])

  const handleRankChange = (optionValue, rank) => {
    const newRankings = [...rankings]
    const existingIndex = newRankings.findIndex(r => r.value === optionValue)
    
    if (existingIndex >= 0) {
      newRankings[existingIndex].rank = rank
    } else {
      newRankings.push({ value: optionValue, rank })
    }
    
    setRankings(newRankings)
    onChange(newRankings)
  }

  return (
    <div className="space-y-3">
      {options.map((option) => {
        const currentRank = rankings.find(r => r.value === option.value)?.rank || ''
        return (
          <div key={option.value} className="flex items-center gap-3">
            <select
              value={currentRank}
              onChange={(e) => handleRankChange(option.value, parseInt(e.target.value))}
              className="w-16 px-2 py-1 border rounded"
            >
              <option value="">-</option>
              {options.map((_, index) => (
                <option key={index + 1} value={index + 1}>{index + 1}</option>
              ))}
            </select>
            <Label className="flex-1">{option.label}</Label>
          </div>
        )
      })}
    </div>
  )
}

// Opportunity Results Component
const OpportunityResults = ({ opportunities, insights }) => {
  if (!opportunities || !insights) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-lg font-semibold mb-2">Complete Assessment to See Results</h3>
        <p className="text-muted-foreground">
          Finish all sections to discover your top business opportunities and get personalized recommendations.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Top Opportunities */}
      <div className="grid md:grid-cols-2 gap-6">
        {opportunities.slice(0, 4).map((opportunity, index) => (
          <Card key={index} className="border-2 border-primary/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{opportunity.title}</CardTitle>
                <Badge variant="secondary">Score: {opportunity.score}/10</Badge>
              </div>
              <CardDescription>{opportunity.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <h4 className="font-semibold text-sm mb-1">Market Size</h4>
                  <p className="text-sm text-muted-foreground">{opportunity.marketSize}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-sm mb-1">Key Advantages</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    {opportunity.advantages.map((advantage, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <CheckCircle className="h-3 w-3 text-green-500" />
                        {advantage}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Insights and Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Your Entrepreneurial Profile</CardTitle>
          <CardDescription>Based on your idea discovery assessment</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-3">Core Strengths</h4>
              <ul className="space-y-2">
                {insights.strengths?.map((strength, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <Star className="h-4 w-4 text-primary" />
                    <span className="text-sm">{strength}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Development Areas</h4>
              <ul className="space-y-2">
                {insights.developmentAreas?.map((area, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-primary" />
                    <span className="text-sm">{area}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Next Steps */}
      <Card>
        <CardHeader>
          <CardTitle>Recommended Next Steps</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {insights.nextSteps?.map((step, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                <div className="w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </div>
                <div>
                  <h4 className="font-semibold text-sm">{step.title}</h4>
                  <p className="text-sm text-muted-foreground">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Question definitions
const coreAlignmentQuestions = [
  {
    id: 'passion-work-matrix',
    question: 'Rate your passion and skill level for different types of work',
    type: 'matrix',
    required: true,
    rows: [
      { id: 'creative-work', label: 'Creative Work (Design, Writing, Art)' },
      { id: 'analytical-work', label: 'Analytical Work (Data, Research, Strategy)' },
      { id: 'technical-work', label: 'Technical Work (Programming, Engineering)' },
      { id: 'people-work', label: 'People Work (Sales, HR, Consulting)' },
      { id: 'operational-work', label: 'Operational Work (Management, Logistics)' }
    ],
    columns: [
      { id: 'passion', label: 'Passion Level' },
      { id: 'skill', label: 'Current Skill' },
      { id: 'potential', label: 'Growth Potential' }
    ],
    helpText: 'Rate each area from 1 (low) to 5 (high). This helps identify your sweet spot for business opportunities.'
  },
  {
    id: 'cause-alignment',
    question: 'Which causes or missions resonate most strongly with you?',
    type: 'ranking',
    required: true,
    options: [
      { value: 'environmental', label: 'Environmental Sustainability' },
      { value: 'education', label: 'Education & Learning' },
      { value: 'healthcare', label: 'Health & Wellness' },
      { value: 'social-justice', label: 'Social Justice & Equality' },
      { value: 'economic-empowerment', label: 'Economic Empowerment' },
      { value: 'technology-innovation', label: 'Technology Innovation' },
      { value: 'community-building', label: 'Community Building' },
      { value: 'personal-development', label: 'Personal Development' }
    ],
    helpText: 'Rank these causes in order of personal importance. Businesses aligned with your values are more sustainable.'
  }
]

const skillsAssessmentQuestions = [
  {
    id: 'current-skills',
    question: 'Rate your current proficiency in key business skills',
    type: 'matrix',
    required: true,
    rows: [
      { id: 'leadership', label: 'Leadership & Team Management' },
      { id: 'sales-marketing', label: 'Sales & Marketing' },
      { id: 'financial-management', label: 'Financial Management' },
      { id: 'product-development', label: 'Product Development' },
      { id: 'operations', label: 'Operations & Process Management' },
      { id: 'strategic-thinking', label: 'Strategic Thinking' },
      { id: 'communication', label: 'Communication & Presentation' },
      { id: 'problem-solving', label: 'Problem Solving & Innovation' }
    ],
    columns: [
      { id: 'current', label: 'Current Level' },
      { id: 'importance', label: 'Importance for Goals' },
      { id: 'willingness', label: 'Willingness to Develop' }
    ],
    helpText: 'Be honest about your current abilities. This assessment helps identify development priorities.'
  }
]

const problemIdentificationQuestions = [
  {
    id: 'problem-experiences',
    question: 'Describe 3 significant problems you have personally experienced',
    type: 'textarea',
    required: true,
    placeholder: 'Think about frustrations in your daily life, work, or community. What problems do you wish someone would solve?',
    helpText: 'The best business opportunities often come from solving problems you understand deeply.'
  },
  {
    id: 'problem-observation',
    question: 'What problems do you frequently observe others struggling with?',
    type: 'textarea',
    required: true,
    placeholder: 'Consider problems in your industry, community, or social circles...',
    helpText: 'External observation can reveal market opportunities you might not have considered.'
  }
]

const marketPromiseQuestions = [
  {
    id: 'value-proposition',
    question: 'If you started a business today, what unique value would you provide?',
    type: 'textarea',
    required: true,
    placeholder: 'What would make customers choose you over alternatives?',
    helpText: 'Think about your unique combination of skills, experience, and perspective.'
  },
  {
    id: 'target-customer',
    question: 'Who would be your ideal first customers?',
    type: 'textarea',
    required: true,
    placeholder: 'Be specific about demographics, needs, and characteristics...',
    helpText: 'Narrow focus on early customers helps validate and refine your business concept.'
  }
]

const opportunityScoringQuestions = [
  {
    id: 'opportunity-criteria',
    question: 'Rate the importance of these factors for your ideal business opportunity',
    type: 'scale',
    required: true,
    scaleRange: { min: 1, max: 10 },
    scaleLabels: { min: 'Not Important', max: 'Extremely Important' },
    helpText: 'This helps weight your opportunity scores based on your personal priorities.'
  }
]

export default IdeaDiscoveryAssessment

