"""Tiny Alexa adapter placeholder.

Alexa integrations usually need a skill, routine, webhook bridge, or vendor
setup. This function marks the extension point without choosing one path.
"""

from app.channels.base import DeliveryResult, reminder_payload


def send(reminder: dict) -> DeliveryResult:
    payload = reminder_payload(reminder)
    target = reminder.get("delivery_target") or "demo-alexa-target"

    print(
        "[alexa:demo] no real Alexa action was triggered; "
        f"target={target} payload={payload}"
    )
    return DeliveryResult(True)
