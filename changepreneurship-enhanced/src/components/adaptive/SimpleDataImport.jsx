import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Progress } from '../ui/progress'
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
  TrendingUp,
  Target,
  Download
} from 'lucide-react'

// Simple data sources configuration
const DATA_SOURCES = {
  linkedin: {
    name: 'LinkedIn Profile',
    icon: Linkedin,
    timeSaved: 15,
    coverage: 85,
    dataTypes: ['work_experience', 'education', 'skills', 'connections']
  },
  financial: {
    name: 'Financial Information',
    icon: DollarSign,
    timeSaved: 10,
    coverage: 60,
    dataTypes: ['income', 'expenses', 'savings', 'investments']
  },
  resume: {
    name: 'Resume/CV Upload',
    icon: FileText,
    timeSaved: 12,
    coverage: 70,
    dataTypes: ['work_history', 'achievements', 'skills']
  },
  social: {
    name: 'Social Media Profiles',
    icon: Share,
    timeSaved: 8,
    coverage: 40,
    dataTypes: ['interests', 'communication_style', 'network']
  },
  email: {
    name: 'Email Communication',
    icon: Mail,
    timeSaved: 6,
    coverage: 30,
    dataTypes: ['communication_patterns', 'business_contacts']
  },
  calendar: {
    name: 'Calendar & Schedule',
    icon: Calendar,
    timeSaved: 4,
    coverage: 25,
    dataTypes: ['time_management', 'availability']
  }
}

