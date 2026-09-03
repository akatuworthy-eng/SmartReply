import os

from fastapi.testclient import TestClient

from app import app

os.environ.pop("OPENAI_API_KEY", None)  # force the rules/fallback path for tests
client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["msg"] == "SmartReply API running"


def test_chat_returns_nonempty_reply():
    r = client.post("/chat", json={"message": "Where is my order?"})
    assert r.status_code == 200
    body = r.json()
    assert body["reply"]
    assert body["source"] == "rules"


def test_chat_maps_shipping_intent():
    r = client.post("/chat", json={"message": "Can you track my parcel please"})
    assert r.status_code == 200
    assert r.json()["intent"] == "shipping"


def test_chat_maps_refund_intent():
    r = client.post("/chat", json={"message": "I want a refund"})
    assert r.json()["intent"] == "refund"


def test_chat_known_intent_does_not_use_fallback():
    r = client.post("/chat", json={"message": "what are your support hours"})
    assert r.json()["intent"] == "support hours"
    assert "canned answer" not in r.json()["reply"]


def test_chat_empty_message_rejected():
    r = client.post("/chat", json={"message": "   "})
    assert r.status_code == 422


def test_intents_endpoint():
    r = client.get("/chat/intents")
    assert r.status_code == 200
    assert "shipping" in r.json()


def test_admin_health():
    r = client.get("/admin/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
