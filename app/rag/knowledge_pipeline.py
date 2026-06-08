from pathlib import Path
from typing import List
import pymupdf4llm
from langchain_text_splitters import MarkdownTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.documents import Document
from concurrent.futures import ProcessPoolExecutor




def parse_single_pdf(pdf_path: Path) -> tuple[Path, str]:
    file_md = pymupdf4llm.to_markdown(pdf_path)
    return pdf_path, file_md

def knowledge_parse(path: Path) -> List[tuple[Path, str]]:
    
    pdf_paths = list(path.glob("*.pdf"))

    results = []

    with ProcessPoolExecutor(max_workers=4) as executor:
        
        parsed_files = executor.map(parse_single_pdf, pdf_paths) # Create a list with maps (fn, iterables)

    for parsed_file in parsed_files:
        results.append(parsed_file)

        return results



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