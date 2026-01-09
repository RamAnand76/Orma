from typing import Dict, Type
from .base import BaseTool
from .utils.basic import TimeTool, CalculatorTool
from .search.ddgs_tool import DdgsTool
from .code.sandbox import PythonTool  # Phase 12: Code Autonomy

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._load_defaults()
        
    def _load_defaults(self):
        self.register(TimeTool())
        self.register(CalculatorTool())
        self.register(DdgsTool())
        self.register(PythonTool())  # Phase 12: The Engineer
        
    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool
        
    def get_tool(self, name: str) -> BaseTool:
        return self._tools.get(name)
        
    def get_docs(self) -> str:
        """Returns documentation for the LLM."""
        docs = []
        for t in self._tools.values():
            docs.append(f"- {t.name}(args): {t.description}")
        return "\n".join(docs)
        
    def execute(self, tool_name: str, *args) -> str:
        tool = self.get_tool(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found."
        try:
            return tool.execute(*args)
        except Exception as e:
            return f"Execution Error: {e}"
