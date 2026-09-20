from langgraph.graph import StateGraph, START, END
from src.state import State
from src.agents.analyst_agent import AnalystAgent
from src.agents.fact_checker_agent import FactCheckerAgent
from src.agents.news_agent import NewsAgent
from src.agents.data_agent import DataAgent
from src.agents.rag_agent import rag_node

data_node = DataAgent().data_node
analyst_node = AnalystAgent().analyst_node
fact_checker_node = FactCheckerAgent().fact_checker_node
news_node = NewsAgent().news_node

def build_graph() -> StateGraph:
    graph = StateGraph(State)

    graph.add_node("data", data_node)
    graph.add_node("news", news_node)
    graph.add_node("rag", rag_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("fact_checker", fact_checker_node)

    # true parallel fan-out: START -> {data, news, rag} run concurrently
    graph.add_edge(START, "data")
    graph.add_edge(START, "news")
    graph.add_edge(START, "rag")

    # fan in: analyst waits for all 3
    graph.add_edge("data", "analyst")
    graph.add_edge("news", "analyst")
    graph.add_edge("rag", "analyst")

    graph.add_edge("analyst", "fact_checker")
    graph.add_edge("fact_checker", END)

    return graph.compile() 