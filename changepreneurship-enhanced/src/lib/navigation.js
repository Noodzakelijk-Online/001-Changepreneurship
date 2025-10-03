const SHORT_KEYS = { phase: 'p', tab: 't', section: 's', question: 'q' };

const first = (items) => (items && items.length ? items[0] : undefined);

const isNumeric = (value) =>
  typeof value === 'number' ||
  (typeof value === 'string' && value.trim() !== '' && !Number.isNaN(Number(value)));

const toNumber = (value) => {
  if (typeof value === 'number') return value;
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value);
    return Number.isNaN(parsed) ? undefined : parsed;
  }
  return undefined;
};

const parseSegment = (segment) => {
  if (segment === undefined || segment === null || segment === '') {
    return undefined;
  }
  if (isNumeric(segment)) {
    return toNumber(segment);
  }
  return segment;
};

const buildPath = (phaseNode, tabNode, sectionNode, questionNode) => ({
  phase: phaseNode?.code,
  phaseId: phaseNode?.id,
  tab: tabNode?.code,
  tabId: tabNode?.id,
  section: sectionNode?.code,
  sectionId: sectionNode?.id,
  question: questionNode?.code,
  questionId: questionNode?.id,
});

const resolveNode = (nodes = [], path = {}, key) => {
  if (!nodes.length) return undefined;
  const shortKey = SHORT_KEYS[key];
  const explicitId = path?.[`${key}Id`];
  const direct = path?.[key];
  const short = shortKey ? path?.[shortKey] : undefined;

  const idCandidates = [
    explicitId,
    typeof direct === 'string' && !isNumeric(direct) ? direct : undefined,
    typeof short === 'string' && !isNumeric(short) ? short : undefined,
  ].filter(Boolean);

  for (const candidate of idCandidates) {
    const match = nodes.find((node) => node?.id === candidate);
    if (match) return match;
  }

  const codeCandidates = [
    path?.[`${key}Code`],
    direct,
    short,
  ].filter((value) => value !== undefined && value !== null);

  for (const candidate of codeCandidates) {
    const values = [];
    if (candidate !== undefined && candidate !== null) {
      values.push(candidate);
      const numeric = toNumber(candidate);
      if (numeric !== undefined) values.push(numeric);
    }

    for (const value of values) {
      const match = nodes.find((node) => node?.code === value);
      if (match) return match;
    }
  }

  return nodes[0];
};

const resolveNormalizedNodes = (normalized, structure) => {
  const phaseNode =
    structure.find((phase) => phase.id === normalized.phaseId) ||
    structure.find((phase) => phase.code === normalized.phase);
  const tabNode =
    phaseNode?.tabs.find((tab) => tab.id === normalized.tabId) ||
    phaseNode?.tabs.find((tab) => tab.code === normalized.tab);
  const sectionNode =
    tabNode?.sections.find((section) => section.id === normalized.sectionId) ||
    tabNode?.sections.find((section) => section.code === normalized.section);
  const questionNode =
    sectionNode?.questions.find((question) => question.id === normalized.questionId) ||
    sectionNode?.questions.find((question) => question.code === normalized.question);

  return { phaseNode, tabNode, sectionNode, questionNode };
};

export function toCode({ phase, tab, section, question }) {
  return [phase, tab, section, question].join('.');
}

export function fromCode(code) {
  if (!code && code !== 0) {
    return {};
  }
  if (typeof code !== 'string') {
    return code ?? {};
  }
  const [phase, tab, section, question] = code.split('.');
  return {
    phase: parseSegment(phase),
    tab: parseSegment(tab),
    section: parseSegment(section),
    question: parseSegment(question),
  };
}

export function normalizePath(path = {}, structure = []) {
  if (!structure.length) return {};
  const phaseNode = resolveNode(structure, path, 'phase') || structure[0];
  const tabNode = resolveNode(phaseNode?.tabs, path, 'tab') || first(phaseNode?.tabs);
  const sectionNode =
    resolveNode(tabNode?.sections, path, 'section') || first(tabNode?.sections);
  const questionNode =
    resolveNode(sectionNode?.questions, path, 'question') || first(sectionNode?.questions);

  if (!phaseNode || !tabNode || !sectionNode || !questionNode) {
    return {};
  }

  return buildPath(phaseNode, tabNode, sectionNode, questionNode);
}

