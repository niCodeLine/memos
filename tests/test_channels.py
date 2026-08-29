from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

from app.channels import alexa, email, telegram, webhook
from app.channels.dispatcher import send_reminder


def reminder(channel="webhook", delivery_target=None):
    return {
        "id": 1,
        "text": "Call the dentist",
        "remind_at": datetime(2026, 7, 24, 9, 0, tzinfo=timezone.utc),
        "category": "health",
        "urgency": "normal",
        "channel": channel,
        "delivery_target": delivery_target,
    }


class ChannelTests(TestCase):
    def test_dispatches_to_webhook(self):
        result = send_reminder(reminder(channel="webhook"))

        self.assertTrue(result.success)

    def test_rejects_unknown_channel(self):
        result = send_reminder(reminder(channel="sms"))

        self.assertFalse(result.success)
        self.assertIn("Unsupported channel", result.error)

    @patch("app.channels.webhook.httpx.post")
    def test_webhook_posts_to_delivery_target(self, post):
        post.return_value.raise_for_status.return_value = None

        result = webhook.send(
            reminder(
                channel="webhook",
                delivery_target="https://example.com/hook",
            )
        )

        self.assertTrue(result.success)
        post.assert_called_once()

    def test_demo_placeholders_succeed(self):
        self.assertTrue(telegram.send(reminder(channel="telegram")).success)
        self.assertTrue(email.send(reminder(channel="email")).success)
        self.assertTrue(alexa.send(reminder(channel="alexa")).success)
