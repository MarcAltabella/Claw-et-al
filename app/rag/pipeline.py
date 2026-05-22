from langchain_openai import OpenAIEmbeddings
from loader import load_pdf
from split import splitter
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
    raise ValueError("Couldn't find the API")

def load_files(file_path: str) -> List[str]:
    docs = load_pdf(file_path=file_path)

    return docs

def chunk_files(docs: List) -> List[str]:
        
    chunks = splitter(docs) # list of chunks

    return chunks


def embedding(chunks: List) -> List:
    texts = []

    for chunk in chunks:
        texts.append(chunk.page_content)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        dimensions=1536,
        chunk_size=200
        ) # embeddings model

    vectors = embeddings.embed_documents(texts) # Crete the embeddings for each chunk
    print(len(vectors), len(vectors[0]))
    
    return vectors, texts
