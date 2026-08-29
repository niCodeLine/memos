"""Tiny Telegram adapter placeholder.

Replace this function with your own Telegram bot implementation. For example,
`delivery_target` could be a Telegram chat id.
"""

from app.channels.base import DeliveryResult, reminder_payload


def send(reminder: dict) -> DeliveryResult:
    payload = reminder_payload(reminder)
    chat_id = reminder.get("delivery_target") or "demo-chat"

    print(
        "[telegram:demo] no real Telegram message was sent; "
        f"chat={chat_id} payload={payload}"
    )
    return DeliveryResult(True)
