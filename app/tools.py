from langchain.tools import tool
from .schemas import UserInput
from app.database import get_db
from fastapi import Depends
from . import models




@tool(args_schema=UserInput)
def find_information(content: str) -> str:

    """
    Search for information in the database based on a user query.
    """

    db = get_db()

    try:

        rows = db.query(models.Documents).filter(models.Documents.user_id == user_id).all()

        if rows is None:
            return "No information found for the user."
        
    finally:
        db.close()
    
    return f"Found information for query: {content}"
