param(
  [string]$LokiUrl = "http://localhost:3100/loki/api/v1/push",
  [string[]]$LogNames = @("Application", "System"),
  [int]$IntervalSeconds = 30,
  [int]$SinceMinutes = 10,
  [switch]$Once
)

$ErrorActionPreference = "Stop"
$seen = @{}

function Convert-Level {
  param([Nullable[int]]$Level)
  switch ($Level) {
    1 { "CRITICAL" }
    2 { "ERROR" }
    3 { "WARNING" }
    4 { "INFO" }
    5 { "DEBUG" }
    default { "UNKNOWN" }
  }
}

function Send-Events {
  $streams = @()
  $startTime = (Get-Date).AddMinutes(-1 * $SinceMinutes)

  foreach ($logName in $LogNames) {
    $events = Get-WinEvent -FilterHashtable @{LogName = $logName; StartTime = $startTime} -ErrorAction SilentlyContinue |
      Sort-Object TimeCreated |
      Select-Object -Last 100

    foreach ($event in $events) {
      $key = "$($event.LogName):$($event.RecordId)"
      if ($seen.ContainsKey($key)) {
        continue
      }
      $seen[$key] = $true

      $severity = Convert-Level $event.Level
      $timestampNs = ([DateTimeOffset]$event.TimeCreated).ToUnixTimeMilliseconds() * 1000000
      $line = @{
        timestamp = $event.TimeCreated.ToString("o")
        eventRecordID = [string]$event.RecordId
        channel = $event.LogName
        provider = $event.ProviderName
        event_id = [string]$event.Id
        severity = $severity
        computer = $event.MachineName
        message = ($event.Message -replace "`r?`n", " ")
      } | ConvertTo-Json -Compress -Depth 4

      $streams += @{
        stream = @{
          job = "windows-eventlog"
          eventlog = $event.LogName
          severity = $severity
          computer = $event.MachineName
          service_name = $event.ProviderName
          host_domain = "windows"
        }
        values = @(, @([string]$timestampNs, [string]$line))
      }
    }
  }

  if ($streams.Count -eq 0) {
    return 0
  }

  $payload = @{streams = $streams} | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Method Post -Uri $LokiUrl -ContentType "application/json" -Body $payload | Out-Null
  return $streams.Count
}

do {
  $count = Send-Events
  Write-Host "Forwarded $count Windows Event Log entries to Loki."
  if ($Once) {
    break
  }
  Start-Sleep -Seconds $IntervalSeconds
} while ($true)
