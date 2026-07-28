# Nexus Research Framework

A robust, multi-agent AI research framework inspired by Google Antigravity. Built with Python, applying Clean Architecture and SOLID principles for scalability and maintainability.

## Architecture

The framework is structured into distinct layers:

- **`core/` (Domain Entities & Interfaces)**: 
  - `Agent`, `Task`, `Plan`, `Skill` definitions.
  - `Artifact System`: Structured files stored persistently in the workspace (JSON/Markdown) representing the state and outputs of the framework.
- **`application/` (Use Cases)**: 
  - `Planner`: Analyzes research prompts and creates a Directed Acyclic Graph (DAG) of tasks.
  - `Assigner`: Selects roles and equips agents with relevant skills (tools).
  - `Orchestrator`: Controls the overall session lifecycle (Planning Mode, Pause/Resume).
  - `Messaging`: A reactive message bus (Queue-based) for async agent communication and events.
- **`infrastructure/` (Implementations)**: 
  - `gemini.py`: Integration with Google GenAI, supporting **Function Calling** (tool loops with limits to prevent runaway tokens).
  - `artifact_store.py`: File-based artifact storage.
  - `registry.py`: Parses and loads agent skills from the environment.
  - `runner.py`: Executes the task DAG, saving states securely into `plan_state.json`.
- **`interfaces/`**: 
  - Rich-based CLI for starting and resuming sessions.

## Key Features

1. **Planning Mode**: Before executing complex tasks, the Planner generates an `implementation_plan.md` artifact outlining the DAG. Users can review it.
2. **Artifact System**: Agent outputs and session states are persistently stored in the `.sessions/` directory.
3. **Pause & Resume**: Safe interruptions. The framework automatically saves `plan_state.json` allowing you to resume the entire DAG exactly where it left off using `--resume`.
4. **Function Calling via Gemini**: Agents are equipped with schemas of your real-world skills. When they need to search data or fetch articles, the framework executes the python function directly on their behalf.

## Getting Started

1. Install dependencies:
   ```bash
   pip install pydantic google-genai rich python-dotenv
   ```
2. Set up your API key:
   ```bash
   export GEMINI_API_KEY="your-api-key"
   ```

### Start a New Session

```bash
python -m research_framework.interfaces.cli "Research the molecular mechanism of Alzheimer's disease"
```
*This will create a new session, generate an implementation plan, and start executing tasks.*

### Resume an Existing Session

If the system was stopped or paused, simply pass the session ID:

```bash
python -m research_framework.interfaces.cli --resume <session_id>
```