import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import AuthModal from './auth/AuthModal'
import UserProfile from './UserProfile'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  User, 
  Lightbulb, 
  Search, 
  Building, 
  ArrowRight, 
  CheckCircle, 
  Star,
  TrendingUp,
  Users,
  Target,
  Zap,
  Shield,
  Brain
} from 'lucide-react'

const LandingPage = () => {
  const { isAuthenticated } = useAuth()
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState('login')

  const handleAuthAction = (mode) => {
    if (isAuthenticated) {
      // User is already authenticated, navigate directly
      return
    }
    setAuthMode(mode)
    setAuthModalOpen(true)
  }
  const features = [
    {
      icon: User,
      title: 'Self-Discovery Assessment',
      description: 'Understand your entrepreneurial personality and discover your unique archetype',
      duration: '60-90 minutes',
      color: 'from-orange-500 to-red-600',
      phase: 'Foundation & Strategy'
    },
    {
      icon: Lightbulb,
      title: 'Idea Discovery',
      description: 'Transform your insights into concrete, validated business opportunities',
      duration: '90-120 minutes',
      color: 'from-blue-500 to-purple-600',
      phase: 'Foundation & Strategy'
    },
    {
      icon: Search,
      title: 'Market Research',
      description: 'Validate assumptions and understand competitive dynamics in your market',
      duration: '2-3 weeks',
      color: 'from-green-500 to-teal-600',
      phase: 'Foundation & Strategy'
    },
    {
      icon: Building,
      title: 'Business Pillars Planning',
      description: 'Define foundational pillars and create your strategic business plan',
      duration: '1-2 weeks',
      color: 'from-purple-500 to-pink-600',
      phase: 'Foundation & Strategy'
    },
    {
      icon: Target,
      title: 'Product Concept Testing',
      description: 'Test market acceptability and validate pricing strategies',
      duration: '3-4 days',
      color: 'from-indigo-500 to-purple-600',
      phase: 'Implementation & Testing'
    },
    {
      icon: TrendingUp,
      title: 'Business Development',
      description: 'Strategic decision-making and resource-opportunity alignment',
      duration: '1-2 weeks',
      color: 'from-emerald-500 to-teal-600',
      phase: 'Implementation & Testing'
    },
    {
      icon: Zap,
      title: 'Business Prototype Testing',
      description: 'Complete business model validation through real-world testing',
      duration: '2-4 weeks',
      color: 'from-rose-500 to-pink-600',
      phase: 'Implementation & Testing'
    }
  ]

  const benefits = [
    {
      icon: Target,
      title: 'Personalized Roadmap',
      description: 'Get a customized path based on your unique profile and goals'
    },
    {
      icon: TrendingUp,
      title: 'AI-Powered Insights',
      description: 'Leverage advanced AI to optimize your business strategy'
    },
    {
      icon: Users,
      title: 'Investor Matching',
      description: 'Connect with investors who align with your business vision'
    },
    {
      icon: Zap,
      title: 'Rapid Validation',
      description: 'Quickly test and validate your business ideas'
    },
    {
      icon: Shield,
      title: 'Risk Assessment',
      description: 'Understand and mitigate potential business risks'
    },
    {
      icon: Star,
      title: 'Expert Guidance',
      description: 'Access proven frameworks and best practices'
    }
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Header */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-background/80 backdrop-blur-md border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold">Changepreneurship</span>
            </div>
            
            <div className="flex items-center gap-4">
              {isAuthenticated ? (
                <UserProfile />
              ) : (
                <div className="flex items-center gap-2">
                  <Button 
                    variant="ghost" 
                    onClick={() => handleAuthAction('login')}
                  >
                    Sign In
                  </Button>
                  <Button 
                    onClick={() => handleAuthAction('register')}
                  >
                    Get Started
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 px-4 pt-32">{/* Added pt-32 for nav spacing */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-accent/10" />
        <div className="container mx-auto text-center relative">
          <Badge variant="secondary" className="mb-6">
            Transform Your Entrepreneurial Journey
          </Badge>
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
            Changepreneurship
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Discover your entrepreneurial archetype, validate business ideas, and build a comprehensive 
            roadmap for success with our AI-powered assessment platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {isAuthenticated ? (
              <>
                <Link to="/assessment">
                  <Button size="lg" className="text-lg px-8 py-6">
                    Continue Assessment
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link to="/ai-recommendations">
                  <Button variant="outline" size="lg" className="text-lg px-8 py-6">
                    <Brain className="mr-2 h-5 w-5" />
                    AI Insights
                  </Button>
                </Link>
                <Link to="/dashboard">
                  <Button variant="outline" size="lg" className="text-lg px-8 py-6">
                    View Dashboard
                  </Button>
                </Link>
              </>
            ) : (
              <>
                <Button 
                  size="lg" 
                  className="text-lg px-8 py-6"
                  onClick={() => handleAuthAction('register')}
                >
                  Start Your Journey
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
                <Button 
                  variant="outline" 
                  size="lg" 
                  className="text-lg px-8 py-6"
                  onClick={() => handleAuthAction('login')}
                >
                  <Brain className="mr-2 h-5 w-5" />
                  Sign In to Continue
                </Button>
              </>
            )}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our comprehensive 7-part framework guides you through every step of your entrepreneurial journey
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <Card key={index} className="relative overflow-hidden group hover:shadow-lg transition-all duration-300">
                  <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-5 group-hover:opacity-10 transition-opacity`} />
                  <CardHeader className="relative">
                    <div className="flex items-center justify-between mb-4">
                      <div className={`p-3 rounded-lg bg-gradient-to-br ${feature.color}`}>
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        <Badge variant="outline" className="text-xs">
                          Step {index + 1}
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          {feature.phase}
                        </Badge>
                      </div>
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                    <CardDescription className="text-sm">{feature.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="relative">
                    <div className="flex items-center justify-between">
                      <Badge variant="secondary" className="text-xs">{feature.duration}</Badge>
                      <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Why Choose Changepreneurship?</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Built on proven frameworks and powered by AI to maximize your chances of success
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon
              return (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <Icon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-semibold mb-2">{benefit.title}</h3>
                        <p className="text-sm text-muted-foreground">{benefit.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary mb-2">500+</div>
              <div className="text-muted-foreground">Assessment Questions</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">6</div>
              <div className="text-muted-foreground">Entrepreneur Archetypes</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">45+</div>
              <div className="text-muted-foreground">Business Assets</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">1000+</div>
              <div className="text-muted-foreground">Verified Investors</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-primary/10 to-accent/10">
        <div className="container mx-auto text-center">
          <h2 className="text-4xl font-bold mb-4">Ready to Transform Your Future?</h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of aspiring entrepreneurs who have discovered their path to success
          </p>
          {isAuthenticated ? (
            <Link to="/assessment">
              <Button size="lg" className="text-lg px-8 py-6">
                Continue Your Assessment
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          ) : (
            <Button 
              size="lg" 
              className="text-lg px-8 py-6"
              onClick={() => handleAuthAction('register')}
            >
              Start Your Assessment Now
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 border-t">
        <div className="container mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <TrendingUp className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">Changepreneurship</span>
          </div>
          <p className="text-muted-foreground">
            Empowering entrepreneurs with AI-driven insights and proven frameworks
          </p>
        </div>
      </footer>

      {/* Authentication Modal */}
      <AuthModal 
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        initialMode={authMode}
      />
    </div>
  )
}

export default LandingPage

