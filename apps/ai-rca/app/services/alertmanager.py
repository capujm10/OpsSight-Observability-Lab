from app.models.rca import AlertContext, AlertmanagerAlert, IncidentContext, LogContext, TraceContext


def incident_from_alert(alert: AlertmanagerAlert) -> IncidentContext:
    labels = alert.labels
    annotations = alert.annotations
    service = labels.get("service") or labels.get("job") or labels.get("app") or "unknown-service"
    alert_name = labels.get("alertname", "unknown-alert")
    severity = labels.get("severity", "warning")
    trace_id = labels.get("trace_id") or annotations.get("trace_id")
    correlation_id = labels.get("correlation_id") or annotations.get("correlation_id")
    dependency = labels.get("dependency")
    if not dependency and ("dependency" in alert_name.lower() or "payment" in service.lower()):
        dependency = labels.get("service") if labels.get("service") != "opsight-api" else "payment-gateway"

    affected = [service]
    if dependency and dependency not in affected:
        affected.append(dependency)

    return IncidentContext(
        incident_id=alert.fingerprint or f"{alert_name}-{service}",
        title=annotations.get("summary") or alert_name,
        affected_services=affected,
        impacted_slos=[labels["slo"]] if labels.get("slo") else [],
        dependency=dependency,
        alert=AlertContext(
            name=alert_name,
            severity=severity,
            service=service,
            status=alert.status,
            summary=annotations.get("summary"),
            description=annotations.get("description"),
            remediation=annotations.get("remediation"),
            started_at=alert.startsAt,
            ended_at=alert.endsAt,
            fingerprint=alert.fingerprint,
            labels=labels,
            annotations=annotations,
        ),
        traces=TraceContext(trace_ids=[trace_id] if trace_id else [], services=affected),
        logs=LogContext(correlation_ids=[correlation_id] if correlation_id else []),
    )
