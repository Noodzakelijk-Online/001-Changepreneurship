import React from "react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card.jsx";
import { Badge } from "@/components/ui/badge.jsx";
import { Progress } from "@/components/ui/progress.jsx";
import {
  CheckCircle,
  Clock,
  Target,
  TrendingUp,
  Heart,
  Lightbulb,
  Star,
  Compass,
  Brain,
  Zap,
} from "lucide-react";

const ProgressTracker = ({
  currentPhase,
  phaseProgress = {},
  timeSpent = 0,
  estimatedTimeRemaining = 60,
  isOptimized = false,
  connectedSources = [],
}) => {
  const phases = [
    {
      id: "self_discovery",
      title: "Self Discovery",
      description: "Core motivation, values, and vision",
      icon: Heart,
      estimatedTime: isOptimized ? 10 : 20,
      sections: [
        "motivation",
        "life-impact",
        "values",
        "vision",
        "confidence",
        "results",
      ],
    },
    {
      id: "idea_discovery",
      title: "Idea Discovery",
      description: "Business ideas and opportunities",
      icon: Lightbulb,
      estimatedTime: isOptimized ? 15 : 25,
      sections: [
        "core-alignment",
        "skills-assessment",
        "problem-identification",
        "market-promise",
        "opportunity-scoring",
      ],
    },
    {
      id: "market_research",
      title: "Market Research",
      description: "Industry analysis and validation",
      icon: Target,
      estimatedTime: isOptimized ? 10 : 20,
      sections: [
        "market-analysis",
        "competitor-research",
        "customer-validation",
      ],
    },
    {
      id: "business_pillars",
      title: "Business Pillars",
      description: "Foundation and strategy planning",
      icon: Star,
      estimatedTime: isOptimized ? 15 : 25,
      sections: [
        "business-model",
        "value-proposition",
        "revenue-streams",
        "key-resources",
      ],
    },
    {
      id: "product-testing",
      title: "Product Testing",
      description: "Concept validation and feedback",
      icon: Brain,
      estimatedTime: isOptimized ? 10 : 20,
      sections: ["concept-testing", "prototype-validation", "user-feedback"],
    },
    {
      id: "business_development",
      title: "Business Development",
      description: "Growth and scaling strategies",
      icon: TrendingUp,
      estimatedTime: isOptimized ? 8 : 15,
      sections: ["growth-strategy", "scaling-plan", "decision-making"],
    },
  ];

  const calculateOverallProgress = () => {
    const totalPhases = phases.length;
    const completedPhases = Object.values(phaseProgress).filter(
      (p) => p === 100
    ).length;
    const currentPhaseProgress = phaseProgress[currentPhase] || 0;

    return Math.round(
      ((completedPhases + currentPhaseProgress / 100) / totalPhases) * 100
    );
  };

  const calculateTimeRemaining = () => {
    const currentPhaseIndex = phases.findIndex((p) => p.id === currentPhase);
    const remainingPhases = phases.slice(currentPhaseIndex + 1);
    const currentPhaseTime = phases[currentPhaseIndex]?.estimatedTime || 0;
    const currentPhaseProgress = phaseProgress[currentPhase] || 0;

    const currentPhaseRemaining =
      currentPhaseTime * (1 - currentPhaseProgress / 100);
    const remainingPhasesTime = remainingPhases.reduce(
      (total, phase) => total + phase.estimatedTime,
      0
    );

    return Math.round(currentPhaseRemaining + remainingPhasesTime);
  };

  const overallProgress = calculateOverallProgress();
  const timeRemaining = calculateTimeRemaining();

  return (
    <Card className="sticky top-4">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Assessment Progress
        </CardTitle>
        <CardDescription>
          Track your journey through the entrepreneurial assessment
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Progress */}
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="font-medium">Overall Progress</span>
            <Badge variant="outline">{overallProgress}%</Badge>
          </div>
          <Progress value={overallProgress} className="h-3" />
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>Started</span>
            <span>Complete</span>
          </div>
        </div>

        {/* Time Information */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-muted/50 rounded-lg">
            <Clock className="h-5 w-5 mx-auto mb-1 text-primary" />
            <div className="text-sm font-medium">
              {Math.round(timeSpent)} min
            </div>
            <div className="text-xs text-muted-foreground">Time Spent</div>
          </div>
          <div className="text-center p-3 bg-muted/50 rounded-lg">
            <Target className="h-5 w-5 mx-auto mb-1 text-orange-600" />
            <div className="text-sm font-medium">{timeRemaining} min</div>
            <div className="text-xs text-muted-foreground">Remaining</div>
          </div>
        </div>

        {/* Optimization Status */}
        {isOptimized && (
          <div className="p-3 bg-green-50 dark:bg-green-950/20 rounded-lg border border-green-200 dark:border-green-800">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-green-800 dark:text-green-200">
                Assessment Optimized
              </span>
            </div>
            <div className="text-xs text-green-600 dark:text-green-400">
              {connectedSources.length} data source
              {connectedSources.length !== 1 ? "s" : ""} connected
            </div>
          </div>
        )}

        {/* Phase Progress */}
        <div className="space-y-3">
          <h4 className="font-medium">Phase Progress</h4>
          <div className="space-y-3">
            {phases.map((phase, index) => {
              const IconComponent = phase.icon;
              const progress = phaseProgress[phase.id] || 0;
              const isCompleted = progress === 100;
              const isCurrent = phase.id === currentPhase;
              const isUpcoming = !isCompleted && !isCurrent;

              return (
                <div
                  key={phase.id}
                  className={`flex items-center gap-3 p-3 rounded-lg border transition-colors ${
                    isCurrent
                      ? "border-primary bg-primary/5"
                      : isCompleted
                      ? "border-green-500 bg-green-50 dark:bg-green-950/20"
                      : "border-muted bg-muted/30"
                  }`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      isCompleted
                        ? "bg-green-500"
                        : isCurrent
                        ? "bg-primary"
                        : "bg-muted"
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle className="h-4 w-4 text-white" />
                    ) : (
                      <IconComponent
                        className={`h-4 w-4 ${
                          isCurrent ? "text-white" : "text-muted-foreground"
                        }`}
                      />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span
                        className={`font-medium text-sm ${
                          isCurrent
                            ? "text-primary"
                            : isCompleted
                            ? "text-green-700 dark:text-green-300"
                            : "text-muted-foreground"
                        }`}
                      >
                        {phase.title}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {phase.estimatedTime} min
                      </span>
                    </div>

                    {(isCurrent || isCompleted) && (
                      <div className="space-y-1">
                        <Progress value={progress} className="h-1" />
                        <div className="text-xs text-muted-foreground">
                          {progress}% complete
                        </div>
                      </div>
                    )}

                    {isUpcoming && (
                      <div className="text-xs text-muted-foreground">
                        {phase.description}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Completion Estimate */}
        <div className="text-center p-3 bg-orange-50 dark:bg-orange-950/20 rounded-lg border border-orange-200 dark:border-orange-800">
          <div className="text-sm font-medium text-orange-800 dark:text-orange-200">
            Estimated Completion
          </div>
          <div className="text-xs text-orange-600 dark:text-orange-400">
            {new Date(Date.now() + timeRemaining * 60000).toLocaleTimeString(
              [],
              {
                hour: "2-digit",
                minute: "2-digit",
              }
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProgressTracker;
