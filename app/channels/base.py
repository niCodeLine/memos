from dataclasses import dataclass


@dataclass
class DeliveryResult:
    success: bool
    error: str | None = None


def reminder_payload(reminder: dict) -> dict:
    """Return the small payload channel adapters can deliver."""
    return {
        "id": reminder["id"],
        "text": reminder["text"],
        "remind_at": reminder["remind_at"].isoformat(),
        "category": reminder.get("category"),
        "urgency": reminder["urgency"],
        "channel": reminder["channel"],
    }
