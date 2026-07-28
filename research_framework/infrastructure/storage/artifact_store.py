import os
import json
from typing import List, Optional
from ...core.ports.storage import ArtifactStore
from ...core.artifact import Artifact, ArtifactType

class FileSystemArtifactStore(ArtifactStore):
    def __init__(self, base_dir: str = ".sessions"):
        self.base_dir = base_dir

    def _get_session_dir(self, session_id: str) -> str:
        d = os.path.join(self.base_dir, session_id, "artifacts")
        os.makedirs(d, exist_ok=True)
        return d

    def save(self, artifact: Artifact) -> None:
        session_dir = self._get_session_dir(artifact.session_id)
        file_path = os.path.join(session_dir, artifact.name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(artifact.content)
            
        # Optional: Save metadata separately or as frontmatter
        meta_path = os.path.join(session_dir, f"{artifact.name}.meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(artifact.model_dump(mode='json'), f)

    def get(self, session_id: str, artifact_id: str) -> Optional[Artifact]:
        session_dir = self._get_session_dir(session_id)
        if not os.path.exists(session_dir):
            return None
            
        for file in os.listdir(session_dir):
            if file.endswith(".meta.json"):
                meta_path = os.path.join(session_dir, file)
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("id") == artifact_id:
                            return Artifact(**data)
                except Exception:
                    continue
        return None
        
    def list_by_session(self, session_id: str) -> List[Artifact]:
        # List all artifacts in the session dir
        return []
