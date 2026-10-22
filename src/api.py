import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.graph import build_graph


app = FastAPI(
    title="PitchIQ API",
    description="Fact-checked football match intelligence assistant",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    news_query: str | None = None
    news_limit: int = Field(default=50, ge=1, le=100)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/dast-demo", response_class=HTMLResponse)
def dast_demo(value: str = "") -> str:
    if os.getenv("DAST_DEMO_VULNERABILITY") != "1":
        raise HTTPException(status_code=404, detail="Not found")
    return f"<html><body>Value: {value}</body></html>"


@app.post("/query")
def query(request: QueryRequest) -> dict:
    state = {
        "query": request.query,
        "news_limit": request.news_limit,
        "stats_data": {},
        "news_data": [],
        "retrieved_context": [],
        "draft_answer": "",
        "verified_answer": "",
        "flagged_claims": [],
    }
    if request.news_query:
        state["news_query"] = request.news_query

    try:
        result = build_graph().invoke(state)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "answer": result.get("verified_answer", ""),
        "draft_answer": result.get("draft_answer", ""),
        "flagged_claims": result.get("flagged_claims", []),
        "stats_data": result.get("stats_data", {}),
        "news_data": result.get("news_data", []),
    }