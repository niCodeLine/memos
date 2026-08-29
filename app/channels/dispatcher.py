from app.channels import alexa, email, telegram, webhook
from app.channels.base import DeliveryResult


def send_reminder(reminder: dict) -> DeliveryResult:
    channel = reminder.get("channel", "webhook")

    if channel == "telegram":
        return telegram.send(reminder)
    if channel == "email":
        return email.send(reminder)
    if channel == "webhook":
        return webhook.send(reminder)
    if channel == "alexa":
        return alexa.send(reminder)

    return DeliveryResult(False, f"Unsupported channel: {channel}")
