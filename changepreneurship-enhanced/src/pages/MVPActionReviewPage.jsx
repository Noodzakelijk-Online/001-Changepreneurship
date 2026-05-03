import React, { useEffect, useState } from 'react';
import { CheckCircle, RefreshCw, Send, ShieldAlert, UserCheck } from 'lucide-react';
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

const MVPActionReviewPage = () => {
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [bootstrap, setBootstrap] = useState(null);
  const [actions, setActions] = useState([]);
  const [mentorRecommendation, setMentorRecommendation] = useState(null);
  const [country, setCountry] = useState('netherlands');
  const [ventureType, setVentureType] = useState('local_service');
  const [mentorNeed, setMentorNeed] = useState('general_business');

  const activeAction = bootstrap?.action || actions?.[0] || null;

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

  useEffect(() => {
    if (isAuthenticated) {
      refreshActions().catch((err) => setError(err.message));
    }
  }, [isAuthenticated]);

  const bootstrapFromAssessment = () => run(async () => {
    const result = await apiService.request('/mvp/bootstrap-from-assessment', {
      method: 'POST',
      body: JSON.stringify({ create_action: true }),
    });
    if (!result.success) throw new Error(result.error || 'Bootstrap failed');
    setBootstrap(result.data);
    await refreshActions();
  });

  const approveAction = (actionId) => run(async () => {
    const result = await apiService.request(`/mvp/actions/${actionId}/approve`, {
      method: 'POST',
      body: JSON.stringify({}),
    });
    if (!result.success) throw new Error(result.error || 'Approve failed');
    await refreshActions();
  });

  const executeMock = (actionId) => run(async () => {
    const result = await apiService.request(`/mvp/actions/${actionId}/execute-mock`, {
      method: 'POST',
      body: JSON.stringify({ result: { result: 'frontend_mock_completed' } }),
    });
    if (!result.success) throw new Error(result.error || 'Mock execution failed');
    await refreshActions();
  });

  const recommendMentors = () => run(async () => {
    const result = await apiService.request('/mvp/mentor-sources/recommend', {
      method: 'POST',
      body: JSON.stringify({
        country,
        venture_type: ventureType,
        mentor_need: mentorNeed,
        max_results: 5,
      }),
    });
    if (!result.success) throw new Error(result.error || 'Mentor recommendation failed');
    setMentorRecommendation(result.data?.mentor_recommendation);
  });

  const proposeMentorOutreach = (sourceKey) => run(async () => {
    const result = await apiService.request('/mvp/mentor-sources/propose-outreach', {
      method: 'POST',
      body: JSON.stringify({
        selected_source_key: sourceKey,
        user_goal: 'Ask for feedback on readiness, validation, and the next responsible venture-building step.',
      }),
    });
    if (!result.success) throw new Error(result.error || 'Mentor outreach proposal failed');
    setBootstrap((prev) => ({ ...(prev || {}), action: result.data?.action, mentor_payload: result.data?.mentor_payload }));
    await refreshActions();
  });

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-black p-8 text-white">
        <Card className="mx-auto max-w-2xl border-gray-800 bg-gray-950 text-white">
          <CardHeader>
            <CardTitle>MVP Action Review</CardTitle>
            <CardDescription className="text-gray-400">Please log in before testing the MVP action routes.</CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black p-6 text-white">
      <div className="mx-auto max-w-6xl space-y-6">
        <div>
          <Badge className="mb-3 bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">Infrastructure test screen</Badge>
          <h1 className="text-3xl font-bold">MVP Action Review</h1>
          <p className="mt-2 max-w-3xl text-gray-400">
            This page connects the existing assessment flow to the new MVP backend loop: diagnose, decide, propose action, approve, mock-execute, and record.
          </p>
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">{error}</div>
        )}

        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="border-gray-800 bg-gray-950 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><ShieldAlert className="h-5 w-5 text-cyan-400" /> Assessment → Decision → Action</CardTitle>
              <CardDescription className="text-gray-400">Bootstrap the new readiness/action layer from existing assessment data.</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={bootstrapFromAssessment} disabled={loading} className="bg-cyan-600 hover:bg-cyan-500">
                <RefreshCw className="mr-2 h-4 w-4" /> Bootstrap from assessment
              </Button>
              {bootstrap && <JsonBlock data={bootstrap} />}
            </CardContent>
          </Card>

          <Card className="border-gray-800 bg-gray-950 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><UserCheck className="h-5 w-5 text-emerald-400" /> Mentor-source routing</CardTitle>
              <CardDescription className="text-gray-400">Country-aware mentor recommendations and outreach proposal.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                <input className="rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm" value={country} onChange={(e) => setCountry(e.target.value)} placeholder="country" />
                <input className="rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm" value={ventureType} onChange={(e) => setVentureType(e.target.value)} placeholder="venture type" />
                <input className="rounded-lg border border-gray-800 bg-black px-3 py-2 text-sm" value={mentorNeed} onChange={(e) => setMentorNeed(e.target.value)} placeholder="mentor need" />
              </div>
              <Button onClick={recommendMentors} disabled={loading} className="bg-purple-600 hover:bg-purple-500">
                Recommend mentors
              </Button>
              {mentorRecommendation && (
                <div className="space-y-3">
                  <JsonBlock data={mentorRecommendation} />
                  <div className="flex flex-wrap gap-2">
                    {(mentorRecommendation.recommendations || []).slice(0, 3).map((source) => (
                      <Button key={source.key} variant="outline" className="border-gray-700 text-white hover:bg-gray-900" onClick={() => proposeMentorOutreach(source.key)}>
                        <Send className="mr-2 h-4 w-4" /> Propose {source.name}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card className="border-gray-800 bg-gray-950 text-white">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><CheckCircle className="h-5 w-5 text-emerald-400" /> Current actions</CardTitle>
            <CardDescription className="text-gray-400">Review, approve, and mock-execute proposed actions.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="mb-4 flex gap-2">
              <Button variant="outline" className="border-gray-700 text-white hover:bg-gray-900" onClick={() => run(refreshActions)} disabled={loading}>Refresh actions</Button>
              {activeAction && activeAction.status !== 'approved' && activeAction.status !== 'completed' && (
                <Button onClick={() => approveAction(activeAction.id)} disabled={loading} className="bg-emerald-600 hover:bg-emerald-500">Approve latest action</Button>
              )}
              {activeAction && activeAction.status === 'approved' && (
                <Button onClick={() => executeMock(activeAction.id)} disabled={loading} className="bg-cyan-600 hover:bg-cyan-500">Mock execute latest action</Button>
              )}
            </div>
            <JsonBlock data={actions} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MVPActionReviewPage;
