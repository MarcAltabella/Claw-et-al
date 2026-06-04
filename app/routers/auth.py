import os

from fastapi import HTTPException, status, Depends, APIRouter, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
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

@router.post("/login", status_code=status.HTTP_200_OK)
def user_login(user_credentials: schemas.UserLogin):

    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": user_credentials.email,
                "password": user_credentials.password,
            }
        )

        print("User token response:", response.session.access_token,
              "\nExpires in:", response.session.expires_in)

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": {
                "id": response.user.id,
                "email": response.user.email
            }
        }


    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Couldn't verify with these credentials")