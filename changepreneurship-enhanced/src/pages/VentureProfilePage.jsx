/**
 * Venture Profile Page — Sprint 14 / Sprint 16
 * Cross-phase synthesis: venture identity + Founder Operating Matrix + all 7 deliverables
 */
import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import apiService from '../services/api'
import {
  Loader2, RefreshCw, ArrowLeft,
  Brain, Lightbulb, Search, Building2, TestTube, Briefcase, FlaskConical,
  CheckCircle2, Lock, ChevronRight, ExternalLink,
  Target, TrendingUp, AlertTriangle, Zap, Tag, BarChart3, MessageSquare,
  ShieldAlert, Shield, Activity, Sparkles,
} from 'lucide-react'

// ── Status label colors (CEO doc: Strong/Adequate/Watch/Soft Block/Hard Block/Hard Stop) ──
const STATUS_COLORS = {
  'Strong':     'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
  'Adequate':   'bg-sky-500/10 border-sky-500/20 text-sky-400',
  'Watch':      'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',
  'Soft Block': 'bg-orange-500/10 border-orange-500/20 text-orange-400',
  'Hard Block': 'bg-red-500/10 border-red-500/20 text-red-400',
  'Hard Stop':  'bg-red-700/15 border-red-700/30 text-red-300 font-extrabold',
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

// ── Phase config ──────────────────────────────────────────────────────────────
const PHASES = [
  {
    num: 1, key: 'phase1', icon: Brain, color: 'indigo',
    label: 'Self Discovery', deliverable: 'Founder Readiness Profile',
    path: '/assessment/entrepreneur-discovery',
    render: (d) => d ? (
      <div className="space-y-2">
        <div className="flex items-center gap-2 flex-wrap">
          <FounderTypeBadge type={d.founder_type} />
          <RouteBadge route={d.recommended_route} />
          {d.burnout_signal && <WarnBadge label="Burnout risk" />}
          {d.overload_signal && <WarnBadge label="Overload risk" />}
        </div>
        {d.active_blockers?.length > 0 && (
          <p className="text-[11px] text-red-400">{d.active_blockers.length} active blocker{d.active_blockers.length > 1 ? 's' : ''}</p>
        )}
      </div>
    ) : null,
  },
  {
    num: 2, key: null, icon: Lightbulb, color: 'yellow',
    label: 'Idea Discovery', deliverable: 'Clarified Venture Concept',
    path: '/assessment/idea-discovery',
    render: (_, venture) => venture?.idea_clarified ? (
      <p className="text-xs text-slate-300 leading-relaxed line-clamp-3">{venture.idea_clarified}</p>
    ) : null,
  },
  {
    num: 3, key: 'phase3', icon: Search, color: 'blue',
    label: 'Market Research', deliverable: 'Market Validity Report',
    path: '/assessment/market-research',
    render: (d) => d ? (
      <div className="space-y-1.5">
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-black text-blue-400 tabular-nums">{d.validity_score}</span>
          <span className="text-xs text-slate-500">/ 100 validity</span>
          <VerdictBadge verdict={d.verdict} />
        </div>
        {d.market_data?.market_size && (
          <p className="text-[11px] text-slate-500">Market: {d.market_data.market_size}</p>
        )}
      </div>
    ) : null,
  },
  {
    num: 4, key: 'phase4', icon: Building2, color: 'purple',
    label: 'Business Pillars', deliverable: 'Business Pillars Blueprint',
    path: '/assessment/business-pillars',
    render: (d) => d ? (
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-black text-purple-400 tabular-nums">{d.coherence_score}</span>
        <span className="text-xs text-slate-500">/ 100 coherence</span>
        {d.ready_for_concept_testing && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-bold">Ready</span>
        )}
      </div>
    ) : null,
  },
  {
    num: 5, key: 'phase5', icon: TestTube, color: 'pink',
    label: 'Concept Testing', deliverable: 'Product Concept Test Result',
    path: '/assessment/product-concept',
    render: (d) => d ? (
      <div className="flex items-center gap-2 flex-wrap">
        <SignalBadge signal={d.adoption_signal} />
        <DecisionBadge decision={d.decision} />
      </div>
    ) : null,
  },
  {
    num: 6, key: 'phase6', icon: Briefcase, color: 'emerald',
    label: 'Business Development', deliverable: 'Personalized Venture Environment',
    path: '/assessment/business-development',
    render: (d) => d ? (
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-black text-emerald-400 tabular-nums">{d.readiness_score}</span>
        <span className="text-xs text-slate-500">/ 100 readiness</span>
        {d.operational_ready && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-bold">Operational</span>
        )}
      </div>
    ) : null,
  },
  {
    num: 7, key: 'phase7', icon: FlaskConical, color: 'orange',
    label: 'Prototype Testing', deliverable: 'Business Prototype Test Report',
    path: '/assessment/business-prototype',
    render: (d) => d ? (
      <div className="space-y-1.5">
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-black text-orange-400 tabular-nums">{d.scale_score}</span>
          <span className="text-xs text-slate-500">/ 100 scale</span>
          <SignalBadge signal={d.scale_readiness} />
        </div>
        <DecisionBadge decision={d.decision} />
      </div>
    ) : null,
  },
]

