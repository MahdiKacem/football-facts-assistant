import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agents.news_agent import NewsAgent


if __name__ == "__main__":
    news_agent = NewsAgent()

    articles = news_agent.fetch_football_news("Manchester United", limit=5)
    print(f"Fetched {len(articles)} articles.")

    for article in articles:
        text = f"{article['title']}: {article['description'] or ''} " 
        entities = news_agent.extract_entities(text)
        topic = news_agent.classify_topic(text)

        print("**" * 40)
        print(f"Article: {article['title']}")
        print(f"Entities: {entities}")
        print(f"Topic: {topic}")