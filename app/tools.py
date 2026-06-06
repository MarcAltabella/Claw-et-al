from langchain.tools import tool
from sqlalchemy.orm import Session
from . import models
from .rag.pipeline import input_embedding
from tavily import TavilyClient
import os

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

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
    def internet_search(content: str,
                        max_results: int = 5,
                        include_raw_content: bool = False) -> str:
        
        """Search the internet for relevant information according to the user's query."""

        search_results = tavily_client.search(query=content, 
                                              num_results=max_results, 
                                              include_raw_content=include_raw_content)
        
        print(search_results) # debugging

        return search_results["answer"]

    return [find_information, internet_search]



