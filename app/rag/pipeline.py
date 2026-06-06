from xml.dom.minidom import Document

from fastapi import UploadFile
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from .split import splitter
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
    raise ValueError("Couldn't find the API") 

def load_files(input_file: UploadFile) -> List[Document]: # will return a list of documents (each document is a page of the original file)
    
    # Save the uploaded file temporarily
    file_path = f"temp_{input_file.filename}"
    
    # Write the file to the disk
    with open(file_path, "wb") as f:
        f.write(input_file.file.read())

    loader = PyPDFLoader(file_path=file_path)
    documents = loader.load()

    for docs in documents:
        print(docs.page_content) # debugging

    return documents

def chunk_files(docs: List[Document]) -> List[str]:
        
    chunks = splitter(docs) # list of chunks (fragments of each page)

    for chunk in chunks:
        print(chunk) # debugging

    return chunks


def embedding(chunk: Document) -> List[float]:

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        dimensions=1536,
        chunk_size=200
        ) # embeddings model
    
    text = chunk.page_content
    print(f"Chunk content: {text}") # debugging

    vector = embeddings.embed_query(text) # Crete the embeddings for each chunk
    
    return vector # return the embedding for the chunk


def input_embedding(prompt: str) -> List[float]:

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        dimensions=1536,
        chunk_size=200
        ) # embeddings model

    vector = embeddings.embed_query(prompt) # Crete the embeddings for the user input
    
    return vector # return the embedding for the user input