from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import AuthApiError
from .supabase_client import supabase
from .schemas import UserResponse

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials

    try:
        user_response = supabase.auth.get_user(token)

        user_id = user_response.user.id
        email = user_response.user.email

         # Check if user_id is present in the token        

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user id"
            )

        return UserResponse(
            user_id=user_id, 
            email=email
            )

    except AuthApiError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {error.message}"
        )


