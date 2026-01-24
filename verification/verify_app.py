import time
from playwright.sync_api import sync_playwright

def run():
    print("Starting verification...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        try:
            print("Navigating to http://localhost:3000...")
            page.goto("http://localhost:3000", timeout=30000)

            # Check for title or main element
            print("Checking page content...")
            page.wait_for_selector("text=Euloge Learning Platform", timeout=10000)

            # Check for current score
            page.wait_for_selector("text=Score actuel:", timeout=5000)

            # Check tabs
            print("Checking navigation tabs...")
            # Use specific selector for sidebar navigation
            # The sidebar is in a <nav> element
            page.click("nav >> text=Productivité")

            # Verify the header changed
            page.wait_for_selector("h2:has-text('Deep Work & Productivité')", timeout=5000)

            # Click back to 'Plans de Maîtrise'
            page.click("nav >> text=Plans de Maîtrise")
            # Verify we are back
            # MasteryDashboard renders "Bienvenue" inside a card
            page.wait_for_selector("text=Bienvenue", timeout=5000)

            print("Verification successful!")
            page.screenshot(path="verification/verification_success.png")
        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="verification_failure.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    run()
