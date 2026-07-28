from typing import Callable, Dict, Any, Optional
from pydantic import BaseModel, Field

class Skill(BaseModel):
    name: str = Field(..., description="Name of the skill (e.g. 'pubmed_search')")
    description: str = Field(..., description="Description of what the skill does, used by LLM to choose it.")
    parameters_schema: Dict[str, Any] = Field(..., description="JSON Schema of the parameters this skill accepts.")
    
    # In runtime, this will hold the actual callable function
    # It is not validated by Pydantic directly to allow flexibility
    executable: Optional[Callable] = Field(default=None, exclude=True)
    
    def execute(self, **kwargs) -> Any:
        if self.executable is None:
            raise NotImplementedError(f"Skill {self.name} has no executable attached.")
        return self.executable(**kwargs)
