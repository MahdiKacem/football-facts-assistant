import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.documents import Document

from src.ingestion.chunk_pdf import _split_documents


def test_rule_book_chunks_keep_laws_separate_and_add_metadata():
    pages = [Document(page_content=(
        "Introductory notes\n\n"
        "Laws of the Game 2026/27 | Law 1 | The Field of Play\n"
        + ("Field details. " * 80)
        + "\n\n"
        "Laws of the Game 2026/27 | Law 2 | The Ball\n"
        + ("Ball details. " * 80)
    ))]

    chunks = _split_documents(pages)

    law_chunks = [chunk for chunk in chunks if "law_number" in chunk.metadata]
    assert law_chunks
    assert {chunk.metadata["law_number"] for chunk in law_chunks} == {1, 2}
    assert all(
        chunk.metadata["law_title"] == ("The Field of Play" if chunk.metadata["law_number"] == 1 else "The Ball")
        for chunk in law_chunks
    )


def test_non_rule_book_documents_keep_generic_chunking():
    chunks = _split_documents([Document(page_content="A short document without law headings.")])

    assert len(chunks) == 1
    assert "law_number" not in chunks[0].metadata