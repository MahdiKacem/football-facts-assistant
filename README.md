# PitchIQ — Football Match Intelligence & Fact-Checked Scouting Assistant

## 1. Overview

**What it does:** PitchIQ answers football questions: player comparisons, match breakdowns, tactical summaries, rules clarifications and that's by combining live stats data, football news, and the official Laws of the Game, then actively fact-checks its own output against the retrieved data before showing an answer.

**The real-world problem it solves:** LLMs asked sports-stat questions directly confidently hallucinate numbers because they don't have live data and won't tell you that. PitchIQ solves this by grounding every stat claim in retrieved, verifiable data, and adding a dedicated agent whose only job is catching claims that aren't actually supported by what was retrieved.

## 2. Run with Docker

Create `.env` from `.env.example` and fill in the API keys, then build and start the application:

```bash
docker compose up --build
```

The API is available at `http://localhost:8000`. Check it with:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/query \
	-H "Content-Type: application/json" \
	-d '{"query":"Compare Yamal and Mbappe goals in La Liga this season"}'
```

Qdrant is exposed at `http://localhost:6333` and its data is persisted in `qdrant_storage/`. The `/query` endpoint also requires the configured Ollama model to be available to the application.

