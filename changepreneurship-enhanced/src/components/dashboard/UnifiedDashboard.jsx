import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import apiService from '../../services/api'
import BlockerPanel from './BlockerPanel'
import {
  Loader2, RefreshCw, Zap, ArrowRight, Rocket,
  CheckCircle2, Brain, Target, TrendingUp, Sparkles,
  Lock, Play, ChevronRight,
  Lightbulb, Search, Building2, TestTube, Briefcase, FlaskConical,
  Activity, Tag, ShieldAlert,
} from 'lucide-react'

// ── Phase config ──────────────────────────────────────────────────────────────
const PHASE_CONFIG = [
  {
    id: 'self_discovery',
    label: 'Self Discovery',
    short: 'P1',
    num: 1,
    icon: Brain,
    color: 'indigo',
    path: '/assessment/entrepreneur-discovery',
    deliverable: 'Founder Readiness Profile',
    question: 'Are you ready to build?',
  },
  {
    id: 'idea_discovery',
    label: 'Idea Discovery',
    short: 'P2',
    num: 2,
    icon: Lightbulb,
    color: 'yellow',
    path: '/assessment/idea-discovery',
    deliverable: 'Clarified Venture Concept',
    question: 'Is the idea clear and testable?',
  },
  {
    id: 'market_research',
    label: 'Market Research',
    short: 'P3',
    num: 3,
    icon: Search,
    color: 'blue',
    path: '/assessment/market-research',
    deliverable: 'Market Validity Report',
    question: 'Does the world care?',
  },
  {
    id: 'business_pillars',
    label: 'Business Pillars',
    short: 'P4',
    num: 4,
    icon: Building2,
    color: 'purple',
    path: '/assessment/business-pillars',
    deliverable: 'Business Pillars Blueprint',
    question: 'Does the model hold together?',
  },
  {
    id: 'product_concept_testing',
    label: 'Concept Testing',
    short: 'P5',
    num: 5,
    icon: TestTube,
    color: 'pink',
    path: '/assessment/product-concept',
    deliverable: 'Product Concept Test Result',
    question: 'Do real people respond positively?',
  },
  {
    id: 'business_development',
    label: 'Business Development',
    short: 'P6',
    num: 6,
    icon: Briefcase,
    color: 'emerald',
    path: '/assessment/business-development',
    deliverable: 'Personalized Venture Environment',
    question: 'Can the venture actually function?',
  },
  {
    id: 'business_prototype_testing',
    label: 'Prototype Testing',
    short: 'P7',
    num: 7,
    icon: FlaskConical,
    color: 'orange',
    path: '/assessment/business-prototype',
    deliverable: 'Business Prototype Test Report',
    question: 'Does it work in the real world?',
  },
]

const COLOR_MAP = {
  indigo:  { bg: 'bg-indigo-500/10',  border: 'border-indigo-500/25',  text: 'text-indigo-400',  bar: 'bg-indigo-500',   ring: 'ring-indigo-500/30' },
  yellow:  { bg: 'bg-yellow-500/10',  border: 'border-yellow-500/25',  text: 'text-yellow-400',  bar: 'bg-yellow-500',   ring: 'ring-yellow-500/30' },
  blue:    { bg: 'bg-blue-500/10',    border: 'border-blue-500/25',    text: 'text-blue-400',    bar: 'bg-blue-500',     ring: 'ring-blue-500/30' },
  purple:  { bg: 'bg-purple-500/10',  border: 'border-purple-500/25',  text: 'text-purple-400',  bar: 'bg-purple-500',   ring: 'ring-purple-500/30' },
  pink:    { bg: 'bg-pink-500/10',    border: 'border-pink-500/25',    text: 'text-pink-400',    bar: 'bg-pink-500',     ring: 'ring-pink-500/30' },
  emerald: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/25', text: 'text-emerald-400', bar: 'bg-emerald-500',  ring: 'ring-emerald-500/30' },
  orange:  { bg: 'bg-orange-500/10',  border: 'border-orange-500/25',  text: 'text-orange-400',  bar: 'bg-orange-500',   ring: 'ring-orange-500/30' },
}

// phase_id → { path, num, label } — used to enrich next_action
const PHASE_ID_MAP = {}
PHASE_CONFIG.forEach(p => { PHASE_ID_MAP[p.id] = { path: p.path, num: p.num, label: p.label } })

