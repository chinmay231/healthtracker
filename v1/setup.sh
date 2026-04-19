#!/usr/bin/env bash
# KARE — Linux/Mac first-time setup
set -e
cd "$(dirname "$0")"

echo ""
echo " KARE — Setup"
echo " =========================="
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo " Python 3 is not installed."
    echo " Mac:   brew install python3   or  https://www.python.org/downloads/"
    echo " Linux: sudo apt install python3"
    exit 1
fi
echo " Found: $(python3 --version)"
echo ""

# Create .env if missing
if [ -f .env ]; then
    echo " .env already exists — skipping."
else
    echo " Setting up WhatsApp reminders..."
    echo ""
    echo " Step 1: Save this number in WhatsApp contacts: +34 644 51 68 88"
    echo " Step 2: Send it this exact message:  I allow callmebot to send me messages"
    echo " Step 3: You will receive your API key. Enter it below."
    echo ""
    read -rp "  Your WhatsApp number (with country code, no + sign, e.g. 919876543210): " WA_PHONE
    read -rp "  Your CallMeBot API key (press Enter to skip for now): " WA_KEY
    read -rp "  Port (press Enter for default 8084): " WA_PORT
    WA_PORT="${WA_PORT:-8084}"
    cat > .env <<EOF
WHATSAPP_PHONE=${WA_PHONE}
CALLMEBOT_APIKEY=${WA_KEY}
PORT=${WA_PORT}
EOF
    echo ""
    echo " .env created."
fi

chmod +x start.sh 2>/dev/null || true

echo ""
echo " Setup complete!"
echo " Run ./start.sh to launch the tracker."
echo ""
