from __future__ import annotations

import ast
import hashlib
from collections import defaultdict
from pathlib import Path

from core.models import CodeIssue


PYTHON_EXTENSIONS = {".py"}
IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache"}


def iter_code_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in PYTHON_EXTENSIONS:
            files.append(path)
    return files


def scan_file(
    path: Path,
    max_file_lines: int,
    max_function_lines: int,
) -> list[CodeIssue]:
    issues: list[CodeIssue] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    if len(lines) > max_file_lines:
        issues.append(
            CodeIssue(
                issue_type="long_file",
                file_path=path,
                line=1,
                severity="medium",
                message=f"File has {len(lines)} lines.",
                suggestion="Consider splitting this file into smaller modules.",
            )
        )

    for idx, line in enumerate(lines, start=1):
        lowered = line.lower()
        if "todo" in lowered:
            issues.append(
                CodeIssue(
                    issue_type="todo",
                    file_path=path,
                    line=idx,
                    severity="low",
                    message="TODO comment found.",
                    suggestion="Convert TODO into a tracked task or resolve it.",
                )
            )
        if "fixme" in lowered:
            issues.append(
                CodeIssue(
                    issue_type="fixme",
                    file_path=path,
                    line=idx,
                    severity="medium",
                    message="FIXME comment found.",
                    suggestion="Prioritize this fix because it may indicate known broken behavior.",
                )
            )
        if "print(" in line and not line.lstrip().startswith("#"):
            issues.append(
                CodeIssue(
                    issue_type="print_statement",
                    file_path=path,
                    line=idx,
                    severity="low",
                    message="print() statement found.",
                    suggestion="Replace print() with structured logging where appropriate.",
                )
            )

    try:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if hasattr(node, "lineno") and hasattr(node, "end_lineno") and node.end_lineno:
                    function_len = node.end_lineno - node.lineno + 1
                    if function_len > max_function_lines:
                        issues.append(
                            CodeIssue(
                                issue_type="long_function",
                                file_path=path,
                                line=node.lineno,
                                severity="medium",
                                message=f"Function `{node.name}` has {function_len} lines.",
                                suggestion="Extract smaller functions and isolate side effects.",
                            )
                        )
    except SyntaxError as exc:
        issues.append(
            CodeIssue(
                issue_type="style",
                file_path=path,
                line=exc.lineno or 1,
                severity="high",
                message=f"Syntax error: {exc.msg}",
                suggestion="Fix syntax before automatic refactoring.",
            )
        )

    return issues


def detect_duplicate_blocks(files: list[Path], block_size: int = 8) -> list[CodeIssue]:
    fingerprints: dict[str, list[tuple[Path, int]]] = defaultdict(list)

    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = [line.strip() for line in text.splitlines()]
        for start in range(0, max(0, len(lines) - block_size + 1)):
            block = "\n".join(lines[start : start + block_size])
            if not block or len(block) < 80:
                continue
            digest = hashlib.sha256(block.encode("utf-8")).hexdigest()
            fingerprints[digest].append((path, start + 1))

    issues: list[CodeIssue] = []
    for locations in fingerprints.values():
        if len(locations) <= 1:
            continue
        for path, line in locations:
            issues.append(
                CodeIssue(
                    issue_type="duplicate_block",
                    file_path=path,
                    line=line,
                    severity="medium",
                    message=f"Possible duplicated {block_size}-line block.",
                    suggestion="Extract duplicated logic into a shared function or module.",
                )
            )
    return issues
