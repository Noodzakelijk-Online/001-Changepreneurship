import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Heart, Target, Lightbulb, TrendingUp, CheckCircle } from 'lucide-react';

const PurposeDiscovery = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [fiveWhysResponses, setFiveWhysResponses] = useState(['', '', '', '', '']);
  const [legacyResponses, setLegacyResponses] = useState(['', '', '', '', '']);
  const [values, setValues] = useState([]);
  const [vision, setVision] = useState('');
  const [impactAreas, setImpactAreas] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const fiveWhysQuestions = [
    'What motivates you to start a business?',
    'Why is that important to you?',
    'Why does that matter in your life?',
    'What deeper need does this fulfill?',
    'What is the ultimate impact you want to make?'
  ];

  const legacyPrompts = [
    'How do you want to be remembered?',
    'What problem in the world keeps you up at night?',
    'If you could solve one major challenge, what would it be?',
    'What would success look like in 20 years?',
    'What legacy do you want to leave behind?'
  ];

  const impactCategories = [
    'Environmental Impact',
    'Social Impact',
    'Economic Impact',
    'Educational Impact',
    'Health & Wellness Impact',
    'Technology Innovation Impact'
  ];

  const coreValues = [
    'Integrity',
    'Innovation',
    'Excellence',
    'Collaboration',
    'Sustainability',
    'Empowerment',
    'Transparency',
    'Respect',
    'Growth',
    'Impact'
  ];

  const handleFiveWhysSubmit = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/purpose-discovery/five-whys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ responses: fiveWhysResponses })
      });
      const result = await response.json();
      if (result.success) {
        setAnalysis(prev => ({ ...prev, fiveWhys: result.data }));
        setCurrentStep(1);
      }
    } catch (error) {
      console.error('Error processing 5 Whys:', error);
    }
    setLoading(false);
  };

  const handleLegacySubmit = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/purpose-discovery/legacy-statement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ legacy_responses: legacyResponses, values, vision })
      });
      const result = await response.json();
      if (result.success) {
        setAnalysis(prev => ({ ...prev, legacy: result.data }));
        setCurrentStep(2);
      }
    } catch (error) {
      console.error('Error creating legacy statement:', error);
    }
    setLoading(false);
  };

  const handleImpactSubmit = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/purpose-discovery/impact-visualization', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          impact_areas: impactAreas,
          scale: { [impactAreas[0]]: 8, [impactAreas[1]]: 6 },
          timeline: { 'Year 1': 'Foundation', 'Year 3': 'Growth', 'Year 5': 'Scale' }
        })
      });
      const result = await response.json();
      if (result.success) {
        setAnalysis(prev => ({ ...prev, impact: result.data }));
        setCurrentStep(3);
      }
    } catch (error) {
      console.error('Error creating impact visualization:', error);
    }
    setLoading(false);
  };

  const toggleValue = value => {
    setValues(prev =>
      prev.includes(value)
        ? prev.filter(v => v !== value)
        : [...prev, value].slice(0, 5)
    );
  };

  const toggleImpactArea = area => {
    setImpactAreas(prev =>
      prev.includes(area)
        ? prev.filter(a => a !== area)
        : [...prev, area].slice(0, 3)
    );
  };

  const renderFiveWhys = () => (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-6 w-6 text-blue-600" />
          The 5 Whys Exercise
        </CardTitle>
        <CardDescription>
          Drill down to discover your core motivations and purpose
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {fiveWhysQuestions.map((question, index) => (
          <div key={index} className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              {index + 1}. {question}
            </label>
            <Textarea
              value={fiveWhysResponses[index]}
              onChange={e => {
                const newResponses = [...fiveWhysResponses];
                newResponses[index] = e.target.value;
                setFiveWhysResponses(newResponses);
              }}
              placeholder="Take your time to reflect deeply..."
              className="min-h-[100px]"
            />
          </div>
        ))}
        <Button
          onClick={handleFiveWhysSubmit}
          disabled={loading || fiveWhysResponses.some(r => !r.trim())}
          className="w-full"
        >
          {loading ? 'Analyzing...' : 'Analyze My Purpose'}
        </Button>
      </CardContent>
    </Card>
  );

  const renderLegacyBuilder = () => (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Heart className="h-6 w-6 text-red-600" />
          Legacy Statement Builder
        </CardTitle>
        <CardDescription>
          Define the legacy you want to leave and the values that guide you
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <Tabs defaultValue="legacy" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="legacy">Legacy Vision</TabsTrigger>
            <TabsTrigger value="values">Core Values</TabsTrigger>
            <TabsTrigger value="vision">Vision Statement</TabsTrigger>
          </TabsList>

          <TabsContent value="legacy" className="space-y-4">
            {legacyPrompts.map((prompt, index) => (
              <div key={index} className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  {prompt}
                </label>
                <Textarea
                  value={legacyResponses[index]}
                  onChange={e => {
                    const newResponses = [...legacyResponses];
                    newResponses[index] = e.target.value;
                    setLegacyResponses(newResponses);
                  }}
                  placeholder="Reflect on your long-term impact..."
                  className="min-h-[80px]"
                />
              </div>
            ))}
          </TabsContent>

          <TabsContent value="values" className="space-y-4">
            <p className="text-sm text-gray-600">Select up to 5 core values that guide your decisions:</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {coreValues.map(value => (
                <Badge
                  key={value}
                  variant={values.includes(value) ? 'default' : 'outline'}
                  className="cursor-pointer p-2 text-center"
                  onClick={() => toggleValue(value)}
                >
                  {value}
                </Badge>
              ))}
            </div>
            <p className="text-xs text-gray-500">Selected: {values.length}/5</p>
          </TabsContent>

          <TabsContent value="vision" className="space-y-4">
            <label className="text-sm font-medium text-gray-700">
              Your Vision Statement
            </label>
            <Textarea
              value={vision}
              onChange={e => setVision(e.target.value)}
              placeholder="Describe the future you want to create..."
              className="min-h-[120px]"
            />
          </TabsContent>
        </Tabs>

        <Button
          onClick={handleLegacySubmit}
          disabled={loading || !vision.trim() || values.length === 0}
          className="w-full"
        >
          {loading ? 'Creating Legacy Statement...' : 'Create Legacy Statement'}
        </Button>
      </CardContent>
    </Card>
  );

  const renderImpactVisualization = () => (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-6 w-6 text-green-600" />
          Impact Visualization
        </CardTitle>
        <CardDescription>
          Visualize the positive impact your business could have on the world
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <label className="text-sm font-medium text-gray-700 mb-3 block">
            Select up to 3 impact areas you're passionate about:
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {impactCategories.map(area => (
              <Card
                key={area}
                className={`cursor-pointer transition-all ${
                  impactAreas.includes(area) ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                }`}
                onClick={() => toggleImpactArea(area)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{area}</span>
                    {impactAreas.includes(area) && <CheckCircle className="h-5 w-5 text-blue-600" />}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">Selected: {impactAreas.length}/3</p>
        </div>

        <Button
          onClick={handleImpactSubmit}
          disabled={loading || impactAreas.length === 0}
          className="w-full"
        >
          {loading ? 'Creating Impact Visualization...' : 'Visualize My Impact'}
        </Button>
      </CardContent>
    </Card>
  );

  const renderResults = () => (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-6 w-6 text-yellow-600" />
            Your Purpose Discovery Results
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {analysis?.fiveWhys && (
            <div>
              <h3 className="font-semibold mb-3">Core Purpose Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Purpose Clarity Score</h4>
                  <div className="flex items-center gap-2">
                    <Progress value={analysis.fiveWhys.purpose_clarity_score * 10} className="flex-1" />
                    <span className="text-sm font-medium">{analysis.fiveWhys.purpose_clarity_score}/10</span>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Recommended Focus Areas</h4>
                  <div className="flex flex-wrap gap-1">
                    {analysis.fiveWhys.recommended_focus_areas?.map(area => (
                      <Badge key={area} variant="secondary" className="text-xs">
                        {area}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {analysis?.legacy && (
            <div>
              <h3 className="font-semibold mb-3">Your Legacy Statement</h3>
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-blue-900 font-medium">{analysis.legacy.statement}</p>
              </div>
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Action Items</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  {analysis.legacy.action_items?.map((item, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-blue-600">•</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {analysis?.impact && (
            <div>
              <h3 className="font-semibold mb-3">Impact Visualization</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(analysis.impact.stakeholder_analysis || {}).map(([area, stakeholders]) => (
                  <Card key={area}>
                    <CardContent className="p-4">
                      <h4 className="font-medium mb-2">{area}</h4>
                      <div className="space-y-1">
                        {stakeholders.map(stakeholder => (
                          <Badge key={stakeholder} variant="outline" className="text-xs mr-1">
                            {stakeholder}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );

  const steps = [
    { title: '5 Whys Exercise', component: renderFiveWhys },
    { title: 'Legacy Builder', component: renderLegacyBuilder },
    { title: 'Impact Visualization', component: renderImpactVisualization },
    { title: 'Results', component: renderResults }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Purpose Discovery Journey</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Uncover your deep purpose and align your business with your personal mission. This journey will help you build a foundation for meaningful entrepreneurship.
          </p>
        </div>

        <div className="flex justify-center mb-8">
          <div className="flex items-center space-x-4">
            {steps.map((step, index) => (
              <div key={index} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    index <= currentStep ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {index + 1}
                </div>
                <span className="ml-2 text-sm font-medium text-gray-700">{step.title}</span>
                {index < steps.length - 1 && (
                  <div
                    className={`w-12 h-0.5 mx-4 ${index < currentStep ? 'bg-blue-600' : 'bg-gray-200'}`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-center">{steps[currentStep].component()}</div>
      </div>
    </div>
  );
};

export default PurposeDiscovery;

