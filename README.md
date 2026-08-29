# Memo

Self-hosted reminder platform for assistants, bots and local automations.
FastAPI, PostgreSQL, Redis, workers and pluggable delivery channels.

Memo builds on the smaller Remi API base. Remi stores reminders; Memo adds the
pieces needed to make reminders move: API keys, background workers, notification
attempts and channel adapters.

## Features

- FastAPI backend for reminders.
- PostgreSQL as the source of truth.
- Redis included for future cache, queues or distributed locks.
- Docker Compose installation for API, worker, PostgreSQL and Redis.
- Admin bootstrap token for local setup.
- API keys for bots and integrations.
- Reminder model with `remind_at`, category, urgency, channel, delivery target
  and status.
- CRUD operations for reminders.
- Worker that polls due reminders and dispatches notifications.
- Worker retries with `retry_count`, `max_retries` and `last_error`.
- Channel adapter structure with small examples for webhook, Telegram, email
  and Alexa.
- AI-ready enrichment endpoint for urgency, category, channel and time
  suggestions.

## Reminder states

Memo uses a small state machine:

- `pending` — saved and waiting.
- `processing` — claimed by the worker.
- `sent` — delivered successfully.
- `failed` — delivery failed after all retries.
- `cancelled` — intentionally stopped.

The worker retries failed delivery attempts up to `max_retries`. Failed
reminders can be listed and manually moved back to `pending` if needed.

## Quick Start

Create a local environment file:

```bash
cp .env.example .env
```

Start the full local stack:

```bash
docker compose up --build
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

## API keys

Create an API key using the admin bootstrap token from `.env`:

```bash
curl -X POST "http://127.0.0.1:8000/admin/api-keys" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: change-me-local-admin-token" \
  -d '{"name": "local-bot", "scopes": ["reminders:write", "reminders:read"]}'
```

Use the returned token as `X-API-Key`.

List API keys:

```bash
curl "http://127.0.0.1:8000/admin/api-keys" \
  -H "X-Admin-Token: change-me-local-admin-token"
```

Revoke an API key:

```bash
curl -X PATCH "http://127.0.0.1:8000/admin/api-keys/1/revoke" \
  -H "X-Admin-Token: change-me-local-admin-token"
```

## AI enrichment

The enrichment endpoint does not create a reminder. It suggests fields that can
be used before saving one.

```bash
curl -X POST "http://127.0.0.1:8000/ai/enrich-reminder" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: paste-token-here" \
  -d '{"text": "urgente llamar al dentista"}'
```

## Reminder examples

Create a reminder:

```bash
curl -X POST "http://127.0.0.1:8000/reminders/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: paste-token-here" \
  -d '{
    "text": "Call the dentist",
    "remind_at": "2026-07-24T09:00:00+02:00",
    "category": "health",
    "channel": "webhook",
    "delivery_target": "https://example.com/my-reminder-webhook"
  }'
```

List reminders:

```bash
curl "http://127.0.0.1:8000/reminders/" \
  -H "X-API-Key: paste-token-here"
```

Get one reminder:

```bash
curl "http://127.0.0.1:8000/reminders/1" \
  -H "X-API-Key: paste-token-here"
```

Update a reminder:

```bash
curl -X PATCH "http://127.0.0.1:8000/reminders/1" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: paste-token-here" \
  -d '{"status": "cancelled"}'
```

Delete a reminder:

```bash
curl -X DELETE "http://127.0.0.1:8000/reminders/1" \
  -H "X-API-Key: paste-token-here"
```

View worker delivery attempts:

```bash
curl "http://127.0.0.1:8000/reminders/1/attempts" \
  -H "X-API-Key: paste-token-here"
```

List failed reminders:

```bash
curl "http://127.0.0.1:8000/reminders/?status=failed" \
  -H "X-API-Key: paste-token-here"
```

## Channels

The channel adapters are intentionally small.

- `webhook.py` is the neutral example. If a `delivery_target` URL is provided,
  the worker sends the reminder payload there.
- `telegram.py`, `email.py` and `alexa.py` are tiny placeholders. They print a
  demo message and return success so the local worker flow can be tested, but
  they do not contact those services until someone replaces the demo function.

## Architecture

```text
assistant / bot / client
        ↓
FastAPI API
        ↓
PostgreSQL
        ↓
worker
        ↓
channel adapter
        ↓
Telegram / email / webhook / Alexa / etc.
```

Redis is included in the Docker stack and ready for cache, queues or distributed
locks. The current MVP uses PostgreSQL for worker claiming because it keeps the
first complete version easier to run and understand.

## Project structure

```text
app/
  main.py              FastAPI app
  core/                settings and security
  db/                  PostgreSQL connection and schema setup
  routers/             HTTP endpoints
  services/            domain logic
  channels/            delivery adapters
  ai/                  enrichment hooks

worker/
  main.py              background reminder worker

tests/
  test_channels.py
  test_enrichment.py
  test_security.py
```

## Tests

```bash
python -m unittest discover -v
```

## Current status

This is the first complete MVP shape for Memo. It is intentionally friendly to
modify: the API, worker and database are ready, while the delivery channels are
small examples meant to be replaced or extended.

## Roadmap

- Webhook signing.
- Stronger examples for custom channel adapters.
- User profiles and per-user timezone.
- Redis-backed locks or queues if the worker grows.
- Real AI extraction and enrichment from natural language.
- Assistant integration using tool calls.
