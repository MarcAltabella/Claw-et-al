from fastapi import APIRouter, Depends, HTTPException, status
from uuid_utils import uuid4
from sqlalchemy.orm import Session

from app.database import get_db
from ..agent import agent
from ..oauth2 import get_current_user
from ..schemas import UserInput
from .. import models



router = APIRouter(
    tags=["user"]
)

# User messages

@router.post("/messages", status_code=status.HTTP_200_OK)
def read_users_me(user_input: UserInput, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
 
    # Retrieve the user from the database using the user_id from the token
    user_query = db.query(models.User).filter(models.User.id == current_user.user_id).first()

    user_query = user_query.dict() # Convert SQLAlchemy model instance to dictionary for easier handling in the agent
    print(user_query)

    if user_query is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    prompt = user_input.content

    response_message = agent.invoke(prompt=prompt, user_id=current_user.user_id, query=user_query)

    message = models.Message(
        id = uuid4(),
        user_id = current_user.user_id,
        content = response_message
    )

    db.add(message)
    db.commit()
    db.refresh(message)
    return message