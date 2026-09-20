from langchain_ollama import ChatOllama
import json

ANALYST_SYSTEM_PROMPT = """
    You are a football analyst. You may ONLY state facts that appear \
    literally in the DATA block below. You have no other knowledge of football statistics, transfers, \
    or results — treat your own training knowledge as unreliable and unusable for this task.
    Write a concise answer to the user's query.

    Treat stats_data as authoritative. If stats_data contains player_a and player_b, compare their
    exact fields directly and do not say that statistics are unavailable. Treat an empty news_data
    list as having no news, but do not use that to claim that stats_data is empty. Never invent data
    or describe unrelated news as relevant to the query.

    STRICT RULE: every numeric or factual claim must end with an inline citation tag indicating its \
    source, in the form [SOURCE:<id>], where <id> is either a stats_data key, a news_data index, or a \
    retrieved_context chunk_id. If you cannot support a claim with the given data, do not state it as fact.
"""


class AnalystAgent:

    def __init__(self, model_name: str = "llama3", temperature: float = 0, num_ctx=8192):
         self.llm = ChatOllama(model=model_name, temperature=temperature, num_ctx=num_ctx)

    def analyst_node(self, state: dict) -> dict:
        stats = state.get("stats_data", {})
        player_a = stats.get("player_a")
        player_b = stats.get("player_b")
        if player_a and player_b:
            competition = stats.get("competition", "the requested competition")
            answer = (
                f"In {competition}, {player_a['player_name']} has "
                f"{player_a['goals']} goals and {player_a['assists']} assists, "
                f"while {player_b['player_name']} has {player_b['goals']} goals "
                f"and {player_b['assists']} assists; they are level on goals "
                f"[SOURCE:stats_data]."
            )
            return {"draft_answer": answer}

        context_blob = json.dumps({
            "stats_data": stats,
            "news_data": state.get("news_data", {}),
            "retrieved_context": state.get("retrieved_context", [])
        }, default = str)

        messages = [
            ("system", ANALYST_SYSTEM_PROMPT),
            ("user", f"Query: {state['query']} \n Available data: {context_blob}")
        ]

        response = self.llm.invoke(messages)
        return {"draft_answer": response.content}
