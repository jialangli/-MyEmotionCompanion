# PowerShell equivalent of start_app.sh

param (
    [string]$LogFile = "flask_output.log",
    [string]$PidFile = "app.pid",
    [string]$GunicornPidFile = "gunicorn.pid"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Join-Path $ScriptDir ".."
$VenvDir = Join-Path $ProjectDir "venv"
$LogsDir = Join-Path $ProjectDir "logs"

# Ensure logs directory exists
if (-Not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}

# Archive old log if exists
$LogPath = Join-Path $ProjectDir $LogFile
if (Test-Path $LogPath) {
    $ArchiveLog = Join-Path $LogsDir ("flask_output_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")
    Move-Item -Path $LogPath -Destination $ArchiveLog
    Write-Host "Archived old log to: $ArchiveLog"
}

# Activate virtual environment
if (Test-Path "$VenvDir\Scripts\Activate.ps1") {
    . "$VenvDir\Scripts\Activate.ps1"
} else {
    Write-Error "Virtual environment not found. Please set up the venv."
    exit 1
}

# Start the app
$StartTime = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
$Cmd = "python `"$ProjectDir\app.py`""
Write-Host "Starting app with command: $Cmd"

Start-Process -FilePath "python" -ArgumentList "`"$ProjectDir\app.py`"" -RedirectStandardOutput $LogPath -RedirectStandardError $LogPath -NoNewWindow -PassThru | ForEach-Object {
    $_.Id | Out-File -FilePath (Join-Path $ProjectDir $PidFile) -Encoding ASCII
    $_.Id | Out-File -FilePath (Join-Path $ProjectDir $GunicornPidFile) -Encoding ASCII
    Add-Content -Path (Join-Path $ProjectDir $PidFile) -Value "Command: $Cmd"
    Add-Content -Path (Join-Path $ProjectDir $PidFile) -Value "Start Time: $StartTime"
    Add-Content -Path (Join-Path $ProjectDir $GunicornPidFile) -Value "Command: $Cmd"
    Add-Content -Path (Join-Path $ProjectDir $GunicornPidFile) -Value "Start Time: $StartTime"
    Write-Host "Started app.py (PID: $_.Id)"
}