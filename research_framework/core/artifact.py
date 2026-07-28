from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ArtifactType(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    TEXT = "text"
    CODE = "code"

class Artifact(BaseModel):
    id: str = Field(..., description="Unique identifier for the artifact")
    session_id: str = Field(..., description="The session this artifact belongs to")
    name: str = Field(..., description="Name of the artifact (e.g. 'research_notes.md')")
    artifact_type: ArtifactType = Field(default=ArtifactType.MARKDOWN)
    content: str = Field(default="", description="The text content of the artifact")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def update_content(self, new_content: str):
        self.content = new_content
        self.updated_at = datetime.utcnow()
