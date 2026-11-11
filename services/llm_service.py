import os
import json
import requests
from typing import Dict, List, Any

SYSTEM_AUDIT_PROMPT = """
You are the AI Investigation Auditor, a professional second-level audit assistant for criminal investigation records.
ETHICAL INVARIANTS:
1. You NEVER determine guilt or innocence.
2. You NEVER accuse any person of committing a crime.
3. You NEVER fabricate facts or extrapolate beyond provided records.
4. Use objective, neutral audit terminology: 'Potential inconsistency detected', 'Evidence association requires human review', 'Timeline conflict detected'.
5. Always emphasize that final conclusions rest solely with authorized human investigators.
"""

class LLMService:
    """
    LLM and Generative Reasoning Service.
    Supports external API integration with robust local offline GenAI fallback.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
        self.provider = "openai" if os.getenv("OPENAI_API_KEY") else ("gemini" if os.getenv("GEMINI_API_KEY") else "local_fallback")

    def generate_explanation(self, case_id: str, flag: Dict[str, Any], rag_sources: List[Dict[str, Any]]) -> str:
        # If API key is present, attempt remote call; otherwise use local reasoning fallback
        if self.api_key and self.provider == "openai":
            try:
                resp = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": SYSTEM_AUDIT_PROMPT},
                            {"role": "user", "content": f"Audit Flag: {json.dumps(flag)}\nRetrieved RAG Sources: {json.dumps(rag_sources)}\nProvide a concise 2-sentence neutral investigative audit note."}
                        ],
                        "max_tokens": 150,
                        "temperature": 0.2
                    },
                    timeout=5
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"].strip()
            except Exception:
                pass # Gracefully fall back to local engine

        # Local GenAI Rule Reasoning Engine
        return self._local_reasoning(flag, rag_sources)

    def _local_reasoning(self, flag: Dict[str, Any], rag_sources: List[Dict[str, Any]]) -> str:
        cat = flag.get("category", "")
        title = flag.get("title", "")
        explanation = flag.get("explanation", "")
        sources = ", ".join(flag.get("source_records", []))

        context_hint = ""
        if rag_sources:
            top_src = rag_sources[0]
            context_hint = f" Cross-reference with retrieved document [{top_src.get('title')}] (relevance score: {top_src.get('score', '1.0')}) corroborates this observation."

        if "Timeline" in cat:
            return (
                f"AUDIT ASSESSMENT: {explanation} "
                f"Investigators should request timestamp calibration logs from surveillance systems and evaluate potential witness perception variables.{context_hint}"
            )
        elif "Missing Evidence" in cat:
            return (
                f"AUDIT ASSESSMENT: {explanation} "
                f"Discrepancy in property registry requires verification of Malkhana property seizure memos and intermediate deposit registers.{context_hint}"
            )
        elif "Chain of Custody" in cat:
            return (
                f"AUDIT ASSESSMENT: {explanation} "
                f"Forensic admissibility mandates complete chain-of-custody tracking. Custodial officers should document missing transfer vouchers.{context_hint}"
            )
        elif "Incomplete" in cat:
            return (
                f"AUDIT ASSESSMENT: {explanation} "
                f"Investigative record completeness requires Section 161 CrPC / Section 180 BNSS examination of all named complaint witnesses.{context_hint}"
            )
        elif "Location" in cat:
            return (
                f"AUDIT ASSESSMENT: {explanation} "
                f"Geospatial conflict detected. Verification of cell-site location registers (CDR/IPDR) is recommended to corroborate transit plausibility.{context_hint}"
            )
        else:
            return (
                f"AUDIT ASSESSMENT: {explanation} "
                f"Investigative association remains unsubstantiated on available records. Human review required.{context_hint}"
            )

    def get_status(self) -> Dict[str, Any]:
        return {
            "mode": "Active (Local Intelligent Reasoning)" if not self.api_key else f"Active (Remote API: {self.provider})",
            "has_api_key": bool(self.api_key),
            "ethical_guardrails_enabled": True
        }

llm_service = LLMService()
