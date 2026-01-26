// Centralized copy for AI empty states and smart defaults
// Surfaces can request a scenario by key + readiness stage to receive copy, CTAs, helper tips.

export const AI_READINESS_STAGES = {
  BLANK: "blank", // user hasn't started assessments
  COLLECTING: "collecting", // some answers, but insufficient AI signal
  BUILDING: "building", // majority answered, waiting on insights or API data
  POLISHED: "polished" // data exists but API not responding; show reassurance
};

const defaultActions = {
  assessmentEntry: {
    label: "Start Self Discovery",
    to: "/assessment/self-discovery-assessment",
    tone: "primary"
  },
  continueJourney: {
    label: "Continue Assessment",
    to: "/assessment",
    tone: "primary"
  },
  openExecutiveSummary: {
    label: "Open Executive Summary",
    to: "/dashboard/executive-summary",
    tone: "default"
  },
  exploreInsightsHub: {
    label: "Explore AI Hub",
    to: "/ai-insights",
    tone: "secondary"
  }
};

const sampleInsight = {
  badge: "Sample Output",
  title: "Vision narrative is 72% confident",
  body: "Once you provide Self Discovery + Market Research responses, AI maps your founder profile and flags the strongest components of your go-to-market story."
};

export const AI_EMPTY_SCENARIOS = {
  recommendationsOverview: {
    [AI_READINESS_STAGES.BLANK]: {
      icon: "bulb",
      headline: "Let AI learn from your story",
      description: "Complete the Self Discovery phase so the recommendations engine understands your founder profile and can craft targeted next steps.",
      checklist: [
        "Answer at least 8 questions in Self Discovery",
        "Outline one business idea in Idea Discovery",
        "Optional: import Sarah Chen's dataset for demos"
      ],
      actions: [defaultActions.assessmentEntry, { ...defaultActions.exploreInsightsHub, tone: "ghost" }]
    },
    [AI_READINESS_STAGES.COLLECTING]: {
      icon: "sparkles",
      headline: "We need a bit more detail",
      description: "Great start! Add depth in Market Research or Business Pillars so AI can connect the dots and prioritize recommendations.",
      checklist: [
        "Finish at least two foundation phases",
        "Add traction metrics or customer quotes",
        "Tag your primary focus areas"
      ],
      actions: [defaultActions.continueJourney]
    },
    [AI_READINESS_STAGES.BUILDING]: {
      icon: "radar",
      headline: "Synthesizing your responses",
      description: "AI is preparing tailored plays from your latest answers. This usually takes under a minute after saving.",
      helper: sampleInsight,
      actions: [{ label: "Refresh in a moment", tone: "secondary" }]
    },
    [AI_READINESS_STAGES.POLISHED]: {
      icon: "shield",
      headline: "Using cached insights",
      description: "Your previous AI run is available below while we reconnect. Data stays safe.",
      helper: sampleInsight,
      actions: [{ label: "Retry now", tone: "secondary" }]
    }
  },
  executiveSummary: {
    [AI_READINESS_STAGES.BLANK]: {
      icon: "brain",
      headline: "Feed the AI Executive Summary",
      description: "Complete Self Discovery and Market Research to unlock a 9-component executive snapshot with readiness scores and investor-grade copy.",
      checklist: [
        "Complete Self Discovery",
        "Complete Market Research",
        "Add at least one traction metric"
      ],
      helper: sampleInsight,
      actions: [defaultActions.assessmentEntry]
    },
    [AI_READINESS_STAGES.COLLECTING]: {
      icon: "layers",
      headline: "Almost ready to score",
      description: "Just one more assessment (Business Pillars) will push you over the threshold for AI scoring.",
      checklist: [
        "Finish Business Pillars",
        "Review idea viability questions",
        "Update company vision paragraph"
      ],
      actions: [defaultActions.continueJourney]
    },
    [AI_READINESS_STAGES.BUILDING]: {
      icon: "loader",
      headline: "Generating your executive summary",
      description: "We are stitching together your multi-phase responses. Leave this tab open—AI writes a fresh summary shortly.",
      helper: sampleInsight,
      actions: [{ label: "Check again in 30s", tone: "secondary" }]
    },
    [AI_READINESS_STAGES.POLISHED]: {
      icon: "shield-check",
      headline: "Serving last known summary",
      description: "We could not reach the AI writer right now, but you still have access to your previous snapshot.",
      helper: sampleInsight,
      actions: [{ label: "Retry generation", tone: "secondary" }]
    }
  },
  insightsHubTile: {
    [AI_READINESS_STAGES.BLANK]: {
      icon: "lock",
      headline: "Unlock after first assessment",
      description: "AI features open as soon as you record your founder profile.",
      actions: [defaultActions.assessmentEntry]
    },
    [AI_READINESS_STAGES.COLLECTING]: {
      icon: "hourglass",
      headline: "Keep feeding the AI",
      description: "Complete one more phase to unlock this card.",
      actions: [defaultActions.continueJourney]
    }
  }
};

export function resolveAiEmptyScenario(surface, stage) {
  const scenario = AI_EMPTY_SCENARIOS[surface];
  if (!scenario) return null;
  return scenario[stage] || scenario[AI_READINESS_STAGES.BLANK] || null;
}
