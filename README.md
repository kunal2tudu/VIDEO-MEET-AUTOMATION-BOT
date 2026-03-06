# 🤖 LPU Auto-Join Bot

Automatically logs into [myclass.lpu.in](https://myclass.lpu.in), finds your class on the schedule calendar, bypasses CodeTantra's anti-bot security, and joins the BigBlueButton video call in **Listen Only** mode — so your attendance is captured without you lifting a finger.

---

## ✨ What It Does

1. **Logs in** to `myclass.lpu.in` using your registration number and password.
2. **Navigates** to the class schedule and finds your subject by keyword.
3. **Extracts** the hidden Meeting ID from the calendar popup (without triggering CodeTantra's bot traps).
4. **Constructs** a direct deep-link to the BigBlueButton room, bypassing intermediate dashboard redirects.
5. **Waits** if the class hasn't started yet — refreshes every 60 seconds for up to 15 minutes.
6. **Pierces the iframe** — BigBlueButton runs inside a nested `<iframe>`, and the bot shifts context inside it to find the audio dialog.
7. **Clicks "Listen Only"** and holds the browser open for 2 hours to ensure full attendance is recorded.

> **How it bypasses CodeTantra security** → see [`how_bot_works.md`](./how_bot_works.md) for a full technical breakdown.

---

## 📋 Requirements

| Requirement | Version |
|---|---|
| Python | 3.8+ |
| Playwright | ≥ 1.41.0 |
| Chromium (via Playwright) | Latest |

> **Windows only** for the auto-scheduler. The bot itself works on any OS.

---

## ⚙️ Installation

### 1. Install Python dependencies

```bash
pip install playwright>=1.41.0
```

### 2. Download the Chromium browser

```bash
playwright install chromium
```

> This is a **required** one-time step. The browser binary is separate from the Python package.

---

## 🔧 Configuration

> **⚠️ IMPORTANT:** Before running anything, open each `.py` file and replace the placeholder values using `Ctrl+F`. The `keywords` file lists all the placeholders you need to replace.

| Placeholder | Replace With |
|---|---|
| `USERNAME-CODE` | Your LPU Registration Number |
| `PASSWORD-CODE` | Your LPU Password |
| `CLASS-CODE` | Your subject keyword (e.g. `INT241`, `CSE401`) |
| `MEETING-ID-CODE` | Your BBB Meeting ID (only needed for `click_listen.py` and `test_redirect.py`) |

Open `lpu_join_class.py` and update the top section:

```python
CREDENTIALS = {
    "reg_no": "USERNAME-CODE",    # ← Your LPU Registration Number
    "password": "PASSWORD-CODE",  # ← Your LPU Password
}

CLASS_KEYWORD = "CLASS-CODE"      # ← Subject keyword to find on the calendar
```

### Optional: Headless Mode

By default the bot runs in a **visible browser window** (`HEADFUL = True`). To run silently in the background:

```python
HEADFUL = False
```

---

## ▶️ Running the Bot

```bash
python lpu_join_class.py
```

The bot will print its progress step-by-step. Press **Ctrl+C** at any time to stop early.

---

## ⏰ Auto-Schedule (Windows Task Scheduler)

To make the bot run automatically at your class time, run the included PowerShell script **once** as Administrator:

1. Open `schedule_bot.ps1` and fill in the variables at the top:

```powershell
$TaskName     = 'LPU_ClassBot'                           # Name for the scheduled task
$BotDir       = 'C:\path\to\lpu_bot'                     # Folder where the bot lives
$BotScript    = 'C:\path\to\lpu_bot\lpu_join_class.py'   # Full path to the main script
$ScheduleTime = '6:00PM'                                  # Time to run (before class starts)
$ScheduleDays = @('Monday', 'Wednesday')                  # Days your class runs
```

> **Valid day names:** `Monday` `Tuesday` `Wednesday` `Thursday` `Friday` `Saturday` `Sunday`

2. Run it in PowerShell **as Administrator**:

```powershell
.\schedule_bot.ps1
```

This registers a Windows Scheduled Task that:
- Runs on your configured days and time
- Has a **2-hour execution limit**
- Only runs if a **network connection** is available
- Starts automatically even if you forgot

---

## 🛠️ Utility & Debug Scripts

These are helper scripts useful for diagnosing issues or running one-off tasks. Each requires the same `USERNAME-CODE` / `PASSWORD-CODE` / `CLASS-CODE` replacements.

### `click_listen.py` — Manual "Listen Only" Clicker
Use this if the main bot joined the class but got stuck at the audio dialog.
Replace `MEETING-ID-CODE` with your actual meeting ID (visible in the BBB URL), then run:
```bash
python click_listen.py
```

### `debug_login.py` — Login Debugger
Navigates to LPU, takes a screenshot of the login page, and dumps the page HTML. Useful if login is failing.
```bash
python debug_login.py
```
Outputs: `lpu_debug_login.png`, `login_dump.html`

### `debug_calendar.py` — Calendar Inspector
Logs in, goes to the class schedule, and prints all `/secure/tla/` links and the HTML of your class event. Useful if the bot can't find your class.
```bash
python debug_calendar.py
```

### `debug_redirect.py` — Redirect Chain Logger
Logs every HTTP request and response to show exactly where CodeTantra redirects you. Useful for understanding session/redirect issues.
```bash
python debug_redirect.py
```
Outputs: `debug_final_page.png`

### `test_calendar_popup.py` — Popup Link Tester
Clicks your class on the calendar and prints the `href` and `target` of the join link from the popup.
```bash
python test_calendar_popup.py
```

### `test_redirect.py` — Direct URL Tester
Logs into LPU, sets up the CodeTantra session, then tests navigating a direct `jnr.jsp` meeting URL to see where it lands.
Replace `MEETING-ID-CODE` with a real meeting ID, then:
```bash
python test_redirect.py
```
Outputs: `redirect_test.png`

---

## 📁 File Reference

| File | Purpose |
|---|---|
| `lpu_join_class.py` | Main bot script — start here |
| `schedule_bot.ps1` | Auto-scheduler for Windows Task Scheduler |
| `how_bot_works.md` | Deep-dive: how CodeTantra security is bypassed |
| `keywords` | ⚠️ List of all placeholders you must replace before running |
| `requirements.txt` | Python dependency list |
| `click_listen.py` | Utility: manually click "Listen Only" in an open session |
| `debug_login.py` | Debug: inspect the login page |
| `debug_calendar.py` | Debug: inspect calendar links |
| `debug_redirect.py` | Debug: trace the redirect chain |
| `test_calendar_popup.py` | Debug: inspect the class popup join link |
| `test_redirect.py` | Debug: test a direct meeting URL |

---

## ⚠️ Disclaimer

This bot is intended for **personal attendance automation** only. Use it responsibly and in accordance with your institution's policies.
