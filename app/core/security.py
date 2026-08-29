import hashlib
import hmac
import secrets

TOKEN_PREFIX = "remi"


def generate_api_token() -> str:
    return f"{TOKEN_PREFIX}_{secrets.token_urlsafe(32)}"


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token(token: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_token(token), stored_hash)


def has_scope(scopes: list[str], required_scope: str) -> bool:
    return "*" in scopes or required_scope in scopes
