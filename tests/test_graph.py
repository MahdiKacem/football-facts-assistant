from src.graph import build_graph

def run_query(query: str):
    graph = build_graph()
    result = graph.invoke({
        "query": query,
        "stats_data": {},
        "news_data": [],
        "retrieved_context": [],
        "draft_answer": "",
        "verified_answer": "",
        "flagged_claims": [],
    })
    print("\nSTATS:", result.get("stats_data"))
    print("NEWS COUNT:", len(result.get("news_data", [])))
    print("DRAFT:\n", result["draft_answer"])
    print("\nVERIFIED:\n", result["verified_answer"])
    print("\nFLAGGED:\n", result["flagged_claims"])

if __name__ == "__main__":
    run_query("Compare Yamal and Mbappé's goals in La Liga this season")