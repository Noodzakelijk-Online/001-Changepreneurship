import os
from typing import List, Dict, Any

from .llm_client import LLMClient


class LLMConsensus:
    """
    Orchestrates multi-model consensus with peer review.

    Algorithm (simplified):
    1) Run N models/providers on the same prompt -> initial findings.
    2) Identify minority findings (unique claims vs majority).
    3) Peer-review: Ask non-claiming models to re-check specifically the minority claim.
    4) If re-check confirms, mark as Niche Insight; if rejected, mark as Hallucination.
    5) Return structured result with confidence scores.
    """

    def __init__(self, configs: List[Dict[str, Any]]):
        # configs: [{provider, model, weight(optional)}]
        self.clients: List[Dict[str, Any]] = []
        for cfg in configs:
            # Temporarily override env for each client instance
            os.environ["LLM_PROVIDER"] = cfg.get("provider", os.getenv("LLM_PROVIDER", "openai"))
            os.environ["LLM_MODEL"] = cfg.get("model", os.getenv("LLM_MODEL", "gpt-4.1-mini"))
            client = LLMClient()
            self.clients.append({"client": client, "weight": float(cfg.get("weight", 1.0)), "provider": os.getenv("LLM_PROVIDER"), "model": os.getenv("LLM_MODEL")})

    def run(self, prompt: str, system: str = "") -> Dict[str, Any]:
        initial: List[Dict[str, Any]] = []
        for c in self.clients:
            text = c["client"].generate(prompt=prompt, system=system)
            initial.append({"provider": c["provider"], "model": c["model"], "text": text})

        # Simple extraction: split into bullet-like lines
        findings_by_model: List[List[str]] = []
        for r in initial:
            lines = [ln.strip("- • ").strip() for ln in r["text"].splitlines() if ln.strip()]
            findings_by_model.append(lines)

        # Tally findings frequency
        freq: Dict[str, int] = {}
        for lines in findings_by_model:
            for f in set(lines):
                freq[f] = freq.get(f, 0) + 1

        majority_threshold = max(2, len(self.clients) // 2 + 1)
        majority = {f for f, n in freq.items() if n >= majority_threshold}
        minority = {f for f, n in freq.items() if n < majority_threshold}

        peer_reviews: List[Dict[str, Any]] = []
        for claim in minority:
            # Ask all models that did not report the claim to re-check explicitly
            recheck_prompt = (
                f"Minority claim detected: '{claim}'. Re-check specifically for evidence supporting or refuting this claim.\n"
                "Return one of: CONFIRM niche insight with reasoning, or REJECT as hallucination with reasoning."
            )
            confirmations = 0
            rejections = 0
            details: List[Dict[str, Any]] = []
            for idx, c in enumerate(self.clients):
                model_findings = set(findings_by_model[idx])
                if claim in model_findings:
                    continue
                txt = c["client"].generate(prompt=recheck_prompt, system="Peer review for claim validation")
                verdict = "REJECT"
                content_low = txt.lower()
                if "confirm" in content_low and "hallucination" not in content_low:
                    verdict = "CONFIRM"
                    confirmations += 1
                elif "reject" in content_low or "hallucination" in content_low:
                    verdict = "REJECT"
                    rejections += 1
                details.append({"provider": c["provider"], "model": c["model"], "verdict": verdict, "text": txt})

            label = "niche_insight" if confirmations >= rejections else "hallucination"
            peer_reviews.append({"claim": claim, "label": label, "confirmations": confirmations, "rejections": rejections, "details": details})

        result = {
            "majority": sorted(list(majority)),
            "minority_reviews": peer_reviews,
            "raw": initial,
        }
        return result
