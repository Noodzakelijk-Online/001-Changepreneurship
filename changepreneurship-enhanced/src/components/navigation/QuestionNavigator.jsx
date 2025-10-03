import React, { useEffect, useState, Suspense } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useNavigation } from '../../contexts/NavigationContext.jsx';
import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator } from '../ui/breadcrumb.jsx';
import { Button } from '../ui/button.jsx';
import {
  fromCode,
  toCode,
  getNextPhase,
  getPrevPhase,
  getNextTab,
  getPrevTab,
  getNextSection,
  getPrevSection,
  getNextQuestion,
  getPrevQuestion,
} from '../../lib/navigation.js';

const QuestionNavigator = () => {
  const params = useParams();
  const navigate = useNavigate();
  const { structure, path, navigateTo, markVisited, progress } = useNavigation();
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    if (!structure.length) return;
    let target;
    if (params.code) {
      target = fromCode(params.code);
    } else if (params.phase) {
      target = {
        phase: parseInt(params.phase, 10),
        tab: parseInt(params.tab, 10),
        section: parseInt(params.section, 10),
        question: parseInt(params.question, 10),
      };
    }
    navigateTo(target);
  }, [params, structure, navigateTo]);

  useEffect(() => {
    if (!structure.length || !path) return;
    const long = `/phase/${path.phase}/tab/${path.tab}/section/${path.section}/question/${path.question}`;
    navigate(long, { replace: true });
  }, [path, structure, navigate]);

  const phaseNode =
    structure.find((p) => p.id === path?.phaseId) ||
    structure.find((p) => p.code === path?.phase);
  const tabNode =
    phaseNode?.tabs.find((t) => t.id === path?.tabId) ||
    phaseNode?.tabs.find((t) => t.code === path?.tab);
  const sectionNode =
    tabNode?.sections.find((s) => s.id === path?.sectionId) ||
    tabNode?.sections.find((s) => s.code === path?.section);
  const questionNode =
    sectionNode?.questions.find((q) => q.id === path?.questionId) ||
    sectionNode?.questions.find((q) => q.code === path?.question);

  useEffect(() => {
    if (questionNode) markVisited(questionNode.id);
  }, [questionNode, markVisited]);

  useEffect(() => {
    if (!sectionNode) return;
    let mounted = true;
    import('../../components/assessment/ComprehensiveQuestionBank.jsx').then(({ SELF_DISCOVERY_QUESTIONS }) => {
      const sectionData = SELF_DISCOVERY_QUESTIONS[sectionNode.id];
      const data = sectionData?.questions || [];
      if (mounted) setQuestions(data);
    });
    return () => {
      mounted = false;
    };
  }, [sectionNode]);

  const ITEM_HEIGHT = 60;
  const [scrollTop, setScrollTop] = useState(0);
  const onScroll = (e) => setScrollTop(e.currentTarget.scrollTop);
  const startIndex = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - 5);
  const endIndex = Math.min(
    questions.length,
    Math.ceil((scrollTop + 250) / ITEM_HEIGHT) + 5
  );
  const offsetY = startIndex * ITEM_HEIGHT;
  const visible = questions.slice(startIndex, endIndex);

  const nextPhase = getNextPhase(path, structure);
  const prevPhase = getPrevPhase(path, structure);
  const nextTab = getNextTab(path, structure);
  const prevTab = getPrevTab(path, structure);
  const nextSection = getNextSection(path, structure);
  const prevSection = getPrevSection(path, structure);
  const nextQuestion = getNextQuestion(path, structure);
  const prevQuestion = getPrevQuestion(path, structure);

  if (!structure.length || !path || !phaseNode || !tabNode || !sectionNode || !questionNode) {
    return null;
  }

  const sectionAnswered = sectionNode.questions.filter((q) => progress[q.id]).length;
  const sectionTotal = sectionNode.questions.length;
  const tabCounts = tabNode
    ? tabNode.sections.reduce(
        (acc, s) => {
          acc.answered += s.questions.filter((q) => progress[q.id]).length;
          acc.total += s.questions.length;
          return acc;
        },
        { answered: 0, total: 0 }
      )
    : { answered: 0, total: 0 };
  const phaseCounts = phaseNode
    ? phaseNode.tabs.reduce(
        (acc, t) => {
          t.sections.forEach((s) => {
            acc.answered += s.questions.filter((q) => progress[q.id]).length;
            acc.total += s.questions.length;
          });
          return acc;
        },
        { answered: 0, total: 0 }
      )
    : { answered: 0, total: 0 };

  return (
    <div className="space-y-4">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink onClick={() => navigateTo({ phaseId: path.phaseId })}>{phaseNode.title}</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbLink onClick={() => navigateTo({ phaseId: path.phaseId, tabId: path.tabId })}>{tabNode.title}</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbLink onClick={() => navigateTo({
              phaseId: path.phaseId,
              tabId: path.tabId,
              sectionId: path.sectionId,
            })}>{sectionNode.title}</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Question {path.question}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      <div className="text-sm space-y-1">
        <div>
          Phase Progress: {phaseCounts.total > 0
            ? Math.round((phaseCounts.answered / phaseCounts.total) * 100)
            : 0}%
        </div>
        <div>
          Tab Progress: {tabCounts.total > 0
            ? Math.round((tabCounts.answered / tabCounts.total) * 100)
            : 0}%
        </div>
        <div>
          Section Progress: {sectionAnswered}/{sectionTotal}
        </div>
      </div>

      <div className="border rounded h-64 overflow-auto" onScroll={onScroll}>
        <Suspense fallback={<div>Loading...</div>}>
          <div style={{ height: questions.length * ITEM_HEIGHT, position: 'relative' }}>
            <div style={{ transform: `translateY(${offsetY}px)` }}>
              {visible.map((q) => (
                <div key={q.id} className="p-4 border-b" style={{ height: ITEM_HEIGHT }}>
                  {q.question}
                </div>
              ))}
            </div>
          </div>
        </Suspense>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between">
          <Button variant="outline" onClick={() => navigateTo(prevPhase)}>
            Prev Phase
          </Button>
          <Button onClick={() => navigateTo(nextPhase)}>Next Phase</Button>
        </div>
        <div className="flex justify-between">
          <Button variant="outline" onClick={() => navigateTo(prevTab)}>
            Prev Tab
          </Button>
          <Button onClick={() => navigateTo(nextTab)}>Next Tab</Button>
        </div>
        <div className="flex justify-between">
          <Button variant="outline" onClick={() => navigateTo(prevSection)}>
            Prev Section
          </Button>
          <Button onClick={() => navigateTo(nextSection)}>Next Section</Button>
        </div>
        <div className="flex justify-between">
          <Button variant="outline" onClick={() => navigateTo(prevQuestion)}>
            Prev Question
          </Button>
          <span>{toCode(path)}</span>
          <Button onClick={() => navigateTo(nextQuestion)}>Next Question</Button>
        </div>
      </div>
    </div>
  );
};

export default QuestionNavigator;
