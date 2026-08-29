from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import require_scope
from app.schemas import (
    NotificationAttemptList,
    ReminderCreate,
    ReminderList,
    ReminderOut,
    ReminderStatus,
    ReminderUpdate,
)
from app.services.reminders import (
    create_reminder,
    delete_reminder,
    get_reminder,
    list_attempts,
    list_reminders,
    update_reminder,
)

router = APIRouter(prefix="/reminders", tags=["reminders"])

NON_NULL_UPDATE_FIELDS = {
    "text",
    "remind_at",
    "urgency",
    "channel",
    "status",
    "max_retries",
    "retry_count",
}


@router.post("/", response_model=ReminderOut)
def create(
    payload: ReminderCreate,
    api_key: dict = Depends(require_scope("reminders:write")),
):
    return create_reminder(payload.model_dump(), api_key_id=api_key["id"])


@router.get("/", response_model=ReminderList)
def list_all(
    status: ReminderStatus | None = Query(default=None),
    api_key: dict = Depends(require_scope("reminders:read")),
):
    return {"reminders": list_reminders(status=status)}


@router.get("/{reminder_id}", response_model=ReminderOut)
def get_one(
    reminder_id: int,
    api_key: dict = Depends(require_scope("reminders:read")),
):
    reminder = get_reminder(reminder_id)
    if reminder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder {reminder_id} not found.",
        )
    return reminder


@router.patch("/{reminder_id}", response_model=ReminderOut)
def update(
    reminder_id: int,
    payload: ReminderUpdate,
    api_key: dict = Depends(require_scope("reminders:write")),
):
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="At least one field must be provided.",
        )
    null_fields = [
        field
        for field in NON_NULL_UPDATE_FIELDS
        if field in changes and changes[field] is None
    ]
    if null_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"These fields cannot be null: {', '.join(null_fields)}.",
        )
    reminder = update_reminder(reminder_id, changes)
    if reminder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder {reminder_id} not found.",
        )
    return reminder


@router.delete("/{reminder_id}", response_model=ReminderOut)
def delete(
    reminder_id: int,
    api_key: dict = Depends(require_scope("reminders:write")),
):
    reminder = delete_reminder(reminder_id)
    if reminder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder {reminder_id} not found.",
        )
    return reminder


@router.get("/{reminder_id}/attempts", response_model=NotificationAttemptList)
def attempts(
    reminder_id: int,
    api_key: dict = Depends(require_scope("reminders:read")),
):
    reminder = get_reminder(reminder_id)
    if reminder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder {reminder_id} not found.",
        )
    return {"attempts": list_attempts(reminder_id)}
