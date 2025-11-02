import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("VITE_SUPABASE_URL")
supabase_key = os.getenv("VITE_SUPABASE_SUPABASE_ANON_KEY")

# Create Supabase client (simple version without custom options)
supabase: Client = create_client(supabase_url, supabase_key)

def get_supabase_client():
    return supabase
