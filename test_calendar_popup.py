import asyncio
from playwright.async_api import async_playwright

async def test_popup():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()

        await page.goto("https://myclass.lpu.in/")
        await page.fill("input[name='username']", "USERNAME-CODE")
        await page.fill("input[name='password']", "PASSWORD-CODE")
        await page.click("button[type='submit']")
        await page.wait_for_load_state("networkidle")

        await page.click("a:has-text('View Class')")
        print("Waiting for calendar...")
        await page.wait_for_timeout(3000)

        print("Clicking class...")
        class_el = page.locator(".fc-title:has-text('CLASS-CODE')").first
        await class_el.click()
        await page.wait_for_timeout(2000)

        print("Looking for join link in popup...")
        join_link = page.locator("a[href*='/secure/tla/']").first
        href = await join_link.get_attribute("href")
        target = await join_link.get_attribute("target")
        print(f"Join link href: {href}")
        print(f"Join link target: {target}")

        await browser.close()

asyncio.run(test_popup())
