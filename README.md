# healthtracker
Healthtracker Workspace
=======================

Folders:
- v1/  Current stable snapshot of the tracker.
- v2/  Working copy for the next round of features.

Notes:
- Both folders are self-contained copies of the app.
- Start from inside each version folder using its own start script.
- Future feature work should happen in v2/.




KARE — Standalone Tracker
======================================

WHAT IS THIS
------------
A simple medicine and activity tracker that runs on your laptop.
- Add medicines with dosage and reminder time
- Mark when you've taken each one
- Track recovery activities
- Daily check-in: pain level, energy, sleep, water intake
- Everything stays on your device (no cloud, no sharing)
- Sends WhatsApp reminders when it's time to take medicine


STEP 1 — Install Python (one time, takes ~2 minutes)
-----------------------------------------------------
Go to: https://www.python.org/downloads/
Download the latest Python 3.x for your system.

IMPORTANT: During install, CHECK THE BOX:
  [x] Add Python to PATH
Then click "Install Now"

To verify it worked:
- Open Command Prompt (search "cmd" in Start menu)
- Type: python --version
- You should see: Python 3.x.x


STEP 2 — Set Up WhatsApp Reminders (optional, one time)
-------------------------------------------------------
If you want WhatsApp messages when medicines are due:

1. Save this number in WhatsApp contacts: +34 644 51 68 88
      (Name it "CallMeBot") 