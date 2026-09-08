# Nexus Infinity Real

Nexus Infinity Real is a local Python/Groq agent foundation with:

- an interactive CLI;
- a FastAPI REST service;
- persistent local conversation, task, approval, and audit files;
- a persistent task scheduler;
- Docker support;
- offline tests and GitHub Actions CI;
- a Windows bootstrap that downloads, configures, tests, and starts the project.

This repository is a working local MVP. It is not an operating system and it is
not yet a production-grade autonomous agent platform.

## Fastest Windows start

Download `NEXUS_BOOTSTRAP.bat` and double-click it. The script:

1. clones or safely fast-forwards the repository;
2. locates Python 3 and can install Python 3.12 through `winget` with consent;
3. creates an isolated `.venv`;
4. installs all dependencies and stops on errors;
5. creates the local `.env` and asks for the Groq key without echoing it;
6. runs the offline self-tests;
7. starts the API and CLI, checks API health, and opens `/docs`.

When the repository is already downloaded, use:

```text
START_NEXUS.bat --all
START_NEXUS.bat --api
START_NEXUS.bat --cli
START_NEXUS.bat --install-only
```

`start.bat` forwards the same optional argument. `QUICK_INSTALL.bat` prepares
the environment without starting services.

## Manual setup

```bash
git clone https://github.com/Lucifer-AI-666/nexus-infinity-real.git
cd nexus-infinity-real
python -m venv .venv
```

Windows:

```text
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python.exe api_server.py
```

macOS/Linux:

```bash
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python api_server.py
```

Put a newly generated Groq key in the local `.env` file:

```dotenv
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
```

Never commit `.env`. It is excluded by `.gitignore` and `.dockerignore`.

## API

The local documentation is at <http://127.0.0.1:8000/docs>.

- `GET /` — service identity;
- `GET /api/status` — local configuration readiness, without pretending to
  perform a live Groq check;
- `POST /api/chat` — one Groq chat completion.

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Ciao Nexus"}'
```

For any network-accessible deployment, set `NEXUS_API_TOKEN` and send it as a
Bearer token. Configure `CORS_ORIGINS` explicitly; wildcard credentialed CORS
is not enabled.

## Docker

Create `.env`, then run:

```bash
docker compose up --build -d
docker compose ps
```

The image runs as an unprivileged user and exposes port `8000`. Local memory,
approval, and audit directories are mounted as volumes.

## Verification

```bash
python -m compileall -q .
python -m unittest -v test_nexus.py
python -m pip check
```

CI runs the suite on Python 3.11, 3.12, and 3.13.

## Security notes

- Revoke any API key pasted into chats, screenshots, tickets, or logs and
  generate a replacement.
- Provider exception details are logged by type and are not returned to API
  clients.
- The API binds to `127.0.0.1` by default. Docker explicitly binds inside the
  container to `0.0.0.0`.
- The approval gate stores decisions; it does not magically sandbox arbitrary
  commands. Do not add shell execution without a separate capability policy.

## Current limitations

- No public deployment or DNS record is created by this repository alone.
- The REST API is stateless per request and does not provide multi-user
  conversation isolation.
- JSON file storage is intended for a single local process, not a distributed
  cluster.
- The scheduler produces model reports for already queued work; it does not
  have unrestricted machine control.

See `PLANNING.md` for the verified state and next production steps.
