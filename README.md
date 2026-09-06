# PitchIQ — Football Match Intelligence & Fact-Checked Scouting Assistant

## 1. Overview

**What it does:** PitchIQ answers football questions: player comparisons, match breakdowns, tactical summaries, rules clarifications and that's by combining live stats data, football news, and the official Laws of the Game, then actively fact-checks its own output against the retrieved data before showing an answer.

**The real-world problem it solves:** LLMs asked sports-stat questions directly confidently hallucinate numbers because they don't have live data and won't tell you that. PitchIQ solves this by grounding every stat claim in retrieved, verifiable data, and adding a dedicated agent whose only job is catching claims that aren't actually supported by what was retrieved.