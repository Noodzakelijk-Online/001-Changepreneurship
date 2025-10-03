import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Brain, Target, Lightbulb } from 'lucide-react'
import apiService from '../services/api.js'

const AIRecommendationsSimple = () => {
  const [principles, setPrinciples] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    apiService
      .getPrinciples()
      .then((res) => {
        if (res.success) {
          setPrinciples(res.data)
        } else {
          setError(res.error || 'Failed to load principles')
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

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

        {/* Principle Recommendations */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-primary" />
              Principle Recommendations
            </CardTitle>
            <CardDescription>Entrepreneurship principles matched to your journey</CardDescription>
          </CardHeader>
          <CardContent>
            {loading && <p className="text-sm text-muted-foreground">Loading...</p>}
            {error && <p className="text-sm text-destructive">{error}</p>}
            {!loading && !error && (
              <div className="space-y-4">
                {principles.map((p) => (
                  <div key={p.id} className="p-4 border rounded-lg">
                    <h3 className="font-semibold mb-1">{p.title}</h3>
                    <p className="text-sm text-muted-foreground mb-2">
                      {p.short_summary}
                    </p>
                    {p.actionable_steps && (
                      <ul className="list-disc ml-4 space-y-1 text-sm">
                        {p.actionable_steps.map((step, i) => (
                          <li key={i}>{step}</li>
                        ))}
                      </ul>
                    )}
                    {p.common_risks && p.common_risks.length > 0 && (
                      <div className="mt-2">
                        <h4 className="text-sm font-medium">Common Risks</h4>
                        <ul className="list-disc ml-4 space-y-1 text-sm text-muted-foreground">
                          {p.common_risks.map((risk, i) => (
                            <li key={i}>{risk}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default AIRecommendationsSimple

