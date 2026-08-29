"""Database operations for API keys.

The admin token creates and manages keys. Bots and assistants then use those
keys to call the reminder endpoints through `X-API-Key`.
"""

from app.core.security import generate_api_token, hash_token
from app.db.connection import get_connection


def create_api_key(*, name: str, scopes: list[str]) -> dict:
    """Create an API key and return the plain token once.

    The database stores only the hash. If the caller loses the returned token,
    the safe path is to revoke it and create a new one.
    """

    token = generate_api_token()
    token_hash = hash_token(token)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO api_keys (name, token_hash, scopes)
                VALUES (%s, %s, %s)
                RETURNING id, name, scopes
                """,
                (name, token_hash, scopes),
            )
            row = cursor.fetchone()
        conn.commit()
    finally:
        conn.close()

    return {**row, "token": token}


def find_active_key(token: str) -> dict | None:
    """Return the active key for a token and update its last-used timestamp."""

    token_hash = hash_token(token)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE api_keys
                SET last_used_at = NOW()
                WHERE token_hash = %s AND revoked_at IS NULL
                RETURNING id, name, scopes
                """,
                (token_hash,),
            )
            row = cursor.fetchone()
        conn.commit()
    finally:
        conn.close()
    return row


def list_api_keys() -> list[dict]:
    """List API keys without exposing token hashes or plain tokens."""

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, scopes, revoked_at, last_used_at, created_at
                FROM api_keys
                ORDER BY created_at DESC, id DESC
                """
            )
            return cursor.fetchall()
    finally:
        conn.close()


def revoke_api_key(api_key_id: int) -> dict | None:
    """Mark an API key as revoked without deleting its audit trail."""

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE api_keys
                SET revoked_at = COALESCE(revoked_at, NOW())
                WHERE id = %s
                RETURNING id, name, scopes, revoked_at, last_used_at, created_at
                """,
                (api_key_id,),
            )
            row = cursor.fetchone()
        conn.commit()
    finally:
        conn.close()
    return row
