import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agents.data_agent import DataAgent
import json

data_agent = DataAgent()

print("=== Premier League scorers ===")
print(json.dumps(data_agent.get_competition_scorers("PL", limit=10), indent=2)[:1000])

print("\n=== Compare players ===")
print(json.dumps(data_agent.compare_players("Erling Haaland", "Bruno Fernandes", "PL"), indent=2)[:1000])