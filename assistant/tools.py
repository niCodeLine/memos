"""Assistant-compatible tools for reminder operations."""

import datetime

import api.log as log
import api.services_db as services_db

logger = log.ger(__name__, "DEBUG", file_name="api")


def _response(response, collection: bool = False) -> dict:
    key = "reminders" if collection else "reminder"
    return {
        "message": response.message,
        key: getattr(response, key),
    }


def date_now():
    """
    Get the current date and weekday number.

    Weekday uses Python's convention: 0=Monday, 6=Sunday.
    """
    now = datetime.datetime.now()
    week_day = now.weekday()

    return {"now": now, "week_day_num": week_day}


async def create_reminder(text: str, day: int, month: int):
    """Create a reminder from an assistant/tool call."""
    try:
        return _response(services_db.create(day=day, month=month, text=text))
    except Exception as exc:
        logger.warning("Assistant create operation failed: %s", exc)
        return {"message": str(exc), "reminder": None}


async def get_reminder_by_id(reminder_id: int):
    """Get one reminder from an assistant/tool call."""
    try:
        return _response(services_db.get_by_id(reminder_id))
    except Exception as exc:
        logger.warning("Assistant get operation failed: %s", exc)
        return {"message": str(exc), "reminder": None}


async def get_reminders(
    day: int | None = None,
    month: int | None = None,
    text: str | None = None,
):
    """List reminders from an assistant/tool call."""
    try:
        return _response(
            services_db.get(day=day, month=month, text=text),
            collection=True,
        )
    except Exception as exc:
        logger.warning("Assistant list operation failed: %s", exc)
        return {"message": str(exc), "reminders": []}


async def delete_reminder(reminder_id: int):
    """Delete a reminder from an assistant/tool call."""
    try:
        return _response(services_db.delete(reminder_id))
    except Exception as exc:
        logger.warning("Assistant delete operation failed: %s", exc)
        return {"message": str(exc), "reminder": None}
