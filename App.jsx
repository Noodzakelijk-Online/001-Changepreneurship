import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Button } from "@/components/ui/button.jsx";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card.jsx";
import { Progress } from "@/components/ui/progress.jsx";
import { Badge } from "@/components/ui/badge.jsx";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs.jsx";
import {
  User,
  Lightbulb,
  Search,
  Building,
  ArrowRight,
  CheckCircle,
  Target,
  Heart,
  Brain,
  Compass,
  Star,
  TrendingUp,
  TestTube,
  Settings,
  Rocket,
} from "lucide-react";
import "./App.css";

// Contexts
import { AuthProvider } from "./contexts/AuthContext";
import {
  AssessmentProvider,
  useAssessment,
} from "./contexts/AssessmentContext";

// Components
import SelfDiscoveryAssessment from "./components/assessment/SelfDiscoveryAssessment";
import IdeaDiscoveryAssessment from "./components/assessment/IdeaDiscoveryAssessment";
import MarketResearchTools from "./components/assessment/MarketResearchTools";
import BusinessPillarsPlanning from "./components/assessment/BusinessPillarsPlanning";
import ProductConceptTesting from "./components/assessment/ProductConceptTesting";
import BusinessDevelopmentDecisionMaking from "./components/assessment/BusinessDevelopmentDecisionMaking";
import BusinessPrototypeTesting from "./components/assessment/BusinessPrototypeTesting";
import AIRecommendationsSimple from "./components/AIRecommendationsSimple";
import LandingPage from "./components/LandingPage";
import UserDashboard from "./components/dashboard/UserDashboard";
import AdaptiveDemo from "./components/AdaptiveDemo";
import SimpleAdaptiveDemo from "./components/SimpleAdaptiveDemo";

