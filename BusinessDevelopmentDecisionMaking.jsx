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
  Settings, 
  Target, 
  TrendingUp, 
  CheckCircle, 
  AlertCircle,
  Plus,
  Trash2,
  BarChart3,
  PieChart,
  Lightbulb,
  Star,
  Users,
  DollarSign,
  Building,
  Zap,
  Globe,
  ArrowRight
} from 'lucide-react'
import { useAssessment } from '../../contexts/AssessmentContext'

const BusinessDevelopmentDecisionMaking = () => {
  const { assessmentData, updateAssessmentData } = useAssessment()
  const [currentSection, setCurrentSection] = useState(0)
  const [sectionData, setSectionData] = useState({
    strategicDecisionMatrix: {
      opportunityMapping: {
        serviceOpportunities: [],
        productOpportunities: [],
        hybridOpportunities: []
      },
      marketStrategies: {
        existingProductExistingMarket: { selected: false, description: '', riskLevel: 1, timeframe: '' },
        existingProductNewMarket: { selected: false, description: '', riskLevel: 3, timeframe: '' },
        newProductExistingMarket: { selected: false, description: '', riskLevel: 3, timeframe: '' },
        newProductNewMarket: { selected: false, description: '', riskLevel: 5, timeframe: '' }
      },
      opportunityPrioritization: {
        criteria: [
          { name: 'Market Size', weight: 20, description: '' },
          { name: 'Competition Level', weight: 15, description: '' },
          { name: 'Resource Requirements', weight: 25, description: '' },
          { name: 'Time to Market', weight: 15, description: '' },
          { name: 'Profit Potential', weight: 25, description: '' }
        ],
        opportunities: []
      }
    },
    resourceOpportunityAlignment: {
      currentResources: {
        human: { available: [], description: '', adequacy: 5 },
        financial: { available: '', description: '', adequacy: 5 },
        physical: { available: [], description: '', adequacy: 5 },
        intangible: { available: [], description: '', adequacy: 5 }
      },
      acquirableResources: {
        human: { acquirable: [], timeline: '', cost: '', feasibility: 5 },
        financial: { acquirable: '', timeline: '', cost: '', feasibility: 5 },
        physical: { acquirable: [], timeline: '', cost: '', feasibility: 5 },
        intangible: { acquirable: [], timeline: '', cost: '', feasibility: 5 }
      },
      opportunityClassification: {
        perfectFit: [],
        stretch: [],
        aspirational: []
      },
      resourceGapAnalysis: {
        criticalGaps: [],
        mitigationStrategies: [],
        alternativeApproaches: []
      }
    },
    marketEntryFramework: {
      strategySelection: {
        selectedStrategy: '',
        rationale: '',
        riskAssessment: 5,
        expectedTimeline: ''
      },
      tacticalImplementation: {
        phase1: { activities: [], timeline: '', resources: [], success_metrics: [] },
        phase2: { activities: [], timeline: '', resources: [], success_metrics: [] },
        phase3: { activities: [], timeline: '', resources: [], success_metrics: [] }
      },
      sequencingOptimization: {
        primaryOpportunity: '',
        secondaryOpportunities: [],
        contingencyPlans: [],
        pivotTriggers: []
      }
    }
  })

  const sections = [
    {
      id: 'strategic-decision-matrix',
      title: 'Strategic Business Decision Matrix',
      description: 'Map and evaluate all possible business opportunities',
      icon: Target,
      duration: '3-4 days',
      subsections: [
        { id: 'opportunity-mapping', title: 'Comprehensive Opportunity Mapping', questions: 12 },
        { id: 'market-strategies', title: 'Market Strategy Selection Matrix', questions: 8 },
        { id: 'opportunity-prioritization', title: 'Opportunity Prioritization Scorecard', questions: 10 }
      ]
    },
    {
      id: 'resource-opportunity-alignment',
      title: 'Resource-Opportunity Alignment',
      description: 'Align opportunities with available and acquirable resources',
      icon: Settings,
      duration: '2-3 days',
      subsections: [
        { id: 'current-resources', title: 'Current Resource Inventory', questions: 8 },
        { id: 'acquirable-resources', title: 'Acquirable Resource Assessment', questions: 8 },
        { id: 'opportunity-classification', title: 'Opportunity Classification Framework', questions: 6 },
        { id: 'resource-gap-analysis', title: 'Resource Gap Analysis', questions: 8 }
      ]
    },
    {
      id: 'market-entry-framework',
      title: 'Strategic Market Entry Framework',
      description: 'Choose optimal market entry strategy for each opportunity',
      icon: TrendingUp,
      duration: '2-3 days',
      subsections: [
        { id: 'strategy-selection', title: 'Market Entry Strategy Selection', questions: 6 },
        { id: 'tactical-implementation', title: 'Tactical Implementation Planning', questions: 12 },
        { id: 'sequencing-optimization', title: 'Sequencing and Timing Optimization', questions: 8 }
      ]
    }
  ]

  // Load existing data
  useEffect(() => {
    const existingData = assessmentData['business-development'] || {}
    if (Object.keys(existingData).length > 0) {
      setSectionData({ ...sectionData, ...existingData })
    }
  }, [])

  // Save data when it changes
  useEffect(() => {
    updateAssessmentData('business-development', sectionData)
  }, [sectionData])

  // Calculate completion percentage
  const calculateSectionCompletion = (sectionId) => {
    const section = sections.find(s => s.id === sectionId)
    if (!section) return 0
    
    let totalQuestions = section.subsections.reduce((sum, sub) => sum + sub.questions, 0)
    let answeredQuestions = 0
    
    // Count answered questions based on section data
    const sectionKey = sectionId.replace(/-([a-z])/g, (g) => g[1].toUpperCase())
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

  const addOpportunity = (type) => {
    const newOpportunity = {
      id: Date.now(),
      title: '',
      description: '',
      marketSize: '',
      competition: '',
      resources: '',
      timeline: '',
      profitPotential: ''
    }
    
    const currentOpportunities = sectionData.strategicDecisionMatrix.opportunityMapping[type] || []
    updateSectionData(`strategicDecisionMatrix.opportunityMapping.${type}`, [...currentOpportunities, newOpportunity])
  }

  const removeOpportunity = (type, id) => {
    const currentOpportunities = sectionData.strategicDecisionMatrix.opportunityMapping[type] || []
    const filteredOpportunities = currentOpportunities.filter(opp => opp.id !== id)
    updateSectionData(`strategicDecisionMatrix.opportunityMapping.${type}`, filteredOpportunities)
  }

  const updateOpportunity = (type, id, field, value) => {
    const currentOpportunities = sectionData.strategicDecisionMatrix.opportunityMapping[type] || []
    const updatedOpportunities = currentOpportunities.map(opp => 
      opp.id === id ? { ...opp, [field]: value } : opp
    )
    updateSectionData(`strategicDecisionMatrix.opportunityMapping.${type}`, updatedOpportunities)
  }

  const renderStrategicDecisionMatrixSection = () => (
    <div className="space-y-8">
      {/* Comprehensive Opportunity Mapping */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Comprehensive Opportunity Mapping
          </CardTitle>
          <CardDescription>
            Map all possible business opportunities across service, product, and hybrid models
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="service" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="service">Service Opportunities</TabsTrigger>
              <TabsTrigger value="product">Product Opportunities</TabsTrigger>
              <TabsTrigger value="hybrid">Hybrid Opportunities</TabsTrigger>
            </TabsList>
            
            {['service', 'product', 'hybrid'].map(type => (
              <TabsContent key={type} value={type} className="space-y-4">
                <div className="flex justify-between items-center">
                  <h4 className="font-semibold capitalize">{type} Opportunities</h4>
                  <Button onClick={() => addOpportunity(`${type}Opportunities`)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add {type.charAt(0).toUpperCase() + type.slice(1)} Opportunity
                  </Button>
                </div>
                
                {(sectionData.strategicDecisionMatrix.opportunityMapping[`${type}Opportunities`] || []).map((opportunity, index) => (
                  <Card key={opportunity.id} className="p-4">
                    <div className="flex justify-between items-start mb-4">
                      <h5 className="font-medium">Opportunity #{index + 1}</h5>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => removeOpportunity(`${type}Opportunities`, opportunity.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label>Opportunity Title</Label>
                        <Input
                          placeholder="Brief, descriptive title"
                          value={opportunity.title || ''}
                          onChange={(e) => updateOpportunity(`${type}Opportunities`, opportunity.id, 'title', e.target.value)}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <Label>Market Size Estimate</Label>
                        <Input
                          placeholder="e.g., $50M TAM, 10K potential customers"
                          value={opportunity.marketSize || ''}
                          onChange={(e) => updateOpportunity(`${type}Opportunities`, opportunity.id, 'marketSize', e.target.value)}
                          className="mt-1"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <Label>Opportunity Description</Label>
                        <Textarea
                          placeholder="Detailed description of the business opportunity, target market, and value proposition"
                          value={opportunity.description || ''}
                          onChange={(e) => updateOpportunity(`${type}Opportunities`, opportunity.id, 'description', e.target.value)}
                          className="mt-1 min-h-[80px]"
                        />
                      </div>
                      <div>
                        <Label>Competition Level</Label>
                        <Input
                          placeholder="High/Medium/Low with key competitors"
                          value={opportunity.competition || ''}
                          onChange={(e) => updateOpportunity(`${type}Opportunities`, opportunity.id, 'competition', e.target.value)}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <Label>Resource Requirements</Label>
                        <Input
                          placeholder="Key resources needed (team, capital, etc.)"
                          value={opportunity.resources || ''}
                          onChange={(e) => updateOpportunity(`${type}Opportunities`, opportunity.id, 'resources', e.target.value)}
                          className="mt-1"
                        />
                      </div>
                    </div>
                  </Card>
                ))}
                
                {(sectionData.strategicDecisionMatrix.opportunityMapping[`${type}Opportunities`] || []).length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <Building className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No {type} opportunities added yet.</p>
                    <p className="text-sm">Click "Add {type.charAt(0).toUpperCase() + type.slice(1)} Opportunity" to get started.</p>
                  </div>
                )}
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      {/* Market Strategy Selection Matrix */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Market Strategy Selection Matrix
          </CardTitle>
          <CardDescription>
            Choose your market entry approach using the Ansoff Matrix framework
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              {
                key: 'existingProductExistingMarket',
                title: 'Market Penetration',
                subtitle: 'Existing Product → Existing Market',
                description: 'Grow market share with current products in current markets',
                riskLevel: 1,
                examples: 'Increase marketing, improve customer service, competitive pricing'
              },
              {
                key: 'existingProductNewMarket',
                title: 'Market Development',
                subtitle: 'Existing Product → New Market',
                description: 'Take current products to new markets or customer segments',
                riskLevel: 3,
                examples: 'Geographic expansion, new customer segments, new channels'
              },
              {
                key: 'newProductExistingMarket',
                title: 'Product Development',
                subtitle: 'New Product → Existing Market',
                description: 'Develop new products for current customer base',
                riskLevel: 3,
                examples: 'Product line extensions, new features, complementary products'
              },
              {
                key: 'newProductNewMarket',
                title: 'Diversification',
                subtitle: 'New Product → New Market',
                description: 'Enter completely new markets with new products',
                riskLevel: 5,
                examples: 'Unrelated diversification, new business ventures, acquisitions'
              }
            ].map(strategy => (
              <Card key={strategy.key} className={`p-4 ${sectionData.strategicDecisionMatrix.marketStrategies[strategy.key]?.selected ? 'ring-2 ring-primary' : ''}`}>
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-semibold">{strategy.title}</h4>
                    <p className="text-sm text-muted-foreground">{strategy.subtitle}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={strategy.riskLevel <= 2 ? 'default' : strategy.riskLevel <= 3 ? 'secondary' : 'destructive'}>
                      Risk: {strategy.riskLevel}/5
                    </Badge>
                    <input
                      type="checkbox"
                      checked={sectionData.strategicDecisionMatrix.marketStrategies[strategy.key]?.selected || false}
                      onChange={(e) => updateSectionData(`strategicDecisionMatrix.marketStrategies.${strategy.key}.selected`, e.target.checked)}
                      className="w-4 h-4"
                    />
                  </div>
                </div>
                
                <p className="text-sm text-muted-foreground mb-3">{strategy.description}</p>
                <p className="text-xs text-muted-foreground mb-3">Examples: {strategy.examples}</p>
                
                {sectionData.strategicDecisionMatrix.marketStrategies[strategy.key]?.selected && (
                  <div className="space-y-3 mt-4 pt-4 border-t">
                    <div>
                      <Label className="text-xs">Strategy Description</Label>
                      <Textarea
                        placeholder="Describe how you'll implement this strategy..."
                        value={sectionData.strategicDecisionMatrix.marketStrategies[strategy.key]?.description || ''}
                        onChange={(e) => updateSectionData(`strategicDecisionMatrix.marketStrategies.${strategy.key}.description`, e.target.value)}
                        className="mt-1 min-h-[60px]"
                      />
                    </div>
                    <div>
                      <Label className="text-xs">Expected Timeframe</Label>
                      <Input
                        placeholder="e.g., 6-12 months"
                        value={sectionData.strategicDecisionMatrix.marketStrategies[strategy.key]?.timeframe || ''}
                        onChange={(e) => updateSectionData(`strategicDecisionMatrix.marketStrategies.${strategy.key}.timeframe`, e.target.value)}
                        className="mt-1"
                      />
                    </div>
                  </div>
                )}
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderResourceOpportunityAlignmentSection = () => (
    <div className="space-y-8">
      {/* Current Resource Inventory */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Current Resource Inventory
          </CardTitle>
          <CardDescription>
            Assess your current resources across all categories
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              {
                key: 'human',
                title: 'Human Resources',
                icon: Users,
                placeholder: 'Team members, advisors, network contacts, skills available...',
                examples: 'Co-founders, employees, consultants, mentors, industry contacts'
              },
              {
                key: 'financial',
                title: 'Financial Resources',
                icon: DollarSign,
                placeholder: 'Available capital, funding sources, revenue streams...',
                examples: 'Personal savings, investor funding, loans, grants, revenue'
              },
              {
                key: 'physical',
                title: 'Physical Resources',
                icon: Building,
                placeholder: 'Equipment, facilities, inventory, technology...',
                examples: 'Office space, manufacturing equipment, computers, inventory'
              },
              {
                key: 'intangible',
                title: 'Intangible Resources',
                icon: Zap,
                placeholder: 'Brand, IP, relationships, knowledge, reputation...',
                examples: 'Patents, trademarks, brand recognition, customer relationships'
              }
            ].map(resource => {
              const Icon = resource.icon
              return (
                <Card key={resource.key} className="p-4">
                  <div className="flex items-center gap-2 mb-4">
                    <Icon className="h-5 w-5 text-primary" />
                    <h4 className="font-semibold">{resource.title}</h4>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm">Available Resources</Label>
                      <Textarea
                        placeholder={resource.placeholder}
                        value={sectionData.resourceOpportunityAlignment.currentResources[resource.key]?.description || ''}
                        onChange={(e) => updateSectionData(`resourceOpportunityAlignment.currentResources.${resource.key}.description`, e.target.value)}
                        className="mt-1 min-h-[80px]"
                      />
                      <p className="text-xs text-muted-foreground mt-1">Examples: {resource.examples}</p>
                    </div>
                    
                    <div>
                      <Label className="text-sm">Resource Adequacy (1-10)</Label>
                      <div className="mt-2">
                        <Slider
                          value={[sectionData.resourceOpportunityAlignment.currentResources[resource.key]?.adequacy || 5]}
                          onValueChange={(value) => updateSectionData(`resourceOpportunityAlignment.currentResources.${resource.key}.adequacy`, value[0])}
                          max={10}
                          step={1}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-muted-foreground mt-1">
                          <span>Insufficient</span>
                          <span>{sectionData.resourceOpportunityAlignment.currentResources[resource.key]?.adequacy || 5}/10</span>
                          <span>Excellent</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Opportunity Classification Framework */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Opportunity Classification Framework
          </CardTitle>
          <CardDescription>
            Classify opportunities based on resource-reality alignment
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                key: 'perfectFit',
                title: 'Perfect Fit Opportunities',
                description: 'Opportunities that align perfectly with current resources',
                color: 'border-green-500',
                bgColor: 'bg-green-50 dark:bg-green-950',
                icon: CheckCircle,
                iconColor: 'text-green-600'
              },
              {
                key: 'stretch',
                title: 'Stretch Opportunities',
                description: 'Opportunities requiring some resource acquisition',
                color: 'border-yellow-500',
                bgColor: 'bg-yellow-50 dark:bg-yellow-950',
                icon: AlertCircle,
                iconColor: 'text-yellow-600'
              },
              {
                key: 'aspirational',
                title: 'Aspirational Opportunities',
                description: 'Opportunities requiring significant resource development',
                color: 'border-blue-500',
                bgColor: 'bg-blue-50 dark:bg-blue-950',
                icon: Star,
                iconColor: 'text-blue-600'
              }
            ].map(category => {
              const Icon = category.icon
              return (
                <Card key={category.key} className={`p-4 ${category.color} ${category.bgColor}`}>
                  <div className="flex items-center gap-2 mb-3">
                    <Icon className={`h-5 w-5 ${category.iconColor}`} />
                    <h4 className="font-semibold">{category.title}</h4>
                  </div>
                  
                  <p className="text-sm text-muted-foreground mb-4">{category.description}</p>
                  
                  <Textarea
                    placeholder={`List ${category.title.toLowerCase()} from your opportunity mapping...`}
                    value={sectionData.resourceOpportunityAlignment.opportunityClassification[category.key]?.join('\n') || ''}
                    onChange={(e) => updateSectionData(`resourceOpportunityAlignment.opportunityClassification.${category.key}`, e.target.value.split('\n').filter(item => item.trim()))}
                    className="min-h-[100px]"
                  />
                </Card>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderMarketEntryFrameworkSection = () => (
    <div className="space-y-8">
      {/* Market Entry Strategy Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Market Entry Strategy Selection
          </CardTitle>
          <CardDescription>
            Choose your primary market entry strategy based on analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label>Selected Primary Strategy</Label>
            <RadioGroup 
              value={sectionData.marketEntryFramework.strategySelection.selectedStrategy}
              onValueChange={(value) => updateSectionData('marketEntryFramework.strategySelection.selectedStrategy', value)}
              className="mt-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="market-penetration" id="market-penetration" />
                <Label htmlFor="market-penetration">Market Penetration - Existing Product → Existing Market</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="market-development" id="market-development" />
                <Label htmlFor="market-development">Market Development - Existing Product → New Market</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="product-development" id="product-development" />
                <Label htmlFor="product-development">Product Development - New Product → Existing Market</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="diversification" id="diversification" />
                <Label htmlFor="diversification">Diversification - New Product → New Market</Label>
              </div>
            </RadioGroup>
          </div>

          <div>
            <Label>Strategy Rationale</Label>
            <Textarea
              placeholder="Explain why this strategy is optimal for your situation, considering resources, market conditions, and risk tolerance..."
              value={sectionData.marketEntryFramework.strategySelection.rationale}
              onChange={(e) => updateSectionData('marketEntryFramework.strategySelection.rationale', e.target.value)}
              className="mt-2 min-h-[100px]"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Risk Assessment (1-10)</Label>
              <div className="mt-2">
                <Slider
                  value={[sectionData.marketEntryFramework.strategySelection.riskAssessment]}
                  onValueChange={(value) => updateSectionData('marketEntryFramework.strategySelection.riskAssessment', value[0])}
                  max={10}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>Low Risk</span>
                  <span>{sectionData.marketEntryFramework.strategySelection.riskAssessment}/10</span>
                  <span>High Risk</span>
                </div>
              </div>
            </div>

            <div>
              <Label>Expected Timeline</Label>
              <Input
                placeholder="e.g., 6-18 months to market entry"
                value={sectionData.marketEntryFramework.strategySelection.expectedTimeline}
                onChange={(e) => updateSectionData('marketEntryFramework.strategySelection.expectedTimeline', e.target.value)}
                className="mt-2"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tactical Implementation Planning */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ArrowRight className="h-5 w-5" />
            Tactical Implementation Planning
          </CardTitle>
          <CardDescription>
            Break down your strategy into actionable phases with clear milestones
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                key: 'phase1',
                title: 'Phase 1: Foundation',
                description: 'Initial setup and preparation activities',
                color: 'border-blue-500'
              },
              {
                key: 'phase2',
                title: 'Phase 2: Launch',
                description: 'Market entry and initial customer acquisition',
                color: 'border-green-500'
              },
              {
                key: 'phase3',
                title: 'Phase 3: Growth',
                description: 'Scaling and optimization activities',
                color: 'border-purple-500'
              }
            ].map(phase => (
              <Card key={phase.key} className={`p-4 ${phase.color}`}>
                <h4 className="font-semibold mb-2">{phase.title}</h4>
                <p className="text-sm text-muted-foreground mb-4">{phase.description}</p>
                
                <div className="space-y-3">
                  <div>
                    <Label className="text-xs">Key Activities</Label>
                    <Textarea
                      placeholder="List main activities for this phase..."
                      value={sectionData.marketEntryFramework.tacticalImplementation[phase.key]?.activities?.join('\n') || ''}
                      onChange={(e) => updateSectionData(`marketEntryFramework.tacticalImplementation.${phase.key}.activities`, e.target.value.split('\n').filter(item => item.trim()))}
                      className="mt-1 min-h-[60px]"
                    />
                  </div>
                  
                  <div>
                    <Label className="text-xs">Timeline</Label>
                    <Input
                      placeholder="e.g., Months 1-3"
                      value={sectionData.marketEntryFramework.tacticalImplementation[phase.key]?.timeline || ''}
                      onChange={(e) => updateSectionData(`marketEntryFramework.tacticalImplementation.${phase.key}.timeline`, e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  
                  <div>
                    <Label className="text-xs">Success Metrics</Label>
                    <Textarea
                      placeholder="How will you measure success?"
                      value={sectionData.marketEntryFramework.tacticalImplementation[phase.key]?.success_metrics?.join('\n') || ''}
                      onChange={(e) => updateSectionData(`marketEntryFramework.tacticalImplementation.${phase.key}.success_metrics`, e.target.value.split('\n').filter(item => item.trim()))}
                      className="mt-1 min-h-[40px]"
                    />
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderCurrentSection = () => {
    switch (currentSection) {
      case 0:
        return renderStrategicDecisionMatrixSection()
      case 1:
        return renderResourceOpportunityAlignmentSection()
      case 2:
        return renderMarketEntryFrameworkSection()
      default:
        return renderStrategicDecisionMatrixSection()
    }
  }

  return (
    <div className="space-y-6">
      {/* Section Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
            <h3 className="font-semibold">Business Development & Decision Making Progress</h3>
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

export default BusinessDevelopmentDecisionMaking

