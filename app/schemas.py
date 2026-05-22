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

###### DOCUMENTS INGESTION ######