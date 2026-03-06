import asyncio
from playwright.async_api import async_playwright

async def debug_codetantra():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        page.on("request", lambda request: print(f">> Request: {request.url}"))
        page.on("response", lambda response: print(f"<< Response: {response.status} {response.url}"))

        await page.goto("https://myclass.lpu.in/")
        await page.fill("input[name='username']", "USERNAME-CODE")
        await page.fill("input[name='password']", "PASSWORD-CODE")
        await page.click("button[type='submit']")
        await page.wait_for_load_state("networkidle")

        await page.click("a:has-text('View Class')")
        await page.wait_for_timeout(3000)

        class_el = page.locator(".fc-title:has-text('CLASS-CODE')").first
        await class_el.click()
        await page.wait_for_timeout(2000)

        try:
            join_link = page.locator("a[href*='/secure/tla/']").first
            href = await join_link.get_attribute("href")

            print(f"\n=========================================")
            print(f"FOUND EXACT HREF IN CALENDAR: {href}")
            print(f"=========================================\n")

            async with context.expect_page(timeout=15000) as new_page_info:
                await join_link.click()

            new_page = await new_page_info.value
            await new_page.wait_for_load_state("domcontentloaded")

            print(f"\n=========================================")
            print(f"FINAL LANDED URL WAS: {new_page.url}")
            print(f"=========================================\n")

            await new_page.screenshot(path="debug_final_page.png")

        except Exception as e:
            print(f"Error clicking popup: {e}")

        await page.wait_for_timeout(10000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_codetantra())
