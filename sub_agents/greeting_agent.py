from tools.adk.tools import say_hello
from google.adk.agents import LlmAgent

greeting_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="greeting_agent", # Keep original name for consistency
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )