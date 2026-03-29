/**
 * AssessmentShell — shared dark-theme layout for all 7 assessment stages.
 * Wraps any assessment with:
 *  - Top horizontal stage progress bars
 *  - One-question-at-a-time navigation within each section
 *  - Bottom nav bar (autosave indicator + Next button)
 *  - Dark design matching the landing page mockup
 *
 * Props:
 *  - phaseName       string    e.g. "Self Discovery Assessment"
 *  - phaseNumber     number    1-7
 *  - sections        array     [{ id, title, icon, questions[] }]
 *  - currentSection  string    currently active section id
 *  - onSectionChange fn(id)    called when user clicks a section tab
 *  - responses       object    { [sectionId]: { [questionId]: value } }
 *  - onResponse      fn(sectionId, questionId, answer)
 *  - sectionProgress object    { [sectionId]: 0-100 }
 *  - onNext          fn()      called on last question of last section
 *  - nextLabel       string    e.g. "Next Phase"
 *  - children        ReactNode optional extra content (e.g. results panel)
 */

import React, { useState, useEffect } from 'react'
import { CheckCircle, ArrowRight, ArrowLeft, ChevronRight } from 'lucide-react'
import { Slider } from '@/components/ui/slider.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import DragDropRanking from '@/components/ui/drag-drop-ranking.jsx'

// ─── Question type renderers ───────────────────────────────────────────────────

const MultipleChoiceInput = ({ question, response, onResponse }) => (
  <div className="space-y-3">
    {question.options.map((option) => {
      const selected = response === option.value
      return (
        <button
          key={option.value}
          type="button"
          onClick={() => onResponse(option.value)}
          className={`w-full flex items-center gap-4 p-4 rounded-xl border text-left transition-all duration-150 ${
            selected
              ? 'border-cyan-500/60 bg-cyan-500/8 text-white shadow-sm shadow-cyan-500/10'
              : 'border-gray-800 bg-black/30 text-gray-400 hover:border-gray-700 hover:text-gray-300'
          }`}
        >
          <div className={`w-4 h-4 rounded-full flex-shrink-0 border-2 flex items-center justify-center transition-colors ${
            selected ? 'border-cyan-500 bg-cyan-500' : 'border-gray-600'
          }`}>
            {selected && <div className="w-1.5 h-1.5 rounded-full bg-white"></div>}
          </div>
          <div>
            <div className="text-sm font-medium leading-snug">{option.label}</div>
            {option.description && (
              <div className={`text-xs mt-0.5 ${selected ? 'text-cyan-300/70' : 'text-gray-600'}`}>
                {option.description}
              </div>
            )}
          </div>
        </button>
      )
    })}
  </div>
)

const ScaleInput = ({ question, response, onResponse }) => {
  const min = question.scaleRange?.min || 1
  const max = question.scaleRange?.max || 10
  const numValue = typeof response === 'number' ? response : parseInt(response) || min
  return (
    <div className="space-y-6">
      <div className="flex justify-between text-xs text-gray-500 uppercase tracking-wider">
        <span>{question.scaleLabels?.min || 'Low'}</span>
        <span>{question.scaleLabels?.max || 'High'}</span>
      </div>
      <Slider
        key={`${question.id}-${numValue}`}
        value={[numValue]}
        onValueChange={(value) => onResponse(value[0])}
        min={min} max={max} step={1}
        className="w-full [&_.slider-track]:bg-gray-800 [&_.slider-range]:bg-gradient-to-r [&_.slider-range]:from-cyan-500 [&_.slider-range]:to-purple-500"
      />
      <div className="flex items-center justify-center">
        <div className="px-4 py-1.5 rounded-full bg-gray-900 border border-gray-800 text-sm font-semibold text-white">
          {numValue} / {max}
        </div>
      </div>
    </div>
  )
}

