import React, { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  Outlet,
} from "react-router-dom";
import "./App.css";

// Navigation utilities
import { NavigationProvider } from "./contexts/NavigationContext.jsx";

// Contexts
import { AuthProvider } from "./contexts/AuthContext";
import { AssessmentProvider } from "./contexts/AssessmentContext";

// Components
const Phase1Form = React.lazy(() => import('./components/assessment/Phase1Form'));
const Phase2Form = React.lazy(() => import('./components/assessment/Phase2Form'));
const MarketResearchTools = React.lazy(() => import('./components/assessment/MarketResearchTools'));
const BusinessPillarsPlanning = React.lazy(() => import('./components/assessment/BusinessPillarsPlanning'));
const ProductConceptTesting = React.lazy(() => import('./components/assessment/ProductConceptTesting'));
const BusinessDevelopmentDecisionMaking = React.lazy(() => import('./components/assessment/BusinessDevelopmentDecisionMaking'));
const BusinessPrototypeTesting = React.lazy(() => import('./components/assessment/BusinessPrototypeTesting'));
import LandingPage from "./components/LandingPage";
import UnifiedDashboard from "./components/dashboard/UnifiedDashboard";
import ProfileSettings from "./components/ProfileSettings";
import AssessmentHistory from "./components/AssessmentHistory";
import AppLayout from "./components/layout/AppLayout";
import AIInsightsPage from "./pages/AIInsightsPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import PhaseCompletionPanel from "./components/assessment/PhaseCompletionPanel.jsx";
import ConsentSettingsPage from "./pages/ConsentSettingsPage.jsx";
import ConnectedAccountsPage from "./pages/ConnectedAccountsPage.jsx";

// Lazy-loaded page wrappers
const StrategyEnginePage = React.lazy(() => import('./pages/StrategyEnginePage.jsx'));
const VentureProfilePage = React.lazy(() => import('./pages/VentureProfilePage.jsx'));
const AccountSettingsPage = React.lazy(() => import('./pages/AccountSettingsPage.jsx'));
const ValueZonePage      = React.lazy(() => import('./pages/ValueZonePage.jsx'));
const MindMappingPage    = React.lazy(() => import('./pages/MindMappingPage.jsx'));

// Loading fallback
const PageLoader = () => (
  <div className="flex items-center justify-center h-full py-24">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500" />
  </div>
);

// Layout wrapper for all authenticated pages (sidebar + content)
const AuthLayout = () => (
  <AppLayout>
    <Outlet />
  </AppLayout>
);

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
            onClick={() => { setRouteError(null); window.location.href = '/dashboard'; }}
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
              <PhaseCompletionPanel />
              <ErrorBoundary>
                <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/assessment" element={<Navigate to="/dashboard" replace />} />
                <Route path="/assessment/:slug" element={<Navigate to="/dashboard" replace />} />

                {/* All authenticated pages wrapped in AuthLayout (provides sidebar) */}
                <Route element={<AuthLayout />}>
                  {/* Phase assessment routes */}
                  <Route path="/assessment/entrepreneur-discovery" element={
                    <React.Suspense fallback={<PageLoader />}><Phase1Form /></React.Suspense>
                  } />
                  <Route path="/assessment/idea-discovery" element={
                    <React.Suspense fallback={<PageLoader />}><Phase2Form /></React.Suspense>
                  } />
                  <Route path="/assessment/market-research" element={
                    <React.Suspense fallback={<PageLoader />}><MarketResearchTools /></React.Suspense>
                  } />
                  <Route path="/assessment/business-pillars" element={
                    <React.Suspense fallback={<PageLoader />}><BusinessPillarsPlanning /></React.Suspense>
                  } />
                  <Route path="/assessment/business-pillars-planning" element={
                    <React.Suspense fallback={<PageLoader />}><BusinessPillarsPlanning /></React.Suspense>
                  } />
                  <Route path="/assessment/product-concept" element={
                    <React.Suspense fallback={<PageLoader />}><ProductConceptTesting /></React.Suspense>
                  } />
                  <Route path="/assessment/product-concept-testing" element={
                    <React.Suspense fallback={<PageLoader />}><ProductConceptTesting /></React.Suspense>
                  } />
                  <Route path="/assessment/business-development" element={
                    <React.Suspense fallback={<PageLoader />}><BusinessDevelopmentDecisionMaking /></React.Suspense>
                  } />
                  <Route path="/assessment/business-prototype" element={
                    <React.Suspense fallback={<PageLoader />}><BusinessPrototypeTesting /></React.Suspense>
                  } />
                  <Route path="/assessment/business-prototype-testing" element={
                    <React.Suspense fallback={<PageLoader />}><BusinessPrototypeTesting /></React.Suspense>
                  } />

                  {/* Main Dashboard */}
                  <Route path="/dashboard" element={<UnifiedDashboard />} />
                  <Route path="/dashboard/executive-summary" element={<Navigate to="/ai-insights" replace />} />

                  {/* Legacy redirects */}
                  <Route path="/user-dashboard" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/ai-insights" element={<AIInsightsPage />} />
                  <Route path="/ai-insights/recommendations" element={<AIInsightsPage />} />
                  <Route path="/ai-recommendations" element={<Navigate to="/ai-insights" replace />} />

                  {/* User settings */}
                  <Route path="/profile" element={<ProfileSettings />} />
                  <Route path="/profile/connections" element={
                    <React.Suspense fallback={<PageLoader />}><ConnectedAccountsPage /></React.Suspense>
                  } />
                  <Route path="/settings/account" element={
                    <React.Suspense fallback={<PageLoader />}><AccountSettingsPage /></React.Suspense>
                  } />
                  <Route path="/settings/consent" element={
                    <React.Suspense fallback={<PageLoader />}><ConsentSettingsPage /></React.Suspense>
                  } />
                  <Route path="/assessment-history" element={<AssessmentHistory />} />

                  {/* Other sidebar pages */}
                  <Route path="/venture-profile" element={
                    <React.Suspense fallback={<PageLoader />}><VentureProfilePage /></React.Suspense>
                  } />
                  <Route path="/routing" element={
                    <React.Suspense fallback={<PageLoader />}><StrategyEnginePage /></React.Suspense>
                  } />

                  {/* Sidebar links that previously had no route — redirect to the relevant phase */}
                  <Route path="/strategic-roadmap" element={<Navigate to="/assessment/market-research" replace />} />
                  <Route path="/ventures" element={<Navigate to="/venture-profile" replace />} />
                  <Route path="/structure-entity" element={<Navigate to="/assessment/business-pillars-planning" replace />} />

                  {/* Legacy redirect routes */}
                  <Route path="/value-zone" element={
                    <React.Suspense fallback={<PageLoader />}><ValueZonePage /></React.Suspense>
                  } />
                  <Route path="/mind-mapping" element={
                    <React.Suspense fallback={<PageLoader />}><MindMappingPage /></React.Suspense>
                  } />
                </Route>

                <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </ErrorBoundary>
            </div>
          </Router>
        </NavigationProvider>
      </AssessmentProvider>
    </AuthProvider>
  );
}

export default App;
