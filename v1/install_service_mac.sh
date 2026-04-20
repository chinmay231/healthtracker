#!/usr/bin/env bash
# Installs KARE as a macOS LaunchAgent (starts on login, auto-restarts).
# Usage: ./install_service_mac.sh
#   Uninstall: launchctl unload ~/Library/LaunchAgents/com.kare.healthtracker.plist

set -e
cd "$(dirname "$0")"

KARE_DIR="$(pwd)"
PLIST_SRC="$KARE_DIR/com.kare.healthtracker.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.kare.healthtracker.plist"

# Patch KARE_DIR into the plist
sed "s|KARE_DIR|$KARE_DIR|g" "$PLIST_SRC" > "$PLIST_DEST"

launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"

echo ""
echo "KARE installed as a macOS LaunchAgent."
echo "  It will start automatically on login and restart if it crashes."
echo "  Logs: $KARE_DIR/kare.log"
echo ""
echo "To stop & remove:"
echo "  launchctl unload $PLIST_DEST && rm $PLIST_DEST"
echo ""
