---
name: builtin_git_push
description: Commits and pushes all current workspace changes to the git repository.
parameters:
  type: object
  properties:
    commit_message:
      type: string
      description: The commit message explaining the changes
  required:
    - commit_message
---

# Built-in Git Push Skill

Provides an agent with the ability to safely add all changes, commit them with a message, pull with rebase to sync upstream changes, and push back to the remote repository.

## Execution
This skill relies on the framework's internal registry loading the python script rather than being called as a standalone CLI tool.
