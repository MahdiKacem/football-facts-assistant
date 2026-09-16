import os
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

from src.ingestion.chunk_pdf import load_and_chunk_pdf

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")

RULES_COLLECTION = "football_rules"
STATS_COLLECTION = "football_stats"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def ingest_rules(pdf_path: str) -> QdrantVectorStore:
    chunks = load_and_chunk_pdf(pdf_path)
    vector_store = QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        url=QDRANT_URL,
        collection_name=RULES_COLLECTION
    )

    print(f"Successfully ingested {len(chunks)} chunks into Qdrant collection '{RULES_COLLECTION}'")
    return vector_store

def stats_to_documents(team_stats: dict) -> list[Document]:
    documents = []
    for match in team_stats.get("recent_matches", []):
        text = (
            f"{team_stats['team_name']} vs {match['opponent']}"
            f"on {match['date']}: {match['score']}."
        )

        documents.append(Document(
            page_content=text,
            metadata={
                "type": "stat_snapshot",
                "source": "football-data.org",
                "team_id": team_stats.get("team_id"),
                "match_id": match.get("match_id"),
                "retrieved_at": team_stats.get("date"),
            }
        ))
        return documents

def ingest_stats(stats_snapshots: list[dict]) -> QdrantVectorStore:
    all_docs: list[Document] = []
    for snapshot in stats_snapshots:
        docs = stats_to_documents(snapshot)
        all_docs.extend(docs)

    vector_store = QdrantVectorStore.from_documents(
        all_docs,
        embeddings,
        url=QDRANT_URL,
        collection_name=STATS_COLLECTION
    )
    print(f"Successfully ingested {len(all_docs)} stat snapshots into Qdrant collection '{STATS_COLLECTION}'")
    return vector_store

def get_rules_store() -> QdrantVectorStore:
    return QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=QDRANT_URL,
        collection_name=RULES_COLLECTION
    )

def get_stats_store() -> QdrantVectorStore:
    return QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=QDRANT_URL,
        collection_name=STATS_COLLECTION
    )