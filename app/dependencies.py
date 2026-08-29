"""FastAPI dependencies that protect endpoints with API keys and scopes."""

from collections.abc import Callable

from fastapi import Header, HTTPException, status

from app.core.security import has_scope
from app.services.api_keys import find_active_key


async def require_api_key(x_api_key: str | None = Header(default=None)) -> dict:
    """Read `X-API-Key`, validate it, and return the matching database row."""

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header.",
        )

    key = find_active_key(x_api_key)
    if key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key.",
        )
    return key


def require_scope(required_scope: str) -> Callable:
    """Build a dependency for endpoints that need a specific permission."""

    async def dependency(x_api_key: str | None = Header(default=None)) -> dict:
        key = await require_api_key(x_api_key)
        if not has_scope(key["scopes"], required_scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {required_scope}.",
            )
        return key

    return dependency
