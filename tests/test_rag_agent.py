import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.rag_agent import retrieve_context

if __name__ == "__main__":
    queries = [
        "What's the offside rule for a defender running back?",
        "What is the rule for a handball in the penalty area?",
        "How many substitutions are allowed in a match?",
        "Was that a valid goal after a back-pass to the keeper?",
    ]

    for q in queries:
        results = retrieve_context(q)
        print("—" * 60)
        print("QUERY:", q)
        print(f"RESULTS ({len(results)}):")
        for r in results:
            print(f"  [{r['metadata'].get('type')}] {r['text'][:100]}...")