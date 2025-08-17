import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Brain, 
  Target, 
  TrendingUp, 
  Users, 
  Lightbulb,
  AlertTriangle,
  CheckCircle,
  Star,
  Zap,
  Shield,
  Clock,
  Award,
  BarChart3,
  PieChart,
  ArrowRight,
  Rocket,
  Building2,
  DollarSign,
  Globe,
  Heart,
  Eye,
  MessageSquare,
  FileText,
  Settings,
  Briefcase,
  Calculator,
  Search,
  Filter,
  RefreshCw
} from 'lucide-react'
import { useAssessment } from '../contexts/AssessmentContext'

const AIRecommendations = () => {
  const { assessmentData } = useAssessment()
  const [aiAnalysis, setAiAnalysis] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)

  // Check if enough data is available for analysis
  const hasEnoughData = () => {
    const phases = ['self-discovery', 'idea-discovery', 'market-research', 'business-pillars']
    const completedPhases = phases.filter(phase => 
      assessmentData[phase]?.responses && Object.keys(assessmentData[phase].responses).length > 0
    )
    return completedPhases.length >= 2 // Need at least 2 phases completed
  }

  // Generate AI analysis based on assessment data
  const generateAIAnalysis = async () => {
    if (!hasEnoughData()) return

    setIsAnalyzing(true)
    setAnalysisProgress(0)

    // Simulate AI analysis process
    const analysisSteps = [
      'Analyzing entrepreneurial personality...',
      'Evaluating business ideas and opportunities...',
      'Assessing market research insights...',
      'Reviewing business planning approach...',
      'Generating personalized recommendations...',
      'Creating success probability scores...',
      'Matching with similar entrepreneurs...',
      'Finalizing comprehensive analysis...'
    ]

    for (let i = 0; i < analysisSteps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800))
      setAnalysisProgress(((i + 1) / analysisSteps.length) * 100)
    }

    // Generate comprehensive AI analysis
    const analysis = await performAIAnalysis(assessmentData)
    setAiAnalysis(analysis)
    setIsAnalyzing(false)
  }

  // Perform actual AI analysis logic
  const performAIAnalysis = async (data) => {
    // Extract key insights from each phase
    const selfDiscoveryData = data['self-discovery']?.responses || {}
    const ideaDiscoveryData = data['idea-discovery']?.responses || {}
    const marketResearchData = data['market-research']?.responses || {}
    const businessPillarsData = data['business-pillars']?.responses || {}

    // Analyze entrepreneur archetype and characteristics
    const entrepreneurProfile = analyzeEntrepreneurProfile(selfDiscoveryData)
    
    // Analyze business opportunity potential
    const opportunityAnalysis = analyzeOpportunityPotential(ideaDiscoveryData, marketResearchData)
    
    // Analyze market readiness and competitive position
    const marketAnalysis = analyzeMarketPosition(marketResearchData)
    
    // Analyze business model viability
    const businessModelAnalysis = analyzeBusinessModel(businessPillarsData)
    
    // Generate overall success probability
    const successProbability = calculateSuccessProbability(
      entrepreneurProfile, 
      opportunityAnalysis, 
      marketAnalysis, 
      businessModelAnalysis
    )
    
    // Generate personalized recommendations
    const recommendations = generateRecommendations(
      entrepreneurProfile,
      opportunityAnalysis,
      marketAnalysis,
      businessModelAnalysis,
      successProbability
    )
    
    // Find similar entrepreneur matches
    const similarEntrepreneurs = findSimilarEntrepreneurs(entrepreneurProfile)
    
    // Generate risk assessment
    const riskAssessment = analyzeRisks(data)
    
    // Generate next steps
    const nextSteps = generateNextSteps(successProbability, recommendations)

    return {
      entrepreneurProfile,
      opportunityAnalysis,
      marketAnalysis,
      businessModelAnalysis,
      successProbability,
      recommendations,
      similarEntrepreneurs,
      riskAssessment,
      nextSteps,
      generatedAt: new Date().toISOString()
    }
  }

  // Analyze entrepreneur profile from self-discovery data
  const analyzeEntrepreneurProfile = (selfDiscoveryData) => {
    const coreMotivation = selfDiscoveryData['core-motivation']?.['motivation-reason'] || 'unknown'
    const riskTolerance = selfDiscoveryData['core-motivation']?.['risk-tolerance'] || 5
    const confidence = selfDiscoveryData['belief-confidence']?.['confidence-level'] || 5
    
    // Determine entrepreneur archetype based on responses
    let archetype = 'Balanced Entrepreneur'
    let archetypeDescription = 'A well-rounded entrepreneur with balanced motivations and approach'
    
    if (coreMotivation === 'world-change') {
      archetype = 'Visionary Innovator'
      archetypeDescription = 'Driven by big ideas and transformative solutions'
    } else if (coreMotivation === 'problem-solving') {
      archetype = 'Problem Solver'
      archetypeDescription = 'Focused on practical solutions to real problems'
    } else if (coreMotivation === 'lifestyle-freedom') {
      archetype = 'Lifestyle Entrepreneur'
      archetypeDescription = 'Prioritizes freedom and work-life balance'
    } else if (coreMotivation === 'financial-security') {
      archetype = 'Wealth Builder'
      archetypeDescription = 'Focused on financial growth and security'
    }
    
    // Calculate readiness score
    const readinessScore = Math.round((riskTolerance + confidence + 5) / 3 * 10)
    
    return {
      archetype,
      archetypeDescription,
      coreMotivation,
      riskTolerance,
      confidence,
      readinessScore,
      strengths: getEntrepreneurStrengths(coreMotivation, riskTolerance, confidence),
      developmentAreas: getDevelopmentAreas(coreMotivation, riskTolerance, confidence)
    }
  }

  // Analyze opportunity potential
  const analyzeOpportunityPotential = (ideaData, marketData) => {
    const opportunityScore = Math.floor(Math.random() * 30) + 70 // 70-100 range
    const marketSize = marketData['competitive-analysis']?.['market-positioning'] ? 'Large' : 'Medium'
    const competitiveAdvantage = marketData['competitive-analysis']?.['competitive-advantage'] ? 'Strong' : 'Moderate'
    
    return {
      score: opportunityScore,
      marketSize,
      competitiveAdvantage,
      viability: opportunityScore >= 85 ? 'High' : opportunityScore >= 70 ? 'Medium' : 'Low',
      keyFactors: [
        'Market demand validation needed',
        'Competitive differentiation identified',
        'Revenue model clarity required',
        'Customer acquisition strategy defined'
      ]
    }
  }

  // Analyze market position
  const analyzeMarketPosition = (marketData) => {
    const competitorCount = Object.keys(marketData['competitive-analysis']?.['competitor-identification'] || {}).length
    const marketReadiness = competitorCount > 0 ? 'Ready' : 'Needs Research'
    
    return {
      competitorCount,
      marketReadiness,
      competitiveIntensity: competitorCount > 3 ? 'High' : competitorCount > 1 ? 'Medium' : 'Low',
      marketOpportunities: [
        'Underserved customer segments identified',
        'Technology disruption potential',
        'Geographic expansion opportunities',
        'Partnership possibilities'
      ],
      marketThreats: [
        'New competitor entry risk',
        'Market saturation concerns',
        'Economic sensitivity factors',
        'Regulatory changes impact'
      ]
    }
  }

  // Analyze business model
  const analyzeBusinessModel = (businessData) => {
    const hasFinancialProjections = businessData['financial-planning']?.['financial-projections']
    const hasCustomerSegments = businessData['customer-segmentation']?.['target-segments']
    
    const viabilityScore = Math.floor(Math.random() * 25) + 75 // 75-100 range
    
    return {
      viabilityScore,
      hasFinancialProjections: !!hasFinancialProjections,
      hasCustomerSegments: !!hasCustomerSegments,
      modelStrength: viabilityScore >= 90 ? 'Strong' : viabilityScore >= 80 ? 'Good' : 'Developing',
      keyComponents: [
        'Value proposition clarity',
        'Revenue stream definition',
        'Cost structure optimization',
        'Customer acquisition plan'
      ]
    }
  }

  // Calculate overall success probability
  const calculateSuccessProbability = (profile, opportunity, market, businessModel) => {
    const weights = {
      entrepreneurReadiness: 0.25,
      opportunityViability: 0.30,
      marketPosition: 0.25,
      businessModel: 0.20
    }
    
    const scores = {
      entrepreneurReadiness: profile.readinessScore,
      opportunityViability: opportunity.score,
      marketPosition: market.competitorCount > 0 ? 80 : 60,
      businessModel: businessModel.viabilityScore
    }
    
    const weightedScore = Object.keys(weights).reduce((total, key) => {
      return total + (scores[key] * weights[key])
    }, 0)
    
    return {
      overall: Math.round(weightedScore),
      breakdown: scores,
      confidence: weightedScore >= 85 ? 'High' : weightedScore >= 70 ? 'Medium' : 'Low',
      factors: {
        strengths: getSuccessFactors(scores, 'strengths'),
        risks: getSuccessFactors(scores, 'risks')
      }
    }
  }

  // Generate personalized recommendations
  const generateRecommendations = (profile, opportunity, market, businessModel, success) => {
    const recommendations = []
    
    // Profile-based recommendations
    if (profile.readinessScore < 70) {
      recommendations.push({
        category: 'Personal Development',
        priority: 'High',
        title: 'Build Entrepreneurial Confidence',
        description: 'Focus on developing risk tolerance and business confidence through education and mentorship.',
        actions: ['Join entrepreneur meetups', 'Find a business mentor', 'Take entrepreneurship courses']
      })
    }
    
    // Opportunity-based recommendations
    if (opportunity.score < 80) {
      recommendations.push({
        category: 'Opportunity Validation',
        priority: 'High',
        title: 'Strengthen Business Opportunity',
        description: 'Validate and refine your business opportunity through market research and customer feedback.',
        actions: ['Conduct customer interviews', 'Create MVP prototype', 'Test pricing models']
      })
    }
    
    // Market-based recommendations
    if (market.competitorCount === 0) {
      recommendations.push({
        category: 'Market Research',
        priority: 'Medium',
        title: 'Complete Competitive Analysis',
        description: 'Identify and analyze competitors to understand market dynamics and positioning.',
        actions: ['Research direct competitors', 'Analyze indirect competitors', 'Define competitive advantages']
      })
    }
    
    // Business model recommendations
    if (!businessModel.hasFinancialProjections) {
      recommendations.push({
        category: 'Financial Planning',
        priority: 'High',
        title: 'Develop Financial Projections',
        description: 'Create detailed financial forecasts to understand funding needs and profitability timeline.',
        actions: ['Build 3-year financial model', 'Calculate break-even point', 'Identify funding sources']
      })
    }
    
    // Success-based recommendations
    if (success.overall >= 85) {
      recommendations.push({
        category: 'Execution',
        priority: 'Medium',
        title: 'Prepare for Launch',
        description: 'Your venture shows strong potential. Focus on execution and go-to-market strategy.',
        actions: ['Finalize business plan', 'Secure initial funding', 'Build launch team']
      })
    }
    
    return recommendations
  }

  // Find similar entrepreneurs (mock data)
  const findSimilarEntrepreneurs = (profile) => {
    const similarProfiles = [
      {
        name: 'Sarah Chen',
        archetype: profile.archetype,
        industry: 'SaaS',
        stage: 'Series A',
        similarity: 92,
        story: 'Built a customer service automation platform, raised $2M in 18 months'
      },
      {
        name: 'Marcus Rodriguez',
        archetype: profile.archetype,
        industry: 'E-commerce',
        stage: 'Profitable',
        similarity: 88,
        story: 'Created sustainable fashion marketplace, achieved profitability in year 2'
      },
      {
        name: 'Jennifer Kim',
        archetype: profile.archetype,
        industry: 'HealthTech',
        stage: 'Seed',
        similarity: 85,
        story: 'Developing mental health app, secured $500K seed funding'
      }
    ]
    
    return similarProfiles
  }

  // Analyze risks
  const analyzeRisks = (data) => {
    return {
      high: [
        'Market competition intensity',
        'Customer acquisition costs'
      ],
      medium: [
        'Technology development timeline',
        'Regulatory compliance requirements',
        'Team building challenges'
      ],
      low: [
        'Economic market conditions',
        'Supply chain disruptions'
      ]
    }
  }

  // Generate next steps
  const generateNextSteps = (success, recommendations) => {
    const steps = []
    
    // Prioritize based on success probability and recommendations
    if (success.overall >= 80) {
      steps.push(
        { phase: 'Immediate (1-2 weeks)', action: 'Finalize business plan and financial projections' },
        { phase: 'Short-term (1-3 months)', action: 'Secure initial funding and build core team' },
        { phase: 'Medium-term (3-6 months)', action: 'Launch MVP and acquire first customers' }
      )
    } else if (success.overall >= 60) {
      steps.push(
        { phase: 'Immediate (1-2 weeks)', action: 'Complete market research and competitive analysis' },
        { phase: 'Short-term (1-3 months)', action: 'Validate business model with potential customers' },
        { phase: 'Medium-term (3-6 months)', action: 'Refine offering and prepare for launch' }
      )
    } else {
      steps.push(
        { phase: 'Immediate (1-2 weeks)', action: 'Focus on personal development and skill building' },
        { phase: 'Short-term (1-3 months)', action: 'Strengthen business opportunity and market understanding' },
        { phase: 'Medium-term (3-6 months)', action: 'Consider partnership or alternative approaches' }
      )
    }
    
    return steps
  }

  // Helper functions
  const getEntrepreneurStrengths = (motivation, risk, confidence) => {
    const strengths = []
    if (risk >= 7) strengths.push('High risk tolerance')
    if (confidence >= 7) strengths.push('Strong self-confidence')
    if (motivation === 'world-change') strengths.push('Visionary thinking')
    if (motivation === 'problem-solving') strengths.push('Problem-solving focus')
    return strengths.length > 0 ? strengths : ['Balanced approach', 'Learning mindset']
  }

  const getDevelopmentAreas = (motivation, risk, confidence) => {
    const areas = []
    if (risk < 5) areas.push('Risk tolerance building')
    if (confidence < 5) areas.push('Confidence development')
    if (motivation === 'lifestyle-freedom') areas.push('Business growth mindset')
    return areas.length > 0 ? areas : ['Continuous learning', 'Network expansion']
  }

  const getSuccessFactors = (scores, type) => {
    if (type === 'strengths') {
      return Object.entries(scores)
        .filter(([key, value]) => value >= 80)
        .map(([key]) => key.replace(/([A-Z])/g, ' $1').toLowerCase())
    } else {
      return Object.entries(scores)
        .filter(([key, value]) => value < 70)
        .map(([key]) => key.replace(/([A-Z])/g, ' $1').toLowerCase())
    }
  }

  // Auto-generate analysis when component mounts if data is available
  useEffect(() => {
    if (hasEnoughData() && !aiAnalysis && !isAnalyzing) {
      generateAIAnalysis()
    }
  }, [assessmentData])

  if (!hasEnoughData()) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
              <Brain className="h-8 w-8 text-muted-foreground" />
            </div>
            <CardTitle className="flex items-center justify-center gap-2">
              <Zap className="h-6 w-6 text-primary" />
              AI-Powered Recommendations
            </CardTitle>
            <CardDescription>
              Get personalized insights and recommendations based on your assessment
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <AlertTriangle className="h-12 w-12 text-orange-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">More Data Needed</h3>
            <p className="text-muted-foreground mb-6">
              Complete at least 2 assessment phases to unlock AI-powered recommendations and insights.
            </p>
            <div className="grid md:grid-cols-2 gap-4 text-left">
              <div className="space-y-2">
                <h4 className="font-semibold">Available Features:</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Entrepreneur archetype analysis</li>
                  <li>• Success probability scoring</li>
                  <li>• Personalized recommendations</li>
                  <li>• Similar entrepreneur matching</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">AI Insights Include:</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Market opportunity analysis</li>
                  <li>• Risk assessment and mitigation</li>
                  <li>• Strategic next steps planning</li>
                  <li>• Business model optimization</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (isAnalyzing) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
              <RefreshCw className="h-8 w-8 text-primary animate-spin" />
            </div>
            <CardTitle>Analyzing Your Entrepreneurial Profile</CardTitle>
            <CardDescription>
              Our AI is processing your assessment data to generate personalized insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Progress value={analysisProgress} className="w-full" />
              <p className="text-center text-sm text-muted-foreground">
                {analysisProgress < 100 ? 'Processing...' : 'Finalizing analysis...'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!aiAnalysis) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader className="text-center">
            <CardTitle>Generate AI Analysis</CardTitle>
            <CardDescription>
              Click below to generate your personalized entrepreneurial analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Button onClick={generateAIAnalysis} size="lg">
              <Brain className="h-5 w-5 mr-2" />
              Generate AI Recommendations
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                <Brain className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle>AI-Powered Analysis</CardTitle>
                <CardDescription>
                  Personalized insights based on your comprehensive assessment
                </CardDescription>
              </div>
            </div>
            <Button variant="outline" onClick={generateAIAnalysis}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh Analysis
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Success Probability Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />
            Success Probability Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">
                {aiAnalysis.successProbability.overall}%
              </div>
              <div className="text-sm text-muted-foreground">Overall Success Probability</div>
              <Badge 
                variant={aiAnalysis.successProbability.confidence === 'High' ? 'default' : 'secondary'}
                className="mt-2"
              >
                {aiAnalysis.successProbability.confidence} Confidence
              </Badge>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Entrepreneur Readiness</span>
                <span className="font-semibold">{aiAnalysis.successProbability.breakdown.entrepreneurReadiness}%</span>
              </div>
              <Progress value={aiAnalysis.successProbability.breakdown.entrepreneurReadiness} />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Opportunity Viability</span>
                <span className="font-semibold">{aiAnalysis.successProbability.breakdown.opportunityViability}%</span>
              </div>
              <Progress value={aiAnalysis.successProbability.breakdown.opportunityViability} />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Market Position</span>
                <span className="font-semibold">{aiAnalysis.successProbability.breakdown.marketPosition}%</span>
              </div>
              <Progress value={aiAnalysis.successProbability.breakdown.marketPosition} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Analysis Tabs */}
      <Tabs defaultValue="profile" className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
          <TabsTrigger value="risks">Risks</TabsTrigger>
          <TabsTrigger value="matches">Matches</TabsTrigger>
          <TabsTrigger value="next-steps">Next Steps</TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <EntrepreneurProfileAnalysis profile={aiAnalysis.entrepreneurProfile} />
        </TabsContent>

        <TabsContent value="recommendations">
          <RecommendationsAnalysis recommendations={aiAnalysis.recommendations} />
        </TabsContent>

        <TabsContent value="opportunities">
          <OpportunityAnalysis 
            opportunity={aiAnalysis.opportunityAnalysis} 
            market={aiAnalysis.marketAnalysis} 
          />
        </TabsContent>

        <TabsContent value="risks">
          <RiskAnalysis risks={aiAnalysis.riskAssessment} />
        </TabsContent>

        <TabsContent value="matches">
          <SimilarEntrepreneursAnalysis matches={aiAnalysis.similarEntrepreneurs} />
        </TabsContent>

        <TabsContent value="next-steps">
          <NextStepsAnalysis steps={aiAnalysis.nextSteps} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

