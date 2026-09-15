from langchain_qdrant import QdrantVectorStore
from typing import Optional
from src.ingestion.embed_and_upsert import get_rules_store, get_stats_store
from src.state import State

def _search_store(vector_store: QdrantVectorStore, query: str, k: int) -> list[dict]:
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    results = retriever.invoke(query)
    return [
        {
            "text": result.page_content,
            "metadata": result.metadata
        }
        for result in results
    ]

def retrieve_rules(query: str, k: int = 2, vector_store: Optional[QdrantVectorStore] = None) -> list[dict]:
    vector_store = vector_store or get_rules_store()
    return _search_store(vector_store, query, k)

def retrieve_stats(query: str, k: int = 6, vector_store: Optional[QdrantVectorStore] = None) -> list[dict]:
    vector_store = vector_store or get_stats_store()
    return _search_store(vector_store, query, k)

def retrieve_context(
        query: str,
        k_rules: int = 2, # usually have one right answer, so fewer chunks needed
        k_stats: int = 6, # stats questions benefit from more matches
        only: Optional[str] = None # "rules" | "stats" | None (both)
) -> list[dict]:
    if only == "rules":
        return retrieve_rules(query, k=k_rules)
    if only == "stats":
        return retrieve_stats(query, k=k_stats)
    return retrieve_rules(query, k=k_rules) + retrieve_stats(query, k=k_stats)

def rag_node(state: State) -> dict:
    query = state.get("query")
    context = retrieve_context(query)
    return {"retrieved_context": context}