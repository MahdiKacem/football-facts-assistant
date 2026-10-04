import re

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

LAW_TITLES = {
    1: "The Field of Play",
    2: "The Ball",
    3: "The Players",
    4: "The Players' Equipment",
    5: "The Referee",
    6: "The Other Match Officials",
    7: "The Duration of the Match",
    8: "The Start and Restart of Play",
    9: "The Ball in and out of Play",
    10: "Determining the Outcome of a Match",
    11: "Offside",
    12: "Fouls and Misconduct",
    13: "Free Kicks",
    14: "The Penalty Kick",
    15: "The Throw-in",
    16: "The Goal Kick",
    17: "The Corner Kick",
}

LAW_HEADING_PATTERN = re.compile(
    r"(?m)^.*?\bLaw\s+(?P<number>1[0-7]|[1-9])\s*\|\s*(?P<title>[^\r\n]+?)\s*$"
)


def _find_law_sections(text: str) -> list[tuple[str, int, str]]:
    sections = []
    matches = []

    seen_numbers = set()
    for match in LAW_HEADING_PATTERN.finditer(text):
        number = int(match.group("number"))
        title = match.group("title").strip()
        normalized_title = title.replace("’", "'")
        if number not in seen_numbers and LAW_TITLES.get(number) == normalized_title:
            matches.append((match, number, title))
            seen_numbers.add(number)

    for index, (match, number, title) in enumerate(matches):
        end = matches[index + 1][0].start() if index + 1 < len(matches) else len(text)
        sections.append((text[match.start():end].strip(), number, title))

    return sections


def _split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    full_text = "\n\n".join(document.page_content for document in documents)
    law_sections = _find_law_sections(full_text)

    if not law_sections:
        return splitter.split_documents(documents)

    chunks = []
    first_law_start = full_text.find(law_sections[0][0])
    preamble = full_text[:first_law_start].strip()
    if preamble:
        chunks.extend(splitter.split_documents([Document(page_content=preamble)]))

    for section, number, title in law_sections:
        law_chunks = splitter.split_documents([Document(page_content=section)])
        for chunk_index, chunk in enumerate(law_chunks):
            chunk.metadata.update({
                "law_number": number,
                "law_title": title,
                "law_chunk_index": chunk_index,
            })
        chunks.extend(law_chunks)

    last_law_end = full_text.rfind(law_sections[-1][0]) + len(law_sections[-1][0])
    postamble = full_text[last_law_end:].strip()
    if postamble:
        chunks.extend(splitter.split_documents([Document(page_content=postamble)]))

    return chunks

def load_and_chunk_pdf(pdf_path: str) -> list[Document]:
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    chunks = _split_documents(pages)

    for chunk in chunks:
        chunk.metadata["type"] = "rule"
        chunk.metadata["source"] = "IFAB Laws of the Game"

    return chunks