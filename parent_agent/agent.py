from typing import Any, List, Optional
from google.adk.agents import LlmAgent 
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import Agent
import datetime
from zoneinfo import ZoneInfo
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
import asyncio
from contextlib import AsyncExitStack


from sub_agents.greeting_agent import greeting_agent
from sub_agents.farewell_agent import farewell_agent
from sub_agents.search_web_agent import search_web_agent

from google.adk.tools import agent_tool
from tools.web_browser.navigate_url import navigate_to_url
from google.adk.tools import LongRunningFunctionTool

long_running_tool = LongRunningFunctionTool(func=navigate_to_url)
# from tools.func_tools.tools import get_weather
# from tools.func_tools.get_current_time import get_current_time

root_agent_model = "gemini-2.0-flash"

async def setup_mcp_tools():
    """Setup MCP tools and return them with exit stack."""
    playwright_tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='npx',
            args=["-y", "@playwright/mcp@latest"],
            #   # Pass the API key as an environment variable to the npx process
            #   env={
            #       "GOOGLE_MAPS_API_KEY": google_maps_api_key
            #   }
        )
    )
    return playwright_tools, exit_stack

class ParentAgent(LlmAgent):
    """Parent agent that coordinates other agents and uses MCP tools."""
    
    def __init__(self):
        # Get MCP tools synchronously
        playwright_tools = None
        try:
            # Run setup in a new event loop
            loop = asyncio.new_event_loop()
            playwright_tools, self._exit_stack = loop.run_until_complete(setup_mcp_tools())
            loop.close()
        except Exception as e:
            print(f"Failed to initialize MCP tools: {e}")
            self._exit_stack = AsyncExitStack()

        # Initialize with all tools including MCP tools
        super().__init__(
            name="parent_agent",
            model=root_agent_model,
            description="The main coordinator agent, responsible for analyzing the tasks and then assigning them appropriately to the sub-agents.",
            instruction="Your main responsibility is to analyze the tasks and then assigning them appropriately to the sub-agents."
                    
                    "Use the 'search_web_agent' agent tool ONLY for question about search web or realtime data (e.g., stock market, weather, news, etc). "
                    "Use the 'playwright_tools' tool ONLY for question about open google browser and navigate to a url. "

                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                    # "3. 'search_web_agent': Handles web search requests or questions realtime data (e.g. stock market, weather, news, etc). Delegate to it for these. "

                    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. If it's a web search or a question about realtime data, delegate to 'search_web_agent'. "
                    
                    # "If it's a weather request, handle it yourself using 'get_weather'. "
                    # "If it's a timezone request, handle it yourself using 'get_current_time'. "
                    "If it's a request which you don't know how to anwser, handle it yourself using 'search_web_agent' tool. "
                    "If it's a request about open web browser or navigate to a url, handle it yourself using 'playwright_tools' tool. "
                    "For anything else, respond appropriately or state you cannot handle it.",
            tools=[agent_tool.AgentTool(agent=search_web_agent)] + ([playwright_tools] if playwright_tools else []),
            sub_agents=[greeting_agent, farewell_agent]
        )
        self._playwright_tools = playwright_tools

    async def cleanup(self):
        """Cleanup resources when done."""
        await self._exit_stack.aclose()

# Create the root agent instance with MCP tools
root_agent = ParentAgent()


root_agent = Agent(
                name="parent_agent",
            model=root_agent_model,
            description="The main coordinator agent, responsible for analyzing the tasks and then assigning them appropriately to the sub-agents.",
            instruction="Your main responsibility is to analyze the tasks and then assigning them appropriately to the sub-agents."
                    
                    "Use the 'search_web_agent' agent tool ONLY for question about search web or realtime data (e.g., stock market, weather, news, etc). "
                    "Use the 'playwright_tools' tool ONLY for question about open google browser and navigate to a url. "

                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                    # "3. 'search_web_agent': Handles web search requests or questions realtime data (e.g. stock market, weather, news, etc). Delegate to it for these. "

                    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. If it's a web search or a question about realtime data, delegate to 'search_web_agent'. "
                    
                    # "If it's a weather request, handle it yourself using 'get_weather'. "
                    # "If it's a timezone request, handle it yourself using 'get_current_time'. "
                    "If it's a request which you don't know how to anwser, handle it yourself using 'search_web_agent' tool. "
                    "If it's a request about open web browser or navigate to a url, handle it yourself using 'playwright_tools' tool. "
                    "For anything else, respond appropriately or state you cannot handle it.",
            tools=[agent_tool.AgentTool(agent=search_web_agent)] + ([playwright_tools] if playwright_tools else []),
            sub_agents=[greeting_agent, farewell_agent]
    )
