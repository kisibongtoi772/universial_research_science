import os
from typing import List
from ...core.skill import Skill

class SkillRegistry:
    def __init__(self, search_paths: List[str] = None):
        if not search_paths:
            # Default locations for agent skills
            self.search_paths = [
                os.path.expanduser("~/.gemini/config/plugins/science/skills"),
                ".agents/skills"
            ]
        else:
            self.search_paths = search_paths
            
        self.skills = []
        self._load_skills()

    def _load_skills(self):
        """
        Scans paths for SKILL.md files and parses YAML frontmatter 
        to build the Skill objects.
        """
        # For prototype, we'll create a dummy skill
        # A real implementation would parse the YAML and dynamically import scripts
        dummy_skill = Skill(
            name="mock_search",
            description="Searches the web or literature for a topic.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            },
            executable=lambda query: f"Mock results for {query}"
        )
        self.skills.append(dummy_skill)

    def get_all_skills(self) -> List[Skill]:
        return self.skills
