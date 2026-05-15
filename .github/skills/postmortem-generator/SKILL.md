# Postmortem Generator Skill

## Goal

Create blameless postmortems from OpsSight incidents, validation failures, or simulated outages.

## Workflow

1. Gather timeline, impact, and detection source.
2. Include metrics, logs, traces, and smoke test evidence.
3. Identify root cause and contributing factors.
4. Generate follow-up actions.

## Commands

```bash
bash .github/skills/postmortem-generator/scripts/new-postmortem.sh incident-id docs/postmortems/incident-id.md
python scripts/generate-postmortem.py
```

## Validation

Every postmortem should include evidence and at least one preventive action.

## Troubleshooting

Do not invent customer impact or telemetry. If evidence is missing, state that explicitly.
