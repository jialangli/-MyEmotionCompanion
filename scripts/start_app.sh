#!/usr/bin/env bash
set -e

# Start the Flask app with nohup and write detailed metadata to app.pid and gunicorn.pid
# Usage: ./scripts/start_app.sh

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$DIR/venv"
LOG="$DIR/flask_output.log"
ARCHIVE_LOG="$DIR/logs/flask_output_$(date +%Y%m%d_%H%M%S).log"
PIDFILE="$DIR/app.pid"
GUNICORN_PIDFILE="$DIR/gunicorn.pid"

# Ensure logs directory exists
mkdir -p "$DIR/logs"

# Archive old log if exists
if [ -f "$LOG" ]; then
  mv "$LOG" "$ARCHIVE_LOG"
  echo "Archived old log to: $ARCHIVE_LOG"
fi

# Try to activate common venv locations (Windows Git Bash or Unix)
if [ -f "$VENV/Scripts/activate" ]; then
  # Windows venv layout
  # shellcheck source=/dev/null
  source "$VENV/Scripts/activate"
elif [ -f "$VENV/bin/activate" ]; then
  # Unix venv layout
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
fi

START_TIME=$(date +%Y-%m-%dT%H:%M:%S%z)
CMD="python \"$DIR/app.py\""

echo "Starting app from: $DIR"
echo "Log file: $LOG"

# Start in background with nohup and save PID
nohup $CMD > "$LOG" 2>&1 &
PID=$!

# Write detailed metadata to PID files
echo "PID: $PID" > "$PIDFILE"
echo "Command: $CMD" >> "$PIDFILE"
echo "Start Time: $START_TIME" >> "$PIDFILE"

# Duplicate metadata for gunicorn.pid
echo "PID: $PID" > "$GUNICORN_PIDFILE"
echo "Command: $CMD" >> "$GUNICORN_PIDFILE"
echo "Start Time: $START_TIME" >> "$GUNICORN_PIDFILE"

echo "Started app.py (PID: $PID)"
echo "PID and metadata written to: $PIDFILE and $GUNICORN_PIDFILE"
