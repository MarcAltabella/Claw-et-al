from pathlib import Path
from typing import List
import pymupdf4llm
from langchain_text_splitters import MarkdownTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.documents import Document



def knowledge_parse(path: Path) -> List[tuple[Path, str]]:
    
    parsed_files = []

    # Parse all pdf's to .md
    for pdf_path in path.glob("*.pdf"):
        
        print(pdf_path) #debugging

        file_md = pymupdf4llm.to_markdown(pdf_path)

        parsed_files.append((pdf_path, file_md))

    return parsed_files


def knowledge_splitter(doc_parsed: str) -> List[Document]:

    splitter = MarkdownTextSplitter(
        chunk_size=1200,  # chunk size (characters)
        chunk_overlap=150,  # chunk overlap (characters)
        add_start_index=True
    )

    chunks_list = splitter.create_documents([doc_parsed]) # chunks per each document
    return chunks_list # document 1 chunks


model_name = "BAAI/bge-small-en-v1.5"
model_kwargs = {'device': 'cuda'}
encode_kwargs = {'normalize_embeddings': True}

model = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

def knowledge_embedding(chunks: List[Document])->List[List[float]]:

    texts=[]
    for chunk in chunks:
        texts.append(chunk.page_content)
        
    chunks_embedded = model.embed_documents(texts) # List[str]
    return chunks_embedded


def knowledge_vectors_chunks(chunks: List[Document]) -> List[List[float]]:
    
    chunk_vectors = []

    for chunk in chunks:
        chunk_vectors.append(pipeline.embedding(chunk))

    return chunk_vectors