// Status → label/color per CEO doc
const STATUS_META = {
  COMPLETED:   { label: 'Complete',          color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
  IN_PROGRESS: { label: 'In progress',       color: 'text-indigo-400',  bg: 'bg-indigo-500/10 border-indigo-500/20' },
  NOT_STARTED: { label: 'Not started',       color: 'text-slate-500',   bg: 'bg-white/5 border-white/5' },
  LOCKED:      { label: 'Locked',            color: 'text-slate-700',   bg: 'bg-transparent border-white/[0.03]' },
  BLOCKED:     { label: 'Blocked',           color: 'text-red-400',     bg: 'bg-red-500/10 border-red-500/20' },
}

// 5 key dimensions to surface in the dashboard health grid
// Must match backend _ALL_DIMENSIONS keys in venture_profile.py
const HEALTH_DIMS = ['financial_readiness', 'motivation_quality', 'time_capacity', 'founder_market_fit', 'legal_employment']

const STATUS_COLORS = {
  'Strong':     'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
  'Adequate':   'bg-sky-500/10 border-sky-500/20 text-sky-400',
  'Watch':      'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',
  'Soft Block': 'bg-orange-500/10 border-orange-500/20 text-orange-400',
  'Hard Block': 'bg-red-500/10 border-red-500/20 text-red-400',
  'Hard Stop':  'bg-red-700/15 border-red-700/30 text-red-300',
  'Unknown':    'bg-white/5 border-white/10 text-slate-500',
}

const STATUS_DOT = {
  'Strong':     'bg-emerald-500',
  'Adequate':   'bg-sky-400',
  'Watch':      'bg-yellow-400',
  'Soft Block': 'bg-orange-400',
  'Hard Block': 'bg-red-500',
  'Hard Stop':  'bg-red-700',
  'Unknown':    'bg-slate-600',
}

const ROUTE_COLOR = {
  CONTINUE: { badge: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400', bar: 'border-emerald-500/20 bg-emerald-500/[0.04]' },
  PAUSE:    { badge: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',   bar: 'border-yellow-500/20 bg-yellow-500/[0.04]' },
  STOP:     { badge: 'bg-red-500/10 border-red-500/20 text-red-400',            bar: 'border-red-500/20 bg-red-500/[0.04]' },
  PIVOT:    { badge: 'bg-orange-500/10 border-orange-500/20 text-orange-400',   bar: 'border-orange-500/20 bg-orange-500/[0.04]' },
}

const UnifiedDashboard = () => {
  const { user, isAuthenticated } = useAuth()
  const [phases, setPhases]       = useState([])
  const [nextAction, setNext]     = useState(null)
  const [blockers, setBlockers]   = useState([])
  const [aiReport, setAiReport]   = useState(null)
  const [venture, setVenture]     = useState(null)
  const [matrix, setMatrix]       = useState(null)
  const [phaseGates, setPhaseGates] = useState({})
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const [phaseRes, actionRes, blockerRes, aiRes, ventureRes, profileRes] = await Promise.allSettled([
        apiService.request('/v1/progress/phases'),
        apiService.request('/v1/progress/next-action'),
        apiService.request('/v1/progress/blockers'),
        apiService.request('/ai/insights-report'),
        apiService.request('/v1/ventures/active'),
        apiService.request('/v1/ventures/profile'),
      ])
      if (phaseRes.status === 'fulfilled')   setPhases(phaseRes.value.data?.phases || [])
      if (actionRes.status === 'fulfilled')  setNext(actionRes.value.data?.next_action || null)
      if (blockerRes.status === 'fulfilled') setBlockers(blockerRes.value.data?.blockers || [])
      if (aiRes.status === 'fulfilled' && aiRes.value.success) {
        setAiReport(aiRes.value.data?.report || null)
      }
      if (ventureRes.status === 'fulfilled') setVenture(ventureRes.value.data?.venture || null)
      if (profileRes.status === 'fulfilled' && profileRes.value.success) {
        setMatrix(profileRes.value.data?.founder_matrix || null)
        setPhaseGates(profileRes.value.data?.phase_gates || {})
      }
    } catch {
      setError('Could not load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { if (isAuthenticated) load() }, [isAuthenticated])

  // Merge config + live data
  const phaseMap = {}
  phases.forEach(p => { phaseMap[p.id] = p })

  const mergedPhases = PHASE_CONFIG.map((cfg, i) => {
    const live = phaseMap[cfg.id] || {}
    const prev = i > 0 ? phaseMap[PHASE_CONFIG[i - 1].id] : null
    const prevDone = i === 0 || (prev?.status === 'COMPLETED')
    const status = live.status || 'NOT_STARTED'
    const locked = !prevDone && status === 'NOT_STARTED'
    const gate = phaseGates[String(i + 1)] || null
    const prevPhaseName = i > 0 ? PHASE_CONFIG[i - 1].label : null
    return {
      ...cfg,
      status: locked ? 'LOCKED' : status,
      progress: live.progress_percentage ?? 0,
      responseCount: live.response_count ?? 0,
      locked,
      blockingReason: gate?.blocking_reason || null,
      prevPhaseName,
      prevPhaseInProgress: i > 0 && (prev?.status === 'IN_PROGRESS'),
    }
  })

  const completed = mergedPhases.filter(p => p.status === 'COMPLETED').length
  const inProgress = mergedPhases.filter(p => p.status === 'IN_PROGRESS').length
  const overallPct = Math.round((completed / 7) * 100)
  const activeBlockers = blockers.filter(b => !b.resolved_at)

  const entScore = aiReport?.entrepreneur?.score ?? null
  const venScore = aiReport?.venture?.score ?? null
  const aiScore  = entScore != null ? Math.round((entScore + (venScore ?? entScore)) / (venScore != null ? 2 : 1)) : null

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-full py-24">
        <p className="text-slate-400 text-sm">
          <Link to="/login" className="text-indigo-400 hover:text-indigo-300 underline">Sign in</Link> to view your journey
        </p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full py-24">
        <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
      </div>
    )
  }

  const route = (matrix?.recommended_route || 'CONTINUE').toUpperCase()
  const rc = ROUTE_COLOR[route] || ROUTE_COLOR.CONTINUE
  const healthDims = matrix?.dimensions
    ? HEALTH_DIMS.map(k => matrix.dimensions[k]).filter(Boolean)
    : []

  // Enrich nextAction with path + phase label derived from phase_id
  const enrichedAction = nextAction ? (() => {
    const phaseInfo = nextAction.phase_id ? PHASE_ID_MAP[nextAction.phase_id] : null
    return {
      title:     nextAction.action || nextAction.title || 'Continue your journey',
      desc:      nextAction.reason || nextAction.description,
      path:      phaseInfo?.path || nextAction.path,
      phaseNum:  phaseInfo?.num ?? null,
      priority:  nextAction.priority,
    }
  })() : null

  return (
    <div className="min-h-full bg-[#0a0a0f] px-4 py-6 max-w-4xl mx-auto space-y-5">

      {/* ── ONBOARDING HERO (new user, 0 phases started) ─── */}
      {completed === 0 && inProgress === 0 && !loading && (
        <div className="rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-500/[0.08] to-purple-500/[0.04] p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/15 flex items-center justify-center shrink-0">
              <Rocket className="h-6 w-6 text-indigo-400" />
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-lg font-bold text-white mb-1">Welcome to your journey</h2>
              <p className="text-sm text-slate-400 leading-relaxed mb-4">
                The Changepreneurship program guides you through <span className="text-white font-medium">7 phases</span> — from idea to validated business. Each phase takes 1–3 weeks and ends with a concrete deliverable. Start with Phase 1 to build your Founder Readiness Profile.
              </p>
              <Link
                to="/assessment/entrepreneur-discovery"
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl transition-colors"
              >
                <Play className="h-4 w-4" />
                Begin Phase 1: Self-Discovery
              </Link>
              <p className="text-xs text-slate-600 mt-2">Takes 60–90 min · Unlocks your Founder Readiness Profile</p>
            </div>
          </div>
        </div>
      )}

      {/* ── VENTURE COCKPIT HEADER ──────────────────── */}
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          {venture ? (
            <>
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${rc.badge}`}>{route}</span>
                {matrix?.overall_status_label && (
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${STATUS_COLORS[matrix.overall_status_label] || STATUS_COLORS.Unknown}`}>
                    {matrix.overall_status_label}
                  </span>
                )}
                {matrix?.burnout_signal && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-400">Burnout risk</span>
                )}
              </div>
              <h1 className="text-xl font-bold text-white leading-tight tracking-tight truncate" title={venture.idea_clarified || venture.idea_raw}>
                {(venture.idea_clarified || venture.idea_raw || 'Your Venture').slice(0, 60)}{(venture.idea_clarified || venture.idea_raw || '').length > 60 ? '…' : ''}
              </h1>
              <p className="text-xs text-slate-500 mt-0.5">
                {completed === 7 ? 'All 7 phases complete' : `${completed} of 7 phases complete`}
              </p>
            </>
          ) : (
            <>
              <h1 className="text-2xl font-bold text-white leading-tight tracking-tight">Venture Cockpit</h1>
              <p className="text-xs text-slate-500 mt-1">
                {completed === 0
                  ? 'Start Phase 1 to begin your venture-building journey'
                  : `${completed} of 7 phases complete`}
              </p>
            </>
          )}
        </div>
        <button onClick={load} disabled={loading} className="p-2 rounded-lg hover:bg-white/5 text-slate-600 hover:text-slate-300 transition-colors mt-0.5 shrink-0">
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {error && (
        <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
          {error}
        </div>
      )}

      {/* ── ROUTE BANNER (if matrix) ─────────────────── */}
      {matrix?.operating_recommendation && (
        <div className={`rounded-xl border px-4 py-3 ${rc.bar}`}>
          <div className="flex items-start gap-3">
            <Activity className="h-4 w-4 mt-0.5 shrink-0 opacity-70" style={{ color: 'inherit' }} />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-white mb-1">{route} — Operating Recommendation</p>
              <p className="text-xs text-slate-400 leading-relaxed">{matrix.operating_recommendation}</p>
              {matrix.pattern_tags?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {matrix.pattern_tags.map(tag => {
                    const isWarn = tag.toLowerCase().includes('risk') || tag.toLowerCase().includes('constraint') ||
                                   tag.toLowerCase().includes('watch') || tag.toLowerCase().includes('needed') ||
                                   tag.toLowerCase().includes('gap')
                    return (
                      <span key={tag} className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${
                        isWarn ? 'bg-orange-500/10 border-orange-500/20 text-orange-400' :
                        'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                      }`}>{tag}</span>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── FOUNDER HEALTH GRID ─────────────────────── */}
      {healthDims.length > 0 && (
        <div className="rounded-xl border border-white/5 bg-white/[0.02] px-4 py-3.5">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="h-3.5 w-3.5 text-slate-600" />
            <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">Founder Health</span>
            <Link to="/venture-profile" className="ml-auto text-[10px] text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-0.5">
              Full matrix <ChevronRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="grid grid-cols-1 gap-1.5">
            {healthDims.map((dim) => (
              <div key={dim.label} className="flex items-center gap-2 text-xs">
                <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${STATUS_DOT[dim.status_label] || 'bg-slate-600'}`} />
                <span className="text-slate-400 flex-1 truncate">{dim.label}</span>
                {dim.score != null && <span className="text-slate-600 tabular-nums w-7 text-right text-[11px]">{dim.score}</span>}
                <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full border shrink-0 ${STATUS_COLORS[dim.status_label] || STATUS_COLORS.Unknown}`}>
                  {dim.status_label}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── STATS ROW ───────────────────────────────── */}
      <div className="grid grid-cols-4 gap-3">
        <StatCard
          value={`${completed}/7`}
          label="Phases Done"
          sub={`${overallPct}% complete`}
          color="text-emerald-400"
          bg="bg-emerald-500/[0.06] border-emerald-500/15"
        />
        <StatCard
          value={aiScore != null ? aiScore : '—'}
          label="AI Score"
          sub={aiScore != null ? 'Combined readiness' : 'Complete P1 to unlock'}
          color="text-purple-400"
          bg="bg-purple-500/[0.06] border-purple-500/15"
        />
        <StatCard
          value={activeBlockers.length > 0 ? activeBlockers.length : '✓'}
          label="Blockers"
          sub={activeBlockers.length > 0 ? 'Need attention' : 'None active'}
          color={activeBlockers.length > 0 ? 'text-red-400' : 'text-emerald-400'}
          bg={activeBlockers.length > 0 ? 'bg-red-500/[0.06] border-red-500/15' : 'bg-white/[0.02] border-white/5'}
        />
        <StatCard
          value={inProgress > 0 ? inProgress : completed === 7 ? '✓' : '—'}
          label="Active"
          sub={inProgress > 0 ? 'Phase in progress' : completed === 7 ? 'Journey complete' : 'Start a phase'}
          color={inProgress > 0 ? 'text-indigo-400' : 'text-slate-500'}
          bg="bg-white/[0.02] border-white/5"
        />
      </div>

      {/* ── OVERALL PROGRESS BAR ────────────────────── */}
      <div className="rounded-xl border border-white/5 bg-white/[0.02] p-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Journey Progress</span>
          <span className="text-sm font-bold text-white tabular-nums">{overallPct}%</span>
        </div>
        {/* Phase segment bar */}
        <div className="flex gap-0.5 h-2 rounded-full overflow-hidden mb-3">
          {PHASE_CONFIG.map((cfg, i) => {
            const ph = mergedPhases[i]
            const c = COLOR_MAP[cfg.color]
            return (
              <div key={cfg.id} className="flex-1 rounded-sm overflow-hidden bg-white/[0.04]">
                {ph.status === 'COMPLETED' ? (
                  <div className={`h-full w-full ${c.bar} opacity-80`} />
                ) : ph.status === 'IN_PROGRESS' ? (
                  <div className={`h-full ${c.bar} opacity-60 transition-all`} style={{ width: `${ph.progress}%` }} />
                ) : null}
              </div>
            )
          })}
        </div>
        {/* Phase dots timeline */}
        <div className="flex items-center justify-between">
          {mergedPhases.map((ph) => {
            const c = COLOR_MAP[ph.color]
            return (
              <div key={ph.id} className="flex flex-col items-center gap-1">
                <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold border ${
                  ph.status === 'COMPLETED' ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400' :
                  ph.status === 'IN_PROGRESS' ? `${c.bg} ${c.border} ${c.text}` :
                  ph.status === 'LOCKED' ? 'bg-transparent border-white/[0.04] text-slate-800' :
                  'bg-white/[0.03] border-white/10 text-slate-600'
                }`}>
                  {ph.status === 'COMPLETED' ? '✓' : ph.num}
                </div>
                <span className={`text-[9px] font-medium ${
                  ph.status === 'COMPLETED' ? 'text-emerald-500/60' :
                  ph.status === 'IN_PROGRESS' ? c.text :
                  'text-slate-700'
                }`}>{ph.short}</span>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── BLOCKERS ────────────────────────────────── */}
      {activeBlockers.length > 0 && (
        <BlockerPanel blockers={activeBlockers} />
      )}

      {/* ── NEXT ACTION ─────────────────────────────── */}
      {enrichedAction && (
        <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/[0.05] p-4">
          <div className="flex items-center gap-2 mb-1.5">
            <Zap className="h-3.5 w-3.5 text-indigo-400" />
            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Next Step</span>
            {enrichedAction.priority === 'CRITICAL' && (
              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-400">CRITICAL</span>
            )}
          </div>
          <p className="text-base font-bold text-white">{enrichedAction.title}</p>
          {enrichedAction.desc && (
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">{enrichedAction.desc}</p>
          )}
          {enrichedAction.phaseNum != null && enrichedAction.phaseNum < 7 && (
            <p className="text-[11px] text-slate-600 mt-1.5">
              Unlocks Phase {enrichedAction.phaseNum + 1}: {PHASE_CONFIG[enrichedAction.phaseNum]?.label}
            </p>
          )}
          {enrichedAction.path && (
            <Link to={enrichedAction.path}
              className="inline-flex items-center gap-1.5 mt-3 text-xs bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 rounded-lg px-3 py-1.5 font-medium transition-colors">
              Go there <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          )}
        </div>
      )}

      {/* ── AI + ROADMAP ────────────────────────────── */}
      <div className="grid grid-cols-2 gap-3">
        <Link to="/ai-insights"
          className="rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] p-4 transition-colors group">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-purple-500/10 flex items-center justify-center">
                <Brain className="h-3.5 w-3.5 text-purple-400" />
              </div>
              <span className="text-xs font-bold text-white">AI Insights</span>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-slate-700 group-hover:text-slate-400 transition-colors" />
          </div>
          {aiScore != null ? (
            <>
              <div className="flex items-baseline gap-1 mb-2">
                <span className="text-3xl font-black text-purple-400 leading-none tabular-nums">{aiScore}</span>
                <span className="text-xs text-slate-500">/100</span>
              </div>
              <div className="flex gap-3 text-xs text-slate-500 mb-2">
                {entScore != null && <span>Founder <span className="text-white font-semibold">{entScore}</span></span>}
                {venScore != null && <span>Venture <span className="text-white font-semibold">{venScore}</span></span>}
              </div>
              <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-purple-500 to-indigo-500" style={{ width: `${aiScore}%` }} />
              </div>
            </>
          ) : (
            <p className="text-xs text-slate-600 flex items-center gap-1.5 mt-1">
              <Sparkles className="h-3 w-3" /> Complete Phase 1 to unlock AI analysis
            </p>
          )}
        </Link>

        <Link to="/venture-profile"
          className="rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] p-4 transition-colors group">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <Target className="h-3.5 w-3.5 text-emerald-400" />
              </div>
              <span className="text-xs font-bold text-white">Venture Profile</span>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-slate-700 group-hover:text-slate-400 transition-colors" />
          </div>
          {venture ? (
            <>
              <span className={`inline-block text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wide border mb-2 ${
                venture.status === 'VALIDATED' ? 'bg-emerald-500/15 border-emerald-500/25 text-emerald-400' :
                venture.status === 'ACTIVE'    ? 'bg-indigo-500/15 border-indigo-500/25 text-indigo-400' :
                'bg-white/5 border-white/10 text-slate-400'
              }`}>
                {venture.status || 'DRAFT'}
              </span>
              <p className="text-xs text-slate-400 leading-snug line-clamp-2">
                {venture.idea_clarified?.slice(0, 70) || venture.idea_raw?.slice(0, 70) || 'Active venture'}
              </p>
            </>
          ) : (
            <p className="text-xs text-slate-600 flex items-center gap-1.5 mt-1">
              <TrendingUp className="h-3 w-3" /> Complete Idea Discovery first
            </p>
          )}
        </Link>
      </div>

      {/* ── 7-PHASE CARDS ───────────────────────────── */}
      <div>
        <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-3">7-Phase Journey</p>
        <div className="space-y-2">
          {mergedPhases.map((phase) => (
            <PhaseCard key={phase.id} phase={phase} isNextUp={completed === 0 && inProgress === 0 && phase.num === 1} />
          ))}
        </div>
      </div>

    </div>
  )
}

// ── StatCard ──────────────────────────────────────────────────────────────────
const StatCard = ({ value, label, sub, color, bg }) => (
  <div className={`rounded-xl border ${bg} p-3`}>
    <div className={`text-xl font-black tabular-nums leading-none mb-1 ${color}`}>{value}</div>
    <div className="text-[11px] font-semibold text-slate-300">{label}</div>
    <div className="text-[10px] text-slate-600 mt-0.5 leading-tight">{sub}</div>
  </div>
)

// ── PhaseCard ─────────────────────────────────────────────────────────────────
const PhaseCard = ({ phase, isNextUp = false }) => {
  const c = COLOR_MAP[phase.color]
  const Icon = phase.icon
  const isDone    = phase.status === 'COMPLETED'
  const isActive  = phase.status === 'IN_PROGRESS'
  const isLocked  = phase.status === 'LOCKED'
  const isReady   = phase.status === 'NOT_STARTED' && !isLocked
  const sm = STATUS_META[phase.status] || STATUS_META.NOT_STARTED

  // Lock hint: blocking reason from gate, or "finish prev phase" text
  const lockHint = phase.blockingReason
    || (phase.prevPhaseInProgress ? `${phase.prevPhaseName} in progress` : null)
    || (phase.prevPhaseName ? `Complete ${phase.prevPhaseName} first` : null)

  const inner = (
    <div className={`rounded-xl border transition-all duration-200 overflow-hidden ${
      isLocked ? 'border-white/[0.03] bg-transparent opacity-40 cursor-not-allowed' :
      isDone   ? 'border-emerald-500/15 bg-emerald-500/[0.025] hover:bg-emerald-500/[0.05]' :
      isActive ? `${c.border} ${c.bg} hover:bg-white/[0.04]` :
      isNextUp ? 'border-indigo-500/40 bg-indigo-500/[0.06] hover:bg-indigo-500/[0.10] ring-1 ring-indigo-500/20' :
                 'border-white/5 bg-white/[0.015] hover:bg-white/[0.035]'
    }`}>
      <div className="flex items-center gap-3 px-4 py-3.5">

        {/* Phase number circle */}
        <div className={`relative w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 border ${
          isDone   ? 'bg-emerald-500/15 border-emerald-500/25' :
          isActive ? `${c.bg} ${c.border}` :
          isLocked ? 'bg-transparent border-white/[0.04]' :
                     'bg-white/[0.03] border-white/8'
        }`}>
          {isDone
            ? <CheckCircle2 className="h-4.5 w-4.5 text-emerald-400" />
            : isLocked
            ? <Lock className="h-3.5 w-3.5 text-slate-800" />
            : <Icon className={`h-4 w-4 ${isActive ? c.text : isReady ? 'text-slate-400' : 'text-slate-600'}`} />
          }
          {isActive && (
            <span className={`absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full ${c.bar} border-2 border-[#0a0a0f] animate-pulse`} />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className={`text-[10px] font-bold uppercase tracking-widest ${isLocked ? 'text-slate-800' : 'text-slate-600'}`}>
              Phase {phase.num}
            </span>
            <span className={`text-[9px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded-full border ${sm.bg} ${sm.color}`}>
              {sm.label}
            </span>
          </div>
          <p className={`text-sm font-bold leading-tight ${
            isDone ? 'text-emerald-200' : isActive ? 'text-white' : isLocked ? 'text-slate-800' : 'text-slate-200'
          }`}>{phase.label}</p>
          <p className={`text-[10px] mt-0.5 ${isLocked ? 'text-slate-800' : 'text-slate-600'}`}>
            {phase.deliverable}
          </p>

          {/* Lock hint */}
          {isLocked && lockHint && (
            <p className="text-[10px] text-slate-700 italic mt-1">{lockHint}</p>
          )}

          {/* Progress bar (active only) */}
          {isActive && phase.progress > 0 && (
            <div className="mt-2 flex items-center gap-2">
              <div className="flex-1 h-1 rounded-full bg-white/[0.06] overflow-hidden">
                <div className={`h-full rounded-full ${c.bar} transition-all duration-700`}
                  style={{ width: `${Math.max(4, phase.progress)}%` }} />
              </div>
              <span className={`text-[10px] font-bold tabular-nums ${c.text}`}>{phase.progress}%</span>
            </div>
          )}
        </div>

        {/* Right side */}
        <div className="flex-shrink-0 flex flex-col items-end gap-1">
          {isDone ? (
            <span className="text-xs font-bold text-emerald-400">100%</span>
          ) : isActive ? (
            <span className={`text-sm font-black tabular-nums ${c.text}`}>{phase.progress}%</span>
          ) : isLocked ? (
            <Lock className="h-3 w-3 text-slate-800" />
          ) : isNextUp ? (
            <span className="text-xs font-bold text-indigo-400 flex items-center gap-1">
              Start <ArrowRight className="h-3 w-3" />
            </span>
          ) : (
            <span className="text-[10px] text-slate-600 flex items-center gap-0.5">
              <Play className="h-2.5 w-2.5" /> Start
            </span>
          )}
          {!isLocked && !isNextUp && (
            <ChevronRight className={`h-3.5 w-3.5 ${isDone ? 'text-emerald-700/50' : 'text-slate-700'}`} />
          )}
        </div>
      </div>

      {/* Active bottom accent */}
      {isActive && (
        <div className="h-0.5 bg-gradient-to-r from-transparent via-current to-transparent opacity-40 transition-all"
          style={{ width: `${phase.progress}%`, color: 'inherit' }}
        />
      )}
    </div>
  )

  return isLocked ? inner : <Link to={phase.path}>{inner}</Link>
}

export default UnifiedDashboard
