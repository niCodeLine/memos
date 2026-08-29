from app.ai.enrichment import enrich_reminder
from app.db.connection import get_connection

REMINDER_COLUMNS = """
    id, text, remind_at, category, urgency, channel, delivery_target,
    status, retry_count, max_retries, last_error, created_at
"""


def create_reminder(data: dict, *, api_key_id: int | None = None) -> dict:
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
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
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
