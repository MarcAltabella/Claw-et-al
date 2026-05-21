import os

from fastapi import HTTPException, status, Depends, APIRouter, Response
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..supabase_client import supabase


router = APIRouter(
    tags=['Auth']
)

##### CREATE USER ######
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserSignUp, db: Session = Depends(get_db)):

    # Check if email exists
    user_query = db.query(models.User).filter(models.User.email == user.email).first()

    if user_query:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with email {user.email} already exists"
        )

    response = supabase.auth.sign_up(
        {
            "email": user.email,
            "password": user.password,
        }
    )

    supabase_user = response.user
    
    if not supabase_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supabase user creation failed"
        )

    db_user = models.User(id=supabase_user.id,
                            email=user.email,
                            password_hash="supabase-managed")
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": f"User with id {supabase_user.id} successfully created"}


##### LOGIN USER ######