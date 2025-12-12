#!/usr/bin/env bash
set -e

# Stop the Flask app using PID files (app.pid and gunicorn.pid)
# Usage: ./scripts/stop_app.sh

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PIDFILE="$DIR/app.pid"
GUNICORN_PIDFILE="$DIR/gunicorn.pid"

kill_pid_file() {
  file="$1"
  if [ -f "$file" ]; then
    pid=$(cat "$file" 2>/dev/null || true)
    if [ -n "$pid" ]; then
      if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" && echo "Killed PID $pid from $file"
      else
        echo "PID $pid from $file is not running"
      fi
    fi
    rm -f "$file"
  else
    echo "PID file $file not found"
  fi
}

kill_pid_file "$PIDFILE"
kill_pid_file "$GUNICORN_PIDFILE"

echo "Stop script completed."
