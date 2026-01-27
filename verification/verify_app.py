from playwright.sync_api import sync_playwright

def verify_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Navigating to http://localhost:3000/")
            page.goto("http://localhost:3000/")
            # Wait for some content to load, e.g., the title
            print("Waiting for selector...")
            page.wait_for_selector("text=Euloge Learning Platform")

            # Take a screenshot
            print("Taking screenshot...")
            page.screenshot(path="verification/app_screenshot.png")
            print("Screenshot taken.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_app()
