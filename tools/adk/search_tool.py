from typing import Any, Dict, Optional
from google.adk import Tool, ToolConfig
from google.adk.tools import SearchTool as ADKSearchTool

class SearchTool:
    """Search tool implementation using Google ADK."""
    
    def __init__(
        self,
        name: str = "search",
        description: str = "Search the web for information",
        max_results: int = 5,
        **kwargs: Any
    ):
        self.config = ToolConfig(
            name=name,
            description=description,
            max_results=max_results,
            **kwargs
        )
        self.tool = ADKSearchTool(self.config)
    
    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute a search using the ADK search tool."""
        return self.tool.search(
            query=query,
            max_results=max_results or self.config.max_results,
            **kwargs
        )
    
    def get_tool(self) -> Tool:
        """Get the ADK tool instance."""
        return self.tool 