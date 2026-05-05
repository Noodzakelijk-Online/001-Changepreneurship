/**
 * AppSidebar — Sprint 8
 *
 * Left navigation sidebar for authenticated users.
 * Mirrors the Manus reference UI and CEO document Section 3.3.
 *
 * Structure:
 *   [Logo / Brand]
 *   ─── OVERVIEW ────────────────
 *   Journey Map
 *   ─── PHASE 1: SELF-DISCOVERY ─
 *   🧭 Entrepreneur Discovery  [status badge]
 *   💰 Value Zone
 *   🧠 Mind Map
 *   ─── PHASE 2: IDEA DISCOVERY ─
 *   💡 Idea Discovery          [LOCKED]
 *   ⚡ Strategy Engine
 *   ... (phases 3-7)
 *   ─────────────────────────────
 *   ⚙️ Settings
 *   🚪 Sign Out
 *
 * Phase gating: locked phases show a lock icon and grey text.
 * Progress %: shown next to each phase header.
 * Active item: highlighted with accent colour.
 */
import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Map, Lightbulb, Search, Building2, FlaskConical,
  TrendingUp, Rocket, Settings, LogOut, ChevronDown,
  ChevronRight, Lock, CheckCircle2, Compass, Zap,
  Brain, Target, BarChart3, X, Shield, Link2, KeyRound,
  Activity,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import apiService from '../../services/api.js';

// ─── Phase / nav structure ───────────────────────────────────────────────────
// Matches CEO doc Section 3.3 + Manus reference UI
const NAV_STRUCTURE = [
  {
    type: 'section',
    label: 'OVERVIEW',
    items: [
      { label: 'Journey Map',      icon: Map,    path: '/dashboard',        id: 'journey-map' },
      { label: 'Venture Profile',  icon: Target, path: '/venture-profile',  id: 'venture-profile' },
    ],
  },
  {
    type: 'phase',
    phaseKey: 'phase1',
    phaseNumber: 1,
    label: 'PHASE 1: SELF-DISCOVERY',
    items: [
      { label: 'Entrepreneur Discovery', icon: Compass, path: '/assessment/entrepreneur-discovery', id: 'self-discovery' },
    ],
  },
  {
    type: 'phase',
    phaseKey: 'phase2',
    phaseNumber: 2,
    label: 'PHASE 2: IDEA DISCOVERY',
    items: [
      { label: 'Idea Discovery',  icon: Lightbulb, path: '/assessment/idea-discovery', id: 'idea-discovery' },
      { label: 'Strategy Engine', icon: Zap,       path: '/routing',                   id: 'strategy' },
    ],
  },
  {
    type: 'phase',
    phaseKey: 'phase3',
    phaseNumber: 3,
    label: 'PHASE 3: MARKET RESEARCH',
    items: [
      { label: 'Market Discovery',  icon: Search,    path: '/assessment/market-research', id: 'market-research' },
      { label: 'Strategic Roadmap', icon: BarChart3, path: '/strategic-roadmap',           id: 'strategic-roadmap' },
    ],
  },
  {
    type: 'phase',
    phaseKey: 'phase4',
    phaseNumber: 4,
    label: 'PHASE 4: BUSINESS PILLARS',
    items: [
      { label: 'Execution Lab',      icon: Building2,  path: '/assessment/business-pillars-planning', id: 'business-pillars' },
      { label: 'Venture Builder',    icon: TrendingUp, path: '/ventures',                             id: 'venture-builder' },
      { label: 'Structure & Entity', icon: Shield,     path: '/structure-entity',                     id: 'structure-entity' },
    ],
  },
  {
    type: 'phase',
    phaseKey: 'phase5',
    phaseNumber: 5,
    label: 'PHASE 5: CONCEPT TESTING',
    items: [
      { label: 'Concept Testing', icon: FlaskConical, path: '/assessment/product-concept-testing', id: 'concept-testing' },
    ],
  },
  {
    type: 'phase',
    phaseKey: 'phase6',
    phaseNumber: 6,
    label: 'PHASE 6: BUSINESS DEVELOPMENT',
    items: [
      { label: 'Business Development', icon: BarChart3, path: '/assessment/business-development', id: 'business-development' },
    ],
  },
  {
    type: 'phase',
    phaseKey: 'phase7',
    phaseNumber: 7,
    label: 'PHASE 7: PROTOTYPE TESTING',
    items: [
      { label: 'Prototype Testing', icon: Rocket, path: '/assessment/business-prototype-testing', id: 'prototype-testing' },
    ],
  },
];

// ─── Helper: is a phase locked? ──────────────────────────────────────────────
// Phase 1 always unlocked. Others unlocked if previous phase completed.
function isPhaseAccessible(phaseNumber, gateStatus) {
  if (phaseNumber <= 1) return true;
  const prevGate = gateStatus[String(phaseNumber - 1)];
  return prevGate === 'COMPLETED';
}

