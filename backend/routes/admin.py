"""Admin route — lightweight operational endpoints for the support assistant."""

from datetime import datetime, timezone

from fastapi import APIRouter

from routes.chat import INTENTS

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/intents")
def intents():
    return {"supported_intents": [intent for intent, _, _ in INTENTS]}
