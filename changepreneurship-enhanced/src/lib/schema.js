import { z } from "zod";

const QuestionSchema = z.object({
  id: z.string(),
  prompt: z.string(),
  type: z.enum(["text", "textarea", "select"]),
  required: z.boolean().optional()
});

const SectionSchema = z.object({
  id: z.string(),
  title: z.string(),
  questions: z.array(QuestionSchema)
});

const TabSchema = z.object({
  id: z.string(),
  title: z.string(),
  sections: z.array(SectionSchema).optional()
});

const PhaseSchema = z.object({
  id: z.string(),
  title: z.string(),
  tabs: z.array(TabSchema).optional(),
  version: z.number().optional()
});

export const QuestionnaireSchema = z.object({
  version: z.number(),
  phases: z.array(PhaseSchema)
});

export function validateQuestionnaire(data) {
  return QuestionnaireSchema.parse(data);
}
