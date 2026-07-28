import asyncio
from typing import Dict, Any, Callable
from ...core.plan import Plan
from ...core.task import Task, TaskStatus
from ...application.messaging import MessageBus, Message
from ...core.agent import Agent
from ...core.artifact import Artifact, ArtifactType
from ...core.ports.storage import ArtifactStore

class ExecutionRunner:
    def __init__(self, message_bus: MessageBus, artifact_store: ArtifactStore, max_concurrency: int = 5):
        self.bus = message_bus
        self.artifact_store = artifact_store
        self.agents: Dict[str, Agent] = {}
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self._state_lock = asyncio.Lock()

    def register_agent(self, agent: Agent):
        self.agents[agent.id] = agent

    async def _save_plan_state(self, plan: Plan):
        artifact = Artifact(
            id="plan_state",
            session_id=plan.session_id,
            name="plan_state.json",
            artifact_type=ArtifactType.JSON,
            content=plan.model_dump_json()
        )
        async with self._state_lock:
            self.artifact_store.save(artifact)

    async def _execute_task_by_agent(self, task: Task, plan: Plan):
        agent = self.agents.get(task.assigned_agent_id)
        if not agent:
            task.status = TaskStatus.FAILED
            task.error_message = f"No agent assigned for {task.id}"
            await self._save_plan_state(plan)
            return
            
        async with self.semaphore:
            print(f"--> Agent {agent.role.name} starting task: {task.title}")
            try:
                # Actual async execution
                await agent.execute_task(task, {"session_id": plan.session_id})
                task.status = TaskStatus.COMPLETED
                print(f"--> Task {task.title} completed.")
            except Exception as e:
                print(f"--> Task {task.title} failed: {e}")
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
            
            await self._save_plan_state(plan)

    def _cancel_downstream_tasks(self, plan: Plan, failed_task_id: str):
        for task in plan.tasks.values():
            if failed_task_id in task.dependencies and task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                task.error_message = f"Dependency {failed_task_id} failed"
                print(f"--> Task {task.title} CANCELLED due to upstream failure.")
                self._cancel_downstream_tasks(plan, task.id)

    async def execute_plan(self, plan: Plan):
        pending_tasks = set()
        
        while not plan.is_completed():
            # Handle cascading cancellations
            for t in list(plan.tasks.values()):
                if t.status == TaskStatus.FAILED:
                    self._cancel_downstream_tasks(plan, t.id)
            
            # A plan is "done" if all tasks are COMPLETED, FAILED, or CANCELLED
            if all(t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] for t in plan.tasks.values()):
                break
                
            ready_tasks = plan.get_ready_tasks()
            
            for task in ready_tasks:
                task.status = TaskStatus.IN_PROGRESS
                await self._save_plan_state(plan)
                
                coro = self._execute_task_by_agent(task, plan)
                asyncio_task = asyncio.create_task(coro)
                pending_tasks.add(asyncio_task)
                
            if not pending_tasks:
                # Check if there are tasks still running
                in_progress = [t for t in plan.tasks.values() if t.status == TaskStatus.IN_PROGRESS]
                if not in_progress:
                    print("Error: DAG is stuck. No ready tasks and no running tasks.")
                    break
                # if stuck waiting but pending is empty this shouldn't happen unless we miss something
            
            done, pending_tasks = await asyncio.wait(
                pending_tasks, return_when=asyncio.FIRST_COMPLETED
            )
            
            for t in done:
                try:
                    t.result()
                except Exception as e:
                    print(f"Execution engine error: {e}")
