import os
import subprocess

def run_python_sandbox(session_id: str, experiment_name: str, code: str, dependencies: list = None) -> str:
    """
    Creates an isolated environment using uv and runs the python code.
    """
    base_dir = os.path.join(".sessions", session_id, "experiments", experiment_name)
    os.makedirs(base_dir, exist_ok=True)
    
    # Write code to main.py
    script_path = os.path.join(base_dir, "main.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)
        
    try:
        # Create venv if not exists
        venv_dir = os.path.join(base_dir, ".venv")
        if not os.path.exists(venv_dir):
            subprocess.run(["uv", "venv", venv_dir], check=True, capture_output=True, text=True)
            
        # Install dependencies
        if dependencies:
            pip_cmd = ["uv", "pip", "install", "--python", venv_dir] + dependencies
            subprocess.run(pip_cmd, check=True, capture_output=True, text=True)
            
        # Run code
        python_bin = os.path.join(venv_dir, "bin", "python")
        if os.name == 'nt':
            python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
            
        result = subprocess.run([python_bin, script_path], capture_output=True, text=True, timeout=300)
        
        output = f"Exit code: {result.returncode}\n"
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
            
        return output
        
    except subprocess.TimeoutExpired:
        return "Error: Execution timed out after 300 seconds."
    except subprocess.CalledProcessError as e:
        return f"Error during setup/execution: {e.stderr or e.output}"
    except Exception as e:
        return f"Error executing sandbox: {str(e)}"
