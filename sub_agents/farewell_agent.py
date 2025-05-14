from google.adk.agents import LlmAgent    
from tools.adk.tools import say_goodbye


farewell_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="farewell_agent", # Keep original name
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )