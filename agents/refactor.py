from __future__ import annotations

from core.agent import BaseAgent
from core.context import RunContext
from core.models import AgentResult, Patch


class RefactorAgent(BaseAgent):
    name = "RefactorAgent"

    def run(self, context: RunContext) -> AgentResult:
        patches: list[Patch] = []

        safe_tasks = [task for task in context.tasks if task.risk == "safe"]

        for task in safe_tasks:
            path = task.file_path
            before = path.read_text(encoding="utf-8", errors="ignore")
            after = self._safe_cleanup(before)

            if before != after:
                patch = Patch(
                    file_path=path,
                    before=before,
                    after=after,
                    description="Applied safe whitespace cleanup.",
                    applied=False,
                )

                if context.apply_changes:
                    path.write_text(after, encoding="utf-8")
                    patch.applied = True

                patches.append(patch)

        context.patches = patches

        mode = "applied" if context.apply_changes else "prepared"
        return AgentResult(
            name=self.name,
            summary=f"{mode} {len(patches)} safe patch(es).",
            data={"patch_count": len(patches), "apply_changes": context.apply_changes},
        )

    def _safe_cleanup(self, text: str) -> str:
        lines = [line.rstrip() for line in text.splitlines()]
        return "\n".join(lines) + "\n"
