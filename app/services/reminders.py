"""Reminder service layer.

Routes call these functions instead of writing SQL directly. This keeps HTTP
concerns, database concerns and worker concerns separated enough to follow.
"""

from app.ai.enrichment import enrich_reminder
from app.db.connection import get_connection

# Shared column list used by reads and mutations that return a reminder.
REMINDER_COLUMNS = """
    id, text, remind_at, category, urgency, channel, delivery_target,
    status, retry_count, max_retries, last_error, created_at
"""


def create_reminder(data: dict, *, api_key_id: int | None = None) -> dict:
    """Enrich and save a new reminder.

    `api_key_id` is optional so tests or trusted local scripts can call the
    service directly, while normal API requests still keep an audit link to the
    key that created the reminder.
    """

    enriched = enrich_reminder(data)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO reminders (
                    text, remind_at, category, urgency, channel,
                    delivery_target, max_retries,
                    created_by_api_key_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING
                    id, text, remind_at, category, urgency, channel,
                    delivery_target, status, retry_count, max_retries,
                    last_error, created_at
                """,
                (
                    enriched["text"],
                    enriched["remind_at"],
                    enriched.get("category"),
                    enriched["urgency"],
                    enriched["channel"],
                    enriched.get("delivery_target"),
                    enriched["max_retries"],
                    api_key_id,
                ),
            )
            row = cursor.fetchone()
        conn.commit()
    finally:
        conn.close()
    return row


def get_reminder(reminder_id: int) -> dict | None:
    """Fetch one reminder by id, or return `None` when it does not exist."""

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT {REMINDER_COLUMNS}
                FROM reminders
                WHERE id = %s
                """,
                (reminder_id,),
            )
            return cursor.fetchone()
    finally:
        conn.close()


def list_reminders(status: str | None = None) -> list[dict]:
    """List reminders, optionally filtered by state."""

    conn = get_connection()
    try:
        query = """
            SELECT
                id, text, remind_at, category, urgency, channel,
                delivery_target, status, retry_count, max_retries,
                last_error, created_at
            FROM reminders
            WHERE 1=1
        """
        params = []
        if status:
            query += " AND status = %s"
            params.append(status)
        query += " ORDER BY remind_at ASC, id ASC"
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
    finally:
        conn.close()


def update_reminder(reminder_id: int, changes: dict) -> dict | None:
    """Apply a partial update and return the updated reminder.

    The route validates public input first. This function still keeps an
    allowlist so only known database columns can be modified dynamically.
    """

    allowed_fields = {
        "text",
        "remind_at",
        "category",
        "urgency",
        "channel",
        "delivery_target",
        "status",
        "max_retries",
        "retry_count",
    }
    filtered = {
        field: value
        for field, value in changes.items()
        if field in allowed_fields
    }
    if not filtered:
        return get_reminder(reminder_id)

    assignments = ", ".join(f"{field} = %s" for field in filtered)
    values = list(filtered.values())
    values.append(reminder_id)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE reminders
                SET {assignments}, updated_at = NOW()
                WHERE id = %s
                RETURNING {REMINDER_COLUMNS}
                """,
                tuple(values),
            )
            row = cursor.fetchone()
        conn.commit()
    finally:
        conn.close()
    return row


def delete_reminder(reminder_id: int) -> dict | None:
    """Delete one reminder and return what was deleted."""

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                DELETE FROM reminders
                WHERE id = %s
                RETURNING {REMINDER_COLUMNS}
                """,
                (reminder_id,),
            )
            row = cursor.fetchone()
        conn.commit()
    finally:
        conn.close()
    return row


def get_due_reminders(limit: int = 25) -> list[dict]:
    """Claim reminders that are ready for the worker to deliver.

    The `FOR UPDATE SKIP LOCKED` query lets more than one worker run without
    sending the same reminder twice. A reminder is moved to `processing` before
    leaving this function, so the worker owns it until it marks success/failure.
    """

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # If a worker dies mid-delivery, processing rows should not stay
            # stuck forever. Five minutes is a simple MVP recovery window.
            cursor.execute(
                """
                UPDATE reminders
                SET status = 'pending',
                    last_error = 'Recovered stale processing reminder.',
                    updated_at = NOW()
                WHERE status = 'processing'
                  AND updated_at < NOW() - INTERVAL '5 minutes'
                """
            )
            cursor.execute(
                """
                WITH due AS (
                    SELECT id
                    FROM reminders
                    WHERE status = 'pending'
                      AND remind_at <= NOW()
                      AND (next_attempt_at IS NULL OR next_attempt_at <= NOW())
                    ORDER BY remind_at ASC, id ASC
                    LIMIT %s
                    FOR UPDATE SKIP LOCKED
                )
                UPDATE reminders
                SET status = 'processing', updated_at = NOW()
                WHERE id IN (SELECT id FROM due)
                RETURNING
                    id, text, remind_at, category, urgency, channel,
                    delivery_target, status, retry_count, max_retries,
                    last_error, created_at
                """,
                (limit,),
            )
            rows = cursor.fetchall()
        conn.commit()
        return rows
    finally:
        conn.close()


def mark_sent(reminder_id: int) -> None:
    """Mark a reminder as successfully delivered."""

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE reminders
                SET status = 'sent',
                    sent_at = NOW(),
                    last_error = NULL,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (reminder_id,),
            )
        conn.commit()
    finally:
        conn.close()


def mark_delivery_failed(reminder_id: int, error: str) -> None:
    """Record a failed delivery and either retry later or mark as failed."""

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE reminders
                SET retry_count = retry_count + 1,
                    last_error = %s,
                    next_attempt_at = NOW() + INTERVAL '1 minute',
                    status = CASE
                        WHEN retry_count + 1 >= max_retries THEN 'failed'
                        ELSE 'pending'
                    END,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (error, reminder_id),
            )
        conn.commit()
    finally:
        conn.close()


def record_attempt(
    *, reminder_id: int, channel: str, success: bool, error: str | None = None
) -> None:
    """Store one worker delivery attempt for debugging and audit history."""

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO notification_attempts (
                    reminder_id, channel, success, error
                )
                VALUES (%s, %s, %s, %s)
                """,
                (reminder_id, channel, success, error),
            )
        conn.commit()
    finally:
        conn.close()


def list_attempts(reminder_id: int) -> list[dict]:
    """Return delivery attempts for a reminder, newest first."""

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, reminder_id, channel, success, error, created_at
                FROM notification_attempts
                WHERE reminder_id = %s
                ORDER BY created_at DESC, id DESC
                """,
                (reminder_id,),
            )
            return cursor.fetchall()
    finally:
        conn.close()
