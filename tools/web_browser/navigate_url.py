from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Tuple, Dict, Any
from contextlib import AsyncExitStack
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams


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
    common_exit_stack = AsyncExitStack()

    tools, _ = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://localhost:5000/sse",
        ),
        async_exit_stack=common_exit_stack
    )

    return await tools[1].run_async(
        args={
            "url": url,
            "headless": headless,
            "keep_open": keep_open,
        },
        tool_context=None,
    )

async def close_browser(browser: Optional[Browser]) -> None:
    """Close the browser instance if it exists."""
    if browser:
        await browser.close()

async def main():
    # Example usage
    test_url = "https://www.facebook.com"
    result = await navigate_to_url(test_url, keep_open=True)
    
    print(f"Navigation result: {result['message']}")
    if result['success']:
        print(f"Successfully opened {result['url']}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
