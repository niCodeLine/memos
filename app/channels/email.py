"""Tiny email adapter placeholder.

Replace this function with SMTP, an email provider, or any local mailer.
`delivery_target` can be an email address.
"""

from app.channels.base import DeliveryResult, reminder_payload


def send(reminder: dict) -> DeliveryResult:
    """Demo email sender. Replace this body with real platform code.

    `delivery_target` can be an email address.
    """

    payload = reminder_payload(reminder)
    recipient = reminder.get("delivery_target") or "demo@example.local"

    print(
        "[email:demo] no real email was sent; "
        f"to={recipient} payload={payload}"
    )
    return DeliveryResult(True)
