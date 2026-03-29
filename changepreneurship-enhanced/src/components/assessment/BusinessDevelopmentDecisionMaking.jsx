import React, { useState, useEffect } from "react";
import { BUSINESS_DEVELOPMENT_QUESTIONS } from "./ComprehensiveQuestionBank.jsx";
import { TrendingUp } from "lucide-react";
import { useAssessment } from "../../contexts/AssessmentContext";
import AssessmentShell from "./AssessmentShell";

const BusinessDevelopmentDecisionMaking = () => {
  const { assessmentData, updateResponse, completePhase, updatePhase } = useAssessment();
  const [sectionProgress, setSectionProgress] = useState({});
  const phaseData = assessmentData['business_development'] || {};
  const responses = phaseData.responses || {};

  useEffect(() => {
    const answered = Object.keys(responses.general || {}).length;
    setSectionProgress({ general: Math.round((answered / BUSINESS_DEVELOPMENT_QUESTIONS.length) * 100) });
  }, [phaseData]);

  const sections = [{
    id: 'general',
    title: 'Business Development',
    icon: TrendingUp,
    questions: BUSINESS_DEVELOPMENT_QUESTIONS,
  }];

  const handleResponse = (sectionId, questionId, answer) => {
    updateResponse('business_development', questionId, answer, sectionId);
    const answered = Object.keys({ ...(responses[sectionId] || {}), [questionId]: answer }).length;
    const total = BUSINESS_DEVELOPMENT_QUESTIONS.length;
    setSectionProgress({ general: Math.round((answered / total) * 100) });
  };

  return (
    <AssessmentShell
      phaseName="Business Development"
      phaseNumber={6}
      sections={sections}
      currentSection="general"
      onSectionChange={() => {}}
      responses={responses}
      onResponse={handleResponse}
      sectionProgress={sectionProgress}
      onNext={() => completePhase('business_development', () => updatePhase('business_prototype_testing'))}
      nextLabel="Next Phase: Business Prototype Testing"
    />
  );
};

export default BusinessDevelopmentDecisionMaking;
