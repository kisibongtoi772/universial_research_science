from typing import List
import uuid
from ..core.task import Task
from ..core.agent import Agent, AgentRole
from ..infrastructure.skills.registry import SkillRegistry

from ..core.ports.llm import LLMProvider

# Note: In a complete system, we might dynamically generate Agent classes
# For this scaffold, we use a GenericAgent that uses the LLM to run.
class GenericAgent(Agent):
    llm: LLMProvider = None

    def execute_task(self, task: Task, context: dict) -> any:
        prompt = f"Task: {task.title}\nDescription: {task.description}\nExpected Output: {task.expected_output}"
        # We call the LLM and pass the agent's skills
        result = self.llm.execute_with_tools(
            prompt=prompt,
            system_prompt=self.role.system_prompt,
            tools=self.skills
        )
        task.result_summary = result
        return result

class Assigner:
    def __init__(self, skill_registry: SkillRegistry, llm_provider: LLMProvider):
        self.skill_registry = skill_registry
        self.llm = llm_provider

    def assign_agent_to_task(self, task: Task, context: dict = None) -> Agent:
        """
        Analyzes the task and builds an Agent equipped with the necessary role and skills.
        """
        # In a real scenario, we might use an LLM to select the skills.
        # Here we perform a simple heuristic or just assign all skills for demonstration.
        
        context = context or {}
        session_id = context.get("session_id", "unknown")
        
        # Simplified:
        role = AgentRole(
            name=f"Specialist for {task.title}",
            system_prompt=(f"You are a specialist responsible for: {task.title}. "
                           f"Provide output matching: {task.expected_output}. "
                           f"Your current Session ID is '{session_id}'. Use this ID when executing tools that require it.")
        )
        
        # In a robust system, we would match task description against skill descriptions
        # For now, we'll just give it access to available skills.
        skills = self.skill_registry.get_all_skills()
        
        agent = GenericAgent(
            id=str(uuid.uuid4()),
            role=role,
            skills=skills,
            llm=self.llm
        )
        task.assigned_agent_id = agent.id
        return agent
