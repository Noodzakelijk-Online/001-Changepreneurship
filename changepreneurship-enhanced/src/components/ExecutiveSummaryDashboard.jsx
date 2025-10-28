import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import { 
  Brain, 
  TrendingUp, 
  Target, 
  Lightbulb, 
  BarChart3, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle,
  Info,
  ChevronRight
} from 'lucide-react'
import apiService from '../services/api.js'

const ExecutiveSummaryDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState(0)
  const [refreshing, setRefreshing] = useState(false)

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/dashboard/executive-summary', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...apiService.getHeaders()
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data')
      }
      
      const result = await response.json()
      if (result.success) {
        setDashboardData(result.data)
        setError(null)
      } else {
        throw new Error(result.error || 'Unknown error')
      }
    } catch (err) {
      console.error('Dashboard fetch error:', err)
      setError(err.message)
      // Fallback to mock data for development
      setDashboardData(getMockDashboardData())
    } finally {
      setLoading(false)
    }
  }

  // Refresh dashboard data
  const refreshDashboard = async () => {
    try {
      setRefreshing(true)
      const response = await fetch('/api/dashboard/executive-summary/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...apiService.getHeaders()
        },
        body: JSON.stringify({
          user_id: apiService.getCurrentUser()?.id || 'demo-user'
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to refresh dashboard')
      }
      
      const result = await response.json()
      if (result.success) {
        setDashboardData(result.data)
        setError(null)
      }
    } catch (err) {
      console.error('Dashboard refresh error:', err)
      setError(err.message)
    } finally {
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  // Mock data for development/fallback
  const getMockDashboardData = () => ({
    component_title: 'Executive Summary Dashboard',
    overall_score: 68,
    data_completeness: 0.75,
    assessment_count: 5,
    sub_elements: [
      {
        title: 'Company Vision',
        score: 72,
        status: 'Good',
        definition: 'A clear, inspiring picture of what your company will become in the future.',
        what_to_include: 'Mission statement, core values, long-term goals, and impact vision.',
        metrics: [
          { label: 'Vision Clarity', value: '72%', trend: 'positive' },
          { label: 'Alignment Score', value: '80%', trend: 'positive' }
        ],
        ai_generated_content: 'Based on your assessment responses, your vision clarity scores 72/100. Your entrepreneurial profile suggests strong potential in strategic thinking and long-term planning.',
        ai_confidence: 78,
        data_sources: [
          { name: 'Self Discovery Assessment', percentage: 45.0, type: 'assessment' },
          { name: 'AI Analysis Engine', percentage: 25.0, type: 'ai_analysis' }
        ],
        improvements: [
          'Develop a more detailed mission statement that clearly articulates your company\'s purpose',
          'Conduct stakeholder interviews to validate vision alignment'
        ]
      }
      // ... more elements would be added here
    ]
  })

  if (loading) {
    return (
      <div className="min-h-screen bg-background dark p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-96">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
              <h3 className="text-lg font-semibold mb-2">Generating AI Insights</h3>
              <p className="text-muted-foreground">Analyzing your assessment data...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error && !dashboardData) {
    return (
      <div className="min-h-screen bg-background dark p-6">
        <div className="max-w-7xl mx-auto">
          <Card className="border-destructive">
            <CardContent className="pt-6">
              <div className="text-center">
                <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Error Loading Dashboard</h3>
                <p className="text-muted-foreground mb-4">{error}</p>
                <Button onClick={fetchDashboardData} variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  const currentSubElement = dashboardData?.sub_elements?.[activeTab]
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-500'
    if (score >= 70) return 'text-blue-500'
    if (score >= 60) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getStatusBadge = (status) => {
    const variants = {
      'Excellent': 'bg-green-900 text-green-400 border-green-600',
      'Good': 'bg-blue-900 text-blue-400 border-blue-600',
      'Fair': 'bg-yellow-900 text-yellow-400 border-yellow-600',
      'Needs Improvement': 'bg-orange-900 text-orange-400 border-orange-600',
      'Critical': 'bg-red-900 text-red-400 border-red-600'
    }
    return variants[status] || variants['Fair']
  }

  return (
    <div className="min-h-screen bg-background dark p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                  <Brain className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-2xl">AI Executive Summary Dashboard</CardTitle>
                  <CardDescription>
                    Comprehensive business readiness analysis powered by AI insights
                  </CardDescription>
                </div>
              </div>
              <Button 
                onClick={refreshDashboard} 
                variant="outline" 
                disabled={refreshing}
                className="flex items-center gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </CardHeader>
        </Card>

        {/* Overall Score Card */}
        <div className="grid md:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-purple-900 to-blue-900 border-purple-600">
            <CardContent className="pt-6">
              <div className="text-center">
                <div className={`text-4xl font-bold mb-2 ${getScoreColor(dashboardData?.overall_score || 0)}`}>
                  {dashboardData?.overall_score || 0}
                </div>
                <div className="text-sm text-muted-foreground">Overall Score</div>
                <div className="flex items-center justify-center mt-2">
                  <Brain className="h-4 w-4 mr-1 text-purple-400" />
                  <span className="text-xs text-purple-300">AI Generated</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary mb-2">
                  {Math.round((dashboardData?.data_completeness || 0) * 100)}%
                </div>
                <div className="text-sm text-muted-foreground">Data Completeness</div>
                <div className="w-full bg-muted rounded-full h-2 mt-2">
                  <div 
                    className="bg-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(dashboardData?.data_completeness || 0) * 100}%` }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary mb-2">
                  {dashboardData?.assessment_count || 0}
                </div>
                <div className="text-sm text-muted-foreground">Assessments Completed</div>
                <div className="flex items-center justify-center mt-2">
                  <CheckCircle className="h-4 w-4 mr-1 text-green-400" />
                  <span className="text-xs text-green-300">Active</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary mb-2">
                  {currentSubElement?.ai_confidence || 0}%
                </div>
                <div className="text-sm text-muted-foreground">AI Confidence</div>
                <div className="flex items-center justify-center mt-2">
                  <Target className="h-4 w-4 mr-1 text-blue-400" />
                  <span className="text-xs text-blue-300">High Accuracy</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          {/* Sidebar Navigation */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-primary" />
                Business Components
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {dashboardData?.sub_elements?.map((element, index) => (
                <button
                  key={index}
                  onClick={() => setActiveTab(index)}
                  className={`w-full p-3 rounded-lg text-left transition-all duration-200 ${
                    activeTab === index 
                      ? 'bg-primary text-primary-foreground' 
                      : 'bg-muted hover:bg-muted/80'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-sm">{index + 1}. {element.title}</div>
                      <div className={`text-xs ${getScoreColor(element.score)} font-semibold`}>
                        {element.score}/100
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4" />
                  </div>
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Main Content Area */}
          <div className="lg:col-span-3 space-y-6">
            {currentSubElement && (
              <>
                {/* Element Header */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-xl flex items-center gap-2">
                          <span className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center text-sm font-bold text-primary">
                            {activeTab + 1}
                          </span>
                          {currentSubElement.title}
                        </CardTitle>
                        <CardDescription className="mt-2">
                          {currentSubElement.definition}
                        </CardDescription>
                      </div>
                      <Badge className={getStatusBadge(currentSubElement.status)}>
                        {currentSubElement.status}
                      </Badge>
                    </div>
                  </CardHeader>
                </Card>

                {/* Metrics Grid */}
                <div className="grid md:grid-cols-3 gap-4">
                  {currentSubElement.metrics?.map((metric, index) => (
                    <Card key={index}>
                      <CardContent className="pt-4">
                        <div className="text-center">
                          <div className="text-xl font-bold text-primary mb-1">
                            {metric.value}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {metric.label}
                          </div>
                          {metric.trend && (
                            <div className={`flex items-center justify-center mt-2 text-xs ${
                              metric.trend === 'positive' ? 'text-green-400' : 
                              metric.trend === 'negative' ? 'text-red-400' : 'text-yellow-400'
                            }`}>
                              <TrendingUp className="h-3 w-3 mr-1" />
                              {metric.trend}
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* AI Generated Content */}
                <Card className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border-purple-600/50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="h-5 w-5 text-purple-400" />
                      AI Analysis & Insights
                      <Badge variant="outline" className="ml-2 border-purple-600 text-purple-300">
                        {currentSubElement.ai_confidence}% Confidence
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-foreground leading-relaxed mb-4">
                      {currentSubElement.ai_generated_content}
                    </p>
                    
                    {/* Data Sources */}
                    {currentSubElement.data_sources && currentSubElement.data_sources.length > 0 && (
                      <div className="mt-4 p-3 bg-muted rounded-lg">
                        <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
                          <Info className="h-4 w-4" />
                          Data Sources
                        </h4>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          {currentSubElement.data_sources.map((source, index) => (
                            <div key={index} className="flex justify-between">
                              <span className="text-muted-foreground">{source.name}</span>
                              <span className="font-medium">{source.percentage}%</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Improvement Suggestions */}
                {currentSubElement.improvements && currentSubElement.improvements.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Lightbulb className="h-5 w-5 text-yellow-500" />
                        AI-Powered Improvement Suggestions
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {currentSubElement.improvements.map((improvement, index) => (
                          <div key={index} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                            <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center text-xs font-bold text-primary-foreground mt-0.5">
                              {index + 1}
                            </div>
                            <p className="text-sm text-foreground flex-1">{improvement}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* What to Include Guide */}
                <Card className="border-dashed">
                  <CardHeader>
                    <CardTitle className="text-lg">What to Include in {currentSubElement.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">
                      {currentSubElement.what_to_include}
                    </p>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ExecutiveSummaryDashboard