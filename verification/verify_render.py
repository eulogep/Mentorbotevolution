from playwright.sync_api import sync_playwright

def verify_app_renders(page):
    # Go to localhost:3000
    page.goto("http://localhost:3000")

    # Wait for the "Score actuel" text to be visible to ensure content is loaded
    page.wait_for_selector("text=Score actuel")

    # Take a screenshot
    page.screenshot(path="verification/app_screenshot.png")
    print("Screenshot saved to verification/app_screenshot.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_app_renders(page)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
