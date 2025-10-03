import React from "react";
import { useAssessment } from "../contexts/AssessmentContext";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card.jsx";
import { Progress } from "@/components/ui/progress.jsx";

const phases = [
  { id: "self_discovery", name: "Self Discovery" },
  { id: "idea_discovery", name: "Idea Discovery" },
  { id: "market_research", name: "Market Research" },
  { id: "business_pillars", name: "Business Pillars" },
  { id: "product_concept_testing", name: "Product Concept Testing" },
  { id: "business_development", name: "Business Development" },
  { id: "business_prototype_testing", name: "Business Prototype Testing" },
];

const AssessmentHistory = () => {
  const { assessmentData } = useAssessment();

  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <Card className="w-full max-w-3xl">
        <CardHeader>
          <CardTitle>Assessment History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {phases.map((phase) => {
              const data = assessmentData[phase.id] || {};
              return (
                <div key={phase.id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{phase.name}</span>
                    <span className="text-sm">
                      {data.completed ? "Completed" : `${data.progress || 0}%`}
                    </span>
                  </div>
                  <Progress value={data.progress || 0} className="h-2" />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AssessmentHistory;
