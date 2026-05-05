import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, Compass, RefreshCw, Send, ShieldAlert, UserCheck } from 'lucide-react';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';

const JsonBlock = ({ data }) => (
  <pre className="mt-3 max-h-72 overflow-auto rounded-xl border border-gray-800 bg-black/50 p-3 text-xs text-gray-300 whitespace-pre-wrap">
    {JSON.stringify(data, null, 2)}
  </pre>
);

const StatusPill = ({ children, tone = 'cyan' }) => {
  const tones = {
    cyan: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
    emerald: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
    amber: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
    red: 'bg-red-500/10 text-red-300 border-red-500/30',
    gray: 'bg-gray-500/10 text-gray-300 border-gray-500/30',
  };
  return <span className={`inline-flex rounded-full border px-3 py-1 text-xs ${tones[tone] || tones.cyan}`}>{children}</span>;
};

const MVPActionReviewPage = () => {
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [journeyState, setJourneyState] = useState(null);
  const [actions, setActions] = useState([]);
  const [country, setCountry] = useState('netherlands');
  const [ventureType, setVentureType] = useState('local_service');

  const currentAction = journeyState?.current_action || actions?.[0] || null;
  const nextStep = journeyState?.next_step_card;
  const mentorSuggestions = nextStep?.mentor_source_suggestions || journeyState?.mentor_recommendation?.recommendations || [];

  const run = async (fn) => {
    setLoading(true);
    setError(null);
    try {
      await fn();
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  const refreshActions = async () => {
    const result = await apiService.request('/mvp/actions');
    if (!result.success) throw new Error(result.error || 'Failed to load actions');
    setActions(result.data?.actions || []);
  };

  const loadJourneyState = async ({ createAction = false } = {}) => {
    const result = await apiService.request('/mvp/journey-state', {
      method: 'POST',
      body: JSON.stringify({
        create_action: createAction,
        country,
        venture_type: ventureType,
      }),
    });
    if (!result.success) throw new Error(result.error || 'Failed to load journey state');
    setJourneyState(result.data?.journey_state);
    await refreshActions();
  };

  useEffect(() => {
    if (isAuthenticated) {
      run(() => loadJourneyState({ createAction: false }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  const createNextAction = () => run(async () => {
    await loadJourneyState({ createAction: true });
  });

  const approveAction = (actionId) => run(async () => {
    const result = await apiService.request(`/mvp/actions/${actionId}/approve`, {
      method: 'POST',
      body: JSON.stringify({}),
    });
    if (!result.success) throw new Error(result.error || 'Approve failed');
    await loadJourneyState({ createAction: false });
  });

  const executeMock = (actionId) => run(async () => {
    const result = await apiService.request(`/mvp/actions/${actionId}/execute-mock`, {
      method: 'POST',
      body: JSON.stringify({ result: { result: 'frontend_mock_completed' } }),
    });
    if (!result.success) throw new Error(result.error || 'Mock execution failed');
    await loadJourneyState({ createAction: false });
  });

  const proposeMentorOutreach = (sourceKey) => run(async () => {
    const result = await apiService.request('/mvp/mentor-sources/propose-outreach', {
      method: 'POST',
      body: JSON.stringify({
        selected_source_key: sourceKey,
        venture_id: journeyState?.venture?.id,
        user_goal: 'Ask for feedback on readiness, validation, and the next responsible venture-building step.',
      }),
    });
    if (!result.success) throw new Error(result.error || 'Mentor outreach proposal failed');
    await loadJourneyState({ createAction: false });
  });

  const statusTone = (code) => {
    if (!code) return 'gray';
    if (code.includes('blocked')) return 'red';
    if (code.includes('validation') || code.includes('foundation')) return 'amber';
    if (code.includes('ready')) return 'emerald';
    return 'cyan';
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-black p-8 text-white">
        <Card className="mx-auto max-w-2xl border-gray-800 bg-gray-950 text-white">
          <CardHeader>
            <CardTitle>MVP Venture Journey</CardTitle>
            <CardDescription className="text-gray-400">Please log in before testing the MVP journey routes.</CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black p-6 text-white">
      <div className="mx-auto max-w-6xl space-y-6">
        <div>
          <Badge className="mb-3 bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">MVP journey screen</Badge>
          <h1 className="text-3xl font-bold">Changepreneurship Venture Journey</h1>
          <p className="mt-2 max-w-4xl text-gray-400">
            {journeyState?.party_explanation || 'This screen shows the guided path from assessment to the next safe venture-building action.'}
          </p>
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">{error}</div>
        )}

        <Card className="border-gray-800 bg-gray-950 text-white">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Compass className="h-5 w-5 text-cyan-400" /> Current MVP state</CardTitle>
            <CardDescription className="text-gray-400">One canonical answer to: where is the user now, what is risky, and what should happen next?</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <StatusPill tone={statusTone(journeyState?.mvp_status?.code)}>{journeyState?.mvp_status?.label || 'Not loaded'}</StatusPill>
              <StatusPill tone="gray">Founder type: {journeyState?.founder_type?.founder_type || 'unknown'}</StatusPill>
              <StatusPill tone="gray">Risk: {journeyState?.decision?.risk_level || 'unknown'}</StatusPill>
              <StatusPill tone={journeyState?.risk_summary?.is_hard_blocked ? 'red' : 'emerald'}>
                {journeyState?.risk_summary?.is_hard_blocked ? 'Blocked for protection' : 'No hard block detected'}
              </StatusPill>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <input className="rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm" value={country} onChange={(e) => setCountry(e.target.value)} placeholder="country" />
              <input className="rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm" value={ventureType} onChange={(e) => setVentureType(e.target.value)} placeholder="venture type" />
              <Button onClick={() => run(() => loadJourneyState({ createAction: false }))} disabled={loading} className="bg-cyan-600 hover:bg-cyan-500">
                <RefreshCw className="mr-2 h-4 w-4" /> Refresh journey
              </Button>
            </div>

            {journeyState?.mvp_completeness && (
              <div className="rounded-xl border border-gray-800 bg-black/40 p-4">
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="text-gray-300">MVP journey completeness</span>
                  <span className="font-semibold text-cyan-300">{journeyState.mvp_completeness.score}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-gray-800">
                  <div className="h-full rounded-full bg-cyan-500" style={{ width: `${journeyState.mvp_completeness.score}%` }} />
                </div>
                <p className="mt-2 text-sm text-gray-400">{journeyState.mvp_completeness.message}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="border-gray-800 bg-gray-950 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><ShieldAlert className="h-5 w-5 text-amber-400" /> Next safe step</CardTitle>
              <CardDescription className="text-gray-400">The practical action the platform recommends right now.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold">{nextStep?.title || 'No next step loaded yet'}</h2>
                <p className="mt-2 text-sm text-gray-400">{nextStep?.why_this_now}</p>
              </div>

              {nextStep?.blocked && (
                <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
                  <div className="mb-1 flex items-center gap-2 font-semibold"><AlertTriangle className="h-4 w-4" /> Action blocked</div>
                  <p>{nextStep.unlock_condition || 'Resolve the blocker before continuing.'}</p>
                </div>
              )}

              {nextStep?.allowed_now?.length > 0 && (
                <div>
                  <p className="mb-2 text-sm font-medium text-gray-300">Allowed now</p>
                  <div className="flex flex-wrap gap-2">
                    {nextStep.allowed_now.map((item) => <StatusPill key={item} tone="gray">{item}</StatusPill>)}
                  </div>
                </div>
              )}

              <div className="flex flex-wrap gap-2">
                {!currentAction && <Button onClick={createNextAction} disabled={loading} className="bg-cyan-600 hover:bg-cyan-500">Create proposed action</Button>}
                {currentAction && currentAction.status !== 'approved' && currentAction.status !== 'completed' && (
                  <Button onClick={() => approveAction(currentAction.id)} disabled={loading} className="bg-emerald-600 hover:bg-emerald-500">Approve current action</Button>
                )}
                {currentAction && currentAction.status === 'approved' && (
                  <Button onClick={() => executeMock(currentAction.id)} disabled={loading} className="bg-cyan-600 hover:bg-cyan-500">Mock execute current action</Button>
                )}
              </div>

              {currentAction && <JsonBlock data={currentAction} />}
            </CardContent>
          </Card>

          <Card className="border-gray-800 bg-gray-950 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><UserCheck className="h-5 w-5 text-emerald-400" /> Mentor-source routing</CardTitle>
              <CardDescription className="text-gray-400">Suggested only when support gaps or mentor needs are detected.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-400">{journeyState?.mentor_recommendation?.route_reason || 'No mentor route has been recommended yet.'}</p>
              {mentorSuggestions.length > 0 ? (
                <div className="space-y-3">
                  {mentorSuggestions.slice(0, 5).map((source) => (
                    <div key={source.key} className="rounded-xl border border-gray-800 bg-black/40 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h3 className="font-semibold text-white">{source.name}</h3>
                          <p className="mt-1 text-xs text-gray-400">{source.notes}</p>
                          <p className="mt-2 text-xs text-cyan-300">Score: {source.score} · {source.cost_model}</p>
                        </div>
                        <Button size="sm" variant="outline" className="border-gray-700 text-white hover:bg-gray-900" onClick={() => proposeMentorOutreach(source.key)}>
                          <Send className="mr-2 h-4 w-4" /> Propose
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="rounded-xl border border-gray-800 bg-black/40 p-4 text-sm text-gray-400">No mentor-source suggestions for the current state.</div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card className="border-gray-800 bg-gray-950 text-white">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><CheckCircle className="h-5 w-5 text-emerald-400" /> Evidence, assumptions, and safety summary</CardTitle>
            <CardDescription className="text-gray-400">The safety layer that prevents the platform from making entrepreneurship look easier than it is.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 lg:grid-cols-3">
            <div className="rounded-xl border border-gray-800 bg-black/40 p-4">
              <h3 className="font-semibold">Evidence</h3>
              <p className="mt-2 text-sm text-gray-400">{journeyState?.evidence_summary?.message}</p>
              <JsonBlock data={journeyState?.evidence_summary || {}} />
            </div>
            <div className="rounded-xl border border-gray-800 bg-black/40 p-4">
              <h3 className="font-semibold">Assumptions</h3>
              <p className="mt-2 text-sm text-gray-400">{journeyState?.assumption_summary?.message}</p>
              <JsonBlock data={journeyState?.assumption_summary || {}} />
            </div>
            <div className="rounded-xl border border-gray-800 bg-black/40 p-4">
              <h3 className="font-semibold">Risk</h3>
              <p className="mt-2 text-sm text-gray-400">Survival risk: {journeyState?.risk_summary?.survival_risk_indicator || 'unknown'}</p>
              <JsonBlock data={journeyState?.risk_summary || {}} />
            </div>
          </CardContent>
        </Card>

        <Card className="border-gray-800 bg-gray-950 text-white">
          <CardHeader>
            <CardTitle>Raw journey state</CardTitle>
            <CardDescription className="text-gray-400">Developer view for Nikola / future devs.</CardDescription>
          </CardHeader>
          <CardContent>
            <JsonBlock data={journeyState || {}} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MVPActionReviewPage;
