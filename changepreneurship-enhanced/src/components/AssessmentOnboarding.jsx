import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  ArrowRight, 
  Clock, 
  Target, 
  CheckCircle, 
  Lightbulb,
  Heart,
  Star,
  Compass,
  Brain,
  TrendingUp,
  Zap,
  Shield,
  Users
} from 'lucide-react'

const AssessmentOnboarding = ({ onStart, onSkip }) => {
  const [currentStep, setCurrentStep] = useState(0)

  const onboardingSteps = [
    {
      id: 'welcome',
      title: 'Welcome to Your Entrepreneurial Journey',
      description: 'Discover if entrepreneurship is right for you with our comprehensive assessment',
      icon: Heart,
      content: (
        <div className="space-y-4">
          <div className="text-center">
            <div className="mx-auto w-20 h-20 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center mb-4">
              <Heart className="h-10 w-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Ready to Transform Your Future?</h2>
            <p className="text-muted-foreground">
              This assessment will help you understand your entrepreneurial potential and create a personalized roadmap for success.
            </p>
          </div>
          
          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <Target className="h-8 w-8 mx-auto mb-2 text-primary" />
              <div className="font-medium">Personalized</div>
              <div className="text-sm text-muted-foreground">Tailored to your unique situation</div>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <Shield className="h-8 w-8 mx-auto mb-2 text-primary" />
              <div className="font-medium">Comprehensive</div>
              <div className="text-sm text-muted-foreground">Deep insights into your potential</div>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <Users className="h-8 w-8 mx-auto mb-2 text-primary" />
              <div className="font-medium">Actionable</div>
              <div className="text-sm text-muted-foreground">Clear next steps for your journey</div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'process',
      title: 'How the Assessment Works',
      description: 'Understanding the 6-phase evaluation process',
      icon: Compass,
      content: (
        <div className="space-y-6">
          <div className="text-center mb-6">
            <Compass className="h-12 w-12 mx-auto mb-3 text-primary" />
            <h3 className="text-xl font-semibold">6 Comprehensive Phases</h3>
            <p className="text-muted-foreground">Each phase builds on the previous to create your complete entrepreneur profile</p>
          </div>
          
          <div className="space-y-4">
            {[
              { icon: Heart, title: 'Self Discovery', desc: 'Core motivation, values, and vision', time: '15-20 min' },
              { icon: Lightbulb, title: 'Idea Discovery', desc: 'Business ideas and opportunities', time: '20-25 min' },
              { icon: Target, title: 'Market Research', desc: 'Industry analysis and validation', time: '15-20 min' },
              { icon: Star, title: 'Business Pillars', desc: 'Foundation and strategy planning', time: '20-25 min' },
              { icon: Brain, title: 'Product Testing', desc: 'Concept validation and feedback', time: '15-20 min' },
              { icon: TrendingUp, title: 'Business Development', desc: 'Growth and scaling strategies', time: '10-15 min' }
            ].map((phase, index) => {
              const IconComponent = phase.icon
              return (
                <div key={index} className="flex items-center gap-4 p-3 border rounded-lg">
                  <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                    <IconComponent className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium">{phase.title}</div>
                    <div className="text-sm text-muted-foreground">{phase.desc}</div>
                  </div>
                  <Badge variant="secondary">{phase.time}</Badge>
                </div>
              )
            })}
          </div>
        </div>
      )
    },
    {
      id: 'optimization',
      title: 'Speed Up Your Assessment',
      description: 'Connect your data to save time and get better insights',
      icon: Zap,
      content: (
        <div className="space-y-6">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-gradient-to-br from-orange-500 to-yellow-500 rounded-full flex items-center justify-center mb-4">
              <Zap className="h-8 w-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Smart Data Integration</h3>
            <p className="text-muted-foreground">
              Connect your existing data sources to pre-populate answers and reduce assessment time by up to 75%
            </p>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg">
              <Clock className="h-6 w-6 text-green-600 mb-2" />
              <div className="font-medium">Save Time</div>
              <div className="text-sm text-muted-foreground">Reduce from 2+ hours to 30-45 minutes</div>
            </div>
            <div className="p-4 border rounded-lg">
              <Target className="h-6 w-6 text-blue-600 mb-2" />
              <div className="font-medium">Better Accuracy</div>
              <div className="text-sm text-muted-foreground">More precise insights from real data</div>
            </div>
            <div className="p-4 border rounded-lg">
              <Shield className="h-6 w-6 text-purple-600 mb-2" />
              <div className="font-medium">Secure & Private</div>
              <div className="text-sm text-muted-foreground">Your data stays protected</div>
            </div>
            <div className="p-4 border rounded-lg">
              <CheckCircle className="h-6 w-6 text-orange-600 mb-2" />
              <div className="font-medium">Optional</div>
              <div className="text-sm text-muted-foreground">You can skip and fill manually</div>
            </div>
          </div>
          
          <div className="bg-orange-50 dark:bg-orange-950/20 p-4 rounded-lg border border-orange-200 dark:border-orange-800">
            <div className="flex items-start gap-3">
              <Lightbulb className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-medium text-orange-800 dark:text-orange-200">Pro Tip</div>
                <div className="text-sm text-orange-700 dark:text-orange-300">
                  You'll see data connection options at the start of the assessment. Even connecting 1-2 sources can save significant time!
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    }
  ]

  const currentStepData = onboardingSteps[currentStep]
  const isLastStep = currentStep === onboardingSteps.length - 1

  const nextStep = () => {
    if (isLastStep) {
      onStart()
    } else {
      setCurrentStep(currentStep + 1)
    }
  }

  const previousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Progress Indicator */}
      <div className="text-center space-y-2">
        <div className="flex justify-center gap-2">
          {onboardingSteps.map((_, index) => (
            <div
              key={index}
              className={`w-3 h-3 rounded-full transition-colors ${
                index <= currentStep ? 'bg-primary' : 'bg-muted'
              }`}
            />
          ))}
        </div>
        <div className="text-sm text-muted-foreground">
          Step {currentStep + 1} of {onboardingSteps.length}
        </div>
      </div>

      {/* Main Content */}
      <Card className="border-2">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center gap-3 mb-2">
            <currentStepData.icon className="h-6 w-6 text-primary" />
            <CardTitle className="text-xl">{currentStepData.title}</CardTitle>
          </div>
          <CardDescription className="text-base">
            {currentStepData.description}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {currentStepData.content}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={previousStep}
            disabled={currentStep === 0}
          >
            Previous
          </Button>
          <Button variant="ghost" onClick={onSkip}>
            Skip Intro
          </Button>
        </div>
        
        <Button onClick={nextStep} className="flex items-center gap-2">
          {isLastStep ? 'Start Assessment' : 'Next'}
          <ArrowRight className="h-4 w-4" />
        </Button>
      </div>

      {/* Time Estimate */}
      <div className="text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-muted rounded-full">
          <Clock className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">
            Total time: 30-45 minutes (with optimization) • 90-120 minutes (manual)
          </span>
        </div>
      </div>
    </div>
  )
}

export default AssessmentOnboarding

