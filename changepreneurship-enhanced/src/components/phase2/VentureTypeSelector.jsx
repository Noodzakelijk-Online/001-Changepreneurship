import React, { useState } from 'react';

const VENTURE_TYPES = [
  { value: 'FORPROFIT', label: 'For-Profit', description: 'Revenue-focused business' },
  { value: 'NONPROFIT', label: 'Non-Profit', description: 'Mission-driven, grant/donation funded' },
  { value: 'SOCIAL', label: 'Social Enterprise', description: 'Profit + social impact' },
  { value: 'LOCAL', label: 'Local / Community', description: 'Serves a specific city or region' },
  { value: 'DEEPTECH', label: 'Deep Tech / R&D', description: 'Research-intensive, patent potential' },
  { value: 'HYBRID', label: 'Hybrid', description: 'Multiple revenue models' },
];

export default function VentureTypeSelector({ value, onChange, hint, disabled = false }) {
  const [selected, setSelected] = useState(value || '');

  const handleSelect = (type) => {
    if (disabled) return;
    setSelected(type);
    onChange?.(type);
  };

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-gray-700">Venture Type</p>
      {hint && (
        <p className="text-xs text-blue-600 bg-blue-50 rounded px-3 py-2">
          Suggested: <strong>{VENTURE_TYPES.find(t => t.value === hint)?.label || hint}</strong>
          {' '}— based on your idea description
        </p>
      )}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {VENTURE_TYPES.map((type) => (
          <button
            key={type.value}
            type="button"
            disabled={disabled}
            onClick={() => handleSelect(type.value)}
            className={`
              rounded-lg border p-3 text-left transition-all
              ${selected === type.value
                ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                : 'border-gray-200 bg-white hover:border-gray-400'}
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            <p className="text-sm font-semibold text-gray-900">{type.label}</p>
            <p className="text-xs text-gray-500 mt-0.5">{type.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
