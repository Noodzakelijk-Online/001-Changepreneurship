import { validateQuestionnaire } from "./lib/schema.js";

let questionnaireCache = null;

export async function fetchQuestionnaire() {
  if (questionnaireCache) return questionnaireCache;
  const res = await fetch("/questionnaire.json");
  const data = await res.json();
  questionnaireCache = validateQuestionnaire(data);
  return questionnaireCache;
}

export async function fetchPhase(phaseId) {
  const q = await fetchQuestionnaire();
  return q.phases.find((p) => p.id === phaseId);
}

export async function fetchTab(phaseId, tabId) {
  const phase = await fetchPhase(phaseId);
  return phase?.tabs?.find((t) => t.id === tabId);
}

export async function fetchSection(phaseId, tabId, sectionId) {
  const tab = await fetchTab(phaseId, tabId);
  return tab?.sections?.find((s) => s.id === sectionId);
}
