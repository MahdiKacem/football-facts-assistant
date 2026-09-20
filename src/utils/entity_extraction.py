import re

from transformers import pipeline

_ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

def extract_person_names(text: str) -> list[str]:
    comparison = re.search(
        r"\bcompare\s+(.+?)\s+and\s+(.+?)(?:'s|\s+(?:goals?|assists?|stats?|numbers?)\b|\s+this\b|$)",
        text,
        flags=re.IGNORECASE,
    )
    if comparison:
        return [part.strip(" ,.'\"") for part in comparison.groups()]

    entities = _ner(text)
    return [e["word"] for e in entities if e["entity_group"] == "PER"]