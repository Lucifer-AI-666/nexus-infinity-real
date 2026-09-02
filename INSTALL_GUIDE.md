# Windows installation guide

## One-file automatic setup

1. Download `NEXUS_BOOTSTRAP.bat` from this repository.
2. Put it in the folder where Nexus should be installed.
3. Double-click it.
4. If Python is missing, approve the `winget` installation when prompted.
5. Paste a newly generated Groq API key into the hidden prompt.

The key is written only to the local `.env` file. The script never writes it to
GitHub and never prints it back to the terminal.

The normal result is two windows:

- Nexus API at <http://127.0.0.1:8000/docs>;
- Nexus CLI, where `exit` stops the interactive session.

## Existing checkout

Run one of these commands from Command Prompt:

```text
START_NEXUS.bat --all
START_NEXUS.bat --api
START_NEXUS.bat --cli
START_NEXUS.bat --install-only
```

The script exits with a non-zero code if Python setup, dependency installation,
configuration validation, tests, or the API health check fails.

## Updating safely

Running `NEXUS_BOOTSTRAP.bat` outside the repository performs a Git
fast-forward-only update. It will stop instead of overwriting local changes.

If Git is unavailable, the first installation falls back to a GitHub ZIP
download through Windows PowerShell.

## Configuration

Local settings are in `.env`:

```dotenv
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
API_HOST=127.0.0.1
API_PORT=8000
API_DEBUG=false
NEXUS_API_TOKEN=
CORS_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

Set `NEXUS_API_TOKEN` before exposing the API outside the computer. Keep
`API_DEBUG=false` in deployments.

## Troubleshooting

### Python was just installed but is not found

Close Command Prompt and run the script again so Windows reloads `PATH`.

### Dependency installation failed

Do not continue with a partial environment. Check internet access, then rerun
`START_NEXUS.bat`; `pip` will resume safely.

### Groq key rejected

Generate a new key in the Groq console. Keys pasted into a public or shared
place must be revoked rather than reused.

### API did not become healthy

Check whether port 8000 is already occupied:

```text
netstat -ano | findstr :8000
```

Change `API_PORT` in `.env` if necessary. The automatic browser link currently
uses the configured port automatically.

### Run tests manually

```text
.venv\Scripts\python.exe -m unittest -v test_nexus.py
.venv\Scripts\python.exe -m compileall -q .
.venv\Scripts\python.exe -m pip check
```
