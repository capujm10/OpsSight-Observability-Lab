# Governance Context

## Relationship to Engineering Standards

`governance.yml` defines how OpsSight consumes engineering standards without turning a portfolio lab into heavyweight process overhead. The repository acts as a practical standards consumer: it applies security, observability, validation, and documentation expectations to a local-first runtime where evidence can be demonstrated quickly.

OpsSight is intentionally governance-aware but implementation-led. Standards are used to shape release quality, risk controls, and documentation completeness, not to increase bureaucracy.

## Governance Philosophy

- Keep governance lightweight, explicit, and enforceable.
- Prefer additive and reversible changes over broad architectural churn.
- Preserve local operability while still validating production-style behaviors.
- Use validation evidence and telemetry outcomes as the source of truth.
- Keep human-supervised operations as the default for incident response and remediation.

## Repository Boundaries

In scope:

- Observability-first application services and local telemetry stack.
- Incident simulation, RCA support workflows, and operational runbooks.
- Kubernetes manifest readiness validation and overlay hygiene.
- Recruiter-facing documentation that reflects real engineering practice.

Out of scope:

- Claims of managed production operation.
- Heavy platform rearchitecture unrelated to observability outcomes.
- Governance artifacts that are not tied to operational value.

## Documentation Expectations

When behavior changes, maintain the docs surface in lockstep:

- `README.md` for architecture, runtime, and validation entrypoints.
- `docs/` runbooks, incident workflows, and architecture references.
- governance context files for standards alignment and repo boundaries.

Documentation quality target:

- clear enough for SRE/platform interviews,
- specific enough for local reproduction,
- honest enough to prevent production overclaim.
