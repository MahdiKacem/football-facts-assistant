from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def load_and_chunk_pdf(pdf_path: str) -> list[Document]:
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(pages)

    for chunk in chunks:
        chunk.metadata["type"] = "rule"
        chunk.metadata["source"] = "IFAB Laws of the Game"

    return chunks