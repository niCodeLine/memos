"""Small health endpoint for local checks and Docker smoke tests."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
def health_check():
    """Confirm that the API process is running."""

    return {"message": "Memo API running."}
