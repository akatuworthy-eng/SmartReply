"""Chat route — answer customer-support questions.

Works with or without an API key:

- With ``OPENAI_API_KEY`` set, a customer message is sent to an OpenAI chat model
  for a natural reply.
- Without a key (or if the call fails) we fall back to a deterministic,
  keyword-based intent classifier with canned replies, so the assistant is fully
  functional offline.

External call failures are swallowed: a bad key or a network hiccup never breaks
the endpoint.
"""

import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

# Intent -> (keywords, response). Matching is case-insensitive, first hit wins.
INTENTS = [
    (
        "shipping",
        ("ship", "track", "deliver", "arrive", "where is my order", "parcel", "courier"),
        "Your order usually ships within 1–2 business days. Once it ships we email you a "
        "tracking link — check your inbox (and spam) for a message from us. If it's been "
        "over 5 business days, reply with your order number and we'll dig in.",
    ),
    (
        "refund",
        ("refund", "return", "money back", "exchange", "reimburse"),
        "Returns are accepted within 30 days of delivery for unused items. Start one by "
        "replied to this chat with your order number, and refunds land in 3–5 business days "
        "after we receive the item.",
    ),
    (
        "order status",
        ("order", "status", "placed", "confirm"),
        "Thanks for checking! Reply with your order number and I'll pull up the latest status.",
    ),
    (
        "account",
        ("login", "password", "account", "sign in", "reset", "locked"),
        "For account or password issues, try 'Forgot password' on the sign-in page. If "
        "you're locked out, tell me your account email and I'll escalate it to our team.",
    ),
    (
        "support hours",
        ("hours", "open", "when", "available", "support team", "someone"),
        "Our support team is here 9am–6pm weekdays (and weekends by email). If a human "
        "would help more than a bot right now, just say 'talk to a person' and we'll queue "
        "you.",
    ),
    (
        "pricing",
        ("price", "cost", "pricing", "plan", "how much", "billing"),
        "We have a free plan and two paid tiers. Tell me what you're looking for and I'll "
        "point you to the right one — billing questions can also go to our team.",
    ),
    (
        "human",
        ("human", "person", "agent", "representative", "talk to someone", "live"),
        "Got it — I'll connect you with a person. Expect a reply within a few hours during "
        "business days; meanwhile, how can I help?"
    ),
]

FALLBACK = (
    "Thanks for your message! I don't have a canned answer for that yet, so I've passed it "
    "to our team — they'll get back to you shortly. Is there anything about delivery, "
    "refunds, or your account I can help with meanwhile?"
)


class ChatIn(BaseModel):
    message: str


class ChatOut(BaseModel):
    reply: str
    intent: str
    source: str


def classify(message: str) -> tuple[str, str]:
    """Return (intent, reply) for a message using keyword matching."""
    text = message.lower()
    for intent, keywords, reply in INTENTS:
        if any(k in text for k in keywords):
            return intent, reply
    return "unknown", FALLBACK


def _ai_reply(message: str) -> str | None:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=key)
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are SmartReply, a concise, warm customer-support agent.",
                },
                {"role": "user", "content": message},
            ],
            max_tokens=180,
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return None


@router.post("", response_model=ChatOut)
def chat(payload: ChatIn):
    if not payload.message.strip():
        raise HTTPException(status_code=422, detail="message must not be empty")

    ai = _ai_reply(payload.message)
    if ai:
        return ChatOut(reply=ai, intent="llm", source="ai")

    intent, reply = classify(payload.message)
    return ChatOut(reply=reply, intent=intent, source="rules")


@router.get("/intents", summary="List supported intents")
def intents():
    return [intent for intent, _, _ in INTENTS]
