import React, { useState } from 'react';
import VentureTypeSelector from './VentureTypeSelector';

const BLOCK_LEVEL_COLORS = {
  3: 'border-yellow-400 bg-yellow-50 text-yellow-800',
  4: 'border-red-400 bg-red-50 text-red-800',
};

export default function IdeaClarificationForm({ onSubmit, loading = false }) {
  const [form, setForm] = useState({
    idea_description: '',
    problem_description: '',
    target_user_description: '',
    value_prop: '',
    first_use_case: '',
    venture_type: '',
  });
  const [blockers, setBlockers] = useState([]);
  const [clarityScore, setClarityScore] = useState(null);

  const set = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await onSubmit?.({ responses: form });
    if (result?.blockers) setBlockers(result.blockers);
    if (result?.clarity_score !== undefined) setClarityScore(result.clarity_score);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Phase 2 — Idea Clarification</h2>
        <p className="text-sm text-gray-500 mt-1">
          Turn your rough idea into a Clarified Venture Concept.
        </p>
      </div>

      {/* Clarity score */}
      {clarityScore !== null && (
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-600">Clarity score:</span>
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                clarityScore >= 70 ? 'bg-green-500' :
                clarityScore >= 40 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${clarityScore}%` }}
            />
          </div>
          <span className="text-sm font-medium">{clarityScore}/100</span>
        </div>
      )}

      {/* Blockers */}
      {blockers.length > 0 && (
        <div className="space-y-2">
          {blockers.map((b) => (
            <div key={b.type} className={`rounded-lg border p-3 ${BLOCK_LEVEL_COLORS[b.level] || 'border-gray-200'}`}>
              <p className="text-sm font-semibold">{b.type.replace(/_/g, ' ')}</p>
              <p className="text-sm mt-1">{b.explanation}</p>
              <p className="text-xs mt-1 font-medium">To unlock: {b.unlock_condition}</p>
            </div>
          ))}
        </div>
      )}

      {/* Fields */}
      <Field
        label="Describe your idea *"
        hint="One paragraph — what it is, not what it does"
        value={form.idea_description}
        onChange={set('idea_description')}
        required
        multiline
      />
      <Field
        label="What problem does it solve? *"
        hint="Be specific: who has this problem, when, how often"
        value={form.problem_description}
        onChange={set('problem_description')}
        required
        multiline
      />
      <Field
        label="Who is your target user? *"
        hint='Avoid "everyone". One specific person type.'
        value={form.target_user_description}
        onChange={set('target_user_description')}
        required
      />
      <Field
        label="What value do you deliver?"
        hint="What outcome does the user get? (time saved, money saved, pain eliminated)"
        value={form.value_prop}
        onChange={set('value_prop')}
        multiline
      />
      <Field
        label="First use case"
        hint="One scenario: person X does Y and gets Z"
        value={form.first_use_case}
        onChange={set('first_use_case')}
        multiline
      />

      <VentureTypeSelector
        value={form.venture_type}
        onChange={(v) => setForm((f) => ({ ...f, venture_type: v }))}
      />

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-blue-600 text-white py-2 px-4 text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Analyzing…' : 'Clarify my idea →'}
      </button>
    </form>
  );
}

function Field({ label, hint, value, onChange, required, multiline }) {
  const common = {
    className:
      'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
    value,
    onChange,
    required,
  };
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      {hint && <p className="text-xs text-gray-400 mt-0.5">{hint}</p>}
      {multiline ? (
        <textarea {...common} rows={3} />
      ) : (
        <input {...common} type="text" />
      )}
    </div>
  );
}
