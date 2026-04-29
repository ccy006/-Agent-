from __future__ import annotations

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.agent import BaseAgent
from core.context import RunContext
from core.models import FinalResult


class Orchestrator:
    def __init__(self, agents: list[BaseAgent], console: Console | None = None) -> None:
        self.agents = agents
        self.console = console or Console()

    def run(self, context: RunContext) -> FinalResult:
        context.report_dir.mkdir(parents=True, exist_ok=True)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            for agent in self.agents:
                task_id = progress.add_task(f"Running {agent.name}...", total=None)
                result = agent.run(context)
                context.agent_results.append(result)
                progress.update(task_id, description=f"{agent.name}: {result.summary}")
                progress.remove_task(task_id)
                self.console.print(f"[bold cyan]{agent.name}[/bold cyan] {result.summary}")

        report_path = context.report_dir / "refactor_report.md"

        return FinalResult(
            report_path=report_path,
            issues=context.issues,
            tasks=context.tasks,
            patches=context.patches,
            test_results=context.test_results,
        )
