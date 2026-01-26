import React from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { 
  Brain, 
  TrendingUp, 
  Lightbulb, 
  BarChart3, 
  Target,
  ArrowRight,
  Sparkles,
  LineChart
} from 'lucide-react'

const AIInsightsHub = () => {
  const aiFeatures = [
    {
      id: 'executive-summary',
      title: 'AI Executive Summary',
      description: 'Comprehensive business readiness analysis with AI-driven insights across 9 key business components',
      icon: BarChart3,
      color: 'from-purple-500 to-blue-600',
      link: '/dashboard/executive-summary',
      features: [
        'AI-generated business insights',
        'Company vision & market analysis',
        'Financial projections & team assessment',
        'Risk management strategies',
        'Personalized improvement suggestions'
      ],
      badge: 'NEW',
      badgeColor: 'bg-green-500'
    },
    {
      id: 'ai-recommendations',
      title: 'AI Recommendations',
      description: 'Personalized business principles and strategic recommendations based on your assessment responses',
      icon: Lightbulb,
      color: 'from-orange-500 to-red-600',
      link: '/ai-insights/recommendations',
      features: [
        'Founder profile analysis',
        'Success probability scoring',
        'Personalized action plans',
        'Risk assessment & mitigation',
        'Real AI-driven insights'
      ],
      badge: 'NEW',
      badgeColor: 'bg-green-500'
    },
    {
      id: 'progress-analytics',
      title: 'Progress Analytics',
      description: 'Track your entrepreneurial journey with detailed progress metrics and completion statistics',
      icon: LineChart,
      color: 'from-green-500 to-teal-600',
      link: '/user-dashboard',
      features: [
        'Assessment completion tracking',
        'Phase-by-phase progress',
        'Time investment analysis',
        'Milestone achievements',
        'Historical performance'
      ]
    },
    {
      id: 'smart-insights',
      title: 'AI Smart Insights',
      description: 'Real-time AI analysis of your responses with intelligent pattern recognition',
      icon: Sparkles,
      color: 'from-pink-500 to-purple-600',
      link: '/assessment',
      features: [
        'Real-time response analysis',
        'Pattern recognition',
        'Comparative benchmarking',
        'Trend identification',
        'Predictive modeling'
      ],
      badge: 'COMING SOON',
      badgeColor: 'bg-yellow-500'
    }
  ]

  return (
    <div className="min-h-screen bg-background dark p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-600 rounded-2xl mb-4">
            <Brain className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
            AI-Powered Insights Hub
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Unlock powerful AI-driven insights to accelerate your entrepreneurial journey. 
            Choose from our suite of intelligent analysis tools.
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid md:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 border-purple-600/50">
            <CardContent className="pt-6">
              <div className="text-center">
                <BarChart3 className="h-8 w-8 text-purple-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">9</div>
                <div className="text-sm text-muted-foreground">Business Components</div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-orange-900/20 to-red-900/20 border-orange-600/50">
            <CardContent className="pt-6">
              <div className="text-center">
                <Lightbulb className="h-8 w-8 text-orange-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">50+</div>
                <div className="text-sm text-muted-foreground">AI Insights</div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-green-900/20 to-teal-900/20 border-green-600/50">
            <CardContent className="pt-6">
              <div className="text-center">
                <TrendingUp className="h-8 w-8 text-green-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">95%</div>
                <div className="text-sm text-muted-foreground">Accuracy Rate</div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-pink-900/20 to-purple-900/20 border-pink-600/50">
            <CardContent className="pt-6">
              <div className="text-center">
                <Target className="h-8 w-8 text-pink-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">Real-time</div>
                <div className="text-sm text-muted-foreground">Analysis</div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AI Features Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {aiFeatures.map((feature) => {
            const Icon = feature.icon
            return (
              <Card 
                key={feature.id} 
                className="group hover:shadow-2xl transition-all duration-300 border-2 hover:border-primary overflow-hidden"
              >
                <div className={`h-2 bg-gradient-to-r ${feature.color}`} />
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center`}>
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <CardTitle className="text-xl flex items-center gap-2">
                          {feature.title}
                          {feature.badge && (
                            <span className={`text-xs px-2 py-1 rounded-full ${feature.badgeColor} text-white font-semibold`}>
                              {feature.badge}
                            </span>
                          )}
                        </CardTitle>
                      </div>
                    </div>
                  </div>
                  <CardDescription className="mt-3">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Features List */}
                  <div className="space-y-2">
                    {feature.features.map((item, index) => (
                      <div key={index} className="flex items-center gap-2 text-sm">
                        <div className={`w-1.5 h-1.5 rounded-full bg-gradient-to-r ${feature.color}`} />
                        <span className="text-muted-foreground">{item}</span>
                      </div>
                    ))}
                  </div>
                  
                  {/* Action Button */}
                  <Link to={feature.link}>
                    <Button 
                      className={`w-full bg-gradient-to-r ${feature.color} hover:opacity-90 transition-opacity`}
                      disabled={feature.badge === 'COMING SOON'}
                    >
                      {feature.badge === 'COMING SOON' ? 'Coming Soon' : 'Explore'}
                      {feature.badge !== 'COMING SOON' && <ArrowRight className="ml-2 h-4 w-4" />}
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Benefits Section */}
        <Card className="bg-gradient-to-br from-purple-900/10 to-blue-900/10 border-purple-600/30">
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-purple-400" />
              Why Use AI Insights?
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <h3 className="font-semibold text-lg text-white">Data-Driven Decisions</h3>
                <p className="text-muted-foreground text-sm">
                  Make informed decisions backed by AI analysis of your assessment responses and business data.
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-semibold text-lg text-white">Personalized Guidance</h3>
                <p className="text-muted-foreground text-sm">
                  Receive tailored recommendations specific to your business stage, industry, and goals.
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-semibold text-lg text-white">Continuous Improvement</h3>
                <p className="text-muted-foreground text-sm">
                  Track progress over time and get actionable suggestions to improve your business readiness.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Call to Action */}
        <div className="text-center space-y-4 py-8">
          <h2 className="text-2xl font-bold text-white">
            Ready to unlock AI-powered insights?
          </h2>
          <p className="text-muted-foreground">
            Start with the AI Executive Summary for a comprehensive overview of your business readiness.
          </p>
          <Link to="/dashboard/executive-summary">
            <Button size="lg" className="bg-gradient-to-r from-purple-500 to-blue-600 hover:opacity-90 px-8">
              <BarChart3 className="mr-2 h-5 w-5" />
              View Executive Summary
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default AIInsightsHub