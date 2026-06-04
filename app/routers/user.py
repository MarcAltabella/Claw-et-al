from openai import OpenAI
from fastapi import APIRouter, HTTPException
from ..oauth2 import get_current_user



router = APIRouter(
    tags=["user"]
)