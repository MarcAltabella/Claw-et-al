from pathlib import Path
from typing import List

from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from langchain_core.documents import Document

from . import pipeline

EXPORT_TYPE = ExportType.DOC_CHUNKS


def knowledge_load(path: Path) -> List[tuple[Path, List[Document]]]:
    
    loaded_files = []

    # Parse all pdf's to .md
    for pdf_path in path.glob("*.pdf"):
        
        print(pdf_path) #debugging

        loader = DoclingLoader(
            file_path=pdf_path,
            export_type=EXPORT_TYPE
            )
        
        chunks = loader.load() # returns List[Document]

        loaded_files.append((pdf_path, chunks))
    
    print(f"Number of docs: {len(loaded_files)}")

    return loaded_files


def knowledge_vectors_chunks(chunks: List[Document]) -> List[List[float]]:
    
    chunk_vectors = []

    for chunk in chunks:
        chunk_vectors.append(pipeline.embedding(chunk))

    return chunk_vectors