from functools import lru_cache

from supabase import Client, create_client

from app.config.secrets import get_supabase_config


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:

    config = get_supabase_config()

    return create_client(
        config["url"],
        config["key"],
    )