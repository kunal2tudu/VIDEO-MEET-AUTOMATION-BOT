# How the LPU Auto-Join Bot Works

This document explains the complete automated flow of the LPU Auto-Join bot, the anti-bot security measures CodeTantra employs, and how the script successfully bypasses them to join the active BigBlueButton class.

---

## Phase 1: The Basics (How the Bot Controls the Browser)
To automate the browser, we use a library called **Playwright**. By default, websites can easily detect "dumb" bots because they usually look like simple scripts. Playwright is powerful because it launches a real, actual Google Chrome browser engine under the hood. 

In the code, you'll see this part:
```python
browser = await p.chromium.launch(...)
context = await browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
```
This tells the bot to pretend it is a normal human running Chrome on Windows. CodeTantra just sees a regular user logging in. It uses your real registration number and password to log in and click the "View Class" button. This part is standard web automation.

---

## Phase 2: The CodeTantra Calendar Trap
Once the bot reaches the class schedule, it scans the page looking for a block of text containing `CLASS-CODE` (your class). When it finds it, it clicks it, and a small popup appears with the class details.

This is where the first huge problem happens: **The TargetClosedError**.
Normally, when a user clicks a link on a calendar, it either opens in the same tab or a new tab. In Playwright, if you expect a new tab but the link redirects in the same tab, Playwright panics and crashes (`TargetClosedError`). CodeTantra's calendar uses heavy JavaScript to handle that click. When the bot tried to click the calendar link using Playwright's click actions, CodeTantra detected the automated click interception, stripped away the bot's login cookies (the "session"), and threw the bot back to the `m.jsp` (dashboard) page.

**The Solution:**
Instead of letting the bot click the calendar link and triggering CodeTantra's security trap, the bot *reads the underlying HTML code* of the popup instead of clicking it:
```python
# Look at the link, don't click it! Extract the URL instead.
raw_url = await join_link.get_attribute("href")
```

---

## Phase 3: The Dashboard Redirect Loop
Even after extracting the URL from the calendar popup, we hit a second wall. 

The URL in the calendar popup looks something like this:
`/secure/tla/mi.jsp?s=m&m=f63cf8a6-8e01-36a9-a770-72eded2eaa4f`

When the bot tried to navigate to that URL directly, CodeTantra servers detected that the request didn't originate from a valid UI button click on the `mi.jsp` page, and immediately kicked the bot back to the `m.jsp` dashboard. The bot was stuck in a redirect loop.

**The Solution:**
By analyzing the CodeTantra URL structure, we can see the `m=f63cf...` part in the URL above. That is the **encrypted unique Meeting ID** for that specific class on that specific day. 
Instead of going through CodeTantra's front-end UI loop that requires button clicks, the bot mathematically extracts that Meeting ID and forcefully constructs the final, deep BigBlueButton generic room link (`jnr.jsp`), bypassing the intermediate pages entirely:

```python
# Extract the unique meeting ID
meeting_id = params["m"][0]

# Force the browser directly into the video room URL
dynamic_url = f"https://lovelyprofessionaluniversity.codetantra.com/secure/tla/jnr.jsp?m={meeting_id}"
await meeting_page.goto(dynamic_url)
```
This completely bypasses CodeTantra's security checks and drops the bot straight into the active class.

---

## Phase 4: The Iframe Mystery (Why it couldn't find "Listen Only")
Once the bot successfully bypassed the dashboard and got into the `jnr.jsp` room, it failed to click the "Listen only" button. The HTML selector `button[aria-label='Listen only']` was correct, but the bot kept reporting that the button was not found.

The reason is that CodeTantra puts the entire BigBlueButton video call **inside an `<iframe>`**. 
An iframe is a separate HTML document embedded inside the main document. When Playwright searches a page for an element, it only searches the "parent" document. It cannot see elements inside the iframe unless explicitly told to look there.

**The Solution:**
The bot detects if an iframe exists. If it does, the bot shifts its entire operational context *inside* that iframe:
```python
# Are we inside an iframe?
has_frame = await bbb_page.locator("iframe#frame").count() > 0

if has_frame:
    # Yes! Shift the bot's vision inside the iframe window
    target_context = bbb_page.frame_locator("iframe#frame")
```
Once the bot's context is shifted inside the iframe, the `Listen only` button becomes visible within the DOM, and it clicks it successfully!

---

## Summary of the Final Flow:
1. **Login:** Pretends to be Chrome and logs into `myclass.lpu.in` using user credentials.
2. **Schedule:** Navigates to the timetable and clicks on `CLASS-CODE` to open the detail popup.
3. **Data Extraction:** Refuses to click the popup link to avoid CodeTantra LTI security traps. Instead, scrapes the hidden `Meeting ID` out of the popup HTML.
4. **Link Construction:** Uses the extracted `Meeting ID` to build a secure, direct link to the `jnr.jsp` video room, bypassing dashboard redirects.
5. **Class Wait Loop:** If the class hasn't started and the join UI isn't ready, it refreshes the page every 60 seconds (up to 15 minutes) until the room opens.
6. **Iframe Piercing:** Once the room loads, shifts context inside the BigBlueButton `<iframe>`.
7. **Join Audio:** Finds the "Listen only" button inside the iframe context, clicks it, and holds the browser open to ensure full attendance is captured.