const COLOR_MAP = {
  indigo:  { bg: 'bg-indigo-500/10',  border: 'border-indigo-500/25',  text: 'text-indigo-400' },
  yellow:  { bg: 'bg-yellow-500/10',  border: 'border-yellow-500/25',  text: 'text-yellow-400' },
  blue:    { bg: 'bg-blue-500/10',    border: 'border-blue-500/25',    text: 'text-blue-400' },
  purple:  { bg: 'bg-purple-500/10',  border: 'border-purple-500/25',  text: 'text-purple-400' },
  pink:    { bg: 'bg-pink-500/10',    border: 'border-pink-500/25',    text: 'text-pink-400' },
  emerald: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/25', text: 'text-emerald-400' },
  orange:  { bg: 'bg-orange-500/10',  border: 'border-orange-500/25',  text: 'text-orange-400' },
}

// ─── Page ─────────────────────────────────────────────────────────────────────
export default function VentureProfilePage() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const res = await apiService.request('/v1/ventures/profile')
      if (res.success) setProfile(res.data)
      else setError('Could not load venture profile')
    } catch {
      setError('Could not load venture profile')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const venture      = profile?.venture
  const deliverables = profile?.deliverables || {}
  const market       = profile?.market || {}
  const matrix       = profile?.founder_matrix

  const phase2Done   = !!venture?.idea_clarified
  const dKeys        = ['phase1', 'phase3', 'phase4', 'phase5', 'phase6', 'phase7']
  const doneCount    = dKeys.filter(k => deliverables[k] != null).length + (phase2Done ? 1 : 0)

  return (
    <div className="min-h-full bg-[#0a0a0f] px-4 py-6 max-w-3xl mx-auto">

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Link to="/dashboard" className="p-1.5 rounded-lg hover:bg-white/5 text-slate-600 hover:text-slate-300 transition-colors">
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <h1 className="text-xl font-bold text-white leading-tight">Venture Profile</h1>
            <p className="text-xs text-slate-500 mt-0.5">{doneCount} of 7 deliverables complete</p>
          </div>
        </div>
        <button onClick={load} disabled={loading}
          className="p-2 rounded-lg hover:bg-white/5 text-slate-600 hover:text-slate-300 transition-colors">
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-24">
          <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
        </div>
      )}

      {error && !loading && (
        <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 mb-4">
          <AlertTriangle className="h-4 w-4 shrink-0" /> {error}
        </div>
      )}

      {!loading && !error && (
        <div className="space-y-4">

          {/* ── Venture Identity Hero ─────────────────────────────── */}
          <VentureHero venture={venture} market={market} />

          {/* ── Founder Operating Matrix ─────────────────────────── */}
          {matrix && <FounderOperatingMatrix matrix={matrix} />}

          {/* ── Value Zone ───────────────────────────────────────── */}
          {matrix && <ValueZonePanel matrix={matrix} />}

          {/* ── Evidence Quality ─────────────────────────────────── */}
          {market.evidence_count > 0 && <EvidenceCard market={market} />}

          {/* ── Phase Deliverables ───────────────────────────────── */}
          <div>
            <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-3">Phase Deliverables</p>
            <div className="space-y-2">
              {PHASES.map((phase) => {
                const deliverable = phase.key ? deliverables[phase.key] : null
                const isPhase2    = phase.num === 2
                const hasData     = isPhase2 ? phase2Done : deliverable != null
                const c = COLOR_MAP[phase.color]
                const Icon = phase.icon

                return (
                  <div key={phase.num}
                    className={`rounded-xl border ${hasData ? `${c.border} bg-white/[0.025]` : 'border-white/5 bg-white/[0.01]'} overflow-hidden`}>
                    <div className="flex items-start gap-3 px-4 py-3.5">
                      <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 border mt-0.5 ${hasData ? `${c.bg} ${c.border}` : 'bg-white/[0.02] border-white/5'}`}>
                        {hasData ? <Icon className={`h-4 w-4 ${c.text}`} /> : <Lock className="h-3.5 w-3.5 text-slate-700" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] font-bold text-slate-600 uppercase tracking-wider">Phase {phase.num}</span>
                          {hasData
                            ? <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-bold">COMPLETE</span>
                            : <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-white/5 border border-white/5 text-slate-600 font-bold">PENDING</span>
                          }
                        </div>
                        <p className={`text-sm font-bold leading-tight mb-0.5 ${hasData ? 'text-white' : 'text-slate-600'}`}>{phase.label}</p>
                        <p className={`text-[10px] mb-2 ${hasData ? 'text-slate-500' : 'text-slate-700'}`}>{phase.deliverable}</p>
                        {hasData && <div>{phase.render(deliverable, venture)}</div>}
                        {!hasData && (
                          <Link to={phase.path} className={`inline-flex items-center gap-1 text-[11px] ${c.text} hover:opacity-80 transition-opacity font-medium`}>
                            Start Phase {phase.num} <ChevronRight className="h-3 w-3" />
                          </Link>
                        )}
                      </div>
                      {hasData && (
                        <Link to={phase.path} className="text-slate-700 hover:text-slate-400 transition-colors mt-1 shrink-0">
                          <ExternalLink className="h-3.5 w-3.5" />
                        </Link>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

        </div>
      )}
    </div>
  )
}

// ─── Venture Hero ─────────────────────────────────────────────────────────────
function VentureHero({ venture, market }) {
  if (!venture) {
    return (
      <div className="rounded-xl border border-white/5 bg-white/[0.02] p-5 text-center">
        <div className="w-10 h-10 rounded-full bg-yellow-500/10 border border-yellow-500/20 flex items-center justify-center mx-auto mb-3">
          <Lightbulb className="h-5 w-5 text-yellow-400" />
        </div>
        <p className="text-sm font-bold text-white mb-1">No venture started yet</p>
        <p className="text-xs text-slate-500 mb-4">Complete Phase 1 then begin Idea Discovery to define your venture</p>
        <Link to="/assessment/entrepreneur-discovery"
          className="inline-flex items-center gap-2 text-xs bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 rounded-lg px-3 py-1.5 font-medium transition-colors">
          <Zap className="h-3 w-3" /> Start Phase 1
        </Link>
      </div>
    )
  }

  const STATUS_COLOR = {
    DRAFT:       'bg-slate-500/10 border-slate-500/20 text-slate-400',
    CLARIFIED:   'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',
    VALIDATED:   'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
    TESTING:     'bg-blue-500/10 border-blue-500/20 text-blue-400',
    OPERATIONAL: 'bg-purple-500/10 border-purple-500/20 text-purple-400',
  }

  return (
    <div className="rounded-xl border border-white/5 bg-white/[0.02] p-5">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-yellow-500/10 border border-yellow-500/20 flex items-center justify-center">
            <Target className="h-4 w-4 text-yellow-400" />
          </div>
          <div>
            <span className={`text-[10px] font-bold uppercase tracking-wide px-2 py-0.5 rounded-full border ${STATUS_COLOR[venture.status] || STATUS_COLOR.DRAFT}`}>
              {venture.status}
            </span>
            {venture.type && <span className="ml-2 text-[10px] text-slate-600">{venture.type}</span>}
          </div>
        </div>
        {market.evidence_count > 0 && (
          <span className="text-[10px] text-slate-500 flex items-center gap-1">
            <TrendingUp className="h-3 w-3" /> {market.evidence_count} evidence item{market.evidence_count !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {venture.idea_clarified && (
        <p className="text-sm font-bold text-white leading-snug mb-3">{venture.idea_clarified}</p>
      )}
      {!venture.idea_clarified && venture.idea_raw && (
        <p className="text-sm text-slate-400 leading-snug mb-3 italic">"{venture.idea_raw}"</p>
      )}

      <div className="grid grid-cols-1 gap-2">
        {venture.problem_statement && <FieldRow label="Problem" value={venture.problem_statement} />}
        {venture.target_user_hypothesis && <FieldRow label="Target user" value={venture.target_user_hypothesis} />}
        {venture.value_proposition && <FieldRow label="Value prop" value={venture.value_proposition} />}
        {market.target_segment && <FieldRow label="Market segment" value={market.target_segment} />}
        {market.pain_intensity && <FieldRow label="Pain intensity" value={<PainBadge intensity={market.pain_intensity} />} />}
      </div>
    </div>
  )
}

// ─── Founder Operating Matrix ─────────────────────────────────────────────────
function FounderOperatingMatrix({ matrix }) {
  const dims = matrix.dimensions || {}
  const tags = matrix.pattern_tags || []
  const route = (matrix.recommended_route || 'CONTINUE').toUpperCase()

  const ROUTE_COLOR = {
    CONTINUE: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
    PAUSE:    'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',
    STOP:     'bg-red-500/10 border-red-500/20 text-red-400',
    PIVOT:    'bg-orange-500/10 border-orange-500/20 text-orange-400',
  }

  return (
    <div className="rounded-xl border border-indigo-500/15 bg-indigo-500/[0.03] overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-indigo-400" />
          <span className="text-sm font-bold text-white">Founder Operating Matrix</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${ROUTE_COLOR[route] || 'bg-white/5 border-white/10 text-slate-400'}`}>
            {route}
          </span>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${STATUS_COLORS[matrix.overall_status_label]}`}>
            {matrix.overall_status_label}
          </span>
        </div>
      </div>

      {/* Operating recommendation */}
      {matrix.operating_recommendation && (
        <div className="px-4 py-2.5 border-b border-white/5 bg-white/[0.01]">
          <p className="text-xs text-slate-400 leading-relaxed">{matrix.operating_recommendation}</p>
        </div>
      )}

      {/* Dimensions grid */}
      <div className="px-4 py-3">
        <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-2.5">13 Dimensions</p>
        <div className="grid grid-cols-1 gap-y-1.5">
          {Object.entries(dims).map(([key, dim]) => (
            <DimRow key={key} name={dim.label || key} score={dim.score} statusLabel={dim.status_label} />
          ))}
        </div>
      </div>

      {/* Pattern tags */}
      {tags.length > 0 && (
        <div className="px-4 pb-3 border-t border-white/5 pt-3">
          <div className="flex items-center gap-1.5 mb-2">
            <Tag className="h-3 w-3 text-slate-600" />
            <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">Pattern Tags</p>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {tags.map(tag => (
              <PatternTag key={tag} tag={tag} />
            ))}
          </div>
        </div>
      )}

      {/* Blockers */}
      {matrix.active_blockers?.length > 0 && (
        <div className="px-4 pb-3 border-t border-white/5 pt-3">
          <div className="flex items-center gap-1.5 mb-2">
            <ShieldAlert className="h-3 w-3 text-red-500" />
            <p className="text-[10px] font-bold text-red-500 uppercase tracking-widest">
              {matrix.active_blockers.length} Active Blocker{matrix.active_blockers.length > 1 ? 's' : ''}
            </p>
          </div>
          {matrix.active_blockers.slice(0, 3).map((b, i) => (
            <p key={i} className="text-[11px] text-red-400 mt-0.5">• {typeof b === 'string' ? b : b.description || JSON.stringify(b)}</p>
          ))}
        </div>
      )}

      {/* AI Narrative */}
      {matrix.ai_narrative && (
        <div className="px-4 pb-3 border-t border-white/5 pt-3">
          <div className="flex items-center gap-1.5 mb-2">
            <MessageSquare className="h-3 w-3 text-indigo-400" />
            <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">AI Narrative</p>
            {matrix.ai_confidence && (
              <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-slate-500 font-bold ml-auto">
                {matrix.ai_confidence} confidence
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">{matrix.ai_narrative}</p>
        </div>
      )}
    </div>
  )
}

// ─── Evidence Card ────────────────────────────────────────────────────────────
function EvidenceCard({ market }) {
  const bd     = market.evidence_by_strength || {}
  const strong = (bd.DIRECT || 0) + (bd.BEHAVIORAL || 0)
  const weak   = (bd.BELIEF || 0) + (bd.OPINION || 0) + (bd.AI_RESEARCH || 0)
  const qs     = market.evidence_quality_score ?? 0

  const barColor = qs >= 70 ? 'bg-emerald-500' : qs >= 40 ? 'bg-yellow-500' : 'bg-red-500'

  return (
    <div className="rounded-xl border border-white/5 bg-white/[0.02] px-4 py-3.5">
      <div className="flex items-center gap-2 mb-3">
        <BarChart3 className="h-4 w-4 text-slate-500" />
        <span className="text-sm font-bold text-white">Evidence Quality</span>
        <span className="ml-auto text-xs font-bold text-slate-400 tabular-nums">{qs} / 100</span>
      </div>
      <div className="h-1.5 rounded-full bg-white/5 mb-3">
        <div className={`h-full rounded-full ${barColor} transition-all`} style={{ width: `${qs}%` }} />
      </div>
      <div className="grid grid-cols-3 gap-2">
        {[
          { label: 'Direct / Behavioral', count: strong, color: 'text-emerald-400' },
          { label: 'Desk / Indirect',     count: (bd.DESK_RESEARCH || 0) + (bd.INDIRECT || 0), color: 'text-yellow-400' },
          { label: 'Belief / Opinion',    count: weak,   color: 'text-slate-500' },
        ].map(({ label, count, color }) => (
          <div key={label} className="text-center">
            <p className={`text-lg font-black ${color} tabular-nums`}>{count}</p>
            <p className="text-[10px] text-slate-600 leading-tight">{label}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Small components ─────────────────────────────────────────────────────────
const FieldRow = ({ label, value }) => (
  <div className="flex gap-3 text-xs">
    <span className="text-slate-600 shrink-0 w-24">{label}</span>
    <span className="text-slate-300 leading-snug">{value}</span>
  </div>
)

const DimRow = ({ name, score, statusLabel }) => {
  const dotClass = STATUS_DOT[statusLabel] || 'bg-slate-600'
  const labelClass = STATUS_COLORS[statusLabel] || 'bg-white/5 border-white/10 text-slate-500'
  return (
    <div className="flex items-center gap-2 text-xs">
      <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${dotClass}`} />
      <span className="text-slate-400 flex-1 truncate">{name}</span>
      {score != null && (
        <span className="text-slate-600 tabular-nums w-8 text-right">{score}</span>
      )}
      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full border shrink-0 ${labelClass}`}>
        {statusLabel}
      </span>
    </div>
  )
}

const PatternTag = ({ tag }) => {
  const isWarning = tag.includes('risk') || tag.includes('constraint') || tag.includes('gap') ||
                    tag.includes('watch') || tag.includes('needed') || tag.includes('Stop')
  return (
    <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${
      isWarning ? 'bg-orange-500/10 border-orange-500/20 text-orange-400' :
      'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
    }`}>{tag}</span>
  )
}

const WarnBadge    = ({ label }) => <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 font-bold">{label}</span>
const FounderTypeBadge = ({ type }) => type ? <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300">Type {type}</span> : null
const RouteBadge = ({ route }) => {
  const color = { CONTINUE: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400', PAUSE: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400', STOP: 'bg-red-500/10 border-red-500/20 text-red-400', PIVOT: 'bg-orange-500/10 border-orange-500/20 text-orange-400' }[route] || 'bg-white/5 border-white/10 text-slate-400'
  return <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${color}`}>{route}</span>
}
const VerdictBadge = ({ verdict }) => {
  if (!verdict) return null
  const color = { STRONG: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400', MODERATE: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400', WEAK: 'bg-orange-500/10 border-orange-500/20 text-orange-400', PROCEED: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400', PROMISING: 'bg-blue-500/10 border-blue-500/20 text-blue-400' }[verdict] || 'bg-white/5 border-white/10 text-slate-400'
  return <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${color}`}>{verdict}</span>
}
const SignalBadge = ({ signal }) => {
  if (!signal) return null
  const color = { STRONG: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400', MODERATE: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400', WEAK: 'bg-orange-500/10 border-orange-500/20 text-orange-400', NONE: 'bg-red-500/10 border-red-500/20 text-red-400' }[signal] || 'bg-white/5 border-white/10 text-slate-400'
  return <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${color}`}>{signal}</span>
}
const DecisionBadge = ({ decision }) => {
  if (!decision) return null
  const isPos = ['PROCEED', 'SCALE_CAREFULLY', 'REMAIN_STABLE'].includes(decision)
  return <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${isPos ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-orange-500/10 border-orange-500/20 text-orange-400'}`}>{decision.replace(/_/g, ' ')}</span>
}
const PainBadge = ({ intensity }) => {
  const color = { HIGH: 'text-red-400', CRITICAL: 'text-red-300', MEDIUM: 'text-yellow-400', LOW: 'text-slate-400' }[intensity] || 'text-slate-400'
  return <span className={`font-bold ${color}`}>{intensity}</span>
}

