from __future__ import annotations

from collections import defaultdict

from core.agent import BaseAgent
from core.context import RunContext
from core.models import AgentResult, RefactorTask


class PlannerAgent(BaseAgent):
    name = "PlannerAgent"

    def run(self, context: RunContext) -> AgentResult:
        by_file = defaultdict(list)
        for issue in context.issues:
            by_file[issue.file_path].append(issue)

        tasks: list[RefactorTask] = []

        for file_path, issues in by_file.items():
            severity_score = sum({"low": 1, "medium": 3, "high": 8}[i.severity] for i in issues)
            has_high = any(i.severity == "high" for i in issues)

            risk = "dangerous" if has_high else "safe"
            priority = min(10, severity_score)

            tasks.append(
                RefactorTask(
                    title=f"Clean technical debt in {context.relative(file_path)}",
                    file_path=file_path,
                    priority=priority,
                    risk=risk,
                    reason=f"{len(issues)} issue(s), severity score {severity_score}.",
                    proposed_action=self._build_action(issues),
                    related_issues=issues,
                )
            )

        tasks.sort(key=lambda t: (-t.priority, str(t.file_path)))
        context.tasks = tasks

        return AgentResult(
            name=self.name,
            summary=f"Created {len(tasks)} refactor tasks.",
            data={"task_count": len(tasks)},
        )

    def _build_action(self, issues) -> str:
        issue_types = {i.issue_type for i in issues}
        actions = []
        if "long_function" in issue_types:
            actions.append("Extract smaller functions from long functions.")
        if "long_file" in issue_types:
            actions.append("Split large module into cohesive files.")
        if "duplicate_block" in issue_types:
            actions.append("Extract duplicated code into a shared helper.")
        if "todo" in issue_types or "fixme" in issue_types:
            actions.append("Resolve TODO/FIXME comments or create tracked tickets.")
        if "print_statement" in issue_types:
            actions.append("Replace print statements with logging.")
        if not actions:
            actions.append("Apply formatting and minor cleanup.")
        return " ".join(actions)
