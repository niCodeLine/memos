"""Shared types and helpers for delivery channel adapters."""

from dataclasses import dataclass


@dataclass
class DeliveryResult:
    """Standard result returned by every channel adapter."""

    success: bool
    error: str | None = None


def reminder_payload(reminder: dict) -> dict:
    """Build the small payload sent to external notification channels."""

    return {
        "id": reminder["id"],
        "text": reminder["text"],
        "remind_at": reminder["remind_at"].isoformat(),
        "category": reminder.get("category"),
        "urgency": reminder["urgency"],
        "channel": reminder["channel"],
    }
