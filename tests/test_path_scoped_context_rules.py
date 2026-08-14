"""验证路径规则按真实配置作用域延迟注入 Read 结果。"""

from __future__ import annotations

import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from src.providers.base import ChatResponse
from src.query.query import QueryParams, query
from src.tool_system.defaults import build_default_registry
from src.tool_system.context import ToolContext
from src.tool_system.tools.read import _read_call
from src.context_system.clawcodex_md import get_path_scoped_rules
from src.types.messages import UserMessage
from src.utils.abort_controller import AbortController


def _write_rule(root: Path) -> Path:
    rule = root / ".clawcodex" / "rules" / "python.md"
    rule.parent.mkdir(parents=True)
    rule.write_text(
        "---\npaths:\n  - src/**/*.py\n---\n生产 Python 文件必须记录失败策略。\n",
        encoding="utf-8",
    )
    return rule


def _write_scoped_rule(
    rules_dir: Path,
    *,
    name: str,
    pattern: str,
    instruction: str,
) -> Path:
    rule = rules_dir / f"{name}.md"
    rule.parent.mkdir(parents=True, exist_ok=True)
    rule.write_text(
        f"---\npaths:\n  - {pattern}\n---\n{instruction}\n",
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
    assert "path-scoped instructions" in text
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


def test_managed_user_and_project_rules_share_one_matcher(tmp_path):
    workspace = tmp_path / "repo"
    managed = tmp_path / "managed"
    user = tmp_path / "user"
    target = workspace / "src" / "worker.py"
    target.parent.mkdir(parents=True)
    target.write_text("print('ok')\n", encoding="utf-8")
    _write_scoped_rule(
        managed / "rules",
        name="managed",
        pattern="src/**/*.py",
        instruction="企业策略要求记录失败边界。",
    )
    _write_scoped_rule(
        user / "rules",
        name="user",
        pattern="src/**/*.py",
        instruction="用户规则要求说明输入来源。",
    )
    _write_scoped_rule(
        workspace / ".clawcodex" / "rules",
        name="project",
        pattern="src/**/*.py",
        instruction="项目规则要求覆盖回归测试。",
    )

    rules = get_path_scoped_rules(
        target,
        workspace,
        managed_config_dir=managed,
        user_config_dir=user,
    )

    assert [rule.type for rule in rules] == ["Managed", "User", "Project"]
    assert [rule.content.strip() for rule in rules] == [
        "企业策略要求记录失败边界。",
        "用户规则要求说明输入来源。",
        "项目规则要求覆盖回归测试。",
    ]


def test_nested_project_rule_is_discovered_between_cwd_and_target(tmp_path):
    target = tmp_path / "src" / "service" / "worker.py"
    target.parent.mkdir(parents=True)
    target.write_text("print('ok')\n", encoding="utf-8")
    nested_rule = _write_scoped_rule(
        target.parent / ".clawcodex" / "rules",
        name="service",
        pattern="worker.py",
        instruction="服务目录规则要求保持任务幂等。",
    )

    rules = get_path_scoped_rules(target, tmp_path, scopes=("Project",))

    assert [Path(rule.path) for rule in rules] == [nested_rule.resolve()]
    assert rules[0].content.strip() == "服务目录规则要求保持任务幂等。"


def test_read_injects_managed_user_and_nested_rules_once(tmp_path, monkeypatch):
    workspace = tmp_path / "repo"
    managed = tmp_path / "managed"
    user = tmp_path / "user"
    target = workspace / "src" / "service" / "worker.py"
    target.parent.mkdir(parents=True)
    target.write_text("print('ok')\n", encoding="utf-8")
    monkeypatch.setenv("CLAWCODEX_MANAGED_CONFIG_DIR", str(managed))
    monkeypatch.setenv("CLAWCODEX_CONFIG_DIR", str(user))
    _write_scoped_rule(managed / "rules", name="m", pattern="src/**/*.py", instruction="托管规则。")
    _write_scoped_rule(user / "rules", name="u", pattern="src/**/*.py", instruction="用户规则。")
    _write_scoped_rule(
        target.parent / ".clawcodex" / "rules",
        name="n",
        pattern="worker.py",
        instruction="嵌套项目规则。",
    )
    context = ToolContext(workspace_root=workspace)

    first = _read_call({"file_path": str(target)}, context)
    second = _read_call({"file_path": str(target)}, context)

    assert first.new_messages is not None
    attached = first.new_messages[0].content
    assert "托管规则。" in attached
    assert "用户规则。" in attached
    assert "嵌套项目规则。" in attached
    assert second.new_messages is None


def test_matching_rule_reaches_next_model_call_exactly_once(tmp_path, monkeypatch):
    workspace = tmp_path / "repo"
    target = workspace / "src" / "service" / "worker.py"
    target.parent.mkdir(parents=True)
    target.write_text("print('ok')\n", encoding="utf-8")
    monkeypatch.setenv("CLAWCODEX_MANAGED_CONFIG_DIR", str(tmp_path / "empty-managed"))
    monkeypatch.setenv("CLAWCODEX_CONFIG_DIR", str(tmp_path / "empty-user"))
    instruction = "模型下一轮必须看到且只能看到一次本规则。"
    _write_scoped_rule(
        target.parent / ".clawcodex" / "rules",
        name="next-turn",
        pattern="worker.py",
        instruction=instruction,
    )
    registry = build_default_registry()
    context = ToolContext(workspace_root=workspace)
    provider = MagicMock()
    provider.chat_stream_response.side_effect = NotImplementedError()
    provider.chat.side_effect = [
        ChatResponse(
            content="读取文件。",
            model="test",
            usage={"input_tokens": 1, "output_tokens": 1},
            finish_reason="tool_use",
            tool_uses=[{
                "id": "toolu_read",
                "name": "Read",
                "input": {"file_path": str(target)},
            }],
        ),
        ChatResponse(
            content="完成。",
            model="test",
            usage={"input_tokens": 1, "output_tokens": 1},
            finish_reason="end_turn",
            tool_uses=None,
        ),
    ]
    params = QueryParams(
        messages=[UserMessage(content="读取 worker.py")],
        system_prompt="执行测试。",
        tools=registry.list_tools(),
        tool_registry=registry,
        tool_use_context=context,
        provider=provider,
        abort_controller=AbortController(),
        max_turns=3,
    )

    async def run_query() -> None:
        async for _ in query(params):
            pass

    asyncio.run(run_query())

    assert provider.chat.call_count == 2
    next_model_messages = provider.chat.call_args_list[1].args[0]
    assert repr(next_model_messages).count(instruction) == 1