const TextareaInput = ({ question, response, onResponse }) => (
  <Textarea
    key={`${question.id}-textarea`}
    value={response || ''}
    onChange={(e) => onResponse(e.target.value)}
    placeholder={question.placeholder || 'Enter your response...'}
    rows={5}
    className="w-full bg-black/50 border-gray-800 rounded-xl text-white placeholder-gray-600 focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 resize-none"
  />
)

const MultipleScaleInput = ({ question, response, onResponse }) => {
  const min = question.scaleRange?.min || 1
  const max = question.scaleRange?.max || 10
  const value = response || {}
  return (
    <div className="space-y-6">
      {question.areas.map((area) => (
        <div key={area}>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-300">{area}</span>
            <span className="text-xs text-gray-500">{value[area] ?? min}/{max}</span>
          </div>
          <Slider
            value={[value[area] ?? min]}
            onValueChange={(v) => onResponse({ ...value, [area]: v[0] })}
            min={min} max={max} step={1}
            className="w-full"
          />
        </div>
      ))}
    </div>
  )
}

const SelectInput = ({ question, response, onResponse }) => (
  <div className="space-y-3">
    {question.options.map((option) => {
      const val = typeof option === 'string' ? option : option.value
      const label = typeof option === 'string' ? option : option.label
      const selected = response === val
      return (
        <button
          key={val}
          type="button"
          onClick={() => onResponse(val)}
          className={`w-full flex items-center gap-4 p-4 rounded-xl border text-left transition-all duration-150 ${
            selected
              ? 'border-cyan-500/60 bg-cyan-500/8 text-white'
              : 'border-gray-800 bg-black/30 text-gray-400 hover:border-gray-700 hover:text-gray-300'
          }`}
        >
          <div className={`w-4 h-4 rounded-full flex-shrink-0 border-2 flex items-center justify-center ${
            selected ? 'border-cyan-500 bg-cyan-500' : 'border-gray-600'
          }`}>
            {selected && <div className="w-1.5 h-1.5 rounded-full bg-white"></div>}
          </div>
          <span className="text-sm font-medium">{label}</span>
        </button>
      )
    })}
  </div>
)

const RankingInput = ({ question, response, onResponse }) => (
  <DragDropRanking
    options={question.options}
    value={response || []}
    onChange={onResponse}
    maxRankings={question.maxRankings}
  />
)

// Single-line text input — for type: 'text'
const TextInput = ({ question, response, onResponse }) => (
  <input
    type="text"
    value={response || ''}
    onChange={(e) => onResponse(e.target.value)}
    placeholder={question.placeholder || 'Type your answer...'}
    className="w-full bg-black/50 border border-gray-800 rounded-xl px-4 py-3 text-white placeholder-gray-600 focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 outline-none text-sm"
  />
)

