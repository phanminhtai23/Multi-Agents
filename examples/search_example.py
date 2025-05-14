import os
from parent_agent.agent import BaseAgent
from tools.adk.search_tool import SearchTool
from configs.adk_config import get_agent_config

def main():
    # Initialize search tool
    search_tool = SearchTool()
    
    # Create search agent with configuration
    agent_config = get_agent_config("search_agent", tools=[search_tool.get_tool()])
    search_agent = BaseAgent(
        **agent_config.dict(),
        api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Example search queries
    queries = [
        "What are the latest developments in AI agents?",
        "How does Google ADK compare to other agent frameworks?",
        "What are the best practices for building AI agents?"
    ]
    
    # Run searches
    for query in queries:
        print(f"\nSearching for: {query}")
        try:
            result = search_agent.run(query)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 