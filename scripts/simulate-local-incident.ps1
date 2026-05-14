param(
  [ValidateSet("docker-memory", "container-crashloop", "ollama-latency", "wsl-cpu", "disk-pressure", "gpu-saturation")]
  [string]$Scenario = "container-crashloop",
  [int]$DurationSeconds = 120
)

$ErrorActionPreference = "Stop"

function Send-RcaFixture {
  param([string]$FixtureName)
  $env:AI_RCA_ALERT_FIXTURE = Join-Path $PSScriptRoot "..\apps\ai-rca\tests\fixtures\$FixtureName"
  python (Join-Path $PSScriptRoot "send-alertmanager-webhook.py")
}

switch ($Scenario) {
  "container-crashloop" {
    docker rm -f opsight-crashloop-demo 2>$null | Out-Null
    docker run -d --name opsight-crashloop-demo --label service=opsight-crashloop-demo --restart=always alpine:3.20 sh -c "echo opsight crash loop scenario; exit 42" | Out-Null
    Start-Sleep -Seconds 20
    Send-RcaFixture "alertmanager-docker-crashloop.json"
  }
  "docker-memory" {
    docker rm -f opsight-memory-pressure-demo 2>$null | Out-Null
    docker run -d --name opsight-memory-pressure-demo --label service=opsight-memory-pressure-demo --memory=128m alpine:3.20 sh -c "apk add --no-cache stress-ng >/dev/null && stress-ng --vm 1 --vm-bytes 110m --timeout ${DurationSeconds}s" | Out-Null
    Start-Sleep -Seconds 20
    Send-RcaFixture "alertmanager-docker-memory.json"
  }
  "ollama-latency" {
    $body = @{ model = $env:OLLAMA_MODEL; prompt = "Explain how GPU VRAM pressure can cause local LLM CPU fallback in one paragraph."; stream = $false } | ConvertTo-Json
    if (-not $env:OLLAMA_MODEL) { $body = @{ model = "llama3.2"; prompt = "Explain local LLM CPU fallback."; stream = $false } | ConvertTo-Json }
    try {
      Invoke-RestMethod -Method Post -Uri "http://localhost:9108/ollama/api/generate" -ContentType "application/json" -Body $body | Out-Null
    } catch {
      Write-Warning "Ollama proxy call failed; RCA fixture will still be sent for the incident workflow."
    }
    Send-RcaFixture "alertmanager-ollama-latency.json"
  }
  "wsl-cpu" {
    docker rm -f opsight-wsl-cpu-demo 2>$null | Out-Null
    docker run -d --name opsight-wsl-cpu-demo --label service=opsight-wsl-cpu-demo alpine:3.20 sh -c "apk add --no-cache stress-ng >/dev/null && stress-ng --cpu 2 --timeout ${DurationSeconds}s" | Out-Null
    Start-Sleep -Seconds 20
    Send-RcaFixture "alertmanager-wsl-pressure.json"
  }
  "disk-pressure" {
    docker rm -f opsight-disk-pressure-demo 2>$null | Out-Null
    docker run -d --name opsight-disk-pressure-demo --label service=opsight-disk-pressure-demo alpine:3.20 sh -c "dd if=/dev/zero of=/tmp/opsight-disk-pressure.bin bs=1M count=512; sleep ${DurationSeconds}" | Out-Null
    Start-Sleep -Seconds 20
    Send-RcaFixture "alertmanager-workstation-disk.json"
  }
  "gpu-saturation" {
    Send-RcaFixture "alertmanager-gpu-vram.json"
  }
}

Write-Host "Scenario submitted. Inspect Grafana dashboards, Prometheus alerts, Loki logs, and artifacts/ai-rca."
