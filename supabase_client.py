from supabase import create_client
from config import Config

# Create a Supabase client instance using credentials from .env
supabase = create_client(
    Config.SUPABASE_URL,
    Config.SUPABASE_SERVICE_ROLE_KEY
)
