import React, { useState, useEffect } from "react";
import { PRODUCT_CONCEPT_TESTING_QUESTIONS } from "./ComprehensiveQuestionBank.jsx";
import { Lightbulb } from "lucide-react";
import { useAssessment } from "../../contexts/AssessmentContext";
import AssessmentShell from "./AssessmentShell";

const ProductConceptTesting = () => {
  const { assessmentData, updateResponse, completePhase, updatePhase } = useAssessment();
  const [sectionProgress, setSectionProgress] = useState({});
  const phaseData = assessmentData['product_concept_testing'] || {};
  const responses = phaseData.responses || {};

  useEffect(() => {
    const answered = Object.keys(responses.general || {}).length;
    setSectionProgress({ general: Math.round((answered / PRODUCT_CONCEPT_TESTING_QUESTIONS.length) * 100) });
  }, [phaseData]);

  const sections = [{
    id: 'general',
    title: 'Product Concept Testing',
    icon: Lightbulb,
    questions: PRODUCT_CONCEPT_TESTING_QUESTIONS,
  }];

  const handleResponse = (sectionId, questionId, answer) => {
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
      onNext={() => completePhase('product_concept_testing', () => updatePhase('business_development'))}
      nextLabel="Next Phase: Business Development"
    />
  );
};

export default ProductConceptTesting;