export function getNext(path, structure, level = 'question') {
  if (!structure.length) return {};
  const normalized = normalizePath(path, structure);
  const { phaseNode, tabNode, sectionNode, questionNode } =
    resolveNormalizedNodes(normalized, structure);

  if (!phaseNode || !tabNode || !sectionNode || !questionNode) {
    return normalized;
  }

  if (level === 'phase') {
    const pIndex = structure.findIndex((phase) => phase.id === phaseNode.id);
    if (pIndex >= 0 && pIndex < structure.length - 1) {
      const nextPhase = structure[pIndex + 1];
      const nextTab = first(nextPhase?.tabs);
      const nextSection = first(nextTab?.sections);
      const nextQuestion = first(nextSection?.questions);
      if (nextPhase && nextTab && nextSection && nextQuestion) {
        return buildPath(nextPhase, nextTab, nextSection, nextQuestion);
      }
    }
    return normalized;
  }

  if (level === 'tab') {
    const tabs = phaseNode.tabs || [];
    const tIndex = tabs.findIndex((tab) => tab.id === tabNode.id);
    if (tIndex >= 0 && tIndex < tabs.length - 1) {
      const nextTab = tabs[tIndex + 1];
      const nextSection = first(nextTab?.sections);
      const nextQuestion = first(nextSection?.questions);
      if (nextTab && nextSection && nextQuestion) {
        return buildPath(phaseNode, nextTab, nextSection, nextQuestion);
      }
    }
    return getNext(normalized, structure, 'phase');
  }

  if (level === 'section') {
    const sections = tabNode.sections || [];
    const sIndex = sections.findIndex((section) => section.id === sectionNode.id);
    if (sIndex >= 0 && sIndex < sections.length - 1) {
      const nextSection = sections[sIndex + 1];
      const nextQuestion = first(nextSection?.questions);
      if (nextSection && nextQuestion) {
        return buildPath(phaseNode, tabNode, nextSection, nextQuestion);
      }
    }
    return getNext(normalized, structure, 'tab');
  }

  const questions = sectionNode.questions || [];
  const qIndex = questions.findIndex((question) => question.id === questionNode.id);
  if (qIndex >= 0 && qIndex < questions.length - 1) {
    const nextQuestion = questions[qIndex + 1];
    return buildPath(phaseNode, tabNode, sectionNode, nextQuestion);
  }

  return getNext(normalized, structure, 'section');
}

export function getPrev(path, structure, level = 'question') {
  if (!structure.length) return {};
  const normalized = normalizePath(path, structure);
  const { phaseNode, tabNode, sectionNode, questionNode } =
    resolveNormalizedNodes(normalized, structure);

  if (!phaseNode || !tabNode || !sectionNode || !questionNode) {
    return normalized;
  }

  if (level === 'phase') {
    const pIndex = structure.findIndex((phase) => phase.id === phaseNode.id);
    if (pIndex > 0) {
      const prevPhase = structure[pIndex - 1];
      const prevTabs = prevPhase.tabs || [];
      const prevTab = prevTabs[prevTabs.length - 1];
      const prevSections = prevTab?.sections || [];
      const prevSection = prevSections[prevSections.length - 1];
      const prevQuestions = prevSection?.questions || [];
      const prevQuestion = prevQuestions[prevQuestions.length - 1];
      if (prevPhase && prevTab && prevSection && prevQuestion) {
        return buildPath(prevPhase, prevTab, prevSection, prevQuestion);
      }
    }
    return normalized;
  }

  if (level === 'tab') {
    const tabs = phaseNode.tabs || [];
    const tIndex = tabs.findIndex((tab) => tab.id === tabNode.id);
    if (tIndex > 0) {
      const prevTab = tabs[tIndex - 1];
      const prevSections = prevTab.sections || [];
      const prevSection = prevSections[prevSections.length - 1];
      const prevQuestions = prevSection?.questions || [];
      const prevQuestion = prevQuestions[prevQuestions.length - 1];
      if (prevTab && prevSection && prevQuestion) {
        return buildPath(phaseNode, prevTab, prevSection, prevQuestion);
      }
    }
    return getPrev(normalized, structure, 'phase');
  }

  if (level === 'section') {
    const sections = tabNode.sections || [];
    const sIndex = sections.findIndex((section) => section.id === sectionNode.id);
    if (sIndex > 0) {
      const prevSection = sections[sIndex - 1];
      const prevQuestions = prevSection.questions || [];
      const prevQuestion = prevQuestions[prevQuestions.length - 1];
      if (prevSection && prevQuestion) {
        return buildPath(phaseNode, tabNode, prevSection, prevQuestion);
      }
    }
    return getPrev(normalized, structure, 'tab');
  }

  const questions = sectionNode.questions || [];
  const qIndex = questions.findIndex((question) => question.id === questionNode.id);
  if (qIndex > 0) {
    const prevQuestion = questions[qIndex - 1];
    return buildPath(phaseNode, tabNode, sectionNode, prevQuestion);
  }

  return getPrev(normalized, structure, 'section');
}

export const getNextPhase = (path, structure) => getNext(path, structure, 'phase');
export const getPrevPhase = (path, structure) => getPrev(path, structure, 'phase');
export const getNextTab = (path, structure) => getNext(path, structure, 'tab');
export const getPrevTab = (path, structure) => getPrev(path, structure, 'tab');
export const getNextSection = (path, structure) => getNext(path, structure, 'section');
export const getPrevSection = (path, structure) => getPrev(path, structure, 'section');
export const getNextQuestion = (path, structure) => getNext(path, structure, 'question');
export const getPrevQuestion = (path, structure) => getPrev(path, structure, 'question');
