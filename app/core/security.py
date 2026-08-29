"""Small security helpers for Memo API keys.

The plain token is shown only when it is created. After that, the database stores
only a SHA-256 hash, so leaking the database does not directly leak usable keys.
"""

import hashlib
import hmac
import secrets

TOKEN_PREFIX = "remi"


def generate_api_token() -> str:
    """Create a random API token safe enough for local bots and integrations."""

    return f"{TOKEN_PREFIX}_{secrets.token_urlsafe(32)}"


def hash_token(token: str) -> str:
    """Hash a token before storing or looking it up in PostgreSQL."""

    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token(token: str, stored_hash: str) -> bool:
    """Compare a raw token with a stored hash without leaking timing clues."""

    return hmac.compare_digest(hash_token(token), stored_hash)


def has_scope(scopes: list[str], required_scope: str) -> bool:
    """Return whether an API key can perform an action.

    `*` works as a simple admin-style wildcard for local development or trusted
    automations.
    """

    return "*" in scopes or required_scope in scopes
