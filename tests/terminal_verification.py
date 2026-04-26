import asyncio
import os
import sys

from playwright.async_api import async_playwright

# Ensure UTF-8
if sys.stdout.encoding != "utf-8":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


async def verify_terminal():
    print("Starting Terminal Verification...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        file_path = os.path.abspath("terminal_v2_panel.html")
        url = f"file:///{file_path.replace('\\', '/')}"

        print(f"Navigating to: {url}")
        await page.goto(url)

        # 1. Check for Table Content
        try:
            await page.wait_for_selector("tbody tr", timeout=5000)
            rows = await page.query_selector_all("tbody tr")
            print(f"PASS: Table populated with {len(rows)} rows.")
        except:
            print("FAIL: Table is empty!")

        # 2. Check for Chart (ApexCharts creates a svg)
        try:
            await page.wait_for_selector(".apexcharts-canvas", timeout=5000)
            print("PASS: ApexCharts rendered successfully.")
        except:
            print("FAIL: Chart not found!")

        # 3. Check for P/E Data (FY26)
        content = await page.content()
        # Look for the specific NVDA P/E '26 value from earlier (22.7)
        if "22.7" in content:
            print("PASS: Forward Estimates (NVDA P/E 22.7) found in HTML.")
        else:
            print("FAIL: Forward Estimates missing from table!")

        # 4. Take Screenshot
        screenshot_path = os.path.abspath("database/terminal_verification_proof.png")
        await page.screenshot(path=screenshot_path)
        print(f"Verification Complete. Proof saved to {screenshot_path}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(verify_terminal())
