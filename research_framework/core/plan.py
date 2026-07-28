from pydantic import BaseModel, Field
from typing import List, Dict
from .task import Task, TaskStatus

class Plan(BaseModel):
    id: str = Field(..., description="Unique ID for the plan")
    session_id: str = Field(..., description="Session ID")
    goal: str = Field(..., description="The overall goal this plan is trying to achieve")
    tasks: Dict[str, Task] = Field(default_factory=dict, description="Dictionary of tasks keyed by task ID")
    
    def add_task(self, task: Task):
        self.tasks[task.id] = task
        
    def get_ready_tasks(self) -> List[Task]:
        """Returns tasks that are PENDING and have all dependencies COMPLETED."""
        ready = []
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            
            can_start = True
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    can_start = False
                    break
                    
            if can_start:
                ready.append(task)
        return ready

    def is_completed(self) -> bool:
        return all(t.status == TaskStatus.COMPLETED for t in self.tasks.values())
