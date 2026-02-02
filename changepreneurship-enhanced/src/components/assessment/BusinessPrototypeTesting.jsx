import React, { useState } from "react";
import { BUSINESS_PROTOTYPE_TESTING_QUESTIONS } from "./ComprehensiveQuestionBank.jsx";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card.jsx";
import { Badge } from "@/components/ui/badge.jsx";
import { Button } from "@/components/ui/button.jsx";
import { Textarea } from "@/components/ui/textarea.jsx";
import { Input } from "@/components/ui/input.jsx";
import { Lightbulb, CheckCircle, Check } from "lucide-react";
import { useAssessment } from "../../contexts/AssessmentContext";
import { useNavigate } from "react-router-dom";

const BusinessPrototypeTesting = () => {
  const [responses, setResponses] = useState({});
  const { updateResponse, completePhase } = useAssessment();
  const navigate = useNavigate();

  const handleChange = (id, value) => {
    setResponses((prev) => ({ ...prev, [id]: value }));
    // Save to backend immediately
    updateResponse('business_prototype_testing', id, value, 'general');
  };

  const handleSubmit = () => {
    // Mark phase as complete
    completePhase('business_prototype_testing');
    
    // Navigate to dashboard
    navigate('/dashboard');
  };

  // Calculate completion
  const answeredCount = Object.keys(responses).filter(key => responses[key]?.trim()).length;
  const totalQuestions = BUSINESS_PROTOTYPE_TESTING_QUESTIONS.length;
  const isComplete = answeredCount === totalQuestions;

  return (
    <div className="space-y-6">
      <Card className="border-l-4 border-l-primary">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-xl flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-primary" /> Business Prototype Testing
              </CardTitle>
              <CardDescription className="mt-1">Complete business model validation in real market conditions</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-8">
          {BUSINESS_PROTOTYPE_TESTING_QUESTIONS.map((q, idx) => {
            const answered = responses[q.id];
            return (
              <Card key={q.id} className="border relative">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <Badge variant="secondary">Question {idx + 1} of {BUSINESS_PROTOTYPE_TESTING_QUESTIONS.length}</Badge>
                        {q.required && <Badge variant="destructive">Required</Badge>}
                      </div>
                      <CardTitle className="text-base font-semibold leading-snug">
                        {q.question}
                      </CardTitle>
                    </div>
                    {answered && <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />}
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  {q.type === 'textarea' && (
                    <Textarea
                      rows={4}
                      placeholder="Enter your response..."
                      value={responses[q.id] || ''}
                      onChange={(e) => handleChange(q.id, e.target.value)}
                      className="mt-2"
                    />
                  )}
                  {q.type === 'text' && (
                    <Input
                      placeholder="Enter answer..."
                      value={responses[q.id] || ''}
                      onChange={(e) => handleChange(q.id, e.target.value)}
                      className="mt-2"
                    />
                  )}
                </CardContent>
              </Card>
            );
          })}
        </CardContent>
      </Card>

      {/* Submit Button */}
      <Card className="border-dashed border-2 border-orange-500 bg-orange-50 dark:bg-orange-950/20">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                isComplete ? 'bg-green-500' : 'bg-orange-500'
              }`}>
                {isComplete ? (
                  <Check className="h-6 w-6 text-white" />
                ) : (
                  <span className="text-white font-bold">{answeredCount}/{totalQuestions}</span>
                )}
              </div>
              <div>
                <h3 className="font-semibold text-lg">
                  {isComplete ? '🎉 Assessment Complete!' : 'Complete Final Phase'}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {isComplete 
                    ? 'Submit to finish all 7 phases and unlock AI insights'
                    : `Answer all ${totalQuestions} questions to complete your entrepreneurial journey`
                  }
                </p>
              </div>
            </div>
            <Button
              size="lg"
              onClick={handleSubmit}
              disabled={!isComplete}
              className="bg-orange-600 hover:bg-orange-700 text-white px-8"
            >
              {isComplete ? 'Submit Assessment' : 'Complete All Questions'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default BusinessPrototypeTesting;
