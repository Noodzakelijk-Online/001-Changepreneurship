import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Progress } from '../ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { 
  Sparkles, 
  Zap, 
  SkipForward, 
  Clock, 
  Target,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  BarChart3,
  Users,
  Lightbulb
} from 'lucide-react'
import { useEnhancedAssessment } from '../../contexts/EnhancedAssessmentContext'
import AdaptiveQuestionComponent from './AdaptiveQuestionComponent'

// Demo questions showing different optimization types
const DEMO_QUESTIONS = {
  original: [
    {
      id: 'financial_risk_comfort',
      text: 'How comfortable are you with financial risk?',
      type: 'scale',
      category: 'risk_tolerance'
    },
    {
      id: 'career_risk_tolerance',
      text: 'How willing are you to risk your current career?',
      type: 'scale',
      category: 'risk_tolerance'
    },
    {
      id: 'investment_risk_preference',
      text: 'What is your investment risk preference?',
      type: 'multiple_choice',
      category: 'risk_tolerance'
    },
    {
      id: 'failure_acceptance',
      text: 'How do you handle the possibility of failure?',
      type: 'multiple_choice',
      category: 'risk_tolerance'
    },
    {
      id: 'uncertainty_comfort',
      text: 'How comfortable are you with uncertainty?',
      type: 'scale',
      category: 'risk_tolerance'
    },
    {
      id: 'primary_motivation',
      text: 'What is your primary motivation for entrepreneurship?',
      type: 'multiple_choice',
      category: 'motivation'
    },
    {
      id: 'success_definition',
      text: 'How do you define success?',
      type: 'textarea',
      category: 'motivation'
    },
    {
      id: 'driving_factors',
      text: 'What factors drive you most?',
      type: 'multiple_choice',
      category: 'motivation'
    },
    {
      id: 'industry_experience_years',
      text: 'How many years of industry experience do you have?',
      type: 'text',
      category: 'experience'
    },
    {
      id: 'leadership_background',
      text: 'Describe your leadership background',
      type: 'textarea',
      category: 'experience'
    }
  ],
  
  optimized: [
    {
      id: 'risk_tolerance_consolidated',
      title: 'Risk Tolerance Assessment',
      text: 'How would you describe your overall approach to risk in entrepreneurship?',
      type: 'consolidated',
      category: 'risk_tolerance',
      originalCount: 5,
      timeSaved: '8 minutes'
    },
    {
      id: 'motivation_consolidated',
      title: 'Entrepreneurial Motivation Assessment',
      text: 'What is your primary motivation for becoming an entrepreneur?',
      type: 'consolidated',
      category: 'motivation',
      originalCount: 3,
      timeSaved: '5 minutes'
    },
    {
      id: 'industry_experience',
      title: 'Industry Experience',
      text: 'What is your industry experience level?',
      type: 'pre_populated',
      category: 'experience',
      prePopulatedValue: 'Technology/Software - 10+ years',
      confidence: 0.9,
      source: 'work_history'
    },
    {
      id: 'leadership_readiness',
      title: 'Leadership Readiness',
      text: 'How ready are you to lead a team?',
      type: 'pre_populated',
      category: 'experience',
      prePopulatedValue: 'Experienced - Led teams of 10+ people',
      confidence: 0.85,
      source: 'management_background'
    }
  ]
}

