from typing import Literal

from pydantic import BaseModel, Field

Confidence = Literal["high", "medium", "low"]


class TelemetrySignal(BaseModel):
    name: str
    value: str | float | int | None = None
    unit: str | None = None
    description: str | None = None


class AlertContext(BaseModel):
    name: str
    severity: str = "warning"
    service: str
    status: str | None = None
    summary: str | None = None
    description: str | None = None
    remediation: str | None = None
    started_at: str | None = None
    ended_at: str | None = None
    fingerprint: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)


class TraceContext(BaseModel):
    trace_ids: list[str] = Field(default_factory=list)
    slow_spans: list[str] = Field(default_factory=list)
    failed_spans: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)


class LogContext(BaseModel):
    correlation_ids: list[str] = Field(default_factory=list)
    patterns: list[str] = Field(default_factory=list)
    exception_signatures: list[str] = Field(default_factory=list)
    loki_queries: list[str] = Field(default_factory=list)


class IncidentContext(BaseModel):
    incident_id: str | None = None
    title: str | None = None
    affected_services: list[str] = Field(default_factory=list)
    impacted_slos: list[str] = Field(default_factory=list)
    burn_rate: float | None = None
    error_rate: float | None = None
    p95_latency_seconds: float | None = None
    dependency: str | None = None
    alert: AlertContext | None = None
    metrics: list[TelemetrySignal] = Field(default_factory=list)
    traces: TraceContext = Field(default_factory=TraceContext)
    logs: LogContext = Field(default_factory=LogContext)
    grafana_links: list[str] = Field(default_factory=list)
    postmortem_path: str | None = None


class RCAHypothesis(BaseModel):
    cause: str
    confidence: Confidence
    supporting_signals: list[str]
    impacted_systems: list[str]
    validation_steps: list[str]


class RCAResponse(BaseModel):
    summary: str
    alert_explanation: str
    trace_analysis: str
    log_analysis: str
    likely_root_causes: list[RCAHypothesis]
    impacted_slos: list[str]
    recommended_actions: list[str]
    risk_notes: list[str]
    telemetry_references: dict[str, list[str]]
    provider: str
    model: str
    fallback_used: bool = False
    confidence: Confidence = "medium"


class AlertmanagerAlert(BaseModel):
    status: str
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    startsAt: str | None = None
    endsAt: str | None = None
    fingerprint: str | None = None
    generatorURL: str | None = None


class AlertmanagerWebhook(BaseModel):
    receiver: str | None = None
    status: str
    alerts: list[AlertmanagerAlert]
    groupLabels: dict[str, str] = Field(default_factory=dict)
    commonLabels: dict[str, str] = Field(default_factory=dict)
    commonAnnotations: dict[str, str] = Field(default_factory=dict)
    externalURL: str | None = None
    version: str | None = None
    groupKey: str | None = None
    truncatedAlerts: int = 0


class RCAArtifact(BaseModel):
    incident_id: str
    json_path: str
    markdown_path: str


class WebhookRCAResult(BaseModel):
    received_alerts: int
    generated: list[RCAArtifact]
    analyses: list[RCAResponse]
