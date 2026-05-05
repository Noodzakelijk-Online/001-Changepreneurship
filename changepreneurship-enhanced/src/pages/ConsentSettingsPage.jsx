/**
 * ConsentSettingsPage — Sprint 7 (S7-06)
 *
 * Shows the user's current GDPR consent status for each data category
 * and allows granting or revoking consent.
 *
 * Route: /profile/consent
 */
import { useState, useEffect } from 'react';
import { Shield, Check, X, AlertTriangle, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Button } from '@/components/ui/button.jsx';
import apiService from '../services/api.js';

// ─── Category metadata (mirrors backend) ───────────────────────────────────
const CATEGORIES = {
  ASSESSMENT_DATA: {
    label: 'Assessment Data',
    description: 'Storage and processing of your assessment responses across all 7 phases.',
    required: true,
    sensitive: false,
    icon: '📋',
  },
  AI_PROCESSING: {
    label: 'AI Analysis',
    description: 'Sending your data to AI services (Groq) for personalised insights and recommendations.',
    required: false,
    sensitive: true,
    icon: '🤖',
  },
  BENCHMARK_SHARING: {
    label: 'Benchmark Contribution',
    description: 'Anonymous contribution of your journey data to improve recommendations for similar founders. Your identity is never stored.',
    required: false,
    sensitive: false,
    icon: '📊',
  },
  EXTERNAL_OUTREACH: {
    label: 'Outreach on Your Behalf',
    description: 'Platform sending messages (emails, mentor applications) on your behalf through connected accounts.',
    required: false,
    sensitive: true,
    icon: '📤',
  },
  ACCOUNT_CONNECTION: {
    label: 'External Account Connection',
    description: 'Connecting and using your external accounts (email, MicroMentor) to send messages or search mentors.',
    required: false,
    sensitive: true,
    icon: '🔗',
  },
  SENSITIVE_DATA: {
    label: 'Sensitive Information',
    description: 'Processing sensitive information: financial situation, personal stress levels, health signals, and legal situation.',
    required: false,
    sensitive: true,
    icon: '🔒',
  },
};

