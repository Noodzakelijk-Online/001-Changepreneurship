import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Brain, Target, Star, Lightbulb } from 'lucide-react'

const AIRecommendationsSimple = () => {
  return (
    <div className="min-h-screen bg-background text-foreground dark p-6">
      <div className="container mx-auto space-y-6">
        {/* Header */}
        <Card>
          <CardHeader>
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
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">85%</div>
              <div className="text-sm text-muted-foreground">Overall Success Probability</div>
              <Badge variant="default" className="mt-2">High Confidence</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Sample Recommendations */}
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
                <div className="text-2xl font-bold text-primary mb-2">Visionary Innovator</div>
                <p className="text-muted-foreground">Driven by big ideas and transformative solutions</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-primary" />
                Key Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 bg-muted/50 rounded-lg">
                  <h4 className="font-semibold text-sm">Focus on Market Validation</h4>
                  <p className="text-sm text-muted-foreground">Conduct customer interviews to validate your assumptions</p>
                </div>
                <div className="p-3 bg-muted/50 rounded-lg">
                  <h4 className="font-semibold text-sm">Build Financial Projections</h4>
                  <p className="text-sm text-muted-foreground">Create detailed 3-year financial forecasts</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Note */}
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-muted-foreground">
              Complete more assessment phases to unlock detailed AI analysis and personalized recommendations.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default AIRecommendationsSimple

