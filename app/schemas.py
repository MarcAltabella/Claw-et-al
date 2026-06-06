import supabase
from pydantic import BaseModel, EmailStr, Field

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

class UserInput(BaseModel):
    content: str


###### MESSAGE SCHEMAS ######

class AgentResponse(BaseModel):
    response: str = Field(description="The agent's response to the user's query.")
    reasoning: str = Field(description="The agent's reasoning process, including which tools were used and how the final answer was derived.")
    sources: list[str] = Field(description="A list of sources or references used by the agent to generate the response, if applicable.")