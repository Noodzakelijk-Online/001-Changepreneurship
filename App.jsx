import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  User, 
  Lightbulb, 
  Search, 
  Building, 
  ArrowRight, 
  CheckCircle, 
  Target,
  Heart,
  Brain,
  Compass,
  Star,
  TrendingUp,
  TestTube,
  Settings,
  Rocket
} from 'lucide-react'
import './App.css'

// Contexts
import { AuthProvider } from './contexts/AuthContext'
import { AssessmentProvider, useAssessment } from './contexts/AssessmentContext'

// Components
import Dashboard from './components/Dashboard'
import SelfDiscoveryAssessment from './components/assessment/SelfDiscoveryAssessment'
import IdeaDiscoveryAssessment from './components/assessment/IdeaDiscoveryAssessment'
import MarketResearchTools from './components/assessment/MarketResearchTools'
import BusinessPillarsPlanning from './components/assessment/BusinessPillarsPlanning'
import ProductConceptTesting from './components/assessment/ProductConceptTesting'
import BusinessDevelopmentDecisionMaking from './components/assessment/BusinessDevelopmentDecisionMaking'
import BusinessPrototypeTesting from './components/assessment/BusinessPrototypeTesting'
import AIRecommendationsSimple from './components/AIRecommendationsSimple'
import LandingPage from './components/LandingPage'

