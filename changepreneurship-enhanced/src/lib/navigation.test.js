import test from 'node:test';
import assert from 'node:assert/strict';
import { fromCode, normalizePath } from './navigation.js';

const buildStructure = () => [
  {
    id: 'phase-5',
    code: 5,
    order: 1,
    title: 'Phase Five',
    tabs: [
      {
        id: 'tab-2',
        code: 2,
        order: 1,
        title: 'Tab Two',
        sections: [
          {
            id: 'section-a',
            code: 7,
            order: 1,
            title: 'Section A',
            questions: [
              { id: 'question-a', code: 3, order: 1 },
              { id: 'question-b', code: 4, order: 2 },
            ],
          },
        ],
      },
      {
        id: 'tab-3',
        code: 3,
        order: 2,
        title: 'Tab Three',
        sections: [
          {
            id: 'section-4',
            code: 4,
            order: 1,
            title: 'Section Four',
            questions: [
              { id: 'question-7', code: 7, order: 1 },
              { id: 'question-8', code: 8, order: 2 },
              { id: 'question-9', code: 9, order: 3 },
            ],
          },
          {
            id: 'section-x',
            code: 9,
            order: 2,
            title: 'Section X',
            questions: [
              { id: 'question-10', code: 10, order: 1 },
            ],
          },
        ],
      },
    ],
  },
];

test('normalizePath resolves the same question for deep links and stored ids after reordering', () => {
  const structure = buildStructure();
  const deepLink = fromCode('5.3.4.8');
  const storedLocation = {
    phaseId: 'phase-5',
    tabId: 'tab-3',
    sectionId: 'section-4',
    questionId: 'question-8',
  };

  const initialDeepLinkPath = normalizePath(deepLink, structure);
  const initialStoredPath = normalizePath(storedLocation, structure);

  assert.equal(initialDeepLinkPath.questionId, 'question-8');
  assert.equal(initialStoredPath.questionId, 'question-8');

  // Reorder tabs and sections to ensure we rely on stable ids/codes rather than index order.
  structure[0].tabs.reverse();
  structure[0].tabs.forEach((tab) => {
    tab.sections.reverse();
  });

  const reorderedDeepLinkPath = normalizePath(deepLink, structure);
  const reorderedStoredPath = normalizePath(storedLocation, structure);

  assert.equal(reorderedDeepLinkPath.questionId, 'question-8');
  assert.equal(reorderedStoredPath.questionId, 'question-8');

  assert.equal(reorderedDeepLinkPath.phase, 5);
  assert.equal(reorderedStoredPath.tab, 3);
});
