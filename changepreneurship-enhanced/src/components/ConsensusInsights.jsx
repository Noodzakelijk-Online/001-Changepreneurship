import React from 'react';
import { Sparkles, CheckCircle2, AlertTriangle, Info } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

/**
 * ConsensusInsights - Displays multi-model AI consensus results
 * Shows majority findings, niche insights, and hallucination detection
 */
export const ConsensusInsights = ({ 
  narrative = '', 
  consensus = null,
  onRegenerate = null 
}) => {
  if (!narrative && !consensus) {
    return null;
  }

  // Parse narrative into sections
  const parseNarrative = (text) => {
    const lines = text.split('\n').filter(l => l.trim());
    const majority = [];
    const minority = [];
    let inMinority = false;

    lines.forEach(line => {
      if (line.toLowerCase().includes('minority review')) {
        inMinority = true;
        return;
      }
      if (inMinority) {
        minority.push(line);
      } else {
        majority.push(line);
      }
    });

    return { majority, minority };
  };

  const { majority, minority } = parseNarrative(narrative);

  // Extract niche insights and hallucinations
  const nicheInsights = minority
    .filter(line => line.toLowerCase().includes('niche insight'))
    .map(line => line.replace(/^-\s*Niche Insight:\s*/i, '').trim());

  const hallucinations = minority
    .filter(line => line.toLowerCase().includes('hallucination'))
    .map(line => line.replace(/^-\s*Hallucination:\s*/i, '').trim());

  const hasConsensusData = consensus && consensus.models && consensus.models.length > 0;
  const confidencePercent = consensus?.confidence ? (consensus.confidence * 100).toFixed(0) : null;

  return (
    <Card className="border-2 border-primary/20 bg-gradient-to-br from-background to-primary/5">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Multi-Model AI Consensus
            </CardTitle>
            <CardDescription>
              {hasConsensusData 
                ? `Analysis from ${consensus.models.length} AI models` 
                : 'AI-generated insights'
              }
            </CardDescription>
          </div>
          {onRegenerate && (
            <Button 
              variant="outline" 
              size="sm"
              onClick={onRegenerate}
              className="gap-2"
            >
              <Sparkles className="h-4 w-4" />
              Regenerate
            </Button>
          )}
        </div>

        {hasConsensusData && confidencePercent && (
          <div className="flex items-center gap-2 pt-2">
            <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className="h-full bg-primary transition-all"
                style={{ width: `${confidencePercent}%` }}
              />
            </div>
            <span className="text-sm font-medium text-muted-foreground">
              {confidencePercent}% confidence
            </span>
          </div>
        )}
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Majority Findings */}
        {majority.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <h4 className="font-semibold text-sm">Consensus Findings</h4>
              <Badge variant="secondary" className="ml-auto">
                {majority.length} findings
              </Badge>
            </div>
            <ul className="space-y-2">
              {majority.map((finding, idx) => (
                <li key={idx} className="flex gap-2 text-sm text-muted-foreground">
                  <span className="text-green-600 mt-0.5">•</span>
                  <span>{finding.replace(/^-\s*/, '')}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Niche Insights */}
        {nicheInsights.length > 0 && (
          <div className="space-y-3 p-4 rounded-lg bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900">
            <div className="flex items-center gap-2">
              <Info className="h-4 w-4 text-blue-600" />
              <h4 className="font-semibold text-sm text-blue-900 dark:text-blue-100">
                Niche Insights
              </h4>
              <Badge variant="default" className="ml-auto bg-blue-600">
                {nicheInsights.length} discovered
              </Badge>
            </div>
            <p className="text-xs text-blue-700 dark:text-blue-300">
              Minority findings validated through peer review - potential competitive advantages
            </p>
            <ul className="space-y-2">
              {nicheInsights.map((insight, idx) => (
                <li key={idx} className="flex gap-2 text-sm text-blue-900 dark:text-blue-100">
                  <span className="text-blue-600 mt-0.5">▸</span>
                  <span>{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Hallucinations */}
        {hallucinations.length > 0 && (
          <div className="space-y-3 p-4 rounded-lg bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              <h4 className="font-semibold text-sm text-amber-900 dark:text-amber-100">
                Rejected Claims
              </h4>
              <Badge variant="secondary" className="ml-auto bg-amber-100 text-amber-900">
                {hallucinations.length} filtered
              </Badge>
            </div>
            <p className="text-xs text-amber-700 dark:text-amber-300">
              Claims flagged as unsupported by peer review models
            </p>
            <ul className="space-y-2">
              {hallucinations.map((claim, idx) => (
                <li key={idx} className="flex gap-2 text-sm text-amber-900 dark:text-amber-100 opacity-75">
                  <span className="text-amber-600 mt-0.5">×</span>
                  <span>{claim}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Model Info */}
        {hasConsensusData && (
          <div className="pt-4 border-t border-border">
            <details className="group">
              <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground transition-colors">
                <span className="inline-flex items-center gap-1">
                  Models used
                  <span className="group-open:rotate-180 transition-transform">▼</span>
                </span>
              </summary>
              <div className="mt-2 space-y-1">
                {consensus.models.map((model, idx) => (
                  <div key={idx} className="text-xs font-mono text-muted-foreground">
                    {idx + 1}. {model.provider}/{model.model}
                  </div>
                ))}
              </div>
            </details>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ConsensusInsights;
