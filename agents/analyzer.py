from __future__ import annotations

from core.agent import BaseAgent
from core.context import RunContext
from core.models import AgentResult
from core.scanner import iter_code_files, scan_file, detect_duplicate_blocks


class AnalyzerAgent(BaseAgent):
    name = "AnalyzerAgent"

    def run(self, context: RunContext) -> AgentResult:
        files = iter_code_files(context.target_dir)
        issues = []

        for file_path in files:
            issues.extend(
                scan_file(
                    file_path,
                    max_file_lines=context.max_file_lines,
                    max_function_lines=context.max_function_lines,
                )
            )

        issues.extend(detect_duplicate_blocks(files))
        context.issues = issues

        counts: dict[str, int] = {}
        for issue in issues:
            counts[issue.issue_type] = counts.get(issue.issue_type, 0) + 1

        return AgentResult(
            name=self.name,
            summary=f"Found {len(issues)} issues in {len(files)} Python files.",
            data={"issue_counts": counts, "file_count": len(files)},
        )