// Matrix input — rows × columns, each cell rated 1–5
// question.rows = [{id, label}], question.columns = [{id, label}]
// response = { [rowId]: { [colId]: number } }
const MatrixInput = ({ question, response, onResponse }) => {
  const value = response || {}
  const setValue = (rowId, colId, num) => {
    onResponse({ ...value, [rowId]: { ...(value[rowId] || {}), [colId]: num } })
  }
  const colCount = question.columns?.length || 0
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th className="text-left py-2 pr-4 text-xs text-gray-500 font-medium min-w-[160px]"></th>
            {question.columns.map((col) => (
              <th key={col.id} className="text-center py-2 px-2 text-xs text-gray-400 font-medium whitespace-nowrap">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {question.rows.map((row, ri) => (
            <tr key={row.id} className={ri % 2 === 0 ? 'bg-white/[0.02]' : ''}>
              <td className="py-3 pr-4 text-xs text-gray-300 font-medium">{row.label}</td>
              {question.columns.map((col) => {
                const current = value[row.id]?.[col.id]
                return (
                  <td key={col.id} className="py-3 px-2 text-center">
                    <div className="flex items-center justify-center gap-1">
                      {[1, 2, 3, 4, 5].map((n) => (
                        <button
                          key={n}
                          type="button"
                          onClick={() => setValue(row.id, col.id, n)}
                          className={`w-7 h-7 rounded-lg text-xs font-semibold transition-all ${
                            current === n
                              ? 'bg-cyan-500 text-white shadow-sm shadow-cyan-500/40'
                              : 'bg-gray-800 text-gray-500 hover:bg-gray-700 hover:text-gray-300'
                          }`}
                        >
                          {n}
                        </button>
                      ))}
                    </div>
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-xs text-gray-600 mt-3">1 = Low / 5 = High</p>
    </div>
  )
}

// Categorised textareas — for resource-planning, stakeholder-map etc.
// question.categories = [{ id, label, description?, placeholder? }]
const CategorizedTextsInput = ({ question, response, onResponse }) => {
  const value = response || {}
  return (
    <div className="space-y-5">
      {question.categories.map((cat) => (
        <div key={cat.id}>
          <div className="mb-1.5">
            <span className="text-sm font-semibold text-gray-200">{cat.label}</span>
            {cat.description && (
              <span className="block text-xs text-gray-500 mt-0.5">{cat.description}</span>
            )}
          </div>
          <Textarea
            value={value[cat.id] || ''}
            onChange={(e) => onResponse({ ...value, [cat.id]: e.target.value })}
            placeholder={cat.placeholder || 'Enter details...'}
            rows={2}
            className="w-full bg-black/50 border-gray-800 rounded-xl text-white placeholder-gray-600 focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 resize-none text-sm"
          />
        </div>
      ))}
    </div>
  )
}

// Multi-entry cards — for customer-segments, competitor-analysis etc.
// question.maxSegments | question.maxCompetitors = N
const MultiEntryInput = ({ question, response, onResponse }) => {
  const max = question.maxSegments || question.maxCompetitors || 3
  const isSegments = !!question.maxSegments
  const label = isSegments ? 'Segment' : 'Competitor'
  const entries = Array.isArray(response) && response.length === max
    ? response
    : Array.from({ length: max }, (_, i) => (response?.[i] || { title: '', description: '' }))

  const updateEntry = (index, field, val) => {
    const next = entries.map((e, i) => i === index ? { ...e, [field]: val } : e)
    onResponse(next)
  }

  return (
    <div className="space-y-4">
      {entries.map((entry, i) => (
        <div key={i} className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 space-y-2.5">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-6 h-6 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-xs font-bold text-cyan-400">
              {i + 1}
            </div>
            <span className="text-xs uppercase tracking-wide text-gray-500 font-medium">{label} {i + 1}</span>
          </div>
          <input
            type="text"
            value={entry.title || ''}
            onChange={(e) => updateEntry(i, 'title', e.target.value)}
            placeholder={isSegments ? 'Segment name (e.g. "Freelance designers")...' : 'Competitor name...'}
            className="w-full bg-black/50 border border-gray-800 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:border-cyan-500/60 outline-none"
          />
          <Textarea
            value={entry.description || ''}
            onChange={(e) => updateEntry(i, 'description', e.target.value)}
            placeholder={isSegments
              ? 'Who are they, what do they need, how will you reach them...'
              : 'What they offer, their strengths and weaknesses...'}
            rows={2}
            className="w-full bg-black/50 border-gray-800 rounded-xl text-white placeholder-gray-600 focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 resize-none text-sm"
          />
        </div>
      ))}
    </div>
  )
}

// Render any question type
const QuestionInput = ({ question, response, onResponse }) => {
  switch (question.type) {
    case 'multiple-choice':    return <MultipleChoiceInput question={question} response={response} onResponse={onResponse} />
    case 'scale':              return <ScaleInput question={question} response={response} onResponse={onResponse} />
    case 'text':               return <TextInput question={question} response={response} onResponse={onResponse} />
    case 'textarea':           return <TextareaInput question={question} response={response} onResponse={onResponse} />
    case 'multiple-scale':     return <MultipleScaleInput question={question} response={response} onResponse={onResponse} />
    case 'select':             return <SelectInput question={question} response={response} onResponse={onResponse} />
    case 'ranking':            return <RankingInput question={question} response={response} onResponse={onResponse} />
    case 'matrix':             return <MatrixInput question={question} response={response} onResponse={onResponse} />
    case 'resource-planning':
    case 'stakeholder-map':    return <CategorizedTextsInput question={question} response={response} onResponse={onResponse} />
    case 'customer-segments':
    case 'competitor-analysis':return <MultiEntryInput question={question} response={response} onResponse={onResponse} />
    default:
      return <p className="text-gray-500 text-sm">Question type "{question.type}" not supported.</p>
  }
}

// ─── Main Shell ───────────────────────────────────────────────────────────────

const AssessmentShell = ({
  phaseName,
  phaseNumber,
  sections,
  currentSection,
  onSectionChange,
  responses,
  onResponse,
  sectionProgress,
  onNext,
  nextLabel = 'Next Phase',
  children,
}) => {
  const [questionIndex, setQuestionIndex] = useState(0)

  // Reset question index when section changes
  useEffect(() => {
    setQuestionIndex(0)
  }, [currentSection])

  const section = sections.find(s => s.id === currentSection)
  const questions = section?.questions || []
  const isResultsSection = !questions.length
  const currentQ = questions[questionIndex]
  const sectionResponse = responses[currentSection] || {}
  const totalSections = sections.filter(s => s.questions?.length > 0).length
  const sectionIdx = sections.findIndex(s => s.id === currentSection)

  const isLastQuestion = questionIndex === questions.length - 1
  const isLastSection = sectionIdx === sections.length - 1 || (sectionIdx === sections.length - 2 && isResultsSection)

  const handleNext = () => {
    if (!isResultsSection && !isLastQuestion) {
      setQuestionIndex(i => i + 1)
    } else {
      // Move to next section or fire onNext
      const nextSectionIdx = sectionIdx + 1
      if (nextSectionIdx < sections.length) {
        onSectionChange(sections[nextSectionIdx].id)
      } else {
        onNext?.()
      }
    }
  }

  const handlePrev = () => {
    if (questionIndex > 0) {
      setQuestionIndex(i => i - 1)
    } else {
      const prevSectionIdx = sectionIdx - 1
      if (prevSectionIdx >= 0) {
        const prevSection = sections[prevSectionIdx]
        onSectionChange(prevSection.id)
        const prevQCount = prevSection.questions?.length || 0
        setQuestionIndex(Math.max(0, prevQCount - 1))
      }
    }
  }

  const isFirstQ = questionIndex === 0 && sectionIdx === 0
  const currentResponse = currentQ ? sectionResponse[currentQ.id] : undefined
  const hasResponse = currentResponse !== undefined && currentResponse !== '' &&
    !(Array.isArray(currentResponse) && currentResponse.length === 0)

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">

      {/* ── Section tabs + fill bars ── */}
      <div className="bg-black/60 border-b border-gray-800/60 px-4 pt-5 pb-0">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-end gap-0 overflow-x-auto">
            {sections.filter(s => s.questions?.length > 0).map((s, i) => {
              const isActive = s.id === currentSection
              const progress = sectionProgress[s.id] || 0
              const isComplete = progress >= 100
              const sQCount = s.questions?.length || 0
              const answered = Object.keys(responses[s.id] || {}).length

              return (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => onSectionChange(s.id)}
                  className={`group relative flex flex-col items-start flex-shrink-0 px-3 pb-0 pt-0 transition-colors ${
                    isActive ? '' : 'hover:opacity-80'
                  }`}
                  style={{ minWidth: 80 }}
                >
                  {/* Section name */}
                  <span className={`text-[11px] font-medium whitespace-nowrap mb-2 transition-colors ${
                    isActive ? 'text-cyan-400' :
                    isComplete ? 'text-emerald-400/70' :
                    'text-gray-600 group-hover:text-gray-400'
                  }`}>
                    {s.title}
                  </span>

                  {/* Question dot row inside tab */}
                  <div className="flex items-center gap-0.5 mb-2">
                    {Array.from({ length: sQCount }).map((_, qi) => {
                      const qId = s.questions[qi]?.id
                      const answered = qId && (responses[s.id] || {})[qId] !== undefined &&
                        (responses[s.id] || {})[qId] !== '' &&
                        !( Array.isArray((responses[s.id] || {})[qId]) && (responses[s.id] || {})[qId].length === 0 )
                      const isCurrent = isActive && qi === questionIndex
                      return (
                        <div
                          key={qi}
                          className={`rounded-full transition-all duration-200 ${
                            isCurrent
                              ? 'w-3.5 h-3.5 bg-cyan-500 shadow-sm shadow-cyan-500/60 ring-2 ring-cyan-500/30'
                              : answered
                              ? 'w-2 h-2 bg-emerald-500/80'
                              : isActive
                              ? 'w-2 h-2 bg-gray-700'
                              : 'w-1.5 h-1.5 bg-gray-800'
                          }`}
                        />
                      )
                    })}
                  </div>

                  {/* Fill bar at bottom */}
                  <div className="w-full h-0.5 rounded-t-full overflow-hidden bg-gray-800/60">
                    <div
                      className={`h-full rounded-t-full transition-all duration-500 ${
                        isActive
                          ? 'bg-gradient-to-r from-cyan-500 to-cyan-400'
                          : isComplete
                          ? 'bg-emerald-500/60'
                          : 'bg-transparent'
                      }`}
                      style={{ width: isActive ? `${((questionIndex + 1) / Math.max(sQCount, 1)) * 100}%` : `${progress}%` }}
                    />
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* ── Content ── */}
      <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full px-6 py-10">
        {children && isResultsSection ? (
          // Results panel
          <div className="flex-1">
            {children}
            <div className="mt-8 flex justify-end">
              <button
                type="button"
                onClick={onNext}
                className="flex items-center gap-2 px-8 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-white font-semibold shadow-lg shadow-cyan-500/20 transition-all"
              >
                {nextLabel}
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        ) : isResultsSection ? (
          <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
            Complete all sections to see results.
          </div>
        ) : currentQ ? (
          <>
            {/* Stage + question counter */}
            <div className="flex items-center gap-3 mb-8">
              <div className="px-3 py-1 rounded-lg bg-cyan-500/10 border border-cyan-500/25 text-cyan-400 text-xs uppercase tracking-wide font-semibold">
                Stage {phaseNumber} — {phaseName}
              </div>
              <span className="text-gray-600 text-xs">
                Question {questionIndex + 1} of {questions.length}
              </span>
            </div>

            {/* Question */}
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white mb-2 leading-snug">
                {currentQ.question}
              </h2>
              {(currentQ.description || currentQ.helpText) && (
                <p className="text-gray-500 text-sm mb-8">
                  {currentQ.description || currentQ.helpText}
                </p>
              )}
              {!currentQ.description && !currentQ.helpText && (
                <div className="mb-8" />
              )}

              <QuestionInput
                question={currentQ}
                response={currentResponse}
                onResponse={(answer) => onResponse(currentSection, currentQ.id, answer)}
              />
            </div>

            {/* Bottom nav */}
            <div className="mt-10 pt-6 border-t border-gray-800/50 flex items-center justify-between">
              <button
                type="button"
                onClick={handlePrev}
                disabled={isFirstQ}
                className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-300 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ArrowLeft className="h-4 w-4" />
                Previous
              </button>

              <div className="flex items-center gap-2 text-xs text-gray-600">
                <CheckCircle className="h-3.5 w-3.5 text-emerald-500/60" />
                Progress saved automatically
              </div>

              <button
                type="button"
                onClick={handleNext}
                className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-lg ${
                  hasResponse
                    ? 'bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-white shadow-cyan-500/20'
                    : 'bg-gray-800 text-gray-500 cursor-pointer hover:bg-gray-700'
                }`}
              >
                {isLastQuestion && isLastSection ? nextLabel : isLastQuestion ? 'Next Section' : 'Next Question'}
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </>
        ) : null}
      </div>
    </div>
  )
}

export default AssessmentShell
