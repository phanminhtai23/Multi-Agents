#server.py
from fastmcp import FastMCP
import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Tuple, Dict, Any

mcp = FastMCP("FastMCP Demo Server")

@mcp.tool()
async def navigate_to_url(url: str, headless: bool = False, keep_open: bool = True) -> Dict[str, Any]:
    """
    Opens a browser and navigates to the specified URL using Playwright.
    
    Args:
        url (str): The URL to navigate to
        headless (bool): Whether to run the browser in headless mode. Defaults to False.
        keep_open (bool): Whether to keep the browser open after navigation. Defaults to True.
    
    Returns:
        Dictionary containing:
        - success: Boolean indicating if navigation was successful
        - message: Status message or error message
        - url: The URL that was navigated to
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
        
        if not keep_open:
            await browser.close()
            return {
                "success": True,
                "message": "Successfully navigated and closed browser",
                "url": url
            }
            
        return {
            "success": True,
            "message": "Successfully navigated and browser kept open",
            "url": url
        }
            
    except Exception as e:
        if 'browser' in locals() and not keep_open:
            await browser.close()
        return {
            "success": False,
            "message": f"Error navigating to URL: {str(e)}",
            "url": url
        }



if __name__ == "__main__":
    asyncio.run(mcp.run_sse_async(host="localhost", port=5000))