from typing import Any, List, Optional
from tools.adk.tools import get_weather
from google.adk.agents import LlmAgent 
# from google.adk.agents import Agent
import datetime
from zoneinfo import ZoneInfo

from sub_agents.greeting_agent import greeting_agent
from sub_agents.farewell_agent import farewell_agent
from tools.adk.get_current_time import get_current_time


root_agent_model = "gemini-2.0-flash"


root_agent  = LlmAgent(
        name="parent_agent", # Give it a new version name
        model=root_agent_model,
        description="The main coordinator agent. Handles weather, timezone requests and delegates greetings/farewells to specialists.",
        instruction="You are the parent Agent coordinating a team. Your primary responsibility is to provide weather information and the current time in a specified city. "
                    "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
                    "If it's a weather request, handle it yourself using 'get_weather'. "
                    "If it's a timezone request, handle it yourself using 'get_current_time'. "
                    "For anything else, respond appropriately or state you cannot handle it.",
        tools=[get_weather, get_current_time], # Root agent still needs the weather tool for its core task
        # Key change: Link the sub-agents here!
        sub_agents=[greeting_agent, farewell_agent]
    )