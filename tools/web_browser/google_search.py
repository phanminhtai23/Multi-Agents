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
            await page.wait_for_selector('#search')
            
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

if __name__ == "__main__":
    # Example usage
    test_query = "Python Playwright tutorial"
    result = search_google(test_query)
    print(f"First result URL: {result}") 