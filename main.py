#!/usr/bin/env python3
"""Nexus Infinity Real command-line core."""

from __future__ import annotations

import os
import sys
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from memory import PersistentMemory
from monitoring import EventType, NexusMonitor

load_dotenv()

DEFAULT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_SYSTEM_PROMPT = (
    "Sei Nexus Infinity, un assistente per automazione, sicurezza, analisi dati "
    "e orchestrazione di task. Non dichiarare di avere eseguito azioni che non "
    "hai realmente eseguito. Rispondi in modo conciso e professionale."
)


class NexusConfigurationError(ValueError):
    """Raised when required local configuration is missing."""


class NexusProviderError(RuntimeError):
    """Raised when the configured model provider fails."""


def _is_valid_groq_key(value: str | None) -> bool:
    return bool(value and value.startswith("gsk_") and len(value) > 20)


class NexusInfinityCore:
    """Groq chat core with optional local memory and audit logging."""

    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str | None = None,
        persist_memory: bool = True,
    ) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        if client is None and not _is_valid_groq_key(api_key):
            raise NexusConfigurationError(
                "GROQ_API_KEY non configurata o non valida nel file .env"
            )

        self.client = client or Groq(api_key=api_key)
        self.model = model or os.getenv("GROQ_MODEL", DEFAULT_MODEL)
        self.conversation_history: list[dict[str, str]] = []
        self.memory = PersistentMemory() if persist_memory else None
        self.monitor = NexusMonitor()

    def chat(self, user_message: str, system_prompt: str | None = None) -> str:
        """Send one message to Groq and return its textual response."""
        message = user_message.strip()
        if not message:
            raise ValueError("Il messaggio non può essere vuoto")
        if len(message) > 20_000:
            raise ValueError("Il messaggio supera il limite di 20.000 caratteri")

        prompt = (system_prompt or DEFAULT_SYSTEM_PROMPT).strip()
        self.conversation_history.append({"role": "user", "content": message})
        if self.memory:
            self.memory.save_conversation("user", message)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    *self.conversation_history,
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            assistant_message = response.choices[0].message.content
            if not isinstance(assistant_message, str) or not assistant_message.strip():
                raise NexusProviderError("Il provider ha restituito una risposta vuota")
        except NexusProviderError:
            raise
        except Exception as exc:
            self.monitor.log_event(
                EventType.TASK_ERROR,
                "Groq request failed",
                {"error_type": type(exc).__name__},
                severity="error",
            )
            raise NexusProviderError("Richiesta al provider Groq non riuscita") from exc

        self.conversation_history.append(
            {"role": "assistant", "content": assistant_message}
        )
        if self.memory:
            self.memory.save_conversation("assistant", assistant_message)
        self.monitor.log_event(
            EventType.API_CALL,
            "Groq chat completion succeeded",
            {"model": self.model},
        )
        return assistant_message

    def run_interactive(self) -> None:
        print("=" * 60)
        print("NEXUS INFINITY REAL - CLI")
        print(f"Model: {self.model}")
        print("Type 'exit' to stop.\n")

        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() == "exit":
                    break
                if not user_input:
                    continue
                print(f"\nNexus: {self.chat(user_input)}\n")
            except KeyboardInterrupt:
                print("\nInterrupted.")
                break
            except (ValueError, NexusProviderError) as exc:
                print(f"Error: {exc}")


def main() -> int:
    try:
        NexusInfinityCore().run_interactive()
        return 0
    except NexusConfigurationError as exc:
        print(f"Configuration error: {exc}")
        print("Run START_NEXUS.bat to configure the local environment.")
        return 1
    except Exception as exc:
        print(f"Unexpected startup error: {type(exc).__name__}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
