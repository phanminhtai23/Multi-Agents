# # agent.py
# import asyncio
# from contextlib import AsyncExitStack
# from google.adk.agents.llm_agent import LlmAgent
# from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, SseServerParams


# async def create_agent():
#   """Gets tools from MCP Server."""
#   common_exit_stack = AsyncExitStack()

#   # local_tools, _ = await MCPToolset.from_server(
#   #     connection_params=StdioServerParameters(
#   #         command='npx',
#   #         args=["-y",    # Arguments for the command
#   #           "@playwright/mcp@latest --port 8931",
#   #         ],
#   #     ),
#   #     async_exit_stack=common_exit_stack
#   # )

#   remote_tools, _ = await MCPToolset.from_server(
#       connection_params=SseServerParams(
#           # TODO: IMPORTANT! Change the path below to your remote MCP Server path
#           url="http://localhost:8931/sse"
#       ),
#       async_exit_stack=common_exit_stack
#   )


#   # agent = LlmAgent(
#   #     model='gemini-2.0-flash',
#   #     name='enterprise_assistant',
#   #     instruction=(
#   #         'Help user interact with the web browser'
#   #     ),
#   #     tools=[
#   #       *local_tools,
#   #       *remote_tools,
#   #     ],
#   # )
#   return remote_tools, common_exit_stack


# # Don't call asyncio.run here - this will be called by the framework
# # tools = asyncio.run(create_agent())

# # This should be an async coroutine that the framework can await
# root_agent = create_agent