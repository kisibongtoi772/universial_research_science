import sys
import argparse
import asyncio
from rich.console import Console
from rich.panel import Panel
from ..core.ports.llm import LLMProvider
from ..application.orchestrator import Orchestrator
from ..application.planner import Planner
from ..application.assigner import Assigner
from ..application.messaging import MessageBus
from ..infrastructure.storage.artifact_store import FileSystemArtifactStore
from ..infrastructure.llm.gemini import GeminiLLMProvider
from ..infrastructure.skills.registry import SkillRegistry
from ..infrastructure.execution.runner import ExecutionRunner

console = Console()

async def async_main():
    console.print(Panel.fit("[bold blue]Nexus Research Framework[/bold blue] (Antigravity-inspired)"))
    
    parser = argparse.ArgumentParser(description="Nexus Research Framework")
    parser.add_argument("prompt", nargs="?", help="The research prompt to start a new session")
    parser.add_argument("--resume", type=str, help="Resume an existing session ID")
    args = parser.parse_args()
    
    # 1. Bootstrapping dependencies
    llm = GeminiLLMProvider()
    store = FileSystemArtifactStore()
    registry = SkillRegistry()
    bus = MessageBus()
    
    planner = Planner(llm)
    assigner = Assigner(registry, llm)
    
    orchestrator = Orchestrator(
        llm_provider=llm,
        artifact_store=store,
        planner=planner,
        assigner=assigner,
        message_bus=bus
    )
    
    runner = ExecutionRunner(bus, store)
    
    try:
        if args.resume:
            console.print(f"[yellow]Resuming session {args.resume}...[/yellow]")
            plan = orchestrator.resume_session(args.resume)
            if not plan:
                return
            
            # Re-register agents
            for task in plan.tasks.values():
                if task.assigned_agent_id:
                    # Normally we'd load agent state, but here we rebuild it for simplicity
                    agent = assigner.assign_agent_to_task(task, context={"session_id": args.resume})
                    runner.register_agent(agent)
                    
            await runner.execute_plan(plan)
            console.print("[green]Session execution completed![/green]")
            
        elif args.prompt:
            console.print("[yellow]Analyzing prompt and generating Plan...[/yellow]")
            session_id = orchestrator.init_research_session(args.prompt)
            console.print(f"[green]Session initialized! ID:[/green] {session_id}")
            console.print("[green]Please review the Implementation Plan artifact in the session folder.[/green]")
        else:
            parser.print_help()
            
    except Exception as e:
        console.print(f"[red]Error during execution: {e}[/red]")

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
