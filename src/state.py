from typing import TypedDict, Literal

class FlaggedClaim(TypedDict):
    claim_text: str 
    severity: Literal["unsupported", "contradicted"]
    evidence_chunk_id: str | None
    rationale: str

class State(TypedDict, total=False):
    query: str
    stats_data: dict
    news_data: list
    retieved_context: list
    draft_answer: str
    verified_answer: str
    flagged_claims: list[FlaggedClaim]