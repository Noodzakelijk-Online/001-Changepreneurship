import React, { useEffect, useState, useRef, useRef as useDoubleRef } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useParams
} from "react-router-dom";
import { slugToPhaseId } from './lib/assessmentPhases.js';
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

// Navigation utilities
import { NavigationProvider } from "./contexts/NavigationContext.jsx";
import QuestionNavigator from "./components/navigation/QuestionNavigator.jsx";

// Contexts
import { AuthProvider } from "./contexts/AuthContext";
import {
  AssessmentProvider,
  useAssessment,
} from "./contexts/AssessmentContext";

// Components
import ReactLazy from 'react';
const SelfDiscoveryAssessment = React.lazy(() => import('./components/assessment/SelfDiscoveryAssessment'));
const IdeaDiscoveryAssessment = React.lazy(() => import('./components/assessment/IdeaDiscoveryAssessment'));
const MarketResearchTools = React.lazy(() => import('./components/assessment/MarketResearchTools'));
const BusinessPillarsPlanning = React.lazy(() => import('./components/assessment/BusinessPillarsPlanning'));
const ProductConceptTesting = React.lazy(() => import('./components/assessment/ProductConceptTesting'));
const BusinessDevelopmentDecisionMaking = React.lazy(() => import('./components/assessment/BusinessDevelopmentDecisionMaking'));
const BusinessPrototypeTesting = React.lazy(() => import('./components/assessment/BusinessPrototypeTesting'));
import AIRecommendationsSimple from "./components/AIRecommendationsSimple";
import LandingPage from "./components/LandingPage";
import UserDashboard from "./components/dashboard/UserDashboard";
import AdaptiveDemo from "./components/AdaptiveDemo";
import SimpleAdaptiveDemo from "./components/SimpleAdaptiveDemo";
import ProfileSettings from "./components/ProfileSettings";
import AssessmentHistory from "./components/AssessmentHistory";
import NavBar from "./components/NavBar";
import PhasePage from "./pages/PhasePage.jsx";

// slugToPhaseId now imported from central mapping

