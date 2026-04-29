from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from core.models import CodeIssue, RefactorTask, Patch, TestResult, AgentResult


@dataclass
class RunContext:
    target_dir: Path
    report_dir: Path
    apply_changes: bool = False
    max_file_lines: int = 400
    max_function_lines: int = 80

    issues: list[CodeIssue] = field(default_factory=list)
    tasks: list[RefactorTask] = field(default_factory=list)
    patches: list[Patch] = field(default_factory=list)
    test_results: list[TestResult] = field(default_factory=list)
    agent_results: list[AgentResult] = field(default_factory=list)

    def relative(self, path: Path) -> Path:
        try:
            return path.resolve().relative_to(self.target_dir)
        except ValueError:
            return path
