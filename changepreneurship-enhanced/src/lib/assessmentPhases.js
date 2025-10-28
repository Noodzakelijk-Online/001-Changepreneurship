// Centralized assessment phase metadata and slug mapping
// This avoids duplication across LandingPage, App routing and AssessmentPage logic.

export const PHASES = [
  {
    id: 'self_discovery',
    slug: 'self-discovery-assessment',
    title: 'Self Discovery',
    landingTitle: 'Self-Discovery Assessment',
    duration: '60-90 minutes',
    category: 'Foundation & Strategy'
  },
  {
    id: 'idea_discovery',
    slug: 'idea-discovery',
    title: 'Idea Discovery',
    duration: '90-120 minutes',
    category: 'Foundation & Strategy'
  },
  {
    id: 'market_research',
    slug: 'market-research',
    title: 'Market Research',
    duration: '2-3 weeks',
    category: 'Foundation & Strategy'
  },
  {
    id: 'business_pillars',
    slug: 'business-pillars-planning',
    title: 'Business Pillars',
    landingTitle: 'Business Pillars Planning',
    duration: '1-2 weeks',
    category: 'Foundation & Strategy'
  },
  {
    id: 'product_concept_testing',
    slug: 'product-concept-testing',
    title: 'Product Concept Testing',
    duration: '2-4 weeks',
    category: 'Implementation & Testing'
  },
  {
    id: 'business_development',
    slug: 'business-development',
    title: 'Business Development',
    duration: '1-2 weeks',
    category: 'Implementation & Testing'
  },
  {
    id: 'business_prototype_testing',
    slug: 'business-prototype-testing',
    title: 'Business Prototype Testing',
    duration: '3-6 weeks',
    category: 'Implementation & Testing'
  }
];

const slugMap = PHASES.reduce((acc, p) => { acc[p.slug] = p.id; return acc; }, {});
const idToSlug = PHASES.reduce((acc, p) => { acc[p.id] = p.slug; return acc; }, {});

export const slugToPhaseId = (slug) => slugMap[slug] || null;
export const phaseIdToSlug = (id) => idToSlug[id] || null;

export function getPhaseMeta(id) {
  return PHASES.find(p => p.id === id) || null;
}
