from pathlib import Path

from core.scanner import scan_file


def test_scan_file_detects_todo_and_print(tmp_path: Path):
    file_path = tmp_path / "x.py"
    file_path.write_text("# TODO: fix\nprint('hello')\n", encoding="utf-8")

    issues = scan_file(file_path, max_file_lines=10, max_function_lines=10)
    issue_types = {issue.issue_type for issue in issues}

    assert "todo" in issue_types
    assert "print_statement" in issue_types
