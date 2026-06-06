from fastapi import APIRouter, Depends, HTTPException, status
from uuid import uuid4
from sqlalchemy.orm import Session

from app.database import get_db
from ..agent import create_agent
from ..oauth2 import get_current_user
from ..schemas import UserInput
from .. import models
from ..tools import create_tools



router = APIRouter(
    tags=["user"]
)

# User messages

@router.post("/messages", status_code=status.HTTP_200_OK)
def read_users_me(user_input: UserInput, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
 
    # Retrieve the user from the database using the user_id from the token
    user_query = db.query(models.User).filter(models.User.id == current_user.user_id).first()

    if user_query is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    prompt = f"""
    Answer this user request: {user_input.content}

    First, use find_information to retrieve relevant information from the user's uploaded documents.
    Then, if current external information is needed, use internet_search.
    Finally, combine both sources into a concise answer.
    """

    tools = create_tools(user_id=current_user.user_id, db=db)
    agent = create_agent(tools=tools, user_id=current_user.user_id)

    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    })

    last_content = response["messages"][-1].content

    print("last_content:", type(last_content), last_content)

    if isinstance(last_content, str):
        response_message = last_content

    elif isinstance(last_content, list):
        text_blocks = [
            block.get("text", "")
            for block in last_content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        response_message = "\n\n".join(text_blocks)

    else:
        response_message = str(last_content)

    message = models.Message(
        id = uuid4(),
        user_id = current_user.user_id,
        content = response_message
    )

    print(response_message) # debugging
    
    db.add(message)
    db.commit()
    db.refresh(message)

    return response_message
