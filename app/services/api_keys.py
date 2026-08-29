from app.core.security import generate_api_token, hash_token
from app.db.connection import get_connection


def create_api_key(*, name: str, scopes: list[str]) -> dict:
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
