from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import settings
from app.schemas import ApiKeyCreate, ApiKeyCreated, ApiKeyOut
from app.services.api_keys import create_api_key, list_api_keys, revoke_api_key

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin_token(x_admin_token: str | None) -> None:
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
    require_admin_token(x_admin_token)
    return create_api_key(name=payload.name, scopes=payload.scopes)


@router.get("/api-keys", response_model=list[ApiKeyOut])
def list_keys(x_admin_token: str | None = Header(default=None)):
    require_admin_token(x_admin_token)
    return list_api_keys()


@router.patch("/api-keys/{api_key_id}/revoke", response_model=ApiKeyOut)
def revoke_key(
    api_key_id: int,
    x_admin_token: str | None = Header(default=None),
):
    require_admin_token(x_admin_token)
    key = revoke_api_key(api_key_id)
    if key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key {api_key_id} not found.",
        )
    return key
