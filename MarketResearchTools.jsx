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
  Search, 
  Users, 
  TrendingUp, 
  Target, 
  BarChart3, 
  Globe,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  AlertCircle,
  Building,
  DollarSign,
  Eye,
  MessageSquare,
  FileText,
  Zap,
  Shield,
  Clock,
  Award,
  Lightbulb
} from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'

const MarketResearchTools = () => {
  const { 
    assessmentData, 
    updateResponse, 
    updateProgress, 
    completePhase 
  } = useAssessment()
  
  const [currentSection, setCurrentSection] = useState('competitive-analysis')
  const [sectionProgress, setSectionProgress] = useState({})
  
  const marketResearchData = assessmentData['market-research'] || {}
  const responses = marketResearchData.responses || {}

  // Assessment sections configuration
  const sections = [
    {
      id: 'competitive-analysis',
      title: 'Competitive Landscape',
      description: 'Analyze your competition and market positioning',
      icon: BarChart3,
      duration: '30-45 minutes',
      questions: competitiveAnalysisQuestions
    },
    {
      id: 'customer-research',
      title: 'Customer Insights',
      description: 'Understand your target customers deeply',
      icon: Users,
      duration: '45-60 minutes',
      questions: customerResearchQuestions
    },
    {
      id: 'stakeholder-mapping',
      title: 'Stakeholder Ecosystem',
      description: 'Map all parties that influence your business',
      icon: Globe,
      duration: '30-40 minutes',
      questions: stakeholderMappingQuestions
    },
    {
      id: 'problem-classification',
      title: 'Problem Analysis',
      description: 'Classify and prioritize the problems you solve',
      icon: Target,
      duration: '25-35 minutes',
      questions: problemClassificationQuestions
    },
    {
      id: 'market-validation',
      title: 'Market Validation',
      description: 'Validate your assumptions with real data',
      icon: Shield,
      duration: '60-90 minutes',
      questions: marketValidationQuestions
    },
    {
      id: 'research-insights',
      title: 'Research Report',
      description: 'Your comprehensive market analysis',
      icon: FileText,
      duration: '10 minutes',
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
    updateProgress('market-research', overallProgress)
    
    // Complete phase if all sections are done
    if (overallProgress >= 100 && !marketResearchData.completed) {
      completePhase('market-research')
    }
  }, [responses])

  const handleResponse = (questionId, answer) => {
    updateResponse('market-research', questionId, answer, currentSection)
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
          {currentSection === 'research-insights' ? (
            <ResearchInsights 
              insights={marketResearchData.insights} 
              competitiveAnalysis={marketResearchData.competitiveAnalysis}
              customerProfiles={marketResearchData.customerProfiles}
              marketValidation={marketResearchData.validation}
            />
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
        <Button 
          onClick={nextSection}
          disabled={currentSectionIndex === sections.length - 1}
        >
          Next
          <ArrowRight className="h-4 w-4 ml-2" />
        </Button>
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

      case 'competitor-analysis':
        return (
          <CompetitorAnalysisInput 
            value={response || []}
            onChange={onResponse}
            maxCompetitors={question.maxCompetitors || 5}
          />
        )

      case 'customer-persona':
        return (
          <CustomerPersonaInput 
            value={response || {}}
            onChange={onResponse}
          />
        )

      case 'stakeholder-map':
        return (
          <StakeholderMapInput 
            value={response || {}}
            onChange={onResponse}
            categories={question.categories}
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

// Competitor Analysis Input Component
const CompetitorAnalysisInput = ({ value, onChange, maxCompetitors }) => {
  const [competitors, setCompetitors] = useState(value || [])

  const addCompetitor = () => {
    if (competitors.length < maxCompetitors) {
      const newCompetitors = [...competitors, {
        name: '',
        description: '',
        strengths: '',
        weaknesses: '',
        marketShare: 1,
        threat: 1
      }]
      setCompetitors(newCompetitors)
      onChange(newCompetitors)
    }
  }

  const updateCompetitor = (index, field, newValue) => {
    const newCompetitors = [...competitors]
    newCompetitors[index][field] = newValue
    setCompetitors(newCompetitors)
    onChange(newCompetitors)
  }

  const removeCompetitor = (index) => {
    const newCompetitors = competitors.filter((_, i) => i !== index)
    setCompetitors(newCompetitors)
    onChange(newCompetitors)
  }

  return (
    <div className="space-y-4">
      {competitors.map((competitor, index) => (
        <Card key={index} className="p-4">
          <div className="flex justify-between items-center mb-3">
            <h4 className="font-semibold">Competitor {index + 1}</h4>
            <Button variant="outline" size="sm" onClick={() => removeCompetitor(index)}>
              Remove
            </Button>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium">Company Name</Label>
              <input
                type="text"
                value={competitor.name}
                onChange={(e) => updateCompetitor(index, 'name', e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded-md"
                placeholder="Enter competitor name"
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Description</Label>
              <input
                type="text"
                value={competitor.description}
                onChange={(e) => updateCompetitor(index, 'description', e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded-md"
                placeholder="What do they do?"
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Key Strengths</Label>
              <Textarea
                value={competitor.strengths}
                onChange={(e) => updateCompetitor(index, 'strengths', e.target.value)}
                className="mt-1"
                rows={2}
                placeholder="What are they good at?"
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Key Weaknesses</Label>
              <Textarea
                value={competitor.weaknesses}
                onChange={(e) => updateCompetitor(index, 'weaknesses', e.target.value)}
                className="mt-1"
                rows={2}
                placeholder="Where do they fall short?"
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Market Share (1-10)</Label>
              <Slider
                value={[competitor.marketShare]}
                onValueChange={(val) => updateCompetitor(index, 'marketShare', val[0])}
                min={1}
                max={10}
                step={1}
                className="mt-2"
              />
              <div className="text-center text-sm mt-1">Score: {competitor.marketShare}</div>
            </div>
            <div>
              <Label className="text-sm font-medium">Threat Level (1-10)</Label>
              <Slider
                value={[competitor.threat]}
                onValueChange={(val) => updateCompetitor(index, 'threat', val[0])}
                min={1}
                max={10}
                step={1}
                className="mt-2"
              />
              <div className="text-center text-sm mt-1">Score: {competitor.threat}</div>
            </div>
          </div>
        </Card>
      ))}
      
      {competitors.length < maxCompetitors && (
        <Button onClick={addCompetitor} variant="outline" className="w-full">
          <Building className="h-4 w-4 mr-2" />
          Add Competitor ({competitors.length}/{maxCompetitors})
        </Button>
      )}
    </div>
  )
}

// Customer Persona Input Component
const CustomerPersonaInput = ({ value, onChange }) => {
  const [persona, setPersona] = useState(value || {
    name: '',
    demographics: '',
    psychographics: '',
    painPoints: '',
    goals: '',
    buyingBehavior: '',
    channels: ''
  })

  const updatePersona = (field, newValue) => {
    const newPersona = { ...persona, [field]: newValue }
    setPersona(newPersona)
    onChange(newPersona)
  }

  return (
    <div className="space-y-4">
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label className="text-sm font-medium">Persona Name</Label>
          <input
            type="text"
            value={persona.name}
            onChange={(e) => updatePersona('name', e.target.value)}
            className="w-full mt-1 px-3 py-2 border rounded-md"
            placeholder="e.g., Tech-Savvy Sarah"
          />
        </div>
        <div>
          <Label className="text-sm font-medium">Demographics</Label>
          <input
            type="text"
            value={persona.demographics}
            onChange={(e) => updatePersona('demographics', e.target.value)}
            className="w-full mt-1 px-3 py-2 border rounded-md"
            placeholder="Age, location, income, etc."
          />
        </div>
      </div>
      
      <div>
        <Label className="text-sm font-medium">Psychographics & Lifestyle</Label>
        <Textarea
          value={persona.psychographics}
          onChange={(e) => updatePersona('psychographics', e.target.value)}
          className="mt-1"
          rows={3}
          placeholder="Values, interests, lifestyle, personality traits..."
        />
      </div>
      
      <div>
        <Label className="text-sm font-medium">Pain Points & Challenges</Label>
        <Textarea
          value={persona.painPoints}
          onChange={(e) => updatePersona('painPoints', e.target.value)}
          className="mt-1"
          rows={3}
          placeholder="What problems do they face? What frustrates them?"
        />
      </div>
      
      <div>
        <Label className="text-sm font-medium">Goals & Aspirations</Label>
        <Textarea
          value={persona.goals}
          onChange={(e) => updatePersona('goals', e.target.value)}
          className="mt-1"
          rows={3}
          placeholder="What do they want to achieve? What motivates them?"
        />
      </div>
      
      <div>
        <Label className="text-sm font-medium">Buying Behavior</Label>
        <Textarea
          value={persona.buyingBehavior}
          onChange={(e) => updatePersona('buyingBehavior', e.target.value)}
          className="mt-1"
          rows={2}
          placeholder="How do they make purchasing decisions? What influences them?"
        />
      </div>
      
      <div>
        <Label className="text-sm font-medium">Preferred Channels</Label>
        <Textarea
          value={persona.channels}
          onChange={(e) => updatePersona('channels', e.target.value)}
          className="mt-1"
          rows={2}
          placeholder="Where do they spend time? How do they prefer to be reached?"
        />
      </div>
    </div>
  )
}

// Stakeholder Map Input Component
const StakeholderMapInput = ({ value, onChange, categories }) => {
  const [stakeholders, setStakeholders] = useState(value || {})

  const updateStakeholder = (category, stakeholder) => {
    const newStakeholders = {
      ...stakeholders,
      [category]: stakeholder
    }
    setStakeholders(newStakeholders)
    onChange(newStakeholders)
  }

  return (
    <div className="space-y-4">
      {categories.map(category => (
        <div key={category.id}>
          <Label className="text-sm font-medium">{category.label}</Label>
          <p className="text-xs text-muted-foreground mb-2">{category.description}</p>
          <Textarea
            value={stakeholders[category.id] || ''}
            onChange={(e) => updateStakeholder(category.id, e.target.value)}
            className="mt-1"
            rows={2}
            placeholder={category.placeholder}
          />
        </div>
      ))}
    </div>
  )
}

// Research Insights Component
const ResearchInsights = ({ insights, competitiveAnalysis, customerProfiles, marketValidation }) => {
  if (!insights) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-lg font-semibold mb-2">Complete Research to See Insights</h3>
        <p className="text-muted-foreground">
          Finish all market research sections to generate your comprehensive market analysis report.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Market Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            Market Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">{insights.marketSize}</div>
              <div className="text-sm text-muted-foreground">Market Size</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">{insights.growthRate}</div>
              <div className="text-sm text-muted-foreground">Growth Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">{insights.competitorCount}</div>
              <div className="text-sm text-muted-foreground">Key Competitors</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Findings */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Market Opportunities</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {insights.opportunities?.map((opportunity, index) => (
                <li key={index} className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                  <span className="text-sm">{opportunity}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Market Challenges</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {insights.challenges?.map((challenge, index) => (
                <li key={index} className="flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 text-orange-500 flex-shrink-0 mt-0.5" />
                  <span className="text-sm">{challenge}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Strategic Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {insights.recommendations?.map((rec, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                <div className="w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </div>
                <div>
                  <h4 className="font-semibold text-sm">{rec.title}</h4>
                  <p className="text-sm text-muted-foreground">{rec.description}</p>
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
const competitiveAnalysisQuestions = [
  {
    id: 'competitor-identification',
    question: 'Identify and analyze your key competitors',
    description: 'List companies that offer similar solutions or compete for the same customers',
    type: 'competitor-analysis',
    required: true,
    maxCompetitors: 5,
    helpText: 'Include both direct competitors (same solution) and indirect competitors (different solution, same problem).'
  },
  {
    id: 'competitive-advantage',
    question: 'What will be your unique competitive advantage?',
    type: 'textarea',
    required: true,
    placeholder: 'Describe what will make you different and better than competitors...',
    helpText: 'Think about your unique combination of features, pricing, service, or approach.'
  },
  {
    id: 'market-positioning',
    question: 'How do you want to position yourself in the market?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'premium', label: 'Premium/Luxury', description: 'High quality, high price, exclusive' },
      { value: 'value', label: 'Value Leader', description: 'Best quality for the price' },
      { value: 'cost', label: 'Cost Leader', description: 'Lowest price in market' },
      { value: 'niche', label: 'Niche Specialist', description: 'Focused on specific segment' },
      { value: 'innovation', label: 'Innovation Leader', description: 'First with new solutions' }
    ],
    helpText: 'Your positioning should align with your target customers and competitive advantages.'
  }
]

const customerResearchQuestions = [
  {
    id: 'primary-persona',
    question: 'Create your primary customer persona',
    description: 'Develop a detailed profile of your most important customer segment',
    type: 'customer-persona',
    required: true,
    helpText: 'Be as specific as possible. This persona should represent your ideal customer.'
  },
  {
    id: 'customer-journey',
    question: 'Describe your customer\'s journey from problem awareness to purchase',
    type: 'textarea',
    required: true,
    placeholder: 'Walk through the steps: awareness → consideration → decision → purchase → onboarding...',
    helpText: 'Understanding this journey helps you identify touchpoints and optimization opportunities.'
  },
  {
    id: 'customer-validation',
    question: 'How will you validate your customer assumptions?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'interviews', label: 'Customer Interviews', description: 'One-on-one conversations' },
      { value: 'surveys', label: 'Online Surveys', description: 'Structured questionnaires' },
      { value: 'focus-groups', label: 'Focus Groups', description: 'Group discussions' },
      { value: 'mvp-testing', label: 'MVP Testing', description: 'Test with minimal product' },
      { value: 'landing-page', label: 'Landing Page Test', description: 'Measure interest/signups' }
    ],
    helpText: 'Choose methods that will give you reliable data about your target customers.'
  }
]

const stakeholderMappingQuestions = [
  {
    id: 'stakeholder-ecosystem',
    question: 'Map your stakeholder ecosystem',
    description: 'Identify all parties that could influence your business success',
    type: 'stakeholder-map',
    required: true,
    categories: [
      {
        id: 'customers',
        label: 'Customers & Users',
        description: 'Who will use and pay for your solution?',
        placeholder: 'End users, decision makers, influencers...'
      },
      {
        id: 'suppliers',
        label: 'Suppliers & Partners',
        description: 'Who will you depend on for resources or capabilities?',
        placeholder: 'Vendors, technology partners, distributors...'
      },
      {
        id: 'regulators',
        label: 'Regulators & Government',
        description: 'What regulatory bodies or government agencies matter?',
        placeholder: 'Industry regulators, local government, licensing bodies...'
      },
      {
        id: 'community',
        label: 'Community & Society',
        description: 'What communities or social groups are affected?',
        placeholder: 'Local community, industry associations, advocacy groups...'
      },
      {
        id: 'investors',
        label: 'Investors & Financiers',
        description: 'Who might provide funding or financial support?',
        placeholder: 'Angel investors, VCs, banks, grants...'
      }
    ],
    helpText: 'Consider both positive and negative stakeholders. Understanding all parties helps you build better relationships and avoid conflicts.'
  }
]

const problemClassificationQuestions = [
  {
    id: 'problem-type',
    question: 'What type of problem are you primarily solving?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'technical', label: 'Technical Problem', description: 'Clear solution exists, needs implementation' },
      { value: 'adaptive', label: 'Adaptive Challenge', description: 'No clear solution, requires learning and experimentation' },
      { value: 'hybrid', label: 'Hybrid Problem', description: 'Mix of technical and adaptive elements' }
    ],
    helpText: 'Technical problems have known solutions. Adaptive challenges require innovation and learning.'
  },
  {
    id: 'problem-urgency',
    question: 'How urgent is this problem for your customers?',
    type: 'scale',
    required: true,
    scaleRange: { min: 1, max: 10 },
    scaleLabels: { min: 'Nice to Have', max: 'Critical/Urgent' },
    helpText: 'Higher urgency typically means customers are more willing to pay and adopt quickly.'
  },
  {
    id: 'problem-frequency',
    question: 'How frequently do customers experience this problem?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'daily', label: 'Daily', description: 'Multiple times per day or every day' },
      { value: 'weekly', label: 'Weekly', description: 'Several times per week' },
      { value: 'monthly', label: 'Monthly', description: 'Several times per month' },
      { value: 'quarterly', label: 'Quarterly', description: 'A few times per year' },
      { value: 'rare', label: 'Rarely', description: 'Once a year or less' }
    ],
    helpText: 'More frequent problems typically create stronger demand for solutions.'
  }
]

const marketValidationQuestions = [
  {
    id: 'validation-methods',
    question: 'What methods will you use to validate market demand?',
    type: 'textarea',
    required: true,
    placeholder: 'Describe your validation approach: surveys, interviews, pre-orders, pilot programs...',
    helpText: 'Plan specific, measurable ways to test if customers actually want your solution.'
  },
  {
    id: 'success-metrics',
    question: 'What metrics will indicate successful market validation?',
    type: 'textarea',
    required: true,
    placeholder: 'Define specific numbers: X% interest rate, Y pre-orders, Z positive interviews...',
    helpText: 'Set clear, measurable criteria for what constitutes validation success.'
  },
  {
    id: 'validation-timeline',
    question: 'What is your timeline for market validation?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: '1-month', label: '1 Month', description: 'Quick validation with existing resources' },
      { value: '3-months', label: '3 Months', description: 'Thorough validation with some investment' },
      { value: '6-months', label: '6 Months', description: 'Comprehensive validation including pilot' },
      { value: '12-months', label: '12+ Months', description: 'Extended validation with full testing' }
    ],
    helpText: 'Balance thoroughness with speed to market. Longer validation reduces risk but delays launch.'
  }
]

export default MarketResearchTools

