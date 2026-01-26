import { useMemo } from "react";
import { useAssessment } from "@/contexts/AssessmentContext.jsx";
import { PHASES } from "@/lib/assessmentPhases.js";
import { AI_READINESS_STAGES } from "@/lib/aiEmptyScenarios.js";

const COUNT_REQUIRED_FOR_READY = 3; // minimum completed phases for confident AI output

const countResponses = (phaseData = {}) => {
  if (!phaseData.responses) return 0;
  return Object.values(phaseData.responses).reduce((sum, block) => sum + Object.keys(block || {}).length, 0);
};

export default function useAiReadiness() {
  const { assessmentData = {}, getOverallProgress, getPhaseData } = useAssessment();

  return useMemo(() => {
    const totalProgress = typeof getOverallProgress === "function" ? getOverallProgress() : 0;
    const phaseEntries = Object.entries(assessmentData || {});
    const completedPhases = phaseEntries.filter(([, data]) => data?.completed).length;
    const answeredQuestions = phaseEntries.reduce((sum, [, data]) => sum + countResponses(data), 0);

    const selfDiscovery = getPhaseData ? getPhaseData("self_discovery") : assessmentData?.self_discovery;
    const hasFounderProfile = Boolean(selfDiscovery?.archetype || countResponses(selfDiscovery) >= 5);

    const readinessStage = resolveStage({
      totalProgress,
      completedPhases,
      answeredQuestions,
      hasFounderProfile
    });

    const nextPhaseMeta = PHASES.find((phase) => !assessmentData?.[phase.id]?.completed);

    return {
      readinessStage,
      stats: {
        totalProgress,
        completedPhases,
        answeredQuestions,
        hasFounderProfile,
        readyForExecutiveSummary: completedPhases >= COUNT_REQUIRED_FOR_READY
      },
      nextPhaseMeta
    };
  }, [assessmentData, getOverallProgress, getPhaseData]);
}

function resolveStage({ totalProgress, completedPhases, answeredQuestions, hasFounderProfile }) {
  if (!answeredQuestions || totalProgress < 5) {
    return AI_READINESS_STAGES.BLANK;
  }

  if (completedPhases < 2 || totalProgress < 45) {
    return AI_READINESS_STAGES.COLLECTING;
  }

  if (completedPhases >= COUNT_REQUIRED_FOR_READY && hasFounderProfile) {
    return AI_READINESS_STAGES.BUILDING;
  }

  return AI_READINESS_STAGES.COLLECTING;
}
