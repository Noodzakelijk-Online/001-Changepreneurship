import React, { useState } from 'react';

const STATUS_ICON = {
  PROPOSED: '🕐',
  REVIEWED: '👁',
  APPROVED: '✅',
  QUEUED: '⏳',
  EXECUTED: '🚀',
  OUTCOME_RECORDED: '📝',
  REJECTED: '❌',
  FAILED: '⚠️',
  CANCELLED: '🚫',
  EXPIRED: '💨',
};

export default function ActionHistoryLog({ history = [], onRecordOutcome }) {
  const [expandedId, setExpandedId] = useState(null);

  if (history.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 p-6 text-center">
        <p className="text-sm text-gray-400">No actions yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-gray-900">Action History</h3>
      <ul className="space-y-2">
        {history.map((action) => {
          const icon = STATUS_ICON[action.approval_status] || '•';
          const isExpanded = expandedId === action.id;
          const canRecord = action.approval_status === 'EXECUTED';

          return (
            <li
              key={action.id}
              className="rounded-lg border border-gray-200 bg-white"
            >
              <button
                type="button"
                className="w-full flex items-center gap-3 px-4 py-3 text-left"
                onClick={() => setExpandedId(isExpanded ? null : action.id)}
              >
                <span className="text-base">{icon}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {action.action_type?.replace(/_/g, ' ')}
                  </p>
                  <p className="text-xs text-gray-500">
                    {action.approval_status} · {action.proposed_at ? new Date(action.proposed_at).toLocaleDateString() : '—'}
                  </p>
                </div>
                <span className="text-xs text-gray-400">{isExpanded ? '▲' : '▼'}</span>
              </button>

              {isExpanded && (
                <div className="border-t border-gray-100 px-4 py-3 space-y-3">
                  {/* Audit trail */}
                  {action.audit_trail?.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Timeline</p>
                      <ul className="space-y-1">
                        {action.audit_trail.map((entry, i) => (
                          <li key={i} className="flex items-start gap-2 text-xs text-gray-600">
                            <span className="font-medium">{entry.event || entry.event_type}</span>
                            <span className="text-gray-400">·</span>
                            <span>{entry.at || entry.timestamp}</span>
                            {entry.by && <span className="text-gray-400">by {entry.by}</span>}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Result */}
                  {action.result_data && (
                    <div>
                      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Result</p>
                      <pre className="text-xs text-gray-600 bg-gray-50 rounded p-2 overflow-auto max-h-20">
                        {JSON.stringify(action.result_data, null, 2)}
                      </pre>
                    </div>
                  )}

                  {/* Record outcome */}
                  {canRecord && (
                    <RecordOutcomeForm actionId={action.id} onSubmit={onRecordOutcome} />
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function RecordOutcomeForm({ actionId, onSubmit }) {
  const [outcome, setOutcome] = useState('');

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-blue-700">Record what happened:</p>
      <div className="flex gap-2">
        <input
          type="text"
          className="flex-1 text-sm border border-gray-300 rounded-md px-2 py-1"
          placeholder="e.g. Mentor responded, No reply, etc."
          value={outcome}
          onChange={(e) => setOutcome(e.target.value)}
        />
        <button
          type="button"
          disabled={!outcome.trim()}
          onClick={() => onSubmit?.(actionId, outcome)}
          className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          Save
        </button>
      </div>
    </div>
  );
}
