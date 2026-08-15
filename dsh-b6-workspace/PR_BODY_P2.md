## 概述

B6 第二阶段（Wave P2）：完成剩余两个可选 P2 功能项，至此 B6 计划文档中全部可执行开发项（P0–P2）完成。

## 变更内容

### P2a — Python-native 安全 Snip（DIFF-CCR03-001 → FUNCTIONAL_ADAPTATION）
- `src/services/compact/snip_compact.py` 从 no-op 占位升级为保守实现：只裁剪**可重建**（只读 allowlist：Read/Glob/Grep/ListDir/WebFetch/TaskOutput）的旧工具结果
- 对话文本、tool_use 块、**变更类工具**（Write/Edit/Bash 等）结果、最近 `keep_recent` 条可裁剪结果、来源工具未知的 tool_result 一律保留
- 修复 `keep_recent=0` 的 `[-0:]` 切片边界（负零切片会保留全部）
- 不再宣称“Reference 也是 no-op”（B6 红线）

### P2b — Scheduler file-backed 持久化增强（DIFF-SCHED-001 更新）
- `SessionCronScheduler(persist_path=...)`：每次变更（create/delete/set_wakeup/clear_wakeup/pop_due）原子写盘（临时文件 + fsync + 原子 replace）；失败仅告警、绝不阻断调度
- `from_persisted` / `restore_persisted`：新进程跨进程恢复，无需会话 resume 文件
- `_AgentSession.cron_scheduler` 默认挂 `~/.clawcodex/scheduled_tasks.json`；resume 恢复后 `persist()` 同步文件
- 恢复规则与既有 `restore` 一致（7 天 recurring 窗口 / durable one-shot 补执行一次 / 过期丢弃 / 未来 wakeup）

## 测试

```text
针对性合计 332 passed（223 + 109）
新增：test_snip_compact.py(10) / test_scheduler_file_backed.py(12)
更新：test_compression_pipeline.py Layer 2（真实 Snip + 变更类工具不裁剪）
```

阶段收尾总全量（最终记录，见 progress 文档）：

```text
10212 passed / 10 skipped / 345 subtests passed
7 failed —— 与基线 commit 复跑完全相同（环境性：sandbox-exec 被禁、无 PTY、
~/.clawcodex 与 ~/.npm 写入被环境沙箱拒绝、外部 npm MCP 服务不可用），零回归
```

## 记录

- `docs/progress/2026/2026-08-14-b6-hierarchical-alignment-wave-p2.md`
- `docs/reference-differences/registry.yaml`（DIFF-CCR03-001 / DIFF-SCHED-001 更新）
- Windows/Linux 真机验证仍为 `PENDING_REAL_DEVICE`（`docs/reference-differences/platform-verification.md`）
- GitHub hosted CI 未配置，只记录 `local tests green`
