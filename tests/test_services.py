from datetime import datetime, timezone
import os
from unittest import TestCase
from unittest.mock import patch

os.environ.setdefault("ADMIN_BOOTSTRAP_TOKEN", "test-admin-token")
os.environ.setdefault("POSTGRES_HOST", "postgres")
os.environ.setdefault("POSTGRES_DB", "remi")
os.environ.setdefault("POSTGRES_USER", "remi_user")
os.environ.setdefault("POSTGRES_PASSWORD", "remi_password")

from app.services import reminders


class FakeCursor:
    def __init__(self, row):
        self.row = row
        self.executed_sql = None
        self.executed_params = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, sql, params=None):
        self.executed_sql = sql
        self.executed_params = params

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self, row):
        self.cursor_obj = FakeCursor(row)
        self.committed = False
        self.closed = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


class ReminderServiceTests(TestCase):
    def test_create_reminder_sends_max_retries_before_api_key_id(self):
        created_at = datetime(2026, 7, 23, 9, 0, tzinfo=timezone.utc)
        row = {
            "id": 1,
            "text": "Call the dentist",
            "remind_at": created_at,
            "category": "health",
            "urgency": "normal",
            "channel": "webhook",
            "delivery_target": None,
            "status": "pending",
            "retry_count": 0,
            "max_retries": 5,
            "last_error": None,
            "created_at": created_at,
        }
        fake_connection = FakeConnection(row)
        enriched = {
            "text": "Call the dentist",
            "remind_at": created_at,
            "category": "health",
            "urgency": "normal",
            "channel": "webhook",
            "delivery_target": None,
            "max_retries": 5,
        }

        with patch(
            "app.services.reminders.get_connection",
            return_value=fake_connection,
        ), patch(
            "app.services.reminders.enrich_reminder",
            return_value=enriched,
        ):
            result = reminders.create_reminder(
                {"text": "Call the dentist"},
                api_key_id=99,
            )

        self.assertEqual(result, row)
        self.assertTrue(fake_connection.committed)
        self.assertTrue(fake_connection.closed)
        self.assertEqual(fake_connection.cursor_obj.executed_params[-2:], (5, 99))
