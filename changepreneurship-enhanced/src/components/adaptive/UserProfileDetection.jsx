import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Progress } from '../ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { 
  User, 
  Clock, 
  Target, 
  TrendingUp, 
  CheckCircle, 
  AlertCircle,
  Lightbulb,
  Users,
  Briefcase,
  Rocket,
  Heart,
  Zap
} from 'lucide-react'
import { useEnhancedAssessment } from '../../contexts/EnhancedAssessmentContext'
import { USER_PROFILE_TYPES, ASSESSMENT_PATHS } from '../../contexts/AdaptiveAssessmentEngine'

const ProfileTypeIcons = {
  [USER_PROFILE_TYPES.BEGINNER_ENTREPRENEUR]: User,
  [USER_PROFILE_TYPES.EXPERIENCED_PROFESSIONAL]: Briefcase,
  [USER_PROFILE_TYPES.SERIAL_ENTREPRENEUR]: Rocket,
  [USER_PROFILE_TYPES.INDUSTRY_SPECIALIST]: Target,
  [USER_PROFILE_TYPES.CREATIVE_INNOVATOR]: Lightbulb
}

const ProfileTypeColors = {
  [USER_PROFILE_TYPES.BEGINNER_ENTREPRENEUR]: 'bg-blue-500',
  [USER_PROFILE_TYPES.EXPERIENCED_PROFESSIONAL]: 'bg-green-500',
  [USER_PROFILE_TYPES.SERIAL_ENTREPRENEUR]: 'bg-purple-500',
  [USER_PROFILE_TYPES.INDUSTRY_SPECIALIST]: 'bg-orange-500',
  [USER_PROFILE_TYPES.CREATIVE_INNOVATOR]: 'bg-pink-500'
}

const ProfileTypeNames = {
  [USER_PROFILE_TYPES.BEGINNER_ENTREPRENEUR]: 'Beginner Entrepreneur',
  [USER_PROFILE_TYPES.EXPERIENCED_PROFESSIONAL]: 'Experienced Professional',
  [USER_PROFILE_TYPES.SERIAL_ENTREPRENEUR]: 'Serial Entrepreneur',
  [USER_PROFILE_TYPES.INDUSTRY_SPECIALIST]: 'Industry Specialist',
  [USER_PROFILE_TYPES.CREATIVE_INNOVATOR]: 'Creative Innovator'
}

