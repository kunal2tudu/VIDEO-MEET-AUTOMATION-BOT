"""
LPU Class Auto-Join Bot
=======================
Automatically logs into https://myclass.lpu.in, navigates to the class schedule,
finds and joins the specified class, and selects the 'Listen' option.

Requirements:
    pip install playwright
    playwright install chromium
"""

import asyncio
import sys
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

CREDENTIALS = {
    "reg_no": "USERNAME-CODE",
    "password": "PASSWORD-CODE",
}

CLASS_KEYWORD = "CLASS-CODE"

HEADFUL = True


async def login(page):
    """Log in to myclass.lpu.in"""
    print("[*] Navigating to LPU MyClass portal...")
    await page.goto("https://myclass.lpu.in/", wait_until="domcontentloaded", timeout=30000)

    print("[*] Entering credentials...")
    for selector in ["#username", "#reg_no", "input[name='username']", "input[type='text']"]:
        try:
            await page.fill(selector, CREDENTIALS["reg_no"], timeout=3000)
            print(f"    ✓ Filled username using selector: {selector}")
            break
        except Exception:
            continue

    for selector in ["#password", "input[name='password']", "input[type='password']"]:
        try:
            await page.fill(selector, CREDENTIALS["password"], timeout=3000)
            print(f"    ✓ Filled password using selector: {selector}")
            break
        except Exception:
            continue

    print("[*] Clicking login button...")
    for selector in ["button[type='submit']", "input[type='submit']", "#loginbtn", ".loginbtn", "button:has-text('Login')"]:
        try:
            await page.click(selector, timeout=3000)
            print(f"    ✓ Clicked login using selector: {selector}")
            break
        except Exception:
            continue

    await page.wait_for_load_state("networkidle", timeout=15000)
    print(f"    ✓ Logged in. Current URL: {page.url}")


async def navigate_to_classes(page):
    """Click 'View Class/Meetings' button"""
    print("[*] Looking for 'View Class/Meetings' button...")
    for selector in [
        "a:has-text('View Class')",
        "a:has-text('View Meetings')",
        "a:has-text('Class')",
        "button:has-text('View Class')",
        "[href*='class']",
        "[href*='meeting']",
    ]:
        try:
            await page.click(selector, timeout=4000)
            print(f"    ✓ Clicked using selector: {selector}")
            await page.wait_for_load_state("networkidle", timeout=10000)
            return
        except Exception:
            continue

    print("    ! Could not find 'View Class' button automatically. Trying screenshot...")
    await page.screenshot(path="lpu_dashboard.png")
    print("    → Screenshot saved as lpu_dashboard.png — check it to debug.")


async def find_and_click_class(page):
    """Find the CLASS-CODE class on the calendar and click it"""
    print(f"[*] Looking for class with keyword '{CLASS_KEYWORD}' on the schedule...")

    await page.wait_for_timeout(3000)

    try:
        class_el = page.locator(f".fc-title:has-text('{CLASS_KEYWORD}')").first
        await class_el.wait_for(timeout=8000)
        await class_el.click()
        print(f"    ✓ Clicked on class: {CLASS_KEYWORD}")

        print("    [*] Waiting for class details popup...")
        await page.wait_for_timeout(2000)
        print("    [*] Waiting for class details popup...")
        await page.wait_for_timeout(2000)

        join_link = page.locator("a[href*='/secure/tla/']").first
        await join_link.wait_for(timeout=5000)

        join_link = page.locator("a[href*='/secure/tla/mi.jsp'], a[href*='/secure/tla/jnr.jsp']").first
        await join_link.wait_for(timeout=5000)

        raw_url = await join_link.get_attribute("href")
        print(f"    ✓ Calendar says meeting URL is: {raw_url}")

        import urllib.parse
        parsed = urllib.parse.urlparse(raw_url)
        params = urllib.parse.parse_qs(parsed.query)

        if "m" in params:
            meeting_id = params["m"][0]
            dynamic_url = f"https://lovelyprofessionaluniversity.codetantra.com/secure/tla/jnr.jsp?m={meeting_id}"
            print(f"    ✓ Converted to direct BigBlueButton room link: {dynamic_url}")
        else:
            if raw_url.startswith("/"):
                dynamic_url = f"https://lovelyprofessionaluniversity.codetantra.com{raw_url}"
            else:
                dynamic_url = raw_url

        print("    [*] Opening direct room link in a new secure tab...")
        meeting_page = await page.context.new_page()
        await meeting_page.goto(dynamic_url, wait_until="domcontentloaded", timeout=20000)

        return meeting_page

    except PlaywrightTimeout:
        print(f"    ! Class '{CLASS_KEYWORD}' or Join link not found on calendar.")
        return None

