import supabase
from pydantic import BaseModel, EmailStr
from datetime import datetime

###### USER SCHEMAS ######

class User(BaseModel):
    email: EmailStr
    password: str

class UserSignUp(User):
    pass

class UserLogin(User):
    pass

class UserResponse(BaseModel):
    user_id: str
    email: EmailStr

    class Config:
        orm_mode = True
###### DOCUMENTS INGESTION ######