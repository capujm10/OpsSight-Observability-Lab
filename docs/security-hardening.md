# Security Hardening

Implemented local baseline:

- API and dependency containers run as non-root users.
- Dependencies are pinned in requirements files.
- Runtime images use slim Python base images.
- Secrets are excluded from Git through `.gitignore` and represented by `.env.example`.
- Kubernetes manifests include resource limits, probes, NetworkPolicy examples, and Secret placeholders.

Production recommendations:

- Replace local Grafana admin credentials with secret-managed credentials.
- Use External Secrets, Sealed Secrets, or cloud secret managers.
- Enable TLS for public endpoints and OTLP transport.
- Add image scanning, SBOM generation, and signature verification.
- Restrict Docker socket access; Alloy should use Kubernetes discovery in clusters.
- Enforce read-only root filesystems and drop Linux capabilities where supported.
