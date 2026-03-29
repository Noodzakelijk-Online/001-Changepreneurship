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
    self_discovery: { icon: User, color: 'from-orange-500 to-red-600', landingTitle: 'Self-Discovery Assessment', landingDescription: 'Understand your strengths, values, and entrepreneurial motivation before committing to a venture' },
    idea_discovery: { icon: Lightbulb, color: 'from-blue-500 to-purple-600', landingDescription: 'Evaluate your business idea against real-world criteria and identify your target customer' },
    market_research: { icon: Search, color: 'from-green-500 to-teal-600', landingDescription: 'Validate demand through customer research and competitive landscape analysis' },
    business_pillars: { icon: Building, color: 'from-purple-500 to-pink-600', landingTitle: 'Business Pillars Planning', landingDescription: 'Define your revenue model, pricing strategy, and key operational elements' },
    product_concept_testing: { icon: Target, color: 'from-indigo-500 to-purple-600', landingDescription: 'Test your product concept with potential customers to refine your offering' },
    business_development: { icon: TrendingUp, color: 'from-emerald-500 to-teal-600', landingDescription: 'Build your go-to-market strategy and growth framework' },
    business_prototype_testing: { icon: Zap, color: 'from-rose-500 to-pink-600', landingDescription: 'Validate your prototype and gather actionable feedback before full launch' }
  }

  const features = PHASES.map((p) => {
    const visual = phaseVisual[p.id] || {}
    return {
      id: p.id,
      slug: p.slug,
      icon: visual.icon || User,
      title: visual.landingTitle || p.title,
      description: visual.landingDescription || '',
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
      title: 'Structured Progress',
      description: 'Track your journey across all 7 phases with clear milestones and completion metrics'
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
          <div className="absolute inset-0 bg-black/80"></div>
          {/* Inner stroke effect */}
          <div className="absolute inset-0 shadow-[inset_0_0_100px_rgba(0,0,0,0.5)]"></div>
          {/* Gradient fade to black at bottom for smooth blending */}
          <div className="absolute bottom-0 left-0 right-0 h-64 bg-gradient-to-b from-transparent to-black"></div>
        </div>
        
        {/* Animated overlay effects - more subtle */}
        <div className="absolute inset-0 z-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>

        {/* Content */}
        <div className="container mx-auto px-6 text-center relative z-10 pt-20">
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold mb-6 leading-tight">
            <span className="block text-white drop-shadow-2xl">Know Yourself.</span>
            <span className="block bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent drop-shadow-2xl">
              Validate Your Idea.
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
            A structured 7-stage assessment that evaluates your entrepreneurial mindset,
            <br />validates your business idea, and delivers AI-powered insights to guide your next move.
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
          <div className="mt-16 flex flex-col sm:flex-row items-center justify-center gap-6 text-sm">
            <div className="flex items-center gap-2 text-gray-500">
              <CheckCircle className="h-4 w-4 text-cyan-500" />
              <span>500+ assessment questions</span>
            </div>
            <div className="flex items-center gap-2 text-gray-500">
              <CheckCircle className="h-4 w-4 text-cyan-500" />
              <span>AI insights report</span>
            </div>
            <div className="flex items-center gap-2 text-gray-500">
              <CheckCircle className="h-4 w-4 text-cyan-500" />
              <span>Free to start</span>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-28 px-6 bg-black relative overflow-hidden">
        {/* Subtle background glow */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute left-1/4 top-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-3xl"></div>
          <div className="absolute right-1/4 top-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-3xl"></div>
        </div>

        <div className="container mx-auto relative z-10">
          <div className="text-center mb-20">
            <div className="inline-block px-4 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 mb-6">
              <span className="text-cyan-400 text-sm uppercase tracking-widest">How It Works</span>
            </div>
            <h2 className="text-5xl font-bold mb-4 text-white">
              Three steps to clarity
            </h2>
            <p className="text-lg text-gray-500 max-w-xl mx-auto">
              From your first answer to a personalized AI strategy — in under an hour.
            </p>
          </div>

          {/* Steps */}
          <div className="relative">
            {/* Connecting line */}
            <div className="hidden lg:block absolute top-[52px] left-[calc(16.66%+32px)] right-[calc(16.66%+32px)] h-px bg-gradient-to-r from-cyan-500/40 via-purple-500/40 to-pink-500/40"></div>

            <div className="grid lg:grid-cols-3 gap-8 lg:gap-12">
              {/* Step 1 */}
              <div className="group flex flex-col items-center text-center">
                <div className="relative mb-8">
                  <div className="absolute inset-0 bg-cyan-500/20 rounded-full blur-xl group-hover:bg-cyan-500/40 transition-all duration-500"></div>
                  <div className="relative w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500 to-cyan-700 flex items-center justify-center shadow-lg shadow-cyan-500/30 group-hover:scale-110 transition-transform duration-300">
                    <User className="h-7 w-7 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-black border border-cyan-500/50 flex items-center justify-center">
                    <span className="text-xs font-bold text-cyan-400">1</span>
                  </div>
                </div>
                <div className="bg-gradient-to-b from-gray-900 to-black border border-gray-800 group-hover:border-cyan-500/40 rounded-2xl p-8 w-full transition-all duration-500 group-hover:shadow-2xl group-hover:shadow-cyan-500/10">
                  <h3 className="text-xl font-bold text-white mb-3">Assess Yourself</h3>
                  <p className="text-gray-400 leading-relaxed">
                    Answer structured questions about your mindset, values, risk tolerance, and entrepreneurial motivation. Understand who you are as a founder before choosing an idea.
                  </p>
                  <div className="mt-5 flex flex-wrap gap-2 justify-center">
                    <span className="px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs">Self-Discovery</span>
                    <span className="px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs">Values & Strengths</span>
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className="group flex flex-col items-center text-center lg:mt-8">
                <div className="relative mb-8">
                  <div className="absolute inset-0 bg-purple-500/20 rounded-full blur-xl group-hover:bg-purple-500/40 transition-all duration-500"></div>
                  <div className="relative w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center shadow-lg shadow-purple-500/30 group-hover:scale-110 transition-transform duration-300">
                    <Lightbulb className="h-7 w-7 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-black border border-purple-500/50 flex items-center justify-center">
                    <span className="text-xs font-bold text-purple-400">2</span>
                  </div>
                </div>
                <div className="bg-gradient-to-b from-gray-900 to-black border border-gray-800 group-hover:border-purple-500/40 rounded-2xl p-8 w-full transition-all duration-500 group-hover:shadow-2xl group-hover:shadow-purple-500/10">
                  <h3 className="text-xl font-bold text-white mb-3">Validate Your Idea</h3>
                  <p className="text-gray-400 leading-relaxed">
                    Work through 6 additional stages — from market research and customer validation to business modeling and prototype testing. Each phase builds on the last.
                  </p>
                  <div className="mt-5 flex flex-wrap gap-2 justify-center">
                    <span className="px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs">Market Research</span>
                    <span className="px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs">Customer Validation</span>
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className="group flex flex-col items-center text-center">
                <div className="relative mb-8">
                  <div className="absolute inset-0 bg-pink-500/20 rounded-full blur-xl group-hover:bg-pink-500/40 transition-all duration-500"></div>
                  <div className="relative w-16 h-16 rounded-full bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center shadow-lg shadow-pink-500/30 group-hover:scale-110 transition-transform duration-300">
                    <Brain className="h-7 w-7 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-black border border-pink-500/50 flex items-center justify-center">
                    <span className="text-xs font-bold text-pink-400">3</span>
                  </div>
                </div>
                <div className="bg-gradient-to-b from-gray-900 to-black border border-gray-800 group-hover:border-pink-500/40 rounded-2xl p-8 w-full transition-all duration-500 group-hover:shadow-2xl group-hover:shadow-pink-500/10">
                  <h3 className="text-xl font-bold text-white mb-3">Get Your AI Report</h3>
                  <p className="text-gray-400 leading-relaxed">
                    Receive a personalized AI-generated insights report — your founder profile, idea viability score, identified risks, and concrete next steps tailored to your data.
                  </p>
                  <div className="mt-5 flex flex-wrap gap-2 justify-center">
                    <span className="px-3 py-1 rounded-full bg-pink-500/10 border border-pink-500/20 text-pink-400 text-xs">AI Insights</span>
                    <span className="px-3 py-1 rounded-full bg-pink-500/10 border border-pink-500/20 text-pink-400 text-xs">Action Plan</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Preview Section */}
      <section className="py-28 px-6 bg-gradient-to-b from-black via-gray-950 to-black relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[400px] bg-purple-500/5 rounded-full blur-3xl"></div>
        </div>

        <div className="container mx-auto relative z-10">
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 mb-6">
              <span className="text-purple-400 text-sm uppercase tracking-widest">Inside the App</span>
            </div>
            <h2 className="text-5xl font-bold mb-4 text-white">See it in action</h2>
            <p className="text-lg text-gray-500 max-w-xl mx-auto">
              A focused, distraction-free experience that guides you through every question.
            </p>
          </div>

          {/* Browser mockup */}
          <div className="max-w-4xl mx-auto">
            <div className="bg-gray-900 rounded-2xl border border-gray-700/50 shadow-2xl shadow-black overflow-hidden">
              {/* Browser chrome */}
              <div className="bg-gray-800/80 px-4 py-3 flex items-center gap-3 border-b border-gray-700/50">
                <div className="flex gap-1.5 flex-shrink-0">
                  <div className="w-3 h-3 rounded-full bg-red-500/50"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500/50"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500/50"></div>
                </div>
                <div className="flex-1 flex justify-center">
                  <div className="bg-gray-700/50 rounded-md px-4 py-1 text-xs text-gray-400 max-w-xs w-full text-center">
                    changepreneurship.duckdns.org/assessment
                  </div>
                </div>
                <div className="w-16 flex-shrink-0"></div>
              </div>

              {/* App content mockup */}
              <div className="bg-gray-950 p-6 md:p-10">
                {/* Stage progress bar */}
                <div className="flex items-center gap-1.5 mb-8">
                  {['Self Discovery', 'Idea Discovery', 'Market Research', 'Business Pillars', '...'].map((stage, i) => (
                    <React.Fragment key={i}>
                      <div className="flex flex-col items-center gap-1">
                        <div className={`h-1.5 w-14 md:w-20 rounded-full ${i === 0 ? 'bg-gradient-to-r from-cyan-500 to-cyan-400' : i === 1 ? 'bg-cyan-500/25' : 'bg-gray-800'}`}></div>
                        <span className="hidden md:block text-xs text-gray-600 whitespace-nowrap">{stage}</span>
                      </div>
                      {i < 4 && <div className="w-2 h-px bg-gray-800 flex-shrink-0 mb-3 md:mb-0"></div>}
                    </React.Fragment>
                  ))}
                </div>

                {/* Stage badge */}
                <div className="flex items-center gap-3 mb-6">
                  <div className="px-2.5 py-1 rounded-lg bg-cyan-500/10 border border-cyan-500/25 text-cyan-400 text-xs uppercase tracking-wide font-medium">
                    Stage 1 — Self Discovery
                  </div>
                  <div className="text-gray-600 text-xs">Question 3 of 7</div>
                </div>

                {/* Question */}
                <h3 className="text-xl font-semibold text-white mb-2">What primarily motivates you to start a business?</h3>
                <p className="text-gray-500 text-sm mb-6">Select the option that best reflects your core motivation as a founder.</p>

                {/* Answer options */}
                <div className="space-y-3">
                  {[
                    { label: 'Financial freedom and wealth creation', selected: false },
                    { label: 'Solving a problem I personally experienced', selected: true },
                    { label: 'Building something that outlasts me', selected: false },
                    { label: 'Escaping traditional employment', selected: false },
                  ].map((opt, i) => (
                    <div
                      key={i}
                      className={`flex items-center gap-4 p-4 rounded-xl border transition-all ${
                        opt.selected
                          ? 'border-cyan-500/50 bg-cyan-500/8 text-white'
                          : 'border-gray-800 bg-black/30 text-gray-500'
                      }`}
                    >
                      <div className={`w-4 h-4 rounded-full flex-shrink-0 border-2 flex items-center justify-center ${
                        opt.selected ? 'border-cyan-500 bg-cyan-500' : 'border-gray-700'
                      }`}>
                        {opt.selected && <div className="w-1.5 h-1.5 rounded-full bg-white"></div>}
                      </div>
                      <span className="text-sm">{opt.label}</span>
                    </div>
                  ))}
                </div>

                {/* Bottom row */}
                <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-800/50">
                  <div className="flex items-center gap-2 text-gray-600 text-xs">
                    <CheckCircle className="h-3.5 w-3.5 text-emerald-500/60" />
                    Progress saved automatically
                  </div>
                  <div className="bg-gradient-to-r from-cyan-500 to-purple-500 text-white text-sm px-6 py-2 rounded-lg font-medium">
                    Next Question →
                  </div>
                </div>
              </div>
            </div>

            {/* Caption below mockup */}
            <p className="text-center text-gray-600 text-sm mt-6">
              Your answers are saved after every question — come back anytime.
            </p>
          </div>
        </div>
      </section>

      {/* 7-Stage Architecture Section */}
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
              Built for Serious Founders
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Evidence-based frameworks and AI analysis so you build the right thing from day one
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
                7
              </div>
              <div className="text-gray-400 text-sm uppercase tracking-wider">Assessment Stages</div>
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
            Ready to Find Out If You're Built for This?
          </h2>
          <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
            Most founders skip self-assessment and waste months on the wrong idea. Don't.
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
              Start Your Assessment
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
              © 2026 Changepreneurship. All rights reserved.
            </p>
            <div className="flex gap-6 text-sm text-gray-500">
              <span className="cursor-default">v1.0 — Early Access</span>
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

