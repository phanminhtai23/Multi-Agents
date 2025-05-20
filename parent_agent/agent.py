import asyncio
from google.adk.agents import LlmAgent 
from google.adk.agents import Agent, BaseAgent

from sub_agents.greeting_agent import greeting_agent
from sub_agents.farewell_agent import farewell_agent
from sub_agents.search_web_agent import search_web_agent

from google.adk.tools import agent_tool
from tools.web_browser.navigate_url import navigate_to_url
from google.adk.tools import LongRunningFunctionTool
# from sub_agents.web_interactive_agent import web_interactive_agent
# from google.adk.tools.tool_context import ToolContext
# from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters


long_running_tool = LongRunningFunctionTool(func=navigate_to_url)
# async def create_agent():
#     # asyncio.get_event_loop() here might create a loop if one isn't running
#     # print(f"Current asyncio event loop: {asyncio.get_event_loop()}") # Be careful, this can create/get a loop

#     connection_params = StdioServerParameters(
#         command='npx',
#         args=["-y", "@playwright/mcp@latest"],
#     )
    
#     print(f"MCP Connection Params: command='{connection_params.command}', args={connection_params.args}")

#     try:
#         tools, mcp_exit_stack = await MCPToolset.from_server(
#             connection_params=connection_params
#         )
#         print("MCPToolset created successfully.")
#     except Exception as e:
#         print(f"Error creating MCPToolset: {e}")
#         import traceback
#         traceback.print_exc()
#         raise

#     # Dummy agent for testing the MCP part
#     agent = LlmAgent(
#         name="parent_agent",
#         model="gemini-2.0-flash", # Use a known simple model for testing
#         instruction="Test agent.",
#         tools=[tools] # Just the MCP tools for now
#     )
#     return agent, mcp_exit_stack # mcp_exit_stack is the AsyncExitStack from MCPToolset


# root_agent = create_agent()

from tools.func_tools.tools import get_weather
from tools.func_tools.get_current_time import get_current_time
root_agent_model = "gemini-2.0-flash"
root_agent = LlmAgent(
            name="parent_agent",
            model=root_agent_model,
            description="The main coordinator agent, responsible for analyzing the tasks and then assigning them appropriately to the sub-agents.",
            instruction="Your main responsibility is to analyze the tasks and then assigning them appropriately to the sub-agents."

                "Use the 'web_interactive_agent' agent tool ONLY for question about missions about web interactive (e.g., navigate to a url, get current url, etc). "

                "Use the 'search_web_agent' agent tool ONLY for question about search web or realtime data (e.g., stock market, weather, news, etc) which is others agent can't handle."
                # "Use the 'playwright_tools' tool ONLY for question about open google browser and navigate to a url. "
                "You have specialized sub-agents: "
                "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                # "3. 'search_web_agent': Handles web search requests or questions realtime data (e.g. stock market, weather, news, etc). Delegate to it for these. "
                "3. 'web_interactive_agent': Handles web interactive requests (e.g. navigate to a url, get current url, etc). Delegate to it for these. "

                "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. If it's a interactive web request like open url, get current url, etc, delegate to 'web_interactive_agent'"
                
                # "If it's a weather request, handle it yourself using 'get_weather'. "
                # "If it's a timezone request, handle it yourself using 'get_current_time'. "
                # "If it's a request which you don't know how to anwser, handle it yourself using 'search_web_agent' tool. "
                # "If it's a request about open web browser or navigate to a url, handle it yourself using 'playwright_tools' tool. "
                "For anything else, respond appropriately or state you cannot handle it.",
            tools=[agent_tool.AgentTool(agent=search_web_agent), long_running_tool],
            sub_agents=[greeting_agent, farewell_agent]
    )