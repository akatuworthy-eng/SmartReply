"""SmartReply — AI Customer Support Assistant API.

FastAPI entrypoint. Mounts the chat and admin routers and sets up CORS so the
frontend can talk to it.

Run from this directory (matches render.yaml):

    uvicorn app:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import admin, chat

app = FastAPI(title="SmartReply API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"msg": "SmartReply API running", "docs": "/docs"}
