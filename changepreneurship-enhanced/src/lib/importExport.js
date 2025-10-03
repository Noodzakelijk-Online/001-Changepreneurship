import { validateQuestionnaire } from "./schema.js";

export async function importJson(file) {
  const text = await file.text();
  const data = JSON.parse(text);
  return validateQuestionnaire(data);
}

export function exportJson(data) {
  return new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json"
  });
}