// ─── Value Zone Panel ──────────────────────────────────────────────────────────
// Shows the intersection of Skills × Passion × Idea Fit from Phase 1 dimensions.
function ValueZonePanel({ matrix }) {
  const dims = matrix.dimensions || {}

  const ZONE_DIMS = [
    {
      key: 'skills_experience',
      label: 'Skills & Experience',
      subtitle: 'What you are capable of doing',
      accentBg: 'bg-blue-500/10',
      accentBorder: 'border-blue-500/20',
      accentText: 'text-blue-400',
      barColor: 'bg-blue-500',
    },
    {
      key: 'motivation_quality',
      label: 'Passion & Motivation',
      subtitle: 'Why you want to do this',
      accentBg: 'bg-pink-500/10',
      accentBorder: 'border-pink-500/20',
      accentText: 'text-pink-400',
      barColor: 'bg-pink-500',
    },
    {
      key: 'founder_idea_fit',
      label: 'Founder–Idea Fit',
      subtitle: 'How well the idea suits you',
      accentBg: 'bg-amber-500/10',
      accentBorder: 'border-amber-500/20',
      accentText: 'text-amber-400',
      barColor: 'bg-amber-500',
    },
  ]

  const data = ZONE_DIMS.map(d => ({ ...d, dim: dims[d.key] })).filter(d => d.dim != null)
  if (data.length === 0) return null

  const avgScore = Math.round(
    data.reduce((sum, d) => sum + (d.dim.score ?? 0), 0) / data.length
  )
  const zoneColor =
    avgScore >= 70 ? 'text-emerald-400' :
    avgScore >= 45 ? 'text-yellow-400' :
    'text-red-400'
  const zoneLabel =
    avgScore >= 70 ? 'Strong Value Zone' :
    avgScore >= 45 ? 'Developing Value Zone' :
    'Value Zone Needs Work'

  return (
    <div className="rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-amber-400" />
          <span className="text-sm font-bold text-white">Value Zone</span>
          <span className="text-[10px] text-slate-500 ml-1">Skills × Passion × Idea Fit</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-black tabular-nums ${zoneColor}`}>{avgScore}</span>
          <span className="text-[10px] text-slate-600">/100</span>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ml-1 ${
            avgScore >= 70
              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
              : avgScore >= 45
                ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400'
                : 'bg-red-500/10 border-red-500/20 text-red-400'
          }`}>{zoneLabel}</span>
        </div>
      </div>

      <div className="px-4 py-3 space-y-3">
        {data.map(({ key, label, subtitle, accentBg, accentBorder, accentText, barColor, dim }) => {
          const score = dim.score ?? 0
          return (
            <div key={key}>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${barColor}`} />
                  <span className="text-xs font-medium text-slate-300">{label}</span>
                  <span className="text-[10px] text-slate-600 hidden sm:inline">{subtitle}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-400 tabular-nums">{score}</span>
                  <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full border ${accentBg} ${accentBorder} ${accentText}`}>
                    {dim.status_label || '—'}
                  </span>
                </div>
              </div>
              <div className="h-1.5 rounded-full bg-white/5">
                <div
                  className={`h-1.5 rounded-full ${barColor} transition-all`}
                  style={{ width: `${Math.min(100, score)}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <div className="px-4 pb-3 pt-1 border-t border-white/5">
        <p className="text-[10px] text-slate-600 leading-relaxed">
          Your Value Zone is where your skills, passion, and idea alignment converge. A strong zone
          means you are the right person to pursue this specific idea.
        </p>
      </div>
    </div>
  )
}

