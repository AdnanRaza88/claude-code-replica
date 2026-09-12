param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8787,
    [int]$TimeoutSec = 30
)

$ui = "http://${HostName}:${Port}/ui/"
$health = "http://${HostName}:${Port}/health"
$deadline = (Get-Date).AddSeconds($TimeoutSec)

while ((Get-Date) -lt $deadline) {
    try {
        $resp = Invoke-WebRequest -UseBasicParsing -Uri $health -TimeoutSec 2
        if ($resp.StatusCode -eq 200) {
            Start-Process $ui
            exit 0
        }
    } catch {
        Start-Sleep -Milliseconds 400
    }
}

Write-Host "Engine did not become healthy at $health"
Start-Process $ui
exit 2
