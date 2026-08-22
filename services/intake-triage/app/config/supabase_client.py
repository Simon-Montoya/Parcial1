from supabase import create_client, Client

from app.config.settings import settings


def get_supabase_client() -> Client:
    if not settings.SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL is not configured")

    if not settings.SUPABASE_KEY:
        raise RuntimeError("SUPABASE_KEY is not configured")

    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )