# Next project: personal reminder platform

This repository is intentionally small. It is the base layer: storing and
retrieving reminders through an API, with PostgreSQL as the source of truth and
Redis as an optional cache.

The next repository can use this base to build a more complete personal reminder
platform.

## Proposed direction

- Docker installation for the full system.
- Background workers that check due reminders and send notifications.
- Users and profiles, with one local admin.
- API keys for bots, assistants and integrations.
- Pluggable delivery channels:
  - Telegram
  - email
  - webhooks
  - Alexa or other voice assistants
- AI-assisted reminder enrichment:
  - urgency classification
  - suggested delivery channel
  - suggested reminder time
  - normalization of vague natural-language dates
  - fallback suggestions when a reminder is incomplete

## Suggested data-model evolution

The current reminder model is deliberately minimal:

- day
- month
- text

For the larger project, the model should probably evolve toward:

- `remind_at`: full date and time
- `timezone`: configured globally or per user
- `category`: health, work, family, errands, personal, etc.
- `urgency`: low, normal, high
- `status`: pending, sent, cancelled
- `delivery_channel`: telegram, email, webhook, alexa, etc.
- `sent_at`
- `last_error`
- `retry_count`

That larger model is intentionally not implemented here, because this repository
is meant to stay clean as a learning and portfolio base.

