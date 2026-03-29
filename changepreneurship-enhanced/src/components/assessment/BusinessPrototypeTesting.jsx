import React, { useState, useEffect } from "react";
import { BUSINESS_PROTOTYPE_TESTING_QUESTIONS } from "./ComprehensiveQuestionBank.jsx";
import { Lightbulb } from "lucide-react";
import { useAssessment } from "../../contexts/AssessmentContext";
import { useNavigate } from "react-router-dom";
import AssessmentShell from "./AssessmentShell";

const BusinessPrototypeTesting = () => {
  const { assessmentData, updateResponse, completePhase } = useAssessment();
  const navigate = useNavigate();
  const [sectionProgress, setSectionProgress] = useState({});
  const phaseData = assessmentData['business_prototype_testing'] || {};
  const responses = phaseData.responses || {};

  useEffect(() => {
    const answered = Object.keys(responses.general || {}).length;
    setSectionProgress({ general: Math.round((answered / BUSINESS_PROTOTYPE_TESTING_QUESTIONS.length) * 100) });
  }, [phaseData]);

  const sections = [{
    id: 'general',
    title: 'Prototype Testing',
    icon: Lightbulb,
    questions: BUSINESS_PROTOTYPE_TESTING_QUESTIONS,
  }];

  const handleResponse = (sectionId, questionId, answer) => {
    updateResponse('business_prototype_testing', questionId, answer, sectionId);
    const answered = Object.keys({ ...(responses[sectionId] || {}), [questionId]: answer }).length;
    const total = BUSINESS_PROTOTYPE_TESTING_QUESTIONS.length;
    setSectionProgress({ general: Math.round((answered / total) * 100) });
  };

  return (
    <AssessmentShell
      phaseName="Business Prototype Testing"
      phaseNumber={7}
      sections={sections}
      currentSection="general"
      onSectionChange={() => {}}
      responses={responses}
      onResponse={handleResponse}
      sectionProgress={sectionProgress}
      onNext={() => completePhase('business_prototype_testing', () => navigate('/dashboard'))}
      nextLabel="Complete Assessment"
    />
  );
};

export default BusinessPrototypeTesting;
