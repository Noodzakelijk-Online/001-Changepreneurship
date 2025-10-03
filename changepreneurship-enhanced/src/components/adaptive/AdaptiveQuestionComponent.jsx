import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Textarea } from '../ui/textarea'
import { Label } from '../ui/label'
import { Slider } from '../ui/slider'
import { 
  CheckCircle, 
  Zap, 
  SkipForward, 
  Lightbulb, 
  AlertCircle,
  Clock,
  Target,
  ArrowRight,
  Info,
  Sparkles
} from 'lucide-react'
import { useEnhancedAssessment } from '../../contexts/EnhancedAssessmentContext'

// Question types for adaptive processing
const QUESTION_TYPES = {
  MULTIPLE_CHOICE: 'multiple_choice',
  SCALE: 'scale',
  TEXT: 'text',
  TEXTAREA: 'textarea',
  CONSOLIDATED: 'consolidated',
  PRE_POPULATED: 'pre_populated'
}

// Sample consolidated questions that replace multiple similar questions
const CONSOLIDATED_QUESTIONS = {
  risk_tolerance_consolidated: {
    id: 'risk_tolerance_consolidated',
    type: QUESTION_TYPES.CONSOLIDATED,
    title: 'Risk Tolerance Assessment',
    description: 'This consolidated question replaces 8 individual risk-related questions',
    originalQuestions: [
      'financial_risk_comfort',
      'career_risk_tolerance',
      'investment_risk_preference',
      'failure_acceptance',
      'uncertainty_comfort',
      'decision_making_style',
      'safety_net_importance',
      'risk_reward_balance'
    ],
    consolidatedQuestion: {
      text: 'How would you describe your overall approach to risk in entrepreneurship?',
      options: [
        {
          value: 'high_risk_high_reward',
          label: 'High Risk, High Reward',
          description: 'I\'m comfortable with significant risks for potentially large returns',
          implications: ['Suitable for disruptive innovation', 'Consider venture capital funding', 'Focus on scalable business models']
        },
        {
          value: 'calculated_risk_taker',
          label: 'Calculated Risk Taker',
          description: 'I take well-researched risks with backup plans',
          implications: ['Good for validated business concepts', 'Consider bootstrapping or angel investment', 'Focus on market-tested opportunities']
        },
        {
          value: 'moderate_risk_comfort',
          label: 'Moderate Risk Comfort',
          description: 'I prefer balanced approaches with manageable risks',
          implications: ['Suitable for established markets', 'Consider franchise opportunities', 'Focus on proven business models']
        },
        {
          value: 'risk_averse',
          label: 'Risk Averse',
          description: 'I prefer stable, predictable opportunities with minimal risk',
          implications: ['Consider service-based businesses', 'Focus on local markets', 'Maintain employment while building']
        }
      ]
    },
    timeSaved: '12 minutes',
    accuracyImprovement: '25%'
  },

  motivation_consolidated: {
    id: 'motivation_consolidated',
    type: QUESTION_TYPES.CONSOLIDATED,
    title: 'Entrepreneurial Motivation Assessment',
    description: 'This consolidated question replaces 6 motivation-related questions',
    originalQuestions: [
      'primary_motivation',
      'success_definition',
      'driving_factors',
      'personal_goals',
      'achievement_orientation',
      'purpose_alignment'
    ],
    consolidatedQuestion: {
      text: 'What is your primary motivation for becoming an entrepreneur?',
      options: [
        {
          value: 'financial_independence',
          label: 'Financial Independence',
          description: 'Building wealth and achieving financial freedom',
          followUpQuestions: ['income_goals', 'timeline_expectations', 'investment_strategy']
        },
        {
          value: 'creative_expression',
          label: 'Creative Expression',
          description: 'Bringing innovative ideas to life and creating something new',
          followUpQuestions: ['innovation_areas', 'creative_process', 'intellectual_property']
        },
        {
          value: 'social_impact',
          label: 'Social Impact',
          description: 'Making a positive difference in the world or community',
          followUpQuestions: ['impact_areas', 'stakeholder_focus', 'measurement_metrics']
        },
        {
          value: 'lifestyle_freedom',
          label: 'Lifestyle Freedom',
          description: 'Having control over my time and work-life balance',
          followUpQuestions: ['work_preferences', 'location_flexibility', 'time_management']
        },
        {
          value: 'professional_growth',
          label: 'Professional Growth',
          description: 'Developing skills and advancing my career',
          followUpQuestions: ['skill_development', 'leadership_goals', 'industry_expertise']
        }
      ]
    },
    timeSaved: '10 minutes',
    accuracyImprovement: '30%'
  }
}

