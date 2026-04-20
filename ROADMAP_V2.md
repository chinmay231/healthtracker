# KARE Health Tracker — V2 Roadmap

> **Goal:** Evolve KARE from a single-machine personal tool into a lightweight cloud-connected health platform with real auth, persistent storage, and multi-role support.

---

## Core Principles for V2

- **User choice first** — local storage OR cloud, never forced.
- **Role-aware** — a single account can be both Patient and Caretaker.
- **Privacy by default** — data never leaves the user's chosen storage without explicit action.
- **Zero friction onboarding** — sign in with Google, done. No manual setup.

---

## Milestones

---

### Milestone 1 — SQLite Backend (replaces flat JSON)

**Why:** `tracker-data.json` doesn't scale, can't be queried, and is fragile.

**What to build:**
- Replace `tracker-data.json` with a local SQLite database (`kare.db`)
- Schema:
  - `users` — id, name, role (patient / caretaker / both), created_at
  - `health_logs` — id, user_id, metric, value, unit, logged_at
  - `reminders` — id, user_id, message, schedule_cron, last_sent, active
  - `caretaker_links` — caretaker_user_id, patient_user_id, permissions, linked_at
- REST API layer (Flask or FastAPI) that wraps the DB — replaces direct JSON reads
- Backward-compat migration: on first run, import existing `tracker-data.json` into SQLite

**Outcome:** Persistent, queryable, crash-safe storage.

---

### Milestone 2 — Google OAuth Login

**Why:** No auth = anyone with the URL sees everything. Google OAuth = zero password UX + proven identity.

**What to build:**
- Integrate `google-auth` / `authlib` OAuth2 flow
- Endpoints:
  - `GET /auth/google` — redirect to Google consent screen
  - `GET /auth/callback` — handle token, create/fetch user in DB, set session cookie
  - `GET /auth/logout` — clear session
- Session management: server-side sessions (Flask-Session or signed JWT)
- UI: "Sign in with Google" button on landing page; replace current open-access dashboard

**Outcome:** Only authenticated users reach their own data.

---

### Milestone 3 — Role Onboarding

**Why:** KARE is already built around the caretaker concept — the DB and auth now make it real.

**What to build:**
- Single onboarding question post-login: **"Who are you tracking health for?"**
  - **Myself** — self-care, tracking my own health
  - **Someone else** — I'm looking after another person (caretaker)
  - **Both** — I track my own health and also look after someone else
- Role stored against the user account; can be updated in settings later
- Separate dashboards vs. unified view: **TBD** — will decide once M1 + M2 are running and we can see what feels right in practice
- Invitation flow (caretaker → patient link): design deferred to M3 build sprint
- Permission levels in `caretaker_links`: `read_only` | `read_write` | `manage_reminders` — schema is in M1, UI design is M3

**Open:** Dashboard layout (separate tabs vs. toggle vs. unified) — decide during M3 sprint.

**Outcome:** Role-aware accounts with clear onboarding intent; dashboard design stays flexible until we build it.

---

### Milestone 4 — Cloud Storage Choice

**Why:** Local SQLite is great for privacy. Google Drive is great for "access anywhere".

**What to build:**

#### Option A — Local only (default, already done by M1)
No additional work. Data stays on the machine.

#### Option B — Google Drive sync
- Use Google Drive API (same OAuth token from M2, request `drive.appdata` scope)
- Store `kare.db` in the app's private Drive folder (`appDataFolder`) — invisible to the user in Drive UI, only readable by KARE
- Sync strategy: on login, pull latest DB snapshot; on any write, push delta or full snapshot
- Conflict resolution: last-write-wins for now (v2 scope)

#### Option C — Self-hosted / custom endpoint (stretch)
- User provides an S3-compatible URL + credentials
- KARE syncs the SQLite file there

**User-facing setting:** "Where should your data live?" → Local / Google Drive (radio, set at onboarding, changeable in settings)

**Outcome:** Truly access-anywhere for users who opt in, full offline for those who don't.

---

