# Retrieval Policy

Prefer:
1. `AGENTS.md` for repository-wide AI agent rules
2. `README.md` for project overview, architecture, services, and validation
3. `.github/copilot-instructions.md` for concise AI coding expectations
4. `docs/` runbooks, architecture, security, incident, SLO, and AI RCA documentation
5. `.ai-context/project-profile.md` for quick orientation
6. source files only when needed for the active task
7. raw logs, generated artifacts, or transcripts only when explicitly needed

Avoid:
- secrets
- .env files
- credentials, tokens, keys, and private endpoints
- raw logs with sensitive values
- generated artifacts unless relevant to the task
- duplicating canonical documentation

Rules:
- Use `.ai-context` as an index, not a source of truth.
- Link decisions back to canonical files when behavior, validation, operations, or security are involved.
- Retrieve the smallest useful context for the current task.