// Pre-population examples based on user profile
const PRE_POPULATION_EXAMPLES = {
  industry_experience: {
    source: 'work_history',
    logic: 'Extracted from 10+ years in technology sector',
    confidence: 0.9,
    value: 'Technology/Software',
    explanation: 'Based on your work history in software development and tech leadership roles'
  },
  financial_runway: {
    source: 'financial_data',
    logic: 'Calculated from savings and monthly expenses',
    confidence: 0.85,
    value: '18 months',
    explanation: 'Based on your current savings of $45,000 and monthly expenses of $2,500'
  },
  team_building_readiness: {
    source: 'leadership_background',
    logic: 'Determined from management experience',
    confidence: 0.8,
    value: 'Experienced',
    explanation: 'Based on your 5+ years managing teams of 10+ people'
  }
}

export default function AdaptiveQuestionComponent({ 
  question, 
  phase, 
  onAnswer, 
  currentAnswer,
  showAdaptiveFeatures = true 
}) {
  const {
    adaptiveEngine,
    getAllResponses,
    getUserProfileType,
    getCurrentPath
  } = useEnhancedAssessment()

  const [localAnswer, setLocalAnswer] = useState(currentAnswer || '')
  const [showExplanation, setShowExplanation] = useState(false)
  const [isPrePopulated, setIsPrePopulated] = useState(false)
  const [prePopulationData, setPrePopulationData] = useState(null)
  const [isConsolidated, setIsConsolidated] = useState(false)
  const [timeSaved, setTimeSaved] = useState(0)

  const allResponses = getAllResponses()
  const userProfile = getUserProfileType()
  const currentPath = getCurrentPath()

  // Check if question should be pre-populated
  useEffect(() => {
    if (showAdaptiveFeatures && question?.id) {
      // Check for pre-population
      const prePopulated = adaptiveEngine.prePopulationEngine.applyPrePopulation(allResponses, question.id)
      if (prePopulated) {
        setIsPrePopulated(true)
        setPrePopulationData(prePopulated)
        setLocalAnswer(prePopulated.value)
      }

      // Check if this is a consolidated question
      if (CONSOLIDATED_QUESTIONS[question.id]) {
        setIsConsolidated(true)
        const consolidatedData = CONSOLIDATED_QUESTIONS[question.id]
        setTimeSaved(parseInt(consolidatedData.timeSaved) || 0)
      }
    }
  }, [question, allResponses, adaptiveEngine, showAdaptiveFeatures])

  // Handle answer changes
  const handleAnswerChange = (value) => {
    setLocalAnswer(value)
    if (onAnswer) {
      onAnswer(question.id, value)
    }
  }

  // Render consolidated question
  const renderConsolidatedQuestion = () => {
    const consolidatedData = CONSOLIDATED_QUESTIONS[question.id]
    if (!consolidatedData) return null

    return (
      <div className="space-y-6">
        {/* Consolidation Info */}
        <div className="p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="h-4 w-4 text-blue-400" />
            <span className="text-blue-400 font-medium">Smart Consolidation</span>
            <Badge variant="secondary" className="bg-blue-900 text-blue-300">
              {consolidatedData.timeSaved} saved
            </Badge>
          </div>
          <p className="text-sm text-blue-300 mb-2">{consolidatedData.description}</p>
          <div className="text-xs text-blue-400">
            Replaces: {consolidatedData.originalQuestions.slice(0, 3).join(', ')}
            {consolidatedData.originalQuestions.length > 3 && ` +${consolidatedData.originalQuestions.length - 3} more`}
          </div>
        </div>

        {/* Consolidated Question */}
        <div className="space-y-4">
          <Label className="text-white text-lg">{consolidatedData.consolidatedQuestion.text}</Label>
          <div className="space-y-3">
            {consolidatedData.consolidatedQuestion.options.map((option) => (
              <div
                key={option.value}
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  localAnswer === option.value
                    ? 'border-orange-500 bg-orange-900/20'
                    : 'border-gray-600 bg-gray-800 hover:bg-gray-700'
                }`}
                onClick={() => handleAnswerChange(option.value)}
              >
                <div className="flex items-start gap-3">
                  <div className={`w-4 h-4 rounded-full border-2 mt-1 ${
                    localAnswer === option.value
                      ? 'border-orange-500 bg-orange-500'
                      : 'border-gray-400'
                  }`} />
                  <div className="flex-1">
                    <div className="text-white font-medium">{option.label}</div>
                    <div className="text-gray-400 text-sm mt-1">{option.description}</div>
                    {option.implications && localAnswer === option.value && (
                      <div className="mt-3 p-3 bg-gray-700 rounded-lg">
                        <div className="text-sm text-gray-300 font-medium mb-2">Implications for your business:</div>
                        <ul className="space-y-1">
                          {option.implications.map((implication, index) => (
                            <li key={index} className="text-xs text-gray-400 flex items-center gap-2">
                              <ArrowRight className="h-3 w-3 text-orange-500" />
                              {implication}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Render pre-populated question
  const renderPrePopulatedQuestion = () => {
    if (!prePopulationData) return null

    return (
      <div className="space-y-4">
        {/* Pre-population Info */}
        <div className="p-4 bg-purple-900/20 border border-purple-500/30 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="h-4 w-4 text-purple-400" />
            <span className="text-purple-400 font-medium">Auto-Populated Answer</span>
            <Badge variant="secondary" className="bg-purple-900 text-purple-300">
              {Math.round(prePopulationData.confidence * 100)}% confidence
            </Badge>
          </div>
          <p className="text-sm text-purple-300 mb-2">
            {prePopulationData.explanation || 'Answer automatically filled based on your previous responses'}
          </p>
          <div className="text-xs text-purple-400">
            Sources: {prePopulationData.sources?.join(', ') || 'Profile analysis'}
          </div>
        </div>

        {/* Pre-populated Answer Display */}
        <div className="space-y-3">
          <Label className="text-white">{question.text}</Label>
          <div className="p-4 bg-gray-800 border border-gray-600 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-white font-medium">Pre-filled Answer:</span>
            </div>
            <div className="text-gray-300">{prePopulationData.value}</div>
          </div>
          
          {/* Option to modify */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="border-gray-600 text-gray-300 hover:bg-gray-800"
              onClick={() => setIsPrePopulated(false)}
            >
              Modify Answer
            </Button>
            <Button
              size="sm"
              className="bg-green-600 hover:bg-green-700 text-white"
              onClick={() => handleAnswerChange(prePopulationData.value)}
            >
              Accept & Continue
            </Button>
          </div>
        </div>
      </div>
    )
  }

  // Render standard question
  const renderStandardQuestion = () => {
    return (
      <div className="space-y-4">
        <Label className="text-white">{question.text}</Label>
        
        {question.type === QUESTION_TYPES.MULTIPLE_CHOICE && (
          <div className="space-y-2">
            {question.options?.map((option) => (
              <div
                key={option.value}
                className={`p-3 border rounded-lg cursor-pointer transition-all ${
                  localAnswer === option.value
                    ? 'border-orange-500 bg-orange-900/20'
                    : 'border-gray-600 bg-gray-800 hover:bg-gray-700'
                }`}
                onClick={() => handleAnswerChange(option.value)}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-4 h-4 rounded-full border-2 ${
                    localAnswer === option.value
                      ? 'border-orange-500 bg-orange-500'
                      : 'border-gray-400'
                  }`} />
                  <span className="text-white">{option.label}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {question.type === QUESTION_TYPES.SCALE && (
          <div className="space-y-3">
            <Slider
              value={[parseInt(localAnswer) || 5]}
              onValueChange={(value) => handleAnswerChange(value[0].toString())}
              max={10}
              min={1}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-400">
              <span>{question.scaleLabels?.min || 'Low'}</span>
              <span className="text-white font-medium">{localAnswer || 5}</span>
              <span>{question.scaleLabels?.max || 'High'}</span>
            </div>
          </div>
        )}

        {question.type === QUESTION_TYPES.TEXT && (
          <Input
            value={localAnswer}
            onChange={(e) => handleAnswerChange(e.target.value)}
            placeholder={question.placeholder}
            className="bg-gray-800 border-gray-600 text-white"
          />
        )}

        {question.type === QUESTION_TYPES.TEXTAREA && (
          <Textarea
            value={localAnswer}
            onChange={(e) => handleAnswerChange(e.target.value)}
            placeholder={question.placeholder}
            rows={4}
            className="bg-gray-800 border-gray-600 text-white"
          />
        )}
      </div>
    )
  }

  if (!question) return null

  return (
    <Card className="bg-gray-900 border-gray-700">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-white flex items-center gap-2">
              {isConsolidated && <Sparkles className="h-5 w-5 text-blue-400" />}
              {isPrePopulated && <Zap className="h-5 w-5 text-purple-400" />}
              {!isConsolidated && !isPrePopulated && <Target className="h-5 w-5 text-orange-500" />}
              {question.title || `Question ${question.id}`}
            </CardTitle>
            {question.description && (
              <CardDescription className="text-gray-400 mt-1">
                {question.description}
              </CardDescription>
            )}
          </div>
          
          {/* Adaptive Features Badges */}
          <div className="flex gap-2">
            {isConsolidated && (
              <Badge variant="secondary" className="bg-blue-900 text-blue-300">
                <Clock className="h-3 w-3 mr-1" />
                {timeSaved}m saved
              </Badge>
            )}
            {isPrePopulated && (
              <Badge variant="secondary" className="bg-purple-900 text-purple-300">
                <Zap className="h-3 w-3 mr-1" />
                Auto-filled
              </Badge>
            )}
            {showAdaptiveFeatures && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowExplanation(!showExplanation)}
                className="text-gray-400 hover:text-white"
              >
                <Info className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-6">
          {/* Adaptive Explanation */}
          {showExplanation && showAdaptiveFeatures && (
            <div className="p-4 bg-gray-800 border border-gray-600 rounded-lg">
              <h4 className="text-white font-medium mb-2 flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-yellow-500" />
                Adaptive Intelligence
              </h4>
              <div className="space-y-2 text-sm text-gray-400">
                {isConsolidated && (
                  <div>• This question consolidates multiple related questions for efficiency</div>
                )}
                {isPrePopulated && (
                  <div>• Answer pre-filled based on your profile and previous responses</div>
                )}
                <div>• Customized for {userProfile?.replace('_', ' ') || 'your profile'}</div>
                <div>• Part of {currentPath?.name || 'your personalized path'}</div>
              </div>
            </div>
          )}

          {/* Question Content */}
          {isConsolidated ? renderConsolidatedQuestion() : 
           isPrePopulated ? renderPrePopulatedQuestion() : 
           renderStandardQuestion()}

          {/* Question Help */}
          {question.help && (
            <div className="p-3 bg-gray-800 border border-gray-600 rounded-lg">
              <div className="flex items-start gap-2">
                <Info className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-gray-400">{question.help}</div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

