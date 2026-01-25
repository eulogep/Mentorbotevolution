from playwright.sync_api import sync_playwright, expect

def test_app(page):
    print("Navigating to http://localhost:3000")
    page.goto("http://localhost:3000")

    # Check header
    print("Checking header")
    expect(page.get_by_role("heading", name="Euloge Learning Platform").first).to_be_visible()

    # Check if main modules are visible
    print("Checking 'Plans de Maîtrise'")
    expect(page.get_by_text("Plans de Maîtrise").first).to_be_visible()

    # Navigation test
    print("Clicking 'Voir' for 'Outils IA'")
    # Find the card containing "Outils IA" and click the "Voir" button inside it
    # We use a locator that filters for the card text, then finds the button
    # The card has "Outils IA" text.

    # Locate the container (Card) that has the text "Outils IA"
    # The structure is somewhat deeply nested, so let's try finding the button directly if possible.
    # But there are multiple "Voir" buttons.

    # Use layout selector: button "Voir" that is near "Outils IA"
    # Or filter
    card = page.locator("div.border-0", has_text="Outils IA").first
    card.get_by_role("button", name="Voir").click()

    # Expect to see "Assistant IA Conversationnel" which is unique to that module
    print("Checking for 'Assistant IA Conversationnel'")
    expect(page.get_by_text("Assistant IA Conversationnel")).to_be_visible()

    print("Taking screenshot")
    page.screenshot(path="verification/verification.png")
    print("Verification complete")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_app(page)
        except Exception as e:
            print(f"Test failed: {e}")
            page.screenshot(path="verification/error.png")
            raise e
        finally:
            browser.close()
