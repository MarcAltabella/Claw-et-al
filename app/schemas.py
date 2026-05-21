import supabase
from pydantic import BaseModel, EmailStr
from datetime import datetime

###### USER SCHEMAS ######

class UserSignUp(BaseModel):
    email: EmailStr
    password: str