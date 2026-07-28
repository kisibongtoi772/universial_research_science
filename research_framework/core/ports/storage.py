from abc import ABC, abstractmethod
from typing import List, Optional
from ..artifact import Artifact

class ArtifactStore(ABC):
    @abstractmethod
    def save(self, artifact: Artifact) -> None:
        pass
        
    @abstractmethod
    def get(self, session_id: str, artifact_id: str) -> Optional[Artifact]:
        pass
        
    @abstractmethod
    def list_by_session(self, session_id: str) -> List[Artifact]:
        pass
