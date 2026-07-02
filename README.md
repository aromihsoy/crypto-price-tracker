# Crypto Price Tracker

A backend service for real-time cryptocurrency price alerts. Users subscribe to trading pairs and set price conditions; the service polls Binance in the background and pushes a notification over WebSocket the moment a condition is met.

## Features

- **JWT authentication** — user registration and token-based auth; every alert operation is scoped to the authenticated user.
- **Alerts CRUD** — create, read, update and delete your own alerts. Access is owner-scoped: a user can only ever see or modify their own alerts.
- **Background Binance monitoring** — a scheduled task regularly fetches prices for all symbols that have active alerts.
- **Trigger deduplication (cooldown)** — a fired alert will not notify again during its cooldown period, so the user isn't spammed while the price stays past the threshold.
- **Real-time delivery via WebSocket** — when an alert fires, the server pushes a notification to that specific user in real time.

## Tech stack

Python, FastAPI, SQLAlchemy (async), PostgreSQL, Redis, Celery, Docker, pytest.

## Architecture

The system is split across two processes (web and worker) that communicate through Redis. Redis plays two distinct roles: a **task broker** (Beat → Worker) and a **pub/sub channel** (Worker → Web).

```
Beat        → enqueues the polling task into Redis (broker)
Worker      → picks up the task
            → fetches prices from Binance
            → caches prices in Redis
            → evaluates alerts (price vs threshold + cooldown)
            → on trigger, publishes to Redis pub/sub (channel: alerts:{user_id})
Web process → subscribed to the user's channel → receives from pub/sub → sends over WebSocket
WebSocket   → delivers the notification to the user
Binance     → external price source
```

The worker and the web process run in **separate processes with separate memory**, so the worker cannot write to a user's WebSocket connection directly. Redis pub/sub is the bridge: the worker publishes to a per-user channel (`alerts:{user_id}`), and the web process — which owns the socket — forwards the message to the client.

## Requirements

- Docker and Docker Compose

## Getting started

1. **Clone the repository**
   ```bash
   git clone https://github.com/aromihsoy/crypto-price-tracker
   cd crypto-price-tracker
   ```

2. **Create your `.env`** from the example and fill in the values:
   ```bash
   cp .env.example .env
   ```
   At minimum set a real `SECRET_KEY`. Generate one with:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Start the containers** (detached, so the terminal is free for the next step):
   ```bash
   docker compose up --build -d
   ```

4. **Apply migrations** inside the running web container:
   ```bash
   docker compose exec web alembic upgrade head
   ```

5. **Open the API docs** (Swagger UI): http://127.0.0.1:8000/docs

## Endpoints

| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/token` | Obtain a JWT access token | No |
| GET | `/users/me` | Get the current authenticated user | Yes |
| GET | `/alerts` | List the current user's alerts | Yes |
| POST | `/alerts` | Create an alert | Yes |
| GET | `/alerts/{alert_id}` | Get one of your alerts by id | Yes |
| PATCH | `/alerts/{alert_id}` | Update fields of your alert by id | Yes |
| DELETE | `/alerts/{alert_id}` | Delete your alert by id | Yes |
| GET | `/prices/{symbol}` | Get the latest cached price for a symbol | No |
| WS | `/ws/alerts?token=<jwt>` | Real-time alert notifications | Yes |

Prices are public market data (no auth). Alerts are private and scoped to their owner (auth required).

## Tests

```bash
docker compose exec web pytest
```

Tests run against an in-memory SQLite database (isolated from the Postgres data), covering authentication, alert privacy, and validation.

## Known limitations / future work

- No retry with backoff on transient Binance network errors (a failed fetch is skipped until the next poll).
- The WebSocket endpoint detects a client disconnect only on the next publish, rather than immediately (a full solution would listen to the socket and the Redis channel in parallel).
- `cooldown` is a fixed constant; it could be made per-alert.
