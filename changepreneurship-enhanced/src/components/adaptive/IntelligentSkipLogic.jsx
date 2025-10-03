import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Progress } from '../ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { 
  SkipForward, 
  Target, 
  TrendingUp, 
  CheckCircle,
  AlertTriangle,
  ArrowRight,
  ArrowDown,
  Clock,
  Zap,
  Filter,
  Star,
  Brain,
  Route
} from 'lucide-react'
import { useEnhancedAssessment } from '../../contexts/EnhancedAssessmentContext'

// Priority levels for questions
const PRIORITY_LEVELS = {
  CRITICAL: { level: 1, label: 'Critical', color: 'text-red-400', bgColor: 'bg-red-900/20', borderColor: 'border-red-500' },
  HIGH: { level: 2, label: 'High', color: 'text-orange-400', bgColor: 'bg-orange-900/20', borderColor: 'border-orange-500' },
  MEDIUM: { level: 3, label: 'Medium', color: 'text-yellow-400', bgColor: 'bg-yellow-900/20', borderColor: 'border-yellow-500' },
  LOW: { level: 4, label: 'Low', color: 'text-green-400', bgColor: 'bg-green-900/20', borderColor: 'border-green-500' },
  SKIPPED: { level: 5, label: 'Skipped', color: 'text-gray-400', bgColor: 'bg-gray-900/20', borderColor: 'border-gray-500' }
}

// Sample questions with skip logic and priority rules
const SAMPLE_QUESTIONS = [
  {
    id: 'business_idea_clarity',
    text: 'How clear is your business idea?',
    category: 'idea_development',
    priority: PRIORITY_LEVELS.CRITICAL,
    skipConditions: [],
    dependsOn: [],
    triggers: ['idea_validation_questions', 'market_research_questions']
  },
  {
    id: 'idea_validation_experience',
    text: 'Have you validated your business idea with potential customers?',
    category: 'idea_development',
    priority: PRIORITY_LEVELS.HIGH,
    skipConditions: [
      { condition: 'business_idea_clarity', value: 'no_idea', reason: 'No business idea to validate' }
    ],
    dependsOn: ['business_idea_clarity'],
    triggers: ['customer_feedback_questions']
  },
  {
    id: 'market_research_capability',
    text: 'How experienced are you with market research?',
    category: 'market_analysis',
    priority: PRIORITY_LEVELS.MEDIUM,
    skipConditions: [
      { condition: 'business_idea_clarity', value: 'no_idea', reason: 'No idea to research' },
      { condition: 'industry_experience', value: 'expert', reason: 'Expert level experience implies research capability' }
    ],
    dependsOn: ['business_idea_clarity'],
    triggers: ['research_methodology_questions']
  },
  {
    id: 'financial_stress_tolerance',
    text: 'How well do you handle financial stress?',
    category: 'financial_readiness',
    priority: PRIORITY_LEVELS.HIGH,
    skipConditions: [
      { condition: 'financial_runway', value: 'very_stable', reason: 'Strong financial position reduces stress concerns' },
      { condition: 'risk_tolerance', value: 'risk_averse', reason: 'Risk-averse individuals need different financial planning' }
    ],
    dependsOn: ['financial_runway', 'risk_tolerance'],
    triggers: ['stress_management_questions']
  },
  {
    id: 'team_management_experience',
    text: 'What is your experience managing teams?',
    category: 'leadership',
    priority: PRIORITY_LEVELS.MEDIUM,
    skipConditions: [
      { condition: 'business_model_preference', value: 'solo_entrepreneur', reason: 'Solo entrepreneurs don\'t need team management' },
      { condition: 'leadership_background', value: 'extensive', reason: 'Already established through background' }
    ],
    dependsOn: ['business_model_preference'],
    triggers: ['leadership_development_questions']
  },
  {
    id: 'technology_comfort_level',
    text: 'How comfortable are you with technology?',
    category: 'technical_skills',
    priority: PRIORITY_LEVELS.LOW,
    skipConditions: [
      { condition: 'industry_focus', value: 'technology', reason: 'Tech industry implies high comfort level' },
      { condition: 'business_type', value: 'traditional_service', reason: 'Traditional services may not require high tech comfort' }
    ],
    dependsOn: ['industry_focus', 'business_type'],
    triggers: ['digital_marketing_questions']
  },
  {
    id: 'investor_relations_interest',
    text: 'Are you interested in working with investors?',
    category: 'funding',
    priority: PRIORITY_LEVELS.MEDIUM,
    skipConditions: [
      { condition: 'funding_preference', value: 'bootstrap_only', reason: 'Bootstrap preference excludes investor relations' },
      { condition: 'business_scale', value: 'lifestyle_business', reason: 'Lifestyle businesses typically don\'t seek investors' }
    ],
    dependsOn: ['funding_preference', 'business_scale'],
    triggers: ['pitch_preparation_questions']
  },
  {
    id: 'international_expansion_plans',
    text: 'Do you plan to expand internationally?',
    category: 'growth_strategy',
    priority: PRIORITY_LEVELS.LOW,
    skipConditions: [
      { condition: 'business_stage', value: 'idea_stage', reason: 'Too early to consider international expansion' },
      { condition: 'market_focus', value: 'local_only', reason: 'Local focus excludes international plans' },
      { condition: 'business_scale', value: 'small_local', reason: 'Small local businesses typically don\'t expand internationally' }
    ],
    dependsOn: ['business_stage', 'market_focus', 'business_scale'],
    triggers: ['international_strategy_questions']
  }
]

