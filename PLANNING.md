# Nexus Infinity Real — verified plan

**Ultimo aggiornamento**: 2026-09-02
**Versione**: 1.1.0 candidate
**Stato**: local MVP verified; public deployment not configured

## Completed and verified

- [x] Groq-backed CLI and FastAPI service share a validated core.
- [x] Provider errors are sanitized before reaching API clients.
- [x] API readiness reports configuration truthfully.
- [x] Optional Bearer-token protection and explicit CORS origins.
- [x] Persistent local conversations, approvals, logs, and scheduler tasks.
- [x] Standalone Windows download/setup/start bootstrap.
- [x] Setup stops on dependency, configuration, test, or health-check errors.
- [x] Docker image runs unprivileged with persistent data volumes.
- [x] Offline test suite and Python 3.11–3.13 CI workflow.
- [x] Secret and runtime files excluded from Git and Docker contexts.

## Not yet complete

- [ ] Run the Windows bootstrap on a real Windows 10/11 machine.
- [ ] Run one live Groq smoke test with a newly rotated key.
- [ ] Choose and provision the production host.
- [ ] Configure TLS, DNS, backups, monitoring, and recovery.
- [ ] Add production rate limiting and a multi-user identity model.
- [ ] Replace local JSON files before running multiple replicas.
- [ ] Add end-to-end deployment tests.

## Production gate

Do not label the system “fully online” until all of these are evidenced:

1. CI is green on the target commit.
2. The container is healthy on the selected host.
3. `NEXUS_API_TOKEN` is configured through the host secret manager.
4. A live Groq request succeeds without logging the key.
5. The domain resolves to the host and HTTPS validates.
6. Backup and rollback procedures have been exercised.

## Verified test baseline

- 14 offline tests pass locally on Python 3.12.
- Python compilation succeeds.
- Installed dependency set passes `pip check`.
- API starts without a key and correctly reports `configuration_required`.
- `/api/chat` correctly returns HTTP 503 until a valid key is configured.
