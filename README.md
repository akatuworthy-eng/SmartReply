# SmartReply — AI Customer Support Assistant 🤖💬

A customer-support assistant that answers common questions instantly, with or
without an API key. Handles shipping, refunds, order status, accounts, pricing,
and escalations — and drops to a person when a human is needed.

## ✨ Features

- **Intent-aware replies** — a lightweight keyword classifier maps a customer's
  message to a concrete, helpful answer (shipping, refunds, account, pricing,
  support hours, talk-to-a-person, …)
- **Optional AI mode** — set `OPENAI_API_KEY` and replies come from GPT-4o-mini
  instead; any failure falls back to the rule-based path, so the API never breaks
- **Admin endpoints** — `/admin/health` and `/admin/intents` for ops
- **Seeding** — `ingest.py` turns a plain-text FAQ into a knowledge bank

## 🏗️ Architecture

```
┌─────────────┐   HTTP/JSON   ┌──────────────┐
│  React UI   │ ────────────► │   FastAPI    │
│  (frontend) │               │  (backend)   │
└─────────────┘               └──────┬───────┘
                                     │
                          ┌──────────▼─────────┐
                          │  rules classifier  │  │ optional LLM (OpenAI)
                          └────────────────────┘
```

| Path | Purpose |
|------|---------|
| `backend/app.py` | FastAPI entrypoint (mounts routers, CORS) |
| `backend/routes/chat.py` | `POST /chat` + intent classifier + AI fallback |
| `backend/routes/admin.py` | `GET /admin/health` · `GET /admin/intents` |
| `backend/ingest.py` | FAQ -> knowledge-bank seeder |
| `backend/tests/` | Route + classifier tests |

## 🚀 Run it

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload     # → http://127.0.0.1:8000, API docs at /docs
```

To enable AI replies, create `backend/.env` (or export) with `OPENAI_API_KEY=...`.
Interactive docs at `http://127.0.0.1:8000/docs`.

## 🔬 Tests

```bash
cd backend && pytest
```

## 🚢 Deploy

A `render.yaml` is included to deploy the backend to Render's free tier
(`pip install -r requirements.txt` to build, `uvicorn app:app` to start).
