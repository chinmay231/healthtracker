#!/usr/bin/env bash
cd "$(dirname "$0")"
[ -f .env ] || bash setup.sh
python3 server.py
