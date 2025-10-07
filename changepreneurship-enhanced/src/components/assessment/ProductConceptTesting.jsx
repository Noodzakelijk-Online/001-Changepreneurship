import React, { useState } from "react";
import { PRODUCT_CONCEPT_TESTING_QUESTIONS } from "./ComprehensiveQuestionBank.jsx";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card.jsx";
import { Badge } from "@/components/ui/badge.jsx";
import { Textarea } from "@/components/ui/textarea.jsx";
import { Input } from "@/components/ui/input.jsx";
import { Lightbulb, CheckCircle } from "lucide-react";

const ProductConceptTesting = () => {
  const [responses, setResponses] = useState({});

  const handleChange = (id, value) => {
    setResponses((prev) => ({ ...prev, [id]: value }));
  };

  return (
    <div className="space-y-6">
      <Card className="border-l-4 border-l-primary">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-xl flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-primary" /> Product Concept Testing
              </CardTitle>
              <CardDescription className="mt-1">Validate product concepts with real customer feedback</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-8">
          {PRODUCT_CONCEPT_TESTING_QUESTIONS.map((q, idx) => {
            const answered = responses[q.id];
            return (
              <Card key={q.id} className="border relative">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <Badge variant="secondary">Question {idx + 1} of {PRODUCT_CONCEPT_TESTING_QUESTIONS.length}</Badge>
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
    </div>
  );
};

export default ProductConceptTesting;
