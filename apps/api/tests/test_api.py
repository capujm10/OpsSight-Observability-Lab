import app.api.orders as orders_api
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


async def fake_dependency_call(*args, **kwargs) -> dict[str, str]:
    return {"dependency": "payment-gateway", "operation": kwargs.get("operation", "test"), "outcome": "success"}


def test_live_health() -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_orders_list_includes_correlation_id() -> None:
    orders_api.observed_dependency_call = fake_dependency_call
    response = client.get("/api/v1/orders", headers={"x-correlation-id": "test-correlation"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["correlation_id"] == "test-correlation"
    assert len(body["data"]) >= 1


def test_get_missing_order_returns_404() -> None:
    response = client.get("/api/v1/orders/999999")
    assert response.status_code == 404


def test_metrics_endpoint_exports_custom_metrics() -> None:
    client.get("/health/live")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "opsight_http_requests_total" in response.text


def test_dependency_failure_returns_503() -> None:
    response = client.get("/api/v1/simulate/dependency-failure")
    assert response.status_code == 503
    assert response.json()["error"] == "dependency_unavailable"