async def join_via_direct_url(page, context, meeting_page):
    """Wait for the class to start on the CodeTantra page, and click Join."""
    print(f"[*] On CodeTantra meeting page: {meeting_page.url}")

    max_retries = 15

    for attempt in range(max_retries):
        if attempt > 0:
            print(f"    [*] Reloading meeting page (Attempt {attempt+1}/{max_retries})")
            await meeting_page.reload(wait_until="domcontentloaded", timeout=20000)
            await meeting_page.wait_for_timeout(3000)

        if await meeting_page.locator("iframe#frame").count() > 0:
            print("    ✓ Already on the actual video call page (iframe present). No need to click Join.")
            bbb_page = meeting_page
            break

        join_btn_found = False
        join_selectors = [".joinBtn", "a.joinBtn", "a:has-text('Join')", "button:has-text('Join')"]

        for selector in join_selectors:
            if await meeting_page.locator(selector).count() > 0:
                join_btn_found = True
                break

        if not join_btn_found:
            print("    ! Join button/iframe not found. Class might not have started yet.")
            if attempt < max_retries - 1:
                print("    ⏳ Waiting 60 seconds before refreshing...")
                await meeting_page.wait_for_timeout(60000)
                continue
            else:
                raise Exception("Class did not start after 15 minutes of waiting.")

        print("[*] Waiting for BigBlueButton to open in a new tab after Join...")
        try:
            async with context.expect_page(timeout=15000) as new_page_info:
                for selector in join_selectors:
                    try:
                        await meeting_page.click(selector, timeout=5000)
                        print(f"    ✓ Clicked Join using selector: {selector}")
                        break
                    except Exception:
                        continue
            bbb_page = await new_page_info.value
            print(f"    ✓ BigBlueButton opened in new tab: {bbb_page.url}")
        except PlaywrightTimeout:
            print("    ! No new tab — assuming BBB loaded in current tab.")
            bbb_page = meeting_page

        break

    await bbb_page.wait_for_load_state("domcontentloaded", timeout=20000)
    await bbb_page.wait_for_timeout(5000)
    return bbb_page


async def select_listen_option(bbb_page):
    """Select the 'Listen only' option on the BigBlueButton audio dialog."""
    print("[*] Looking for 'Listen only' button on BBB page...")

    has_frame = await bbb_page.locator("iframe#frame").count() > 0
    if has_frame:
        print("    [*] Detected BigBlueButton is inside an iframe. Switching context to iframe...")
        target_context = bbb_page.frame_locator("iframe#frame")
    else:
        target_context = bbb_page

    for selector in [
        "button[aria-label='Listen only']",
        ".icon-bbb-listen",
        "i.icon-bbb-listen",
        "span:has(.icon-bbb-listen)",
        "[class*='icon-bbb-listen']",
    ]:
        try:
            el = target_context.locator(selector).first
            await el.wait_for(state="visible", timeout=10000)
            await el.click()
            print(f"    ✓ Clicked 'Listen only' using selector: {selector}")
            await bbb_page.wait_for_timeout(2000)
            await bbb_page.screenshot(path="lpu_joined.png")
            print("    → Screenshot saved as lpu_joined.png")
            return True
        except Exception as e:
            print(f"    ! Selector '{selector}' failed.")
            continue

    print("    ! Could not find 'Listen only' button.")
    await bbb_page.screenshot(path="lpu_join_options.png")
    print("    → Screenshot saved as lpu_join_options.png")
    return False


async def main():
    async with async_playwright() as p:
        print("=" * 55)
        print("   LPU Class Auto-Join Bot")
        print("=" * 55)

        browser = await p.chromium.launch(
            headless=not HEADFUL,
            slow_mo=500,
            args=["--start-maximized"],
        )
        context = await browser.new_context(
            no_viewport=True,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        try:
            await login(page)
            await navigate_to_classes(page)
            meeting_url = await find_and_click_class(page)

            if not meeting_url:
                raise Exception("Could not find the meeting link on the calendar for today. Cannot join.")

            meeting_page = await join_via_direct_url(page, context, meeting_url)
            await select_listen_option(meeting_page)

            print("\n[✓] Bot finished joining. Holding browser open for 2 hours (class ends at 9 PM).")
            print("    Press Ctrl+C to exit early.")
            await asyncio.sleep(2 * 60 * 60)
            print("\n[✓] 2 hours elapsed — class should be over. Closing browser.")

        except KeyboardInterrupt:
            print("\n[*] Exiting...")
        except Exception as e:
            print(f"\n[!] Error: {e}")
            await page.screenshot(path="lpu_error.png")
            print("    → Error screenshot saved as lpu_error.png")
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBye!")
