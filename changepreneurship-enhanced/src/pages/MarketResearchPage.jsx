/**
 * MarketResearchPage — Sprint 9
 *
 * CEO Section 3.3 Phase 3: "Does the world care?"
 *
 * Tabs:
 *   1. Evidence   — submit interviews, payments, surveys, etc.
 *   2. Competitors — map direct/indirect alternatives
 *   3. Market     — pain intensity, WTP, segment, timing
 *   4. Report     — Market Validity Report (generate + view)
 *
 * All data persisted to backend via Phase 3 API.
 * Minimalist design — no redundant UI.
 */
import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search, Plus, Trash2, RefreshCw, AlertTriangle,
  CheckCircle2, ChevronRight, FileText, Users,
  BarChart3, Target, ArrowRight, Loader2,
} from 'lucide-react';
import apiService from '../services/api.js';

// ── Constants (mirror backend) ───────────────────────────────────────────────
const EVIDENCE_TYPES = ['INTERVIEW','SURVEY','PAYMENT','SIGNUP','LOI','PILOT','REPEAT','REFERRAL','THIRDPARTY'];
const STRENGTHS = ['BELIEF','OPINION','DESK_RESEARCH','AI_RESEARCH','INDIRECT','DIRECT','BEHAVIORAL'];
const STRENGTH_LABEL = {
  BELIEF: 'Personal belief',
  OPINION: "Someone's opinion",
  DESK_RESEARCH: 'Desk research',
  AI_RESEARCH: 'AI research',
  INDIRECT: 'Indirect signal',
  DIRECT: 'Direct signal',
  BEHAVIORAL: 'Behavioral (paid/signed up)',
};
const STRENGTH_COLOR = {
  BELIEF: 'bg-red-500/10 text-red-400',
  OPINION: 'bg-orange-500/10 text-orange-400',
  DESK_RESEARCH: 'bg-yellow-500/10 text-yellow-400',
  AI_RESEARCH: 'bg-yellow-500/10 text-yellow-400',
  INDIRECT: 'bg-blue-500/10 text-blue-400',
  DIRECT: 'bg-indigo-500/10 text-indigo-400',
  BEHAVIORAL: 'bg-emerald-500/10 text-emerald-400',
};
const PAIN_OPTIONS = ['LOW','MEDIUM','HIGH','CRITICAL'];
const PAIN_COLOR = { LOW:'text-slate-400', MEDIUM:'text-yellow-400', HIGH:'text-orange-400', CRITICAL:'text-red-400' };
const RECOMMEND_LABEL = {
  PROCEED: { label: 'Ready for Phase 4', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
  PROCEED_WITH_CAUTION: { label: 'Proceed with caution', color: 'text-yellow-400', bg: 'bg-yellow-500/10 border-yellow-500/20' },
  MORE_VALIDATION_NEEDED: { label: 'More validation needed', color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/20' },
  INSUFFICIENT_EVIDENCE: { label: 'Insufficient evidence', color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20' },
  REVISE_IDEA: { label: 'Revise your idea', color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20' },
  PIVOT_OR_STOP: { label: 'Pivot or stop', color: 'text-red-500', bg: 'bg-red-500/10 border-red-500/20' },
};

// ── Shared tab styles ─────────────────────────────────────────────────────────
const Tab = ({ label, active, onClick, icon: Icon }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-1.5 px-3 py-2 text-sm rounded-lg transition-colors ${
      active ? 'bg-indigo-600/20 text-indigo-300' : 'text-slate-400 hover:text-white hover:bg-white/5'
    }`}
  >
    <Icon className="h-3.5 w-3.5" />
    {label}
  </button>
);

// ── Main page ─────────────────────────────────────────────────────────────────
export default function MarketResearchPage() {
  const navigate = useNavigate();
  const [tab, setTab] = useState('evidence');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Evidence state
  const [evidence, setEvidence] = useState([]);
  const [evidenceForm, setEvidenceForm] = useState({ evidence_type: 'INTERVIEW', strength: 'DIRECT', description: '', source: '' });
  const [addingEvidence, setAddingEvidence] = useState(false);

  // Competitors state
  const [competitors, setCompetitors] = useState([]);
  const [competitorForm, setCompetitorForm] = useState({ name: '', description: '', strengths: '', weaknesses: '', is_direct: true });
  const [addingCompetitor, setAddingCompetitor] = useState(false);

  // Market context state
  const [marketData, setMarketData] = useState({ pain_intensity: 'MEDIUM', willingness_to_pay: false, target_segment: '', estimated_price_range: '', market_timing: '', market_size_note: '' });
  const [marketSaving, setMarketSaving] = useState(false);
  const [marketSaved, setMarketSaved] = useState(false);

  // Report state
  const [report, setReport] = useState(null);
  const [generating, setGenerating] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [evRes, compRes, mktRes, rptRes] = await Promise.all([
        apiService.request('/v1/phase3/evidence'),
        apiService.request('/v1/phase3/competitors'),
        apiService.request('/v1/phase3/market-data'),
        apiService.request('/v1/phase3/report'),
      ]);
      setEvidence(evRes.data?.evidence || []);
      setCompetitors(compRes.data?.competitors || []);
      if (mktRes.data?.market_data) setMarketData(mktRes.data.market_data);
      if (rptRes.data?.report) setReport(rptRes.data.report);
    } catch {
      setError('Failed to load Phase 3 data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  // ── Evidence handlers ───────────────────────────────────────────────────────
  async function submitEvidence(e) {
    e.preventDefault();
    if (!evidenceForm.description.trim()) return;
    setAddingEvidence(true);
    try {
      const res = await apiService.request('/v1/phase3/evidence', { method: 'POST', body: JSON.stringify(evidenceForm) });
      setEvidence(prev => [res.data?.evidence, ...prev].filter(Boolean));
      setEvidenceForm(f => ({ ...f, description: '', source: '' }));
    } catch (err) {
      setError(err.message || 'Failed to add evidence');
    } finally {
      setAddingEvidence(false);
    }
  }

  async function deleteEvidence(id) {
    await apiService.request(`/v1/phase3/evidence/${id}`, { method: 'DELETE' });
    setEvidence(prev => prev.filter(e => e.id !== id));
  }

  // ── Competitor handlers ─────────────────────────────────────────────────────
  async function submitCompetitor(e) {
    e.preventDefault();
    if (!competitorForm.name.trim()) return;
    setAddingCompetitor(true);
    try {
      const res = await apiService.request('/v1/phase3/competitors', { method: 'POST', body: JSON.stringify(competitorForm) });
      setCompetitors(prev => [...prev, res.data?.competitor].filter(Boolean));
      setCompetitorForm({ name: '', description: '', strengths: '', weaknesses: '', is_direct: true });
    } catch (err) {
      setError(err.message || 'Failed to add competitor');
    } finally {
      setAddingCompetitor(false);
    }
  }

  async function deleteCompetitor(id) {
    await apiService.request(`/v1/phase3/competitors/${id}`, { method: 'DELETE' });
    setCompetitors(prev => prev.filter(c => c.id !== id));
  }

  // ── Market data handler ─────────────────────────────────────────────────────
  async function saveMarketData(e) {
    e.preventDefault();
    setMarketSaving(true);
    try {
      await apiService.request('/v1/phase3/market-data', { method: 'PATCH', body: JSON.stringify(marketData) });
      setMarketSaved(true);
      setTimeout(() => setMarketSaved(false), 2000);
    } catch (err) {
      setError(err.message || 'Failed to save');
    } finally {
      setMarketSaving(false);
    }
  }

  // ── Generate report ─────────────────────────────────────────────────────────
  async function generateReport() {
    setGenerating(true);
    setError('');
    try {
      const res = await apiService.request('/v1/phase3/submit', { method: 'POST', body: '{}' });
      setReport(res.data?.report);
      setTab('report');
    } catch (err) {
      setError(err.message || 'Failed to generate report');
    } finally {
      setGenerating(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full py-24">
        <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="min-h-full bg-[#0a0a0f] px-4 py-8 max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-8 h-8 rounded-xl bg-indigo-500/10 flex items-center justify-center">
            <Search className="h-4 w-4 text-indigo-400" />
          </div>
          <h1 className="text-xl font-bold text-white">Market Research</h1>
          <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-slate-400">Phase 3</span>
        </div>
        <p className="text-sm text-slate-400 ml-11">Does the world care enough for this to become a venture?</p>
      </div>

      {error && (
        <div className="mb-4 flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          {error}
          <button onClick={() => setError('')} className="ml-auto text-xs underline">Dismiss</button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-white/5 pb-2">
        <Tab label="Evidence" icon={FileText} active={tab === 'evidence'} onClick={() => setTab('evidence')} />
        <Tab label="Competitors" icon={BarChart3} active={tab === 'competitors'} onClick={() => setTab('competitors')} />
        <Tab label="Market" icon={Target} active={tab === 'market'} onClick={() => setTab('market')} />
        <Tab label={`Report${report ? ' ✓' : ''}`} icon={Users} active={tab === 'report'} onClick={() => setTab('report')} />
      </div>

      {/* ── Evidence Tab ─────────────────────────────────────────────────── */}
      {tab === 'evidence' && (
        <div className="space-y-4">
          <p className="text-xs text-slate-500">
            CEO rule: behavioral evidence (payments, signups, repeat use) is the strongest signal. Personal belief is the weakest.
          </p>

          {/* Add form */}
          <form onSubmit={submitEvidence} className="rounded-xl border border-white/5 bg-white/[0.02] p-4 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Type</label>
                <select
                  value={evidenceForm.evidence_type}
                  onChange={e => setEvidenceForm(f => ({ ...f, evidence_type: e.target.value }))}
                  className="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-3 py-2 text-sm text-white"
                >
                  {EVIDENCE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Strength</label>
                <select
                  value={evidenceForm.strength}
                  onChange={e => setEvidenceForm(f => ({ ...f, strength: e.target.value }))}
                  className="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-3 py-2 text-sm text-white"
                >
                  {STRENGTHS.map(s => <option key={s} value={s}>{STRENGTH_LABEL[s]}</option>)}
                </select>
              </div>
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">What did you find? *</label>
              <textarea
                required
                rows={2}
                value={evidenceForm.description}
                onChange={e => setEvidenceForm(f => ({ ...f, description: e.target.value }))}
                placeholder="e.g. Spoke with 3 potential customers — all confirmed they pay €50/month for workarounds..."
                className="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 resize-none"
              />
            </div>
            <div className="flex gap-3 items-end">
              <div className="flex-1">
                <label className="text-xs text-slate-400 mb-1 block">Source (optional)</label>
                <input
                  value={evidenceForm.source}
                  onChange={e => setEvidenceForm(f => ({ ...f, source: e.target.value }))}
                  placeholder="LinkedIn, survey link, name..."
                  className="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600"
                />
              </div>
              <button
                type="submit"
                disabled={addingEvidence || !evidenceForm.description.trim()}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm rounded-lg transition-colors"
              >
                {addingEvidence ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Plus className="h-3.5 w-3.5" />}
                Add
              </button>
            </div>
          </form>

          {/* Evidence list */}
          {evidence.length === 0 ? (
            <p className="text-sm text-slate-500 text-center py-6">No evidence yet. Add your first finding above.</p>
          ) : (
            <div className="space-y-2">
              {evidence.map(item => (
                <div key={item.id} className="flex items-start gap-3 rounded-xl border border-white/5 bg-white/[0.01] px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 mt-0.5 ${STRENGTH_COLOR[item.strength] || 'bg-slate-500/10 text-slate-400'}`}>
                    {STRENGTH_LABEL[item.strength] || item.strength}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white">{item.description}</p>
                    {item.source && <p className="text-xs text-slate-500 mt-0.5">{item.evidence_type} · {item.source}</p>}
                  </div>
                  <button onClick={() => deleteEvidence(item.id)} className="text-slate-600 hover:text-red-400 transition-colors shrink-0">
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Interview script CTA */}
          <div className="rounded-xl border border-indigo-500/10 bg-indigo-500/5 p-4 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-indigo-300">Need a customer interview script?</p>
              <p className="text-xs text-slate-400 mt-0.5">Personalised questions based on your venture concept.</p>
            </div>
            <button
              onClick={async () => {
                try {
                  const res = await apiService.request('/v1/phase3/interview-script');
                  alert(JSON.stringify(res.script, null, 2)); // TODO: replace with modal in Sprint 10
                } catch {
                  setError('Complete Phase 2 first to generate a personalised script');
                }
              }}
              className="flex items-center gap-1.5 text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              View script <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* ── Competitors Tab ───────────────────────────────────────────────── */}
      {tab === 'competitors' && (
        <div className="space-y-4">
          <p className="text-xs text-slate-500">
            Map who already solves this problem. CEO: awareness of competition = credibility. "No competition" is a warning sign.
          </p>

          <form onSubmit={submitCompetitor} className="rounded-xl border border-white/5 bg-white/[0.02] p-4 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Name *</label>
                <input
                  required
                  value={competitorForm.name}
                  onChange={e => setCompetitorForm(f => ({ ...f, name: e.target.value }))}
                  placeholder="Competitor or alternative"
                  className="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600"
                />
              </div>
              <div className="flex items-end gap-2">
                <label className="flex items-center gap-2 cursor-pointer pb-2">
                  <input
                    type="checkbox"
                    checked={competitorForm.is_direct}
                    onChange={e => setCompetitorForm(f => ({ ...f, is_direct: e.target.checked }))}
                    className="accent-indigo-500"
                  />
                  <span className="text-sm text-slate-300">Direct competitor</span>
                </label>
              </div>
            </div>
            <input
              value={competitorForm.description}
              onChange={e => setCompetitorForm(f => ({ ...f, description: e.target.value }))}
              placeholder="What do they do?"
              className="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600"
            />
            <div className="grid grid-cols-2 gap-3">
              <input
                value={competitorForm.strengths}
                onChange={e => setCompetitorForm(f => ({ ...f, strengths: e.target.value }))}
                placeholder="Their strengths"
                className="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600"
              />
              <input
                value={competitorForm.weaknesses}
                onChange={e => setCompetitorForm(f => ({ ...f, weaknesses: e.target.value }))}
                placeholder="Their weaknesses / gaps"
                className="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600"
              />
            </div>
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={addingCompetitor || !competitorForm.name.trim()}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm rounded-lg"
              >
                {addingCompetitor ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Plus className="h-3.5 w-3.5" />}
                Add competitor
              </button>
            </div>
          </form>

          {competitors.length === 0 ? (
            <p className="text-sm text-slate-500 text-center py-6">No competitors added yet.</p>
          ) : (
            <div className="space-y-2">
              {competitors.map(c => (
                <div key={c.id} className="rounded-xl border border-white/5 bg-white/[0.01] px-4 py-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-white">{c.name}</span>
                        <span className={`text-xs px-1.5 py-0.5 rounded-full ${c.is_direct ? 'bg-red-500/10 text-red-400' : 'bg-slate-500/10 text-slate-400'}`}>
                          {c.is_direct ? 'Direct' : 'Indirect'}
                        </span>
                      </div>
                      {c.description && <p className="text-xs text-slate-400 mt-0.5">{c.description}</p>}
                      {(c.strengths || c.weaknesses) && (
                        <div className="flex gap-4 mt-1 text-xs">
                          {c.strengths && <span className="text-emerald-400/70">+ {c.strengths}</span>}
                          {c.weaknesses && <span className="text-orange-400/70">− {c.weaknesses}</span>}
                        </div>
                      )}
                    </div>
                    <button onClick={() => deleteCompetitor(c.id)} className="text-slate-600 hover:text-red-400 transition-colors ml-4">
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Market Tab ───────────────────────────────────────────────────── */}
      {tab === 'market' && (
        <form onSubmit={saveMarketData} className="space-y-4">
          <p className="text-xs text-slate-500">Capture your understanding of the market context. This feeds directly into your Market Validity Report.</p>

          <div className="rounded-xl border border-white/5 bg-white/[0.02] p-4 space-y-4">
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Target segment</label>
              <input
                value={marketData.target_segment}
                onChange={e => setMarketData(m => ({ ...m, target_segment: e.target.value }))}
                placeholder="Who specifically has this problem?"
                className="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600"
              />
            </div>

            <div>
              <label className="text-xs text-slate-400 mb-2 block">Pain intensity</label>
              <div className="flex gap-2">
                {PAIN_OPTIONS.map(p => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setMarketData(m => ({ ...m, pain_intensity: p }))}
                    className={`flex-1 py-2 rounded-lg text-sm border transition-colors ${
                      marketData.pain_intensity === p
                        ? 'border-indigo-500/50 bg-indigo-600/20 text-white'
                        : 'border-white/5 bg-white/[0.02] text-slate-400 hover:border-white/10'
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={marketData.willingness_to_pay}
                  onChange={e => setMarketData(m => ({ ...m, willingness_to_pay: e.target.checked }))}
                  className="accent-indigo-500"
                />
                <span className="text-sm text-slate-300">Confirmed willingness to pay</span>
              </label>
              {marketData.willingness_to_pay && (
                <input
                  value={marketData.estimated_price_range}
                  onChange={e => setMarketData(m => ({ ...m, estimated_price_range: e.target.value }))}
                  placeholder="e.g. €50–100/month"
                  className="flex-1 bg-[#0a0a0f] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600"
                />
              )}
            </div>

            <div>
              <label className="text-xs text-slate-400 mb-1 block">Market timing</label>
              <input
                value={marketData.market_timing}
                onChange={e => setMarketData(m => ({ ...m, market_timing: e.target.value }))}
                placeholder="Is the market ready? Too early? Growing? Declining?"
                className="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600"
              />
            </div>

            <div>
              <label className="text-xs text-slate-400 mb-1 block">Market size note</label>
              <textarea
                rows={2}
                value={marketData.market_size_note}
                onChange={e => setMarketData(m => ({ ...m, market_size_note: e.target.value }))}
                placeholder="Rough estimate of addressable market — don't over-invest in this at Phase 3"
                className="w-full bg-[#0a0a0f] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 resize-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={marketSaving}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm rounded-lg"
          >
            {marketSaving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : marketSaved ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" /> : null}
            {marketSaved ? 'Saved' : 'Save market context'}
          </button>
        </form>
      )}

      {/* ── Report Tab ───────────────────────────────────────────────────── */}
      {tab === 'report' && (
        <div className="space-y-4">
          {!report ? (
            <div className="rounded-xl border border-white/5 bg-white/[0.02] p-8 text-center">
              <p className="text-slate-400 text-sm mb-4">
                Add evidence, map competitors, and set your market context — then generate your Market Validity Report.
              </p>
              <div className="flex items-center justify-center gap-4 text-xs text-slate-500 mb-6">
                <span className={evidence.length > 0 ? 'text-emerald-400' : ''}>
                  {evidence.length > 0 ? '✓' : '○'} {evidence.length} evidence item{evidence.length !== 1 ? 's' : ''}
                </span>
                <span className={competitors.length > 0 ? 'text-emerald-400' : ''}>
                  {competitors.length > 0 ? '✓' : '○'} {competitors.length} competitor{competitors.length !== 1 ? 's' : ''}
                </span>
                <span className={marketData.pain_intensity !== 'MEDIUM' ? 'text-emerald-400' : ''}>
                  {marketData.pain_intensity !== 'MEDIUM' ? '✓' : '○'} Market context
                </span>
              </div>
              <button
                onClick={generateReport}
                disabled={generating || evidence.length === 0}
                className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm rounded-xl mx-auto"
              >
                {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                Generate Market Validity Report
              </button>
              {evidence.length === 0 && (
                <p className="text-xs text-slate-500 mt-3">Add at least one evidence item first.</p>
              )}
            </div>
          ) : (
            <ReportView report={report} onRegenerate={generateReport} generating={generating} />
          )}
        </div>
      )}
    </div>
  );
}

// ── Report display ────────────────────────────────────────────────────────────
function ReportView({ report, onRegenerate, generating }) {
  const rec = RECOMMEND_LABEL[report.final_recommendation] || { label: report.final_recommendation, color: 'text-white', bg: 'bg-white/5 border-white/10' };

  return (
    <div className="space-y-4">
      {/* Headline verdict */}
      <div className={`rounded-xl border p-5 ${rec.bg}`}>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-slate-400 uppercase tracking-wider">Market Validity Report</span>
          <span className="text-xs text-slate-500">{new Date(report.generated_at).toLocaleDateString()}</span>
        </div>
        <div className="flex items-center gap-3 mb-3">
          <span className={`text-xl font-bold ${rec.color}`}>{rec.label}</span>
          <span className="text-xs text-slate-400">Validity score: {report.validity_score}/100</span>
        </div>
        <div className="grid grid-cols-3 gap-3 text-center">
          <div>
            <div className="text-lg font-bold text-white">{report.evidence_score?.score ?? 0}</div>
            <div className="text-xs text-slate-400">Evidence score</div>
          </div>
          <div>
            <div className="text-lg font-bold text-white">{report.evidence_score?.evidence_count ?? 0}</div>
            <div className="text-xs text-slate-400">Evidence items</div>
          </div>
          <div>
            <div className="text-lg font-bold text-white">{report.competitor_count}</div>
            <div className="text-xs text-slate-400">Competitors</div>
          </div>
        </div>
      </div>

      {/* Assumptions */}
      {report.assumption_evaluation?.results?.length > 0 && (
        <div className="rounded-xl border border-white/5 bg-white/[0.01] p-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Assumptions tested</h3>
          <div className="space-y-2">
            {report.assumption_evaluation.results.map((a, i) => (
              <div key={i} className="flex items-start gap-3 text-sm">
                <span className={`shrink-0 text-xs px-2 py-0.5 rounded-full ${
                  a.status === 'CONFIRMED' ? 'bg-emerald-500/10 text-emerald-400' :
                  a.status === 'REJECTED'  ? 'bg-red-500/10 text-red-400' :
                  a.status === 'PARTIALLY' ? 'bg-yellow-500/10 text-yellow-400' :
                  'bg-slate-500/10 text-slate-400'
                }`}>{a.status}</span>
                <span className="text-slate-300">{a.assumption}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Validation gaps */}
      {report.validation_gaps?.length > 0 && (
        <div className="rounded-xl border border-orange-500/10 bg-orange-500/5 p-4">
          <h3 className="text-xs font-semibold text-orange-400 uppercase tracking-wider mb-2">What's still missing</h3>
          <ul className="space-y-1">
            {report.validation_gaps.map((g, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="text-orange-400 shrink-0 mt-0.5">·</span>
                {g}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={onRegenerate}
          disabled={generating}
          className="flex items-center gap-2 px-4 py-2 border border-white/10 text-sm text-slate-400 hover:text-white rounded-lg transition-colors"
        >
          {generating ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
          Regenerate
        </button>
        {report.ready_for_business_pillars && (
          <a
            href="/assessment/business-pillars-planning"
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm rounded-lg transition-colors"
          >
            Continue to Phase 4 <ArrowRight className="h-3.5 w-3.5" />
          </a>
        )}
      </div>
    </div>
  );
}
