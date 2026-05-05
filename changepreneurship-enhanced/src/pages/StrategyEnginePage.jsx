/**
 * StrategicRoadmapPage — Sprint 9
 *
 * Shows the Market Validity Report summary as a strategic roadmap overview.
 * If no report exists, prompts to complete Phase 3 first.
 */
import { useState, useEffect } from 'react';
import { BarChart3, ArrowLeft, ArrowRight, RefreshCw, Loader2, AlertTriangle } from 'lucide-react';
import { Link } from 'react-router-dom';
import apiService from '../services/api.js';

export default function StrategicRoadmapPage() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    apiService.request('/v1/phase3/report')
      .then(res => setReport(res.report))
      .catch(() => setError('Could not load report'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full py-24">
        <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="min-h-full bg-[#0a0a0f] px-4 py-8 max-w-3xl mx-auto">
      <Link to="/assessment/market-research" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-8 transition-colors">
        <ArrowLeft className="h-4 w-4" /> Back to Market Research
      </Link>

      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 rounded-xl bg-indigo-500/10 flex items-center justify-center">
          <BarChart3 className="h-4 w-4 text-indigo-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">Strategic Roadmap</h1>
          <p className="text-sm text-slate-400">Based on your Market Validity Report</p>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 mb-6">
          <AlertTriangle className="h-4 w-4 shrink-0" /> {error}
        </div>
      )}

      {!report ? (
        <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-8 text-center">
          <div className="w-14 h-14 rounded-full bg-indigo-500/10 flex items-center justify-center mx-auto mb-4">
            <BarChart3 className="h-7 w-7 text-indigo-400" />
          </div>
          <h2 className="text-lg font-semibold text-white mb-2">No report generated yet</h2>
          <p className="text-slate-400 text-sm max-w-sm mx-auto mb-6">
            Complete Phase 3 Market Research — add evidence, map competitors, and generate your Market Validity Report.
          </p>
          <Link
            to="/assessment/market-research"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm rounded-xl transition-colors"
          >
            Go to Market Research <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Verdict */}
          <div className="rounded-xl border border-white/5 bg-white/[0.02] p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs text-slate-400 uppercase tracking-wider">Phase 3 Outcome</span>
              <span className="text-xs text-slate-500">{report.generated_at ? new Date(report.generated_at).toLocaleDateString() : ''}</span>
            </div>
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-bold text-white">{report.validity_score}</span>
              <span className="text-slate-400 text-sm">/ 100 validity score</span>
            </div>
            <p className="text-indigo-300 text-sm font-medium mt-1">{report.final_recommendation?.replace(/_/g, ' ')}</p>
          </div>

          {/* Evidence breakdown */}
          {report.evidence_score && (
            <div className="rounded-xl border border-white/5 bg-white/[0.01] p-4">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Evidence quality</h3>
              <div className="flex items-center gap-4">
                <div className="text-2xl font-bold text-white">{report.evidence_score.score}</div>
                <div className="flex-1 space-y-1">
                  {Object.entries(report.evidence_score.breakdown || {})
                    .filter(([, v]) => v > 0)
                    .map(([k, v]) => (
                      <div key={k} className="flex items-center gap-2 text-xs">
                        <span className="text-slate-400 w-28">{k}</span>
                        <div className="flex-1 bg-slate-800 rounded-full h-1.5">
                          <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: `${(v / report.evidence_score.evidence_count) * 100}%` }} />
                        </div>
                        <span className="text-slate-400">{v}</span>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}

          {/* Gaps & next actions */}
          {report.validation_gaps?.length > 0 && (
            <div className="rounded-xl border border-orange-500/10 bg-orange-500/5 p-4">
              <h3 className="text-xs font-semibold text-orange-400 uppercase tracking-wider mb-2">Before moving forward</h3>
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

          {/* CTA */}
          <div className="flex gap-3">
            <Link to="/assessment/market-research" className="flex items-center gap-2 px-4 py-2 border border-white/10 text-sm text-slate-400 hover:text-white rounded-lg transition-colors">
              <RefreshCw className="h-3.5 w-3.5" /> Update research
            </Link>
            {report.ready_for_business_pillars && (
              <Link to="/assessment/business-pillars-planning" className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm rounded-lg transition-colors">
                Continue to Phase 4 <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

