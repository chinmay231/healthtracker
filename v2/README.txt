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

2. Send it this exact message:
   I allow callmebot to send me messages

3. You'll get a reply with your API key.

4. Open the .env file in this folder with Notepad.
5. Fill in:
   WHATSAPP_PHONE=919876543210     (your number, country code, no +)
   CALLMEBOT_APIKEY=paste-key-here

This sets the DEFAULT WhatsApp fallback for one number.

If you add extra caretakers with different phone numbers:
- open the app
- go to "Caretakers"
- add each caretaker's WhatsApp number
- add that caretaker's own CallMeBot API key

That's it. The server will check every minute and send WhatsApp messages.


STEP 3 — Run It
---------------
Windows: Double-click start.bat
Mac/Linux: Run ./start.sh in Terminal

This machine: http://localhost:8084
From other computers on the network: http://<your-laptop-ip>:8084


USING THE TRACKER
-----------------
1. Fill in your name and caregiver's name (optional)
2. Add medicines:
   - Name (e.g. "Aspirin")
   - Dosage (e.g. "500mg")
   - Reminder time (e.g. "09:00")
3. Add recovery activities (e.g. "Walk", "Stretching")
4. Each day:
   - Check off medicines you've taken
   - Check off activities you've done
   - Enter pain level, energy, sleep, water intake
5. Your history is saved automatically


OPENING ON YOUR PHONE
---------------------
Make sure your phone is on the SAME WiFi as your laptop.

1. Find your laptop's IP:
   Windows: Open Command Prompt → type ipconfig → look for "IPv4 Address"
   Mac: System Settings → WiFi → Details → IP Address

2. On your phone, open the browser and go to:
   http://<your-laptop-ip>:8084

iPhone: Tap Share → "Add to Home Screen" to make it look like an app


TROUBLESHOOTING
---------------
- "python is not recognized" → Python not installed or PATH not set.
  Reinstall Python, check the PATH box.

- No WhatsApp messages → Check the app's "WhatsApp Settings" or .env for
  the default phone and API key. Extra caretaker numbers need their own
  CallMeBot API keys too. Make sure each person sent the magic message first.

- Can't open from phone → Make sure both devices are on same WiFi.

- Data disappeared → Check that localhost:8084 is actually running
  (start.bat window should be open). Data is saved in your browser.


FILES
-----
index.html             The tracker (runs in your browser)
server.py             Serves the tracker + sends WhatsApp reminders
.env.example          Template for WhatsApp setup
.env                  Default WhatsApp fallback config (you create this)
whatsapp-config.json  Saved WhatsApp settings from inside the app
tracker-data.json     Your data backup (created automatically)
start.bat / start.sh  Double-click to launch
setup.bat / setup.sh  First-time setup


TIPS
----
- Export your record regularly (button in the app) as a backup
- You can import from a backup file to restore data
- All data stays in your browser — the server never sees it
  (except when sending reminders, it only reads medicine times)
- The tracker works without internet as long as the server is running
