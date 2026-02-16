import React, { useState, useEffect } from 'react'
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
import { PHASES, phaseIdToSlug } from '@/lib/assessmentPhases.js'

const LandingPage = () => {
  const { isAuthenticated } = useAuth()
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState('login')
  const [typedText, setTypedText] = useState('')
  const fullText = 'Autonomously.'
  
  useEffect(() => {
    if (typedText.length < fullText.length) {
      const timeout = setTimeout(() => {
        setTypedText(fullText.slice(0, typedText.length + 1))
      }, 100)
      return () => clearTimeout(timeout)
    }
  }, [typedText])

  const handleAuthAction = (mode) => {
    if (isAuthenticated) {
      // User is already authenticated, navigate directly
      return
    }
    setAuthMode(mode)
    setAuthModalOpen(true)
  }
  // Merge static icon/color styling with central PHASES metadata
  const phaseVisual = {
    self_discovery: { icon: User, color: 'from-orange-500 to-red-600', landingTitle: 'Self-Discovery Assessment' },
    idea_discovery: { icon: Lightbulb, color: 'from-blue-500 to-purple-600' },
    market_research: { icon: Search, color: 'from-green-500 to-teal-600' },
    business_pillars: { icon: Building, color: 'from-purple-500 to-pink-600', landingTitle: 'Business Pillars Planning' },
    product_concept_testing: { icon: Target, color: 'from-indigo-500 to-purple-600' },
    business_development: { icon: TrendingUp, color: 'from-emerald-500 to-teal-600' },
    business_prototype_testing: { icon: Zap, color: 'from-rose-500 to-pink-600' }
  }

  const features = PHASES.map((p) => {
    const visual = phaseVisual[p.id] || {}
    return {
      id: p.id,
      slug: p.slug,
      icon: visual.icon || User,
      title: visual.landingTitle || p.title,
      description: '', // original long descriptions could be restored or centralized later
      duration: p.duration,
      color: visual.color || 'from-primary to-accent',
      phase: p.category
    }
  })

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
    <div className="min-h-screen bg-black text-white">
      {/* Navigation Header */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/60 backdrop-blur-lg border-b border-cyan-500/20">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="absolute inset-0 bg-cyan-500 blur-lg opacity-50"></div>
                <TrendingUp className="h-8 w-8 text-cyan-400 relative" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                Changepreneurship
              </span>
            </div>
            
            <div className="flex items-center gap-4">
              {isAuthenticated ? (
                <UserProfile />
              ) : (
                <div className="flex items-center gap-3">
                  <Button 
                    variant="ghost" 
                    onClick={() => handleAuthAction('login')}
                    className="text-gray-300 hover:text-white hover:bg-white/10"
                  >
                    Log In
                  </Button>
                  <Button 
                    onClick={() => handleAuthAction('register')}
                    className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-white border-0 shadow-lg shadow-cyan-500/50"
                  >
                    Start Building
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section with Background */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background Image - Sharp, Only Darkened */}
        <div 
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: 'url(/bg.jpg)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          }}
        >
          {/* Dark overlay - NO BLUR, just darkening */}
          <div className="absolute inset-0 bg-black/60"></div>
        </div>
        
        {/* Animated overlay effects - more subtle */}
        <div className="absolute inset-0 z-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>

        {/* Content */}
        <div className="container mx-auto px-6 text-center relative z-10 pt-20">
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold mb-6 leading-tight">
            <span className="block text-white drop-shadow-2xl">From Idea to IPO,</span>
            <span className="block bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent drop-shadow-2xl">
              {typedText}<span className="animate-pulse">|</span>
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
            The world's first cognitive venture architecture. Orchestrate AI agents to
            <br />validate, build, and scale your business in real-time.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
            {isAuthenticated ? (
              <>
                <Link to="/assessment">
                  <Button 
                    size="lg" 
                    className="text-lg px-10 py-7 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-white border-0 shadow-2xl shadow-cyan-500/50 rounded-full font-semibold"
                  >
                    Continue Assessment
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link to="/dashboard">
                  <Button 
                    variant="outline" 
                    size="lg" 
                    className="text-lg px-10 py-7 bg-white/5 hover:bg-white/10 text-white border-white/20 backdrop-blur-sm rounded-full"
                  >
                    <Brain className="mr-2 h-5 w-5" />
                    Dashboard
                  </Button>
                </Link>
              </>
            ) : (
              <>
                <Button 
                  size="lg" 
                  className="text-lg px-10 py-7 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-white border-0 shadow-2xl shadow-cyan-500/50 rounded-full font-semibold transform hover:scale-105 transition-transform"
                  onClick={() => handleAuthAction('register')}
                >
                  Start Building
                  <ArrowRight className="ml-3 h-5 w-5" />
                </Button>
              </>
            )}
          </div>

          {/* Tech badge */}
          <div className="mt-16 flex items-center justify-center gap-8 text-gray-500 text-sm">
            <span className="uppercase tracking-wider">Powered by Next-Gen Intelligence</span>
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded border border-gray-700 flex items-center justify-center hover:border-cyan-500/50 transition-colors">
                <span className="text-xs">AI</span>
              </div>
              <div className="w-8 h-8 rounded-full border border-gray-700 flex items-center justify-center hover:border-cyan-500/50 transition-colors">
                <span className="text-xs">◇</span>
              </div>
              <div className="w-8 h-8 rounded border border-gray-700 rotate-45 flex items-center justify-center hover:border-cyan-500/50 transition-colors">
                <span className="text-xs -rotate-45">▢</span>
              </div>
              <div className="w-8 h-8 border border-gray-700 flex items-center justify-center hover:border-cyan-500/50 transition-colors">
                <span className="text-xs">□</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-6 bg-black">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 mb-6">
              <span className="text-cyan-400 text-sm uppercase tracking-wider">Our Framework</span>
            </div>
            <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              7-Stage Architecture
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Navigate every phase of your entrepreneurial journey with precision
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon
              const targetPath = `/assessment/${feature.slug}`
              const card = (
                <Card
                  key={index}
                  className="relative overflow-hidden group hover:shadow-2xl hover:shadow-cyan-500/20 transition-all duration-500 cursor-pointer bg-gradient-to-br from-gray-900 to-black border-gray-800 hover:border-cyan-500/50"
                  onClick={(e) => {
                    if (!isAuthenticated) {
                      setAuthMode('register')
                      setAuthModalOpen(true)
                    }
                  }}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      if (!isAuthenticated) {
                        setAuthMode('register')
                        setAuthModalOpen(true)
                      }
                    }
                  }}
                  aria-label={`Open ${feature.title} assessment`}
                >
                  <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity duration-500`} />
                  
                  {/* Glow effect */}
                  <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500/0 via-cyan-500/20 to-purple-500/0 opacity-0 group-hover:opacity-100 blur transition-opacity duration-500"></div>
                  
                  <CardHeader className="relative">
                    <div className="flex items-center justify-between mb-4">
                      <div className={`p-3 rounded-lg bg-gradient-to-br ${feature.color} shadow-lg`}>
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        <Badge variant="outline" className="text-xs bg-cyan-500/10 border-cyan-500/30 text-cyan-400">
                          Stage {index + 1}
                        </Badge>
                      </div>
                    </div>
                    <CardTitle className="text-lg flex items-center justify-between gap-2 text-white">
                      <span>{feature.title}</span>
                      <ArrowRight className="h-4 w-4 text-gray-500 group-hover:text-cyan-400 transition-colors transform group-hover:translate-x-1" />
                    </CardTitle>
                    <CardDescription className="text-sm text-gray-400">{feature.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="relative">
                    <div className="flex items-center justify-between">
                      <Badge variant="secondary" className="text-xs bg-gray-800 text-gray-300">{feature.duration}</Badge>
                      <span className="text-xs text-gray-500 group-hover:text-cyan-400 transition-colors">
                        {isAuthenticated ? 'Launch →' : 'Authenticate'}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              )
              // If authenticated, wrap in Link for SPA navigation; otherwise clickable card opens modal
              return isAuthenticated ? (
                <Link key={index} to={targetPath} className="block focus:outline-none focus:ring-2 focus:ring-primary rounded-lg">
                  {card}
                </Link>
              ) : card
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-6 bg-gradient-to-b from-black via-gray-900 to-black">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 mb-6">
              <span className="text-purple-400 text-sm uppercase tracking-wider">Advantages</span>
            </div>
            <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Enterprise-Grade Intelligence
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Built on proven frameworks and powered by AI to maximize your success probability
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon
              return (
                <Card 
                  key={index} 
                  className="bg-gradient-to-br from-gray-900 to-black border-gray-800 hover:border-purple-500/50 hover:shadow-2xl hover:shadow-purple-500/20 transition-all duration-500 group"
                >
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/30 group-hover:bg-purple-500/20 transition-colors">
                        <Icon className="h-6 w-6 text-purple-400" />
                      </div>
                      <div>
                        <h3 className="font-semibold mb-2 text-white">{benefit.title}</h3>
                        <p className="text-sm text-gray-400">{benefit.description}</p>
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
      <section className="py-20 px-6 bg-black border-y border-cyan-500/20">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div className="group">
              <div className="text-5xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform">
                500+
              </div>
              <div className="text-gray-400 text-sm uppercase tracking-wider">Assessment Vectors</div>
            </div>
            <div className="group">
              <div className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform">
                6
              </div>
              <div className="text-gray-400 text-sm uppercase tracking-wider">Entrepreneur Profiles</div>
            </div>
            <div className="group">
              <div className="text-5xl font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform">
                45+
              </div>
              <div className="text-gray-400 text-sm uppercase tracking-wider">Strategic Assets</div>
            </div>
            <div className="group">
              <div className="text-5xl font-bold bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform">
                1000+
              </div>
              <div className="text-gray-400 text-sm uppercase tracking-wider">Capital Partners</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 px-6 bg-gradient-to-br from-cyan-900/20 via-black to-purple-900/20 relative overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>
        
        <div className="container mx-auto text-center relative z-10">
          <h2 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
            Ready to Build the Future?
          </h2>
          <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
            Join the next generation of entrepreneurs leveraging AI-powered intelligence
          </p>
          {isAuthenticated ? (
            <Link to="/assessment">
              <Button 
                size="lg" 
                className="text-lg px-12 py-8 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-white border-0 shadow-2xl shadow-cyan-500/50 rounded-full font-semibold transform hover:scale-105 transition-transform"
              >
                Continue Your Assessment
                <ArrowRight className="ml-3 h-6 w-6" />
              </Button>
            </Link>
          ) : (
            <Button 
              size="lg" 
              className="text-lg px-12 py-8 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-white border-0 shadow-2xl shadow-cyan-500/50 rounded-full font-semibold transform hover:scale-105 transition-transform"
              onClick={() => handleAuthAction('register')}
            >
              Initialize Your Journey
              <ArrowRight className="ml-3 h-6 w-6" />
            </Button>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-gray-800 bg-black">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="absolute inset-0 bg-cyan-500 blur-lg opacity-30"></div>
                <TrendingUp className="h-6 w-6 text-cyan-400 relative" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                Changepreneurship
              </span>
            </div>
            <p className="text-gray-500 text-sm">
              Cognitive Venture Architecture © 2026
            </p>
            <div className="flex gap-6 text-sm text-gray-500">
              <a href="#" className="hover:text-cyan-400 transition-colors">Privacy</a>
              <a href="#" className="hover:text-cyan-400 transition-colors">Terms</a>
              <a href="#" className="hover:text-cyan-400 transition-colors">API</a>
            </div>
          </div>
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

