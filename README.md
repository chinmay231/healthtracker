# Healthtracker / KARE

## What this repo is
This repository contains a local care tracker called KARE, built to manage medicine reminders, daily recovery tracking, and caretaker notifications without forcing data into the cloud.

The app is designed for:
- people tracking medication and activities,
- family members or caretakers who need to stay informed,
- small home care setups where a lightweight local server is enough.

It runs locally on your computer and can optionally send WhatsApp reminders through CallMeBot.

## Mission
The mission of this app is to make caregiving reliable and simple by:
- tracking medicines, doses, and schedules,
- tracking activity and wellbeing records,
- letting caretakers know when doses are due,
- keeping all data on your own machine,
- integrating with WhatsApp reminders only when you want them.

## Repo structure
- `v1/` – current stable snapshot of the tracker.
- `v2/` – working copy for the next round of features, including improved caretaker support and WhatsApp configuration.

Each folder is a self-contained app. Run `setup.sh` and `start.sh` from the version folder you want to use.

---

## Setup guide
Use the version you want:
- `cd v1`
- or `cd v2`

### 1. Install Python
The app uses Python 3.

#### Linux / macOS
- Install from your package manager or https://www.python.org/downloads/
- Verify with:
  ```bash
  python3 --version
  ```

#### Windows
- Install Python 3 from https://www.python.org/downloads/
- Make sure you select `Add Python to PATH` during install.
- Verify with:
  ```bat
  python --version
  ```

### 2. Run first-time setup
From inside `v1/` or `v2/`:

#### Linux / macOS
```bash
bash setup.sh
```

#### Windows
```bat
setup.bat
```

The setup script will:
- check that Python is installed,
- create a `.env` file if needed,
- prompt for your WhatsApp number,
- prompt for your CallMeBot API key,
- prompt for the local server port (default `8084`).

### 3. CallMeBot WhatsApp setup
If you want WhatsApp reminders, do this before entering the API key:

1. Visit: https://www.callmebot.com/blog/free-api-whatsapp-messages/
2. Save this phone number in WhatsApp: `+34 644 51 68 88`
   - Name it `CallMeBot`.
3. Open WhatsApp and send this exact message to CallMeBot:
   ```text
   I allow callmebot to send me messages
   ```
4. Wait for CallMeBot to send back your API key.
5. Enter that API key when prompted by `setup.sh` or paste it into `.env` later.

### 4. Start the tracker
From the same folder:

#### Linux / macOS
```bash
./start.sh
```

#### Windows
```bat
start.bat
```

Then open your browser at:
- `http://localhost:8084`
- or the port you set in `.env`

---

## What the app does
KARE lets you:
- create one or more patient profiles,
- add medicines with name, dose, frequency, and schedule,
- track when medicines are taken or missed,
- add recovery activities and mark them done,
- log daily wellbeing: pain, energy, sleep, water, mood,
- see a local history of medicine and activity events,
- optionally send WhatsApp reminders when doses are due.

All data is stored locally in the version folder:
- `tracker-data.json` – main tracker data,
- `.env` – WhatsApp and server settings,
- `whatsapp-config.json` – saved WhatsApp config and caretaker API keys.

---

## CallMeBot and caretaker setup
### Default WhatsApp notifications
The first `.env` setup asks for these settings:
- `WHATSAPP_PHONE` – your WhatsApp phone number in digits only,
- `CALLMEBOT_APIKEY` – the API key returned by CallMeBot,
- `PORT` – local server port (default `8084`).

When a medicine reminder triggers, the app can send WhatsApp messages using this default phone and API key.

### Caretaker WhatsApp keys
If you add caretakers in the app, each caretaker can also receive reminders.

In the web UI you can add:
- caretaker name,
- caretaker phone number with country code,
- caretaker CallMeBot API key.

Each caretaker needs their own WhatsApp permission if their phone number is different from the default number.

### How to add a caretaker
1. Start the app and open the browser interface.
2. Go to the `Caretakers` section.
3. Click `+ Add Caretaker`.
4. Enter:
   - `Caretaker name`,
   - `Caretaker phone` in country-code format (example: `919876543210`),
   - `CallMeBot API key` for that caretaker’s WhatsApp number.
5. Save.

If a caretaker has the same phone number as the default `.env` number, the default API key will also work there.
If the caretaker uses a different WhatsApp number, they must get their own CallMeBot API key and enter it in the UI.

---

## Running and adding data
### Add a patient
- Create a profile in the app,
- give the patient a name,
- optionally set caregiver/caretaker details.

### Add medicines
- Give the medicine a name,
- set dose information,
- select the schedule and times,
- enable reminders.

### Add activities
- Track recovery or daily tasks,
- set how often they repeat,
- mark them done or missed.

### Track progress
- Mark medicine doses as taken or missed,
- mark activities as completed,
- review the activity log and history.

---

## Backup and restore
- The app keeps data in `tracker-data.json`.
- Backup this file if you want to keep your history or move the tracker to another machine.

## Notes
- `v1/` is the stable release.
- `v2/` is the next version and includes the same basic flow plus improvements.
- Both versions are local apps. You can run only one version at a time on the same port.
- If you do not want WhatsApp notifications, you can still use the tracker fully offline.

## Troubleshooting
- If `python3` is not found, install Python 3 and ensure it is on your PATH.
- If the browser does not open, manually navigate to `http://localhost:8084`.
- If reminders do not send, confirm the CallMeBot API key is correct and the WhatsApp number is registered.

## Quick commands
```bash
cd v1
bash setup.sh
./start.sh
```
Or for v2:
```bash
cd v2
bash setup.sh
./start.sh
```

---

Enjoy using Healthtracker to keep care routines organized, local, and easy to manage.
