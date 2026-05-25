from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

print(f"Using Supabase url: {supabase_url}")

supabase = create_client(supabase_url, supabase_key)