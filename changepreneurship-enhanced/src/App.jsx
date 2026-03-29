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
  ArrowLeft,
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
import LandingPage from "./components/LandingPage";
import UnifiedDashboard from "./components/dashboard/UnifiedDashboard";
import ExecutiveSummaryDashboard from "./components/ExecutiveSummaryDashboard";
import ProfileSettings from "./components/ProfileSettings";
import AssessmentHistory from "./components/AssessmentHistory";
import NavBar from "./components/NavBar";
import PhasePage from "./pages/PhasePage.jsx";
import AIInsightsPage from "./pages/AIInsightsPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";

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
    // Only restore from localStorage if we arrived via a direct URL slug above.
    // At plain /assessment we always show the picker so the user can choose.
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

  // Phase selected — render AssessmentShell directly, no outer wrappers
  if (CurrentComponent) {
    const Icon = currentPhaseData.icon;
    return (
      <div className="flex flex-col min-h-screen bg-gray-950">
        {/* Phase breadcrumb bar */}
        <div className="sticky top-16 z-30 bg-black/70 backdrop-blur-md border-b border-gray-800/60 px-6 py-2.5 flex items-center justify-between">
          <button
            type="button"
            onClick={handleBackToPhases}
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-cyan-400 transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            All Stages
          </button>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Icon className="h-3.5 w-3.5" />
            <span className="text-gray-300 font-medium">{currentPhaseData.title}</span>
            <span className="text-gray-600">— Phase {currentPhaseIndex + 1} of {phases.length}</span>
          </div>
          {/* Mini phase switcher */}
          <div className="hidden md:flex items-center gap-1">
            {phases.map((p, i) => {
              const isActive = p.id === selectedPhase;
              const isDone = assessmentData[p.id]?.completed;
              return (
                <button
                  key={p.id}
                  type="button"
                  title={p.title}
                  onClick={() => handlePhaseSelect(p.id)}
                  className={`w-6 h-6 rounded-md text-xs font-bold transition-all ${
                    isActive
                      ? 'bg-gradient-to-br from-cyan-500 to-purple-500 text-white shadow-sm shadow-cyan-500/30'
                      : isDone
                      ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30'
                      : 'bg-gray-800 text-gray-600 hover:bg-gray-700 hover:text-gray-400'
                  }`}
                >
                  {i + 1}
                </button>
              );
            })}
          </div>
        </div>

        {unknownSlug && (
          <div className="px-6 py-2 text-sm text-red-400 bg-red-500/10 border-b border-red-500/20">
            Unknown segment "{params.slug}".{' '}
            <button className="underline" onClick={handleBackToPhases}>Return to all phases</button>
          </div>
        )}

        <div className="flex-1">
          <React.Suspense fallback={
            <div className="min-h-[60vh] bg-gray-950 flex items-center justify-center">
              <div className="animate-pulse text-sm text-gray-600">Loading assessment...</div>
            </div>
          }>
            <CurrentComponent />
          </React.Suspense>
        </div>
      </div>
    );
  }

  // No phase selected — dark phase picker
  return (
    <div className="min-h-screen bg-black text-white">
      <div className="container mx-auto px-6 py-12">
        {unknownSlug && (
          <div className="mb-6 p-4 border border-red-500/30 bg-red-500/10 rounded-xl text-sm text-red-400">
            Unknown assessment segment "{params.slug}".{' '}
            <button className="underline" onClick={() => { setSelectedPhase(null); }}>
              Return to all phases
            </button>
          </div>
        )}

        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-block px-4 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 mb-4">
            <span className="text-cyan-400 text-sm uppercase tracking-widest">7-Stage Framework</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-3">Choose Your Stage</h1>
          <p className="text-gray-500 text-lg max-w-xl mx-auto">
            Each stage builds on the previous. Work through them in order for the best results.
          </p>
        </div>

        {/* Overall progress bar */}
        <div className="max-w-xl mx-auto mb-10 flex items-center gap-4">
          <span className="text-sm text-gray-500 whitespace-nowrap">Overall Progress</span>
          <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full transition-all duration-500"
              style={{ width: `${calculateProgress()}%` }}
            />
          </div>
          <span className="text-sm font-semibold text-cyan-400 whitespace-nowrap">{calculateProgress()}%</span>
        </div>

        {/* Phase cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {phases.map((phase, index) => {
            const Icon = phase.icon;
            const isCompleted = assessmentData[phase.id]?.completed || false;

            return (
              <button
                key={phase.id}
                type="button"
                onClick={() => handlePhaseSelect(phase.id)}
                className={`relative overflow-hidden group text-left rounded-2xl border p-6 transition-all duration-300 hover:scale-[1.02] ${
                  isCompleted
                    ? 'border-emerald-500/30 bg-gradient-to-br from-emerald-500/5 to-gray-900'
                    : 'border-gray-800 bg-gradient-to-br from-gray-900 to-black hover:border-cyan-500/40'
                }`}
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${phase.color} opacity-0 group-hover:opacity-5 transition-opacity rounded-2xl`} />
                <div className="relative">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-2.5 rounded-xl bg-gradient-to-br ${phase.color} shadow-lg`}>
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex items-center gap-2">
                      {isCompleted && <CheckCircle className="h-4 w-4 text-emerald-400" />}
                      <span className="text-xs text-gray-600 font-medium">Stage {index + 1}</span>
                    </div>
                  </div>
                  <h3 className="font-semibold text-white mb-1.5 text-sm">{phase.title}</h3>
                  <p className="text-xs text-gray-500 leading-relaxed mb-4">{phase.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-600">{phase.duration}</span>
                    <span className={`text-xs font-medium ${isCompleted ? 'text-emerald-400' : 'text-cyan-400 group-hover:text-cyan-300'}`}>
                      {isCompleted ? 'Completed ✓' : 'Start →'}
                    </span>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
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
                  
                  {/* Main Dashboard - Unified */}
                  <Route path="/dashboard" element={<UnifiedDashboard />} />
                  
                  {/* Executive Summary → redirect to full AI Insights */}
                  <Route path="/dashboard/executive-summary" element={<Navigate to="/ai-insights" replace />} />
                  
                  {/* Legacy redirects - maintain backward compatibility */}
                  <Route path="/user-dashboard" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/ai-insights" element={<AIInsightsPage />} />
                  <Route path="/ai-insights/recommendations" element={<AIInsightsPage />} />
                  <Route path="/ai-recommendations" element={<Navigate to="/ai-insights" replace />} />
                  <Route path="/login" element={<LoginPage />} />
                  
                  {/* User settings */}
                  <Route path="/profile" element={<ProfileSettings />} />
                  <Route path="/assessment-history" element={<AssessmentHistory />} />
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
