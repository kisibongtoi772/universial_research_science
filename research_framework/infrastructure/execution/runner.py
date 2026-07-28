import asyncio
from typing import Dict, Any, Callable
from ...core.plan import Plan
from ...core.task import Task, TaskStatus
from ...application.messaging import MessageBus, Message
from ...core.agent import Agent
from ...core.artifact import Artifact, ArtifactType
from ...core.ports.storage import ArtifactStore

class ExecutionRunner:
    def __init__(self, message_bus: MessageBus, artifact_store: ArtifactStore):
        self.bus = message_bus
        self.artifact_store = artifact_store
        self.agents: Dict[str, Agent] = {}

    def register_agent(self, agent: Agent):
        self.agents[agent.id] = agent

    def _save_plan_state(self, plan: Plan):
        artifact = Artifact(
            id="plan_state",
            session_id=plan.session_id,
            name="plan_state.json",
            artifact_type=ArtifactType.JSON,
            content=plan.model_dump_json()
        )
        self.artifact_store.save(artifact)

    async def execute_plan(self, plan: Plan):
        # Setup event loops or DAG runner
        # Prototype: Sequential execution
        while not plan.is_completed():
            ready_tasks = plan.get_ready_tasks()
            
            if not ready_tasks:
                # Check if there are tasks in progress, if none and not completed, we are stuck
                in_progress = [t for t in plan.tasks.values() if t.status == TaskStatus.IN_PROGRESS]
                if not in_progress and not plan.is_completed():
                    print("Error: DAG is stuck. No ready tasks and no running tasks.")
                    break
                await asyncio.sleep(1)
                continue
                
            for task in ready_tasks:
                task.status = TaskStatus.IN_PROGRESS
                self._save_plan_state(plan)
                
                agent = self.agents.get(task.assigned_agent_id)
                if agent:
                    print(f"--> Agent {agent.role.name} starting task: {task.title}")
                    # Simulate work
                    await asyncio.sleep(2)
                    task.status = TaskStatus.COMPLETED
                    print(f"--> Task {task.title} completed.")
                else:
                    print(f"Error: No agent assigned for {task.id}")
                    task.status = TaskStatus.FAILED
                    
                self._save_plan_state(plan)
