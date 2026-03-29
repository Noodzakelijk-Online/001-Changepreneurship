import React from 'react';
import { CheckCircle, ArrowRight, Sparkles, Loader2 } from 'lucide-react';
import { useAssessment } from '../../contexts/AssessmentContext';
import { scoreColorClass } from '@/lib/utils.js';

// Human-readable phase names
const PHASE_NAMES = {
  self_discovery: 'Self Discovery',
  idea_discovery: 'Idea Discovery',
  market_research: 'Market Research',
  business_pillars: 'Business Pillars',
  product_concept_testing: 'Product Concept Testing',
  business_development: 'Business Development',
  business_prototype_testing: 'Business Prototype Testing',
};

function scoreBg(score) {
  if (score >= 70) return 'bg-emerald-500/15 border-emerald-500/30';
  if (score >= 50) return 'bg-yellow-500/15 border-yellow-500/30';
  return 'bg-orange-500/15 border-orange-500/30';
}

export default function PhaseCompletionPanel() {
  const { phaseSummary, dismissPhaseSummary } = useAssessment();

  if (!phaseSummary) return null;

  const { phaseId, data } = phaseSummary;
  const phaseName = PHASE_NAMES[phaseId] || phaseId.replace(/_/g, ' ');
  const isLoading = !data;

  return (
    // Fixed full-screen overlay
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4
                    bg-black/70 backdrop-blur-sm animate-fadeIn">

      <div className="relative w-full max-w-lg bg-gray-900 border border-gray-700/60
                      rounded-2xl shadow-2xl shadow-black/60 overflow-hidden">

        {/* Top accent stripe */}
        <div className="h-1 w-full bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500" />

        <div className="p-8">
          {/* Header */}
          <div className="flex items-center gap-3 mb-6">
            <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30
                            flex items-center justify-center">
              <CheckCircle className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-widest font-medium">Phase Complete</p>
              <h2 className="text-lg font-bold text-white leading-tight">{phaseName}</h2>
            </div>

            {/* AI badge */}
            <div className="ml-auto flex items-center gap-1.5 px-2.5 py-1 rounded-lg
                            bg-purple-500/10 border border-purple-500/20">
              <Sparkles className="h-3 w-3 text-purple-400" />
              <span className="text-[10px] text-purple-400 font-medium uppercase tracking-wider">AI Analysis</span>
            </div>
          </div>

          {/* Loading state */}
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-10 gap-3">
              <Loader2 className="h-8 w-8 text-cyan-500 animate-spin" />
              <p className="text-sm text-gray-500">Generating your phase insights…</p>
            </div>
          ) : (
            <>
              {/* Score + headline */}
              <div className="flex items-center gap-4 mb-4">
                <div className={`flex-shrink-0 px-4 py-2 rounded-xl border text-center ${scoreBg(data.score)}`}>
                  <div className={`text-2xl font-bold tabular-nums ${scoreColorClass(data.score)}`}>
                    {data.score}
                  </div>
                  <div className="text-[10px] text-gray-500 uppercase tracking-wide">Score</div>
                </div>
                <p className="text-base font-semibold text-white leading-snug flex-1">
                  {data.headline}
                </p>
              </div>

              {/* Summary */}
              <p className="text-sm text-gray-400 leading-relaxed mb-5">
                {data.summary}
              </p>

              {/* Key findings */}
              {data.key_findings?.length > 0 && (
                <div className="mb-5">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-2">
                    Key Findings
                  </p>
                  <ul className="space-y-2">
                    {data.key_findings.map((finding, i) => (
                      <li key={i} className="flex gap-2 text-sm text-gray-300">
                        <span className="flex-shrink-0 mt-0.5 w-4 h-4 rounded-full bg-cyan-500/15
                                         border border-cyan-500/30 flex items-center justify-center
                                         text-[9px] font-bold text-cyan-400">
                          {i + 1}
                        </span>
                        <span>{finding}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Next focus */}
              {data.next_focus && (
                <div className="px-4 py-3 rounded-xl bg-yellow-500/5 border border-yellow-500/15 mb-6">
                  <p className="text-xs font-semibold text-yellow-500/70 uppercase tracking-wide mb-1">
                    Next Focus
                  </p>
                  <p className="text-sm text-yellow-200/80">{data.next_focus}</p>
                </div>
              )}
            </>
          )}

          {/* Continue button */}
          <button
            type="button"
            onClick={dismissPhaseSummary}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl
                       bg-gradient-to-r from-cyan-500 to-purple-500
                       hover:from-cyan-400 hover:to-purple-400
                       disabled:opacity-50 disabled:cursor-not-allowed
                       text-white font-semibold shadow-lg shadow-cyan-500/20
                       transition-all duration-200"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Analysing…
              </>
            ) : (
              <>
                Continue
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
