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
    
    prompt = f"Find information for: {user_input.content}"

    tools = create_tools(user_id=current_user.user_id, db=db)
    agent = create_agent(tools=tools)

    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    })

    print(response)

    response_message = response["messages"][-1].content[0]["text"]

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
