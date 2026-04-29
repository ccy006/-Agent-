from __future__ import annotations

from datetime import datetime

from core.agent import BaseAgent
from core.context import RunContext
from core.models import AgentResult


class ReviewerAgent(BaseAgent):
    name = "ReviewerAgent"

    def run(self, context: RunContext) -> AgentResult:
        context.report_dir.mkdir(parents=True, exist_ok=True)
        report_path = context.report_dir / "refactor_report.md"

        report = self._build_report(context)
        report_path.write_text(report, encoding="utf-8")

        return AgentResult(
            name=self.name,
            summary=f"Wrote report to {report_path}.",
            data={"report_path": str(report_path)},
        )

    def _build_report(self, context: RunContext) -> str:
        lines: list[str] = []
        lines.append("# Multi-Agent Refactor Report")
        lines.append("")
        lines.append(f"- Generated at: {datetime.now().isoformat(timespec='seconds')}")
        lines.append(f"- Target: `{context.target_dir}`")
        lines.append(f"- Mode: `{'APPLY' if context.apply_changes else 'DRY RUN'}`")
        lines.append("")

        lines.append("## Agent Summaries")
        lines.append("")
        for result in context.agent_results:
            lines.append(f"- **{result.name}**: {result.summary}")
        lines.append("")

        lines.append("## Issues")
        lines.append("")
        if not context.issues:
            lines.append("No issues found.")
        else:
            lines.append("| Severity | Type | File | Line | Message | Suggestion |")
            lines.append("|---|---|---:|---:|---|---|")
            for issue in context.issues:
                lines.append(
                    f"| {issue.severity} | {issue.issue_type} | "
                    f"`{context.relative(issue.file_path)}` | {issue.line} | "
                    f"{issue.message} | {issue.suggestion} |"
                )
        lines.append("")

        lines.append("## Refactor Plan")
        lines.append("")
        if not context.tasks:
            lines.append("No refactor tasks created.")
        else:
            lines.append("| Priority | Risk | File | Task | Action |")
            lines.append("|---:|---|---:|---|---|")
            for task in context.tasks:
                lines.append(
                    f"| {task.priority} | {task.risk} | `{context.relative(task.file_path)}` | "
                    f"{task.title} | {task.proposed_action} |"
                )
        lines.append("")

        lines.append("## Patches")
        lines.append("")
        if not context.patches:
            lines.append("No safe patches generated.")
        else:
            for patch in context.patches:
                status = "applied" if patch.applied else "dry-run"
                lines.append(f"### `{context.relative(patch.file_path)}`")
                lines.append("")
                lines.append(f"- Status: `{status}`")
                lines.append(f"- Description: {patch.description}")
                lines.append("")

        lines.append("## Test Results")
        lines.append("")
        if not context.test_results:
            lines.append("No tests/checks executed.")
        else:
            lines.append("| Passed | Command | Output |")
            lines.append("|---|---|---|")
            for result in context.test_results:
                out = result.output.replace("\n", "<br>")
                lines.append(f"| {result.passed} | `{result.command}` | {out} |")
        lines.append("")

        lines.append("## Reviewer Notes")
        lines.append("")
        if any(not r.passed for r in context.test_results):
            lines.append("- Some checks failed. Do not merge before fixing failures.")
        elif context.patches:
            lines.append("- Safe patches are ready. Review report and commit changes incrementally.")
        else:
            lines.append("- No automatic patch was necessary. Use the plan section for manual cleanup.")

        return "\n".join(lines)
