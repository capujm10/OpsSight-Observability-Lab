param(
  [string]$WindowsExporterVersion = "0.31.6",
  [int]$Port = 9182
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$toolsDir = Join-Path $repoRoot ".opsight-tools\windows_exporter"
New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null

$exeName = "windows_exporter-$WindowsExporterVersion-amd64.exe"
$exePath = Join-Path $toolsDir $exeName

if (-not (Test-Path $exePath)) {
  $downloadUrl = "https://github.com/prometheus-community/windows_exporter/releases/download/v$WindowsExporterVersion/$exeName"
  Write-Host "Downloading $downloadUrl"
  Invoke-WebRequest -Uri $downloadUrl -OutFile $exePath
}

$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $existing) {
  $collectors = "cpu,logical_disk,memory,net,os,process,service,system,tcp,physical_disk"
  Start-Process -FilePath $exePath -WindowStyle Hidden -ArgumentList @(
    "--web.listen-address=:$Port",
    "--collectors.enabled=$collectors"
  )
  Start-Sleep -Seconds 3
}

$response = Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:$Port/metrics" -TimeoutSec 10
if ($response.StatusCode -ne 200) {
  throw "windows_exporter did not respond on http://localhost:$Port/metrics"
}

$targetFile = Join-Path $repoRoot "observability\prometheus\file_sd\targets.local.json"
$targets = @(
  @{
    targets = @("host.docker.internal:$Port")
    labels = @{
      job = "windows-exporter"
      service = "windows-host"
      host_domain = "windows"
    }
  }
)
$json = ConvertTo-Json -InputObject @($targets) -Depth 5
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($targetFile, $json, $utf8NoBom)

try {
  Invoke-RestMethod -Method Post -Uri "http://localhost:9090/-/reload" | Out-Null
} catch {
  Write-Warning "Prometheus reload failed. Restart Prometheus with: docker compose restart prometheus"
}

Write-Host "windows_exporter is running at http://localhost:$Port/metrics."
