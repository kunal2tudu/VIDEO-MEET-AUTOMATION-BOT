import asyncio
from playwright.async_api import async_playwright

async def test_link():
    url = "https://lovelyprofessionaluniversity.codetantra.com/secure/tla/jnr.jsp?m=MEETING-ID-CODE"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://myclass.lpu.in/")
        await page.fill("#username", "USERNAME-CODE")
        await page.fill("#password", "PASSWORD-CODE")
        await page.click("button[type='submit']")
        await page.wait_for_load_state("networkidle")

        await page.click("a:has-text('View Class')")
        await page.wait_for_load_state("networkidle")

        print(f"[*] Navigating to: {url}")
        await page.goto(url)
        await page.wait_for_timeout(3000)

        print(f"[*] Final URL after redirect: {page.url}")
        await page.screenshot(path="redirect_test.png")
        await browser.close()

asyncio.run(test_link())
