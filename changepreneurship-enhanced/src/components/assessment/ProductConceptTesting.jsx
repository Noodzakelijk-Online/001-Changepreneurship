import React, { useState } from "react";
import { PRODUCT_CONCEPT_TESTING_QUESTIONS } from "./ComprehensiveQuestionBank.jsx";
import { Lightbulb } from "lucide-react";
import { useAssessment } from "../../contexts/AssessmentContext";
import AssessmentShell from "./AssessmentShell";

const ProductConceptTesting = () => {
  const { updateResponse, completePhase, updatePhase } = useAssessment();
  const [sectionProgress, setSectionProgress] = useState({});
  const [responses, setResponses] = useState({ general: {} });

  const sections = [{
    id: 'general',
    title: 'Product Concept Testing',
    icon: Lightbulb,
    questions: PRODUCT_CONCEPT_TESTING_QUESTIONS,
  }];

  const handleResponse = (sectionId, questionId, answer) => {
    setResponses(prev => ({
      ...prev,
      [sectionId]: { ...prev[sectionId], [questionId]: answer }
    }));
    updateResponse('product_concept_testing', questionId, answer, sectionId);
    const answered = Object.keys({ ...(responses[sectionId] || {}), [questionId]: answer }).length;
    const total = PRODUCT_CONCEPT_TESTING_QUESTIONS.length;
    setSectionProgress({ general: Math.round((answered / total) * 100) });
  };

  return (
    <AssessmentShell
      phaseName="Product Concept Testing"
      phaseNumber={5}
      sections={sections}
      currentSection="general"
      onSectionChange={() => {}}
      responses={responses}
      onResponse={handleResponse}
      sectionProgress={sectionProgress}
      onNext={() => { completePhase('product_concept_testing'); updatePhase('business_development'); }}
      nextLabel="Next Phase: Business Development"
    />
  );
};

export default ProductConceptTesting;
