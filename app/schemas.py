"""Pydantic models that define Memo's public API shapes."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ReminderStatus = Literal["pending", "processing", "sent", "failed", "cancelled"]


class ApiKeyCreate(BaseModel):
    """Request body for creating a bot/integration API key."""

    name: str = Field(min_length=1, max_length=80)
    scopes: list[str] = Field(default_factory=list)


class ApiKeyCreated(BaseModel):
    """Response returned only once after creating an API key."""

    id: int
    name: str
    token: str
    scopes: list[str]


class ReminderCreate(BaseModel):
    """Fields accepted when creating or enriching a reminder."""

    text: str = Field(min_length=1, max_length=300)
    remind_at: datetime | None = None
    category: str | None = Field(default=None, max_length=50)
    urgency: str | None = Field(default=None, max_length=20)
    channel: str | None = Field(default=None, max_length=40)
    delivery_target: str | None = Field(default=None, max_length=500)
    max_retries: int = Field(default=3, ge=0, le=10)


class ReminderUpdate(BaseModel):
    """Patch body where every field is optional but still validated."""

    text: str | None = Field(default=None, min_length=1, max_length=300)
    remind_at: datetime | None = None
    category: str | None = Field(default=None, max_length=50)
    urgency: str | None = Field(default=None, max_length=20)
    channel: str | None = Field(default=None, max_length=40)
    delivery_target: str | None = Field(default=None, max_length=500)
    status: ReminderStatus | None = None
    max_retries: int | None = Field(default=None, ge=0, le=10)
    retry_count: int | None = Field(default=None, ge=0, le=10)


class ReminderOut(BaseModel):
    """Reminder shape returned by the API."""

    id: int
    text: str
    remind_at: datetime
    category: str | None
    urgency: str
    channel: str
    delivery_target: str | None
    status: ReminderStatus
    retry_count: int
    max_retries: int
    last_error: str | None
    created_at: datetime


class ReminderList(BaseModel):
    """Wrapper used by list endpoints to keep responses extensible."""

    reminders: list[ReminderOut]


class ReminderEnrichment(BaseModel):
    """Suggested reminder fields returned by the enrichment endpoint."""

    text: str
    remind_at: datetime
    category: str | None
    urgency: str
    channel: str
    delivery_target: str | None
    max_retries: int


class NotificationAttemptOut(BaseModel):
    """One attempt made by the worker to deliver a reminder."""

    id: int
    reminder_id: int
    channel: str
    success: bool
    error: str | None
    created_at: datetime


class NotificationAttemptList(BaseModel):
    """Wrapper for a reminder's delivery history."""

    attempts: list[NotificationAttemptOut]


class ApiKeyOut(BaseModel):
    """Safe API-key listing response that never includes secrets."""

    id: int
    name: str
    scopes: list[str]
    revoked_at: datetime | None
    last_used_at: datetime | None
    created_at: datetime
