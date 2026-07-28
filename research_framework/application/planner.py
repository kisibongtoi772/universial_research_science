import json
import uuid
from typing import Dict, Any
from ..core.ports.llm import LLMProvider
from ..core.plan import Plan
from ..core.task import Task
from ..core.artifact import Artifact, ArtifactType

class Planner:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def create_plan(self, session_id: str, prompt: str) -> Plan:
        """
        Uses LLM to break down the research prompt into a Plan.
        """
        system_prompt = '''
You are a master research planner. Break down the user's research goal into a series of distinct tasks.
Return a JSON array of tasks where each task object has:
- id: string (unique short id, e.g. "task_1")
- title: string
- description: string (detailed)
- expected_output: string
- dependencies: list of string (ids of tasks that must finish before this one)
Make sure the dependencies form a valid Directed Acyclic Graph (DAG).
'''
        # We expect the LLM to return JSON. In a real implementation we might use structured outputs.
        # For simplicity, we just extract json from the response.
        response = self.llm.generate_text(prompt, system_prompt=system_prompt)
        
        # Naive extraction of JSON block
        try:
            # Assuming the LLM returns well-formed JSON array
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            tasks_data = json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Failed to parse LLM plan response: {e}\nResponse was:\n{response}")

        plan = Plan(id=str(uuid.uuid4()), session_id=session_id, goal=prompt)
        
        for t_data in tasks_data:
            task = Task(
                id=t_data["id"],
                title=t_data["title"],
                description=t_data["description"],
                expected_output=t_data["expected_output"],
                dependencies=t_data.get("dependencies", [])
            )
            plan.add_task(task)
            
        return plan
        
    def generate_implementation_plan_artifact(self, plan: Plan) -> Artifact:
        """
        Creates an implementation_plan.md artifact as per Antigravity pattern.
        """
        content = f"# Implementation Plan\\n\\n## Goal\\n{plan.goal}\\n\\n## Proposed Tasks\\n\\n"
        for task_id, task in plan.tasks.items():
            deps = ", ".join(task.dependencies) if task.dependencies else "None"
            content += f"### {task.title} ({task_id})\\n"
            content += f"- **Description**: {task.description}\\n"
            content += f"- **Expected Output**: {task.expected_output}\\n"
            content += f"- **Dependencies**: {deps}\\n\\n"
            
        return Artifact(
            id=str(uuid.uuid4()),
            session_id=plan.session_id,
            name="implementation_plan.md",
            artifact_type=ArtifactType.MARKDOWN,
            content=content
        )
