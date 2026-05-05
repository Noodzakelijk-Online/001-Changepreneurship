/**
 * ConnectedAccountsPage — Sprint 7 (S7-06)
 *
 * Shows external platform connections (email, MicroMentor, LinkedIn…)
 * and allows connecting/revoking them.
 *
 * Route: /profile/connections
 */
import { useState, useEffect } from 'react';
import { Link2, Plus, Trash2, AlertTriangle, CheckCircle, Clock, XCircle, Mail, ExternalLink, RefreshCw } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Button } from '@/components/ui/button.jsx';
import apiService from '../services/api.js';

// ─── Platform metadata ───────────────────────────────────────────────────────
const PLATFORMS = {
  EMAIL: {
    label: 'Email (SMTP)',
    description: 'Connect your email account to send mentor outreach and receive replies.',
    icon: '📧',
    available: true,
    permOptions: ['READ_ONLY', 'DRAFT', 'SEND'],
  },
  MICROMENTOR: {
    label: 'MicroMentor',
    description: 'Search mentors and send applications through MicroMentor.org.',
    icon: '🤝',
    available: true,
    permOptions: ['READ_ONLY', 'DRAFT', 'SEND'],
  },
  LINKEDIN: {
    label: 'LinkedIn',
    description: 'Professional outreach — coming soon.',
    icon: '💼',
    available: false,
    permOptions: [],
  },
  CALENDAR: {
    label: 'Calendar',
    description: 'Schedule mentor meetings — coming soon.',
    icon: '📅',
    available: false,
    permOptions: [],
  },
};

const STATUS_CONFIG = {
  ACTIVE:   { label: 'Active',   color: 'text-emerald-600', bg: 'bg-emerald-50 border-emerald-200', Icon: CheckCircle },
  PENDING:  { label: 'Pending',  color: 'text-amber-600',   bg: 'bg-amber-50 border-amber-200',    Icon: Clock },
  REVOKED:  { label: 'Revoked',  color: 'text-red-500',     bg: 'bg-red-50 border-red-200',        Icon: XCircle },
  EXPIRED:  { label: 'Expired',  color: 'text-slate-400',   bg: 'bg-slate-50 border-slate-200',    Icon: Clock },
};

const PERM_LABELS = {
  READ_ONLY: 'Read-only',
  DRAFT:     'Draft (no auto-send)',
  SEND:      'Send (requires approval)',
  FULL:      'Full access',
};

