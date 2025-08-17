import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group.jsx'
import { Slider } from '@/components/ui/slider.jsx'
import { 
  TestTube, 
  Users, 
  DollarSign, 
  Target, 
  TrendingUp, 
  CheckCircle, 
  AlertCircle,
  Plus,
  Trash2,
  BarChart3,
  PieChart,
  Lightbulb,
  Star
} from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'

const ProductConceptTesting = () => {
  const { assessmentData, updateAssessmentData } = useAssessment()
  const [currentSection, setCurrentSection] = useState(0)
  const [sectionData, setSectionData] = useState({
    marketAcceptability: {
      testDesign: {
        primaryTarget: 70,
        adjacentSegments: 20,
        edgeCases: 10,
        sampleSize: 100,
        testingMethod: '',
        conceptMaterials: []
      },
      feedbackFramework: {
        effectiveness: '',
        meaning: '',
        usageIntention: '',
        pricingExpectations: '',
        recommendationLikelihood: ''
      },
      crossSegmentValidation: {
        segments: [],
        validationResults: {}
      },
      investmentCriteria: {
        quantitativeThresholds: {
          conceptAppeal: 40,
          purchaseIntent: 30,
          willingnessToPay: '',
          differentiation: 60
        },
        qualitativeIndicators: [],
        riskFactors: []
      }
    },
    priceAcceptability: {
      priceTestingDesign: {
        testingMethod: '',
        pricePoints: [],
        testingMaterials: []
      },
      pricingInsights: {
        bullsEyeTarget: '',
        productPositioning: '',
        optimalPricing: '',
        futureViability: ''
      },
      priceValuePerception: {
        valueAssessment: '',
        behavioralIndicators: [],
        competitiveBenchmarking: ''
      },
      secondaryBenefits: {
        wordOfMouth: [],
        marketingIntelligence: [],
        productDevelopmentInputs: []
      }
    },
    integratedTesting: {
      testingSequence: {
        phase1: { completed: false, insights: '' },
        phase2: { completed: false, insights: '' },
        phase3: { completed: false, insights: '' }
      },
      methodologySelection: {
        qualitativeMethods: [],
        quantitativeMethods: [],
        behavioralMethods: []
      },
      actionableResults: {
        decisionCriteria: [],
        segmentedAnalysis: '',
        iterativeImprovement: ''
      }
    },
    resultsAnalysis: {
      dataAnalysis: {
        quantitativeAnalysis: '',
        qualitativeAnalysis: '',
        integratedInsights: ''
      },
      goNoGoDecision: {
        marketDemand: { score: 0, weight: 30 },
        priceAcceptance: { score: 0, weight: 25 },
        competitivePosition: { score: 0, weight: 25 },
        executionFeasibility: { score: 0, weight: 20 },
        overallScore: 0,
        decision: ''
      },
      conceptOptimization: {
        productRefinement: [],
        pricingOptimization: [],
        marketingOptimization: [],
        implementationPlan: ''
      }
    }
  })

  const sections = [
    {
      id: 'market-acceptability',
      title: 'Market Acceptability Testing',
      description: 'Test product concept appeal with diverse customer segments',
      icon: Users,
      duration: '1-2 weeks',
      subsections: [
        { id: 'test-design', title: 'Test Design & Sample Selection', questions: 8 },
        { id: 'feedback-framework', title: 'Comprehensive Feedback Framework', questions: 12 },
        { id: 'cross-segment', title: 'Cross-Segment Validation', questions: 6 },
        { id: 'investment-criteria', title: 'Investment Decision Criteria', questions: 10 }
      ]
    },
    {
      id: 'price-acceptability',
      title: 'Price Acceptability Testing',
      description: 'Optimize pricing strategy through systematic testing',
      icon: DollarSign,
      duration: '1-2 weeks',
      subsections: [
        { id: 'price-design', title: 'Price Testing Design', questions: 8 },
        { id: 'pricing-insights', title: 'Pricing Insights Framework', questions: 10 },
        { id: 'price-value', title: 'Price-Value Perception', questions: 8 },
        { id: 'secondary-benefits', title: 'Secondary Benefits', questions: 6 }
      ]
    },
    {
      id: 'integrated-testing',
      title: 'Integrated Testing Approach',
      description: 'Combine product and price testing for comprehensive validation',
      icon: Target,
      duration: '2-3 weeks',
      subsections: [
        { id: 'testing-sequence', title: 'Testing Sequence Optimization', questions: 6 },
        { id: 'methodology', title: 'Testing Methodology Selection', questions: 8 },
        { id: 'actionable-results', title: 'Actionable Results Framework', questions: 8 }
      ]
    },
    {
      id: 'results-analysis',
      title: 'Results Analysis & Decision Making',
      description: 'Make evidence-based business decisions using systematic analysis',
      icon: BarChart3,
      duration: '3-4 days',
      subsections: [
        { id: 'data-analysis', title: 'Data Analysis Framework', questions: 6 },
        { id: 'go-no-go', title: 'Go/No-Go Decision Matrix', questions: 8 },
        { id: 'optimization', title: 'Concept Optimization Framework', questions: 10 }
      ]
    }
  ]

  // Load existing data
  useEffect(() => {
    const existingData = assessmentData['product-concept-testing'] || {}
    if (Object.keys(existingData).length > 0) {
      setSectionData({ ...sectionData, ...existingData })
    }
  }, [])

  // Save data when it changes
  useEffect(() => {
    updateAssessmentData('product-concept-testing', sectionData)
  }, [sectionData])

  // Calculate completion percentage
  const calculateSectionCompletion = (sectionId) => {
    const section = sections.find(s => s.id === sectionId)
    if (!section) return 0
    
    let totalQuestions = section.subsections.reduce((sum, sub) => sum + sub.questions, 0)
    let answeredQuestions = 0
    
    // Count answered questions based on section data
    const sectionKey = sectionId.replace('-', '')
    const data = sectionData[sectionKey] || {}
    
    // Simple completion check - count non-empty values
    const countAnswered = (obj) => {
      let count = 0
      Object.values(obj).forEach(value => {
        if (typeof value === 'string' && value.trim()) count++
        else if (typeof value === 'number' && value > 0) count++
        else if (Array.isArray(value) && value.length > 0) count++
        else if (typeof value === 'object' && value !== null) {
          count += countAnswered(value)
        }
      })
      return count
    }
    
    answeredQuestions = countAnswered(data)
    return Math.min((answeredQuestions / totalQuestions) * 100, 100)
  }

  const overallCompletion = sections.reduce((sum, section) => 
    sum + calculateSectionCompletion(section.id), 0) / sections.length

  const updateSectionData = (path, value) => {
    setSectionData(prev => {
      const newData = { ...prev }
      const keys = path.split('.')
      let current = newData
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {}
        current = current[keys[i]]
      }
      
      current[keys[keys.length - 1]] = value
      return newData
    })
  }

  const renderMarketAcceptabilitySection = () => (
    <div className="space-y-8">
      {/* Test Design & Sample Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Test Design & Sample Selection
          </CardTitle>
          <CardDescription>
            Design your product concept test for maximum learning with diverse customer segments
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="primary-target">Primary Target Segment (%)</Label>
              <div className="mt-2">
                <Slider
                  value={[sectionData.marketAcceptability.testDesign.primaryTarget]}
                  onValueChange={(value) => updateSectionData('marketAcceptability.testDesign.primaryTarget', value[0])}
                  max={100}
                  step={5}
                  className="w-full"
                />
                <div className="text-sm text-muted-foreground mt-1">
                  {sectionData.marketAcceptability.testDesign.primaryTarget}% - Core customer segment from Part 4
                </div>
              </div>
            </div>
            <div>
              <Label htmlFor="adjacent-segments">Adjacent Segments (%)</Label>
              <div className="mt-2">
                <Slider
                  value={[sectionData.marketAcceptability.testDesign.adjacentSegments]}
                  onValueChange={(value) => updateSectionData('marketAcceptability.testDesign.adjacentSegments', value[0])}
                  max={50}
                  step={5}
                  className="w-full"
                />
                <div className="text-sm text-muted-foreground mt-1">
                  {sectionData.marketAcceptability.testDesign.adjacentSegments}% - Related segments for expansion
                </div>
              </div>
            </div>
            <div>
              <Label htmlFor="edge-cases">Edge Cases (%)</Label>
              <div className="mt-2">
                <Slider
                  value={[sectionData.marketAcceptability.testDesign.edgeCases]}
                  onValueChange={(value) => updateSectionData('marketAcceptability.testDesign.edgeCases', value[0])}
                  max={20}
                  step={5}
                  className="w-full"
                />
                <div className="text-sm text-muted-foreground mt-1">
                  {sectionData.marketAcceptability.testDesign.edgeCases}% - Outside typical profile
                </div>
              </div>
            </div>
          </div>

          <div>
            <Label htmlFor="sample-size">Target Sample Size</Label>
            <Input
              id="sample-size"
              type="number"
              placeholder="100-300 participants for statistical validity"
              value={sectionData.marketAcceptability.testDesign.sampleSize}
              onChange={(e) => updateSectionData('marketAcceptability.testDesign.sampleSize', parseInt(e.target.value) || 0)}
              className="mt-2"
            />
          </div>

          <div>
            <Label htmlFor="testing-method">Testing Methodology</Label>
            <RadioGroup 
              value={sectionData.marketAcceptability.testDesign.testingMethod}
              onValueChange={(value) => updateSectionData('marketAcceptability.testDesign.testingMethod', value)}
              className="mt-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="monadic" id="monadic" />
                <Label htmlFor="monadic">Monadic Testing - Single concept evaluation</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="sequential" id="sequential" />
                <Label htmlFor="sequential">Sequential Monadic - Multiple concepts in sequence</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="comparative" id="comparative" />
                <Label htmlFor="comparative">Comparative Testing - Direct concept comparison</Label>
              </div>
            </RadioGroup>
          </div>
        </CardContent>
      </Card>

      {/* Comprehensive Feedback Framework */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Star className="h-5 w-5" />
            Comprehensive Feedback Framework
          </CardTitle>
          <CardDescription>
            Systematic approach to gathering valuable customer insights on your product concept
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label htmlFor="effectiveness">Product Effectiveness Assessment</Label>
            <Textarea
              id="effectiveness"
              placeholder="How will you measure product effectiveness? Include rating scales (1-10), specific benefits evaluation, problem-solving capability assessment..."
              value={sectionData.marketAcceptability.feedbackFramework.effectiveness}
              onChange={(e) => updateSectionData('marketAcceptability.feedbackFramework.effectiveness', e.target.value)}
              className="mt-2 min-h-[100px]"
            />
          </div>

          <div>
            <Label htmlFor="meaning">Product Meaning and Relevance</Label>
            <Textarea
              id="meaning"
              placeholder="How will you assess product meaning? Include relevance to customer situation, lifestyle/workflow fit, potential life/work changes..."
              value={sectionData.marketAcceptability.feedbackFramework.meaning}
              onChange={(e) => updateSectionData('marketAcceptability.feedbackFramework.meaning', e.target.value)}
              className="mt-2 min-h-[100px]"
            />
          </div>

          <div>
            <Label htmlFor="usage-intention">Usage Intention Analysis</Label>
            <Textarea
              id="usage-intention"
              placeholder="How will you analyze usage intentions? Include frequency expectations, usage situations, potential stopping factors..."
              value={sectionData.marketAcceptability.feedbackFramework.usageIntention}
              onChange={(e) => updateSectionData('marketAcceptability.feedbackFramework.usageIntention', e.target.value)}
              className="mt-2 min-h-[100px]"
            />
          </div>

          <div>
            <Label htmlFor="pricing-expectations">Pricing Expectations</Label>
            <Textarea
              id="pricing-expectations"
              placeholder="How will you gather pricing expectations? Include expected price range, fair price assessment, price sensitivity thresholds..."
              value={sectionData.marketAcceptability.feedbackFramework.pricingExpectations}
              onChange={(e) => updateSectionData('marketAcceptability.feedbackFramework.pricingExpectations', e.target.value)}
              className="mt-2 min-h-[100px]"
            />
          </div>

          <div>
            <Label htmlFor="recommendation">Recommendation Likelihood</Label>
            <Textarea
              id="recommendation"
              placeholder="How will you measure recommendation likelihood? Include NPS scoring, target audience for recommendations, factors affecting recommendation..."
              value={sectionData.marketAcceptability.feedbackFramework.recommendationLikelihood}
              onChange={(e) => updateSectionData('marketAcceptability.feedbackFramework.recommendationLikelihood', e.target.value)}
              className="mt-2 min-h-[100px]"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderPriceAcceptabilitySection = () => (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Price Testing Design Methodology
          </CardTitle>
          <CardDescription>
            Systematic approach to understanding optimal pricing strategy through customer testing
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label htmlFor="price-testing-method">Price Testing Approach</Label>
            <RadioGroup 
              value={sectionData.priceAcceptability.priceTestingDesign.testingMethod}
              onValueChange={(value) => updateSectionData('priceAcceptability.priceTestingDesign.testingMethod', value)}
              className="mt-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="van-westendorp" id="van-westendorp" />
                <Label htmlFor="van-westendorp">Van Westendorp Price Sensitivity Method</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="sample-sales" id="sample-sales" />
                <Label htmlFor="sample-sales">Sample Sales Testing with Inaugural Price</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="value-bundle" id="value-bundle" />
                <Label htmlFor="value-bundle">Value Bundle Testing</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="competitive-price" id="competitive-price" />
                <Label htmlFor="competitive-price">Competitive Price Testing</Label>
              </div>
            </RadioGroup>
          </div>

          <div>
            <Label>Price Points to Test</Label>
            <div className="mt-2 space-y-2">
              {sectionData.priceAcceptability.priceTestingDesign.pricePoints.map((price, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Input
                    type="number"
                    placeholder="Price point"
                    value={price.value || ''}
                    onChange={(e) => {
                      const newPricePoints = [...sectionData.priceAcceptability.priceTestingDesign.pricePoints]
                      newPricePoints[index] = { ...price, value: e.target.value }
                      updateSectionData('priceAcceptability.priceTestingDesign.pricePoints', newPricePoints)
                    }}
                    className="flex-1"
                  />
                  <Input
                    placeholder="Description (e.g., Premium, Standard, Budget)"
                    value={price.description || ''}
                    onChange={(e) => {
                      const newPricePoints = [...sectionData.priceAcceptability.priceTestingDesign.pricePoints]
                      newPricePoints[index] = { ...price, description: e.target.value }
                      updateSectionData('priceAcceptability.priceTestingDesign.pricePoints', newPricePoints)
                    }}
                    className="flex-1"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      const newPricePoints = sectionData.priceAcceptability.priceTestingDesign.pricePoints.filter((_, i) => i !== index)
                      updateSectionData('priceAcceptability.priceTestingDesign.pricePoints', newPricePoints)
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              <Button
                variant="outline"
                onClick={() => {
                  const newPricePoints = [...sectionData.priceAcceptability.priceTestingDesign.pricePoints, { value: '', description: '' }]
                  updateSectionData('priceAcceptability.priceTestingDesign.pricePoints', newPricePoints)
                }}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Price Point
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderIntegratedTestingSection = () => (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Testing Sequence Optimization
          </CardTitle>
          <CardDescription>
            Three-phase approach for maximum insight generation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">Phase 1: Concept-Only</h4>
                <Badge variant={sectionData.integratedTesting.testingSequence.phase1.completed ? "default" : "secondary"}>
                  Week 1
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Test product concept without price to understand pure product appeal
              </p>
              <Textarea
                placeholder="Document insights from concept-only testing..."
                value={sectionData.integratedTesting.testingSequence.phase1.insights}
                onChange={(e) => updateSectionData('integratedTesting.testingSequence.phase1.insights', e.target.value)}
                className="min-h-[80px]"
              />
            </Card>

            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">Phase 2: Price Introduction</h4>
                <Badge variant={sectionData.integratedTesting.testingSequence.phase2.completed ? "default" : "secondary"}>
                  Week 2
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Introduce pricing to understand price-value relationship
              </p>
              <Textarea
                placeholder="Document insights from price testing..."
                value={sectionData.integratedTesting.testingSequence.phase2.insights}
                onChange={(e) => updateSectionData('integratedTesting.testingSequence.phase2.insights', e.target.value)}
                className="min-h-[80px]"
              />
            </Card>

            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">Phase 3: Purchase Simulation</h4>
                <Badge variant={sectionData.integratedTesting.testingSequence.phase3.completed ? "default" : "secondary"}>
                  Weeks 2-3
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Simulate actual purchase decisions with real commitment
              </p>
              <Textarea
                placeholder="Document insights from purchase simulation..."
                value={sectionData.integratedTesting.testingSequence.phase3.insights}
                onChange={(e) => updateSectionData('integratedTesting.testingSequence.phase3.insights', e.target.value)}
                className="min-h-[80px]"
              />
            </Card>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderResultsAnalysisSection = () => (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Go/No-Go Decision Matrix
          </CardTitle>
          <CardDescription>
            Systematic decision framework with weighted scoring across key criteria
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label>Market Demand (30% weight)</Label>
              <div className="mt-2">
                <Slider
                  value={[sectionData.resultsAnalysis.goNoGoDecision.marketDemand.score]}
                  onValueChange={(value) => updateSectionData('resultsAnalysis.goNoGoDecision.marketDemand.score', value[0])}
                  max={10}
                  step={0.5}
                  className="w-full"
                />
                <div className="text-sm text-muted-foreground mt-1">
                  Score: {sectionData.resultsAnalysis.goNoGoDecision.marketDemand.score}/10
                </div>
              </div>
            </div>

            <div>
              <Label>Price Acceptance (25% weight)</Label>
              <div className="mt-2">
                <Slider
                  value={[sectionData.resultsAnalysis.goNoGoDecision.priceAcceptance.score]}
                  onValueChange={(value) => updateSectionData('resultsAnalysis.goNoGoDecision.priceAcceptance.score', value[0])}
                  max={10}
                  step={0.5}
                  className="w-full"
                />
                <div className="text-sm text-muted-foreground mt-1">
                  Score: {sectionData.resultsAnalysis.goNoGoDecision.priceAcceptance.score}/10
                </div>
              </div>
            </div>

            <div>
              <Label>Competitive Position (25% weight)</Label>
              <div className="mt-2">
                <Slider
                  value={[sectionData.resultsAnalysis.goNoGoDecision.competitivePosition.score]}
                  onValueChange={(value) => updateSectionData('resultsAnalysis.goNoGoDecision.competitivePosition.score', value[0])}
                  max={10}
                  step={0.5}
                  className="w-full"
                />
                <div className="text-sm text-muted-foreground mt-1">
                  Score: {sectionData.resultsAnalysis.goNoGoDecision.competitivePosition.score}/10
                </div>
              </div>
            </div>

            <div>
              <Label>Execution Feasibility (20% weight)</Label>
              <div className="mt-2">
                <Slider
                  value={[sectionData.resultsAnalysis.goNoGoDecision.executionFeasibility.score]}
                  onValueChange={(value) => updateSectionData('resultsAnalysis.goNoGoDecision.executionFeasibility.score', value[0])}
                  max={10}
                  step={0.5}
                  className="w-full"
                />
                <div className="text-sm text-muted-foreground mt-1">
                  Score: {sectionData.resultsAnalysis.goNoGoDecision.executionFeasibility.score}/10
                </div>
              </div>
            </div>
          </div>

          {/* Calculate overall score */}
          {(() => {
            const overallScore = (
              sectionData.resultsAnalysis.goNoGoDecision.marketDemand.score * 0.30 +
              sectionData.resultsAnalysis.goNoGoDecision.priceAcceptance.score * 0.25 +
              sectionData.resultsAnalysis.goNoGoDecision.competitivePosition.score * 0.25 +
              sectionData.resultsAnalysis.goNoGoDecision.executionFeasibility.score * 0.20
            ).toFixed(1)

            let decision = ''
            let decisionColor = ''
            if (overallScore >= 7.0) {
              decision = 'Strong GO - Proceed with confidence'
              decisionColor = 'text-green-600'
            } else if (overallScore >= 5.0) {
              decision = 'Conditional GO - Proceed with modifications'
              decisionColor = 'text-yellow-600'
            } else {
              decision = 'NO GO - Pivot or abandon'
              decisionColor = 'text-red-600'
            }

            return (
              <div className="mt-6 p-4 bg-muted rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold">Overall Decision Score</h4>
                  <Badge variant="outline" className="text-lg">
                    {overallScore}/10
                  </Badge>
                </div>
                <div className={`font-semibold ${decisionColor}`}>
                  {decision}
                </div>
                <Progress value={overallScore * 10} className="mt-2" />
              </div>
            )
          })()}
        </CardContent>
      </Card>
    </div>
  )

  const renderCurrentSection = () => {
    switch (currentSection) {
      case 0:
        return renderMarketAcceptabilitySection()
      case 1:
        return renderPriceAcceptabilitySection()
      case 2:
        return renderIntegratedTestingSection()
      case 3:
        return renderResultsAnalysisSection()
      default:
        return renderMarketAcceptabilitySection()
    }
  }

  return (
    <div className="space-y-6">
      {/* Section Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {sections.map((section, index) => {
          const Icon = section.icon
          const completion = calculateSectionCompletion(section.id)
          const isActive = currentSection === index

          return (
            <Card 
              key={section.id}
              className={`cursor-pointer transition-all duration-300 ${
                isActive ? 'ring-2 ring-primary' : 'hover:shadow-lg'
              }`}
              onClick={() => setCurrentSection(index)}
            >
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <Icon className="h-5 w-5 text-primary" />
                  {completion === 100 && <CheckCircle className="h-4 w-4 text-green-500" />}
                </div>
                <h3 className="font-semibold text-sm mb-1">{section.title}</h3>
                <p className="text-xs text-muted-foreground mb-2">{section.description}</p>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span>{Math.round(completion)}% complete</span>
                    <Badge variant="secondary" className="text-xs">
                      {section.duration}
                    </Badge>
                  </div>
                  <Progress value={completion} className="h-1" />
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Overall Progress */}
      <Card>
        <CardContent className="p-4">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">Product Concept Testing Progress</h3>
            <span className="text-sm text-muted-foreground">{Math.round(overallCompletion)}% Complete</span>
          </div>
          <Progress value={overallCompletion} className="h-2" />
        </CardContent>
      </Card>

      {/* Current Section Content */}
      <div>
        {renderCurrentSection()}
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={() => setCurrentSection(Math.max(0, currentSection - 1))}
          disabled={currentSection === 0}
        >
          Previous Section
        </Button>
        <Button
          onClick={() => setCurrentSection(Math.min(sections.length - 1, currentSection + 1))}
          disabled={currentSection === sections.length - 1}
        >
          Next Section
        </Button>
      </div>
    </div>
  )
}

export default ProductConceptTesting

