import asyncio
from playwright.async_api import async_playwright

try:
    from config.local import URL
except ImportError:
    URL = "https://portal.parkon.ch"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(URL)
        await page.wait_for_timeout(5000)
        await browser.close()

asyncio.run(main())