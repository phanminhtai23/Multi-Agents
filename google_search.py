import asyncio
from playwright.async_api import async_playwright
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('google_search.log'),
        logging.StreamHandler()
    ]
)

async def google_search(query: str) -> str:
    """
    Perform a Google search using Playwright and return the first result URL.
    
    Args:
        query (str): The search query to enter in Google
        
    Returns:
        str: The URL of the first search result
    """
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Log the start of search
            logging.info(f"Starting Google search for query: {query}")
            
            # Navigate to Google
            await page.goto('https://www.google.com')
            
            # Accept cookies if the dialog appears
            try:
                await page.click('button:has-text("Accept all")')
            except:
                pass
            
            # Type the search query and press Enter
            await page.fill('textarea[name="q"]', query)
            await page.press('textarea[name="q"]', 'Enter')
            
            # Wait for search results to load
            await page.wait_for_selector('div#search')
            
            # Get the first result URL
            first_result = await page.query_selector('div#search a')
            if first_result:
                url = await first_result.get_attribute('href')
                logging.info(f"Found first result URL: {url}")
            else:
                url = "No results found"
                logging.warning("No search results found")
            
            # Take screenshot for verification (optional)
            screenshot_path = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            logging.info(f"Screenshot saved to: {screenshot_path}")
            
            # Close browser
            await browser.close()
            
            return url
            
    except Exception as e:
        logging.error(f"Error during Google search: {str(e)}")
        raise

def search_google(query: str) -> str:
    """
    Synchronous wrapper for the async google_search function.
    
    Args:
        query (str): The search query to enter in Google
        
    Returns:
        str: The URL of the first search result
    """
    return asyncio.run(google_search(query))

def search_google_wait_enter(query: str, is_visible: bool = True) -> None:
    """
    Perform a Google search and wait for user to press Enter before closing.
    
    Args:
        query (str): The search query to enter in Google
        is_visible (bool): Whether to show the browser (True) or run in headless mode (False)
    """
    from playwright.sync_api import sync_playwright
    import logging
    
    try:
        with sync_playwright() as p:
            # Launch browser with specified visibility
            browser = p.chromium.launch(
                headless=not is_visible,
                slow_mo=50  # Slow down operations by 50ms for better visibility
            )
            
            # Create a new browser context with specific viewport and user agent
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            # Create a new page
            page = context.new_page()
            
            # Log the start of search
            logging.info(f"Starting {'visible' if is_visible else 'headless'} Google search for query: {query}")
            
            # Navigate to Google
            page.goto('https://www.google.com')
            
            # Accept cookies if the dialog appears
            try:
                page.click('button:has-text("Accept all")')
            except:
                pass
            
            # Type the search query and press Enter
            page.fill('textarea[name="q"]', query)
            page.press('textarea[name="q"]', 'Enter')
            
            # Wait for search results to load
            page.wait_for_selector('div#search')
            
            # Log that search is complete
            logging.info(f"Search completed for query: {query}")
            
            # Take screenshot of results
            screenshot_path = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            page.screenshot(path=screenshot_path)
            logging.info(f"Screenshot saved to: {screenshot_path}")
            
            # Wait for user to press Enter
            input("Press Enter to close the browser...")
            
            # Close browser
            browser.close()
            logging.info("Browser closed")
            
    except Exception as e:
        logging.error(f"Error during Google search: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    test_query = "Python Playwright tutorial"
    
    # Example 1: Headless search (original function)
    print("Running headless search...")
    result = search_google(test_query)
    print(f"First result URL: {result}")
    
    # Example 2: Visible search with Enter wait
    print("\nRunning visible search (wait for Enter)...")
    search_google_wait_enter(test_query, is_visible=True)
    print("Visible search completed")
    
    # Example 3: Headless search with Enter wait
    print("\nRunning headless search (wait for Enter)...")
    search_google_wait_enter(test_query, is_visible=False)
    print("Headless search completed") 