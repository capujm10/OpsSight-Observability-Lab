# SRE Runbook Generator Skill

## Goal

Generate practical runbooks for OpsSight services, incidents, and validation failures.

## Workflow

1. Identify service or failure mode.
2. Select a template from `templates/`.
3. Include detection, triage, mitigation, validation, and rollback.
4. Use real repository commands.

## Commands

```bash
bash .github/skills/sre-runbook-generator/scripts/new-runbook.sh service-outage docs/runbooks/service-outage-runbook.md
```

## Validation

Runbook commands should be copy-pasteable in WSL/Bash or clearly labeled as PowerShell.

## Troubleshooting

Avoid generic advice; every step should reference a real service, endpoint, dashboard, or command.
