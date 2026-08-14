"""B6 P1 — real new-process resume smoke test.

The Wave F3 target: "服务重启后能从 transcript + 安全 metadata 重建常见后台
Agent". A terminal background agent is written by ONE fresh Python interpreter
(transcript + DurableResumeMetadata on disk) and resumed by a SECOND fresh
interpreter that re-resolves provider / tool registry / agent definition from
its own process — the exact "service restart" scenario, not a same-process
re-entry.

Verifies across the process boundary:
* transcript + metadata survive (replayed_message_count > 0);
* the winner claims the terminal state and lands a fresh ``running`` state;
* current-process dependencies are rebuilt (not persisted live objects);
* the resumed run drives a real background thread and persists a terminal
  result through the stub run_agent.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

_WRITER_SCRIPT = textwrap.dedent("""\
    import os
    import sys
    from pathlib import Path
    from types import SimpleNamespace

    workspace = Path(sys.argv[1])
    os.environ["CLAWCODEX_CONFIG_DIR"] = str(Path(sys.argv[2]))

    from src.agent.transcript import TranscriptWriter
    from src.tasks.local_agent import complete_agent_task, register_async_agent
    from src.tasks_core import generate_task_id
    from src.tool_system.context import ToolContext

    ctx = ToolContext(workspace_root=workspace)
    agent_id = generate_task_id("local_agent")
    # parent_context records workspace_root into the durable metadata, so the
    # resumer's current-process workspace must match (the restart path guard).
    register_async_agent(
        agent_id=agent_id,
        description="durable",
        prompt="initial",
        agent_type="general-purpose",
        model="test-model",
        resume_run_params=SimpleNamespace(parent_context=ctx),
        registry=ctx.runtime_tasks,
    )
    with TranscriptWriter(ctx.runtime_tasks.get(agent_id).output_file) as w:
        w.append({"role": "user", "content": "hello"})
        w.append({"role": "assistant", "content": "world"})
    complete_agent_task(agent_id, result_text="done", registry=ctx.runtime_tasks)
    print(agent_id)
""")

_RESUMER_SCRIPT = textwrap.dedent("""\
    import asyncio
    import os
    import sys
    import time
    from pathlib import Path
    from types import SimpleNamespace

    workspace = Path(sys.argv[1])
    os.environ["CLAWCODEX_CONFIG_DIR"] = str(Path(sys.argv[2]))
    agent_id = sys.argv[3]

    from src.agent.resume_agent import resume_agent_background
    from src.tool_system.context import ToolContext
    from src.tool_system.defaults import build_default_registry
    from src.types.messages import AssistantMessage

    # The provider/tool registry live in THIS process only — the whole point
    # of the restart path. The resumed run must complete without a real model,
    # so stub run_agent in this fresh process. NOTE: ``src.agent.run_agent``
    # as an attribute resolves to the re-exported FUNCTION, so patch the real
    # module via importlib.
    import importlib

    run_agent_mod = importlib.import_module("src.agent.run_agent")

    async def fake_run_agent(params):
        yield AssistantMessage(content="resumed in new process")

    run_agent_mod.run_agent = fake_run_agent

    ctx = ToolContext(workspace_root=workspace)
    ctx.tool_registry = build_default_registry()
    ctx._active_provider = SimpleNamespace(model="current-model")

    result = asyncio.run(resume_agent_background(
        agent_id=agent_id, prompt="wake up after restart", context=ctx,
    ))
    assert result.resumed is True, result.reason
    assert result.replayed_message_count == 2, result.replayed_message_count

    state = ctx.runtime_tasks.get(agent_id)
    assert state.status == "running", state.status

    # Let the resumed background thread run to completion through the stub.
    for _ in range(400):
        s = ctx.runtime_tasks.get(agent_id)
        if getattr(s, "status", None) in ("completed", "failed"):
            break
        time.sleep(0.05)
    final = ctx.runtime_tasks.get(agent_id)
    assert final.status == "completed", final.status
    assert final.result_text == "resumed in new process", final.result_text
    print("RESUME_OK")
""")


def _run_child(script: str, *args: str, tmp_path: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["CLAWCODEX_CONFIG_DIR"] = str(tmp_path / "config")
    return subprocess.run(
        [sys.executable, "-c", script, *args],
        cwd=Path(__file__).resolve().parents[1],  # repo root → `src` importable
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_resume_across_two_fresh_processes(tmp_path: Path) -> None:
    workspace = tmp_path / "repo"
    workspace.mkdir()

    writer = _run_child(_WRITER_SCRIPT, str(workspace), str(tmp_path), tmp_path=tmp_path)
    assert writer.returncode == 0, writer.stderr
    agent_id = writer.stdout.strip().splitlines()[-1]
    assert agent_id

    resumer = _run_child(
        _RESUMER_SCRIPT, str(workspace), str(tmp_path), agent_id, tmp_path=tmp_path
    )
    assert resumer.returncode == 0, resumer.stderr
    assert "RESUME_OK" in resumer.stdout