// ─── Add Connection Dialog (simple, no OAuth redirect in MVP) ────────────────
function AddConnectionDialog({ onClose, onCreated }) {
  const [platform, setPlatform] = useState('EMAIL');
  const [email, setEmail]       = useState('');
  const [perm, setPerm]         = useState('DRAFT');
  const [saving, setSaving]     = useState(false);
  const [error, setError]       = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await apiService.request('/v1/connections', {
        method: 'POST',
        body: JSON.stringify({
          platform,
          external_account_email: email,
          external_display_name: email,
          permission_level: perm,
        }),
      });
      onCreated();
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to add connection');
    } finally {
      setSaving(false);
    }
  }

  const meta = PLATFORMS[platform];

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">Connect an Account</h2>

        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Platform picker */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Platform</label>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(PLATFORMS)
                .filter(([, m]) => m.available)
                .map(([key, m]) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => { setPlatform(key); setPerm(m.permOptions[1] ?? 'DRAFT'); }}
                    className={`flex items-center gap-2 p-3 rounded-lg border text-sm text-left transition ${
                      platform === key
                        ? 'border-indigo-400 bg-indigo-50 text-indigo-700'
                        : 'border-slate-200 text-slate-600 hover:border-slate-300'
                    }`}
                  >
                    <span>{m.icon}</span>
                    <span className="font-medium">{m.label}</span>
                  </button>
                ))}
            </div>
          </div>

          {/* Email / identifier */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Account email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>

          {/* Permission level */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Permission level</label>
            <select
              value={perm}
              onChange={e => setPerm(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              {(meta.permOptions || ['DRAFT']).map(p => (
                <option key={p} value={p}>{PERM_LABELS[p]}</option>
              ))}
            </select>
            <p className="text-xs text-slate-400 mt-1">
              {perm === 'DRAFT' && 'Platform prepares messages, you must approve before sending.'}
              {perm === 'SEND' && 'Platform can send after your approval step — always with your knowledge.'}
              {perm === 'READ_ONLY' && 'Platform can only read/search, never send.'}
            </p>
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
            <Button type="submit" disabled={saving} className="bg-indigo-600 text-white hover:bg-indigo-700">
              {saving ? 'Connecting…' : 'Connect Account'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Main page ───────────────────────────────────────────────────────────────
export default function ConnectedAccountsPage() {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState(null);
  const [showAdd, setShowAdd]         = useState(false);
  const [revoking, setRevoking]       = useState(null);

  useEffect(() => { fetchConnections(); }, []);

  async function fetchConnections() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.request('/v1/connections');
      setConnections(data.connections || []);
    } catch (err) {
      setError(err.message || 'Failed to load connections');
    } finally {
      setLoading(false);
    }
  }

  async function handleRevoke(id) {
    setRevoking(id);
    try {
      await apiService.request(`/v1/connections/${id}/revoke`, { method: 'POST' });
      await fetchConnections();
    } catch (err) {
      setError(err.message || 'Failed to revoke connection');
    } finally {
      setRevoking(null);
    }
  }

  async function handleDelete(id) {
    try {
      await apiService.request(`/v1/connections/${id}`, { method: 'DELETE' });
      await fetchConnections();
    } catch (err) {
      setError(err.message || 'Failed to delete connection');
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link2 className="h-7 w-7 text-indigo-600" />
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Connected Accounts</h1>
            <p className="text-sm text-slate-500">
              External accounts the platform may use to act on your behalf.
            </p>
          </div>
        </div>
        <Button
          size="sm"
          className="bg-indigo-600 text-white hover:bg-indigo-700 flex items-center gap-1.5"
          onClick={() => setShowAdd(true)}
        >
          <Plus className="h-4 w-4" />
          Connect
        </Button>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Connections list */}
      {loading ? (
        <div className="flex justify-center py-10">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
        </div>
      ) : connections.length === 0 ? (
        <Card className="border-dashed border-slate-200">
          <CardContent className="p-8 text-center">
            <Link2 className="h-10 w-10 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500 text-sm">No accounts connected yet.</p>
            <p className="text-slate-400 text-xs mt-1">
              Connect your email to enable mentor outreach.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {connections.map(conn => {
            const meta = PLATFORMS[conn.platform] ?? { label: conn.platform, icon: '🔗' };
            const status = STATUS_CONFIG[conn.connection_status] ?? STATUS_CONFIG.PENDING;
            const StatusIcon = status.Icon;
            const isRevoking = revoking === conn.id;

            return (
              <Card key={conn.id} className={`border ${status.bg}`}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl mt-0.5">{meta.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-semibold text-slate-800 text-sm">{meta.label}</span>
                        <span className={`flex items-center gap-1 text-xs font-medium ${status.color}`}>
                          <StatusIcon className="h-3 w-3" />
                          {status.label}
                        </span>
                      </div>

                      {conn.external_account_email && (
                        <p className="text-xs text-slate-500 mt-0.5">{conn.external_account_email}</p>
                      )}

                      <div className="flex items-center gap-3 mt-2">
                        <Badge variant="outline" className="text-xs text-slate-500">
                          {PERM_LABELS[conn.permission_level] ?? conn.permission_level}
                        </Badge>
                        {conn.connected_at && (
                          <span className="text-xs text-slate-400">
                            Connected {new Date(conn.connected_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      {conn.connection_status !== 'REVOKED' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleRevoke(conn.id)}
                          disabled={isRevoking}
                          className="text-amber-600 border-amber-200 hover:bg-amber-50 text-xs h-7"
                        >
                          {isRevoking ? <RefreshCw className="h-3 w-3 animate-spin" /> : 'Revoke'}
                        </Button>
                      )}
                      {conn.connection_status === 'REVOKED' && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDelete(conn.id)}
                          className="text-red-400 hover:text-red-600 text-xs h-7"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Coming soon platforms */}
      <div>
        <p className="text-xs font-medium text-slate-400 mb-2 uppercase tracking-wide">Coming Soon</p>
        <div className="flex gap-2">
          {Object.entries(PLATFORMS)
            .filter(([, m]) => !m.available)
            .map(([key, m]) => (
              <div
                key={key}
                className="flex items-center gap-1.5 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-400 text-xs"
              >
                <span>{m.icon}</span>
                <span>{m.label}</span>
              </div>
            ))}
        </div>
      </div>

      {/* Safety note */}
      <div className="text-xs text-slate-400 p-3 bg-slate-50 rounded-lg border border-slate-200">
        🔐 Platform never stores plaintext tokens. All connection tokens are encrypted at rest.
        The platform will never send messages without your explicit approval first.
      </div>

      {/* Add dialog */}
      {showAdd && (
        <AddConnectionDialog
          onClose={() => setShowAdd(false)}
          onCreated={fetchConnections}
        />
      )}
    </div>
  );
}
