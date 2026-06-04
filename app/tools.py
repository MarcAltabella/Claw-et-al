from langchain.tools import tool
from .schemas import UserInput

@tool(args_schema=UserInput)
def find_information(prompt: str, user_id: str, query) -> str:

    """
    Search for information in the database matching the user_id based on a query.
    """


    return f"Found information for query: {prompt} and user_id: {user_id}"