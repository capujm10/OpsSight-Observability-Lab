# SEV-1 Incident Postmortem: $title

This template is for broad customer-impacting outages, rapid SLO burn, or executive-visible incidents.

| Field | Value |
| --- | --- |
| Incident ID | `$id` |
| Severity | `$severity` |
| Status | `$status` |
| Incident Commander | `$incident_commander` |
| Technical Owner | `$owner` |
| Started | `$started_at` |
| Resolved | `$resolved_at` |
| Duration | `$duration` |

## Executive Summary

$impact_summary

## Impact

### Affected Systems

$affected_systems

### Customer Impact

$customer_impact

## Detection and Alerting

- Detection method: $detection_method
- Primary alert: `$alert_triggered`
- SLO burn: $slo_burn

## Timeline

$timeline

## Root Cause

$root_cause

## Contributing Factors

$contributing_factors

## Mitigation and Resolution

### Mitigation Steps

$mitigation_steps

### Resolution

$resolution

## Recovery Validation

$recovery_validation

## Preventive Actions

$preventive_actions

## Follow-Up Tasks

$follow_up_tasks

## Lessons Learned

$lessons_learned

$ai_enrichment

## Telemetry References

$telemetry_references

## Grafana Operational Annotations

```json
$grafana_annotations
```
