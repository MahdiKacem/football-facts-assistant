import os
import time
import requests 
from dotenv import load_dotenv
from src.state import State

load_dotenv()

class DataAgent:
    def __init__(self):
        self.football_data_api_key = os.getenv("FOOTBALL_DATA_API_KEY")
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {
            "X-Auth-Token": self.football_data_api_key
        }

    def _get(self, endpoint: str, params: dict = None, max_retries: int = 3):
        url = f"{self.base_url}/{endpoint}"
        for attempt in range(max_retries):
            resp = requests.get(url, headers=self.headers, params=params)
            # rate-limit handling (HTTP 429 -> wait and retry)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 6))
                print(f"Rate limit reached. Waiting for {wait} seconds before retrying...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        raise RuntimeError(f"Failed to fetch data from {url} after {max_retries} attempts.")

    def get_team_stats(self, team_id: int):
        endpoint = f"teams/{team_id}"
        data = self._get(endpoint)
        # not the full raw API payload because agents should only see fields they'll actually use
        return {
            "team_id": data["id"],
            "team_name": data["name"],
            "founded": data.get("founded"),
            "venue": data.get("venue"),
            "squad": [
                {"player_id": player["id"], "name": player["name"], "position": player.get("position"), "nationality": player.get("nationality")} 
                for player in data.get("squad", [])
            ],
            "competition": [
                {"competition_id": comp["id"], "name": comp["name"]} 
                for comp in data.get("competitions", [])
            ]
        }

    def get_competition_scorers(self, competition_code: str, limit: int = 20) -> list[dict]:
        data = self._get(f"competitions/{competition_code}/scorers", params={"limit": limit})
        return [
            {
                "player_id": s["player"]["id"],
                "player_name": s["player"]["name"],
                "team": s["team"]["name"],
                # 'or 0' if the field is missing (expl: for players who haven't scored yet)
                "goals": s.get("goals") or 0,
                "assists": s.get("assists") or 0,
                "penalties": s.get("penalties") or 0,
                "matches_played": s.get("playedMatches") or 0,
            }
            for s in data.get("scorers", [])
        ]

    def compare_players(self, player_a_name: str, player_b_name: str, competition_code: str) -> dict:
        scorers = self.get_competition_scorers(competition_code, limit=50)
        a = next((s for s in scorers if player_a_name.lower() in s["player_name"].lower()), None)
        b = next((s for s in scorers if player_b_name.lower() in s["player_name"].lower()), None)
        return {"player_a": a, "player_b": b, "competition": competition_code}

    def data_node(self, state: State) -> dict:
        if "team_id" in state:
            return {"stats_data": self.get_team_stats(state["team_id"])}

        competition_code = state.get("competition_code")
        player_a_name = state.get("player_a_name")
        player_b_name = state.get("player_b_name")

        if player_a_name and player_b_name and competition_code:
            return {
                "stats_data": self.compare_players(
                    player_a_name,
                    player_b_name,
                    competition_code,
                )
            }

        if competition_code:
            return {
                "stats_data": {
                    "competition": competition_code,
                    "scorers": self.get_competition_scorers(competition_code),
                }
            }

        raise ValueError(
            "data_node requires team_id, competition_code, or player comparison fields"
        )