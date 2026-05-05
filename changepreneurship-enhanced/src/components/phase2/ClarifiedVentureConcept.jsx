import React, { useState } from 'react';

const CONFIDENCE_BADGE = {
  SPECULATIVE: 'bg-red-100 text-red-700',
  LOW: 'bg-orange-100 text-orange-700',
  MEDIUM: 'bg-yellow-100 text-yellow-700',
  HIGH: 'bg-green-100 text-green-700',
  VERIFIED: 'bg-blue-100 text-blue-700',
};

export default function ClarifiedVentureConcept({ cvc, ventureId, onEdit, onApprove, readonly = false }) {
  const [expanded, setExpanded] = useState(false);

  if (!cvc) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 p-6 text-center text-sm text-gray-400">
        No Clarified Venture Concept yet. Complete the idea clarification form.
      </div>
    );
  }

  const {
    problem_statement,
    target_user_hypothesis,
    value_proposition,
    assumptions = [],
    open_questions = [],
    status,
    confidence,
  } = cvc;

  const testedCount = assumptions.filter((a) => a.tested).length;
  const totalCount = assumptions.length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-900">Clarified Venture Concept</span>
          <span className="rounded-full bg-amber-100 text-amber-700 text-xs font-medium px-2 py-0.5">
            DRAFT
          </span>
          {status && (
            <span className="rounded-full bg-gray-100 text-gray-600 text-xs px-2 py-0.5">
              {status}
            </span>
          )}
        </div>
        {confidence && (
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${CONFIDENCE_BADGE[confidence] || 'bg-gray-100 text-gray-600'}`}>
            {confidence}
          </span>
        )}
      </div>

      {/* Core fields */}
      <div className="px-5 py-4 space-y-4">
        <Section label="Problem Statement" content={problem_statement} />
        <Section label="Target User" content={target_user_hypothesis} />
        <Section label="Value Proposition" content={value_proposition} />
      </div>

      {/* Assumptions summary */}
      {totalCount > 0 && (
        <div className="px-5 pb-4">
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
          >
            <span>
              Assumptions: {testedCount}/{totalCount} tested
            </span>
            <span>{expanded ? '▲' : '▼'}</span>
          </button>
          {expanded && (
            <ul className="mt-2 space-y-1">
              {assumptions.map((a, i) => (
                <li key={a.id || i} className="flex items-start gap-2 text-sm">
                  <span className={`mt-0.5 h-4 w-4 rounded-full flex-shrink-0 ${a.tested ? 'bg-green-400' : 'bg-gray-300'}`} />
                  <span className="text-gray-700">{a.claim}</span>
                  {a.tested && (
                    <span className="text-xs text-green-600 font-medium ml-auto">Tested</span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Open questions */}
      {open_questions.length > 0 && (
        <div className="px-5 pb-4">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Open Questions</p>
          <ul className="space-y-1">
            {open_questions.map((q, i) => (
              <li key={q.id || i} className="text-sm text-gray-600">
                {i + 1}. {q.question || q}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      {!readonly && (
        <div className="flex items-center gap-3 px-5 py-4 border-t border-gray-100">
          {onEdit && (
            <button
              type="button"
              onClick={() => onEdit(ventureId)}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Edit
            </button>
          )}
          {onApprove && (
            <button
              type="button"
              onClick={() => onApprove(ventureId)}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Approve this concept →
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function Section({ label, content }) {
  if (!content) return null;
  return (
    <div>
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{label}</p>
      <p className="mt-1 text-sm text-gray-800">{content}</p>
    </div>
  );
}
