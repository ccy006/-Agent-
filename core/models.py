from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


Severity = Literal["low", "medium", "high"]
IssueType = Literal[
    "todo",
    "fixme",
    "long_file",
    "long_function",
    "duplicate_block",
    "print_statement",
    "style",
    "test_failure",
]


@dataclass
class CodeIssue:
    issue_type: IssueType
    file_path: Path
    line: int
    severity: Severity
    message: str
    suggestion: str = ""


@dataclass
class RefactorTask:
    title: str
    file_path: Path
    priority: int
    risk: Literal["safe", "medium", "dangerous"]
    reason: str
    proposed_action: str
    related_issues: list[CodeIssue] = field(default_factory=list)


@dataclass
class Patch:
    file_path: Path
    before: str
    after: str
    description: str
    applied: bool = False


@dataclass
class TestResult:
    command: str
    passed: bool
    output: str


@dataclass
class AgentResult:
    name: str
    summary: str
    data: dict = field(default_factory=dict)


@dataclass
class FinalResult:
    report_path: Path
    issues: list[CodeIssue]
    tasks: list[RefactorTask]
    patches: list[Patch]
    test_results: list[TestResult]
