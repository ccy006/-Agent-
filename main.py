from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from core.context import RunContext
from core.orchestrator import Orchestrator
from agents.analyzer import AnalyzerAgent
from agents.planner import PlannerAgent
from agents.refactor import RefactorAgent
from agents.test_agent import TestAgent
from agents.reviewer import ReviewerAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Multi-Agent Code Refactoring / Technical Debt Cleanup System"
    )
    parser.add_argument("--target", required=True, help="Target project directory")
    parser.add_argument("--out", default="./reports", help="Output report directory")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply safe automatic refactors. Without this flag, dry-run only.",
    )
    parser.add_argument(
        "--max-file-lines",
        type=int,
        default=400,
        help="Files longer than this are marked as technical debt.",
    )
    parser.add_argument(
        "--max-function-lines",
        type=int,
        default=80,
        help="Functions longer than this are marked as technical debt.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    console = Console()

    context = RunContext(
        target_dir=Path(args.target).resolve(),
        report_dir=Path(args.out).resolve(),
        apply_changes=args.apply,
        max_file_lines=args.max_file_lines,
        max_function_lines=args.max_function_lines,
    )

    if not context.target_dir.exists():
        raise FileNotFoundError(f"Target directory not found: {context.target_dir}")

    orchestrator = Orchestrator(
        agents=[
            AnalyzerAgent(),
            PlannerAgent(),
            RefactorAgent(),
            TestAgent(),
            ReviewerAgent(),
        ],
        console=console,
    )

    console.print(
        Panel.fit(
            f"[bold]Target:[/bold] {context.target_dir}\n"
            f"[bold]Mode:[/bold] {'APPLY' if context.apply_changes else 'DRY RUN'}",
            title="Multi-Agent Refactor System",
        )
    )

    result = orchestrator.run(context)

    console.print("\n[bold green]Done.[/bold green]")
    console.print(f"Report: [cyan]{result.report_path}[/cyan]")


if __name__ == "__main__":
    main()
