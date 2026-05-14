param(
  [string]$WindowsExporterVersion = "0.31.6",
  [switch]$SkipWindowsExporter,
  [switch]$SkipAlloyConfig
)

$ErrorActionPreference = "Stop"

function Assert-Administrator {
  $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = New-Object Security.Principal.WindowsPrincipal($identity)
  if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Run this script from an elevated PowerShell session."
  }
}

Assert-Administrator

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

if (-not $SkipWindowsExporter) {
  $msiName = "windows_exporter-$WindowsExporterVersion-amd64.msi"
  $downloadUrl = "https://github.com/prometheus-community/windows_exporter/releases/download/v$WindowsExporterVersion/$msiName"
  $downloadPath = Join-Path $env:TEMP $msiName

  Write-Host "Downloading $downloadUrl"
  Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath

  $collectors = "cpu,logical_disk,memory,net,os,process,service,system,tcp,physical_disk"
  Write-Host "Installing windows_exporter with collectors: $collectors"
  Start-Process msiexec.exe -Wait -ArgumentList @(
    "/i", "`"$downloadPath`"",
    "ENABLED_COLLECTORS=`"$collectors`"",
    "/qn"
  )

  $response = Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:9182/metrics"
  if ($response.StatusCode -ne 200) {
    throw "windows_exporter did not respond on http://localhost:9182/metrics"
  }
}

if (-not $SkipAlloyConfig) {
  $alloyConfig = Join-Path $repoRoot "observability\alloy\windows-host.alloy"
  $targetConfig = "C:\Program Files\GrafanaLabs\Alloy\config.alloy"
  if (Test-Path "C:\Program Files\GrafanaLabs\Alloy") {
    Copy-Item $alloyConfig $targetConfig -Force
    Restart-Service Alloy -ErrorAction Stop
    Write-Host "Restarted Grafana Alloy with OpsSight Windows Event Log config."
  } else {
    Write-Warning "Grafana Alloy is not installed at C:\Program Files\GrafanaLabs\Alloy. Install Alloy first, then rerun without -SkipAlloyConfig."
  }
}

$targetFile = Join-Path $repoRoot "observability\prometheus\file_sd\targets.local.json"
$targets = @(
  @{
    targets = @("host.docker.internal:9182")
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
  Write-Host "Prometheus reloaded optional Windows target discovery."
} catch {
  Write-Warning "Prometheus reload failed. Restart Prometheus with: docker compose restart prometheus"
}

Write-Host "Windows observability setup complete."
