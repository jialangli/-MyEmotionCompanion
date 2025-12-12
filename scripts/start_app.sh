#!/usr/bin/env bash
set -e

# Start the Flask app with nohup and write PID to app.pid and gunicorn.pid
# Usage: ./scripts/start_app.sh

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$DIR/venv"
LOG="$DIR/flask_output.log"
PIDFILE="$DIR/app.pid"
GUNICORN_PIDFILE="$DIR/gunicorn.pid"

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

echo "Starting app from: $DIR"
echo "Log file: $LOG"

# Start in background with nohup and save PID
nohup python "$DIR/app.py" > "$LOG" 2>&1 &
PID=$!

echo "$PID" > "$PIDFILE"
echo "$PID" > "$GUNICORN_PIDFILE"

echo "Started app.py (PID: $PID)"
echo "PID written to: $PIDFILE and $GUNICORN_PIDFILE"
