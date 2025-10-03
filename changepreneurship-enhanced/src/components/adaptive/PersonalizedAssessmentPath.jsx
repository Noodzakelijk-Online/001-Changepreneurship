import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Progress } from '../ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { 
  CheckCircle, 
  Clock, 
  Target, 
  Zap, 
  SkipForward,
  TrendingUp,
  Users,
  Lightbulb,
  ArrowRight,
  Star,
  Award,
  BarChart3
} from 'lucide-react'
import { useEnhancedAssessment } from '../../contexts/EnhancedAssessmentContext'

export default function PersonalizedAssessmentPath() {
  const {
    assessmentData,
    currentPhase,
    adaptiveState,
    userProfile,
    getAllResponses,
    getAdaptiveProgress,
    getSkippedQuestions,
    getPrePopulatedAnswers,
    getCurrentPath,
    getAssessmentSummary,
    updatePhase
  } = useEnhancedAssessment()

  const [selectedPhase, setSelectedPhase] = useState(currentPhase)
  const currentPath = getCurrentPath()
  const assessmentSummary = getAssessmentSummary()
  const allResponses = getAllResponses()

  // Assessment phases with adaptive data
  const phases = [
    {
      id: 'self_discovery',
      name: 'Self Discovery',
      description: 'Understanding your entrepreneurial personality and motivations',
      icon: Users,
      color: 'bg-blue-500',
      estimatedTime: '60-90 min'
    },
    {
      id: 'idea_discovery',
      name: 'Idea Discovery',
      description: 'Identifying and validating business opportunities',
      icon: Lightbulb,
      color: 'bg-yellow-500',
      estimatedTime: '90-120 min'
    },
    {
      id: 'market_research',
      name: 'Market Research',
      description: 'Analyzing market conditions and competitive landscape',
      icon: BarChart3,
      color: 'bg-green-500',
      estimatedTime: '2-3 weeks'
    },
    {
      id: 'business_pillars',
      name: 'Business Pillars',
      description: 'Building comprehensive business foundation',
      icon: Target,
      color: 'bg-purple-500',
      estimatedTime: '1-2 weeks'
    },
    {
      id: 'product_concept_testing',
      name: 'Product Concept Testing',
      description: 'Validating product concepts with target market',
      icon: Star,
      color: 'bg-orange-500',
      estimatedTime: '1-2 weeks'
    },
    {
      id: 'business_development',
      name: 'Business Development',
      description: 'Strategic business development and decision making',
      icon: TrendingUp,
      color: 'bg-red-500',
      estimatedTime: '2-3 weeks'
    },
    {
      id: 'business_prototype_testing',
      name: 'Business Prototype Testing',
      description: 'Testing business prototypes and market readiness',
      icon: Award,
      color: 'bg-indigo-500',
      estimatedTime: '3-4 weeks'
    }
  ]

  // Get adaptive data for selected phase
  const getPhaseAdaptiveData = (phaseId) => {
    const phaseData = assessmentData[phaseId]
    if (!phaseData) return null

    return {
      progress: phaseData.progress || 0,
      adaptiveProgress: getAdaptiveProgress(phaseId),
      skippedQuestions: getSkippedQuestions(phaseId),
      prePopulatedAnswers: getPrePopulatedAnswers(phaseId),
      completed: phaseData.completed || false,
      responses: Object.keys(phaseData.responses || {}).length
    }
  }

  // Calculate overall adaptive progress
  const calculateOverallProgress = () => {
    const totalPhases = phases.length
    let completedPhases = 0
    let totalProgress = 0

    phases.forEach(phase => {
      const adaptiveData = getPhaseAdaptiveData(phase.id)
      if (adaptiveData) {
        if (adaptiveData.completed) completedPhases++
        totalProgress += adaptiveData.adaptiveProgress || 0
      }
    })

    return {
      completedPhases,
      totalPhases,
      averageProgress: totalProgress / totalPhases,
      overallCompletion: (completedPhases / totalPhases) * 100
    }
  }

  const overallProgress = calculateOverallProgress()
  const selectedPhaseData = getPhaseAdaptiveData(selectedPhase)

  return (
    <div className="space-y-6">
      {/* Overall Progress Header */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Target className="h-5 w-5 text-orange-500" />
            Your Personalized Assessment Journey
          </CardTitle>
          <CardDescription className="text-gray-400">
            {currentPath?.name} - Optimized for your experience level
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Progress Overview */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <div className="text-2xl font-bold text-orange-500">
                  {overallProgress.completedPhases}/{overallProgress.totalPhases}
                </div>
                <div className="text-xs text-gray-400">Phases Complete</div>
              </div>
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <div className="text-2xl font-bold text-blue-500">
                  {Math.round(overallProgress.averageProgress)}%
                </div>
                <div className="text-xs text-gray-400">Overall Progress</div>
              </div>
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <div className="text-2xl font-bold text-green-500">
                  {currentPath?.estimatedTime || 'N/A'}
                </div>
                <div className="text-xs text-gray-400">Time Estimate</div>
              </div>
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <div className="text-2xl font-bold text-purple-500">
                  {Object.keys(allResponses).length}
                </div>
                <div className="text-xs text-gray-400">Total Responses</div>
              </div>
            </div>

            {/* Overall Progress Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Assessment Progress</span>
                <span className="text-white">{Math.round(overallProgress.averageProgress)}%</span>
              </div>
              <Progress value={overallProgress.averageProgress} className="h-3" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Phase Selection and Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Phase List */}
        <div className="lg:col-span-1">
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white text-lg">Assessment Phases</CardTitle>
              <CardDescription className="text-gray-400">
                Click to view phase details
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {phases.map((phase) => {
                  const adaptiveData = getPhaseAdaptiveData(phase.id)
                  const IconComponent = phase.icon
                  const isSelected = selectedPhase === phase.id
                  const isCurrent = currentPhase === phase.id

                  return (
                    <button
                      key={phase.id}
                      onClick={() => setSelectedPhase(phase.id)}
                      className={`w-full p-3 rounded-lg border transition-all ${
                        isSelected 
                          ? 'bg-orange-900 border-orange-500' 
                          : 'bg-gray-800 border-gray-600 hover:bg-gray-700'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-full ${phase.color}`}>
                          <IconComponent className="h-4 w-4 text-white" />
                        </div>
                        <div className="flex-1 text-left">
                          <div className="flex items-center gap-2">
                            <span className="text-white font-medium text-sm">{phase.name}</span>
                            {isCurrent && (
                              <Badge variant="secondary" className="bg-orange-900 text-orange-300 text-xs">
                                Current
                              </Badge>
                            )}
                            {adaptiveData?.completed && (
                              <CheckCircle className="h-4 w-4 text-green-500" />
                            )}
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            {adaptiveData ? `${Math.round(adaptiveData.adaptiveProgress)}% complete` : 'Not started'}
                          </div>
                        </div>
                      </div>
                    </button>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Phase Details */}
        <div className="lg:col-span-2">
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                {(() => {
                  const phase = phases.find(p => p.id === selectedPhase)
                  const IconComponent = phase?.icon || Target
                  return <IconComponent className="h-5 w-5 text-orange-500" />
                })()}
                {phases.find(p => p.id === selectedPhase)?.name}
              </CardTitle>
              <CardDescription className="text-gray-400">
                {phases.find(p => p.id === selectedPhase)?.description}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedPhaseData ? (
                <Tabs defaultValue="progress" className="w-full">
                  <TabsList className="grid w-full grid-cols-3 bg-gray-800">
                    <TabsTrigger value="progress" className="text-gray-300">Progress</TabsTrigger>
                    <TabsTrigger value="adaptive" className="text-gray-300">Adaptive</TabsTrigger>
                    <TabsTrigger value="insights" className="text-gray-300">Insights</TabsTrigger>
                  </TabsList>

                  <TabsContent value="progress" className="space-y-4">
                    <div className="space-y-4">
                      {/* Progress Stats */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-gray-800 rounded-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <Target className="h-4 w-4 text-blue-500" />
                            <span className="text-white font-medium">Standard Progress</span>
                          </div>
                          <div className="text-2xl font-bold text-blue-500">
                            {Math.round(selectedPhaseData.progress)}%
                          </div>
                        </div>
                        <div className="p-4 bg-gray-800 rounded-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <Zap className="h-4 w-4 text-purple-500" />
                            <span className="text-white font-medium">Adaptive Progress</span>
                          </div>
                          <div className="text-2xl font-bold text-purple-500">
                            {Math.round(selectedPhaseData.adaptiveProgress)}%
                          </div>
                        </div>
                      </div>

                      {/* Progress Bars */}
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-400">Standard Progress</span>
                            <span className="text-white">{Math.round(selectedPhaseData.progress)}%</span>
                          </div>
                          <Progress value={selectedPhaseData.progress} className="h-2" />
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-400">Adaptive Progress</span>
                            <span className="text-white">{Math.round(selectedPhaseData.adaptiveProgress)}%</span>
                          </div>
                          <Progress value={selectedPhaseData.adaptiveProgress} className="h-2 bg-purple-900" />
                        </div>
                      </div>

                      {/* Action Button */}
                      <div className="flex gap-2">
                        {selectedPhase === currentPhase ? (
                          <Button className="bg-orange-600 hover:bg-orange-700 text-white">
                            Continue Assessment
                          </Button>
                        ) : (
                          <Button 
                            onClick={() => updatePhase(selectedPhase)}
                            variant="outline"
                            className="border-gray-600 text-gray-300 hover:bg-gray-800"
                          >
                            Switch to This Phase
                          </Button>
                        )}
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="adaptive" className="space-y-4">
                    <div className="space-y-4">
                      {/* Adaptive Features */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 bg-gray-800 rounded-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <SkipForward className="h-4 w-4 text-green-500" />
                            <span className="text-white font-medium">Questions Skipped</span>
                          </div>
                          <div className="text-2xl font-bold text-green-500">
                            {selectedPhaseData.skippedQuestions.length}
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            Irrelevant questions automatically skipped
                          </div>
                        </div>
                        <div className="p-4 bg-gray-800 rounded-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <Zap className="h-4 w-4 text-purple-500" />
                            <span className="text-white font-medium">Pre-populated</span>
                          </div>
                          <div className="text-2xl font-bold text-purple-500">
                            {Object.keys(selectedPhaseData.prePopulatedAnswers).length}
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            Answers filled automatically
                          </div>
                        </div>
                      </div>

                      {/* Time Savings */}
                      <div className="p-4 bg-gray-800 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Clock className="h-4 w-4 text-orange-500" />
                          <span className="text-white font-medium">Time Optimization</span>
                        </div>
                        <div className="text-sm text-gray-400">
                          Estimated time saved: {Math.round((selectedPhaseData.skippedQuestions.length + Object.keys(selectedPhaseData.prePopulatedAnswers).length) * 0.5)} minutes
                        </div>
                      </div>

                      {/* Skipped Questions List */}
                      {selectedPhaseData.skippedQuestions.length > 0 && (
                        <div className="p-4 bg-gray-800 rounded-lg">
                          <h5 className="text-white font-medium mb-2">Skipped Question Categories</h5>
                          <div className="space-y-1">
                            {selectedPhaseData.skippedQuestions.slice(0, 5).map((questionId, index) => (
                              <div key={index} className="text-sm text-gray-400 flex items-center gap-2">
                                <SkipForward className="h-3 w-3 text-green-500" />
                                {questionId.replace('_', ' ').replace('-', ' ')}
                              </div>
                            ))}
                            {selectedPhaseData.skippedQuestions.length > 5 && (
                              <div className="text-sm text-gray-500">
                                +{selectedPhaseData.skippedQuestions.length - 5} more...
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </TabsContent>

                  <TabsContent value="insights" className="space-y-4">
                    <div className="space-y-4">
                      {/* Phase Insights */}
                      <div className="p-4 bg-gray-800 rounded-lg">
                        <h5 className="text-white font-medium mb-2">Phase Insights</h5>
                        <div className="space-y-2 text-sm text-gray-400">
                          <div>• {selectedPhaseData.responses} responses collected</div>
                          <div>• {selectedPhaseData.skippedQuestions.length} questions optimized away</div>
                          <div>• {Object.keys(selectedPhaseData.prePopulatedAnswers).length} answers pre-filled</div>
                          <div>• {Math.round(selectedPhaseData.adaptiveProgress)}% adaptive completion</div>
                        </div>
                      </div>

                      {/* Recommendations */}
                      {assessmentSummary?.recommendations && (
                        <div className="p-4 bg-gray-800 rounded-lg">
                          <h5 className="text-white font-medium mb-2">Personalized Recommendations</h5>
                          <div className="space-y-2">
                            {assessmentSummary.recommendations.slice(0, 3).map((rec, index) => (
                              <div key={index} className="text-sm text-gray-400 flex items-start gap-2">
                                <ArrowRight className="h-3 w-3 text-orange-500 mt-0.5 flex-shrink-0" />
                                {rec}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </TabsContent>
                </Tabs>
              ) : (
                <div className="text-center py-8">
                  <div className="text-gray-400 mb-4">This phase hasn't been started yet</div>
                  <Button 
                    onClick={() => updatePhase(selectedPhase)}
                    className="bg-orange-600 hover:bg-orange-700 text-white"
                  >
                    Start This Phase
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

