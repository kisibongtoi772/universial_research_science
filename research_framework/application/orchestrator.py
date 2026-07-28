import json
import uuid
from typing import Dict, Any, Optional
from .planner import Planner
from .assigner import Assigner
from .messaging import MessageBus
from ..core.ports.storage import ArtifactStore
from ..core.ports.llm import LLMProvider
from ..core.artifact import Artifact, ArtifactType
from ..core.plan import Plan

class Orchestrator:
    def __init__(self, 
                 llm_provider: LLMProvider, 
                 artifact_store: ArtifactStore, 
                 planner: Planner,
                 assigner: Assigner,
                 message_bus: MessageBus):
        self.llm = llm_provider
        self.artifact_store = artifact_store
        self.planner = planner
        self.assigner = assigner
        self.bus = message_bus

    def _save_plan_state(self, plan: Plan):
        """Saves the current plan state to the artifact store"""
        artifact = Artifact(
            id="plan_state",
            session_id=plan.session_id,
            name="plan_state.json",
            artifact_type=ArtifactType.JSON,
            content=plan.model_dump_json()
        )
        self.artifact_store.save(artifact)

    def init_research_session(self, prompt: str) -> str:
        """
        Initializes a new session and returns the session ID.
        In Planning Mode, it generates an implementation plan artifact and pauses.
        """
        session_id = str(uuid.uuid4())
        
        # 1. Plan
        plan = self.planner.create_plan(session_id, prompt)
        
        # 2. Assign agents to tasks
        for task in plan.tasks.values():
            self.assigner.assign_agent_to_task(task)
            
        # 3. Save Plan State to storage
        self._save_plan_state(plan)
        
        # 4. Generate Implementation Plan Artifact for User Review
        plan_artifact = self.planner.generate_implementation_plan_artifact(plan)
        self.artifact_store.save(plan_artifact)
        
        print(f"Session {session_id} initialized.")
        print(f"Implementation Plan artifact created: {plan_artifact.id}")
        return session_id

    def resume_session(self, session_id: str) -> Optional[Plan]:
        """
        Loads the plan_state.json and resumes the session.
        """
        artifact = self.artifact_store.get(session_id, "plan_state")
        if not artifact:
            print(f"Error: Could not find plan_state.json for session {session_id}")
            return None
            
        plan_dict = json.loads(artifact.content)
        plan = Plan(**plan_dict)
        print(f"Session {session_id} resumed successfully.")
        print(f"Goal: {plan.goal}")
        return plan

