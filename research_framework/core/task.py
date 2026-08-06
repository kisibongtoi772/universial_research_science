from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED_FOR_INPUT = "paused_for_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task(BaseModel):
    id: str = Field(..., description="Unique identifier for the task")
    title: str = Field(..., description="Short title of the task")
    description: str = Field(..., description="Detailed description of what needs to be done")
    expected_output: str = Field(..., description="What the expected output looks like")
    
    # Dependencies: List of Task IDs that must be completed before this task can start
    dependencies: List[str] = Field(default_factory=list)
    
    # Flags
    requires_human_input: bool = Field(default=False, description="If true, pauses agent to request human input via CLI")
    max_retries: int = Field(default=3, description="Maximum number of retries on failure")
    current_retries: int = Field(default=0, description="Current number of retries attempted")
    timeout_seconds: Optional[int] = Field(default=None, description="Maximum execution time in seconds")
    priority: int = Field(default=0, description="Task priority. Higher runs first when semaphore is limited.")
    
    # Context: Identifiers for artifacts this task has access to (read/write)
    input_artifacts: List[str] = Field(default_factory=list, description="IDs of artifacts to read from")
    output_artifacts: List[str] = Field(default_factory=list, description="IDs of artifacts to write to")
    
    # Runtime state
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    assigned_agent_id: Optional[str] = Field(default=None)
    result_summary: Optional[str] = Field(default=None)
    error_message: Optional[str] = Field(default=None, description="Reason for failure or cancellation")