// ─── Component ──────────────────────────────────────────────────────────────
export default function ConsentSettingsPage() {
  const [consentStatus, setConsentStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(null); // category key being saved
  const [error, setError] = useState(null);
  const [expandedLog, setExpandedLog] = useState(false);
  const [auditLog, setAuditLog] = useState([]);

  useEffect(() => {
    fetchConsent();
  }, []);

  async function fetchConsent() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.request('/v1/consent/status');
      setConsentStatus(data.consent);
    } catch (err) {
      setError(err.message || 'Failed to load consent settings');
    } finally {
      setLoading(false);
    }
  }

  async function fetchAuditLog() {
    try {
      const data = await apiService.request('/v1/consent/log');
      setAuditLog(data.log || []);
    } catch (err) {
      // non-critical
    }
  }

  async function toggleConsent(category, currentlyGranted) {
    if (CATEGORIES[category]?.required && currentlyGranted) return; // can't revoke required

    setSaving(category);
    setError(null);
    try {
      const endpoint = currentlyGranted ? '/v1/consent/revoke' : '/v1/consent/grant';
      await apiService.request(endpoint, {
        method: 'POST',
        body: JSON.stringify({
          categories: [category],
          consent_text_version: 'v1.0',
          source: 'consent_settings_page',
        }),
      });
      // Refresh
      await fetchConsent();
    } catch (err) {
      setError(err.message || 'Failed to update consent');
    } finally {
      setSaving(null);
    }
  }

  async function grantAll() {
    setSaving('all');
    setError(null);
    try {
      const all = Object.keys(CATEGORIES);
      await apiService.request('/v1/consent/grant', {
        method: 'POST',
        body: JSON.stringify({
          categories: all,
          consent_text_version: 'v1.0',
          source: 'grant_all',
        }),
      });
      await fetchConsent();
    } catch (err) {
      setError(err.message || 'Failed to grant all consent');
    } finally {
      setSaving(null);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Shield className="h-7 w-7 text-indigo-600" />
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Privacy & Consent</h1>
          <p className="text-sm text-slate-500">
            Control how we process your data. Changes take effect immediately.
          </p>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Quick action */}
      <div className="flex justify-end">
        <Button
          size="sm"
          variant="outline"
          onClick={grantAll}
          disabled={saving !== null}
          className="text-indigo-600 border-indigo-200 hover:bg-indigo-50"
        >
          {saving === 'all' ? 'Saving…' : 'Grant All (Recommended)'}
        </Button>
      </div>

      {/* Category cards */}
      <div className="space-y-3">
        {Object.entries(CATEGORIES).map(([key, meta]) => {
          const granted = consentStatus?.[key]?.granted ?? false;
          const isRequired = meta.required;
          const isSaving = saving === key;

          return (
            <Card key={key} className={`border ${granted ? 'border-emerald-200 bg-emerald-50/30' : 'border-slate-200'}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <span className="text-xl mt-0.5">{meta.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-semibold text-slate-800 text-sm">{meta.label}</span>
                        {isRequired && (
                          <Badge variant="outline" className="text-xs text-slate-500 border-slate-300">
                            Required
                          </Badge>
                        )}
                        {meta.sensitive && (
                          <Badge variant="outline" className="text-xs text-amber-600 border-amber-200">
                            Sensitive
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-slate-500 mt-1">{meta.description}</p>
                    </div>
                  </div>

                  <div className="shrink-0">
                    {isRequired ? (
                      <div className="flex items-center gap-1 text-xs text-slate-400">
                        <Info className="h-3.5 w-3.5" />
                        <span>Always on</span>
                      </div>
                    ) : (
                      <button
                        onClick={() => toggleConsent(key, granted)}
                        disabled={isSaving}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-1 ${
                          granted ? 'bg-emerald-500' : 'bg-slate-300'
                        } ${isSaving ? 'opacity-50 cursor-not-allowed' : ''}`}
                        aria-label={`${granted ? 'Revoke' : 'Grant'} ${meta.label} consent`}
                        role="switch"
                        aria-checked={granted}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
                            granted ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Legal note */}
      <div className="text-xs text-slate-400 flex items-start gap-1.5 p-3 bg-slate-50 rounded-lg border border-slate-200">
        <Info className="h-3.5 w-3.5 mt-0.5 shrink-0" />
        <span>
          Your consent choices are logged with timestamp and the exact consent text version shown.
          You can request a full export or deletion of your data at any time by contacting us.
          Required categories are necessary for the platform to function (GDPR Art. 6(1)(b) — contract).
        </span>
      </div>

      {/* Audit log toggle */}
      <div>
        <button
          className="text-sm text-indigo-600 hover:underline flex items-center gap-1"
          onClick={() => {
            if (!expandedLog) fetchAuditLog();
            setExpandedLog(v => !v);
          }}
        >
          {expandedLog ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          {expandedLog ? 'Hide' : 'Show'} consent audit log
        </button>

        {expandedLog && (
          <div className="mt-3 border border-slate-200 rounded-lg overflow-hidden">
            {auditLog.length === 0 ? (
              <p className="text-sm text-slate-400 p-4 text-center">No consent records yet.</p>
            ) : (
              <table className="w-full text-xs">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="text-left p-2 text-slate-500 font-medium">Category</th>
                    <th className="text-left p-2 text-slate-500 font-medium">Action</th>
                    <th className="text-left p-2 text-slate-500 font-medium">Date</th>
                    <th className="text-left p-2 text-slate-500 font-medium">Version</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLog.map(record => (
                    <tr key={record.id} className="border-b border-slate-100 last:border-0">
                      <td className="p-2 text-slate-700">
                        {CATEGORIES[record.data_category]?.label ?? record.data_category}
                      </td>
                      <td className="p-2">
                        {record.consent_given ? (
                          <span className="flex items-center gap-1 text-emerald-600">
                            <Check className="h-3 w-3" /> Granted
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-red-500">
                            <X className="h-3 w-3" /> Revoked
                          </span>
                        )}
                      </td>
                      <td className="p-2 text-slate-500">
                        {record.consented_at
                          ? new Date(record.consented_at).toLocaleDateString()
                          : '—'}
                      </td>
                      <td className="p-2 text-slate-400">{record.consent_text_version}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
