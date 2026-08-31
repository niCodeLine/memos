from datetime import datetime, timezone
import os
from unittest import TestCase
from unittest.mock import patch

os.environ.setdefault("ADMIN_BOOTSTRAP_TOKEN", "test-admin-token")
os.environ.setdefault("POSTGRES_HOST", "postgres")
os.environ.setdefault("POSTGRES_DB", "remi")
os.environ.setdefault("POSTGRES_USER", "remi_user")
os.environ.setdefault("POSTGRES_PASSWORD", "remi_password")

from app.channels.base import DeliveryResult
from worker.main import run_once


def due_reminder(channel="webhook"):
    return {
        "id": 1,
        "text": "Call the dentist",
        "remind_at": datetime(2026, 7, 24, 9, 0, tzinfo=timezone.utc),
        "category": "health",
        "urgency": "normal",
        "channel": channel,
        "delivery_target": None,
        "status": "processing",
        "retry_count": 0,
        "max_retries": 3,
        "last_error": None,
        "created_at": datetime(2026, 7, 23, 9, 0, tzinfo=timezone.utc),
    }


class WorkerTests(TestCase):
    def test_run_once_marks_successful_reminder_as_sent(self):
        reminder = due_reminder()

        with patch("worker.main.get_due_reminders", return_value=[reminder]),              patch("worker.main.send_reminder", return_value=DeliveryResult(True)) as send,              patch("worker.main.record_attempt") as record_attempt,              patch("worker.main.mark_sent") as mark_sent,              patch("worker.main.mark_delivery_failed") as mark_failed:
            processed = run_once()

        self.assertEqual(processed, 1)
        send.assert_called_once_with(reminder)
        record_attempt.assert_called_once_with(
            reminder_id=1,
            channel="webhook",
            success=True,
            error=None,
        )
        mark_sent.assert_called_once_with(1)
        mark_failed.assert_not_called()

    def test_run_once_records_failure_and_schedules_retry(self):
        reminder = due_reminder(channel="telegram")

        with patch("worker.main.get_due_reminders", return_value=[reminder]),              patch("worker.main.send_reminder", return_value=DeliveryResult(False, "boom")),              patch("worker.main.record_attempt") as record_attempt,              patch("worker.main.mark_sent") as mark_sent,              patch("worker.main.mark_delivery_failed") as mark_failed:
            processed = run_once()

        self.assertEqual(processed, 1)
        record_attempt.assert_called_once_with(
            reminder_id=1,
            channel="telegram",
            success=False,
            error="boom",
        )
        mark_sent.assert_not_called()
        mark_failed.assert_called_once_with(1, "boom")

    def test_run_once_does_nothing_when_there_are_no_due_reminders(self):
        with patch("worker.main.get_due_reminders", return_value=[]),              patch("worker.main.send_reminder") as send,              patch("worker.main.record_attempt") as record_attempt:
            processed = run_once()

        self.assertEqual(processed, 0)
        send.assert_not_called()
        record_attempt.assert_not_called()
