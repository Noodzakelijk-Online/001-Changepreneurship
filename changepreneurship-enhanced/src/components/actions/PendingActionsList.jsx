import React, { useState } from 'react';
import ActionPreviewCard from './ActionPreviewCard';

export default function PendingActionsList({
  actions = [],
  onApprove,
  onReject,
  loading = false,
}) {
  const [rejectingId, setRejectingId] = useState(null);
  const [rejectReason, setRejectReason] = useState('');

  const handleRejectSubmit = (id) => {
    onReject?.(id, rejectReason);
    setRejectingId(null);
    setRejectReason('');
  };

  if (actions.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 p-6 text-center">
        <p className="text-sm text-gray-400">No pending actions awaiting your approval.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">
          Pending Actions
          <span className="ml-2 rounded-full bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5">
            {actions.length}
          </span>
        </h3>
        <p className="text-xs text-gray-500">
          Review each action before it is sent
        </p>
      </div>

      {actions.map((action) => (
        <div key={action.id}>
          {rejectingId === action.id ? (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4 space-y-3">
              <p className="text-sm font-medium text-red-800">Reject this action?</p>
              <textarea
                className="w-full text-sm border border-red-300 rounded-md px-3 py-2"
                placeholder="Reason (optional)"
                rows={2}
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
              />
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setRejectingId(null)}
                  className="text-sm text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => handleRejectSubmit(action.id)}
                  className="ml-auto rounded-lg bg-red-600 text-white px-4 py-1.5 text-sm hover:bg-red-700"
                >
                  Confirm rejection
                </button>
              </div>
            </div>
          ) : (
            <ActionPreviewCard
              action={action}
              loading={loading}
              onApprove={onApprove}
              onReject={(id) => setRejectingId(id)}
            />
          )}
        </div>
      ))}
    </div>
  );
}
