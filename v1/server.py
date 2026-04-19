#!/usr/bin/env python3
"""
KARE — standalone server.
- Serves index.html at http://localhost:PORT/
- Stores tracker data in tracker-data.json
- Background thread sends WhatsApp reminders via CallMeBot
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).parent
DATA_FILE  = BASE_DIR / "tracker-data.json"
NOTIF_FILE = BASE_DIR / "notified.json"
HTML_FILE  = BASE_DIR / "index.html"
ENV_FILE   = BASE_DIR / ".env"
WHATSAPP_CONFIG_FILE = BASE_DIR / "whatsapp-config.json"

def _load_env():
    env: dict[str, str] = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    # environment variables override .env
    for k in ("WHATSAPP_PHONE", "CALLMEBOT_APIKEY", "PORT"):
        if k in os.environ:
            env[k] = os.environ[k]
    return env

ENV = _load_env()
PORT = int(ENV.get("PORT", "8084"))

# ── Data helpers ──────────────────────────────────────────────────────────────

def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_data(data: dict) -> None:
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def load_notified() -> dict:
    if NOTIF_FILE.exists():
        try:
            return json.loads(NOTIF_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_notified(notified: dict) -> None:
    NOTIF_FILE.write_text(json.dumps(notified, indent=2), encoding="utf-8")

def load_whatsapp_config() -> dict:
    config = {
        "default_phone": ENV.get("WHATSAPP_PHONE", "").strip(),
        "default_api_key": ENV.get("CALLMEBOT_APIKEY", "").strip(),
        "caretaker_keys": {},
    }
    if WHATSAPP_CONFIG_FILE.exists():
        try:
            raw = json.loads(WHATSAPP_CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                default_phone = raw.get("default_phone")
                default_api_key = raw.get("default_api_key")
                caretaker_keys = raw.get("caretaker_keys")
                if isinstance(default_phone, str):
                    config["default_phone"] = default_phone.strip()
                if isinstance(default_api_key, str):
                    config["default_api_key"] = default_api_key.strip()
                if isinstance(caretaker_keys, dict):
                    config["caretaker_keys"] = {
                        str(k): str(v).strip()
                        for k, v in caretaker_keys.items()
                        if str(v).strip()
                    }
        except Exception:
            pass
    for env_name, key in (
        ("WHATSAPP_PHONE", "default_phone"),
        ("CALLMEBOT_APIKEY", "default_api_key"),
    ):
        if env_name in os.environ:
            config[key] = os.environ[env_name].strip()
    return config

def save_whatsapp_config(config: dict) -> dict:
    caretaker_keys = config.get("caretaker_keys") if isinstance(config, dict) else {}
    cleaned = {
        "default_phone": _normalize_phone((config or {}).get("default_phone", "")),
        "default_api_key": str((config or {}).get("default_api_key", "")).strip(),
        "caretaker_keys": {},
    }
    if isinstance(caretaker_keys, dict):
        cleaned["caretaker_keys"] = {
            str(k): str(v).strip()
            for k, v in caretaker_keys.items()
            if str(v).strip()
        }
    WHATSAPP_CONFIG_FILE.write_text(json.dumps(cleaned, indent=2), encoding="utf-8")
    return cleaned

# ── WhatsApp sender ───────────────────────────────────────────────────────────

def _normalize_phone(raw: str) -> str:
    return "".join(ch for ch in str(raw or "") if ch.isdigit())

def _build_whatsapp_targets(data: dict, config: dict) -> list[dict]:
    default_phone = _normalize_phone(config.get("default_phone", ""))
    default_api_key = str(config.get("default_api_key", "")).strip()
    caretaker_keys = config.get("caretaker_keys") if isinstance(config.get("caretaker_keys"), dict) else {}
    targets: list[dict] = []
    seen_phones: set[str] = set()

    for caretaker in data.get("caretakers") or []:
        phone = _normalize_phone(caretaker.get("phone", ""))
        if not phone or phone in seen_phones:
            continue
        caretaker_id = str(caretaker.get("id") or "")
        api_key = ""
        if caretaker_id:
            api_key = str(caretaker_keys.get(caretaker_id, "")).strip()
        if not api_key:
            # Backward-compatible fallback if older data already stored the key inline.
            api_key = str(caretaker.get("callmebotApiKey", "")).strip()
        if not api_key and phone == default_phone:
            api_key = default_api_key
        if api_key:
            targets.append({
                "name": caretaker.get("name") or phone,
                "phone": phone,
                "api_key": api_key,
            })
            seen_phones.add(phone)
        else:
            name = caretaker.get("name") or phone
            print(f"[reminder] Skipping {name} ({phone}) — missing CallMeBot API key.")

    if not targets and default_phone and default_api_key:
        targets.append({
            "name": "Default WhatsApp",
            "phone": default_phone,
            "api_key": default_api_key,
        })

    return targets

def send_whatsapp_to(message: str, phone: str, api_key: str) -> bool:
    """Send WhatsApp message to a specific phone number."""
    if not phone or not api_key:
        print(f"[reminder] WhatsApp not configured for {phone} — would have sent: {message}")
        return False
    try:
        params = urllib.parse.urlencode({
            "phone":  phone,
            "text":   message,
            "apikey": api_key,
        })
        url = f"https://api.callmebot.com/whatsapp.php?{params}"
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            ok = resp.status == 200 and "message queued" in body.lower()
            if ok:
                print(f"[reminder] WhatsApp sent to {phone}: {message}")
            else:
                print(f"[reminder] CallMeBot returned {resp.status}: {body[:120]}")
            return ok
    except Exception as exc:
        print(f"[reminder] WhatsApp send to {phone} failed: {exc}")
        return False

def send_whatsapp(message: str) -> bool:
    """Send WhatsApp message using default configured number."""
    config = load_whatsapp_config()
    return send_whatsapp_to(
        message,
        _normalize_phone(config.get("default_phone", "")),
        str(config.get("default_api_key", "")).strip(),
    )

# ── Reminder logic ────────────────────────────────────────────────────────────

def _parse_am_pm_time(raw: str) -> str | None:
    """Convert '09:00 AM' or '14:30' → 'HH:MM' (24h). Returns None on failure."""
    raw = (raw or "").strip()
    import re
    m = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)?$", raw, re.IGNORECASE)
    if not m:
        return None
    hour, minute, period = int(m.group(1)), int(m.group(2)), (m.group(3) or "").upper()
    if period == "PM" and hour != 12:
        hour += 12
    elif period == "AM" and hour == 12:
        hour = 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return f"{hour:02d}:{minute:02d}"

def check_reminders() -> None:
    """Check due medicines/activities and send WhatsApp if needed."""
    data = load_data()
    if not data:
        return
    whatsapp_config = load_whatsapp_config()

    now    = datetime.now().astimezone()
    today  = now.strftime("%Y-%m-%d")
    hhmm   = now.strftime("%H:%M")

    notified = load_notified()
    # Purge old entries (> 2 days)
    cutoff = (now - timedelta(days=2)).strftime("%Y-%m-%d")
    notified = {k: v for k, v in notified.items() if v >= cutoff}

    changed = False

    targets = _build_whatsapp_targets(data, whatsapp_config)
    if not targets:
        return

    meds = data.get("medicines") or []
    for med in meds:
        if not med.get("active", True):
            continue
        name   = med.get("name", "Medicine")
        dose   = med.get("dose", "")
        times  = med.get("times") or []
        for raw_time in times:
            slot_24 = _parse_am_pm_time(raw_time)
            if not slot_24:
                continue
            if slot_24 != hhmm:
                continue
            key = f"{med.get('id', name)}::{today}::{slot_24}"
            if key in notified:
                continue
            label = f"💊 Time for {name}"
            if dose:
                label += f" ({dose})"
            label += f" at {raw_time}"
            for target in targets:
                send_whatsapp_to(label, target["phone"], target["api_key"])
            notified[key] = today
            changed = True

    activities = data.get("activities") or []
    for act in activities:
        if not act.get("active", True):
            continue
        name       = act.get("name", "Activity")
        remind_at  = _parse_am_pm_time(act.get("reminder_time") or act.get("time") or "")
        if not remind_at or remind_at != hhmm:
            continue
        key = f"{act.get('id', name)}::{today}::{remind_at}"
        if key in notified:
            continue
        for target in targets:
            send_whatsapp_to(f"🏃 Reminder: {name}", target["phone"], target["api_key"])
        notified[key] = today
        changed = True

    if changed:
        save_notified(notified)

def _reminder_loop() -> None:
    print("[reminder] Background checker started (checks every 60 s)")
    while True:
        try:
            check_reminders()
        except Exception as exc:
            print(f"[reminder] Error: {exc}")
        time.sleep(60)

# ── HTTP handler ──────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence default access log

    def _send(self, code: int, content_type: str, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            body = HTML_FILE.read_bytes()
            self._send(200, "text/html; charset=utf-8", body)
        elif path == "/api/data":
            body = json.dumps(load_data()).encode()
            self._send(200, "application/json", body)
        elif path == "/api/whatsapp-config":
            body = json.dumps(load_whatsapp_config()).encode()
            self._send(200, "application/json", body)
        else:
            self._send(404, "text/plain", b"Not found")

    def do_POST(self):
        path = self.path.split("?")[0]
        if path == "/api/data":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                data = json.loads(raw)
                save_data(data)
                self._send(200, "application/json", b'{"ok":true}')
            except Exception as exc:
                self._send(400, "application/json", json.dumps({"error": str(exc)}).encode())
        elif path == "/api/whatsapp-config":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                data = json.loads(raw or b"{}")
                if not isinstance(data, dict):
                    raise ValueError("Expected a JSON object")
                body = json.dumps(save_whatsapp_config(data)).encode()
                self._send(200, "application/json", body)
            except Exception as exc:
                self._send(400, "application/json", json.dumps({"error": str(exc)}).encode())
        else:
            self._send(404, "text/plain", b"Not found")

# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    if not HTML_FILE.exists():
        print("ERROR: index.html not found next to server.py")
        sys.exit(1)

    whatsapp_config = load_whatsapp_config()
    if not whatsapp_config.get("default_phone") or not whatsapp_config.get("default_api_key"):
        print("WARNING: Default WhatsApp fallback is not fully configured.")
        print("         Set it in the app's WhatsApp Settings or edit .env.")
        print("         Caretakers with their own CallMeBot API keys can still receive reminders.\n")

    threading.Thread(target=_reminder_loop, daemon=True).start()

    server = HTTPServer(("0.0.0.0", PORT), Handler)
    local_url  = f"http://localhost:{PORT}"
    try:
        import socket
        lan_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        lan_ip = "your-laptop-ip"

    print(f"KARE running on 0.0.0.0:{PORT}")
    print(f"  Local:  {local_url}")
    print(f"  Network (same WiFi/LAN): http://{lan_ip}:{PORT}")
    print(f"  Remote: http://<your-public-ip>:{PORT}")
    print(f"\nPress Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
