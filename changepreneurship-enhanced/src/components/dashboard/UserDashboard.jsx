import React, { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useAssessment } from '../../contexts/AssessmentContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Progress } from '../ui/progress'
import { Badge } from '../ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
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
  Share2,
  RefreshCw
} from 'lucide-react'

const UserDashboard = () => {
  const { user, isAuthenticated } = useAuth()
  const { assessmentData, calculateOverallProgress, getCompletedPhases } = useAssessment()
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)

  // Phase definitions for the 7-part framework
  const phases = [
    { id: 'self_discovery', name: 'Self Discovery', duration: '60-90 min', category: 'Foundation' },
    { id: 'idea_discovery', name: 'Idea Discovery', duration: '90-120 min', category: 'Foundation' },
    { id: 'market_research', name: 'Market Research', duration: '2-3 weeks', category: 'Foundation' },
    { id: 'business_pillars', name: 'Business Pillars', duration: '1-2 weeks', category: 'Foundation' },
    { id: 'product_concept_testing', name: 'Product Concept Testing', duration: '3-4 days', category: 'Implementation' },
    { id: 'business_development', name: 'Business Development', duration: '1-2 weeks', category: 'Implementation' },
    { id: 'business_prototype_testing', name: 'Business Prototype Testing', duration: '2-4 weeks', category: 'Implementation' }
  ]

  useEffect(() => {
    if (isAuthenticated) {
      loadDashboardData()
    }
  }, [isAuthenticated, assessmentData])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Calculate dashboard metrics
      const overallProgress = calculateOverallProgress()
      const completedPhases = getCompletedPhases()
      const currentPhase = getCurrentPhase()
      const timeSpent = calculateTimeSpent()
      const achievements = calculateAchievements()
      const insights = generateInsights()

      setDashboardData({
        overallProgress,
        completedPhases: completedPhases.length,
        totalPhases: phases.length,
        currentPhase,
        timeSpent,
        achievements,
        insights,
        phaseProgress: phases.map(phase => ({
          ...phase,
          progress: assessmentData[phase.id]?.progress || 0,
          completed: assessmentData[phase.id]?.completed || false,
          lastUpdated: assessmentData[phase.id]?.lastUpdated
        }))
      })
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getCurrentPhase = () => {
    for (const phase of phases) {
      const phaseData = assessmentData[phase.id]
      if (!phaseData?.completed) {
        return phase
      }
    }
    return phases[phases.length - 1] // All completed
  }

  const calculateTimeSpent = () => {
    // Mock calculation - in real implementation, track actual time
    const completedCount = Object.values(assessmentData).filter(data => data?.completed).length
    return completedCount * 45 // Average 45 minutes per completed phase
  }

  const calculateAchievements = () => {
    const achievements = []
    const completedCount = Object.values(assessmentData).filter(data => data?.completed).length
    
    if (completedCount >= 1) achievements.push({ name: 'First Steps', description: 'Completed your first assessment phase', icon: '🎯' })
    if (completedCount >= 4) achievements.push({ name: 'Foundation Builder', description: 'Completed all foundation phases', icon: '🏗️' })
    if (completedCount >= 7) achievements.push({ name: 'Journey Complete', description: 'Completed the entire assessment', icon: '🏆' })
    
    // Check for specific achievements
    if (assessmentData['self_discovery']?.archetype) {
      achievements.push({ name: 'Self-Aware', description: 'Discovered your entrepreneur archetype', icon: '🧠' })
    }
    
    return achievements
  }

  const generateInsights = () => {
    const insights = []
    const completedCount = Object.values(assessmentData).filter(data => data?.completed).length
    const overallProgress = calculateOverallProgress()
    
    if (overallProgress > 75) {
      insights.push({
        type: 'success',
        title: 'Excellent Progress!',
        description: 'You\'re well on your way to completing your entrepreneurial assessment.'
      })
    } else if (overallProgress > 25) {
      insights.push({
        type: 'info',
        title: 'Keep Going!',
        description: 'You\'ve made good progress. Continue with the next phase to build momentum.'
      })
    } else {
      insights.push({
        type: 'warning',
        title: 'Get Started',
        description: 'Begin your entrepreneurial journey by completing the Self Discovery assessment.'
      })
    }

    return insights
  }

  const exportData = () => {
    const exportData = {
      user: user,
      assessmentData: assessmentData,
      dashboardData: dashboardData,
      exportDate: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `changepreneurship-assessment-${user?.username || 'user'}-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <Card className="w-full max-w-md bg-gray-800 border-gray-700">
          <CardHeader className="text-center">
            <CardTitle className="text-white">Sign In Required</CardTitle>
            <CardDescription className="text-gray-400">
              Please sign in to view your dashboard and assessment progress.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Button className="bg-orange-600 hover:bg-orange-700">
              Sign In to Continue
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (loading) {
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
                <User className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Welcome back, {user?.username}!</h1>
                <p className="text-gray-400">Track your entrepreneurial journey progress</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Button variant="outline" onClick={exportData} className="border-gray-600 text-gray-300 hover:bg-gray-700">
                <Download className="h-4 w-4 mr-2" />
                Export Data
              </Button>
              <Button variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-700">
                <Share2 className="h-4 w-4 mr-2" />
                Share Progress
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="bg-gray-800 border-gray-700">
            <TabsTrigger value="overview" className="data-[state=active]:bg-orange-600">Overview</TabsTrigger>
            <TabsTrigger value="progress" className="data-[state=active]:bg-orange-600">Progress</TabsTrigger>
            <TabsTrigger value="insights" className="data-[state=active]:bg-orange-600">Insights</TabsTrigger>
            <TabsTrigger value="achievements" className="data-[state=active]:bg-orange-600">Achievements</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">Overall Progress</CardTitle>
                  <TrendingUp className="h-4 w-4 text-orange-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">{dashboardData?.overallProgress || 0}%</div>
                  <Progress value={dashboardData?.overallProgress || 0} className="mt-2" />
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">Completed Phases</CardTitle>
                  <CheckCircle className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">
                    {dashboardData?.completedPhases || 0}/{dashboardData?.totalPhases || 7}
                  </div>
                  <p className="text-xs text-gray-400 mt-1">phases completed</p>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">Time Invested</CardTitle>
                  <Clock className="h-4 w-4 text-blue-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">{dashboardData?.timeSpent || 0}m</div>
                  <p className="text-xs text-gray-400 mt-1">minutes spent</p>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">Current Phase</CardTitle>
                  <Target className="h-4 w-4 text-purple-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-lg font-bold text-white">{dashboardData?.currentPhase?.name || 'Not Started'}</div>
                  <p className="text-xs text-gray-400 mt-1">{dashboardData?.currentPhase?.category || ''}</p>
                </CardContent>
              </Card>
            </div>

            {/* Current Phase Focus */}
            {dashboardData?.currentPhase && (
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Target className="h-5 w-5 mr-2 text-orange-600" />
                    Continue Your Journey
                  </CardTitle>
                  <CardDescription className="text-gray-400">
                    Your next step in the entrepreneurial assessment
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-white">{dashboardData.currentPhase.name}</h3>
                      <p className="text-gray-400">Estimated time: {dashboardData.currentPhase.duration}</p>
                      <Badge variant="outline" className="mt-2 border-orange-600 text-orange-600">
                        {dashboardData.currentPhase.category}
                      </Badge>
                    </div>
                    <Button className="bg-orange-600 hover:bg-orange-700">
                      Continue Assessment
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Recent Insights */}
            {dashboardData?.insights && dashboardData.insights.length > 0 && (
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <BarChart3 className="h-5 w-5 mr-2 text-orange-600" />
                    Insights & Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {dashboardData.insights.map((insight, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className={`p-2 rounded-lg ${
                        insight.type === 'success' ? 'bg-green-900 text-green-400' :
                        insight.type === 'warning' ? 'bg-yellow-900 text-yellow-400' :
                        'bg-blue-900 text-blue-400'
                      }`}>
                        {insight.type === 'success' ? <CheckCircle className="h-4 w-4" /> :
                         insight.type === 'warning' ? <AlertCircle className="h-4 w-4" /> :
                         <BarChart3 className="h-4 w-4" />}
                      </div>
                      <div>
                        <h4 className="font-semibold text-white">{insight.title}</h4>
                        <p className="text-gray-400 text-sm">{insight.description}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Progress Tab */}
          <TabsContent value="progress" className="space-y-6">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Assessment Progress</CardTitle>
                <CardDescription className="text-gray-400">
                  Track your progress through all 7 phases of the entrepreneurial journey
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {dashboardData?.phaseProgress?.map((phase, index) => (
                    <div key={phase.id} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                            phase.completed ? 'bg-green-600 text-white' : 
                            phase.progress > 0 ? 'bg-orange-600 text-white' : 
                            'bg-gray-600 text-gray-400'
                          }`}>
                            {phase.completed ? '✓' : index + 1}
                          </div>
                          <div>
                            <h3 className="font-semibold text-white">{phase.name}</h3>
                            <p className="text-sm text-gray-400">{phase.duration} • {phase.category}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-white">{phase.progress}%</div>
                          {phase.lastUpdated && (
                            <div className="text-xs text-gray-400">
                              {new Date(phase.lastUpdated).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                      </div>
                      <Progress value={phase.progress} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Insights Tab */}
          <TabsContent value="insights" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white">Entrepreneur Profile</CardTitle>
                </CardHeader>
                <CardContent>
                  {assessmentData['self_discovery']?.archetype ? (
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-600">
                          {assessmentData['self_discovery'].archetype.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </div>
                        <p className="text-gray-400 mt-2">Your Entrepreneur Archetype</p>
                      </div>
                      {/* Add more archetype details here */}
                    </div>
                  ) : (
                    <div className="text-center text-gray-400">
                      <p>Complete the Self Discovery assessment to see your entrepreneur profile</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white">Journey Timeline</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(assessmentData).map(([phaseId, data]) => {
                      if (data?.lastUpdated) {
                        const phase = phases.find(p => p.id === phaseId)
                        return (
                          <div key={phaseId} className="flex items-center space-x-3">
                            <Calendar className="h-4 w-4 text-orange-600" />
                            <div>
                              <div className="text-sm font-semibold text-white">{phase?.name}</div>
                              <div className="text-xs text-gray-400">
                                {new Date(data.lastUpdated).toLocaleDateString()}
                              </div>
                            </div>
                          </div>
                        )
                      }
                      return null
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Achievements Tab */}
          <TabsContent value="achievements" className="space-y-6">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Award className="h-5 w-5 mr-2 text-orange-600" />
                  Your Achievements
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Milestones you've reached on your entrepreneurial journey
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {dashboardData?.achievements?.map((achievement, index) => (
                    <div key={index} className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                      <div className="text-2xl mb-2">{achievement.icon}</div>
                      <h3 className="font-semibold text-white">{achievement.name}</h3>
                      <p className="text-sm text-gray-400 mt-1">{achievement.description}</p>
                    </div>
                  ))}
                  
                  {(!dashboardData?.achievements || dashboardData.achievements.length === 0) && (
                    <div className="col-span-full text-center text-gray-400 py-8">
                      <Star className="h-12 w-12 mx-auto mb-4 text-gray-600" />
                      <p>Complete assessment phases to unlock achievements!</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default UserDashboard

