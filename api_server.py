#!/usr/bin/env python3
"""
API Server FastAPI per Nexus Infinity Real
Espone l'intelligenza AI via REST API
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = FastAPI(
    title="Nexus Infinity Real API",
    description="Sistema Operativo per Agenti AI",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq Client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Models
class ChatRequest(BaseModel):
    message: str
    system_prompt: str = "Sei Nexus Infinity, un sistema operativo intelligente per agenti AI."

class ChatResponse(BaseModel):
    response: str
    model: str = "llama-3.3-70b-versatile"

# Routes
@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "Nexus Infinity Real API",
        "version": "1.0.0"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Invia un messaggio e ricevi una risposta da Groq"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        
        return ChatResponse(
            response=response.choices[0].message.content,
            model="llama-3.3-70b-versatile"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def status():
    """Status dell'API"""
    return {
        "status": "operational",
        "groq_connected": True,
        "model": "llama-3.3-70b-versatile"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("API_DEBUG", "false").lower() == "true"
    )
