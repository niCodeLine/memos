"""Admin endpoints for creating and managing API keys."""

from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import settings
from app.schemas import ApiKeyCreate, ApiKeyCreated, ApiKeyOut
from app.services.api_keys import create_api_key, list_api_keys, revoke_api_key

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin_token(x_admin_token: str | None) -> None:
    """Protect local admin endpoints with the bootstrap token from `.env`."""

    if x_admin_token != settings.ADMIN_BOOTSTRAP_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token.",
        )


@router.post("/api-keys", response_model=ApiKeyCreated)
def create_key(
    payload: ApiKeyCreate,
    x_admin_token: str | None = Header(default=None),
):
    """Create a bot/integration API key.

    The plain token appears only in this response, so copy it immediately.
    """

    require_admin_token(x_admin_token)
    return create_api_key(name=payload.name, scopes=payload.scopes)


@router.get("/api-keys", response_model=list[ApiKeyOut])
def list_keys(x_admin_token: str | None = Header(default=None)):
    """List API keys and their status without exposing the token hash."""

    require_admin_token(x_admin_token)
    return list_api_keys()


@router.patch("/api-keys/{api_key_id}/revoke", response_model=ApiKeyOut)
def revoke_key(
    api_key_id: int,
    x_admin_token: str | None = Header(default=None),
):
    """Revoke a key so future requests using it are rejected."""

    require_admin_token(x_admin_token)
    key = revoke_api_key(api_key_id)
    if key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key {api_key_id} not found.",
        )
    return key
