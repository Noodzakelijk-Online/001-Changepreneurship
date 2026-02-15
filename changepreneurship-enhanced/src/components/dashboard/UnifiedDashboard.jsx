import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useAssessment } from '../../contexts/AssessmentContext'
import useDashboardData from '../../hooks/useDashboardData'
import { phaseIdToSlug } from '../../lib/assessmentPhases'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Progress } from '../ui/progress'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { 
  User, 
  TrendingUp, 
  Calendar, 
  Target, 
  Award, 
  BarChart3, 
  Clock, 
  CheckCircle,
  AlertCircle,
  Star,
  Download,
  RefreshCw,
  Brain,
  Lightbulb,
  ArrowRight,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

const UnifiedDashboard = () => {
  const { user, isAuthenticated } = useAuth()
  const { getOverallProgress } = useAssessment()
  const { metrics, profile, responses, insights, loading, error, refresh, hasData } = useDashboardData()
  const [expandedPhases, setExpandedPhases] = useState({})
  const [showAllResponses, setShowAllResponses] = useState(false)

  // Phase definitions
  const phases = [
    { id: 'self_discovery', name: 'Self Discovery', emoji: '🧭', category: 'Foundation' },
    { id: 'idea_discovery', name: 'Idea Discovery', emoji: '💡', category: 'Foundation' },
    { id: 'market_research', name: 'Market Research', emoji: '🔍', category: 'Foundation' },
    { id: 'business_pillars', name: 'Business Pillars', emoji: '🏛️', category: 'Foundation' },
    { id: 'product_concept_testing', name: 'Product Testing', emoji: '🧪', category: 'Implementation' },
    { id: 'business_development', name: 'Business Development', emoji: '📈', category: 'Implementation' },
    { id: 'business_prototype_testing', name: 'Prototype Testing', emoji: '🚀', category: 'Implementation' }
  ]

  const togglePhaseExpand = (phaseId) => {
    setExpandedPhases(prev => ({ ...prev, [phaseId]: !prev[phaseId] }))
  }

  const exportData = () => {
    const exportObj = {
      user: { id: user?.id, username: user?.username, email: user?.email },
      metrics,
      profile,
      responses: responses?.responses || [],
      insights,
      exported_at: new Date().toISOString()
    }
    const blob = new Blob([JSON.stringify(exportObj, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `dashboard-export-${user?.username || 'user'}-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Calculate metrics from available data
  // Prioritize insights (executive-summary) over metrics (analytics/overview)
  const overallProgress = getOverallProgress() || metrics?.overall_progress || 0
  const totalTime = metrics?.total_time_spent || 0
  const aiScore = insights?.overall_score || profile?.success_probability || 0
  const totalResponses = responses?.total_responses || 0
  
  // Calculate completed phases from responses data
  const completedPhasesFromResponses = phases.filter(phase => {
    const phaseResponses = responses?.by_phase?.[phase.id]
    return phaseResponses && phaseResponses.length >= 10
  }).length
  
  const completedPhasesCount = completedPhasesFromResponses || metrics?.completed_phases || 0

  // Debug logging
  console.log('[UnifiedDashboard] Data:', {
    overallProgress,
    completedPhasesCount,
    aiScore,
    totalResponses,
    insightsAvailable: !!insights,
    insightsScore: insights?.overall_score,
    keyInsightsCount: insights?.ai_insights?.key_insights?.length,
    responsesById: Object.keys(responses?.by_phase || {})
  })

  // Get next steps
  const getNextSteps = () => {
    const steps = []
    
    // Check incomplete phases
    phases.forEach(phase => {
      const phaseResponses = responses?.by_phase?.[phase.id]
      if (!phaseResponses || phaseResponses.length < 10) {
        const remaining = 10 - (phaseResponses?.length || 0)
        const slug = phaseIdToSlug(phase.id) || phase.id
        steps.push({
          type: 'assessment',
          icon: '📝',
          text: `Complete ${remaining} remaining questions in ${phase.name}`,
          link: `/assessment/${slug}`
        })
      }
    })

    // AI recommendations
    if (aiScore > 0 && totalResponses > 10) {
      steps.push({
        type: 'insights',
        icon: '🧠',
        text: 'Review your AI-powered business insights',
        link: '#ai-insights'
      })
    }

    return steps.slice(0, 3) // Top 3 next steps
  }

  const nextSteps = getNextSteps()

  // Top AI insights (max 3)
  const topInsights = insights?.ai_insights?.key_insights?.slice(0, 3) || []

  // Recent responses (max 5)
  const recentResponses = responses?.responses?.slice(0, showAllResponses ? undefined : 5) || []

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <Card className="w-full max-w-md bg-gray-800 border-gray-700">
          <CardHeader className="text-center">
            <CardTitle className="text-white">Sign In Required</CardTitle>
            <CardDescription className="text-gray-400">
              Please sign in to view your dashboard.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  if (loading && !hasData) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="flex items-center space-x-2 text-white">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span>Loading your dashboard...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-orange-600 p-3 rounded-lg">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">My Entrepreneurial Dashboard</h1>
                <p className="text-gray-400">Complete overview of your journey</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Button 
                variant="outline" 
                onClick={refresh} 
                disabled={loading}
                className="border-gray-600 text-gray-300 hover:bg-gray-700"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button 
                variant="outline" 
                onClick={exportData}
                className="border-gray-600 text-gray-300 hover:bg-gray-700"
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Compact Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Progress</p>
                  <p className="text-3xl font-bold text-white">{Math.round(overallProgress)}%</p>
                </div>
                <TrendingUp className="h-8 w-8 text-orange-600" />
              </div>
              <Progress value={overallProgress} className="mt-3 h-2" />
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Phases</p>
                  <p className="text-3xl font-bold text-white">{completedPhasesCount}/7</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <p className="text-xs text-gray-400 mt-3">phases completed</p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Time</p>
                  <p className="text-3xl font-bold text-white">{totalTime}m</p>
                </div>
                <Clock className="h-8 w-8 text-blue-600" />
              </div>
              <p className="text-xs text-gray-400 mt-3">minutes invested</p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">AI Score</p>
                  <p className="text-3xl font-bold text-white">{Math.round(aiScore)}%</p>
                </div>
                <Brain className="h-8 w-8 text-purple-600" />
              </div>
              <p className="text-xs text-gray-400 mt-3">success probability</p>
            </CardContent>
          </Card>
        </div>

        {/* Next Steps Section */}
        {nextSteps.length > 0 && (
          <Card className="bg-gradient-to-r from-orange-900/20 to-orange-800/20 border-orange-600/50">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Target className="h-5 w-5 mr-2 text-orange-500" />
                Next Steps for You
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {nextSteps.map((step, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{step.icon}</span>
                      <span className="text-white">{step.text}</span>
                    </div>
                    {step.link && (
                      <Link to={step.link}>
                        <Button size="sm" variant="outline" className="border-orange-600 text-orange-400 hover:bg-orange-900/30">
                          Go <ArrowRight className="h-4 w-4 ml-1" />
                        </Button>
                      </Link>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Two Column Layout: Progress + AI Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Left: Phase Progress */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <BarChart3 className="h-5 w-5 mr-2 text-orange-600" />
                Phase Progress
              </CardTitle>
              <CardDescription className="text-gray-400">
                Track your journey through all 7 assessment phases
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {phases.map((phase) => {
                const phaseResponses = responses?.by_phase?.[phase.id] || []
                const phaseProgress = phaseResponses.length > 0 ? Math.min(100, (phaseResponses.length / 10) * 100) : 0
                const isCompleted = phaseProgress === 100

                return (
                  <div key={phase.id} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="text-xl">{phase.emoji}</span>
                        <span className={`text-sm ${isCompleted ? 'text-green-400' : 'text-white'}`}>
                          {phase.name}
                        </span>
                        {isCompleted && <CheckCircle className="h-4 w-4 text-green-600" />}
                      </div>
                      <span className="text-sm text-gray-400">{Math.round(phaseProgress)}%</span>
                    </div>
                    <Progress value={phaseProgress} className="h-2" />
                    <p className="text-xs text-gray-500">{phaseResponses.length} responses</p>
                  </div>
                )
              })}
            </CardContent>
          </Card>

          {/* Right: AI Insights */}
          <Card className="bg-gray-800 border-gray-700" id="ai-insights">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Brain className="h-5 w-5 mr-2 text-purple-600" />
                AI Insights
              </CardTitle>
              <CardDescription className="text-gray-400">
                AI-powered analysis of your business readiness
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {topInsights.length > 0 ? (
                <>
                  {topInsights.map((insight, idx) => (
                    <div key={idx} className="flex items-start space-x-3 p-3 bg-gray-900/50 rounded-lg">
                      <div className="mt-1">
                        {insight.type === 'strength' && <CheckCircle className="h-5 w-5 text-green-500" />}
                        {insight.type === 'warning' && <AlertCircle className="h-5 w-5 text-yellow-500" />}
                        {insight.type === 'recommendation' && <Lightbulb className="h-5 w-5 text-blue-500" />}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-white text-sm">{insight.title || insight.category}</h4>
                        <p className="text-gray-400 text-sm mt-1">{insight.description || insight.insight}</p>
                      </div>
                    </div>
                  ))}
                  <Link to="/dashboard/executive-summary">
                    <Button variant="outline" className="w-full border-purple-600 text-purple-400 hover:bg-purple-900/30">
                      View Full AI Analysis <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </Link>
                </>
              ) : (
                <div className="text-center py-8">
                  <Brain className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">Complete more assessments to unlock AI insights</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* My Responses Section */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-white flex items-center">
                  <Calendar className="h-5 w-5 mr-2 text-blue-600" />
                  My Assessment Responses ({totalResponses} total)
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Your answers across all assessment phases
                </CardDescription>
              </div>
              {totalResponses > 5 && (
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setShowAllResponses(!showAllResponses)}
                  className="text-gray-400 hover:text-white"
                >
                  {showAllResponses ? (
                    <>Show Less <ChevronUp className="h-4 w-4 ml-1" /></>
                  ) : (
                    <>Show All <ChevronDown className="h-4 w-4 ml-1" /></>
                  )}
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {recentResponses.length > 0 ? (
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {recentResponses.map((response) => {
                  const phase = phases.find(p => p.id === response.phase_id)
                  return (
                    <div key={response.id} className="border-l-4 border-orange-600 pl-4 py-3 bg-gray-900/30 rounded-r-lg">
                      <div className="flex items-center justify-between mb-2">
                        <Badge variant="outline" className="border-orange-600 text-orange-400">
                          {phase?.emoji} {phase?.name || response.phase_id}
                        </Badge>
                        <span className="text-xs text-gray-500">
                          {new Date(response.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-400 mb-2">{response.question_text}</p>
                      <p className="text-white">{response.response_value}</p>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-12">
                <Calendar className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400 mb-4">No responses yet. Start your assessment journey!</p>
                <Link to="/assessment">
                  <Button className="bg-orange-600 hover:bg-orange-700">
                    Start Assessment <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

      </div>
    </div>
  )
}

export default UnifiedDashboard
