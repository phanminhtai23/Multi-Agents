

# long_running_tool = LongRunningFunctionTool(func=navigate_to_url)

# async def get_sum(a: int, b: int) -> int:
#     """Calculate the sum of two numbers.

#     Args:
#         a: number
#         b: number

#     Returns:
#         the sum of two numbers.
#     """
#     common_exit_stack = AsyncExitStack()

#     tools, _ = await MCPToolset.from_server(
#         connection_params=SseServerParams(
#             url="http://localhost:5000/sse",
#         ),
#         async_exit_stack=common_exit_stack
#     )

#     return await tools[0].run_async(
#         args={
#             "a": a,
#             "b": b,
#         },
#         tool_context=None,
#     )

# async def get_google_url() -> Dict[str, Any]:
#     """
#     Get the google URL of the browser.
    
#     Returns:
#         Dictionary containing:
#         - success: Boolean indicating if getting current URL was successful
#     """
#     common_exit_stack = AsyncExitStack()

#     tools, _ = await MCPToolset.from_server(
#         connection_params=SseServerParams(
#             url="http://localhost:5000/sse",
#         ),
#         async_exit_stack=common_exit_stack
#     )

#     return await tools[2].run_async(
#         args={
#         },
#         tool_context=None,
#     )

# async def navigate_to_url(url: str, headless: bool = False, keep_open: bool = True) -> Dict[str, Any]:
#     """
#     Opens a browser and navigates to the specified URL using Playwright.
    
#     Args:
#         url (str): The URL to navigate to
#         headless (bool): Whether to run the browser in headless mode. Defaults to False.
#         keep_open (bool): Whether to keep the browser open after navigation. Defaults to True.
    
#     Returns:
#         Dictionary containing:
#         - success: Boolean indicating if navigation was successful
#         - message: Status message or error message
#         - url: The URL that was navigated to
#     """
#     common_exit_stack = AsyncExitStack()

#     tools, _ = await MCPToolset.from_server(
#         connection_params=SseServerParams(
#             url="http://localhost:5000/sse",
#         ),
#         async_exit_stack=common_exit_stack
#     )
#     tools1, _1 = await MCPToolset.from_server(
#         connection_params=SseServerParams(
#             url="http://localhost:8931/sse",
#         ),
#         async_exit_stack=common_exit_stack
#     )


#     # print(f"Tools {len(tools)}")
#     # print(f"Tools {[tool.name for tool in tools]}")
#     print(f"Tools {len(tools1)}")
#     print(f"Tools {[tool.name for tool in tools1]}")


#     return await tools[1].run_async(
#         args={
#             "url": url,
#             "headless": headless,
#             "keep_open": keep_open,
#         },
#         tool_context=None,
#     )

import os

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_toolset import StdioServerParameters, SseServerParams
import asyncio
_allowed_path = os.path.dirname(os.path.abspath(__file__))

web_interactive_agent1 = LlmAgent(
        name="web_interactive_agent",
        model="gemini-2.0-flash",
        instruction="You are a web interactive agent, you can also use other tools to interact with the web browser",
        # instruction="You are a web interactive agent, you can use 'navigate_to_url' tool to navigate to a url and 'get_current_url' tool to get the current url, you can also use other tools to interact with the web browser",
        tools=[]
                # don't want agent to do write operation
                # you can also do below
                # tool_filter=lambda tool, ctx=None: tool.name
                # not in [
                #     'write_file',
                #     'edit_file',
                #     'create_directory',
                #     'move_file',
                # ],
                # tool_filter=[
                #     'browser_close',
                #     'browser_resize',
                #     'browser_console_messages',
                #     'browser_handle_dialog',
                #     'browser_file_upload',
                #     'browser_install',
                #     'browser_press_key',
                #     'browser_navigate',
                #     'browser_navigate_back',
                #     'browser_navigate_forward',
                #     'browser_network_requests',
                #     'browser_pdf_save',
                #     'browser_take_screenshot',
                #     'browser_snapshot',
                #     'browser_click',
                #     'browser_drag',
                #     'browser_hover',
                #     'browser_type',
                #     'browser_select_option',
                #     'browser_tab_list',
                #     'browser_tab_new',
                #     'browser_tab_select',
                #     'browser_tab_close',
                #     'browser_generate_playwright_test',
                #     'browser_wait_for'
                # ],
            )
        
async def initialize_web_interactive_agent():
    # _allowed_path = os.path.dirname(os.path.abspath(__file__))
    tools, exit_stack = await MCPToolset.from_server(
        # connection_params=StdioServerParameters(
        #     command='npx',
        #     args=["-y", "@playwright/mcp@latest", _allowed_path],
        # )
        connection_params=SseServerParams(url="http://localhost:8931/sse")
    )
    
    return LlmAgent(
        name="web_interactive_agent",
        model="gemini-2.0-flash",
        instruction="You are a web interactive agent, you can also use other tools to interact with the web browser",
        tools=tools
    )

async def create_web_interactive_agent():
    agent = await initialize_web_interactive_agent()
    return agent

web_interactive_agent = create_web_interactive_agent() # Bây giờ web_interactive_agent là một coroutine
# Sau đó, ở đâu đó trong file thực thi chính của bạn:
# web_interactive_agent = asyncio.run(create_web_interactive_agent())