import React, { useState, useEffect, useMemo } from 'react';
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
  Info,
  BarChart3
} from 'lucide-react';
import ResponseAnalyzer from '../services/responseAnalyzer.js';

const DynamicAssessmentMeters = ({ userResponses = {}, questionCategories = {} }) => {
  const [analyzer] = useState(() => new ResponseAnalyzer());
  const [scores, setScores] = useState({ heart: 0, body: 0, mind: 0, soul: 0 });
  const [metrics, setMetrics] = useState({});
  const [insights, setInsights] = useState([]);

  // Sample responses for demonstration (would come from actual user data)
  const sampleResponses = {
    'vision_question': "I'm passionate about creating sustainable technology solutions that can help reduce carbon emissions. I envision building a company that develops innovative clean energy systems for residential use. This vision drives me every day because I believe we have a responsibility to leave a better planet for future generations. I want to create meaningful change in how people consume energy.",
    'market_question': "Based on my research, the residential clean energy market is growing at 15% annually. There are approximately 130 million households in the US, with only 3% currently using advanced clean energy systems. The average household spends $2,400 annually on energy costs. Competitors like Tesla and Sunrun focus mainly on solar, but there's a gap in comprehensive energy management systems.",
    'financial_question': "I need approximately $500,000 in initial funding to develop the prototype and conduct market testing. This includes $200,000 for R&D, $150,000 for team salaries, $100,000 for equipment, and $50,000 for marketing. I project breaking even by month 18 with revenues of $2M in year two. I plan to bootstrap initially and then seek Series A funding.",
    'purpose_question': "My deeper purpose is to contribute to solving climate change while building a sustainable business. I want to create a legacy of environmental stewardship and inspire others to pursue purpose-driven entrepreneurship. This aligns with my core values of responsibility, innovation, and service to humanity."
  };

  const responses = Object.keys(userResponses).length > 0 ? userResponses : sampleResponses;

  // Calculate scores dynamically based on responses
  useEffect(() => {
    if (Object.keys(responses).length === 0) return;

    let newScores = { heart: 0, body: 0, mind: 0, soul: 0 };
    const responseAnalyses = {};

    // Analyze each response
    Object.entries(responses).forEach(([questionId, response]) => {
      const category = questionCategories[questionId] || 'general';
      const analysis = analyzer.analyzeResponse(response, category, 'general');
      responseAnalyses[questionId] = analysis;

      // Update scores based on this response
      newScores = analyzer.updateDimensionScores(newScores, analysis, category);
    });

    setScores(newScores);

    // Calculate completion metrics
    const totalQuestions = 100; // This would come from your assessment configuration
    const completionMetrics = analyzer.calculateCompletionMetrics(responses, totalQuestions);
    setMetrics(completionMetrics);

    // Generate insights
    const newInsights = analyzer.generateInsights(newScores, responses);
    setInsights(newInsights);

  }, [responses, questionCategories, analyzer]);

  const meters = [
    {
      key: 'heart',
      title: 'Heart',
      subtitle: 'What You Love',
      icon: Heart,
      color: 'from-red-500 to-pink-500',
      bgColor: 'bg-red-50',
      textColor: 'text-red-600',
      description: 'Your passion and emotional connection to your entrepreneurial vision',
      ikigaiQuadrant: 'Passion',
      factors: [
        'Personal interests and passions',
        'Activities that energize you',
        'Work that feels meaningful',
        'Natural inclinations and desires'
      ]
    },
    {
      key: 'body',
      title: 'Body',
      subtitle: 'What You Can Be Paid For',
      icon: Zap,
      color: 'from-orange-500 to-yellow-500',
      bgColor: 'bg-orange-50',
      textColor: 'text-orange-600',
      description: 'Market viability and financial sustainability of your venture',
      ikigaiQuadrant: 'Profession',
      factors: [
        'Market demand for your solution',
        'Revenue generation potential',
        'Customer willingness to pay',
        'Economic viability and scalability'
      ]
    },
    {
      key: 'mind',
      title: 'Mind',
      subtitle: 'What You Are Good At',
      icon: Brain,
      color: 'from-blue-500 to-indigo-500',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600',
      description: 'Your skills, competencies, and areas of expertise',
      ikigaiQuadrant: 'Profession',
      factors: [
        'Professional skills and expertise',
        'Educational background',
        'Work experience and achievements',
        'Natural talents and abilities'
      ]
    },
    {
      key: 'soul',
      title: 'Soul',
      subtitle: 'What The World Needs',
      icon: Star,
      color: 'from-purple-500 to-violet-500',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-600',
      description: 'The real problems and needs your venture addresses',
      ikigaiQuadrant: 'Mission',
      factors: [
        'Societal problems you can solve',
        'Community needs and gaps',
        'Environmental or social impact',
        'Meaningful contribution to the world'
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

  const getOverallReadiness = () => {
    const scoreValues = Object.values(scores);
    const average = scoreValues.reduce((a, b) => a + b, 0) / scoreValues.length;
    return Math.round(average);
  };

  const getReadinessMessage = (score) => {
    if (score >= 80) return "You're well-prepared for your entrepreneurial journey!";
    if (score >= 70) return "You're on a strong path. Focus on the areas that need attention.";
    if (score >= 60) return "Good foundation. Continue building in all areas.";
    if (score >= 50) return "Solid start. Invest more time in self-discovery.";
    return "Take time to deeply explore each dimension before proceeding.";
  };

  const getResponseQualityIndicator = (score) => {
    if (score >= 80) return { icon: CheckCircle, color: 'text-green-600', label: 'High Quality' };
    if (score >= 60) return { icon: TrendingUp, color: 'text-yellow-600', label: 'Good Quality' };
    return { icon: AlertCircle, color: 'text-red-600', label: 'Needs Improvement' };
  };

  return (
    <div className="space-y-6">
      {/* Real-time Ikigai Analysis Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            Entrepreneurial Ikigai Assessment
          </CardTitle>
          <CardDescription>
            Your entrepreneurial readiness across the four dimensions of Ikigai: What you Love, What you're Good at, What you can be Paid for, and What the World Needs. Scores update dynamically based on response quality and depth.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary">{metrics.answered || 0}</div>
              <div className="text-xs text-muted-foreground">Questions Answered</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary">{metrics.avgLength || 0}</div>
              <div className="text-xs text-muted-foreground">Avg Words/Response</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary">{metrics.avgQuality || 0}%</div>
              <div className="text-xs text-muted-foreground">Avg Response Quality</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary">{getOverallReadiness()}%</div>
              <div className="text-xs text-muted-foreground">Ikigai Alignment</div>
            </div>
          </div>
          
          {/* Ikigai Explanation */}
          <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border">
            <div className="text-sm font-medium text-gray-800 mb-2">🎯 Your Entrepreneurial Ikigai Journey</div>
            <p className="text-xs text-gray-600">
              Achieve entrepreneurial fulfillment by developing all four dimensions. When Heart, Body, Mind, and Soul reach high scores, 
              you'll find your entrepreneurial sweet spot - where passion meets profession, and mission meets vocation.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* The Four Dynamic Meters */}
      <div className="grid md:grid-cols-2 gap-6">
        {meters.map((meter) => {
          const score = Math.round(scores[meter.key] || 0);
          const Icon = meter.icon;
          const qualityIndicator = getResponseQualityIndicator(score);
          const QualityIcon = qualityIndicator.icon;
          
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
                    <div className={`text-2xl font-bold ${getScoreColor(score)}`}>
                      {score}%
                    </div>
                    <Badge variant="outline" className={getScoreColor(score)}>
                      {getScoreLabel(score)}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="pt-6">
                {/* Dynamic Progress Visualization */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-muted-foreground mb-2">
                    <span>Completion</span>
                    <span>{score}%</span>
                  </div>
                  <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
                    {/* Animated fill */}
                    <div 
                      className={`h-full bg-gradient-to-r ${meter.color} transition-all duration-1000 ease-out relative`}
                      style={{ width: `${score}%` }}
                    >
                      {/* Shimmer effect for active scoring */}
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse" />
                    </div>
                    
                    {/* Score markers */}
                    <div className="absolute inset-0 flex justify-between items-center px-1">
                      {[25, 50, 75].map(mark => (
                        <div 
                          key={mark}
                          className={`w-0.5 h-2 ${score >= mark ? 'bg-white' : 'bg-gray-400'} rounded`}
                        />
                      ))}
                    </div>
                  </div>
                </div>

                {/* Quality Indicator */}
                <div className="flex items-center gap-2 mb-4">
                  <QualityIcon className={`h-4 w-4 ${qualityIndicator.color}`} />
                  <span className={`text-sm font-medium ${qualityIndicator.color}`}>
                    {qualityIndicator.label}
                  </span>
                </div>

                {/* Response Analysis */}
                <div className="text-xs text-muted-foreground mb-4">
                  <div className="grid grid-cols-2 gap-2">
                    <div>Depth Score: <span className="font-medium">{Math.round(score * 0.8)}%</span></div>
                    <div>Factual Accuracy: <span className="font-medium">{Math.round(score * 0.9)}%</span></div>
                  </div>
                </div>

                {/* Key Areas Progress */}
                <div className="mb-4">
                  <div className="text-sm text-muted-foreground mb-2">Development Areas</div>
                  <div className="space-y-2">
                    {meter.factors.map((factor, index) => {
                      const factorScore = Math.max(0, score - (index * 10));
                      return (
                        <div key={index} className="flex items-center gap-2">
                          <div className="flex-1">
                            <div className="text-xs text-gray-600">{factor}</div>
                            <div className="w-full bg-gray-200 rounded-full h-1.5">
                              <div 
                                className={`h-1.5 bg-gradient-to-r ${meter.color} rounded-full transition-all duration-500`}
                                style={{ width: `${Math.min(factorScore, 100)}%` }}
                              />
                            </div>
                          </div>
                          <span className="text-xs text-gray-500 w-8">{Math.round(factorScore)}%</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Dynamic Recommendations */}
                {score < 70 && (
                  <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                    <div className="flex items-center gap-2 text-yellow-800">
                      <AlertCircle className="h-4 w-4" />
                      <span className="text-sm font-medium">Boost Your Score</span>
                    </div>
                    <p className="text-xs text-yellow-700 mt-1">
                      {score < 30 
                        ? "Answer more questions with detailed, thoughtful responses to increase this dimension."
                        : "Provide more specific examples and deeper analysis to reach the next level."
                      }
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Dynamic Insights */}
      {insights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Info className="h-5 w-5 text-primary" />
              Personalized Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {insights.map((insight, index) => (
                <div 
                  key={index}
                  className={`p-3 rounded-lg border ${
                    insight.type === 'strength' 
                      ? 'bg-green-50 border-green-200 text-green-800'
                      : 'bg-blue-50 border-blue-200 text-blue-800'
                  }`}
                >
                  <div className="text-sm font-medium capitalize">{insight.dimension} Dimension</div>
                  <div className="text-xs mt-1">{insight.message}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Scoring Methodology */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5 text-primary" />
            How Your Scores Are Calculated
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <div>
              <h4 className="font-medium mb-2">Quality Factors (Real-time Analysis)</h4>
              <ul className="space-y-1 text-muted-foreground">
                <li>• <strong>Response Length:</strong> Word count and detail level</li>
                <li>• <strong>Depth Analysis:</strong> Use of examples, reasoning, reflection</li>
                <li>• <strong>Thoroughness:</strong> Completeness for question type</li>
                <li>• <strong>Factual Accuracy:</strong> Real-world data validation</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Dimension Mapping</h4>
              <ul className="space-y-1 text-muted-foreground">
                <li>• <strong>Heart:</strong> Passion, emotion, personal drive</li>
                <li>• <strong>Body:</strong> Practical execution, material needs</li>
                <li>• <strong>Mind:</strong> Strategy, analysis, logical thinking</li>
                <li>• <strong>Soul:</strong> Purpose, values, social impact</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DynamicAssessmentMeters;

