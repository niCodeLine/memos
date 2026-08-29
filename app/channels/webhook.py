"""Webhook delivery example.

This is the most neutral adapter: the worker sends the reminder payload to a
URL, and the receiving service decides what to do with it.
"""

import httpx

from app.channels.base import DeliveryResult, reminder_payload


def send(reminder: dict) -> DeliveryResult:
    target_url = reminder.get("delivery_target")
    payload = reminder_payload(reminder)

    if not target_url:
        print(f"[webhook:demo] {payload}")
        return DeliveryResult(True)

    try:
        response = httpx.post(target_url, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as exc:
        return DeliveryResult(False, str(exc))

    return DeliveryResult(True)
