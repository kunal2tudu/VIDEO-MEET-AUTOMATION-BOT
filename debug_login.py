import asyncio
from playwright.async_api import async_playwright

async def debug_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
        context = await browser.new_context()
        page = await context.new_page()

        print("Navigating to LPU...")
        await page.goto("https://myclass.lpu.in/")

        print("Waiting 5 seconds then taking screenshot...")
        await page.wait_for_timeout(5000)
        await page.screenshot(path="lpu_debug_login.png")
        print("Saved lpu_debug_login.png")

        try:
            print("Fetching form HTML...")
            form_html = await page.evaluate("() => document.body.innerHTML")
            with open("login_dump.html", "w", encoding="utf-8") as f:
                f.write(form_html)
            print("Saved form HTML to login_dump.html")

            print("Looking for username input...")
            await page.wait_for_selector("input[type='text']", timeout=5000)
            print("Found using input[type='text']!")

        except Exception as e:
            print(f"Failed to interact: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_login())
