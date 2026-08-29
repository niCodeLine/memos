from datetime import datetime, timezone
import os
from unittest import TestCase
from unittest.mock import patch

os.environ.setdefault("ADMIN_BOOTSTRAP_TOKEN", "test-admin-token")
os.environ.setdefault("POSTGRES_HOST", "postgres")
os.environ.setdefault("POSTGRES_DB", "remi")
os.environ.setdefault("POSTGRES_USER", "remi_user")
os.environ.setdefault("POSTGRES_PASSWORD", "remi_password")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def reminder_payload(reminder_id=1):
    return {
        "id": reminder_id,
        "text": "Call the dentist",
        "remind_at": datetime(2026, 7, 24, 9, 0, tzinfo=timezone.utc),
        "category": "health",
        "urgency": "normal",
        "channel": "webhook",
        "delivery_target": None,
        "status": "pending",
        "retry_count": 0,
        "max_retries": 3,
        "last_error": None,
        "created_at": datetime(2026, 7, 23, 9, 0, tzinfo=timezone.utc),
    }


def api_key():
    return {"id": 1, "name": "test-key", "scopes": ["*"]}


class ReminderRouteTests(TestCase):
    @patch("app.dependencies.find_active_key", return_value=api_key())
    def test_invalid_status_filter_returns_422(self, _):
        response = client.get(
            "/reminders/?status=banana",
            headers={"X-API-Key": "test-token"},
        )

        self.assertEqual(response.status_code, 422)

    @patch("app.dependencies.find_active_key", return_value=api_key())
    def test_empty_patch_returns_422(self, _):
        response = client.patch(
            "/reminders/1",
            headers={"X-API-Key": "test-token"},
            json={},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json()["detail"],
            "At least one field must be provided.",
        )

    @patch("app.dependencies.find_active_key", return_value=api_key())
    def test_null_required_update_field_returns_422(self, _):
        response = client.patch(
            "/reminders/1",
            headers={"X-API-Key": "test-token"},
            json={"text": None},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("text", response.json()["detail"])

    @patch("app.routers.reminders.get_reminder", return_value=None)
    @patch("app.dependencies.find_active_key", return_value=api_key())
    def test_attempts_for_missing_reminder_returns_404(self, _, __):
        response = client.get(
            "/reminders/99/attempts",
            headers={"X-API-Key": "test-token"},
        )

        self.assertEqual(response.status_code, 404)

    @patch("app.routers.reminders.list_attempts", return_value=[])
    @patch("app.routers.reminders.get_reminder", return_value=reminder_payload())
    @patch("app.dependencies.find_active_key", return_value=api_key())
    def test_attempts_for_existing_reminder_returns_list(self, _, __, ___):
        response = client.get(
            "/reminders/1/attempts",
            headers={"X-API-Key": "test-token"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"attempts": []})
