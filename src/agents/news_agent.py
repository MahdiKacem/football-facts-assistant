import os
import requests
from src.utils.entity_extraction import extract_person_names
from dotenv import load_dotenv
from transformers import pipeline
from src.state import State

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
                "id": f"news_{i}",
                "title": article["title"],
                "description": article.get("description", "No description available"),
                "source": article["source"]["name"],
                "url": article["url"],
                "publishedAt": article["publishedAt"]
            }
            for i, article in enumerate(data.get("articles", []))
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

    def news_node(self, state: State) -> dict:
        query = state.get("news_query", state.get("query"))
        if not query:
            raise ValueError("news_node requires query or news_query in state")

        names = extract_person_names(query)
        if len(names) >= 2:
            query = " ".join(names)

        articles = self.fetch_football_news(query, limit=state.get("news_limit", 50))
        enriched_articles = []
        for article in articles:
            text = f"{article['title']}: {article['description'] or ''}"
            enriched_articles.append({
                **article,
                "entities": self.extract_entities(text),
                "topic": self.classify_topic(text),
            })

        return {"news_data": enriched_articles}
