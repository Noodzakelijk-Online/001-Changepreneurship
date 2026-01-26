import React from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card.jsx";
import { Badge } from "@/components/ui/badge.jsx";
import { Button } from "@/components/ui/button.jsx";
import { cn } from "@/lib/utils.js";
import {
  Brain,
  Lightbulb,
  Sparkles,
  Shield,
  ShieldCheck,
  Loader2,
  Layers,
  Lock,
  Hourglass,
  Radar,
  AlertOctagon
} from "lucide-react";

const ICON_MAP = {
  brain: Brain,
  bulb: Lightbulb,
  sparkles: Sparkles,
  shield: Shield,
  "shield-check": ShieldCheck,
  loader: Loader2,
  layers: Layers,
  lock: Lock,
  hourglass: Hourglass,
  radar: Radar,
  warning: AlertOctagon
};

const toneStyles = {
  primary: "bg-primary text-primary-foreground hover:bg-primary/90",
  secondary: "bg-muted text-foreground hover:bg-muted/80",
  ghost: "bg-transparent border border-dashed border-gray-700 text-muted-foreground hover:bg-gray-800/40",
  default: "",
  outline: "border border-gray-600 text-gray-200"
};

const SmartEmptyState = ({ scenario, metrics = [], className = "", onRetry }) => {
  const navigate = useNavigate();
  if (!scenario) return null;
  const Icon = ICON_MAP[scenario.icon] || Sparkles;

  const renderAction = (action, idx) => {
    if (!action) return null;
    const handleClick = () => {
      if (action.to) navigate(action.to);
      if (action.onClick) action.onClick();
      if (action.tone === "secondary" && onRetry) onRetry();
    };

    return (
      <Button
        key={`${action.label}-${idx}`}
        size="sm"
        className={cn("w-full sm:w-auto", toneStyles[action.tone] || toneStyles.primary)}
        disabled={action.disabled}
        onClick={handleClick}
      >
        {action.label}
      </Button>
    );
  };

  return (
    <Card className={cn("bg-gray-900 border-gray-800", className)}>
      <CardHeader className="flex flex-col gap-4">
        <div className="flex items-center gap-4">
          <div className="rounded-2xl bg-primary/10 p-3">
            <Icon className="h-6 w-6 text-primary" />
          </div>
          <div>
            <CardTitle className="text-xl text-white">{scenario.headline}</CardTitle>
            {scenario.description && (
              <CardDescription className="text-gray-400">
                {scenario.description}
              </CardDescription>
            )}
          </div>
        </div>

        {scenario.helper && (
          <div className="rounded-xl border border-dashed border-purple-700/40 bg-purple-900/10 p-4 text-sm text-purple-100">
            <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-purple-300">
              <Badge variant="outline" className="border-purple-500/50 text-purple-200">
                {scenario.helper.badge || "Example"}
              </Badge>
              <span>{scenario.helper.title}</span>
            </div>
            <p className="mt-2 text-sm text-purple-100">{scenario.helper.body}</p>
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-6">
        {scenario.checklist && scenario.checklist.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-semibold text-gray-300">To unlock this view:</p>
            <ul className="space-y-2">
              {scenario.checklist.map((item, index) => (
                <li key={index} className="flex items-center gap-3 text-sm text-gray-400">
                  <span className="h-2 w-2 rounded-full bg-primary" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        {metrics.length > 0 && (
          <div className="grid gap-3 sm:grid-cols-3">
            {metrics.map((metric, index) => (
              <div key={index} className="rounded-xl border border-gray-800 bg-gray-800/40 p-3">
                <p className="text-xs text-gray-500">{metric.label}</p>
                <p className="text-lg font-semibold text-white">{metric.value}</p>
                {metric.helper && <p className="text-xs text-gray-400">{metric.helper}</p>}
              </div>
            ))}
          </div>
        )}

        {scenario.actions && scenario.actions.length > 0 && (
          <div className="flex flex-col gap-3 sm:flex-row">
            {scenario.actions.map((action, idx) => renderAction(action, idx))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SmartEmptyState;
