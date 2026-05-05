import React from 'react';

const ACTION_TYPE_LABELS = {
  SEND_MESSAGE: 'Send Message',
  SUBMIT_APPLICATION: 'Submit Application',
  CHANGE_PROFILE: 'Update Profile',
  SEND_OUTREACH: 'Send Outreach',
  POST_CONTENT: 'Post Content',
  DRAFT_OUTREACH: 'Draft Outreach',
  SEARCH_MENTORS: 'Search Mentors',
  HIGH_IMPACT_ACTION: 'High-Impact Action',
};

const PLATFORM_LABELS = {
  micromentor: 'MicroMentor',
  linkedin: 'LinkedIn',
  email: 'Email',
};

const STATUS_BADGE = {
  PROPOSED: 'bg-yellow-100 text-yellow-700',
  REVIEWED: 'bg-blue-100 text-blue-700',
  APPROVED: 'bg-green-100 text-green-700',
  QUEUED: 'bg-purple-100 text-purple-700',
  EXECUTED: 'bg-gray-100 text-gray-700',
  OUTCOME_RECORDED: 'bg-green-200 text-green-900',
  REJECTED: 'bg-red-100 text-red-700',
  FAILED: 'bg-red-200 text-red-900',
  CANCELLED: 'bg-gray-200 text-gray-600',
  EXPIRED: 'bg-gray-100 text-gray-500',
};

export default function ActionPreviewCard({
  action,
  onApprove,
  onReject,
  loading = false,
}) {
  const {
    id,
    action_type,
    approval_status,
    rationale,
    external_platform,
    action_data,
    proposed_at,
    requires_approval,
  } = action;

  const typeLabel = ACTION_TYPE_LABELS[action_type] || action_type;
  const platformLabel = PLATFORM_LABELS[external_platform] || external_platform;
  const badgeCls = STATUS_BADGE[approval_status] || 'bg-gray-100 text-gray-600';

  const isPending = ['PROPOSED', 'REVIEWED'].includes(approval_status);
  const canAct = isPending && requires_approval;

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm p-4 space-y-3">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-gray-900">{typeLabel}</p>
          {platformLabel && (
            <p className="text-xs text-gray-500">via {platformLabel}</p>
          )}
        </div>
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${badgeCls}`}>
          {approval_status.replace(/_/g, ' ')}
        </span>
      </div>

      {/* Rationale */}
      {rationale && (
        <p className="text-sm text-gray-700 border-l-2 border-gray-200 pl-3">{rationale}</p>
      )}

      {/* Data preview */}
      {action_data && (
        <div className="rounded-md bg-gray-50 border border-gray-200 p-3">
          <p className="text-xs font-medium text-gray-400 uppercase mb-1">Content preview</p>
          {action_data.subject && (
            <p className="text-xs text-gray-700"><strong>Subject:</strong> {action_data.subject}</p>
          )}
          {action_data.body_preview && (
            <p className="text-xs text-gray-600 mt-1">{action_data.body_preview}…</p>
          )}
          {!action_data.subject && !action_data.body_preview && (
            <pre className="text-xs text-gray-600 whitespace-pre-wrap overflow-auto max-h-20">
              {JSON.stringify(action_data, null, 2)}
            </pre>
          )}
        </div>
      )}

      {/* Meta */}
      {proposed_at && (
        <p className="text-xs text-gray-400">
          Proposed {new Date(proposed_at).toLocaleString()}
        </p>
      )}

      {/* Actions */}
      {canAct && (
        <div className="flex items-center gap-3 pt-1">
          <button
            type="button"
            disabled={loading}
            onClick={() => onReject?.(id)}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            Reject
          </button>
          <button
            type="button"
            disabled={loading}
            onClick={() => onApprove?.(id)}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Approve & Send
          </button>
        </div>
      )}
    </div>
  );
}