const AssessmentPage = () => {
  const { assessmentData, updateAssessmentData, currentPhase, updatePhase } =
    useAssessment();

  // Check for URL parameters to set initial phase
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const phaseParam = urlParams.get("phase");
    if (phaseParam) {
      const phaseNumber = parseInt(phaseParam);
      if (phaseNumber >= 1 && phaseNumber <= 7) {
        const phaseIds = [
          "self-discovery",
          "idea-discovery",
          "market-research",
          "business-pillars",
          "product-concept-testing",
          "business-development",
          "business-prototype-testing",
        ];
        updatePhase(phaseIds[phaseNumber - 1]);
      }
    }
  }, [updatePhase]);

  const phases = [
    {
      id: "self-discovery",
      title: "Self Discovery",
      description:
        "Understand your entrepreneurial personality and motivations",
      icon: User,
      color: "from-orange-500 to-red-500",
      duration: "60-90 minutes",
      category: "Foundation & Strategy",
      component: SelfDiscoveryAssessment,
    },
    {
      id: "idea-discovery",
      title: "Idea Discovery",
      description: "Transform insights into concrete business opportunities",
      icon: Lightbulb,
      color: "from-blue-500 to-purple-500",
      duration: "90-120 minutes",
      category: "Foundation & Strategy",
      component: IdeaDiscoveryAssessment,
    },
    {
      id: "market-research",
      title: "Market Research",
      description: "Validate assumptions and understand competitive dynamics",
      icon: Search,
      color: "from-green-500 to-teal-500",
      duration: "2-3 weeks",
      category: "Foundation & Strategy",
      component: MarketResearchTools,
    },
    {
      id: "business-pillars",
      title: "Business Pillars",
      description: "Define foundational elements for strategic planning",
      icon: Building,
      color: "from-purple-500 to-pink-500",
      duration: "1-2 weeks",
      category: "Foundation & Strategy",
      component: BusinessPillarsPlanning,
    },
    {
      id: "product-concept-testing",
      title: "Product Concept Testing",
      description: "Validate product concepts with real customer feedback",
      icon: TestTube,
      color: "from-yellow-500 to-orange-500",
      duration: "2-4 weeks",
      category: "Implementation & Testing",
      component: ProductConceptTesting,
    },
    {
      id: "business-development",
      title: "Business Development",
      description: "Strategic decision-making and resource optimization",
      icon: Settings,
      color: "from-indigo-500 to-blue-500",
      duration: "1-2 weeks",
      category: "Implementation & Testing",
      component: BusinessDevelopmentDecisionMaking,
    },
    {
      id: "business-prototype-testing",
      title: "Business Prototype Testing",
      description:
        "Complete business model validation in real market conditions",
      icon: Rocket,
      color: "from-red-500 to-pink-500",
      duration: "3-6 weeks",
      category: "Implementation & Testing",
      component: BusinessPrototypeTesting,
    },
  ];

  const currentPhaseIndex = phases.findIndex((p) => p.id === currentPhase);
  const currentPhaseData = phases[currentPhaseIndex];
  const CurrentComponent = currentPhaseData?.component;

  const calculateProgress = () => {
    const completedPhases = phases.filter(
      (phase) => assessmentData[phase.id]?.completed
    ).length;
    return Math.round((completedPhases / phases.length) * 100);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-primary to-orange-500 bg-clip-text text-transparent">
            Changepreneurship Assessment
          </h1>
          <p className="text-muted-foreground text-lg">
            Transform your entrepreneurial journey with our comprehensive 7-part
            framework
          </p>
        </div>

        {/* Progress Overview */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Compass className="h-5 w-5" />
              Your Journey Progress
            </CardTitle>
            <CardDescription>
              Complete all seven phases to unlock your personalized business
              development roadmap
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-4 mb-6">
              {phases.map((phase, index) => {
                const Icon = phase.icon;
                const isCompleted =
                  assessmentData[phase.id]?.completed || false;
                const isCurrent = phase.id === currentPhase;
                const isAccessible = true; // All phases accessible for testing

                return (
                  <Card
                    key={phase.id}
                    className={`relative overflow-hidden transition-all duration-300 ${
                      isCurrent ? "ring-2 ring-primary" : ""
                    } ${
                      isAccessible
                        ? "cursor-pointer hover:shadow-lg"
                        : "opacity-50"
                    }`}
                    onClick={() => isAccessible && updatePhase(phase.id)}
                  >
                    <div
                      className={`absolute inset-0 bg-gradient-to-br ${phase.color} opacity-10`}
                    />
                    <CardContent className="p-4 relative">
                      <div className="flex items-center justify-between mb-2">
                        <Icon className="h-6 w-6 text-primary" />
                        {isCompleted && (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        )}
                      </div>
                      <h3 className="font-semibold text-sm mb-1">
                        {phase.title}
                      </h3>
                      <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                        {phase.description}
                      </p>
                      <div className="space-y-1">
                        <Badge variant="secondary" className="text-xs">
                          {phase.category}
                        </Badge>
                        <p className="text-xs text-muted-foreground">
                          {phase.duration}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Overall Progress</span>
                <Badge variant="outline">{calculateProgress()}%</Badge>
              </div>
              <Progress value={calculateProgress()} className="flex-1 mx-4" />
            </div>
          </CardContent>
        </Card>

        {/* Current Assessment */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {currentPhaseData && (
                <currentPhaseData.icon className="h-5 w-5" />
              )}
              {currentPhaseData?.title}
            </CardTitle>
            <CardDescription>{currentPhaseData?.description}</CardDescription>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{currentPhaseData?.category}</Badge>
              <span className="text-sm text-muted-foreground">
                Phase {currentPhaseIndex + 1} of {phases.length}
              </span>
            </div>
          </CardHeader>
          <CardContent>{CurrentComponent && <CurrentComponent />}</CardContent>
        </Card>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <AssessmentProvider>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/assessment" element={<AssessmentPage />} />
              <Route
                path="/ai-recommendations"
                element={<AIRecommendationsSimple />}
              />
              <Route path="/user-dashboard" element={<UserDashboard />} />
              <Route path="/adaptive-demo" element={<AdaptiveDemo />} />
              <Route path="/simple-adaptive" element={<SimpleAdaptiveDemo />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </Router>
      </AssessmentProvider>
    </AuthProvider>
  );
}

export default App;
