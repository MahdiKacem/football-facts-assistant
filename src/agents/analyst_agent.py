from langchain_ollama import ChatOllama
import json

ANALYST_SYSTEM_PROMPT = """
    You are a football analyst. You are given structured stats data, \
    recent news items, and retrieved rules/stats context. Write a concise answer to the user's query.

    STRICT RULE: every numeric or factual claim must end with an inline citation tag indicating its \
    source, in the form [SOURCE:<id>], where <id> is either a stats_data key, a news_data index, or a \
    retrieved_context chunk_id. If you cannot support a claim with the given data, do not state it as fact.
"""


class AnalystAgent:

    def __init__(self, model_name: str = "llama3", temperature: float = 0):
         self.llm = ChatOllama(model=model_name, temperature=temperature)

    def analyst_node(self, state: dict) -> dict:
        context_blob = json.dumps({
            "stats_data": state.get("stats_data", {}),
            "news_data": state.get("news_data", {}),
            "retrieved_context": state.get("retrieved_context", [])
        }, default = str)

        messages = [
            ("system", ANALYST_SYSTEM_PROMPT),
            ("user", f"Query: {state['query']} \n Available data: {context_blob}")
        ]

        response = self.llm.invoke(messages)
        return {"draft_answer": response.content}
