# Security Hardening

Implemented local baseline:

- Custom application containers run as non-root users.
- Local app services use read-only root filesystems, dropped capabilities, no-new-privileges, tmpfs-backed `/tmp`, and health checks where compatible.
- API-facing FastAPI services add conservative security headers.
- Dependencies are pinned in requirements files.
- Runtime images use slim Python base images.
- Secrets are excluded from Git through `.gitignore` and represented by `.env.example`.
- GitHub Actions runs Ruff, format checks, pytest, mypy, YAML validation, Compose validation, Kubernetes dry-run validation, dependency auditing, image builds, and smoke testing.
- Kubernetes manifests include resource limits, probes, NetworkPolicy examples, and Secret placeholders.

Production recommendations:

- Replace local Grafana admin credentials with secret-managed credentials. The `admin` / `admin` default is local-demo only.
- Use External Secrets, Sealed Secrets, or cloud secret managers.
- Enable TLS for public endpoints and OTLP transport.
- Add image scanning, SBOM generation, and signature verification.
- Restrict Docker socket and host filesystem access; Alloy and the local runtime exporter use these mounts only for workstation observability.
- Use Kubernetes discovery in clusters instead of Docker socket discovery.
- Enforce read-only root filesystems and drop Linux capabilities for every production workload that does not need write access.
- Add authentication and authorization before exposing API or AI RCA endpoints beyond a trusted local network.
