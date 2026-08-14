from __future__ import annotations

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from src.tool_system.context import ToolContext
from src.tool_system.tools.read import _read_call


def _write_rule(root: Path) -> Path:
    rule = root / ".clawcodex" / "rules" / "python.md"
    rule.parent.mkdir(parents=True)
    rule.write_text(
        "---\npaths:\n  - src/**/*.py\n---\n生产 Python 文件必须记录失败策略。\n",
        encoding="utf-8",
    )
    return rule


def test_read_matching_file_injects_path_rule_once(tmp_path):
    rule = _write_rule(tmp_path)
    target = tmp_path / "src" / "service" / "worker.py"
    target.parent.mkdir(parents=True)
    target.write_text("print('ok')\n", encoding="utf-8")
    context = ToolContext(workspace_root=tmp_path)

    first = _read_call({"file_path": str(target)}, context)
    second = _read_call({"file_path": str(target)}, context)

    assert first.new_messages is not None
    text = first.new_messages[0].content
    assert "生产 Python 文件必须记录失败策略" in text
    assert "path-scoped project instructions" in text
    assert second.new_messages is None
    assert rule.resolve() in context.loaded_path_rule_files


def test_read_unmatched_file_does_not_inject_path_rule(tmp_path):
    _write_rule(tmp_path)
    target = tmp_path / "README.md"
    target.write_text("hello\n", encoding="utf-8")
    context = ToolContext(workspace_root=tmp_path)

    result = _read_call({"file_path": str(target)}, context)

    assert result.new_messages is None
    assert context.loaded_path_rule_files == set()


def test_path_rule_claim_is_atomic_for_concurrent_reads(tmp_path):
    rule = _write_rule(tmp_path).resolve()
    context = ToolContext(workspace_root=tmp_path)

    with ThreadPoolExecutor(max_workers=8) as pool:
        claimed = list(pool.map(lambda _: context.claim_path_rules([rule]), range(32)))

    assert sum(1 for batch in claimed if batch == [rule]) == 1
    assert sum(1 for batch in claimed if batch == []) == 31


def test_project_rule_symlink_escape_is_not_injected(tmp_path):
    external = tmp_path.parent / f"{tmp_path.name}-external-rule.md"
    external.write_text(
        "---\npaths:\n  - src/**/*.py\n---\n不应加载的外部规则。\n",
        encoding="utf-8",
    )
    rules_dir = tmp_path / ".clawcodex" / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "escape.md").symlink_to(external)
    target = tmp_path / "src" / "worker.py"
    target.parent.mkdir()
    target.write_text("print('ok')\n", encoding="utf-8")
    context = ToolContext(workspace_root=tmp_path)

    result = _read_call({"file_path": str(target)}, context)

    assert result.new_messages is None
    assert context.loaded_path_rule_files == set()