const AssessmentPage = () => {
  const { assessmentData, updatePhase, currentPhase } = useAssessment();
  const [selectedPhase, setSelectedPhase] = useState(null);
  const params = typeof useParams === 'function' ? useParams() : {};
  const slugPhaseId = slugToPhaseId(params?.slug);
  const unknownSlug = params?.slug && !slugPhaseId;

  const initRef = useRef(false);
  useEffect(() => {
    if (initRef.current) return; // only run once
    initRef.current = true;
    if (slugPhaseId) {
      setSelectedPhase(slugPhaseId);
      updatePhase(slugPhaseId);
      localStorage.setItem('cp_selected_phase', slugPhaseId);
      return;
    }
    const urlParams = new URLSearchParams(window.location.search);
    const phaseParam = urlParams.get("phase");
    if (phaseParam) {
      const phaseNumber = parseInt(phaseParam);
      const phaseIds = [
        "self_discovery",
        "idea_discovery",
        "market_research",
        "business_pillars",
        "product_concept_testing",
        "business_development",
        "business_prototype_testing",
      ];
      if (phaseNumber >= 1 && phaseNumber <= phaseIds.length) {
        const phaseId = phaseIds[phaseNumber - 1];
        setSelectedPhase(phaseId);
        updatePhase(phaseId);
        localStorage.setItem('cp_selected_phase', phaseId);
        return;
      }
    }
    const stored = localStorage.getItem('cp_selected_phase');
    if (stored) {
      setSelectedPhase(stored);
      updatePhase(stored);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const phases = [
    {
      id: "self_discovery",
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
      id: "idea_discovery",
      title: "Idea Discovery",
      description: "Transform insights into concrete business opportunities",
      icon: Lightbulb,
      color: "from-blue-500 to-purple-500",
      duration: "90-120 minutes",
      category: "Foundation & Strategy",
      component: IdeaDiscoveryAssessment,
    },
    {
      id: "market_research",
      title: "Market Research",
      description: "Validate assumptions and understand competitive dynamics",
      icon: Search,
      color: "from-green-500 to-teal-500",
      duration: "2-3 weeks",
      category: "Foundation & Strategy",
      component: MarketResearchTools,
    },
    {
      id: "business_pillars",
      title: "Business Pillars",
      description: "Define foundational elements for strategic planning",
      icon: Building,
      color: "from-purple-500 to-pink-500",
      duration: "1-2 weeks",
      category: "Foundation & Strategy",
      component: BusinessPillarsPlanning,
    },
    {
      id: "product_concept_testing",
      title: "Product Concept Testing",
      description: "Validate product concepts with real customer feedback",
      icon: TestTube,
      color: "from-yellow-500 to-orange-500",
      duration: "2-4 weeks",
      category: "Implementation & Testing",
      component: ProductConceptTesting,
    },
    {
      id: "business_development",
      title: "Business Development",
      description: "Strategic decision-making and resource optimization",
      icon: Settings,
      color: "from-indigo-500 to-blue-500",
      duration: "1-2 weeks",
      category: "Implementation & Testing",
      component: BusinessDevelopmentDecisionMaking,
    },
    {
      id: "business_prototype_testing",
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

  // Sync only when context changes explicitly and not during initial mount
  useEffect(() => {
    if (initRef.current && currentPhase !== selectedPhase) {
      setSelectedPhase(currentPhase);
    }
  }, [currentPhase]);

  const currentPhaseIndex = phases.findIndex((p) => p.id === selectedPhase);
  const currentPhaseData = phases[currentPhaseIndex];
  const CurrentComponent = currentPhaseData?.component;
  const phaseHeadingRef = useRef(null);

  const handlePhaseSelect = (phaseId) => {
    setSelectedPhase(phaseId);
    updatePhase(phaseId);
    localStorage.setItem('cp_selected_phase', phaseId);
  };

  const handleBackToPhases = () => {
    setSelectedPhase(null);
    updatePhase(null);
    localStorage.removeItem('cp_selected_phase');
  };

  // Focus phase heading when a phase is selected
  useEffect(() => {
    if (CurrentComponent && phaseHeadingRef.current) {
      phaseHeadingRef.current.focus();
    }
  }, [CurrentComponent, selectedPhase]);

  const calculateProgress = () => {
    const completedPhases = phases.filter(
      (phase) => assessmentData[phase.id]?.completed
    ).length;
    return Math.round((completedPhases / phases.length) * 100);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {unknownSlug && (
          <div className="mb-4 p-4 border border-destructive/30 bg-destructive/10 rounded text-sm">
            Unknown assessment segment "{params.slug}". <button className="underline" onClick={() => { setSelectedPhase(null); window.location.hash = '#/assessment'; }}>Return to all phases</button>
          </div>
        )}
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

        {/* Phase Selection or Current Assessment */}
        {!CurrentComponent ? (
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
                {phases.map((phase) => {
                  const Icon = phase.icon;
                  const isCompleted =
                    assessmentData[phase.id]?.completed || false;
                  const isCurrent = phase.id === selectedPhase;
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
                      onClick={() => isAccessible && handlePhaseSelect(phase.id)}
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
        ) : (
          <>
            <Button
              variant="outline"
              className="mb-4"
              onClick={handleBackToPhases}
            >
              ← Back to phases
            </Button>
            <Card>
              <CardHeader>
                <CardTitle ref={phaseHeadingRef} tabIndex="-1" className="flex items-center gap-2 focus:outline-none">
                  {currentPhaseData?.icon ? (() => { const IconComp = currentPhaseData.icon; return <IconComp className="h-5 w-5" />; })() : null}
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
              <CardContent>
                {CurrentComponent && (
                  <React.Suspense fallback={<div className="animate-pulse text-sm text-muted-foreground">Loading assessment...</div>}>
                    <CurrentComponent />
                  </React.Suspense>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

function App() {
  // Simple error boundary wrapper (hook-based fallback)
  const [routeError, setRouteError] = useState(null);
  const ErrorBoundary = ({ children }) => {
    if (routeError) {
      return (
        <div className="p-8 text-center">
          <h2 className="text-xl font-semibold mb-4">Something went wrong</h2>
          <p className="text-muted-foreground mb-4">{routeError.message}</p>
          <button
            className="px-4 py-2 rounded bg-primary text-primary-foreground"
            onClick={() => { setRouteError(null); window.location.hash = '#/assessment'; }}
          >
            Back to Assessments
          </button>
        </div>
      );
    }
    return children;
  };

  return (
    <AuthProvider>
      <AssessmentProvider>
        <NavigationProvider>
          <Router>
            <div className="App">
              <NavBar />
              <main className="pt-16">
                <ErrorBoundary>
                  <Routes>
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/assessment" element={<AssessmentPage />} />
                  <Route path="/assessment/:slug" element={<AssessmentPage />} />
                  <Route
                    path="/ai-recommendations"
                    element={<AIRecommendationsSimple />}
                  />
                  <Route path="/user-dashboard" element={<UserDashboard />} />
                  <Route path="/adaptive-demo" element={<AdaptiveDemo />} />
                  <Route path="/simple-adaptive" element={<SimpleAdaptiveDemo />} />
                  <Route path="/profile" element={<ProfileSettings />} />
                  <Route path="/assessment-history" element={<AssessmentHistory />} />
                  <Route
                    path="/new/:phaseId/:tabId/:sectionId/:questionId"
                    element={<PhasePage />}
                  />
                  <Route
                    path="/phase/:phase/tab/:tab/section/:section/question/:question"
                    element={<QuestionNavigator />}
                  />
                  <Route path="/:code" element={<QuestionNavigator />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </ErrorBoundary>
              </main>
            </div>
          </Router>
        </NavigationProvider>
      </AssessmentProvider>
    </AuthProvider>
  );
}

export default App;
