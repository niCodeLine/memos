"""Heuristic reminder enrichment.

This file is the future AI seam. Today it uses simple word rules so the project
works without paid APIs, keys, latency or external dependencies. A real model can
replace these functions later without changing the rest of the app.
"""

from datetime import datetime, timedelta, timezone

URGENT_WORDS = {"urgent", "urgente", "asap", "important", "importante"}
HEALTH_WORDS = {"doctor", "dentist", "dentista", "medico", "médico", "salud"}
WORK_WORDS = {"meeting", "reunion", "reunión", "deadline", "trabajo"}


def classify_urgency(text: str) -> str:
    """Guess whether the reminder sounds urgent."""

    lowered = text.lower()
    if any(word in lowered for word in URGENT_WORDS):
        return "high"
    return "normal"


def suggest_category(text: str) -> str | None:
    """Suggest a broad category from a few readable keyword groups."""

    lowered = text.lower()
    if any(word in lowered for word in HEALTH_WORDS):
        return "health"
    if any(word in lowered for word in WORK_WORDS):
        return "work"
    return None


def suggest_channel(category: str | None, urgency: str) -> str:
    """Pick a default delivery channel from category and urgency.

    Urgent reminders go to Telegram in this demo because chat notifications are a
    natural fit. Work and unknown reminders default to webhook because it is the
    most neutral integration point.
    """

    if urgency == "high":
        return "telegram"
    if category == "work":
        return "webhook"
    return "webhook"


def suggest_remind_at() -> datetime:
    """Provide a safe default time when the client did not send one."""

    return datetime.now(timezone.utc) + timedelta(hours=1)


def enrich_reminder(data: dict) -> dict:
    """Return reminder data with missing fields filled by simple suggestions.

    This function does not save anything. It only prepares a complete reminder
    shape for the service layer or for the `/ai/enrich-reminder` endpoint.
    """

    enriched = dict(data)
    text = enriched["text"]

    urgency = enriched.get("urgency") or classify_urgency(text)
    category = enriched.get("category") or suggest_category(text)
    channel = enriched.get("channel") or suggest_channel(category, urgency)
    remind_at = enriched.get("remind_at") or suggest_remind_at()
    max_retries = enriched.get("max_retries", 3)

    enriched.update(
        urgency=urgency,
        category=category,
        channel=channel,
        delivery_target=enriched.get("delivery_target"),
        remind_at=remind_at,
        max_retries=max_retries,
    )
    return enriched
