from langchain.tools import tool
from sqlalchemy.orm import Session
from . import models
from .rag.pipeline import input_embedding



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


        for chunk in results:
            "\n\n".join(chunk.content)# extract the content of each chunk
        
        print(chunk.content) # debugging
        return chunk.content

    return [find_information]


