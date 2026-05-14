from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import time
from typing import Any

import docker
import httpx
from docker.errors import DockerException
from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

APP_NAME = "opsight-local-runtime-exporter"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")
HOST_ROOT = os.getenv("HOST_ROOT", "/host-root")
logger = logging.getLogger(APP_NAME)

app = FastAPI(title=APP_NAME, version="1.0.0")

ollama_requests = Counter(
    "opsight_ollama_requests_total",
    "Ollama API requests proxied by OpsSight.",
    ["endpoint", "model", "status"],
)
ollama_failures = Counter(
    "opsight_ollama_failures_total",
    "Ollama API requests that failed or returned an error.",
    ["endpoint", "model", "reason"],
)
ollama_latency = Histogram(
    "opsight_ollama_request_duration_seconds",
    "Ollama request latency observed through the OpsSight instrumentation proxy.",
    ["endpoint", "model"],
    buckets=(0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120),
)
ollama_tokens = Counter(
    "opsight_ollama_tokens_total",
    "Ollama prompt and completion tokens observed in API responses.",
    ["model", "kind"],
)
ollama_token_throughput = Gauge(
    "opsight_ollama_tokens_per_second",
    "Most recent Ollama completion token throughput.",
    ["model"],
)
ollama_model_load = Gauge(
    "opsight_ollama_model_load_seconds",
    "Most recent Ollama model load duration reported by the runtime.",
    ["model"],
)
ollama_active_models = Gauge(
    "opsight_ollama_active_models",
    "Ollama models currently known to the local runtime.",
    ["model"],
)
ollama_up = Gauge("opsight_ollama_up", "Whether the configured Ollama endpoint is reachable.")

docker_container_state = Gauge(
    "opsight_docker_container_state",
    "Docker container state by name.",
    ["container", "image", "state"],
)
docker_container_health = Gauge(
    "opsight_docker_container_health",
    "Docker container health status. healthy=1, unhealthy=0, no healthcheck=-1.",
    ["container", "image"],
)
docker_container_restarts = Gauge(
    "opsight_docker_container_restart_count",
    "Docker restart count by container.",
    ["container", "image"],
)
docker_daemon_up = Gauge("opsight_docker_daemon_up", "Whether the Docker daemon is reachable.")

wsl_load = Gauge("opsight_wsl_load_average", "Linux/WSL load average.", ["window"])
wsl_memory = Gauge("opsight_wsl_memory_bytes", "Linux/WSL memory by type.", ["type"])
wsl_filesystem = Gauge("opsight_wsl_filesystem_bytes", "Mounted host filesystem usage.", ["mount", "type"])

gpu_up = Gauge("opsight_gpu_telemetry_available", "Whether GPU telemetry was available from nvidia-smi.")
gpu_utilization = Gauge("opsight_gpu_utilization_percent", "NVIDIA GPU utilization percent.", ["gpu", "name"])
gpu_memory = Gauge("opsight_gpu_memory_bytes", "NVIDIA GPU memory by type.", ["gpu", "name", "type"])
gpu_temperature = Gauge("opsight_gpu_temperature_celsius", "NVIDIA GPU temperature.", ["gpu", "name"])
gpu_power = Gauge("opsight_gpu_power_watts", "NVIDIA GPU power draw.", ["gpu", "name"])


@app.get("/health/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready", "service": APP_NAME}


@app.get("/metrics")
async def metrics() -> Response:
    collect_docker_metrics()
    await collect_ollama_inventory()
    collect_wsl_metrics()
    collect_gpu_metrics()
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/ollama/api/generate")
async def proxy_ollama_generate(request: Request) -> Response:
    payload = await request.json()
    model = str(payload.get("model") or "unknown")
    endpoint = "/api/generate"
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(f"{OLLAMA_BASE_URL}{endpoint}", json=payload)
        elapsed = time.perf_counter() - started
        ollama_latency.labels(endpoint, model).observe(elapsed)
        status = str(response.status_code)
        ollama_requests.labels(endpoint, model, status).inc()
        if response.status_code >= 400:
            ollama_failures.labels(endpoint, model, f"http_{status}").inc()
        _record_ollama_response(model, response)
        return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type"))
    except httpx.HTTPError as exc:
        elapsed = time.perf_counter() - started
        ollama_latency.labels(endpoint, model).observe(elapsed)
        ollama_requests.labels(endpoint, model, "exception").inc()
        ollama_failures.labels(endpoint, model, exc.__class__.__name__).inc()
        logger.warning("ollama proxy request failed", extra={"endpoint": endpoint, "model": model, "reason": exc.__class__.__name__})
        return Response(
            content=json.dumps({"error": f"Ollama proxy request failed: {exc.__class__.__name__}"}),
            status_code=502,
            media_type="application/json",
        )


