from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from .skill import Skill
from .task import Task

class AgentRole(BaseModel):
    name: str = Field(..., description="Role name (e.g. 'Literature Researcher')")
    system_prompt: str = Field(..., description="The core persona and instructions for this agent")

class Agent(BaseModel, ABC):
    id: str = Field(..., description="Unique identifier for the agent")
    role: AgentRole = Field(..., description="The role this agent assumes")
    skills: List[Skill] = Field(default_factory=list, description="Skills equipped to this agent")
    
    @abstractmethod
    def execute_task(self, task: Task, context: Dict[str, Any]) -> Any:
        """
        Executes a given task. Needs to be implemented by concrete classes.
        """
        pass
