import requests
from functools import lru_cache

THESPORTSDB_BASE = "https://www.thesportsdb.com/api/v1/json/3"  

class ResolutionResult:
    def __init__(self, status, player=None, candidates=None):
        self.status = status          # "resolved" | "ambiguous" | "not_found"
        self.player = player          # dict, if resolved
        self.candidates = candidates or []  # list of dicts, if ambiguous

@lru_cache(maxsize=256) # avoid re-hitting the API 
def resolve_player_name(name: str) -> ResolutionResult:
    resp = requests.get(f"{THESPORTSDB_BASE}/searchplayers.php", params={"p": name}, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    players = data.get("player") or []

    if not players:
        return ResolutionResult(status="not_found")

    if len(players) == 1:
        return ResolutionResult(status="resolved", player=players[0])

    # Multiple matches — genuinely ambiguous (e.g. common surname, retired player
    # sharing a name with an active one). Don't silently guess.
    return ResolutionResult(status="ambiguous", candidates=players)