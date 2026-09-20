COMPETITION_ALIASES = {
    "premier league": "PL", "epl": "PL",
    "la liga": "PD", "laliga": "PD",
    "champions league": "CL", "ucl": "CL",
    "bundesliga": "BL1",
    "serie a": "SA",
    "ligue 1": "FL1",
}

def resolve_competition_code(query: str) -> str | None:
    q = query.lower()
    for alias, code in COMPETITION_ALIASES.items():
        if alias in q:
            return code
    return None