// Mock user responses for demonstration
const MOCK_RESPONSES = {
  business_idea_clarity: 'clear_idea',
  industry_experience: 'intermediate',
  financial_runway: 'moderate',
  risk_tolerance: 'calculated',
  business_model_preference: 'team_based',
  leadership_background: 'some_experience',
  industry_focus: 'technology',
  business_type: 'tech_startup',
  funding_preference: 'mixed_funding',
  business_scale: 'scalable_startup',
  business_stage: 'validation_stage',
  market_focus: 'regional'
}

export default function IntelligentSkipLogic() {
  const {
    getAllResponses,
    getUserProfileType,
    getCurrentPath,
    adaptiveEngine
  } = useEnhancedAssessment()

  const [currentResponses, setCurrentResponses] = useState(MOCK_RESPONSES)
  const [processedQuestions, setProcessedQuestions] = useState([])
  const [skipAnalysis, setSkipAnalysis] = useState({})
  const [priorityAnalysis, setPriorityAnalysis] = useState({})
  const [showSkipLogic, setShowSkipLogic] = useState(true)
  const [selectedQuestion, setSelectedQuestion] = useState(null)

  // Process questions with skip logic and priority ordering
  useEffect(() => {
    const processed = SAMPLE_QUESTIONS.map(question => {
      // Check skip conditions
      const shouldSkip = question.skipConditions.some(condition => {
        const userResponse = currentResponses[condition.condition]
        return userResponse === condition.value
      })

      // Calculate dynamic priority based on user responses
      let dynamicPriority = question.priority
      if (shouldSkip) {
        dynamicPriority = PRIORITY_LEVELS.SKIPPED
      } else {
        // Boost priority if dependencies are met
        const dependenciesMet = question.dependsOn.every(dep => currentResponses[dep])
        if (dependenciesMet && question.priority.level > 2) {
          dynamicPriority = PRIORITY_LEVELS.HIGH
        }
      }

      return {
        ...question,
        shouldSkip,
        dynamicPriority,
        skipReason: shouldSkip ? question.skipConditions.find(c => currentResponses[c.condition] === c.value)?.reason : null
      }
    })

    // Sort by priority (lower level = higher priority)
    const sorted = processed.sort((a, b) => {
      if (a.shouldSkip && !b.shouldSkip) return 1
      if (!a.shouldSkip && b.shouldSkip) return -1
      return a.dynamicPriority.level - b.dynamicPriority.level
    })

    setProcessedQuestions(sorted)

    // Generate analysis
    const skipCount = processed.filter(q => q.shouldSkip).length
    const priorityDistribution = processed.reduce((acc, q) => {
      const priority = q.dynamicPriority.label
      acc[priority] = (acc[priority] || 0) + 1
      return acc
    }, {})

    setSkipAnalysis({
      totalQuestions: SAMPLE_QUESTIONS.length,
      skippedQuestions: skipCount,
      activeQuestions: SAMPLE_QUESTIONS.length - skipCount,
      timeReduction: Math.round((skipCount / SAMPLE_QUESTIONS.length) * 100)
    })

    setPriorityAnalysis(priorityDistribution)
  }, [currentResponses])

  // Simulate response change
  const handleResponseChange = (questionId, value) => {
    setCurrentResponses(prev => ({
      ...prev,
      [questionId]: value
    }))
  }

  // Render question card
  const renderQuestionCard = (question, index) => {
    const priority = question.dynamicPriority
    const isSelected = selectedQuestion === question.id

    return (
      <Card 
        key={question.id} 
        className={`cursor-pointer transition-all ${
          isSelected ? 'ring-2 ring-orange-500' : ''
        } ${priority.bgColor} border ${priority.borderColor}`}
        onClick={() => setSelectedQuestion(isSelected ? null : question.id)}
      >
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="text-lg font-bold text-gray-400">#{index + 1}</div>
              <CardTitle className={`text-sm ${priority.color}`}>
                {question.text}
              </CardTitle>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className={`text-xs ${priority.color} border-current`}>
                {priority.label}
              </Badge>
              {question.shouldSkip && (
                <SkipForward className="h-4 w-4 text-gray-400" />
              )}
            </div>
          </div>
        </CardHeader>
        
        {isSelected && (
          <CardContent className="pt-0">
            <div className="space-y-3">
              <div className="text-sm text-gray-400">
                <strong>Category:</strong> {question.category.replace('_', ' ')}
              </div>
              
              {question.shouldSkip ? (
                <div className="p-3 bg-gray-800 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <SkipForward className="h-4 w-4 text-gray-400" />
                    <span className="text-gray-300 font-medium">Skipped</span>
                  </div>
                  <div className="text-sm text-gray-400">{question.skipReason}</div>
                </div>
              ) : (
                <div className="space-y-2">
                  {question.dependsOn.length > 0 && (
                    <div className="text-sm text-gray-400">
                      <strong>Depends on:</strong> {question.dependsOn.join(', ')}
                    </div>
                  )}
                  
                  {question.triggers.length > 0 && (
                    <div className="text-sm text-gray-400">
                      <strong>Triggers:</strong> {question.triggers.join(', ')}
                    </div>
                  )}
                </div>
              )}
              
              {question.skipConditions.length > 0 && (
                <div className="p-3 bg-gray-800 rounded-lg">
                  <div className="text-sm text-gray-300 font-medium mb-2">Skip Conditions:</div>
                  <div className="space-y-1">
                    {question.skipConditions.map((condition, idx) => (
                      <div key={idx} className="text-xs text-gray-400 flex items-center gap-2">
                        <ArrowRight className="h-3 w-3" />
                        If {condition.condition} = "{condition.value}" → {condition.reason}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        )}
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Brain className="h-5 w-5 text-orange-500" />
            Intelligent Skip Logic & Priority Ordering
          </CardTitle>
          <CardDescription className="text-gray-400">
            See how the system intelligently skips irrelevant questions and prioritizes important ones
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-blue-400">{skipAnalysis.totalQuestions}</div>
              <div className="text-xs text-gray-400">Total Questions</div>
            </div>
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-green-400">{skipAnalysis.activeQuestions}</div>
              <div className="text-xs text-gray-400">Active Questions</div>
            </div>
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-red-400">{skipAnalysis.skippedQuestions}</div>
              <div className="text-xs text-gray-400">Skipped Questions</div>
            </div>
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-orange-400">{skipAnalysis.timeReduction}%</div>
              <div className="text-xs text-gray-400">Time Saved</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Controls */}
      <div className="flex gap-2">
        <Button
          onClick={() => setShowSkipLogic(!showSkipLogic)}
          variant={showSkipLogic ? 'default' : 'outline'}
          className={showSkipLogic ? 'bg-orange-600 hover:bg-orange-700' : 'border-gray-600 text-gray-300'}
        >
          <Filter className="h-4 w-4 mr-2" />
          {showSkipLogic ? 'Hide' : 'Show'} Skip Logic
        </Button>
        <Button
          onClick={() => setCurrentResponses({})}
          variant="outline"
          className="border-gray-600 text-gray-300 hover:bg-gray-800"
        >
          Reset Responses
        </Button>
        <Button
          onClick={() => setCurrentResponses(MOCK_RESPONSES)}
          variant="outline"
          className="border-gray-600 text-gray-300 hover:bg-gray-800"
        >
          Load Sample Responses
        </Button>
      </div>

      <Tabs defaultValue="questions" className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-gray-800">
          <TabsTrigger value="questions" className="text-gray-300">Question Flow</TabsTrigger>
          <TabsTrigger value="analysis" className="text-gray-300">Skip Analysis</TabsTrigger>
          <TabsTrigger value="priority" className="text-gray-300">Priority Logic</TabsTrigger>
        </TabsList>

        <TabsContent value="questions" className="space-y-4">
          <div className="space-y-3">
            {processedQuestions.map((question, index) => renderQuestionCard(question, index))}
          </div>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Skip Logic Rules */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <SkipForward className="h-5 w-5 text-green-500" />
                  Skip Logic Rules
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Conditions that trigger question skipping
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {SAMPLE_QUESTIONS.filter(q => q.skipConditions.length > 0).map(question => (
                    <div key={question.id} className="p-3 bg-gray-800 rounded-lg">
                      <div className="text-white font-medium text-sm mb-2">{question.text}</div>
                      <div className="space-y-1">
                        {question.skipConditions.map((condition, idx) => (
                          <div key={idx} className="text-xs text-gray-400 flex items-center gap-2">
                            <ArrowRight className="h-3 w-3 text-orange-500" />
                            Skip if {condition.condition} = "{condition.value}"
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Current Skip Status */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Target className="h-5 w-5 text-blue-500" />
                  Current Skip Status
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Questions being skipped based on current responses
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {processedQuestions.filter(q => q.shouldSkip).map(question => (
                    <div key={question.id} className="p-3 bg-red-900/20 border border-red-500/30 rounded-lg">
                      <div className="text-white font-medium text-sm mb-1">{question.text}</div>
                      <div className="text-red-300 text-xs">{question.skipReason}</div>
                    </div>
                  ))}
                  {processedQuestions.filter(q => q.shouldSkip).length === 0 && (
                    <div className="text-gray-400 text-sm">No questions are currently being skipped</div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="priority" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Priority Distribution */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Star className="h-5 w-5 text-yellow-500" />
                  Priority Distribution
                </CardTitle>
                <CardDescription className="text-gray-400">
                  How questions are prioritized based on your responses
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(priorityAnalysis).map(([priority, count]) => {
                    const priorityData = Object.values(PRIORITY_LEVELS).find(p => p.label === priority)
                    if (!priorityData) return null
                    
                    return (
                      <div key={priority} className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                        <div className="flex items-center gap-2">
                          <div className={`w-3 h-3 rounded-full ${priorityData.color.replace('text-', 'bg-')}`} />
                          <span className="text-white">{priority}</span>
                        </div>
                        <Badge variant="secondary" className="bg-gray-700 text-gray-300">
                          {count} questions
                        </Badge>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Priority Logic Explanation */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Route className="h-5 w-5 text-purple-500" />
                  Priority Logic
                </CardTitle>
                <CardDescription className="text-gray-400">
                  How the system determines question priority
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-3 bg-gray-800 rounded-lg">
                    <h4 className="text-white font-medium mb-2">Dynamic Priority Rules</h4>
                    <div className="space-y-2 text-sm text-gray-400">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-3 w-3 text-green-500" />
                        Critical questions always come first
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-3 w-3 text-green-500" />
                        Dependencies boost question priority
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-3 w-3 text-green-500" />
                        User profile influences ordering
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-3 w-3 text-green-500" />
                        Skipped questions move to bottom
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-3 bg-gray-800 rounded-lg">
                    <h4 className="text-white font-medium mb-2">Optimization Benefits</h4>
                    <div className="space-y-2 text-sm text-gray-400">
                      <div>• Reduces assessment time by {skipAnalysis.timeReduction}%</div>
                      <div>• Focuses on relevant questions first</div>
                      <div>• Adapts to user responses in real-time</div>
                      <div>• Maintains assessment accuracy</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Interactive Response Simulator */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Zap className="h-5 w-5 text-orange-500" />
            Interactive Response Simulator
          </CardTitle>
          <CardDescription className="text-gray-400">
            Change responses to see how skip logic and priorities adapt in real-time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(currentResponses).map(([key, value]) => (
              <div key={key} className="p-3 bg-gray-800 rounded-lg">
                <div className="text-white font-medium text-sm mb-2">
                  {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </div>
                <select
                  value={value}
                  onChange={(e) => handleResponseChange(key, e.target.value)}
                  className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                >
                  <option value="">Select...</option>
                  <option value="no_idea">No Idea</option>
                  <option value="clear_idea">Clear Idea</option>
                  <option value="expert">Expert</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="beginner">Beginner</option>
                  <option value="very_stable">Very Stable</option>
                  <option value="moderate">Moderate</option>
                  <option value="limited">Limited</option>
                  <option value="risk_averse">Risk Averse</option>
                  <option value="calculated">Calculated</option>
                  <option value="high_risk">High Risk</option>
                  <option value="solo_entrepreneur">Solo</option>
                  <option value="team_based">Team Based</option>
                  <option value="bootstrap_only">Bootstrap Only</option>
                  <option value="mixed_funding">Mixed Funding</option>
                  <option value="lifestyle_business">Lifestyle</option>
                  <option value="scalable_startup">Scalable</option>
                  <option value="local_only">Local Only</option>
                  <option value="regional">Regional</option>
                  <option value="global">Global</option>
                </select>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

