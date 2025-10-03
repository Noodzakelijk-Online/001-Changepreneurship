export async function getNavigationStructure() {
  const { SELF_DISCOVERY_QUESTIONS, SELF_DISCOVERY_NAVIGATION } = await import('../components/assessment/ComprehensiveQuestionBank.jsx');

  const sectionMap = Object.values(SELF_DISCOVERY_QUESTIONS).reduce((acc, section) => {
    acc[section.id] = {
      id: section.id,
      code: section.code,
      order: section.order,
      title: section.title || section.id,
      questions: [...section.questions]
        .sort((a, b) => a.order - b.order)
        .map((question) => ({
          id: question.id,
          code: question.code,
          order: question.order,
        })),
    };
    return acc;
  }, {});

  const phase = SELF_DISCOVERY_NAVIGATION;
  const tabs = phase.tabs
    .map((tab) => {
      const sectionIds = tab.sectionIds?.length
        ? tab.sectionIds
        : Object.keys(sectionMap);
      const sections = sectionIds
        .map((id) => sectionMap[id])
        .filter(Boolean);
      const orderedSections = (sections.length
        ? sections
        : Object.values(sectionMap)
      ).map((section) => ({ ...section }));

      if (!tab.sectionIds?.length) {
        orderedSections.sort((a, b) => a.order - b.order);
      }

      return {
        id: tab.id,
        code: tab.code,
        order: tab.order,
        title: tab.title,
        sections: orderedSections,
      };
    })
    .sort((a, b) => a.order - b.order);

  return [
    {
      id: phase.id,
      code: phase.code,
      order: phase.order,
      title: phase.title,
      tabs,
    },
  ];
}
