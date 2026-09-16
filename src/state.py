from typing import TypedDict, Literal

class FlaggedClaim(TypedDict):
    claim_text: str 
    severity: Literal["unsupported", "contradicted"]
    evidence_chunk_id: str | None
    rationale: str

class State(TypedDict, total=False):
    query: str
    news_query: str
    news_limit: int
    team_id: int
    competition_code: str
    player_a_name: str
    player_b_name: str
    stats_data: dict
    news_data: list
    retrieved_context: list
    draft_answer: str
    verified_answer: str
    flagged_claims: list[FlaggedClaim]