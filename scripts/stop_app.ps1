# PowerShell equivalent of stop_app.sh

param (
    [string]$PidFile = "app.pid",
    [string]$GunicornPidFile = "gunicorn.pid"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Join-Path $ScriptDir ".."

# Stop the app using PID files
$PidPath = Join-Path $ProjectDir $PidFile
$GunicornPidPath = Join-Path $ProjectDir $GunicornPidFile

if (Test-Path $PidPath) {
    $Pid = Get-Content $PidPath | Select-String -Pattern "^\d+$" | ForEach-Object { $_.ToString() }
    if ($Pid) {
        Write-Host "Stopping app with PID: $Pid"
        Stop-Process -Id $Pid -Force -ErrorAction SilentlyContinue
        Remove-Item $PidPath
        Write-Host "Stopped app and removed PID file: $PidPath"
    } else {
        Write-Warning "No valid PID found in $PidPath"
    }
} else {
    Write-Warning "PID file not found: $PidPath"
}

if (Test-Path $GunicornPidPath) {
    $GunicornPid = Get-Content $GunicornPidPath | Select-String -Pattern "^\d+$" | ForEach-Object { $_.ToString() }
    if ($GunicornPid) {
        Write-Host "Stopping Gunicorn with PID: $GunicornPid"
        Stop-Process -Id $GunicornPid -Force -ErrorAction SilentlyContinue
        Remove-Item $GunicornPidPath
        Write-Host "Stopped Gunicorn and removed PID file: $GunicornPidPath"
    } else {
        Write-Warning "No valid PID found in $GunicornPidPath"
    }
} else {
    Write-Warning "Gunicorn PID file not found: $GunicornPidPath"
}