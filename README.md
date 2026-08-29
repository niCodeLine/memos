# Memo

> A local-first reminder platform for bots, assistants and small automations.

Memo is a backend for the kind of reminders that start in one place and should
arrive somewhere else later: a voice assistant, a bot, a webhook, a tiny script,
or whatever you feel like connecting next.

The project is intentionally practical. It has the parts a real backend needs —
a database, API keys, a worker, retries, delivery attempts and channel adapters —
but it is still small enough to open, read, break, fix and understand.

## The short version

```text
capture a reminder  →  save it  →  wait until it is due  →  dispatch it
```

Memo does not try to be the final reminder app for everyone. The idea is more
useful than that: it gives you a clean base so you can decide how reminders
enter the system and where they should go.

Maybe you want Alexa to save them. Maybe you want Telegram to deliver them.
Maybe you want a local assistant running on a Raspberry Pi. Memo leaves those
doors open.

## Remi & Memo

Memo comes from [Remi](https://github.com/niCodeLine/remi), the smaller base
project.

| Project | Shape | Good for |
| :--- | :--- | :--- |
| [Remi](https://github.com/niCodeLine/remi) | Small reminders API | Learning the API/database logic without much noise |
| Memo | Full reminder platform | Workers, API keys, delivery flow and extensible channels |

```text
Remi saves reminders.
Memo saves them, protects them, watches them, retries them, and dispatches them.
```

Remi also keeps a `basic` branch with only the API and database logic, without
the assistant layer. That branch exists on purpose: sometimes the simple version
is the one you want to study or reuse.

## What is inside

| Piece | Why it exists |
| :--- | :--- |
| FastAPI | The HTTP API for bots, assistants or clients |
| PostgreSQL | The source of truth for reminders, API keys and attempts |
| Worker | Checks due reminders and moves them through the delivery flow |
| API keys | Lets automations use the API without a full user system |
| Channels | Small adapters for webhook, Telegram, email, Alexa or your own sender |
| AI enrichment | A simple place to improve the reminder before saving it |

## How the flow feels

```text
assistant / bot / script
        ↓
      Memo API
        ↓
    PostgreSQL
        ↓
      worker
        ↓
 channel adapter
        ↓
webhook / telegram / email / alexa / custom
```

A reminder can be created by anything that can call the API. Once it is saved,
the worker picks it up when the time comes and sends it through the selected
channel.

## Current features

- Reminder CRUD: create, list, read, update and delete.
- API-key access for bots and assistant-style integrations.
- Admin endpoints to create, list and revoke API keys.
- Reminder states: `pending`, `processing`, `sent`, `failed`, `cancelled`.
- Retry tracking with `retry_count`, `max_retries` and `last_error`.
- Delivery attempt history, useful when something fails.
- Docker Compose setup for API, worker, PostgreSQL and Redis.
- Webhook adapter as the neutral real example.
- Tiny Telegram, email and Alexa adapters as simple extension examples.
- Heuristic enrichment endpoint for urgency, category, channel and time hints.

Redis is included because it is a natural next step for queues, cache or locks.
For this MVP, the worker claims jobs directly in PostgreSQL to keep the first
version easier to reason about.

## Reminder states

| State | Meaning |
| :--- | :--- |
| `pending` | Waiting for its moment |
| `processing` | Claimed by the worker |
| `sent` | Delivered successfully |
| `failed` | Exhausted its retries |
| `cancelled` | Stopped on purpose |

Failed reminders are not hidden. You can inspect them, see their attempts, and
move them back into the flow later if you decide to add that kind of recovery.

## Quick start

Create your local environment file:

```bash
cp .env.example .env
```

Start the stack:

```bash
docker compose up --build
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

## First useful call

Create an API key with the local admin token:

```bash
curl -X POST "http://127.0.0.1:8000/admin/api-keys" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: change-me-local-admin-token" \
  -d '{"name": "local-bot", "scopes": ["reminders:write", "reminders:read"]}'
```

Use the returned token as `X-API-Key`.

Create a reminder:

```bash
curl -X POST "http://127.0.0.1:8000/reminders/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: paste-token-here" \
  -d '{
    "text": "Call the dentist",
    "remind_at": "2026-07-24T09:00:00+02:00",
    "category": "health",
    "channel": "webhook"
  }'
```

List reminders:

```bash
curl "http://127.0.0.1:8000/reminders/" \
  -H "X-API-Key: paste-token-here"
```

See delivery attempts:

```bash
curl "http://127.0.0.1:8000/reminders/1/attempts" \
  -H "X-API-Key: paste-token-here"
```

## API map

### Admin

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `POST` | `/admin/api-keys` | Create an API key |
| `GET` | `/admin/api-keys` | List API keys |
| `PATCH` | `/admin/api-keys/{id}/revoke` | Revoke an API key |

### Reminders

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `POST` | `/reminders/` | Create a reminder |
| `GET` | `/reminders/` | List reminders |
| `GET` | `/reminders/{id}` | Get one reminder |
| `PATCH` | `/reminders/{id}` | Update a reminder |
| `DELETE` | `/reminders/{id}` | Delete a reminder |
| `GET` | `/reminders/{id}/attempts` | See delivery attempts |

### Enrichment

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `POST` | `/ai/enrich-reminder` | Suggest fields before saving a reminder |

## AI enrichment

The enrichment endpoint is deliberately modest. It does not create the reminder;
it only suggests fields that can make the save step nicer.

```bash
curl -X POST "http://127.0.0.1:8000/ai/enrich-reminder" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: paste-token-here" \
  -d '{"text": "urgente llamar al dentista"}'
```

Example response:

```json
{
  "text": "urgente llamar al dentista",
  "category": "health",
  "urgency": "high",
  "channel": "telegram",
  "delivery_target": null,
  "max_retries": 3
}
```

Today this is heuristic. Tomorrow it could be a real model extracting dates,
tone, urgency, category or preferred delivery channel from natural language.
The seam is already there.

## Channels

Channels are intentionally tiny.

- `webhook.py` is the clean working example. If `delivery_target` is a URL, the
  worker sends the reminder payload there.
- `telegram.py`, `email.py` and `alexa.py` are small placeholders. They keep the
  shape of a real adapter without forcing credentials, OAuth or platform setup.

That is the design choice: Memo owns the reminder flow; you own the delivery
personality.

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
  test_routes.py
  test_security.py
  test_services.py
```

## Tests

```bash
python -m unittest discover -v
```

## Possible next steps

- Signed webhooks.
- A real Telegram adapter.
- Per-user profiles and timezone preferences.
- Redis-backed queue or distributed worker lock.
- Real natural-language extraction with an AI model.
- Assistant integration through tool calls.

## Why I like this shape

A lot of assistant projects become demos that look magical for five minutes and
then become hard to extend. Memo goes the other way: the magic is optional, and
the backend stays understandable.

That makes it a good base for experimenting without losing the thread.
