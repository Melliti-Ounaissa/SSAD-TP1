# test_connection_fixed.py
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(os.getenv("VITE_SUPABASE_URL"), os.getenv("VITE_SUPABASE_SUPABASE_ANON_KEY"))

try:
    response = supabase.table("users").select("*").limit(1).execute()
    print("✅ Connected successfully! Supabase is working.")
    print("Sample data:", response.data)
except Exception as e:
    print("❌ Connection failed:")
    print(e)
