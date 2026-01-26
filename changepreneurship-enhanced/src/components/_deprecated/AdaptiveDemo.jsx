import React, { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { 
  Brain,
  User, 
  Target, 
  Sparkles,
  Zap,
  ArrowLeft,
  Play,
  Settings,
  BarChart3,
  Clock,
  CheckCircle,
  TrendingUp
} from 'lucide-react'

// Import adaptive components
import DataImportDemo from './adaptive/DataImportDemo'
import QuestionOptimizationDemo from './adaptive/QuestionOptimizationDemo'
import IntelligentSkipLogic from './adaptive/IntelligentSkipLogic'

// Import enhanced context
import { EnhancedAssessmentProvider } from '../contexts/EnhancedAssessmentContext'

export default function AdaptiveDemo() {
  const [currentTab, setCurrentTab] = useState('overview')

  const adaptiveFeatures = [
    { 
      id: 'overview', 
      label: 'Overview', 
      icon: BarChart3,
      description: 'Complete overview of data-driven assessment optimization'
    },
    { 
      id: 'data-import', 
      label: 'Data Import', 
      icon: Database,
      description: 'Connect data sources for automatic pre-population'
    },
    { 
      id: 'question-optimization', 
      label: 'Question Optimization', 
      icon: Sparkles,
      description: 'Smart question consolidation and pre-population'
    },
    { 
      id: 'skip-logic', 
      label: 'Skip Logic', 
      icon: Zap,
      description: 'Intelligent question prioritization and skipping'
    }
  ]

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Hero Section */}
      <Card className="bg-gradient-to-br from-gray-900 to-gray-800 border-gray-700">
        <CardHeader className="text-center pb-8">
          <CardTitle className="text-3xl font-bold text-white flex items-center justify-center gap-3">
            <Brain className="h-8 w-8 text-orange-500" />
            Intelligent Adaptive Assessment System
          </CardTitle>
          <CardDescription className="text-gray-300 text-lg mt-4">
            Experience the next generation of personalized entrepreneur assessment with AI-powered optimization
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
            <div className="text-center p-6 bg-gray-800/50 rounded-lg border border-gray-600">
              <div className="text-3xl font-bold text-orange-500 mb-2">500+</div>
              <div className="text-sm text-gray-400">Total Questions</div>
              <div className="text-xs text-gray-500 mt-1">Comprehensive coverage</div>
            </div>
            <div className="text-center p-6 bg-gray-800/50 rounded-lg border border-gray-600">
              <div className="text-3xl font-bold text-green-500 mb-2">60%</div>
              <div className="text-sm text-gray-400">Time Reduction</div>
              <div className="text-xs text-gray-500 mt-1">Smart optimization</div>
            </div>
            <div className="text-center p-6 bg-gray-800/50 rounded-lg border border-gray-600">
              <div className="text-3xl font-bold text-blue-500 mb-2">5</div>
              <div className="text-sm text-gray-400">Profile Types</div>
              <div className="text-xs text-gray-500 mt-1">Personalized paths</div>
            </div>
            <div className="text-center p-6 bg-gray-800/50 rounded-lg border border-gray-600">
              <div className="text-3xl font-bold text-purple-500 mb-2">AI</div>
              <div className="text-sm text-gray-400">Powered</div>
              <div className="text-xs text-gray-500 mt-1">Machine learning</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-gray-900 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <User className="h-5 w-5 text-blue-400" />
              Smart User Profiling
            </CardTitle>
            <CardDescription className="text-gray-400">
              AI automatically detects your entrepreneur type and experience level
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500" />
                5 distinct entrepreneur profiles
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500" />
                90%+ accuracy in profile detection
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Real-time adaptation to responses
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-400" />
              Question Consolidation
            </CardTitle>
            <CardDescription className="text-gray-400">
              Combines similar questions for maximum efficiency
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Reduces 8 questions to 1 comprehensive question
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Maintains 95% assessment accuracy
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Saves 12+ minutes per section
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Zap className="h-5 w-5 text-yellow-400" />
              Auto Pre-population
            </CardTitle>
            <CardDescription className="text-gray-400">
              Automatically fills answers based on your profile and responses
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500" />
                85% confidence threshold for auto-fill
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500" />
                User can review and modify any answer
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Learns from user corrections
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Target className="h-5 w-5 text-green-400" />
              Intelligent Skip Logic
            </CardTitle>
            <CardDescription className="text-gray-400">
              Skips irrelevant questions and prioritizes important ones
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500" />
                20+ skip conditions per question
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Dynamic priority reordering
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Context-aware question flow
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Benefits Summary */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-orange-500" />
            Optimization Benefits
          </CardTitle>
          <CardDescription className="text-gray-400">
            How adaptive assessment transforms the user experience
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-gray-800 rounded-lg">
              <Clock className="h-8 w-8 text-blue-400 mx-auto mb-3" />
              <h3 className="text-white font-semibold mb-2">Time Efficiency</h3>
              <p className="text-gray-400 text-sm">
                Reduces assessment time from 8+ hours to 3-4 hours while maintaining comprehensive coverage
              </p>
            </div>
            <div className="text-center p-4 bg-gray-800 rounded-lg">
              <Target className="h-8 w-8 text-green-400 mx-auto mb-3" />
              <h3 className="text-white font-semibold mb-2">Personalization</h3>
              <p className="text-gray-400 text-sm">
                Tailors questions and explanations to user's experience level and entrepreneur type
              </p>
            </div>
            <div className="text-center p-4 bg-gray-800 rounded-lg">
              <Brain className="h-8 w-8 text-purple-400 mx-auto mb-3" />
              <h3 className="text-white font-semibold mb-2">Intelligence</h3>
              <p className="text-gray-400 text-sm">
                Learns from user responses to continuously improve accuracy and relevance
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Call to Action */}
      <div className="text-center">
        <Button
          onClick={() => setCurrentTab('profile-detection')}
          size="lg"
          className="bg-orange-600 hover:bg-orange-700 text-white px-8 py-3 text-lg"
        >
          <Play className="h-5 w-5 mr-2" />
          Explore Adaptive Features
        </Button>
      </div>
    </div>
  )

  const renderTabContent = () => {
    switch (currentTab) {
      case 'overview':
        return renderOverview()
      case 'profile-detection':
        return <UserProfileDetection />
      case 'assessment-path':
        return <PersonalizedAssessmentPath />
      case 'question-optimization':
        return <QuestionOptimizationDemo />
      case 'skip-logic':
        return <IntelligentSkipLogic />
      default:
        return renderOverview()
    }
  }

  return (
    <EnhancedAssessmentProvider>
      <div className="min-h-screen bg-black text-white">
        {/* Header */}
        <header className="bg-gray-900 border-b border-gray-700 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              {/* Logo and Title */}
              <div className="flex items-center gap-4">
                <Button
                  onClick={() => window.history.back()}
                  variant="ghost"
                  size="sm"
                  className="text-gray-400 hover:text-white"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Button>
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-bold text-orange-500">Changepreneurship</h1>
                  <Badge variant="secondary" className="bg-purple-900 text-purple-300">
                    <Brain className="h-3 w-3 mr-1" />
                    Adaptive Demo
                  </Badge>
                </div>
              </div>

              {/* Navigation */}
              <nav className="hidden md:block">
                <div className="flex items-center space-x-1">
                  {adaptiveFeatures.slice(1).map((feature) => {
                    const IconComponent = feature.icon
                    return (
                      <button
                        key={feature.id}
                        onClick={() => setCurrentTab(feature.id)}
                        className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
                          currentTab === feature.id
                            ? 'bg-orange-600 text-white'
                            : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                        }`}
                      >
                        <IconComponent className="h-4 w-4" />
                        <span className="hidden lg:inline">{feature.label}</span>
                      </button>
                    )
                  })}
                </div>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Tabs value={currentTab} onValueChange={setCurrentTab} className="w-full">
            {/* Mobile Tab Navigation */}
            <div className="md:hidden mb-6">
              <TabsList className="grid w-full grid-cols-3 bg-gray-800">
                <TabsTrigger value="overview" className="text-gray-300">
                  <BarChart3 className="h-4 w-4" />
                </TabsTrigger>
                <TabsTrigger value="profile-detection" className="text-gray-300">
                  <User className="h-4 w-4" />
                </TabsTrigger>
                <TabsTrigger value="question-optimization" className="text-gray-300">
                  <Sparkles className="h-4 w-4" />
                </TabsTrigger>
              </TabsList>
            </div>

            {/* Tab Content */}
            <div className="space-y-6">
              {renderTabContent()}
            </div>
          </Tabs>
        </main>

        {/* Feature Navigation Cards (Desktop) */}
        {currentTab === 'overview' && (
          <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {adaptiveFeatures.slice(1).map((feature) => {
                const IconComponent = feature.icon
                return (
                  <Card 
                    key={feature.id}
                    className="bg-gray-900 border-gray-700 cursor-pointer hover:bg-gray-800 transition-colors"
                    onClick={() => setCurrentTab(feature.id)}
                  >
                    <CardHeader className="pb-3">
                      <CardTitle className="text-white text-sm flex items-center gap-2">
                        <IconComponent className="h-4 w-4 text-orange-500" />
                        {feature.label}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <p className="text-gray-400 text-xs">{feature.description}</p>
                      <Button
                        size="sm"
                        variant="outline"
                        className="mt-3 w-full border-gray-600 text-gray-300 hover:bg-gray-800"
                      >
                        Explore
                      </Button>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </section>
        )}

        {/* Footer */}
        <footer className="bg-gray-900 border-t border-gray-700 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center">
              <p className="text-gray-400">
                © 2024 Changepreneurship. Empowering entrepreneurs with intelligent assessment technology.
              </p>
              <div className="mt-4 flex justify-center gap-4">
                <Badge variant="secondary" className="bg-blue-900 text-blue-300">
                  <User className="h-3 w-3 mr-1" />
                  Smart Profiling
                </Badge>
                <Badge variant="secondary" className="bg-purple-900 text-purple-300">
                  <Sparkles className="h-3 w-3 mr-1" />
                  Question Optimization
                </Badge>
                <Badge variant="secondary" className="bg-green-900 text-green-300">
                  <Zap className="h-3 w-3 mr-1" />
                  Intelligent Skip Logic
                </Badge>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </EnhancedAssessmentProvider>
  )
}

