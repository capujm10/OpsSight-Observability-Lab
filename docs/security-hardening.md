# Security Hardening

Implemented local baseline:

- Custom application containers run as non-root users.
- Local app services use read-only root filesystems, dropped capabilities, no-new-privileges, tmpfs-backed `/tmp`, and health checks where compatible.
- API-facing FastAPI services add conservative security headers.
- Dependencies are pinned in requirements files.
- Runtime images use slim Python base images.
- Secrets are excluded from Git through `.gitignore` and represented by `.env.example`.
- GitHub Actions runs Ruff, format checks, pytest, mypy, YAML validation, Compose validation, Kubernetes dry-run validation, dependency auditing, image builds, and smoke testing.
- Kubernetes validation in CI starts a KIND cluster before running `kubectl apply --dry-run=client --validate=false`.
- Repository settings currently include GitHub secret scanning, push protection, and branch protection for `main`.
- Dependabot is configured for governed version-update pull requests across GitHub Actions and Python requirement files, with grouped minor/patch updates, maintainer review assignment, scoped labels, and consistent dependency commit prefixes.
- CodeQL runs Python static analysis in a separate GitHub Actions workflow and uploads findings to GitHub code scanning.
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
- Enable Dependabot security updates if the repository owner wants GitHub-managed vulnerability PRs in addition to scheduled version updates.
- Review CodeQL findings after the first scheduled run and tune only if findings are noisy or unactionable.

Dependency governance expectations:

- Review grouped minor/patch PRs as maintenance changes, but still require the normal CI, security, and smoke-relevant checks before merge.
- Treat major version PRs as compatibility work. Review changelogs, API changes, runtime behavior, and rollback risk before merge.
- Keep Dependabot PR labels intact so dependency, Python service, and GitHub Actions updates remain easy to filter.
