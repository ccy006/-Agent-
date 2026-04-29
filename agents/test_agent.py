from __future__ import annotations

import subprocess
import sys

from core.agent import BaseAgent
from core.context import RunContext
from core.models import AgentResult, TestResult


class TestAgent(BaseAgent):
    name = "TestAgent"

    def run(self, context: RunContext) -> AgentResult:
        results: list[TestResult] = []

        commands = [
            [sys.executable, "-m", "compileall", "-q", str(context.target_dir)],
        ]

        tests_dir = context.target_dir / "tests"
        if tests_dir.exists():
            commands.append([sys.executable, "-m", "pytest", str(tests_dir), "-q"])

        for command in commands:
            completed = subprocess.run(
                command,
                cwd=context.target_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = (completed.stdout or "") + (completed.stderr or "")
            results.append(
                TestResult(
                    command=" ".join(command),
                    passed=completed.returncode == 0,
                    output=output.strip(),
                )
            )

        context.test_results = results
        passed = sum(1 for r in results if r.passed)

        return AgentResult(
            name=self.name,
            summary=f"{passed}/{len(results)} checks passed.",
            data={"passed": passed, "total": len(results)},
        )
