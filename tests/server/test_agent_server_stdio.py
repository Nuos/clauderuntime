"""验证本地 TUI 通过标准输入输出连接 Agent 服务的完整生命周期。

该业务链路使用 NDJSON 管道传输，避免 WebSocket 空闲断开。测试启动真实子进程，
确认服务先输出 ``system/init`` JSON 帧，并在父进程关闭输入后正常退出。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]


def test_stdio_emits_init_and_exits_on_stdin_close(tmp_path: Path) -> None:
    env = {
        **os.environ,
        "PYTHONPATH": str(_REPO),
        "PYTHONUNBUFFERED": "1",
        # 子进程会创建会话索引；必须写入测试临时目录，禁止污染真实用户数据。
        "CLAWCODEX_CONFIG_DIR": str(tmp_path / ".clawcodex"),
    }
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "src.entrypoints.agent_server_cli",
            "--stdio", "--permission-mode", "bypassPermissions",
            "--workspace", str(tmp_path),
        ],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1, env=env, cwd=str(_REPO),
    )

    frames: list[dict] = []
    non_json: list[str] = []

    def _reader() -> None:
        assert proc.stdout is not None
        for line in proc.stdout:
            s = line.strip()
            if not s:
                continue
            try:
                frames.append(json.loads(s))
            except json.JSONDecodeError:
                non_json.append(s)

    threading.Thread(target=_reader, daemon=True).start()

    try:
        # 1) system/init shows up on stdout within a generous startup window.
        deadline = time.time() + 50
        while time.time() < deadline and not any(
            f.get("type") == "system" and f.get("subtype") == "init" for f in frames
        ):
            time.sleep(0.2)
        assert any(
            f.get("type") == "system" and f.get("subtype") == "init" for f in frames
        ), f"no system/init frame on stdout (got types={[f.get('type') for f in frames]})"

        # stdout is reserved for JSON frames — the banner must NOT pollute it.
        assert not non_json, f"non-JSON lines on stdout: {non_json[:3]}"

        # 2) closing stdin (parent gone) ends the session.
        assert proc.stdin is not None
        proc.stdin.close()
        proc.wait(timeout=15)
        assert proc.returncode == 0
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
