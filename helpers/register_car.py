import os
import asyncio
from playwright.async_api import async_playwright

PARKON_URL = os.getenv("PARKON_URL")

async def register_car(kanton: str, kennzeichen: str, email: str, duration_hours: int) -> bool:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(PARKON_URL)
            await page.wait_for_load_state("networkidle")

            await page.get_by_placeholder("Auswählen...").nth(0).click()
            await page.get_by_text(kanton, exact=True).click()

            await page.get_by_placeholder("354484").click()
            await page.get_by_placeholder("354484").fill(kennzeichen)

            await page.get_by_placeholder("Auswählen...").nth(1).click()
            await page.get_by_text(f"{duration_hours}h", exact=True).click()

            await page.get_by_placeholder("E-Mail Adresse").click()
            await page.get_by_placeholder("E-Mail Adresse").fill(email)

            await page.get_by_role("checkbox", name="Ich akzeptiere die ").check()

            await page.get_by_role("button", name="Absenden").click()


            await page.wait_for_timeout(1000)
            await browser.close()
        return True
    
    except Exception as e:
        print(f"Fehler bei Registrierung von {kennzeichen}: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(register_car("ZH", "123456", "default@example.com"))

