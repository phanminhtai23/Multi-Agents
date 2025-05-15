from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Tuple

async def navigate_to_url(url: str, headless: bool = False) -> Tuple[Optional[Browser], Optional[BrowserContext], Optional[Page], Optional[str]]:
    """
    Opens a browser and navigates to the specified URL using Playwright.
    
    Args:
        url (str): The URL to navigate to
        headless (bool): Whether to run the browser in headless mode. Defaults to False.
    
    Returns:
        Tuple containing:
        - Browser instance
        - Browser context
        - Page instance
        - Error message (if any)
    """
    try:
        playwright = await async_playwright().start()
        # Launch the browser (using Chromium by default)
        browser = await playwright.chromium.launch(headless=headless)
        
        # Create a new browser context
        context = await browser.new_context()
        
        # Create a new page
        page = await context.new_page()
        
        # Navigate to the URL
        await page.goto(url)
        
        # Wait for the page to load
        await page.wait_for_load_state("networkidle")
        
        return browser, context, page, None
            
    except Exception as e:
        return None, None, None, f"Error navigating to URL: {str(e)}"

async def close_browser(browser: Optional[Browser]) -> None:
    """Close the browser instance if it exists."""
    if browser:
        await browser.close()

async def main():
    # Example usage
    test_url = "https://www.facebook.com"
    browser, context, page, error = await navigate_to_url(test_url)
    
    if error:
        print(error)
    else:
        print("Successfully navigated to the URL")
        print("Browser is still open. You can continue working with it.")
        print("To close the browser, call await close_browser(browser) when you're done.")
        
        # Example of how to use the browser instance
        try:
            # Keep the script running until user decides to close
            input("Press Enter to close the browser...")
        finally:
            # Clean up when done
            await close_browser(browser)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