export default function SimpleDataImport() {
  const [connectedSources, setConnectedSources] = useState([])
  const [importProgress, setImportProgress] = useState({})
  const [importedData, setImportedData] = useState({})

  // Calculate total optimization
  const totalTimeSaved = connectedSources.reduce((total, sourceId) => {
    return total + (DATA_SOURCES[sourceId]?.timeSaved || 0)
  }, 0)

  const averageCoverage = connectedSources.length > 0 
    ? Math.round(connectedSources.reduce((total, sourceId) => {
        return total + (DATA_SOURCES[sourceId]?.coverage || 0)
      }, 0) / connectedSources.length)
    : 0

  // Connect data source with animation
  const connectDataSource = (sourceId) => {
    if (connectedSources.includes(sourceId)) return
    
    // Start import animation
    setImportProgress(prev => ({ ...prev, [sourceId]: 0 }))
    
    const interval = setInterval(() => {
      setImportProgress(prev => {
        const current = prev[sourceId] || 0
        if (current >= 100) {
          clearInterval(interval)
          
          // Mark as connected
          setConnectedSources(prevSources => [...prevSources, sourceId])
          setImportedData(prev => ({
            ...prev,
            [sourceId]: {
              connected: true,
              recordCount: Math.floor(Math.random() * 500) + 100,
              lastSync: new Date().toISOString()
            }
          }))
          
          return { ...prev, [sourceId]: 100 }
        }
        return { ...prev, [sourceId]: current + 20 }
      })
    }, 300)
  }

  // Disconnect data source
  const disconnectDataSource = (sourceId) => {
    setConnectedSources(prev => prev.filter(id => id !== sourceId))
    setImportedData(prev => {
      const newData = { ...prev }
      delete newData[sourceId]
      return newData
    })
    setImportProgress(prev => {
      const newProgress = { ...prev }
      delete newProgress[sourceId]
      return newProgress
    })
  }

  return (
    <div className="space-y-6">
      {/* Optimization Summary */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Database className="h-5 w-5 text-orange-500" />
            Data Import Optimization
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
              <div className="text-2xl font-bold text-green-400">{totalTimeSaved}m</div>
              <div className="text-xs text-gray-400">Time Saved</div>
            </div>
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-purple-400">{averageCoverage}%</div>
              <div className="text-xs text-gray-400">Pre-populated</div>
            </div>
            <div className="text-center p-3 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-orange-400">{Math.max(15, 60 - totalTimeSaved)}m</div>
              <div className="text-xs text-gray-400">Final Time</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Sources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(DATA_SOURCES).map(([sourceId, source]) => {
          const IconComponent = source.icon
          const isConnected = connectedSources.includes(sourceId)
          const isImporting = importProgress[sourceId] !== undefined && importProgress[sourceId] < 100
          const progress = importProgress[sourceId] || 0
          
          return (
            <Card 
              key={sourceId} 
              className={`${
                isConnected 
                  ? 'bg-green-900/20 border-green-500' 
                  : isImporting
                  ? 'bg-blue-900/20 border-blue-500'
                  : 'bg-gray-900 border-gray-700'
              } transition-all`}
            >
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-sm flex items-center gap-2">
                  <IconComponent className={`h-4 w-4 ${
                    isConnected ? 'text-green-400' : 
                    isImporting ? 'text-blue-400' : 'text-gray-400'
                  }`} />
                  {source.name}
                  {isConnected && <CheckCircle className="h-4 w-4 text-green-400" />}
                  {isImporting && <Download className="h-4 w-4 text-blue-400 animate-pulse" />}
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  <div className="text-xs text-gray-400">
                    <strong>Data:</strong> {source.dataTypes.join(', ')}
                  </div>
                  
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Coverage:</span>
                    <span className="text-purple-400">{source.coverage}%</span>
                  </div>
                  
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Time saved:</span>
                    <span className="text-green-400">{source.timeSaved}m</span>
                  </div>
                  
                  {isImporting && (
                    <div className="space-y-2">
                      <Progress value={progress} className="h-2" />
                      <div className="text-xs text-blue-400 text-center">
                        Importing data... {progress}%
                      </div>
                    </div>
                  )}
                  
                  {isConnected ? (
                    <div className="space-y-2">
                      <div className="text-xs text-green-400">
                        ✓ {importedData[sourceId]?.recordCount || 0} records imported
                      </div>
                      <Button
                        onClick={() => disconnectDataSource(sourceId)}
                        size="sm"
                        variant="outline"
                        className="w-full border-red-600 text-red-400 hover:bg-red-900/20"
                      >
                        Disconnect
                      </Button>
                    </div>
                  ) : !isImporting ? (
                    <Button
                      onClick={() => connectDataSource(sourceId)}
                      size="sm"
                      className="w-full bg-orange-600 hover:bg-orange-700 text-white"
                    >
                      <Plus className="h-3 w-3 mr-1" />
                      Connect
                    </Button>
                  ) : null}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Optimization Results */}
      {connectedSources.length > 0 && (
        <Card className="bg-green-900/20 border-green-500">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-400" />
              Current Optimization Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <div className="text-xl font-bold text-green-400">{totalTimeSaved}m</div>
                <div className="text-xs text-gray-400">Time Saved</div>
              </div>
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <div className="text-xl font-bold text-purple-400">{averageCoverage}%</div>
                <div className="text-xs text-gray-400">Pre-populated</div>
              </div>
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <div className="text-xl font-bold text-blue-400">{Math.max(15, 60 - totalTimeSaved)}m</div>
                <div className="text-xs text-gray-400">Remaining Time</div>
              </div>
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <div className="text-xl font-bold text-orange-400">{Math.round((totalTimeSaved / 45) * 100)}%</div>
                <div className="text-xs text-gray-400">Optimization</div>
              </div>
            </div>
            
            <div className="text-center">
              <div className="text-green-400 font-medium">
                Assessment time reduced from 60 minutes to {Math.max(15, 60 - totalTimeSaved)} minutes
              </div>
              <div className="text-gray-400 text-sm mt-1">
                {Math.round((totalTimeSaved / 45) * 100)}% optimization achieved
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Connect All Demo */}
      {connectedSources.length < Object.keys(DATA_SOURCES).length && (
        <div className="text-center">
          <Button
            onClick={() => {
              Object.keys(DATA_SOURCES).forEach((sourceId, index) => {
                if (!connectedSources.includes(sourceId)) {
                  setTimeout(() => connectDataSource(sourceId), index * 500)
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

