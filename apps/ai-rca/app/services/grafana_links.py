from urllib.parse import quote

from app.config import Settings
from app.models.rca import IncidentContext


def build_grafana_links(context: IncidentContext, settings: Settings) -> list[str]:
    base = settings.grafana_url.rstrip("/")
    links = [
        f"{base}/d/opsight-sre-overview/opsight-sre-overview",
        f"{base}/d/opsight-incident-investigation/opsight-incident-investigation",
    ]
    for trace_id in context.traces.trace_ids:
        links.append(f"{base}/explore?left={quote('{"datasource":"tempo","queries":[{"query":"' + trace_id + '"}]}')}")
    for query in context.logs.loki_queries:
        links.append(f"{base}/explore?left={quote('{"datasource":"loki","queries":[{"expr":"' + query + '"}]}')}")
    return links
