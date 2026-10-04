import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.analyst_agent import AnalystAgent
from src.agents.fact_checker_agent import FactCheckerAgent


class ContradictionResponse:
    content = json.dumps({
        "verdict": "contradicted",
        "rationale": "The evidence says Mbappe has 15 goals and Yamal has 7, so they are not level.",
    })


class DeterministicFactChecker:
    def invoke(self, messages):
        return ContradictionResponse()


class SupportedResponse:
    content = json.dumps({
        "verdict": "supported",
        "rationale": "The evidence supports the cited goal total.",
    })


class DeterministicSupportedFactChecker:
    def invoke(self, messages):
        return SupportedResponse()


def test_injected_wrong_stat_is_flagged_as_contradicted():
    stats_data = {
        "competition": "La Liga",
        "player_a": {"player_name": "Yamal", "goals": 7, "assists": 9},
        "player_b": {"player_name": "Mbappe", "goals": 15, "assists": 4},
    }
    state = {"stats_data": stats_data}

    draft_answer = AnalystAgent.__new__(AnalystAgent).analyst_node(state)["draft_answer"]
    fact_checker = FactCheckerAgent.__new__(FactCheckerAgent)
    fact_checker.llm = DeterministicFactChecker()
    result = fact_checker.fact_checker_node({
        "draft_answer": draft_answer,
        "stats_data": stats_data,
    })

    assert "they are level on goals" in draft_answer
    assert len(result["flagged_claims"]) == 1
    assert result["flagged_claims"][0]["severity"] == "contradicted"
    assert "[CONTRADICTED]" in result["verified_answer"]
    assert "[UNVERIFIED]" not in result["verified_answer"]


def test_partial_comparison_cites_available_and_missing_records():
    state = {
        "player_a_name": "Erling Haaland",
        "player_b_name": "Mohamed Salah",
        "stats_data": {
            "player_a": {"player_name": "Erling Haaland", "goals": 5, "assists": 0},
            "player_b": None,
            "competition": "PL",
        },
    }

    answer = AnalystAgent.__new__(AnalystAgent).analyst_node(state)["draft_answer"]

    assert "Erling Haaland has 5 goals and 0 assists [SOURCE:stats_data]." in answer
    assert "No stats_data record was returned for Mohamed Salah [SOURCE:stats_data]." in answer


def test_uncited_claim_is_flagged_as_unsupported():
    fact_checker = FactCheckerAgent.__new__(FactCheckerAgent)

    result = fact_checker.fact_checker_node({
        "draft_answer": "Haaland has 5 goals.",
        "stats_data": {"player_a": {"player_name": "Haaland", "goals": 5}},
    })

    assert result["flagged_claims"][0]["severity"] == "unsupported"
    assert result["flagged_claims"][0]["rationale"] == "Claim has no inline source citation"
    assert result["verified_answer"] == "Haaland has 5 goals. [UNVERIFIED]"


def test_uncited_clause_after_citation_is_flagged_as_unsupported():
    fact_checker = FactCheckerAgent.__new__(FactCheckerAgent)
    fact_checker.llm = DeterministicSupportedFactChecker()

    result = fact_checker.fact_checker_node({
        "draft_answer": (
            "Haaland has 5 goals [SOURCE:stats_data] and is the best striker in Europe."
        ),
        "stats_data": {"player_a": {"player_name": "Haaland", "goals": 5}},
    })

    assert len(result["flagged_claims"]) == 1
    assert result["flagged_claims"][0]["claim_text"] == "and is the best striker in Europe."
    assert result["flagged_claims"][0]["severity"] == "unsupported"
    assert "[UNVERIFIED]" in result["verified_answer"]


if __name__ == "__main__":
    test_injected_wrong_stat_is_flagged_as_contradicted()
    print("Injected-fault test passed: contradicted")