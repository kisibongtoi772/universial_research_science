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
        
        # Load git_push dynamically
        git_push_script = os.path.join(".agents", "skills", "builtin-git-push", "scripts", "git_push.py")
        if os.path.exists(git_push_script):
            import importlib.util
            spec = importlib.util.spec_from_file_location("builtin_git_push", git_push_script)
            git_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(git_module)
            
            git_skill = Skill(
                name="builtin_git_push",
                description="Commits and pushes all current workspace changes to the git repository.",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "commit_message": {"type": "string", "description": "The commit message explaining the changes"}
                    },
                    "required": ["commit_message"]
                },
                executable=git_module.run_git_push
            )
            self.skills.append(git_skill)

    def get_all_skills(self) -> List[Skill]:
        return self.skills
