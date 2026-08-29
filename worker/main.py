import time

from app.channels.dispatcher import send_reminder
from app.core.config import settings
from app.db.schema import ensure_schema
from app.services.reminders import (
    get_due_reminders,
    mark_delivery_failed,
    mark_sent,
    record_attempt,
)


def run_once() -> int:
    reminders = get_due_reminders()
    for reminder in reminders:
        result = send_reminder(reminder)
        record_attempt(
            reminder_id=reminder["id"],
            channel=reminder["channel"],
            success=result.success,
            error=result.error,
        )
        if result.success:
            mark_sent(reminder["id"])
        else:
            mark_delivery_failed(
                reminder["id"],
                result.error or "Unknown delivery error.",
            )
    return len(reminders)


def main() -> None:
    ensure_schema()
    while True:
        processed = run_once()
        if processed:
            print(f"Processed {processed} due reminder(s).")
        time.sleep(settings.WORKER_POLL_SECONDS)


if __name__ == "__main__":
    main()
