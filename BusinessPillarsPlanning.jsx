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
  Building2, 
  Users, 
  TrendingUp, 
  Target, 
  DollarSign, 
  Layers,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  AlertCircle,
  PieChart,
  BarChart3,
  Zap,
  Shield,
  Clock,
  Award,
  Lightbulb,
  Calculator,
  FileText,
  Briefcase,
  Globe,
  Heart,
  Star,
  Rocket,
  Settings,
  TrendingDown,
  Plus,
  Minus
} from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'

const BusinessPillarsPlanning = () => {
  const { 
    assessmentData, 
    updateResponse, 
    updateProgress, 
    completePhase 
  } = useAssessment()
  
  const [currentSection, setCurrentSection] = useState('customer-segmentation')
  const [sectionProgress, setSectionProgress] = useState({})
  
  const businessPillarsData = assessmentData['business-pillars'] || {}
  const responses = businessPillarsData.responses || {}

  // Assessment sections configuration
  const sections = [
    {
      id: 'customer-segmentation',
      title: 'Customer Segmentation',
      description: 'Define and prioritize your target customer segments',
      icon: Users,
      duration: '45-60 minutes',
      questions: customerSegmentationQuestions
    },
    {
      id: 'value-proposition',
      title: 'Value Proposition',
      description: 'Craft compelling value propositions for each segment',
      icon: Star,
      duration: '30-45 minutes',
      questions: valuePropositionQuestions
    },
    {
      id: 'business-model',
      title: 'Business Model',
      description: 'Design your revenue streams and cost structure',
      icon: Building2,
      duration: '60-90 minutes',
      questions: businessModelQuestions
    },
    {
      id: 'financial-planning',
      title: 'Financial Planning',
      description: 'Project revenues, costs, and funding requirements',
      icon: Calculator,
      duration: '90-120 minutes',
      questions: financialPlanningQuestions
    },
    {
      id: 'operational-strategy',
      title: 'Operations Strategy',
      description: 'Plan your key activities, resources, and partnerships',
      icon: Settings,
      duration: '60-75 minutes',
      questions: operationalStrategyQuestions
    },
    {
      id: 'go-to-market',
      title: 'Go-to-Market Strategy',
      description: 'Plan your launch and customer acquisition strategy',
      icon: Rocket,
      duration: '45-60 minutes',
      questions: goToMarketQuestions
    },
    {
      id: 'business-plan',
      title: 'Business Plan Summary',
      description: 'Your comprehensive business plan overview',
      icon: FileText,
      duration: '15 minutes',
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
    updateProgress('business-pillars', overallProgress)
    
    // Complete phase if all sections are done
    if (overallProgress >= 100 && !businessPillarsData.completed) {
      completePhase('business-pillars')
    }
  }, [responses])

  const handleResponse = (questionId, answer) => {
    updateResponse('business-pillars', questionId, answer, currentSection)
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
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
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
          {currentSection === 'business-plan' ? (
            <BusinessPlanSummary 
              businessPlan={businessPillarsData.businessPlan} 
              customerSegments={businessPillarsData.customerSegments}
              valuePropositions={businessPillarsData.valuePropositions}
              businessModel={businessPillarsData.businessModel}
              financialProjections={businessPillarsData.financialProjections}
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

      case 'customer-segments':
        return (
          <CustomerSegmentsInput 
            value={response || []}
            onChange={onResponse}
            maxSegments={question.maxSegments || 3}
          />
        )

      case 'value-proposition-canvas':
        return (
          <ValuePropositionCanvas 
            value={response || {}}
            onChange={onResponse}
          />
        )

      case 'business-model-canvas':
        return (
          <BusinessModelCanvas 
            value={response || {}}
            onChange={onResponse}
          />
        )

      case 'financial-projections':
        return (
          <FinancialProjectionsInput 
            value={response || {}}
            onChange={onResponse}
          />
        )

      case 'resource-planning':
        return (
          <ResourcePlanningInput 
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

// Customer Segments Input Component
const CustomerSegmentsInput = ({ value, onChange, maxSegments }) => {
  const [segments, setSegments] = useState(value || [])

  const addSegment = () => {
    if (segments.length < maxSegments) {
      const newSegments = [...segments, {
        name: '',
        description: '',
        size: '',
        painPoints: '',
        willingness: 1,
        accessibility: 1
      }]
      setSegments(newSegments)
      onChange(newSegments)
    }
  }

  const updateSegment = (index, field, newValue) => {
    const newSegments = [...segments]
    newSegments[index][field] = newValue
    setSegments(newSegments)
    onChange(newSegments)
  }

  const removeSegment = (index) => {
    const newSegments = segments.filter((_, i) => i !== index)
    setSegments(newSegments)
    onChange(newSegments)
  }

  return (
    <div className="space-y-4">
      {segments.map((segment, index) => (
        <Card key={index} className="p-4">
          <div className="flex justify-between items-center mb-3">
            <h4 className="font-semibold">Customer Segment {index + 1}</h4>
            <Button variant="outline" size="sm" onClick={() => removeSegment(index)}>
              Remove
            </Button>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium">Segment Name</Label>
              <input
                type="text"
                value={segment.name}
                onChange={(e) => updateSegment(index, 'name', e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded-md"
                placeholder="e.g., Small Business Owners"
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Market Size</Label>
              <input
                type="text"
                value={segment.size}
                onChange={(e) => updateSegment(index, 'size', e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded-md"
                placeholder="e.g., 500K businesses in US"
              />
            </div>
            <div className="md:col-span-2">
              <Label className="text-sm font-medium">Description</Label>
              <Textarea
                value={segment.description}
                onChange={(e) => updateSegment(index, 'description', e.target.value)}
                className="mt-1"
                rows={2}
                placeholder="Describe this customer segment..."
              />
            </div>
            <div className="md:col-span-2">
              <Label className="text-sm font-medium">Key Pain Points</Label>
              <Textarea
                value={segment.painPoints}
                onChange={(e) => updateSegment(index, 'painPoints', e.target.value)}
                className="mt-1"
                rows={2}
                placeholder="What problems do they face?"
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Willingness to Pay (1-10)</Label>
              <Slider
                value={[segment.willingness]}
                onValueChange={(val) => updateSegment(index, 'willingness', val[0])}
                min={1}
                max={10}
                step={1}
                className="mt-2"
              />
              <div className="text-center text-sm mt-1">Score: {segment.willingness}</div>
            </div>
            <div>
              <Label className="text-sm font-medium">Market Accessibility (1-10)</Label>
              <Slider
                value={[segment.accessibility]}
                onValueChange={(val) => updateSegment(index, 'accessibility', val[0])}
                min={1}
                max={10}
                step={1}
                className="mt-2"
              />
              <div className="text-center text-sm mt-1">Score: {segment.accessibility}</div>
            </div>
          </div>
        </Card>
      ))}
      
      {segments.length < maxSegments && (
        <Button onClick={addSegment} variant="outline" className="w-full">
          <Plus className="h-4 w-4 mr-2" />
          Add Customer Segment ({segments.length}/{maxSegments})
        </Button>
      )}
    </div>
  )
}

// Value Proposition Canvas Component
const ValuePropositionCanvas = ({ value, onChange }) => {
  const [canvas, setCanvas] = useState(value || {
    customerJobs: '',
    painPoints: '',
    gains: '',
    products: '',
    painRelievers: '',
    gainCreators: ''
  })

  const updateCanvas = (field, newValue) => {
    const newCanvas = { ...canvas, [field]: newValue }
    setCanvas(newCanvas)
    onChange(newCanvas)
  }

  const canvasFields = [
    { key: 'customerJobs', label: 'Customer Jobs', placeholder: 'What jobs is your customer trying to get done?' },
    { key: 'painPoints', label: 'Pain Points', placeholder: 'What pains are your customers experiencing?' },
    { key: 'gains', label: 'Customer Gains', placeholder: 'What gains do your customers want?' },
    { key: 'products', label: 'Products & Services', placeholder: 'What products and services do you offer?' },
    { key: 'painRelievers', label: 'Pain Relievers', placeholder: 'How do your products relieve customer pains?' },
    { key: 'gainCreators', label: 'Gain Creators', placeholder: 'How do your products create customer gains?' }
  ]

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div className="space-y-4">
        <h4 className="font-semibold text-center">Customer Profile</h4>
        {canvasFields.slice(0, 3).map(field => (
          <div key={field.key}>
            <Label className="text-sm font-medium">{field.label}</Label>
            <Textarea
              value={canvas[field.key]}
              onChange={(e) => updateCanvas(field.key, e.target.value)}
              className="mt-1"
              rows={3}
              placeholder={field.placeholder}
            />
          </div>
        ))}
      </div>
      <div className="space-y-4">
        <h4 className="font-semibold text-center">Value Map</h4>
        {canvasFields.slice(3, 6).map(field => (
          <div key={field.key}>
            <Label className="text-sm font-medium">{field.label}</Label>
            <Textarea
              value={canvas[field.key]}
              onChange={(e) => updateCanvas(field.key, e.target.value)}
              className="mt-1"
              rows={3}
              placeholder={field.placeholder}
            />
          </div>
        ))}
      </div>
    </div>
  )
}

// Business Model Canvas Component
const BusinessModelCanvas = ({ value, onChange }) => {
  const [canvas, setCanvas] = useState(value || {
    keyPartners: '',
    keyActivities: '',
    keyResources: '',
    valuePropositions: '',
    customerRelationships: '',
    channels: '',
    customerSegments: '',
    costStructure: '',
    revenueStreams: ''
  })

  const updateCanvas = (field, newValue) => {
    const newCanvas = { ...canvas, [field]: newValue }
    setCanvas(newCanvas)
    onChange(newCanvas)
  }

  const canvasFields = [
    { key: 'keyPartners', label: 'Key Partners', placeholder: 'Who are your key partners and suppliers?' },
    { key: 'keyActivities', label: 'Key Activities', placeholder: 'What key activities does your value proposition require?' },
    { key: 'keyResources', label: 'Key Resources', placeholder: 'What key resources does your value proposition require?' },
    { key: 'valuePropositions', label: 'Value Propositions', placeholder: 'What value do you deliver to customers?' },
    { key: 'customerRelationships', label: 'Customer Relationships', placeholder: 'What type of relationship do you establish?' },
    { key: 'channels', label: 'Channels', placeholder: 'Through which channels do you reach customers?' },
    { key: 'customerSegments', label: 'Customer Segments', placeholder: 'For whom are you creating value?' },
    { key: 'costStructure', label: 'Cost Structure', placeholder: 'What are the most important costs?' },
    { key: 'revenueStreams', label: 'Revenue Streams', placeholder: 'For what value are customers willing to pay?' }
  ]

  return (
    <div className="grid md:grid-cols-3 gap-4">
      {canvasFields.map(field => (
        <div key={field.key}>
          <Label className="text-sm font-medium">{field.label}</Label>
          <Textarea
            value={canvas[field.key]}
            onChange={(e) => updateCanvas(field.key, e.target.value)}
            className="mt-1"
            rows={3}
            placeholder={field.placeholder}
          />
        </div>
      ))}
    </div>
  )
}

// Financial Projections Input Component
const FinancialProjectionsInput = ({ value, onChange }) => {
  const [projections, setProjections] = useState(value || {
    year1Revenue: '',
    year2Revenue: '',
    year3Revenue: '',
    initialCosts: '',
    monthlyOperatingCosts: '',
    fundingNeeded: '',
    breakEvenMonth: '',
    pricingModel: '',
    revenueAssumptions: ''
  })

  const updateProjections = (field, newValue) => {
    const newProjections = { ...projections, [field]: newValue }
    setProjections(newProjections)
    onChange(newProjections)
  }

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-3 gap-4">
        <div>
          <Label className="text-sm font-medium">Year 1 Revenue ($)</Label>
          <input
            type="number"
            value={projections.year1Revenue}
            onChange={(e) => updateProjections('year1Revenue', e.target.value)}
            className="w-full mt-1 px-3 py-2 border rounded-md"
            placeholder="100000"
          />
        </div>
        <div>
          <Label className="text-sm font-medium">Year 2 Revenue ($)</Label>
          <input
            type="number"
            value={projections.year2Revenue}
            onChange={(e) => updateProjections('year2Revenue', e.target.value)}
            className="w-full mt-1 px-3 py-2 border rounded-md"
            placeholder="250000"
          />
        </div>
        <div>
          <Label className="text-sm font-medium">Year 3 Revenue ($)</Label>
          <input
            type="number"
            value={projections.year3Revenue}
            onChange={(e) => updateProjections('year3Revenue', e.target.value)}
            className="w-full mt-1 px-3 py-2 border rounded-md"
            placeholder="500000"
          />
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label className="text-sm font-medium">Initial Startup Costs ($)</Label>
          <input
            type="number"
            value={projections.initialCosts}
            onChange={(e) => updateProjections('initialCosts', e.target.value)}
            className="w-full mt-1 px-3 py-2 border rounded-md"
            placeholder="50000"
          />
        </div>
        <div>
          <Label className="text-sm font-medium">Monthly Operating Costs ($)</Label>
          <input
            type="number"
            value={projections.monthlyOperatingCosts}
            onChange={(e) => updateProjections('monthlyOperatingCosts', e.target.value)}
            className="w-full mt-1 px-3 py-2 border rounded-md"
            placeholder="10000"
          />
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label className="text-sm font-medium">Total Funding Needed ($)</Label>
          <input
            type="number"
            value={projections.fundingNeeded}
            onChange={(e) => updateProjections('fundingNeeded', e.target.value)}
            className="w-full mt-1 px-3 py-2 border rounded-md"
            placeholder="100000"
          />
        </div>
        <div>
          <Label className="text-sm font-medium">Break-Even Month</Label>
          <input
            type="number"
            value={projections.breakEvenMonth}
            onChange={(e) => updateProjections('breakEvenMonth', e.target.value)}
            className="w-full mt-1 px-3 py-2 border rounded-md"
            placeholder="18"
          />
        </div>
      </div>

      <div>
        <Label className="text-sm font-medium">Pricing Model</Label>
        <Textarea
          value={projections.pricingModel}
          onChange={(e) => updateProjections('pricingModel', e.target.value)}
          className="mt-1"
          rows={2}
          placeholder="Describe your pricing strategy and model..."
        />
      </div>

      <div>
        <Label className="text-sm font-medium">Revenue Assumptions</Label>
        <Textarea
          value={projections.revenueAssumptions}
          onChange={(e) => updateProjections('revenueAssumptions', e.target.value)}
          className="mt-1"
          rows={3}
          placeholder="Explain the key assumptions behind your revenue projections..."
        />
      </div>
    </div>
  )
}

// Resource Planning Input Component
const ResourcePlanningInput = ({ value, onChange, categories }) => {
  const [resources, setResources] = useState(value || {})

  const updateResource = (category, resource) => {
    const newResources = {
      ...resources,
      [category]: resource
    }
    setResources(newResources)
    onChange(newResources)
  }

  return (
    <div className="space-y-4">
      {categories.map(category => (
        <div key={category.id}>
          <Label className="text-sm font-medium">{category.label}</Label>
          <p className="text-xs text-muted-foreground mb-2">{category.description}</p>
          <Textarea
            value={resources[category.id] || ''}
            onChange={(e) => updateResource(category.id, e.target.value)}
            className="mt-1"
            rows={3}
            placeholder={category.placeholder}
          />
        </div>
      ))}
    </div>
  )
}

// Business Plan Summary Component
const BusinessPlanSummary = ({ businessPlan, customerSegments, valuePropositions, businessModel, financialProjections }) => {
  if (!businessPlan) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-lg font-semibold mb-2">Complete All Sections to Generate Business Plan</h3>
        <p className="text-muted-foreground">
          Finish all business pillars sections to generate your comprehensive business plan summary.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Executive Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            {businessPlan.executiveSummary || 'Complete all sections to generate your executive summary.'}
          </p>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-primary">{businessPlan.targetMarketSize || 'TBD'}</div>
            <div className="text-sm text-muted-foreground">Target Market Size</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-primary">${businessPlan.year3Revenue || 'TBD'}</div>
            <div className="text-sm text-muted-foreground">Year 3 Revenue</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-primary">${businessPlan.fundingNeeded || 'TBD'}</div>
            <div className="text-sm text-muted-foreground">Funding Needed</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-primary">{businessPlan.breakEvenMonth || 'TBD'} mo</div>
            <div className="text-sm text-muted-foreground">Break-Even</div>
          </CardContent>
        </Card>
      </div>

      {/* Business Model Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Business Model Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold mb-2">Value Proposition</h4>
              <p className="text-sm text-muted-foreground">
                {businessPlan.valueProposition || 'Complete value proposition section to see summary.'}
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Revenue Model</h4>
              <p className="text-sm text-muted-foreground">
                {businessPlan.revenueModel || 'Complete business model section to see summary.'}
              </p>
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
            {businessPlan.nextSteps?.map((step, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                <div className="w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </div>
                <div>
                  <h4 className="font-semibold text-sm">{step.title}</h4>
                  <p className="text-sm text-muted-foreground">{step.description}</p>
                </div>
              </div>
            )) || (
              <p className="text-muted-foreground">Complete all sections to see personalized next steps.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Question definitions
const customerSegmentationQuestions = [
  {
    id: 'target-segments',
    question: 'Define your primary customer segments',
    description: 'Identify and describe the different groups of customers you plan to serve',
    type: 'customer-segments',
    required: true,
    maxSegments: 3,
    helpText: 'Focus on 2-3 segments maximum. Quality over quantity - it\'s better to serve fewer segments well.'
  },
  {
    id: 'segment-priority',
    question: 'Which customer segment will you focus on first?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'segment-1', label: 'Segment 1', description: 'Your first defined segment' },
      { value: 'segment-2', label: 'Segment 2', description: 'Your second defined segment' },
      { value: 'segment-3', label: 'Segment 3', description: 'Your third defined segment' }
    ],
    helpText: 'Choose the segment with the highest combination of need, willingness to pay, and accessibility.'
  }
]

const valuePropositionQuestions = [
  {
    id: 'value-proposition-canvas',
    question: 'Create your value proposition canvas',
    description: 'Map how your products and services create value for customers',
    type: 'value-proposition-canvas',
    required: true,
    helpText: 'Focus on the fit between what customers want and what you offer. Be specific and concrete.'
  },
  {
    id: 'unique-selling-proposition',
    question: 'What is your unique selling proposition (USP)?',
    type: 'textarea',
    required: true,
    placeholder: 'In one clear sentence, what makes you uniquely valuable to customers?',
    helpText: 'Your USP should be clear, specific, and differentiate you from competitors.'
  }
]

const businessModelQuestions = [
  {
    id: 'business-model-canvas',
    question: 'Complete your business model canvas',
    description: 'Design the key components of your business model',
    type: 'business-model-canvas',
    required: true,
    helpText: 'Think about how all the pieces fit together to create and deliver value profitably.'
  },
  {
    id: 'revenue-model',
    question: 'What is your primary revenue model?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'subscription', label: 'Subscription', description: 'Recurring monthly/annual fees' },
      { value: 'transaction', label: 'Transaction-based', description: 'Fee per transaction or sale' },
      { value: 'product-sales', label: 'Product Sales', description: 'One-time product purchases' },
      { value: 'service-fees', label: 'Service Fees', description: 'Fees for professional services' },
      { value: 'advertising', label: 'Advertising', description: 'Revenue from ads or sponsorships' },
      { value: 'freemium', label: 'Freemium', description: 'Free basic, paid premium features' }
    ],
    helpText: 'Choose the model that best aligns with your value proposition and customer preferences.'
  }
]

const financialPlanningQuestions = [
  {
    id: 'financial-projections',
    question: 'Create your financial projections',
    description: 'Project your revenues, costs, and funding requirements',
    type: 'financial-projections',
    required: true,
    helpText: 'Be realistic but optimistic. Base projections on market research and comparable businesses.'
  },
  {
    id: 'funding-strategy',
    question: 'How do you plan to fund your business?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'bootstrap', label: 'Bootstrap', description: 'Self-funded from personal savings' },
      { value: 'friends-family', label: 'Friends & Family', description: 'Funding from personal network' },
      { value: 'angel-investors', label: 'Angel Investors', description: 'Individual investor funding' },
      { value: 'venture-capital', label: 'Venture Capital', description: 'Professional VC funding' },
      { value: 'bank-loan', label: 'Bank Loan', description: 'Traditional debt financing' },
      { value: 'crowdfunding', label: 'Crowdfunding', description: 'Platform-based funding' }
    ],
    helpText: 'Consider your funding needs, timeline, and willingness to give up equity.'
  }
]

const operationalStrategyQuestions = [
  {
    id: 'key-resources',
    question: 'What are your key resources and capabilities?',
    type: 'resource-planning',
    required: true,
    categories: [
      {
        id: 'human-resources',
        label: 'Human Resources',
        description: 'Key team members and skills needed',
        placeholder: 'Founders, employees, advisors, consultants...'
      },
      {
        id: 'physical-resources',
        label: 'Physical Resources',
        description: 'Equipment, facilities, and physical assets',
        placeholder: 'Office space, equipment, inventory, manufacturing...'
      },
      {
        id: 'intellectual-resources',
        label: 'Intellectual Resources',
        description: 'IP, data, and knowledge assets',
        placeholder: 'Patents, trademarks, proprietary data, algorithms...'
      },
      {
        id: 'financial-resources',
        label: 'Financial Resources',
        description: 'Capital and financial assets needed',
        placeholder: 'Startup capital, working capital, credit lines...'
      }
    ],
    helpText: 'Focus on the resources that are most critical to your value proposition and competitive advantage.'
  },
  {
    id: 'key-partnerships',
    question: 'What key partnerships will you need?',
    type: 'textarea',
    required: true,
    placeholder: 'Describe strategic partnerships, suppliers, distributors, or other key relationships...',
    helpText: 'Think about partnerships that can help you access resources, capabilities, or markets more effectively.'
  }
]

const goToMarketQuestions = [
  {
    id: 'customer-acquisition',
    question: 'How will you acquire your first customers?',
    type: 'textarea',
    required: true,
    placeholder: 'Describe your customer acquisition strategy and tactics...',
    helpText: 'Be specific about channels, tactics, and how you\'ll measure success.'
  },
  {
    id: 'marketing-channels',
    question: 'What marketing channels will you use?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: 'digital-marketing', label: 'Digital Marketing', description: 'SEO, SEM, social media, content' },
      { value: 'direct-sales', label: 'Direct Sales', description: 'Personal selling and relationship building' },
      { value: 'partnerships', label: 'Channel Partners', description: 'Resellers, distributors, affiliates' },
      { value: 'referrals', label: 'Referral Program', description: 'Word-of-mouth and customer referrals' },
      { value: 'events', label: 'Events & Trade Shows', description: 'Industry events and networking' },
      { value: 'pr-media', label: 'PR & Media', description: 'Public relations and media coverage' }
    ],
    helpText: 'Choose channels where your target customers are most active and receptive.'
  },
  {
    id: 'launch-timeline',
    question: 'What is your launch timeline?',
    type: 'multiple-choice',
    required: true,
    options: [
      { value: '3-months', label: '3 Months', description: 'Quick launch with MVP' },
      { value: '6-months', label: '6 Months', description: 'Moderate development timeline' },
      { value: '12-months', label: '12 Months', description: 'Comprehensive product development' },
      { value: '18-months', label: '18+ Months', description: 'Complex product or regulatory requirements' }
    ],
    helpText: 'Balance speed to market with product readiness and market preparation.'
  }
]

export default BusinessPillarsPlanning

