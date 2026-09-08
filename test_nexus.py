#!/usr/bin/env python3
"""Offline test suite for Nexus Infinity Real."""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from api_server import api_status, require_api_token
from approval_gate import ActionType, ApprovalGate
from main import NexusConfigurationError, NexusInfinityCore, NexusProviderError
from memory import PersistentMemory
from monitoring import EventType, NexusMonitor
from task_scheduler import TaskScheduler


class FakeCompletions:
    def __init__(self, content: str = "ok", error: Exception | None = None) -> None:
        self.content = content
        self.error = error

    def create(self, **_: object) -> SimpleNamespace:
        if self.error:
            raise self.error
        message = SimpleNamespace(content=self.content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeClient:
    def __init__(self, content: str = "ok", error: Exception | None = None) -> None:
        completions = FakeCompletions(content, error)
        self.chat = SimpleNamespace(completions=completions)


class TemporaryDirectoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()


class TestPersistentMemory(TemporaryDirectoryTest):
    def setUp(self) -> None:
        super().setUp()
        self.memory = PersistentMemory(str(self.root / "memory"))

    def test_save_conversation(self) -> None:
        self.memory.save_conversation("user", "Ciao!")
        conversations = self.memory.get_conversations()
        self.assertEqual(conversations[0]["role"], "user")

    def test_save_state(self) -> None:
        self.memory.save_state({"status": "online", "tasks": 5})
        self.assertEqual(self.memory.load_state()["status"], "online")

    def test_checkpoint(self) -> None:
        checkpoint_id = self.memory.create_checkpoint("Test", {"version": "1.0"})
        self.assertEqual(
            self.memory.load_checkpoint(checkpoint_id)["version"], "1.0"
        )


class TestApprovalGate(TemporaryDirectoryTest):
    def setUp(self) -> None:
        super().setUp()
        self.gate = ApprovalGate(str(self.root / "approvals"))

    def test_approve_and_reject(self) -> None:
        approved = self.gate.request_approval(ActionType.MODIFY_FILE, "Modify")
        rejected = self.gate.request_approval(ActionType.DELETE_FILE, "Delete")
        self.gate.approve(approved)
        self.gate.reject(rejected, "unsafe")
        self.assertEqual(self.gate.get_approval_status(approved)["status"], "approved")
        self.assertEqual(self.gate.get_approval_status(rejected)["status"], "rejected")


class TestMonitoring(TemporaryDirectoryTest):
    def test_events_and_metrics(self) -> None:
        monitor = NexusMonitor(str(self.root / "logs"))
        monitor.log_event(EventType.TASK_START, "Task started")
        monitor.log_api_call("/api/chat", "POST", 200, 0.15)
        self.assertEqual(len(monitor.get_events()), 2)
        self.assertEqual(monitor.get_metrics()["events"]["api_call"], 1)

    def test_logger_handler_is_not_duplicated(self) -> None:
        first = NexusMonitor(str(self.root / "logs"))
        second = NexusMonitor(str(self.root / "logs"))
        self.assertIs(first.logger, second.logger)
        self.assertEqual(len(first.logger.handlers), 1)


class TestNexusCore(unittest.TestCase):
    def test_chat_with_injected_client(self) -> None:
        core = NexusInfinityCore(client=FakeClient("response"), persist_memory=False)
        self.assertEqual(core.chat("hello"), "response")
        self.assertEqual(len(core.conversation_history), 2)

    def test_missing_key_is_rejected(self) -> None:
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            with self.assertRaises(NexusConfigurationError):
                NexusInfinityCore(persist_memory=False)

    def test_provider_error_is_sanitized(self) -> None:
        core = NexusInfinityCore(
            client=FakeClient(error=RuntimeError("secret provider detail")),
            persist_memory=False,
        )
        with self.assertRaisesRegex(NexusProviderError, "Richiesta al provider"):
            core.chat("hello")


class TestTaskScheduler(TemporaryDirectoryTest):
    def test_tasks_persist_across_instances(self) -> None:
        planning = self.root / "PLANNING.md"
        planning.write_text(
            "# Plan\n\n**Ultimo aggiornamento**: old\n", encoding="utf-8"
        )
        state = self.root / "tasks.json"
        scheduler = TaskScheduler(str(planning), str(state), client=FakeClient())
        task = scheduler.create_task("Audit", "Inspect repository", "high")
        reloaded = TaskScheduler(str(planning), str(state), client=FakeClient())
        self.assertEqual(reloaded.tasks[0]["id"], task["id"])
        self.assertIn("Stato task generato", planning.read_text(encoding="utf-8"))

    def test_task_execution_moves_task_to_completed(self) -> None:
        scheduler = TaskScheduler(
            str(self.root / "PLANNING.md"),
            str(self.root / "tasks.json"),
            client=FakeClient("done"),
        )
        task = scheduler.create_task("Audit", "Inspect repository")
        self.assertEqual(scheduler.execute_task(task["id"]), "done")
        self.assertEqual(scheduler.get_status()["completed_tasks"], 1)

    def test_state_file_is_valid_json(self) -> None:
        state = self.root / "tasks.json"
        scheduler = TaskScheduler(
            str(self.root / "PLANNING.md"), str(state), client=FakeClient()
        )
        scheduler.create_task("Test", "Persist JSON")
        self.assertIn("tasks", json.loads(state.read_text(encoding="utf-8")))


class TestApiConfiguration(unittest.TestCase):
    def test_status_does_not_claim_live_connection(self) -> None:
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            result = asyncio.run(api_status())
        self.assertFalse(result["groq_configured"])
        self.assertNotIn("groq_connected", result)

    def test_optional_api_token(self) -> None:
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="correct"
        )
        with patch.dict(os.environ, {"NEXUS_API_TOKEN": "correct"}):
            require_api_token(credentials)
        with patch.dict(os.environ, {"NEXUS_API_TOKEN": "correct"}):
            with self.assertRaises(HTTPException):
                require_api_token(None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
