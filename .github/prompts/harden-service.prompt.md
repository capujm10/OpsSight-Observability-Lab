# Harden Service Prompt

Review a service in `apps/` and propose safe hardening changes.

Focus on:

- FastAPI health/readiness behavior
- request validation
- structured logging
- correlation IDs
- OpenTelemetry traces
- Prometheus metrics
- container non-root/runtime restrictions
- dependency timeouts
- tests and CI validation

Do not rename service-local `app` packages or change telemetry labels without a migration note.