function App() {
  return (
    <AuthProvider>
      <AssessmentProvider>
        <Router>
          <div className="min-h-screen bg-background text-foreground dark">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/assessment" element={<AssessmentFlow />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/ai-recommendations" element={<AIRecommendationsSimple />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </Router>
      </AssessmentProvider>
    </AuthProvider>
  )
}

function AssessmentFlow() {
  const { currentPhase, assessmentData, updatePhase } = useAssessment()
  
  const phases = [
    // Foundation & Strategy Phase (Parts 1-4)
    {
      id: 'self-discovery',
      title: 'Self Discovery',
      description: 'Understand your entrepreneurial personality and motivations',
      icon: User,
      component: SelfDiscoveryAssessment,
      duration: '60-90 minutes',
      color: 'from-orange-500 to-red-600',
      phase: 'Foundation & Strategy'
    },
    {
      id: 'idea-discovery',
      title: 'Idea Discovery',
      description: 'Transform insights into concrete business opportunities',
      icon: Lightbulb,
      component: IdeaDiscoveryAssessment,
      duration: '90-120 minutes',
      color: 'from-blue-500 to-purple-600',
      phase: 'Foundation & Strategy'
    },
    {
      id: 'market-research',
      title: 'Market Research',
      description: 'Validate assumptions and understand competitive dynamics',
      icon: Search,
      component: MarketResearchTools,
      duration: '2-3 weeks',
      color: 'from-green-500 to-teal-600',
      phase: 'Foundation & Strategy'
    },
    {
      id: 'business-pillars',
      title: 'Business Pillars',
      description: 'Define foundational elements for strategic planning',
      icon: Building,
      component: BusinessPillarsPlanning,
      duration: '1-2 weeks',
      color: 'from-purple-500 to-pink-600',
      phase: 'Foundation & Strategy'
    },
    // Implementation & Testing Phase (Parts 5-7)
    {
      id: 'product-concept-testing',
      title: 'Product Concept Testing',
      description: 'Validate product concepts with real customer feedback',
      icon: TestTube,
      component: ProductConceptTesting,
      duration: '2-4 weeks',
      color: 'from-cyan-500 to-blue-600',
      phase: 'Implementation & Testing'
    },
    {
      id: 'business-development',
      title: 'Business Development',
      description: 'Strategic decision-making and resource optimization',
      icon: Settings,
      component: BusinessDevelopmentDecisionMaking,
      duration: '1-2 weeks',
      color: 'from-indigo-500 to-purple-600',
      phase: 'Implementation & Testing'
    },
    {
      id: 'business-prototype-testing',
      title: 'Business Prototype Testing',
      description: 'Complete business model validation in real market conditions',
      icon: Rocket,
      component: BusinessPrototypeTesting,
      duration: '3-6 weeks',
      color: 'from-pink-500 to-rose-600',
      phase: 'Implementation & Testing'
    }
  ]

  const currentPhaseIndex = phases.findIndex(phase => phase.id === currentPhase)
  const CurrentComponent = phases[currentPhaseIndex]?.component || SelfDiscoveryAssessment

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          Changepreneurship Assessment
        </h1>
        <p className="text-muted-foreground text-lg">
          Transform your entrepreneurial journey with our comprehensive 7-part framework
        </p>
      </div>

      {/* Progress Overview */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Compass className="h-5 w-5" />
            Your Journey Progress
          </CardTitle>
          <CardDescription>
            Complete all seven phases to unlock your personalized business development roadmap
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-4 mb-6">
            {phases.map((phase, index) => {
              const Icon = phase.icon
              const isCompleted = assessmentData[phase.id]?.completed || false
              const isCurrent = phase.id === currentPhase
              const isAccessible = (() => {
                // For review purposes, make all phases accessible
                return true
                // Original logic (commented out for review):
                // Foundation phases (0-3) are always accessible with some progression
                // if (index <= 3) {
                //   return index <= currentPhaseIndex + 3 || isCompleted
                // }
                // Implementation phases (4-6) unlock after completing foundation phases
                // const foundationCompleted = phases.slice(0, 4).every(p => assessmentData[p.id]?.completed)
                // return foundationCompleted || isCompleted
              })()

              return (
                <Card 
                  key={phase.id} 
                  className={`relative overflow-hidden transition-all duration-300 ${
                    isCurrent ? 'ring-2 ring-primary' : ''
                  } ${isAccessible ? 'cursor-pointer hover:shadow-lg' : 'opacity-50'}`}
                  onClick={() => isAccessible && updatePhase(phase.id)}
                >
                  <div className={`absolute inset-0 bg-gradient-to-br ${phase.color} opacity-10`} />
                  <CardContent className="p-4 relative">
                    <div className="flex items-center justify-between mb-2">
                      <Icon className="h-6 w-6 text-primary" />
                      {isCompleted && <CheckCircle className="h-5 w-5 text-green-500" />}
                    </div>
                    <h3 className="font-semibold mb-1">{phase.title}</h3>
                    <p className="text-xs text-muted-foreground mb-2">{phase.description}</p>
                    <div className="space-y-1">
                      <Badge 
                        variant={phase.phase === 'Foundation & Strategy' ? 'default' : 'secondary'} 
                        className="text-xs mb-1"
                      >
                        {phase.phase}
                      </Badge>
                      <div className="flex justify-between text-xs">
                        <Badge variant="outline" className="text-xs">
                          {phase.duration}
                        </Badge>
                        {!isAccessible && (
                          <Badge variant="outline" className="text-xs text-muted-foreground">
                            Locked
                          </Badge>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Overall Progress</span>
              <span>{Math.round((Object.values(assessmentData).filter(data => data?.completed).length / phases.length) * 100)}%</span>
            </div>
            <Progress 
              value={(Object.values(assessmentData).filter(data => data?.completed).length / phases.length) * 100} 
              className="h-2"
            />
          </div>
        </CardContent>
      </Card>

      {/* Current Assessment */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                {phases[currentPhaseIndex]?.icon && React.createElement(phases[currentPhaseIndex].icon, { className: "h-6 w-6" })}
                {phases[currentPhaseIndex]?.title || 'Assessment'}
              </CardTitle>
              <CardDescription>
                {phases[currentPhaseIndex]?.description || 'Complete your assessment'}
              </CardDescription>
            </div>
            <Badge variant="outline">
              Phase {currentPhaseIndex + 1} of {phases.length}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <CurrentComponent />
        </CardContent>
      </Card>
    </div>
  )
}

export default App

