from langchain.tools import tool
from sqlalchemy.orm import Session
from . import models
from .rag.pipeline import input_embedding
import os
from exa_py import Exa

exa = Exa(api_key=os.getenv("EXA_API_KEY"))

def create_tools(user_id: str, db: Session):

    @tool
    def find_information(content: str) -> str:

        """
        Search the current user's uploaded document chunks.

        Use this when the user asks about their own uploaded files, wants evidence from
        documents, or when the curated knowledge base is not enough. The input should be
        a focused semantic search query. The output contains the top matching chunks and
        should be cited as uploaded document evidence when used.
        """

        query_embed = input_embedding(content) # convert input to vector 

        results = (
            db.query(models.DocumentChunks)
            .join(models.Document, models.Document.id == models.DocumentChunks.document_id)
            .filter(models.Document.user_id == user_id)
            .order_by(models.DocumentChunks.embedding.cosine_distance(query_embed)) # perform cosine similarity with the content imput
            .limit(5) # return the top 5 results
            .all()
        )

        if not results:
            return "No relevant information found for the query."

        return {
            "Results": [
                (
                    f"Uploaded document chunk {idx}\n"
                    f"Document ID: {chunk.document_id}\n"
                    f"Chunk index: {chunk.chunk_idx}\n"
                    f"Content: {chunk.content}"
                )
                for idx, chunk in enumerate(results)
            ]
        }

    @tool
    def internet_search(content: str, max_results: int = 5) -> str:
        
        """
        Search trusted external research sources on the internet.

        Use this only when local sources are missing, stale, or insufficient for the
        user's research question. Prefer precise queries with paper names, methods,
        datasets, or benchmark names. Return facts only when supported by the returned
        URLs, and include those URLs in the final sources list.
        """

        search_results = exa.search(
            query=content,  
            include_domains=["arxiv.org", "figshare.com", "lightning.ai"],
            type="deep-lite",
            num_results=max_results,
        )
        print(f"search_results: {search_results}") # debugging
        
        results = getattr(search_results, "results", None) or []

        if not results:
            return "No external search results found for the query."

        return results

    @tool
    def knowledge_search(content: str)->str:
        """
        Search the curated knowledge base.

        Always use this first for research questions. Treat it as the primary source for
        stable background knowledge, internal research notes, and previously indexed
        material. If the result is empty or incomplete, use find_information or
        internet_search as needed.
        """
        
        query_embed = input_embedding(content)

        results = (
            db.query(models.Knowledge)
            .filter(models.Knowledge.user_id == user_id)
            .order_by(models.Knowledge.embedding.cosine_distance(query_embed))
            .limit(10)
            .all()
        )

        if not results:
            return "No relevant curated knowledge found for the query."

        return{
            "Results": [
                (
                    f"Knowledge chunk {idx}\n"
                    f"Document ID: {chunk.document_id}\n"
                    f"Chunk index: {chunk.chunk_idx}\n"
                    f"Content: {chunk.raw_text or ''}"
                )
                for idx, chunk in enumerate(results, start=1)
            ]
        }

    return [internet_search, find_information, knowledge_search]
