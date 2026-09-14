import os
import requests
from dotenv import load_dotenv
from transformers import pipeline

load_dotenv()

class NewsAgent:

    def __init__(self):
        self.news_api_key = os.getenv("NEWSAPI_API_KEY")
        self.news_api_url = "https://newsapi.org/v2/everything"
        self.ner_pipeline = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
        self.zero_shot_pipeline = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )

    def fetch_football_news(self, query: str, limit: int = 50) -> list[dict]:
        params = {
            "q": query,
            "language": "en",
            "pageSize": limit,
            "sortBy": "publishedAt",
            "apiKey": self.news_api_key
        }
        response = requests.get(self.news_api_url, params=params)
        response.raise_for_status()
        data = response.json()

        return [
            {
                "title": article["title"],
                "description": article.get("description", "No description available"),
                "source": article["source"]["name"],
                "url": article["url"],
                "publishedAt": article["publishedAt"]
            }
            for article in data.get("articles", [])
        ]

    def extract_entities(self, text: str) -> list[dict]:
        results = self.ner_pipeline(text)
        seen = {}
        for result in results:
            key = result['word']
            score = result['score']
            # deduplicate entities by their text and keep the one with the highest score
            if key not in seen or score > seen[key]['score']:
                seen[key] = {"text": key, "entity": result["entity_group"], "score": score}
        return list(seen.values())

    def classify_topic(self, text: str) -> dict:
        candidate_labels = ["injury", "transfer", "match result", "tactics", "player profile", "team news", "live match", "match preview"]
        result = self.zero_shot_pipeline(text, candidate_labels)
        top_score = result["scores"][0]
        return {
            "top_label": result["labels"][0] if top_score > 0.5 else "uncertain",
            "score": result["scores"][0],
            "all_scores": dict(zip(result["labels"], [score for score in result["scores"]]))

        }
