#!/usr/bin/env python3
"""Persistent, approval-friendly task scheduler for Nexus."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

PLANNING_START = "<!-- NEXUS_TASKS_START -->"
PLANNING_END = "<!-- NEXUS_TASKS_END -->"


class TaskScheduler:
    """Persist tasks and let Groq produce reports for explicitly queued work."""

    def __init__(
        self,
        planning_file: str = "PLANNING.md",
        state_file: str = "nexus_memory/tasks.json",
        client: Any | None = None,
    ) -> None:
        self.planning_file = Path(planning_file)
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.client = client
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        state = self._load_state()
        self.tasks: list[dict[str, Any]] = state.get("tasks", [])
        self.completed_tasks: list[dict[str, Any]] = state.get("completed", [])

    def _load_state(self) -> dict[str, list[dict[str, Any]]]:
        if not self.state_file.exists():
            return {"tasks": [], "completed": []}
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"tasks": [], "completed": []}
        return data if isinstance(data, dict) else {"tasks": [], "completed": []}

    def _save_state(self) -> None:
        temporary = self.state_file.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(
                {"tasks": self.tasks, "completed": self.completed_tasks},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        temporary.replace(self.state_file)

    def _next_id(self) -> int:
        all_tasks = [*self.tasks, *self.completed_tasks]
        return max((int(task["id"]) for task in all_tasks), default=0) + 1

    def create_task(
        self, title: str, description: str, priority: str = "medium"
    ) -> dict[str, Any]:
        now = datetime.now().isoformat()
        task = {
            "id": self._next_id(),
            "title": title.strip(),
            "description": description.strip(),
            "priority": priority,
            "status": "pending",
            "created_at": now,
            "updated_at": now,
            "subtasks": [],
            "notes": [],
        }
        if not task["title"] or not task["description"]:
            raise ValueError("title and description are required")
        self.tasks.append(task)
        self._commit_updates()
        return task

    def execute_task(self, task_id: int) -> str:
        task = next((item for item in self.tasks if item["id"] == task_id), None)
        if not task:
            raise KeyError(f"Task {task_id} non trovato")

        if self.client is None:
            api_key = os.getenv("GROQ_API_KEY", "")
            if not (api_key.startswith("gsk_") and len(api_key) > 20):
                raise ValueError("GROQ_API_KEY non configurata")
            self.client = Groq(api_key=api_key)

        task["status"] = "in_progress"
        task["updated_at"] = datetime.now().isoformat()
        self._commit_updates()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Sei Nexus Infinity. Produci un report sul task richiesto. "
                            "Non dichiarare azioni esterne non realmente eseguite."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Titolo: {task['title']}\n"
                            f"Descrizione: {task['description']}"
                        ),
                    },
                ],
                temperature=0.4,
                max_tokens=2048,
            )
            result = response.choices[0].message.content
        except Exception:
            task["status"] = "failed"
            task["updated_at"] = datetime.now().isoformat()
            self._commit_updates()
            raise

        task["status"] = "completed"
        task["result"] = result
        task["updated_at"] = datetime.now().isoformat()
        self.completed_tasks.append(task)
        self.tasks.remove(task)
        self._commit_updates()
        return result

    def add_subtask(self, task_id: int, subtask: str) -> dict[str, Any]:
        task = next((item for item in self.tasks if item["id"] == task_id), None)
        if not task:
            raise KeyError(f"Task {task_id} non trovato")
        item = {
            "id": len(task["subtasks"]) + 1,
            "title": subtask.strip(),
            "completed": False,
            "created_at": datetime.now().isoformat(),
        }
        task["subtasks"].append(item)
        self._commit_updates()
        return item

    def add_note(self, task_id: int, note: str) -> None:
        task = next((item for item in self.tasks if item["id"] == task_id), None)
        if not task:
            raise KeyError(f"Task {task_id} non trovato")
        task["notes"].append(
            {"text": note.strip(), "timestamp": datetime.now().isoformat()}
        )
        self._commit_updates()

    def get_status(self) -> dict[str, Any]:
        return {
            "total_tasks": len(self.tasks),
            "pending_tasks": sum(t["status"] == "pending" for t in self.tasks),
            "in_progress_tasks": sum(
                t["status"] == "in_progress" for t in self.tasks
            ),
            "completed_tasks": len(self.completed_tasks),
            "tasks": self.tasks,
            "completed": self.completed_tasks,
        }

    def _commit_updates(self) -> None:
        self._save_state()
        self._update_planning_file()

    def _update_planning_file(self) -> None:
        content = (
            self.planning_file.read_text(encoding="utf-8")
            if self.planning_file.exists()
            else "# Nexus Planning\n"
        )
        timestamp = datetime.now().isoformat(timespec="seconds")
        timestamp_line = f"**Ultimo aggiornamento**: {timestamp}"
        if re.search(r"^\*\*Ultimo aggiornamento\*\*:.*$", content, re.MULTILINE):
            content = re.sub(
                r"^\*\*Ultimo aggiornamento\*\*:.*$",
                timestamp_line,
                content,
                count=1,
                flags=re.MULTILINE,
            )
        else:
            content = f"{timestamp_line}\n\n{content}"

        rows = [
            "## Stato task generato",
            "",
            "| ID | Titolo | Priorità | Stato |",
            "|---:|---|---|---|",
        ]
        for task in self.tasks:
            safe_title = str(task["title"]).replace("|", "\\|")
            rows.append(
                f"| {task['id']} | {safe_title} | {task['priority']} | {task['status']} |"
            )
        if not self.tasks:
            rows.append("| - | Nessun task attivo | - | - |")
        generated = f"{PLANNING_START}\n" + "\n".join(rows) + f"\n{PLANNING_END}"
        pattern = re.compile(
            re.escape(PLANNING_START) + r".*?" + re.escape(PLANNING_END),
            re.DOTALL,
        )
        content = pattern.sub(generated, content) if pattern.search(content) else (
            content.rstrip() + "\n\n" + generated + "\n"
        )
        self.planning_file.write_text(content, encoding="utf-8")

    def run_autonomous(self, duration_hours: int = 1) -> None:
        """Run already-approved pending tasks within a maximum time window."""
        start_time = datetime.now()
        for task in list(self.tasks):
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed >= duration_hours * 3600:
                break
            if task["status"] == "pending":
                self.execute_task(task["id"])


if __name__ == "__main__":
    print(json.dumps(TaskScheduler().get_status(), indent=2, ensure_ascii=False))