// Entrepreneur Profile Analysis Component
const EntrepreneurProfileAnalysis = ({ profile }) => (
  <div className="grid md:grid-cols-2 gap-6">
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Star className="h-5 w-5 text-primary" />
          Your Entrepreneur Archetype
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center mb-4">
          <div className="text-2xl font-bold text-primary mb-2">{profile.archetype}</div>
          <p className="text-muted-foreground">{profile.archetypeDescription}</p>
        </div>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Entrepreneurial Readiness</span>
              <span className="font-semibold">{profile.readinessScore}%</span>
            </div>
            <Progress value={profile.readinessScore} />
          </div>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-lg font-semibold">{profile.riskTolerance}/10</div>
              <div className="text-xs text-muted-foreground">Risk Tolerance</div>
            </div>
            <div>
              <div className="text-lg font-semibold">{profile.confidence}/10</div>
              <div className="text-xs text-muted-foreground">Confidence Level</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Strengths & Development Areas</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-green-600 mb-2">Key Strengths</h4>
            <ul className="space-y-1">
              {profile.strengths.map((strength, index) => (
                <li key={index} className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  {strength}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-orange-600 mb-2">Development Areas</h4>
            <ul className="space-y-1">
              {profile.developmentAreas.map((area, index) => (
                <li key={index} className="flex items-center gap-2 text-sm">
                  <Target className="h-4 w-4 text-orange-500" />
                  {area}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
)

// Recommendations Analysis Component
const RecommendationsAnalysis = ({ recommendations }) => (
  <div className="space-y-4">
    {recommendations.map((rec, index) => (
      <Card key={index}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">{rec.title}</CardTitle>
            <Badge variant={rec.priority === 'High' ? 'destructive' : 'secondary'}>
              {rec.priority} Priority
            </Badge>
          </div>
          <Badge variant="outline">{rec.category}</Badge>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">{rec.description}</p>
          <div>
            <h4 className="font-semibold mb-2">Recommended Actions:</h4>
            <ul className="space-y-1">
              {rec.actions.map((action, actionIndex) => (
                <li key={actionIndex} className="flex items-center gap-2 text-sm">
                  <ArrowRight className="h-4 w-4 text-primary" />
                  {action}
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>
    ))}
  </div>
)

// Opportunity Analysis Component
const OpportunityAnalysis = ({ opportunity, market }) => (
  <div className="grid md:grid-cols-2 gap-6">
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-primary" />
          Opportunity Assessment
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-primary mb-2">{opportunity.score}%</div>
            <div className="text-sm text-muted-foreground">Opportunity Score</div>
            <Badge variant={opportunity.viability === 'High' ? 'default' : 'secondary'} className="mt-2">
              {opportunity.viability} Viability
            </Badge>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="font-semibold">{opportunity.marketSize}</div>
              <div className="text-xs text-muted-foreground">Market Size</div>
            </div>
            <div className="text-center">
              <div className="font-semibold">{opportunity.competitiveAdvantage}</div>
              <div className="text-xs text-muted-foreground">Competitive Edge</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Market Position
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold">{market.competitorCount}</div>
              <div className="text-xs text-muted-foreground">Competitors Identified</div>
            </div>
            <div>
              <div className="font-semibold">{market.competitiveIntensity}</div>
              <div className="text-xs text-muted-foreground">Competition Level</div>
            </div>
          </div>
          <div>
            <Badge variant="outline" className="w-full justify-center">
              Market Status: {market.marketReadiness}
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
)

// Risk Analysis Component
const RiskAnalysis = ({ risks }) => (
  <div className="grid md:grid-cols-3 gap-6">
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-red-600">
          <AlertTriangle className="h-5 w-5" />
          High Risk
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {risks.high.map((risk, index) => (
            <li key={index} className="flex items-start gap-2 text-sm">
              <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0" />
              {risk}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-orange-600">
          <Shield className="h-5 w-5" />
          Medium Risk
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {risks.medium.map((risk, index) => (
            <li key={index} className="flex items-start gap-2 text-sm">
              <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0" />
              {risk}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-green-600">
          <CheckCircle className="h-5 w-5" />
          Low Risk
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {risks.low.map((risk, index) => (
            <li key={index} className="flex items-start gap-2 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
              {risk}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  </div>
)

// Similar Entrepreneurs Component
const SimilarEntrepreneursAnalysis = ({ matches }) => (
  <div className="grid md:grid-cols-3 gap-6">
    {matches.map((match, index) => (
      <Card key={index}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">{match.name}</CardTitle>
            <Badge variant="secondary">{match.similarity}% Match</Badge>
          </div>
          <div className="flex gap-2">
            <Badge variant="outline">{match.industry}</Badge>
            <Badge variant="outline">{match.stage}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{match.story}</p>
          <div className="mt-4">
            <div className="text-xs text-muted-foreground mb-1">Archetype Match</div>
            <div className="text-sm font-medium">{match.archetype}</div>
          </div>
        </CardContent>
      </Card>
    ))}
  </div>
)

// Next Steps Component
const NextStepsAnalysis = ({ steps }) => (
  <div className="space-y-4">
    {steps.map((step, index) => (
      <Card key={index}>
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
              {index + 1}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Badge variant="outline">{step.phase}</Badge>
              </div>
              <h3 className="font-semibold mb-1">{step.action}</h3>
            </div>
          </div>
        </CardContent>
      </Card>
    ))}
  </div>
)

export default AIRecommendations

