"""持久化后台 Agent 跨进程恢复所需的最小安全元数据。

元数据只记录 Agent 类型、模型名、工作目录、transcript 路径和终态，不序列化
provider 对象、API key、工具实例、权限会话或 AbortController。恢复时必须使用
当前进程的运行时工厂重新解析这些依赖，避免把过期凭据和临时信任带入新进程。
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1


@dataclass(frozen=True)
class DurableResumeMetadata:
    """描述可恢复任务身份和磁盘状态，不包含任何实时运行对象。"""

    schema_version: int
    agent_id: str
    agent_type: str
    description: str
    initial_prompt: str
    model: str | None
    tool_use_id: str | None
    output_file: str
    workspace_root: str | None
    worktree_root: str | None
    status: str


def metadata_path_for_output(output_file: str | Path) -> Path:
    """返回 transcript 同目录下的恢复元数据路径。"""
    transcript = Path(output_file)
    return transcript.with_name(f"{transcript.name}.resume.json")


def build_metadata(
    *,
    agent_id: str,
    agent_type: str,
    description: str,
    initial_prompt: str,
    model: str | None,
    tool_use_id: str | None,
    output_file: str,
    resume_run_params: Any,
    status: str,
) -> DurableResumeMetadata:
    """从实时参数提取允许落盘的身份和工作区字段。"""
    parent_context = getattr(resume_run_params, "parent_context", None)
    workspace_root = getattr(parent_context, "workspace_root", None)
    worktree_root = getattr(parent_context, "worktree_root", None)
    return DurableResumeMetadata(
        schema_version=SCHEMA_VERSION,
        agent_id=agent_id,
        agent_type=agent_type,
        description=description,
        initial_prompt=initial_prompt,
        model=model,
        tool_use_id=tool_use_id,
        output_file=output_file,
        workspace_root=str(workspace_root) if workspace_root is not None else None,
        worktree_root=str(worktree_root) if worktree_root is not None else None,
        status=status,
    )


def save_metadata(metadata: DurableResumeMetadata) -> Path:
    """以同目录临时文件加原子替换写入恢复元数据。"""
    target = metadata_path_for_output(metadata.output_file)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(asdict(metadata), ensure_ascii=False, sort_keys=True).encode("utf-8")
    handle = tempfile.NamedTemporaryFile(dir=target.parent, prefix=f".{target.name}.", delete=False)
    temporary = Path(handle.name)
    try:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        handle.close()
        os.chmod(temporary, 0o600)
        os.replace(temporary, target)
    finally:
        if not handle.closed:
            handle.close()
        temporary.unlink(missing_ok=True)
    return target


def load_metadata(output_file: str | Path) -> DurableResumeMetadata | None:
    """读取并校验恢复元数据；损坏或版本不支持时返回空。"""
    path = metadata_path_for_output(output_file)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        metadata = DurableResumeMetadata(**raw)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return None
    if metadata.schema_version != SCHEMA_VERSION:
        return None
    return metadata


def update_metadata_status(output_file: str | Path, status: str) -> bool:
    """原子更新持久化终态，供进程重启后的恢复判定使用。"""
    metadata = load_metadata(output_file)
    if metadata is None:
        return False
    save_metadata(replace(metadata, status=status))
    return True