function phaseGateHint(phaseNumber, gateStatus) {
  if (phaseNumber <= 1) return null;
  const prevStatus = gateStatus[String(phaseNumber - 1)];
  if (prevStatus === 'IN_PROGRESS') return `Phase ${phaseNumber - 1} in progress`;
  if (!prevStatus || prevStatus === 'NOT_STARTED') return `Complete Phase ${phaseNumber - 1} first`;
  return null;
}

// ─── PhaseProgress bar ───────────────────────────────────────────────────────
function MiniProgress({ pct }) {
  if (pct == null) return null;
  return (
    <div className="mt-0.5 w-full bg-slate-700 rounded-full h-1">
      <div
        className="h-1 rounded-full bg-indigo-500 transition-all"
        style={{ width: `${Math.min(100, pct)}%` }}
      />
    </div>
  );
}

// ─── Sidebar content ─────────────────────────────────────────────────────────
export default function AppSidebar({ onClose }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const [gateStatus, setGateStatus]       = useState({});   // { "1": "IN_PROGRESS", "2": "LOCKED", ... }
  const [phaseProgress, setPhaseProgress] = useState({});   // { "1": 45, "2": 0, ... }
  const [collapsed, setCollapsed]         = useState({});   // which phase sections are collapsed
  const [venture, setVenture]             = useState(null); // active venture for context strip
  const [matrix, setMatrix]               = useState(null); // founder matrix for route badge

  // Load phase gate + progress + venture context from backend
  // Re-fetch on every route change so phase unlocks are reflected immediately
  useEffect(() => {
    async function load() {
      try {
        const [phasesRes, activeRes, profileRes] = await Promise.allSettled([
          apiService.request('/v1/progress/phases'),
          apiService.request('/v1/ventures/active'),
          apiService.request('/v1/ventures/profile'),
        ]);

        // Phase progress — FIX: result.data contains the payload; use p.order (1-7) as key
          if (phasesRes.status === 'fulfilled' && phasesRes.value.success) {
          const gates = {};
          const pcts  = {};
          (phasesRes.value.data?.phases || []).forEach(p => {
            const key = String(p.order ?? p.phase_number);
            gates[key] = p.status;
            pcts[key]  = p.progress_percentage ?? 0;
          });
          setGateStatus(gates);
          setPhaseProgress(pcts);
        } else {
          setGateStatus({ '1': 'IN_PROGRESS' });
        }

        // Venture context
        if (activeRes.status === 'fulfilled' && activeRes.value.success) {
          setVenture(activeRes.value.data?.venture || null);
        }

        // Founder matrix for route badge
        if (profileRes.status === 'fulfilled' && profileRes.value.success) {
          setMatrix(profileRes.value.data?.founder_matrix || null);
        }
      } catch {
        setGateStatus({ '1': 'IN_PROGRESS' });
      }
    }
    load();
  }, [location.pathname]);

  function handleSignOut() {
    logout();
    navigate('/');
  }

  function toggleCollapse(key) {
    setCollapsed(prev => ({ ...prev, [key]: !prev[key] }));
  }

  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/');

  const route = (matrix?.recommended_route || '').toUpperCase()
  const ROUTE_BADGE = {
    CONTINUE: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
    PAUSE:    'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',
    STOP:     'bg-red-500/10 border-red-500/20 text-red-400',
    PIVOT:    'bg-orange-500/10 border-orange-500/20 text-orange-400',
  }

  return (
    <aside className="flex flex-col h-full bg-[#0f0f14] border-r border-white/5 text-white w-60 shrink-0 select-none">
      {/* Brand */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-white/5">
        <Link to="/dashboard" className="flex items-center gap-2" onClick={onClose}>
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">C</div>
          <span className="font-semibold text-sm tracking-tight">Changepreneurship</span>
        </Link>
        {onClose && (
          <button onClick={onClose} className="lg:hidden text-slate-400 hover:text-white">
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Venture context strip */}
      {venture && (
        <Link to="/venture-profile" onClick={onClose}
          className="flex flex-col gap-1 px-4 py-3 border-b border-white/5 hover:bg-white/[0.03] transition-colors group">
          <div className="flex items-center gap-1.5">
            <Activity className="h-3 w-3 text-slate-600 shrink-0" />
            <span className="text-[9px] font-bold text-slate-600 uppercase tracking-widest">Active Venture</span>
            {route && (
              <span className={`ml-auto text-[9px] font-bold px-1.5 py-0.5 rounded-full border shrink-0 ${ROUTE_BADGE[route] || 'bg-white/5 border-white/10 text-slate-400'}`}>
                {route}
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 leading-snug group-hover:text-slate-200 transition-colors truncate">
            {(venture.idea_clarified || venture.idea_raw || 'Untitled venture').slice(0, 50)}
          </p>
          {venture.status && (
            <span className="text-[9px] text-slate-600">{venture.status}</span>
          )}
        </Link>
      )}

      {/* Scrollable nav */}
      <nav className="flex-1 overflow-y-auto py-2 scrollbar-thin scrollbar-thumb-slate-700">
        {NAV_STRUCTURE.map((section) => {
          if (section.type === 'section') {
            return (
              <div key={section.label} className="mb-1">
                <div className="px-4 py-1.5">
                  <span className="text-[10px] font-semibold text-slate-500 tracking-widest uppercase">
                    {section.label}
                  </span>
                </div>
                {section.items.map(item => (
                  <NavItem
                    key={item.id}
                    item={item}
                    active={isActive(item.path)}
                    onClick={onClose}
                  />
                ))}
              </div>
            );
          }

          // Phase section
          const phaseNum  = section.phaseNumber;
          const accessible = isPhaseAccessible(phaseNum, gateStatus);
          const status    = gateStatus[String(phaseNum)];
          const pct       = phaseProgress[String(phaseNum)] ?? 0;
          const isOpen    = collapsed[section.phaseKey] !== true; // default open

          return (
            <div key={section.phaseKey} className="mb-1">
              {/* Phase header — clickable to collapse */}
              <button
                onClick={() => toggleCollapse(section.phaseKey)}
                className="w-full flex items-center gap-2 px-4 py-1.5 group"
              >
                <span className={`text-[10px] font-semibold tracking-widest uppercase flex-1 text-left ${accessible ? 'text-slate-400' : 'text-slate-600'}`}>
                  {section.label}
                </span>
                {phaseNum === 1 && Object.keys(gateStatus).length === 0 && (
                  <span className="text-[9px] font-bold text-indigo-400 bg-indigo-500/15 px-1.5 py-0.5 rounded-full mr-1 shrink-0">START</span>
                )}
                <PhaseStatusBadge status={status} accessible={accessible} pct={pct} />
                {isOpen
                  ? <ChevronDown className="h-3 w-3 text-slate-600 shrink-0" />
                  : <ChevronRight className="h-3 w-3 text-slate-600 shrink-0" />
                }
              </button>

              {/* Progress bar under phase header */}
              {accessible && pct > 0 && (
                <div className="px-4 mb-1">
                  <MiniProgress pct={pct} />
                </div>
              )}

              {/* Locked gate hint */}
              {isOpen && !accessible && (
                <p className="px-6 py-1 text-[10px] text-slate-700 italic">
                  {phaseGateHint(phaseNum, gateStatus) || `Locked`}
                </p>
              )}

              {/* Phase items */}
              {isOpen && section.items.map((item, idx) => {
                const itemAccessible = accessible || (idx === 0 && phaseNum === 1);
                return (
                  <NavItem
                    key={item.id}
                    item={item}
                    active={isActive(item.path)}
                    locked={!itemAccessible}
                    onClick={onClose}
                    indent
                  />
                );
              })}
            </div>
          );
        })}
      </nav>

      {/* Bottom actions */}
      <div className="border-t border-white/5 py-2">
        <NavItem
          item={{ label: 'Profile & Privacy', icon: Settings, path: '/profile' }}
          active={isActive('/profile')}
          onClick={onClose}
        />
        <NavItem
          item={{ label: 'Connected Accounts', icon: Link2, path: '/profile/connections' }}
          active={isActive('/profile/connections')}
          onClick={onClose}
        />
        <NavItem
          item={{ label: 'Account Settings', icon: KeyRound, path: '/settings/account' }}
          active={isActive('/settings/account')}
          onClick={onClose}
        />
        <button
          onClick={handleSignOut}
          className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors"
        >
          <LogOut className="h-4 w-4 shrink-0" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}

// ─── NavItem ──────────────────────────────────────────────────────────────────
function NavItem({ item, active, locked, onClick, indent }) {
  const { icon: Icon, label, path } = item;

  const base = 'w-full flex items-center gap-3 py-2 text-sm transition-colors rounded-sm';
  const px   = indent ? 'px-6' : 'px-4';

  if (locked) {
    return (
      <div className={`${base} ${px} text-slate-600 cursor-not-allowed`}>
        <Lock className="h-4 w-4 shrink-0" />
        <span>{label}</span>
      </div>
    );
  }

  return (
    <Link
      to={path}
      onClick={onClick}
      className={`${base} ${px} ${
        active
          ? 'bg-indigo-600/20 text-indigo-300 border-r-2 border-indigo-500'
          : 'text-slate-400 hover:bg-white/5 hover:text-white'
      }`}
    >
      <Icon className="h-4 w-4 shrink-0" />
      <span className="truncate">{label}</span>
    </Link>
  );
}

// ─── Phase status badge ───────────────────────────────────────────────────────
function PhaseStatusBadge({ status, accessible, pct }) {
  if (!accessible) {
    return <Lock className="h-3 w-3 text-slate-600 shrink-0" />;
  }
  if (status === 'COMPLETED') {
    return <CheckCircle2 className="h-3 w-3 text-emerald-500 shrink-0" />;
  }
  if (status === 'IN_PROGRESS' && pct > 0) {
    return <span className="text-[10px] text-indigo-400 font-medium shrink-0">{Math.round(pct)}%</span>;
  }
  return null;
}
