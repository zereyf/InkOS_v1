import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from your .env file
load_dotenv()

# Securely fetch credentials from the environment
SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("System Fault: Missing Supabase environment variables.")

# Initialize and export the client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)