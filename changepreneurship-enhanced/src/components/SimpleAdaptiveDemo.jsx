import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import { 
  Database,
  Clock, 
  Zap, 
  CheckCircle,
  TrendingUp,
  Target,
  Sparkles,
  BarChart3,
  ArrowLeft,
  DollarSign,
  FileText
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

// Import simplified components
import SimpleDataImport from './adaptive/SimpleDataImport'
import QuestionOptimizationDemo from './adaptive/QuestionOptimizationDemo'
import IntelligentSkipLogic from './adaptive/IntelligentSkipLogic'

export default function SimpleAdaptiveDemo() {
  const [currentTab, setCurrentTab] = useState('overview')
  const navigate = useNavigate()

  const adaptiveFeatures = [
    { 
      id: 'overview', 
      label: 'Overview', 
      icon: BarChart3,
      description: 'Simple data-driven assessment optimization'
    },
    { 
      id: 'data-import', 
      label: 'Data Import', 
      icon: Database,
      description: 'Connect sources for automatic pre-population'
    },
    { 
      id: 'optimization', 
      label: 'Optimization', 
      icon: Sparkles,
      description: 'Question consolidation and time savings'
    },
    { 
      id: 'skip-logic', 
      label: 'Skip Logic', 
      icon: Zap,
      description: 'Smart question filtering'
    }
  ]

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Hero Section */}
      <Card className="bg-gradient-to-r from-orange-900/20 to-gray-900 border-orange-500">
        <CardHeader>
          <CardTitle className="text-white text-2xl flex items-center gap-3">
            <Database className="h-8 w-8 text-orange-500" />
            Data-Driven Assessment Optimization
          </CardTitle>
          <CardDescription className="text-gray-300 text-lg">
            Simple approach: More data import = More pre-population = Faster assessment
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-800/50 rounded-lg">
              <div className="text-3xl font-bold text-blue-400 mb-2">85%</div>
              <div className="text-sm text-gray-300">Pre-populated</div>
            </div>
            <div className="text-center p-4 bg-gray-800/50 rounded-lg">
              <div className="text-3xl font-bold text-green-400 mb-2">43m</div>
              <div className="text-sm text-gray-300">Time Saved</div>
            </div>
            <div className="text-center p-4 bg-gray-800/50 rounded-lg">
              <div className="text-3xl font-bold text-purple-400 mb-2">6</div>
              <div className="text-sm text-gray-300">Data Sources</div>
            </div>
            <div className="text-center p-4 bg-gray-800/50 rounded-lg">
              <div className="text-3xl font-bold text-orange-400 mb-2">15m</div>
              <div className="text-sm text-gray-300">Final Time</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Simple Process */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Target className="h-5 w-5 text-orange-500" />
            How It Works (Simple)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto">
                <Database className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-white font-semibold">1. Connect Data</h3>
              <p className="text-gray-400 text-sm">
                Link LinkedIn, social media, financial accounts, resume, etc.
              </p>
            </div>
            
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center mx-auto">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-white font-semibold">2. AI Pre-populates</h3>
              <p className="text-gray-400 text-sm">
                System analyzes your data and fills in relevant answers automatically
              </p>
            </div>
            
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center mx-auto">
                <CheckCircle className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-white font-semibold">3. Quick Review</h3>
              <p className="text-gray-400 text-sm">
                Review and adjust pre-populated answers, complete in 15-20 minutes
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Sources Impact */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-500" />
            Data Source Impact
          </CardTitle>
          <CardDescription className="text-gray-400">
            See how each data source speeds up your assessment
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
              <div className="flex items-center gap-3">
                <Database className="h-5 w-5 text-blue-400" />
                <div>
                  <div className="text-white font-medium">LinkedIn Profile</div>
                  <div className="text-gray-400 text-sm">Work experience, education, skills</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-green-400 font-bold">15m saved</div>
                <div className="text-purple-400 text-sm">85% coverage</div>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
              <div className="flex items-center gap-3">
                <DollarSign className="h-5 w-5 text-green-400" />
                <div>
                  <div className="text-white font-medium">Financial Data</div>
                  <div className="text-gray-400 text-sm">Income, expenses, savings</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-green-400 font-bold">10m saved</div>
                <div className="text-purple-400 text-sm">60% coverage</div>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-orange-400" />
                <div>
                  <div className="text-white font-medium">Resume/CV</div>
                  <div className="text-gray-400 text-sm">Work history, achievements</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-green-400 font-bold">12m saved</div>
                <div className="text-purple-400 text-sm">70% coverage</div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-green-900/20 border border-green-500 rounded-lg">
            <div className="text-center">
              <div className="text-green-400 font-bold text-lg">Total Potential: 43 minutes saved</div>
              <div className="text-gray-300 text-sm">Complete assessment in 15-20 minutes instead of 60</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <div className="border-b border-gray-800 bg-gray-900/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                onClick={() => navigate('/')}
                variant="ghost"
                size="sm"
                className="text-gray-400 hover:text-white"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <h1 className="text-xl font-bold text-white">
                Simple Adaptive Assessment Demo
              </h1>
            </div>
            <Badge variant="secondary" className="bg-orange-900 text-orange-300">
              Data-Driven Optimization
            </Badge>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <Tabs value={currentTab} onValueChange={setCurrentTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 bg-gray-800 mb-8">
            {adaptiveFeatures.map((feature) => {
              const IconComponent = feature.icon
              return (
                <TabsTrigger 
                  key={feature.id}
                  value={feature.id} 
                  className="text-gray-300 data-[state=active]:text-orange-500 data-[state=active]:bg-gray-700"
                >
                  <IconComponent className="h-4 w-4 mr-2" />
                  {feature.label}
                </TabsTrigger>
              )
            })}
          </TabsList>

          <TabsContent value="overview">
            {renderOverview()}
          </TabsContent>

          <TabsContent value="data-import">
            <SimpleDataImport />
          </TabsContent>

          <TabsContent value="optimization">
            <QuestionOptimizationDemo />
          </TabsContent>

          <TabsContent value="skip-logic">
            <IntelligentSkipLogic />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

