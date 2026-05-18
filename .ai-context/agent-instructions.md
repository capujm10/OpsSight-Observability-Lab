# Agent Instructions

## Allowed actions
- Inspect repository structure and canonical docs before changing files.
- Refine documentation or context files when requested.
- Make small, reversible code or config changes only when explicitly in scope.
- Run local validation commands and report failures with concrete evidence.

## Forbidden actions
- Do not commit, push, merge, or open PRs without explicit approval.
- Do not modify runtime, Docker, Kubernetes, CI, dependency, secret, or deployment files unless explicitly requested.
- Do not weaken tests, smoke checks, telemetry contracts, CodeQL, or security gates.
- Do not duplicate canonical documentation in `.ai-context`.
- Do not read or expose secrets, `.env` files, credentials, tokens, or private endpoints.

## Required checks
- For context-only documentation changes:
  - `git diff --check`
  - `git status --short`
- Before PRs or behavior changes, follow the validation requirements in `AGENTS.md` and `.github/copilot-instructions.md`.
- Record any skipped validation and the reason.

## Context retrieval rules
- Treat `AGENTS.md`, `README.md`, `.github/copilot-instructions.md`, and `docs/` as canonical.
- Use `.ai-context` as a routing and safety index only.
- Prefer runbooks and architecture docs over raw logs or generated artifacts.
- When behavior changes, check the relevant canonical docs before proposing documentation updates.

## Approval requirements
- Ask before editing files outside the requested scope.
- Ask before running commands that require elevated permissions, network access, or destructive operations.
- Ask before committing, pushing, changing branch strategy, or modifying repository governance.
