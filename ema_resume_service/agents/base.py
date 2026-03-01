from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Abstract Base Class representing an execution node in the LangGraph workflow.
    Enforces Object-Oriented polymorphism across all pipeline steps.
    """
    
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the business logic for the specific node.
        Must return a dictionary updating the AgentState.
        """
        pass
