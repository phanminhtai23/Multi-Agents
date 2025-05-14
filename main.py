import os
from parent_agent.agent import BaseAgent
from tools.mcp.search_mcp import SearchMCPTool
from configs.agent_config import get_agent_config

def main():
    # Initialize MCP tools
    search_tool = SearchMCPTool()
    
    # Create agents with configurations
    search_agent_config = get_agent_config("search_agent", tools=[search_tool.tool])
    search_agent = BaseAgent(
        **search_agent_config.dict(),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Example usage
    query = "What are the latest developments in AI agents?"
    result = search_agent.run(query)
    print(f"Search result: {result}")

if __name__ == "__main__":
    main() 