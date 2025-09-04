import React from "react";
import { Card, CardContent } from "@/components/ui/card.jsx";
import { Button } from "@/components/ui/button.jsx";
import { Badge } from "@/components/ui/badge.jsx";
import { Zap } from "lucide-react";

export default function DataImportBanner({ onOptimize, onDismiss }) {
  return (
    <Card className="border-2 border-orange-400/70">
      <CardContent className="p-5 md:p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="rounded-xl bg-orange-500/15 p-2">
              <Zap className="h-5 w-5 text-orange-500" />
            </div>
            <div>
              <div className="font-semibold">Speed Up Your Assessment</div>
              <p className="text-sm text-muted-foreground">
                Connect your data sources to pre-populate answers and save time
              </p>
            </div>
          </div>

          <button
            onClick={onDismiss}
            className="text-muted-foreground hover:text-foreground text-sm"
          >
            ✕
          </button>
        </div>

        <div className="mt-4 grid gap-4 md:grid-cols-3 bg-muted/40 rounded-lg p-4">
          <Stat
            label="Estimated Time"
            value="60min"
            className="text-orange-500"
          />
          <Stat label="Time Saved" value="0min" className="text-green-500" />
          <Stat label="Pre-populated" value="0%" className="text-blue-500" />
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <Badge variant="outline" className="px-3 py-1 cursor-pointer">
            LinkedIn Profile
          </Badge>
          <Badge variant="outline" className="px-3 py-1 cursor-pointer">
            $ Financial Data
          </Badge>
          <Badge variant="outline" className="px-3 py-1 cursor-pointer">
            Resume / CV
          </Badge>
        </div>

        <div className="mt-4 flex flex-col sm:flex-row gap-2">
          <Button
            className="flex-1"
            onClick={() => onOptimize?.(["linkedin", "financial"])}
          >
            Start Optimized Assessment
          </Button>
          <Button className="flex-1" variant="secondary">
            Continue Without Optimization
          </Button>
        </div>

        <p className="mt-3 text-xs text-muted-foreground">
          💡 Users typically save 40–75% of assessment time with data import
        </p>
      </CardContent>
    </Card>
  );
}

const Stat = ({ label, value, className = "" }) => (
  <div className="rounded-lg bg-card/60 border p-3">
    <div className={`text-2xl font-bold ${className}`}>{value}</div>
    <div className="text-xs text-muted-foreground">{label}</div>
  </div>
);
