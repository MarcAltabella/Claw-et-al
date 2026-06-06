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
    tags=["messages"],
    prefix="/messages"
)

# User messages

@router.post("/send_message", status_code=status.HTTP_200_OK)
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
                "content": prompt
            }
        ]
    })

    structured_response = response["structured_response"] # pydantic model reply

    response_message = structured_response.response
    reasoning = structured_response.reasoning
    sources = structured_response.sources


    message = models.Message(
        id = uuid4(),
        user_id = current_user.user_id,
        content = response_message
    )

    print(f"Response message: {response_message}") # debugging
    
    db.add(message)
    db.commit()
    db.refresh(message)

    return {
        "message": response_message,
        "reasoning": reasoning,
        "sources": sources
    }


@router.get("/{message_id}", status_code=status.HTTP_200_OK)
def get_messages(db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    messages_query = db.query(models.Message).filter(models.Message.user_id == current_user.user_id).all()

    if not messages_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return {
        "Message": [
            {
                "message_id": message.id,
                "user_id": message.id,
                "content": message.content
            }
            for message in messages_query
        ]
    }