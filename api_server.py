#!/usr/bin/env python3
"""FastAPI server for Nexus Infinity Real."""

from __future__ import annotations

import hmac
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from main import (
    DEFAULT_MODEL,
    NexusConfigurationError,
    NexusInfinityCore,
    NexusProviderError,
)

load_dotenv()

app = FastAPI(
    title="Nexus Infinity Real API",
    description="Groq-backed Nexus API",
    version="1.1.0",
)

cors_origins = [
    value.strip()
    for value in os.getenv("CORS_ORIGINS", "").split(",")
    if value.strip()
]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

bearer = HTTPBearer(auto_error=False)


def require_api_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> None:
    """Require a bearer token only when NEXUS_API_TOKEN is configured."""
    expected = os.getenv("NEXUS_API_TOKEN", "").strip()
    if not expected:
        return
    supplied = credentials.credentials if credentials else ""
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)
    system_prompt: str | None = Field(default=None, max_length=8_000)


class ChatResponse(BaseModel):
    response: str
    model: str


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "status": "online",
        "service": "Nexus Infinity Real API",
        "version": "1.1.0",
    }


@app.get("/api/status")
async def api_status() -> dict[str, str | bool]:
    key = os.getenv("GROQ_API_KEY", "")
    configured = key.startswith("gsk_") and len(key) > 20
    return {
        "status": "ready" if configured else "configuration_required",
        "groq_configured": configured,
        "model": os.getenv("GROQ_MODEL", DEFAULT_MODEL),
    }


@app.post(
    "/api/chat",
    response_model=ChatResponse,
    dependencies=[Depends(require_api_token)],
)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        core = NexusInfinityCore(persist_memory=False)
        response = core.chat(request.message, request.system_prompt)
        return ChatResponse(response=response, model=core.model)
    except NexusConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except NexusProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("API_DEBUG", "false").lower() == "true",
    )