export default function QuestionOptimizationDemo() {
  const {
    getAllResponses,
    getUserProfileType,
    getCurrentPath,
    getAssessmentSummary
  } = useEnhancedAssessment()

  const [currentView, setCurrentView] = useState('comparison')
  const [animationStep, setAnimationStep] = useState(0)
  const [showOptimization, setShowOptimization] = useState(false)

  const userProfile = getUserProfileType()
  const currentPath = getCurrentPath()
  const allResponses = getAllResponses()

  // Calculate optimization metrics
  const optimizationMetrics = {
    originalQuestions: DEMO_QUESTIONS.original.length,
    optimizedQuestions: DEMO_QUESTIONS.optimized.length,
    questionsReduced: DEMO_QUESTIONS.original.length - DEMO_QUESTIONS.optimized.length,
    timeReduction: Math.round(((DEMO_QUESTIONS.original.length - DEMO_QUESTIONS.optimized.length) / DEMO_QUESTIONS.original.length) * 100),
    consolidatedQuestions: DEMO_QUESTIONS.optimized.filter(q => q.type === 'consolidated').length,
    prePopulatedQuestions: DEMO_QUESTIONS.optimized.filter(q => q.type === 'pre_populated').length
  }

  // Animation effect
  useEffect(() => {
    if (showOptimization) {
      const timer = setInterval(() => {
        setAnimationStep(prev => (prev + 1) % 4)
      }, 2000)
      return () => clearInterval(timer)
    }
  }, [showOptimization])

  const renderQuestionCard = (question, isOptimized = false) => {
    return (
      <Card key={question.id} className={`bg-gray-900 border-gray-700 ${isOptimized ? 'border-orange-500/50' : ''}`}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-white text-sm flex items-center gap-2">
              {question.type === 'consolidated' && <Sparkles className="h-4 w-4 text-blue-400" />}
              {question.type === 'pre_populated' && <Zap className="h-4 w-4 text-purple-400" />}
              {!question.type || question.type === 'standard' ? <Target className="h-4 w-4 text-gray-400" /> : null}
              {question.title || question.text}
            </CardTitle>
            {isOptimized && (
              <div className="flex gap-1">
                {question.type === 'consolidated' && (
                  <Badge variant="secondary" className="bg-blue-900 text-blue-300 text-xs">
                    <Clock className="h-3 w-3 mr-1" />
                    {question.timeSaved}
                  </Badge>
                )}
                {question.type === 'pre_populated' && (
                  <Badge variant="secondary" className="bg-purple-900 text-purple-300 text-xs">
                    <Zap className="h-3 w-3 mr-1" />
                    Auto-filled
                  </Badge>
                )}
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-2">
            <p className="text-gray-400 text-sm">{question.text}</p>
            
            {question.type === 'consolidated' && (
              <div className="p-2 bg-blue-900/20 border border-blue-500/30 rounded text-xs">
                <div className="text-blue-300">
                  Consolidates {question.originalCount} questions • Saves {question.timeSaved}
                </div>
              </div>
            )}
            
            {question.type === 'pre_populated' && (
              <div className="p-2 bg-purple-900/20 border border-purple-500/30 rounded text-xs">
                <div className="text-purple-300 mb-1">
                  Pre-filled: {question.prePopulatedValue}
                </div>
                <div className="text-purple-400">
                  {Math.round(question.confidence * 100)}% confidence from {question.source}
                </div>
              </div>
            )}
            
            <Badge variant="outline" className="text-xs border-gray-600 text-gray-400">
              {question.category?.replace('_', ' ')}
            </Badge>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-orange-500" />
            Question Optimization Demo
          </CardTitle>
          <CardDescription className="text-gray-400">
            See how our adaptive system consolidates questions and pre-populates answers to save you time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-red-400">{optimizationMetrics.originalQuestions}</div>
              <div className="text-xs text-gray-400">Original Questions</div>
            </div>
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-green-400">{optimizationMetrics.optimizedQuestions}</div>
              <div className="text-xs text-gray-400">Optimized Questions</div>
            </div>
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-orange-400">{optimizationMetrics.timeReduction}%</div>
              <div className="text-xs text-gray-400">Time Reduction</div>
            </div>
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-purple-400">{optimizationMetrics.questionsReduced}</div>
              <div className="text-xs text-gray-400">Questions Saved</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Demo Controls */}
      <div className="flex gap-2">
        <Button
          onClick={() => setCurrentView('comparison')}
          variant={currentView === 'comparison' ? 'default' : 'outline'}
          className={currentView === 'comparison' ? 'bg-orange-600 hover:bg-orange-700' : 'border-gray-600 text-gray-300'}
        >
          Side-by-Side Comparison
        </Button>
        <Button
          onClick={() => setCurrentView('interactive')}
          variant={currentView === 'interactive' ? 'default' : 'outline'}
          className={currentView === 'interactive' ? 'bg-orange-600 hover:bg-orange-700' : 'border-gray-600 text-gray-300'}
        >
          Interactive Demo
        </Button>
        <Button
          onClick={() => setShowOptimization(!showOptimization)}
          variant="outline"
          className="border-gray-600 text-gray-300 hover:bg-gray-800"
        >
          {showOptimization ? 'Stop' : 'Start'} Animation
        </Button>
      </div>

      {/* Content */}
      {currentView === 'comparison' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Original Questions */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Users className="h-5 w-5 text-red-500" />
                Original Approach
              </CardTitle>
              <CardDescription className="text-gray-400">
                Traditional assessment with {DEMO_QUESTIONS.original.length} individual questions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {DEMO_QUESTIONS.original.map((question) => renderQuestionCard(question, false))}
              </div>
              <div className="mt-4 p-3 bg-red-900/20 border border-red-500/30 rounded-lg">
                <div className="text-red-300 text-sm">
                  Estimated time: {DEMO_QUESTIONS.original.length * 1.5} minutes
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Optimized Questions */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-orange-500" />
                Adaptive Approach
              </CardTitle>
              <CardDescription className="text-gray-400">
                Optimized assessment with {DEMO_QUESTIONS.optimized.length} smart questions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {DEMO_QUESTIONS.optimized.map((question) => renderQuestionCard(question, true))}
              </div>
              <div className="mt-4 p-3 bg-green-900/20 border border-green-500/30 rounded-lg">
                <div className="text-green-300 text-sm">
                  Estimated time: {DEMO_QUESTIONS.optimized.length * 1.5} minutes
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {currentView === 'interactive' && (
        <Card className="bg-gray-900 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Interactive Question Demo</CardTitle>
            <CardDescription className="text-gray-400">
              Experience how adaptive questions work in real-time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="consolidated" className="w-full">
              <TabsList className="grid w-full grid-cols-2 bg-gray-800">
                <TabsTrigger value="consolidated" className="text-gray-300">Consolidated Questions</TabsTrigger>
                <TabsTrigger value="prepopulated" className="text-gray-300">Pre-populated Questions</TabsTrigger>
              </TabsList>

              <TabsContent value="consolidated" className="space-y-4">
                <div className="space-y-4">
                  <AdaptiveQuestionComponent
                    question={{
                      id: 'risk_tolerance_consolidated',
                      title: 'Risk Tolerance Assessment',
                      text: 'How would you describe your overall approach to risk in entrepreneurship?',
                      type: 'consolidated',
                      options: [
                        { value: 'high_risk', label: 'High Risk, High Reward' },
                        { value: 'calculated', label: 'Calculated Risk Taker' },
                        { value: 'moderate', label: 'Moderate Risk Comfort' },
                        { value: 'risk_averse', label: 'Risk Averse' }
                      ]
                    }}
                    phase="self_discovery"
                    showAdaptiveFeatures={true}
                  />
                </div>
              </TabsContent>

              <TabsContent value="prepopulated" className="space-y-4">
                <div className="space-y-4">
                  <AdaptiveQuestionComponent
                    question={{
                      id: 'industry_experience',
                      title: 'Industry Experience',
                      text: 'What is your industry experience level?',
                      type: 'pre_populated'
                    }}
                    phase="self_discovery"
                    showAdaptiveFeatures={true}
                  />
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {/* Optimization Benefits */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-500" />
            Optimization Benefits
          </CardTitle>
          <CardDescription className="text-gray-400">
            How adaptive questioning improves your assessment experience
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-gray-800 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="h-5 w-5 text-blue-400" />
                <span className="text-white font-medium">Question Consolidation</span>
              </div>
              <div className="text-sm text-gray-400 space-y-1">
                <div>• Combines similar questions into comprehensive assessments</div>
                <div>• Reduces redundancy while maintaining accuracy</div>
                <div>• Provides deeper insights with fewer questions</div>
              </div>
            </div>
            
            <div className="p-4 bg-gray-800 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-5 w-5 text-purple-400" />
                <span className="text-white font-medium">Smart Pre-population</span>
              </div>
              <div className="text-sm text-gray-400 space-y-1">
                <div>• Automatically fills answers based on your profile</div>
                <div>• Uses previous responses to predict answers</div>
                <div>• Maintains high confidence and accuracy</div>
              </div>
            </div>
            
            <div className="p-4 bg-gray-800 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <SkipForward className="h-5 w-5 text-green-400" />
                <span className="text-white font-medium">Intelligent Skipping</span>
              </div>
              <div className="text-sm text-gray-400 space-y-1">
                <div>• Skips irrelevant questions based on your responses</div>
                <div>• Adapts to your experience level and background</div>
                <div>• Focuses on what matters most for your profile</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Real-time Optimization Display */}
      {showOptimization && (
        <Card className="bg-gray-900 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-yellow-500" />
              Real-time Optimization
            </CardTitle>
            <CardDescription className="text-gray-400">
              Watch how the system optimizes questions in real-time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="text-sm text-gray-400 mb-2">Optimization Progress</div>
                  <Progress value={(animationStep + 1) * 25} className="h-2" />
                </div>
                <div className="text-white font-medium">{(animationStep + 1) * 25}%</div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className={`p-3 rounded-lg border ${animationStep >= 0 ? 'bg-blue-900/20 border-blue-500' : 'bg-gray-800 border-gray-600'}`}>
                  <div className="flex items-center gap-2">
                    <CheckCircle className={`h-4 w-4 ${animationStep >= 0 ? 'text-blue-400' : 'text-gray-500'}`} />
                    <span className="text-white text-sm">Analyzing Questions</span>
                  </div>
                </div>
                
                <div className={`p-3 rounded-lg border ${animationStep >= 1 ? 'bg-purple-900/20 border-purple-500' : 'bg-gray-800 border-gray-600'}`}>
                  <div className="flex items-center gap-2">
                    <CheckCircle className={`h-4 w-4 ${animationStep >= 1 ? 'text-purple-400' : 'text-gray-500'}`} />
                    <span className="text-white text-sm">Consolidating</span>
                  </div>
                </div>
                
                <div className={`p-3 rounded-lg border ${animationStep >= 2 ? 'bg-green-900/20 border-green-500' : 'bg-gray-800 border-gray-600'}`}>
                  <div className="flex items-center gap-2">
                    <CheckCircle className={`h-4 w-4 ${animationStep >= 2 ? 'text-green-400' : 'text-gray-500'}`} />
                    <span className="text-white text-sm">Pre-populating</span>
                  </div>
                </div>
                
                <div className={`p-3 rounded-lg border ${animationStep >= 3 ? 'bg-orange-900/20 border-orange-500' : 'bg-gray-800 border-gray-600'}`}>
                  <div className="flex items-center gap-2">
                    <CheckCircle className={`h-4 w-4 ${animationStep >= 3 ? 'text-orange-400' : 'text-gray-500'}`} />
                    <span className="text-white text-sm">Optimized</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

