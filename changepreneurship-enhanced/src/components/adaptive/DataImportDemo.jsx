import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Progress } from '../ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { 
  Database,
  Clock, 
  Zap, 
  CheckCircle,
  Plus,
  Linkedin,
  Mail,
  Calendar,
  DollarSign,
  FileText,
  Share,
  ArrowRight,
  TrendingUp,
  Target,
  Download
} from 'lucide-react'

// Import the data-driven engine
import { DATA_SOURCES, DataDrivenAdaptiveEngine } from '../../contexts/DataDrivenAdaptiveEngine'

const SourceIcons = {
  linkedin: Linkedin,
  share: Share,
  mail: Mail,
  calendar: Calendar,
  'dollar-sign': DollarSign,
  'file-text': FileText
}

export default function DataImportDemo() {
  const [connectedSources, setConnectedSources] = useState([])
  const [optimization, setOptimization] = useState({})
  const [showImportDemo, setShowImportDemo] = useState(false)
  const [importProgress, setImportProgress] = useState(0)
  const [importedData, setImportedData] = useState({})

  const adaptiveEngine = new DataDrivenAdaptiveEngine()

  // Calculate optimization when sources change
  useEffect(() => {
    const opt = adaptiveEngine.calculateOptimization(connectedSources, importedData)
    setOptimization(opt)
  }, [connectedSources, importedData])

  // Simulate data source connection
  const connectDataSource = (sourceId) => {
    if (connectedSources.includes(sourceId)) return
    
    setConnectedSources(prev => [...prev, sourceId])
    
    // Simulate data import
    setShowImportDemo(true)
    setImportProgress(0)
    
    const importInterval = setInterval(() => {
      setImportProgress(prev => {
        if (prev >= 100) {
          clearInterval(importInterval)
          setShowImportDemo(false)
          
          // Simulate imported data
          const source = DATA_SOURCES[sourceId]
          setImportedData(prev => ({
            ...prev,
            [sourceId]: {
              connected: true,
              dataTypes: source.dataTypes,
              lastSync: new Date().toISOString(),
              recordCount: Math.floor(Math.random() * 1000) + 100
            }
          }))
          
          return 100
        }
        return prev + 10
      })
    }, 200)
  }

  // Disconnect data source
  const disconnectDataSource = (sourceId) => {
    setConnectedSources(prev => prev.filter(id => id !== sourceId))
    setImportedData(prev => {
      const newData = { ...prev }
      delete newData[sourceId]
      return newData
    })
  }

  // Sample questions that can be pre-populated
  const sampleQuestions = [
    {
      id: 'work_experience_years',
      text: 'How many years of work experience do you have?',
      canPrePopulate: ['LINKEDIN', 'RESUME_CV'],
      estimatedTime: 1
    },
    {
      id: 'current_income_range',
      text: 'What is your current income range?',
      canPrePopulate: ['FINANCIAL_DATA'],
      estimatedTime: 2
    },
    {
      id: 'professional_network_size',
      text: 'How large is your professional network?',
      canPrePopulate: ['LINKEDIN', 'SOCIAL_MEDIA'],
      estimatedTime: 2
    },
    {
      id: 'time_availability',
      text: 'How many hours per week can you dedicate to your business?',
      canPrePopulate: ['CALENDAR_DATA'],
      estimatedTime: 3
    },
    {
      id: 'communication_style',
      text: 'How would you describe your communication style?',
      canPrePopulate: ['EMAIL_ANALYSIS', 'SOCIAL_MEDIA'],
      estimatedTime: 2
    }
  ]

  const getQuestionStatus = (question) => {
    const connectedSourcesForQuestion = question.canPrePopulate.filter(source => 
      connectedSources.includes(DATA_SOURCES[source].id)
    )
    
    if (connectedSourcesForQuestion.length > 0) {
      return {
        status: 'pre-populated',
        color: 'text-green-400',
        bgColor: 'bg-green-900/20',
        borderColor: 'border-green-500',
        icon: CheckCircle,
        message: `Pre-populated from ${connectedSourcesForQuestion.length} source(s)`
      }
    }
    
    return {
      status: 'manual',
      color: 'text-orange-400',
      bgColor: 'bg-orange-900/20',
      borderColor: 'border-orange-500',
      icon: Clock,
      message: `Manual input required (${question.estimatedTime} min)`
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Database className="h-5 w-5 text-orange-500" />
            Data-Driven Assessment Optimization
          </CardTitle>
          <CardDescription className="text-gray-400">
            Connect your data sources to automatically pre-populate answers and speed up your assessment
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-blue-400">{connectedSources.length}</div>
              <div className="text-xs text-gray-400">Connected Sources</div>
            </div>
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-green-400">{optimization.timeSavedMinutes || 0}m</div>
              <div className="text-xs text-gray-400">Time Saved</div>
            </div>
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-purple-400">{optimization.prePopulationCoverage || 0}%</div>
              <div className="text-xs text-gray-400">Pre-populated</div>
            </div>
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-orange-400">{optimization.skippableQuestions || 0}</div>
              <div className="text-xs text-gray-400">Questions Skipped</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Import Progress */}
      {showImportDemo && (
        <Card className="bg-blue-900/20 border-blue-500">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3 mb-3">
              <Download className="h-5 w-5 text-blue-400 animate-pulse" />
              <span className="text-white font-medium">Importing data...</span>
            </div>
            <Progress value={importProgress} className="mb-2" />
            <div className="text-sm text-gray-400">
              Analyzing and extracting relevant information for pre-population
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="sources" className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-gray-800">
          <TabsTrigger value="sources" className="text-gray-300">Data Sources</TabsTrigger>
          <TabsTrigger value="questions" className="text-gray-300">Question Impact</TabsTrigger>
          <TabsTrigger value="optimization" className="text-gray-300">Optimization</TabsTrigger>
        </TabsList>

        <TabsContent value="sources" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.values(DATA_SOURCES).map((source) => {
              const IconComponent = SourceIcons[source.icon] || Database
              const isConnected = connectedSources.includes(source.id)
              
              return (
                <Card 
                  key={source.id} 
                  className={`${
                    isConnected 
                      ? 'bg-green-900/20 border-green-500' 
                      : 'bg-gray-900 border-gray-700'
                  } transition-all`}
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="text-white text-sm flex items-center gap-2">
                      <IconComponent className={`h-4 w-4 ${
                        isConnected ? 'text-green-400' : 'text-gray-400'
                      }`} />
                      {source.name}
                      {isConnected && <CheckCircle className="h-4 w-4 text-green-400" />}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-3">
                      <div className="text-xs text-gray-400">
                        <strong>Data Types:</strong> {source.dataTypes.join(', ')}
                      </div>
                      
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-400">Pre-population:</span>
                        <span className="text-green-400">{source.prePopulationPotential}%</span>
                      </div>
                      
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-400">Time saved:</span>
                        <span className="text-blue-400">{source.estimatedTimeSaved}m</span>
                      </div>
                      
                      {isConnected ? (
                        <div className="space-y-2">
                          <div className="text-xs text-green-400">
                            ✓ {importedData[source.id]?.recordCount || 0} records imported
                          </div>
                          <Button
                            onClick={() => disconnectDataSource(source.id)}
                            size="sm"
                            variant="outline"
                            className="w-full border-red-600 text-red-400 hover:bg-red-900/20"
                          >
                            Disconnect
                          </Button>
                        </div>
                      ) : (
                        <Button
                          onClick={() => connectDataSource(source.id)}
                          size="sm"
                          className="w-full bg-orange-600 hover:bg-orange-700 text-white"
                        >
                          <Plus className="h-3 w-3 mr-1" />
                          Connect
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        <TabsContent value="questions" className="space-y-4">
          <div className="space-y-3">
            {sampleQuestions.map((question) => {
              const status = getQuestionStatus(question)
              const StatusIcon = status.icon
              
              return (
                <Card 
                  key={question.id} 
                  className={`${status.bgColor} border ${status.borderColor}`}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="text-white font-medium text-sm mb-1">
                          {question.text}
                        </div>
                        <div className={`text-xs ${status.color} flex items-center gap-1`}>
                          <StatusIcon className="h-3 w-3" />
                          {status.message}
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${status.color} border-current`}
                        >
                          {status.status === 'pre-populated' ? 'Auto-filled' : `${question.estimatedTime}m`}
                        </Badge>
                        
                        {question.canPrePopulate.length > 0 && (
                          <div className="text-xs text-gray-400 mt-1">
                            Sources: {question.canPrePopulate.map(source => 
                              DATA_SOURCES[source].name
                            ).join(', ')}
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        <TabsContent value="optimization" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Current Optimization */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-500" />
                  Current Optimization
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Your current assessment optimization level
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Overall Optimization</span>
                    <Badge variant="secondary" className="bg-green-900 text-green-300">
                      {Math.round(optimization.totalOptimization || 0)}%
                    </Badge>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Time Saved</span>
                      <span className="text-blue-400">{optimization.timeSavedMinutes || 0} minutes</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Pre-populated</span>
                      <span className="text-purple-400">{optimization.prePopulationCoverage || 0}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Questions Skipped</span>
                      <span className="text-orange-400">{optimization.skippableQuestions || 0}</span>
                    </div>
                  </div>
                  
                  <Progress value={optimization.totalOptimization || 0} />
                </div>
              </CardContent>
            </Card>

            {/* Recommended Sources */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Target className="h-5 w-5 text-orange-500" />
                  Recommended Sources
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Connect these sources for maximum optimization
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {adaptiveEngine.getRecommendedDataSources(connectedSources).slice(0, 3).map((source) => {
                    const IconComponent = SourceIcons[source.icon] || Database
                    const impact = source.estimatedTimeSaved + (source.prePopulationPotential * 0.1)
                    
                    return (
                      <div 
                        key={source.id}
                        className="flex items-center justify-between p-3 bg-gray-800 rounded-lg"
                      >
                        <div className="flex items-center gap-2">
                          <IconComponent className="h-4 w-4 text-gray-400" />
                          <div>
                            <div className="text-white text-sm font-medium">{source.name}</div>
                            <div className="text-xs text-gray-400">
                              {source.estimatedTimeSaved}m saved, {source.prePopulationPotential}% coverage
                            </div>
                          </div>
                        </div>
                        <Button
                          onClick={() => connectDataSource(source.id)}
                          size="sm"
                          className="bg-orange-600 hover:bg-orange-700 text-white"
                        >
                          <Plus className="h-3 w-3 mr-1" />
                          Connect
                        </Button>
                      </div>
                    )
                  })}
                  
                  {adaptiveEngine.getRecommendedDataSources(connectedSources).length === 0 && (
                    <div className="text-center text-gray-400 py-4">
                      All available sources connected!
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Optimization Projection */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                Optimization Projection
              </CardTitle>
              <CardDescription className="text-gray-400">
                See how connecting additional sources improves your assessment experience
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Current vs Potential */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-gray-800 rounded-lg">
                    <div className="text-2xl font-bold text-orange-400 mb-1">
                      {60 - (optimization.timeSavedMinutes || 0)}m
                    </div>
                    <div className="text-sm text-gray-400">Current Time</div>
                  </div>
                  <div className="text-center p-4 bg-gray-800 rounded-lg">
                    <div className="text-2xl font-bold text-green-400 mb-1">
                      {Math.max(15, 60 - 43)}m
                    </div>
                    <div className="text-sm text-gray-400">Potential Time (All Sources)</div>
                  </div>
                </div>
                
                {/* Potential Improvements */}
                <div className="p-4 bg-gray-800 rounded-lg">
                  <h4 className="text-white font-medium mb-3">If you connect all sources:</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-green-400">
                      <CheckCircle className="h-3 w-3" />
                      Save up to 43 minutes of manual input
                    </div>
                    <div className="flex items-center gap-2 text-green-400">
                      <CheckCircle className="h-3 w-3" />
                      Pre-populate 85% of assessment questions
                    </div>
                    <div className="flex items-center gap-2 text-green-400">
                      <CheckCircle className="h-3 w-3" />
                      Skip 25+ irrelevant questions automatically
                    </div>
                    <div className="flex items-center gap-2 text-green-400">
                      <CheckCircle className="h-3 w-3" />
                      Complete assessment in 15-20 minutes instead of 60
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Quick Connect All */}
      {connectedSources.length < Object.keys(DATA_SOURCES).length && (
        <div className="text-center">
          <Button
            onClick={() => {
              Object.keys(DATA_SOURCES).forEach(sourceId => {
                if (!connectedSources.includes(sourceId)) {
                  setTimeout(() => connectDataSource(sourceId), Math.random() * 1000)
                }
              })
            }}
            size="lg"
            className="bg-orange-600 hover:bg-orange-700 text-white px-8 py-3"
          >
            <Zap className="h-5 w-5 mr-2" />
            Connect All Sources (Demo)
          </Button>
        </div>
      )}
    </div>
  )
}

