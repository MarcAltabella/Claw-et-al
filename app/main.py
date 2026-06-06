from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, documents, messages

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins, # allow domains
    allow_credentials=True, # allow http methods (e.g. not allowing POST requests)
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(messages.router)