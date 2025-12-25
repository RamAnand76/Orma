from abc import ABC, abstractmethod

class BaseTool(ABC):
    """
    Abstract Base Class for all Orma Tools.
    This ensures that any tool you add follows a strict contract.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The tool name used in the [ACTION: name(args)] syntax."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Short description for the LLM to understand when to use it."""
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> str:
        """The core logic. Must return a string."""
        pass
