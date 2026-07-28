import subprocess

def run_git_push(commit_message: str) -> str:
    """
    Adds all files, commits, pulls with rebase, and pushes to the repository.
    """
    try:
        # Add all
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        
        # Commit
        commit_res = subprocess.run(
            ["git", "commit", "-m", commit_message], 
            capture_output=True, text=True
        )
        if "nothing to commit" in commit_res.stdout or "nothing to commit" in commit_res.stderr:
            return "No changes to commit."
            
        # Pull rebase
        subprocess.run(["git", "pull", "--rebase"], check=True, capture_output=True, text=True)
        
        # Push
        push_res = subprocess.run(["git", "push"], check=True, capture_output=True, text=True)
        return f"Git push successful! Output: {push_res.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Git operation failed during command '{' '.join(e.cmd)}': {e.stderr or e.output}"
    except Exception as e:
        return f"Error: {str(e)}"
