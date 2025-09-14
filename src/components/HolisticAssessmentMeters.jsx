import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Progress } from '@/components/ui/progress.jsx';
import { 
  Heart, 
  Brain, 
  Zap, 
  Star,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';

const HolisticAssessmentMeters = ({ assessmentData = null }) => {
  // Default assessment data for demonstration
  const defaultData = {
    heart: {
      score: 75,
      totalQuestions: 25,
      answeredQuestions: 19,
      avgResponseLength: 180,
      depthScore: 82,
      passionIndicators: ['entrepreneurship', 'innovation', 'impact'],
      recentActivity: 'Strong passion responses in vision and motivation sections'
    },
    body: {
      score: 45,
      totalQuestions: 30,
      answeredQuestions: 12,
      avgResponseLength: 95,
      depthScore: 38,
      practicalAreas: ['financial planning', 'market research'],
      recentActivity: 'Needs more depth in execution and practical planning'
    },
    mind: {
      score: 88,
      totalQuestions: 35,
      answeredQuestions: 31,
      avgResponseLength: 220,
      depthScore: 91,
      strategicAreas: ['market analysis', 'competitive strategy', 'business model'],
      recentActivity: 'Excellent strategic thinking and analytical responses'
    },
    soul: {
      score: 62,
      totalQuestions: 20,
      answeredQuestions: 14,
      avgResponseLength: 160,
      depthScore: 68,
      purposeAreas: ['social impact', 'personal values'],
      recentActivity: 'Good purpose clarity, could explore deeper meaning'
    }
  };

  const data = assessmentData || defaultData;

  const meters = [
    {
      key: 'heart',
      title: 'Heart',
      subtitle: 'Passion & Emotion',
      icon: Heart,
      color: 'from-red-500 to-pink-500',
      bgColor: 'bg-red-50',
      textColor: 'text-red-600',
      description: 'Your emotional connection and passion for entrepreneurship',
      factors: [
        'Passion for your vision',
        'Emotional resilience',
        'Motivation and drive',
        'Personal connection to the problem'
      ]
    },
    {
      key: 'body',
      title: 'Body',
      subtitle: 'Material & Execution',
      icon: Zap,
      color: 'from-orange-500 to-yellow-500',
      bgColor: 'bg-orange-50',
      textColor: 'text-orange-600',
      description: 'Your practical execution and material understanding',
      factors: [
        'Financial planning and needs',
        'Resource requirements',
        'Execution capabilities',
        'Market realities and constraints'
      ]
    },
    {
      key: 'mind',
      title: 'Mind',
      subtitle: 'Strategy & Intelligence',
      icon: Brain,
      color: 'from-blue-500 to-indigo-500',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600',
      description: 'Your strategic thinking and intellectual preparation',
      factors: [
        'Strategic planning',
        'Market analysis',
        'Competitive intelligence',
        'Business model design'
      ]
    },
    {
      key: 'soul',
      title: 'Soul',
      subtitle: 'Purpose & Meaning',
      icon: Star,
      color: 'from-purple-500 to-violet-500',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-600',
      description: 'Your deeper purpose and spiritual connection to your mission',
      factors: [
        'Life purpose alignment',
        'Values and ethics',
        'Social impact vision',
        'Legacy and meaning'
      ]
    }
  ];

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score) => {
    if (score >= 90) return 'Exceptional';
    if (score >= 80) return 'Strong';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Developing';
    if (score >= 40) return 'Emerging';
    return 'Needs Focus';
  };

  const getCompletionRate = (answered, total) => {
    return Math.round((answered / total) * 100);
  };

  const getOverallReadiness = () => {
    const scores = [data.heart.score, data.body.score, data.mind.score, data.soul.score];
    const average = scores.reduce((a, b) => a + b, 0) / scores.length;
    return Math.round(average);
  };

  const getReadinessMessage = (score) => {
    if (score >= 80) return "You're well-prepared for your entrepreneurial journey!";
    if (score >= 70) return "You're on a strong path. Focus on the areas that need attention.";
    if (score >= 60) return "Good foundation. Continue building in all areas.";
    if (score >= 50) return "Solid start. Invest more time in self-discovery.";
    return "Take time to deeply explore each dimension before proceeding.";
  };

  return (
    <div className="space-y-6">
      {/* Overall Readiness */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            Entrepreneurial Readiness
          </CardTitle>
          <CardDescription>
            Your holistic preparation across all dimensions of entrepreneurship
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center mb-4">
            <div className="text-4xl font-bold text-primary mb-2">{getOverallReadiness()}%</div>
            <div className="text-sm text-muted-foreground mb-2">Overall Readiness Score</div>
            <Badge variant="outline" className={getScoreColor(getOverallReadiness())}>
              {getScoreLabel(getOverallReadiness())}
            </Badge>
          </div>
          <p className="text-sm text-center text-muted-foreground">
            {getReadinessMessage(getOverallReadiness())}
          </p>
        </CardContent>
      </Card>

      {/* The Four Meters */}
      <div className="grid md:grid-cols-2 gap-6">
        {meters.map((meter) => {
          const meterData = data[meter.key];
          const Icon = meter.icon;
          const completionRate = getCompletionRate(meterData.answeredQuestions, meterData.totalQuestions);
          
          return (
            <Card key={meter.key} className="relative overflow-hidden">
              <CardHeader className={`${meter.bgColor} relative`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-full ${meter.bgColor} flex items-center justify-center border-2 border-white shadow-sm`}>
                      <Icon className={`h-6 w-6 ${meter.textColor}`} />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{meter.title}</CardTitle>
                      <CardDescription className="text-sm">{meter.subtitle}</CardDescription>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-2xl font-bold ${getScoreColor(meterData.score)}`}>
                      {meterData.score}%
                    </div>
                    <Badge variant="outline" className={getScoreColor(meterData.score)}>
                      {getScoreLabel(meterData.score)}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="pt-6">
                {/* Progress Visualization */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-muted-foreground mb-2">
                    <span>Completion</span>
                    <span>{meterData.score}%</span>
                  </div>
                  <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full bg-gradient-to-r ${meter.color} transition-all duration-1000 ease-out`}
                      style={{ width: `${meterData.score}%` }}
                    />
                  </div>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                  <div>
                    <div className="text-muted-foreground">Questions</div>
                    <div className="font-medium">
                      {meterData.answeredQuestions}/{meterData.totalQuestions}
                      <span className="text-xs text-muted-foreground ml-1">
                        ({completionRate}%)
                      </span>
                    </div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Depth Score</div>
                    <div className={`font-medium ${getScoreColor(meterData.depthScore)}`}>
                      {meterData.depthScore}%
                    </div>
                  </div>
                </div>

                {/* Recent Activity */}
                <div className="mb-4">
                  <div className="text-sm text-muted-foreground mb-1">Recent Activity</div>
                  <p className="text-xs text-gray-600 italic">
                    {meterData.recentActivity}
                  </p>
                </div>

                {/* Key Areas */}
                <div>
                  <div className="text-sm text-muted-foreground mb-2">Key Focus Areas</div>
                  <div className="space-y-1">
                    {meter.factors.map((factor, index) => (
                      <div key={index} className="flex items-center gap-2 text-xs">
                        <div className={`w-2 h-2 rounded-full ${
                          index < Math.floor(meterData.score / 25) ? 
                          `bg-gradient-to-r ${meter.color}` : 
                          'bg-gray-300'
                        }`} />
                        <span className="text-gray-600">{factor}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Action Needed */}
                {meterData.score < 70 && (
                  <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                    <div className="flex items-center gap-2 text-yellow-800">
                      <AlertCircle className="h-4 w-4" />
                      <span className="text-sm font-medium">Action Needed</span>
                    </div>
                    <p className="text-xs text-yellow-700 mt-1">
                      Continue answering questions in this area to build a stronger foundation.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Guidance Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5 text-primary" />
            How to Improve Your Scores
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <div>
              <h4 className="font-medium mb-2">Quality Factors</h4>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Answer more questions thoroughly</li>
                <li>• Provide detailed, thoughtful responses</li>
                <li>• Be honest and realistic in your answers</li>
                <li>• Include specific examples and evidence</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Depth Indicators</h4>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Response length and detail</li>
                <li>• Real-world data and research</li>
                <li>• Personal reflection and insight</li>
                <li>• Practical implementation plans</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default HolisticAssessmentMeters;

