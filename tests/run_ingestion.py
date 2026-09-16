import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.embed_and_upsert import ingest_rules, ingest_stats

example_stats_snapshot = {
    "team_name": "Esperence Tunis",
    "team_id": 1,
    "recent_matches": [
        {"opponent": "Club Africain", "date": "2026-08-30", "score": "2-1", "match_id": "m1"},
        {"opponent": "Etoile du Sahel", "date": "2026-09-06", "score": "0-0", "match_id": "m2"},
    ],
}

def main() -> None:
    ingest_rules(str(PROJECT_ROOT / "data" / "Laws of the Game 2026_27.pdf"))
    ingest_stats([example_stats_snapshot])


if __name__ == "__main__":
    main()

"""
output: 
Successfully ingested 666 chunks into Qdrant collection 'football_rules'
Successfully ingested 1 stat snapshots into Qdrant collection 'football_stats'
"""