### Milestone 5 — Reliability & Production Hardening

**Why:** The v1 gaps that affect anyone running this beyond a laptop demo.

**What to build:**
- `systemd` unit file for auto-restart on boot
- Proper secret management: move `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `CALLMEBOT_KEY` out of JSON into env vars / `.env`
- Reminder engine: replace 60s polling with APScheduler cron jobs (eliminate ±60s drift)
- WhatsApp send: add retry with exponential backoff, dead-letter logging
- Basic rate limiting on API endpoints (Flask-Limiter)
- Health endpoint: `GET /healthz` returns DB status + scheduler status

**Outcome:** Something you can actually leave running and trust.

---

## What's NOT in V2

- Native mobile app (PWA is good enough for now)
- Multi-tenancy / SaaS billing
- End-to-end encryption of Drive data (V3 candidate)
- HIPAA/GDPR compliance hardening (V3 candidate)

---

## Suggested Build Order

```
M1 (SQLite) → M2 (Google OAuth) → M3 (Roles) → M5 (Hardening) → M4 (Cloud Storage)
```

M4 depends on M2 (OAuth token) and M1 (the file to sync). M5 can run in parallel with M3 and M4.

---

## Open Questions

1. Should the Google Drive sync be automatic (background) or manual (user hits "Sync now")?
2. For the Caretaker invite flow — link-based or email-based?
3. Do both Patient and Caretaker need separate notification channels, or share one WhatsApp number per account?
4. Target deployment: still self-hosted (user's machine), or move toward a hosted option for V2?

---

## V2 Summary

- M1: Replace brittle `tracker-data.json` with a local SQLite backend and REST API, plus one-time migration support.
- M2: Add Google OAuth authentication so users sign in and only access their own data.
- M3: Build role-aware onboarding for Patient / Caretaker / Both, with caretaker links and permissions.
- M4: Offer a cloud storage choice: local by default, optional Google Drive sync for cross-device access.
- M5: Harden the platform with systemd support, env-based secrets, scheduler improvements, retry logic, rate limiting, and health checks.

## Future Additions

- Caretaker invite flow (link-based or email-based) and shared patient access controls.
- Option for manual vs. automatic sync and better conflict resolution for cloud storage.
- Separate notification channels per account and richer reminder delivery beyond WhatsApp.
- PWA/mobile UX improvements for better phone use and onboarding.
- V3 candidates: encrypted Drive storage, HIPAA/GDPR compliance hardening, and optional hosted SaaS deployment.

---

## V2 Execution Plan

### Phase 1 — Design and local storage preparation
- Define the SQLite schema for `users`, `health_logs`, `daily_vitals`, `reminders`, and `caretaker_links`.
- Design the REST API contract for reading/writing app data and fetching daily vitals.
- Plan a backward compatibility migration path from `tracker-data.json` to `kare.db`.
- Document expected data shape, query patterns, and export formats.

### Phase 2 — Build the SQLite backend and migration
- Add SQLite support to the server stack.
- Implement database initialization and schema creation on first run.
- Write a migration script that reads existing `tracker-data.json`, transforms records, and inserts them into the new DB.
- Preserve user settings and WhatsApp configuration during migration.

### Phase 3 — Connect the UI and API
- Update the front-end to use the new REST endpoints instead of direct JSON file handling.
- Implement daily vitals and metric logging using table-backed records.
- Add export/import helpers for JSON and optional CSV reports.

### Phase 4 — Validation and hardening
- Build tests or manual checks for migration correctness and data integrity.
- Verify support for long-running storage growth: many dates, many reminders, many logs.
- Add backups or automatic DB snapshots before migration.
- Ensure a single `kare.db` file is the main storage artifact.

### Phase 5 — Future storage UX
- Add a setting for storage preference: Local only or Google Drive sync.
- Keep local SQLite as the primary source of truth; sync only as an optional layer.
- Use CSV/JSON exports for reporting, not as the main storage engine.

---

*Roadmap created: 2026-04-19 | Status: Planning*
