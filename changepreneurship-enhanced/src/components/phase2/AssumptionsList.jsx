import React, { useState } from 'react';

const TYPE_BADGE = {
  USER_BELIEF: { label: 'User Belief', cls: 'bg-red-100 text-red-700' },
  AI_RESEARCH: { label: 'AI Research', cls: 'bg-orange-100 text-orange-700' },
  DESK_RESEARCH: { label: 'Desk Research', cls: 'bg-yellow-100 text-yellow-700' },
  WEAK_SIGNAL: { label: 'Weak Signal', cls: 'bg-yellow-100 text-yellow-800' },
  PROFESSIONAL_OPINION: { label: 'Expert Opinion', cls: 'bg-blue-100 text-blue-700' },
  PARTIAL_VALIDATION: { label: 'Partial Validation', cls: 'bg-teal-100 text-teal-700' },
  STRONG_VALIDATION: { label: 'Strong Validation', cls: 'bg-green-100 text-green-700' },
  BEHAVIORAL_EVIDENCE: { label: 'Behavioral Evidence', cls: 'bg-green-200 text-green-800' },
  VERIFIED_FACT: { label: 'Verified Fact', cls: 'bg-blue-200 text-blue-900' },
};

export default function AssumptionsList({
  assumptions = [],
  onMarkTested,
  onAddEvidence,
  ventureId,
}) {
  const [activeId, setActiveId] = useState(null);
  const [testResult, setTestResult] = useState('');
  const [newType, setNewType] = useState('');

  const handleMarkTested = async (assumptionId) => {
    if (!testResult.trim()) return;
    await onMarkTested?.({
      venture_id: ventureId,
      assumption_id: assumptionId,
      test_result: testResult,
      new_type: newType || undefined,
    });
    setActiveId(null);
    setTestResult('');
    setNewType('');
  };

  const untested = assumptions.filter((a) => !a.tested);
  const tested = assumptions.filter((a) => a.tested);
  const pct = assumptions.length ? Math.round((tested.length / assumptions.length) * 100) : 0;

  return (
    <div className="space-y-4">
      {/* Progress bar */}
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-600">{tested.length}/{assumptions.length} tested</span>
        <div className="flex-1 bg-gray-100 rounded-full h-2">
          <div
            className="h-2 rounded-full bg-blue-500 transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className="text-sm font-semibold text-gray-700">{pct}%</span>
      </div>

      {/* Untested */}
      {untested.length > 0 && (
        <section>
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
            Needs Testing ({untested.length})
          </h3>
          <ul className="space-y-2">
            {untested.map((a) => (
              <AssumptionItem
                key={a.id}
                assumption={a}
                active={activeId === a.id}
                testResult={testResult}
                newType={newType}
                onToggle={() => setActiveId(activeId === a.id ? null : a.id)}
                onTestResultChange={setTestResult}
                onNewTypeChange={setNewType}
                onMarkTested={() => handleMarkTested(a.id)}
              />
            ))}
          </ul>
        </section>
      )}

      {/* Tested */}
      {tested.length > 0 && (
        <section>
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
            Tested ({tested.length})
          </h3>
          <ul className="space-y-2">
            {tested.map((a) => (
              <AssumptionItem key={a.id} assumption={a} readonly />
            ))}
          </ul>
        </section>
      )}

      {assumptions.length === 0 && (
        <p className="text-sm text-gray-400 text-center py-4">
          No assumptions yet. Submit your idea to generate them.
        </p>
      )}
    </div>
  );
}

function AssumptionItem({
  assumption,
  active,
  testResult,
  newType,
  onToggle,
  onTestResultChange,
  onNewTypeChange,
  onMarkTested,
  readonly,
}) {
  const badge = TYPE_BADGE[assumption.assumption_type] || { label: assumption.assumption_type, cls: 'bg-gray-100 text-gray-600' };

  return (
    <li className={`rounded-lg border ${assumption.tested ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-white'} p-3`}>
      <div className="flex items-start gap-2">
        <span className={`mt-0.5 h-3 w-3 rounded-full flex-shrink-0 ${assumption.tested ? 'bg-green-400' : 'bg-gray-300'}`} />
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-800">{assumption.claim}</p>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badge.cls}`}>{badge.label}</span>
            {assumption.tested && assumption.test_result && (
              <span className="text-xs text-gray-500">→ {assumption.test_result}</span>
            )}
          </div>
        </div>
        {!readonly && !assumption.tested && (
          <button
            type="button"
            onClick={onToggle}
            className="text-xs text-blue-600 hover:text-blue-800 flex-shrink-0"
          >
            {active ? 'Cancel' : 'Mark tested'}
          </button>
        )}
      </div>

      {active && (
        <div className="mt-2 space-y-2">
          <textarea
            className="w-full text-sm border border-gray-300 rounded-md px-3 py-2 focus:ring-1 focus:ring-blue-500"
            placeholder="What did you find out?"
            rows={2}
            value={testResult}
            onChange={(e) => onTestResultChange(e.target.value)}
          />
          <div className="flex items-center gap-2">
            <select
              className="text-xs border border-gray-300 rounded px-2 py-1"
              value={newType}
              onChange={(e) => onNewTypeChange(e.target.value)}
            >
              <option value="">Keep type ({assumption.assumption_type})</option>
              {Object.keys(TYPE_BADGE).map((t) => (
                <option key={t} value={t}>{TYPE_BADGE[t].label}</option>
              ))}
            </select>
            <button
              type="button"
              onClick={onMarkTested}
              disabled={!testResult.trim()}
              className="ml-auto text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Save
            </button>
          </div>
        </div>
      )}
    </li>
  );
}