def collect_docker_metrics() -> None:
    docker_container_state.clear()
    docker_container_health.clear()
    docker_container_restarts.clear()
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        docker_daemon_up.set(1)
    except DockerException:
        docker_daemon_up.set(0)
        return

    for container in containers:
        attrs = container.attrs
        name = container.name
        image = attrs.get("Config", {}).get("Image", "unknown")
        state = attrs.get("State", {})
        status = state.get("Status", "unknown")
        restart_count = attrs.get("RestartCount", 0)
        health = state.get("Health", {}).get("Status")
        docker_container_state.labels(name, image, status).set(1)
        docker_container_restarts.labels(name, image).set(restart_count)
        docker_container_health.labels(name, image).set(_health_value(health))


async def collect_ollama_inventory() -> None:
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
        response.raise_for_status()
        data = response.json()
        ollama_up.set(1)
        models = data.get("models", [])
        seen = set()
        for model in models:
            name = str(model.get("name") or model.get("model") or "unknown")
            seen.add(name)
            ollama_active_models.labels(name).set(1)
        if not seen:
            ollama_active_models.labels("none").set(0)
    except (httpx.HTTPError, ValueError) as exc:
        ollama_up.set(0)
        logger.debug("ollama inventory unavailable", extra={"reason": exc.__class__.__name__})


def collect_wsl_metrics() -> None:
    try:
        one, five, fifteen = _read_text("/proc/loadavg").split()[:3]
        wsl_load.labels("1m").set(float(one))
        wsl_load.labels("5m").set(float(five))
        wsl_load.labels("15m").set(float(fifteen))
    except (OSError, ValueError) as exc:
        logger.debug("wsl load average unavailable", extra={"reason": exc.__class__.__name__})

    meminfo = _parse_meminfo()
    for key in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree"):
        if key in meminfo:
            wsl_memory.labels(key).set(meminfo[key])

    if os.path.exists(HOST_ROOT):
        try:
            usage = shutil.disk_usage(HOST_ROOT)
            wsl_filesystem.labels(HOST_ROOT, "total").set(usage.total)
            wsl_filesystem.labels(HOST_ROOT, "used").set(usage.used)
            wsl_filesystem.labels(HOST_ROOT, "free").set(usage.free)
        except OSError as exc:
            logger.debug("host filesystem usage unavailable", extra={"reason": exc.__class__.__name__})


def collect_gpu_metrics() -> None:
    command = [
        "nvidia-smi",
        "--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=3)
    except (FileNotFoundError, subprocess.SubprocessError, OSError) as exc:
        gpu_up.set(0)
        logger.debug("gpu telemetry unavailable", extra={"reason": exc.__class__.__name__})
        return

    gpu_up.set(1)
    for row in result.stdout.splitlines():
        parts = [part.strip() for part in row.split(",")]
        if len(parts) != 7:
            continue
        index, name, util, mem_used, mem_total, temp, power = parts
        gpu_utilization.labels(index, name).set(_float(util))
        gpu_memory.labels(index, name, "used").set(_float(mem_used) * 1024 * 1024)
        gpu_memory.labels(index, name, "total").set(_float(mem_total) * 1024 * 1024)
        gpu_temperature.labels(index, name).set(_float(temp))
        gpu_power.labels(index, name).set(_float(power))


def _record_ollama_response(model: str, response: httpx.Response) -> None:
    if "application/json" not in response.headers.get("content-type", ""):
        return
    try:
        data: dict[str, Any] = response.json()
    except ValueError:
        return
    prompt_tokens = int(data.get("prompt_eval_count") or 0)
    completion_tokens = int(data.get("eval_count") or 0)
    eval_duration = int(data.get("eval_duration") or 0)
    load_duration = int(data.get("load_duration") or 0)
    if prompt_tokens:
        ollama_tokens.labels(model, "prompt").inc(prompt_tokens)
    if completion_tokens:
        ollama_tokens.labels(model, "completion").inc(completion_tokens)
    if eval_duration and completion_tokens:
        ollama_token_throughput.labels(model).set(completion_tokens / (eval_duration / 1_000_000_000))
    if load_duration:
        ollama_model_load.labels(model).set(load_duration / 1_000_000_000)


def _health_value(health: str | None) -> int:
    if health == "healthy":
        return 1
    if health == "unhealthy":
        return 0
    return -1


def _parse_meminfo() -> dict[str, float]:
    values: dict[str, float] = {}
    try:
        for line in _read_text("/proc/meminfo").splitlines():
            key, value = line.split(":", 1)
            values[key] = float(value.strip().split()[0]) * 1024
    except (OSError, ValueError) as exc:
        logger.debug("meminfo unavailable", extra={"reason": exc.__class__.__name__})
        return values
    return values


def _read_text(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return 0.0