export default function UserProfileDetection() {
  const {
    userProfile,
    adaptiveState,
    getAllResponses,
    isProfileDetected,
    getUserProfileType,
    getProfileConfidence,
    getCurrentPath,
    processAdaptiveLogic
  } = useEnhancedAssessment()

  const [showDetails, setShowDetails] = useState(false)
  const [detectionProgress, setDetectionProgress] = useState(0)

  const profileType = getUserProfileType()
  const confidence = getProfileConfidence()
  const currentPath = getCurrentPath()
  const allResponses = getAllResponses()
  const responseCount = Object.keys(allResponses).length

  // Calculate detection progress
  useEffect(() => {
    const minResponses = 5
    const optimalResponses = 15
    const progress = Math.min(100, (responseCount / optimalResponses) * 100)
    setDetectionProgress(progress)
  }, [responseCount])

  // Auto-trigger profile detection when enough responses
  useEffect(() => {
    if (responseCount >= 5 && !isProfileDetected()) {
      processAdaptiveLogic('self_discovery')
    }
  }, [responseCount, isProfileDetected, processAdaptiveLogic])

  if (responseCount < 3) {
    return (
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <User className="h-5 w-5 text-orange-500" />
            Profile Detection
          </CardTitle>
          <CardDescription className="text-gray-400">
            Answer a few questions to unlock your personalized assessment path
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-gray-400">
              <AlertCircle className="h-4 w-4" />
              <span>Need {5 - responseCount} more responses to detect your profile</span>
            </div>
            <Progress value={(responseCount / 5) * 100} className="h-2" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!isProfileDetected()) {
    return (
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <User className="h-5 w-5 text-orange-500" />
            Analyzing Your Profile...
          </CardTitle>
          <CardDescription className="text-gray-400">
            Processing your responses to create a personalized experience
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Progress value={detectionProgress} className="h-2" />
            <div className="text-sm text-gray-400">
              Analyzing {responseCount} responses...
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const IconComponent = ProfileTypeIcons[profileType] || User
  const colorClass = ProfileTypeColors[profileType] || 'bg-gray-500'
  const profileName = ProfileTypeNames[profileType] || 'Unknown Profile'

  return (
    <div className="space-y-6">
      {/* Profile Detection Result */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            Profile Detected
          </CardTitle>
          <CardDescription className="text-gray-400">
            Your personalized assessment path has been configured
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Profile Type Display */}
            <div className="flex items-center gap-4 p-4 bg-gray-800 rounded-lg">
              <div className={`p-3 rounded-full ${colorClass}`}>
                <IconComponent className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white">{profileName}</h3>
                <p className="text-gray-400">{currentPath?.description}</p>
              </div>
              <Badge variant="secondary" className="bg-green-900 text-green-300">
                {Math.round(confidence * 100)}% confidence
              </Badge>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <Clock className="h-5 w-5 text-orange-500 mx-auto mb-1" />
                <div className="text-sm font-medium text-white">{currentPath?.estimatedTime}</div>
                <div className="text-xs text-gray-400">Estimated Time</div>
              </div>
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <Target className="h-5 w-5 text-blue-500 mx-auto mb-1" />
                <div className="text-sm font-medium text-white">{currentPath?.questionCount}</div>
                <div className="text-xs text-gray-400">Questions</div>
              </div>
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <TrendingUp className="h-5 w-5 text-green-500 mx-auto mb-1" />
                <div className="text-sm font-medium text-white">
                  {Math.round(((500 - currentPath?.questionCount) / 500) * 100)}%
                </div>
                <div className="text-xs text-gray-400">Time Saved</div>
              </div>
              <div className="text-center p-3 bg-gray-800 rounded-lg">
                <Zap className="h-5 w-5 text-purple-500 mx-auto mb-1" />
                <div className="text-sm font-medium text-white">Smart</div>
                <div className="text-xs text-gray-400">Adaptive</div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <Button 
                onClick={() => setShowDetails(!showDetails)}
                variant="outline"
                className="border-gray-600 text-gray-300 hover:bg-gray-800"
              >
                {showDetails ? 'Hide Details' : 'View Details'}
              </Button>
              <Button className="bg-orange-600 hover:bg-orange-700 text-white">
                Continue Assessment
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Profile Information */}
      {showDetails && (
        <Card className="bg-gray-900 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Your Personalized Assessment Path</CardTitle>
            <CardDescription className="text-gray-400">
              Detailed breakdown of your adaptive assessment experience
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-4 bg-gray-800">
                <TabsTrigger value="overview" className="text-gray-300">Overview</TabsTrigger>
                <TabsTrigger value="features" className="text-gray-300">Features</TabsTrigger>
                <TabsTrigger value="focus" className="text-gray-300">Focus Areas</TabsTrigger>
                <TabsTrigger value="optimization" className="text-gray-300">Optimization</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <div className="space-y-4">
                  <div>
                    <h4 className="text-white font-medium mb-2">Assessment Path: {currentPath?.name}</h4>
                    <p className="text-gray-400">{currentPath?.description}</p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-800 rounded-lg">
                      <h5 className="text-white font-medium mb-2">Time Commitment</h5>
                      <p className="text-gray-400">{currentPath?.estimatedTime}</p>
                    </div>
                    <div className="p-4 bg-gray-800 rounded-lg">
                      <h5 className="text-white font-medium mb-2">Question Count</h5>
                      <p className="text-gray-400">{currentPath?.questionCount} questions</p>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="features" className="space-y-4">
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {currentPath?.skipQuestions && (
                      <div className="p-4 bg-gray-800 rounded-lg">
                        <h5 className="text-white font-medium mb-2 flex items-center gap-2">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          Questions Skipped
                        </h5>
                        <p className="text-gray-400 text-sm">
                          {currentPath.skipQuestions.length} irrelevant questions automatically skipped
                        </p>
                      </div>
                    )}
                    
                    {currentPath?.prePopulate && (
                      <div className="p-4 bg-gray-800 rounded-lg">
                        <h5 className="text-white font-medium mb-2 flex items-center gap-2">
                          <Zap className="h-4 w-4 text-purple-500" />
                          Pre-populated Answers
                        </h5>
                        <p className="text-gray-400 text-sm">
                          {currentPath.prePopulate.length} answers automatically filled based on your profile
                        </p>
                      </div>
                    )}
                    
                    <div className="p-4 bg-gray-800 rounded-lg">
                      <h5 className="text-white font-medium mb-2 flex items-center gap-2">
                        <Target className="h-4 w-4 text-blue-500" />
                        Explanation Level
                      </h5>
                      <p className="text-gray-400 text-sm capitalize">
                        {currentPath?.explanationLevel} explanations and guidance
                      </p>
                    </div>
                    
                    <div className="p-4 bg-gray-800 rounded-lg">
                      <h5 className="text-white font-medium mb-2 flex items-center gap-2">
                        <Heart className="h-4 w-4 text-red-500" />
                        Educational Content
                      </h5>
                      <p className="text-gray-400 text-sm">
                        {currentPath?.educationalContent ? 'Included' : 'Streamlined'} educational materials
                      </p>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="focus" className="space-y-4">
                <div className="space-y-4">
                  {currentPath?.focusAreas && (
                    <div>
                      <h4 className="text-white font-medium mb-3">Primary Focus Areas</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {currentPath.focusAreas.map((area, index) => (
                          <div key={index} className="flex items-center gap-2 p-3 bg-gray-800 rounded-lg">
                            <Target className="h-4 w-4 text-orange-500" />
                            <span className="text-gray-300 capitalize">{area.replace('_', ' ')}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {currentPath?.addQuestions && (
                    <div>
                      <h4 className="text-white font-medium mb-3">Additional Questions</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {currentPath.addQuestions.map((question, index) => (
                          <div key={index} className="flex items-center gap-2 p-3 bg-gray-800 rounded-lg">
                            <Lightbulb className="h-4 w-4 text-yellow-500" />
                            <span className="text-gray-300 capitalize">{question.replace('_', ' ')}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="optimization" className="space-y-4">
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-gray-800 rounded-lg">
                      <div className="text-2xl font-bold text-green-400">
                        {Math.round(((500 - currentPath?.questionCount) / 500) * 100)}%
                      </div>
                      <div className="text-sm text-gray-400">Time Reduction</div>
                    </div>
                    <div className="text-center p-4 bg-gray-800 rounded-lg">
                      <div className="text-2xl font-bold text-blue-400">
                        {500 - currentPath?.questionCount}
                      </div>
                      <div className="text-sm text-gray-400">Questions Saved</div>
                    </div>
                    <div className="text-center p-4 bg-gray-800 rounded-lg">
                      <div className="text-2xl font-bold text-purple-400">
                        {Math.round(confidence * 100)}%
                      </div>
                      <div className="text-sm text-gray-400">Accuracy</div>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-gray-800 rounded-lg">
                    <h5 className="text-white font-medium mb-2">Optimization Benefits</h5>
                    <ul className="space-y-2 text-gray-400 text-sm">
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        Personalized question selection based on your background
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        Intelligent skipping of irrelevant questions
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        Pre-populated answers from profile analysis
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        Adaptive explanations matching your experience level
                      </li>
                    </ul>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

