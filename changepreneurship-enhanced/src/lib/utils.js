import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/**
 * Returns a Tailwind CSS text-color class for a 0–100 score.
 * Used by components that render scores as styled text (e.g. PhaseCompletionPanel).
 */
export function scoreColorClass(score) {
  if (score >= 70) return 'text-emerald-400';
  if (score >= 50) return 'text-yellow-400';
  return 'text-orange-400';
}

/**
 * Returns a CSS hex color string for a 0–100 score.
 * Used by components that set inline `color` / `background` styles (e.g. AIInsightsPage).
 */
export function scoreColorHex(score) {
  if (score >= 80) return '#22c55e';
  if (score >= 65) return '#f97316';
  return '#ef4444';
}
