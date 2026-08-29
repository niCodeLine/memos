from fastapi import APIRouter, Depends

from app.ai.enrichment import enrich_reminder
from app.dependencies import require_scope
from app.schemas import ReminderCreate, ReminderEnrichment

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/enrich-reminder", response_model=ReminderEnrichment)
def enrich(
    payload: ReminderCreate,
    api_key: dict = Depends(require_scope("reminders:write")),
):
    return enrich_reminder(payload.model_dump())
