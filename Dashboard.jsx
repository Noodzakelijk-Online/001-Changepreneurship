import React from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  User, 
  Lightbulb, 
  Search, 
  Building, 
  TrendingUp,
  CheckCircle,
  Clock,
  ArrowRight,
  BarChart3,
  Users,
  FileText
} from 'lucide-react'
import { useAssessment, ENTREPRENEUR_ARCHETYPES } from '../contexts/AssessmentContext'

const Dashboard = () => {
  const { assessmentData, currentPhase } = useAssessment()

  const phases = [
    {
      id: 'self-discovery',
      title: 'Self Discovery',
      icon: User,
      color: 'from-orange-500 to-red-600'
    },
    {
      id: 'idea-discovery',
      title: 'Idea Discovery',
      icon: Lightbulb,
      color: 'from-blue-500 to-purple-600'
    },
    {
      id: 'market-research',
      title: 'Market Research',
      icon: Search,
      color: 'from-green-500 to-teal-600'
    },
    {
      id: 'business-pillars',
      title: 'Business Pillars',
      icon: Building,
      color: 'from-purple-500 to-pink-600'
    }
  ]

  const overallProgress = Math.round(
    (Object.values(assessmentData).filter(data => data?.completed).length / phases.length) * 100
  )

  const selfDiscoveryData = assessmentData['self-discovery'] || {}
  const archetype = selfDiscoveryData.archetype
  const archetypeData = archetype ? ENTREPRENEUR_ARCHETYPES[archetype] : null

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="container mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Your Dashboard</h1>
            <p className="text-muted-foreground">
              Track your entrepreneurial journey and access your personalized insights
            </p>
          </div>
          <Link to="/assessment">
            <Button>
              Continue Assessment
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>

        {/* Progress Overview */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Overall Progress</p>
                  <p className="text-3xl font-bold">{overallProgress}%</p>
                </div>
                <TrendingUp className="h-8 w-8 text-primary" />
              </div>
              <Progress value={overallProgress} className="mt-4" />
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Completed Phases</p>
                  <p className="text-3xl font-bold">
                    {Object.values(assessmentData).filter(data => data?.completed).length}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Current Phase</p>
                  <p className="text-lg font-semibold">
                    {phases.find(p => p.id === currentPhase)?.title || 'Not Started'}
                  </p>
                </div>
                <Clock className="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Archetype</p>
                  <p className="text-lg font-semibold">
                    {archetypeData ? archetypeData.name : 'Not Determined'}
                  </p>
                </div>
                <User className="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Phase Progress */}
        <Card>
          <CardHeader>
            <CardTitle>Assessment Progress</CardTitle>
            <CardDescription>
              Complete all phases to unlock your full entrepreneurial profile
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              {phases.map((phase) => {
                const Icon = phase.icon
                const phaseData = assessmentData[phase.id] || {}
                const isCompleted = phaseData.completed || false
                const progress = phaseData.progress || 0

                return (
                  <div key={phase.id} className="flex items-center gap-4 p-4 rounded-lg border">
                    <div className={`p-3 rounded-lg bg-gradient-to-br ${phase.color}`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold">{phase.title}</h3>
                        {isCompleted && <CheckCircle className="h-5 w-5 text-green-500" />}
                      </div>
                      <Progress value={progress} className="mb-2" />
                      <p className="text-sm text-muted-foreground">{progress}% complete</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Archetype Results */}
        {archetypeData && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-primary" />
                Your Entrepreneur Archetype
              </CardTitle>
              <CardDescription>
                Based on your self-discovery assessment
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-2xl font-bold mb-2">{archetypeData.name}</h3>
                  <p className="text-muted-foreground italic mb-4">"{archetypeData.description}"</p>
                  <div className="space-y-2">
                    <h4 className="font-semibold">Key Traits:</h4>
                    <ul className="space-y-1">
                      {archetypeData.traits.map((trait, index) => (
                        <li key={index} className="flex items-center gap-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          {trait}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Business Focus</h4>
                  <p className="text-sm text-muted-foreground mb-4">{archetypeData.businessFocus}</p>
                  <h4 className="font-semibold mb-2">Recommended Business Types</h4>
                  <ul className="space-y-1">
                    {archetypeData.examples.map((example, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm">
                        <Lightbulb className="h-4 w-4 text-primary" />
                        {example}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-6 text-center">
              <BarChart3 className="h-12 w-12 text-primary mx-auto mb-4" />
              <h3 className="font-semibold mb-2">View Analytics</h3>
              <p className="text-sm text-muted-foreground">
                Detailed insights and progress analytics
              </p>
              <Badge variant="secondary" className="mt-2">Coming Soon</Badge>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-6 text-center">
              <Users className="h-12 w-12 text-primary mx-auto mb-4" />
              <h3 className="font-semibold mb-2">Investor Matches</h3>
              <p className="text-sm text-muted-foreground">
                Connect with relevant investors
              </p>
              <Badge variant="secondary" className="mt-2">Coming Soon</Badge>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-6 text-center">
              <FileText className="h-12 w-12 text-primary mx-auto mb-4" />
              <h3 className="font-semibold mb-2">Business Assets</h3>
              <p className="text-sm text-muted-foreground">
                Generate business documents and plans
              </p>
              <Badge variant="secondary" className="mt-2">Coming Soon</Badge>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

