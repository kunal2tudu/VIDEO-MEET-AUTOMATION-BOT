import asyncio
import json
from playwright.async_api import async_playwright

async def debug_calendar_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://myclass.lpu.in/")
        await page.fill("input[type='text']", "USERNAME-CODE")
        await page.fill("input[type='password']", "PASSWORD-CODE")
        await page.click("button[type='submit']")
        await page.wait_for_load_state("networkidle")

        await page.click("a:has-text('View Class')")
        print("Waiting for calendar...")
        await page.wait_for_timeout(5000)

        print("\n=== All Links with /secure/tla/ ===")
        links = await page.locator("a[href*='/secure/tla/']").all()
        for link in links:
            href = await link.get_attribute("href")
            print(f"Link: {href}")

        print("\n=== Let's inspect the calendar elements directly ===")
        events = await page.locator(".fc-event").all()
        for i, event in enumerate(events):
            title = await event.locator(".fc-title").inner_text()
            if "CLASS-CODE" in title:
                print(f"Found class! HTML:")
                html = await event.evaluate("el => el.outerHTML")
                print(html)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_calendar_data())
