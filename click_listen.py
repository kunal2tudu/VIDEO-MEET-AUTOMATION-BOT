"""
Quick fix: Click the 'Listen only' button in the already-joined class.
Run this if the main bot left the browser open at the audio dialog.
"""
import asyncio
from playwright.async_api import async_playwright

JOIN_URL = "https://lovelyprofessionaluniversity.codetantra.com/secure/tla/jnr.jsp?m=MEETING-ID-CODE"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        print("[*] Opening join URL...")
        await page.goto(JOIN_URL, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(4000)
        print(f"    Current URL: {page.url}")

        for pg in context.pages:
            print(f"    Checking page: {pg.url}")
            try:
                listen_btn = pg.locator(".icon-bbb-listen").first
                await listen_btn.wait_for(timeout=5000)
                print("    ✓ Found 'Listen only' button via .icon-bbb-listen !")
                await listen_btn.click()
                print("    ✓ Clicked 'Listen only'!")
                await pg.wait_for_timeout(3000)
                await pg.screenshot(path="lpu_listen_clicked.png")
                print("    → Screenshot: lpu_listen_clicked.png")
                break
            except Exception as e:
                print(f"    ! Not found on this page: {e}")

        print("\n[✓] Done! Press Ctrl+C to quit.")
        try:
            await asyncio.sleep(999999)
        except KeyboardInterrupt:
            pass
        finally:
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bye!")
