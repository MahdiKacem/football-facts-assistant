import json
import re
from langchain_ollama import ChatOllama

CLAIM_PATTERN = re.compile(r"([^\n.]*[^\s.])\s*\[SOURCE:([^\]]+)\]")
SOURCE_TAG_PATTERN = re.compile(r"\[SOURCE:[^\]]+\]")
VERIFY_PROMPT = """
    You are a fact-checking agent. You will be given one claim and the evidence chunk it cited. Decide:
    - "supported": evidence clearly backs the claim
    - "unsupported": evidence doesn't address the claim at all
    - "contradicted": evidence explicitly disagrees with the claim

    Respond ONLY with JSON: {{"verdict": "...", "rationale": "one sentence"}}

    Claim: {claim}
    Evidence: {evidence}
"""

class FactCheckerAgent:
    def __init__(self, model_name: str = "llama3", temperature: float = 0.0):
        self.llm = ChatOllama(model=model_name, temperature=temperature)

    def _find_evidence(self, source_id: str, state: dict):
        # source_id could reference stats, news or retieved chunk
        if source_id == "stats_data":
            return state.get("stats_data") or None
        if source_id in state.get("stats_data", {}):  #stats
            return state["stats_data"][source_id]
        for chunk in state.get("retrieved_context", []):  # retreived chunk
            if chunk.get("chunk_id") == source_id:
                return chunk
        for item in state.get("news_data", []):  # news
            if item.get("id") == source_id:
                return item
        return None

    def fact_checker_node(self, state: dict) -> dict:
        draft_answer = state["draft_answer"]
        flagged = []
        verified_answer = draft_answer

        # Every factual sentence must identify evidence. Uncited text cannot be
        # checked by the evidence loop below, so fail it closed as unsupported.
        sentences = re.split(r"(?<=[.!?])\s+", draft_answer.strip())
        for sentence in sentences:
            sentence = sentence.strip()
            source_tags = list(SOURCE_TAG_PATTERN.finditer(sentence))
            if sentence and not source_tags:
                flagged.append({
                    "claim_text": sentence,
                    "evidence_chunk_id": None,
                    "severity": "unsupported",
                    "rationale": "Claim has no inline source citation",
                })
                verified_answer = verified_answer.replace(
                    sentence, f"{sentence} [UNVERIFIED]", 1
                )
            elif source_tags:
                trailing_claim = sentence[source_tags[-1].end():].strip()
                if trailing_claim.strip(" \t,;:.!?"):
                    flagged.append({
                        "claim_text": trailing_claim,
                        "evidence_chunk_id": None,
                        "severity": "unsupported",
                        "rationale": "Claim has no inline source citation",
                    })
                    verified_answer = verified_answer.replace(
                        trailing_claim,
                        f"{trailing_claim} [UNVERIFIED]",
                        1,
                    )

        for match in CLAIM_PATTERN.finditer(draft_answer):
            claim_text = match.group(1).strip()
            source_id = match.group(2).strip()
            evidence = self._find_evidence(source_id, state)

            if evidence is None:
                flagged.append({
                    "claim_text": claim_text,
                    "evidence_chunk_id": None,
                    "severity": "unsupported",
                    "rationale": f"No evidence found for source ID: {source_id}"
                })
                verified_answer = verified_answer.replace(match.group(0), f"{claim_text} [UNVERIFIED]", 1)
                continue

            response = self.llm.invoke([
                ("system", VERIFY_PROMPT.format(claim=claim_text, evidence=json.dumps(evidence, default=str))),
            ])
            try:
                result = json.loads(response.content)
            except json.JSONDecodeError:
                result = {"verdict": "unsupported", "rationale": "Failed to parse LLM response"}

            if result["verdict"] in ("unsupported", "contradicted"):
                flagged.append({
                    "claim_text": claim_text,
                    "evidence_chunk_id": evidence.get("chunk_id") if evidence else None,
                    "severity": result["verdict"],
                    "rationale": result["rationale"]
                })
                marker = "[UNVERIFIED]" if result["verdict"] == "unsupported" else "[CONTRADICTED]"
                verified_answer = verified_answer.replace(match.group(0), f"{claim_text} {marker}", 1)
            else:
                verified_answer = verified_answer.replace(match.group(0), claim_text, 1)
        return {"verified_answer": verified_answer, "flagged_claims": flagged}    