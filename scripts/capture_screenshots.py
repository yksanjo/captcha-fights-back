"""
Automated screenshot capture for CAPTCHA documentation.
"""

from playwright.sync_api import sync_playwright
import time
import os

SCREENSHOTS_DIR = "docs/screenshots"


def capture_screenshots():
    """Capture all required screenshots."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Navigate to CAPTCHA
        print("Navigating to CAPTCHA interface...")
        page.goto("http://localhost:5000")
        time.sleep(2)  # Wait for challenge to load
        
        # Capture main interface
        print("Capturing main interface...")
        page.screenshot(path=f"{SCREENSHOTS_DIR}/captcha-interface.png", full_page=True)
        page.screenshot(path=f"{SCREENSHOTS_DIR}/challenge-screen.png", full_page=True)
        
        # Try to answer (this will show success or failure)
        try:
            answer_input = page.locator("#answer")
            if answer_input.is_visible():
                answer_input.fill("test")
                page.locator("button").click()
                time.sleep(1)
                page.screenshot(path=f"{SCREENSHOTS_DIR}/result-state.png", full_page=True)
        except:
            pass
        
        browser.close()
        print(f"Screenshots saved to {SCREENSHOTS_DIR}/")


if __name__ == "__main__":
    print("Make sure CAPTCHA server is running on http://localhost:5000")
    input("Press Enter when ready...")
    capture_screenshots()

