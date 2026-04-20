#!/usr/bin/env bash
# Run KARE as a background service that survives terminal close.
# Logs go to kare.log in the same directory.
# Usage:
#   ./start_service.sh          — start in background
#   ./start_service.sh stop     — stop the running instance
#   ./start_service.sh status   — show whether it's running

cd "$(dirname "$0")"
PIDFILE="kare.pid"
LOGFILE="kare.log"

case "${1:-start}" in
  start)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      echo "KARE is already running (PID $(cat "$PIDFILE")). Use: ./start_service.sh stop"
      exit 1
    fi
    [ -f .env ] || bash setup.sh
    nohup python3 server.py >> "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    echo "KARE started (PID $!). Logs: $LOGFILE"
    ;;
  stop)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      kill "$(cat "$PIDFILE")" && rm -f "$PIDFILE"
      echo "KARE stopped."
    else
      echo "KARE is not running."
    fi
    ;;
  status)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      echo "KARE is running (PID $(cat "$PIDFILE"))."
    else
      echo "KARE is not running."
    fi
    ;;
  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
