import logging
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    url: str = os.getenv("SUPABASE_URL", "")
    key: str = os.getenv("SUPABASE_KEY", "")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

    try:
        client: Client = create_client(url, key)
        logger.info("Supabase client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        raise