import json
import os
from functools import lru_cache

import boto3


SECRET_NAME = "emergency-platform/supabase"


@lru_cache(maxsize=1)
def get_supabase_config() -> dict:
    """
    Obtiene las credenciales de Supabase.

    En desarrollo local usa variables de entorno.
    En AWS Lambda utiliza Secrets Manager.
    """

    running_on_lambda = bool(
        os.getenv("AWS_LAMBDA_FUNCTION_NAME")
    )

    if not running_on_lambda:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url:
            raise RuntimeError(
                "SUPABASE_URL is not configured"
            )

        if not key:
            raise RuntimeError(
                "SUPABASE_KEY is not configured"
            )

        return {
            "url": url,
            "key": key,
        }

    client = boto3.client(
        "secretsmanager"
    )

    response = client.get_secret_value(
        SecretId=SECRET_NAME
    )

    secret = json.loads(
        response["SecretString"]
    )

    if "SUPABASE_URL" not in secret:
        raise RuntimeError(
            "SUPABASE_URL missing from AWS secret"
        )

    if "SUPABASE_KEY" not in secret:
        raise RuntimeError(
            "SUPABASE_KEY missing from AWS secret"
        )

    return {
        "url": secret["SUPABASE_URL"],
        "key": secret["SUPABASE_KEY"],
    }