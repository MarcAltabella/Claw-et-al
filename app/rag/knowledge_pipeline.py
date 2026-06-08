from pathlib import Path
from typing import List
import pymupdf4llm
from langchain_text_splitters import MarkdownTextSplitter


from langchain_core.documents import Document

from . import pipeline


def knowledge_parse(path: Path) -> List[str]:
    
    parsed_files = []

    # Parse all pdf's to .md
    for pdf_path in path.glob("*.pdf"):
        
        print(pdf_path) #debugging

        file_md = pymupdf4llm.to_markdown(pdf_path)

        parsed_files.append(file_md)

    return parsed_files


def knowledge_splitter(doc_parsed: str) -> List[str]:

    splitter = MarkdownTextSplitter(
        chunk_size=1200,  # chunk size (characters)
        chunk_overlap=150,  # chunk overlap (characters)
        add_start_index=True
    )

    chunks_list = []
    chunks = splitter.create_documents([doc_parsed]) # chunks per each document
        
    for chunk in chunks:
        chunks_list.append(chunk) # append each chunk to the list of chunks per document

    return chunks_list # document 1 chunks


def knowledge_embedding()


def knowledge_vectors_chunks(chunks: List[Document]) -> List[List[float]]:
    
    chunk_vectors = []

    for chunk in chunks:
        chunk_vectors.append(pipeline.embedding(chunk))

    return chunk_vectors