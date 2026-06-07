from langchain.tools import tool
from sqlalchemy.orm import Session
from . import models
from .rag.pipeline import input_embedding
from tavily import TavilyClient
import os
from exa_py import Exa

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
exa = Exa(api_key=os.getenv("EXA_API_KEY"))

def create_tools(user_id: str, db: Session):

    @tool
    def find_information(content: str) -> str:

        """Search the current user's uploaded document chunks for relevant information."""


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


        return "\n\n".join([chunk.content for chunk in results])
    

    @tool
    def internet_search(content: str, max_results: int = 5) -> str:
        
        """Search the internet for relevant information according to the user's query. Return the reasoning process, sources (links), and final answer."""

        search_results = exa.search(
            query=content,  
            include_domains=["arxiv.org", "figshare.com", "lightning.ai"],
            type="deep-lite"
        )
        print(f"search_results: {search_results}") # debugging
        
        return search_results

    return [internet_search, find_information]


