from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..skill import Skill

class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        pass
        
    @abstractmethod
    def execute_with_tools(self, prompt: str, system_prompt: str, tools: List[Skill]) -> Any:
        """
        Executes a prompt while providing a list of skills/tools the LLM can use (Function Calling).
        """
        pass
