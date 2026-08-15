## 概述

B6 分级 Reference 对齐第一阶段交付：**Wave F0（差异透明制度）+ P0 安全修复 + P1 最高优先级功能项**。

核心原则：能确定则对齐；部分确定则已知部分对齐；不能确定才做核心功能一致，并强制记录差异。

## 变更内容

### F0 — 差异透明制度（已落地）
- 新建 `docs/reference-differences/registry.yaml` 全局台账（7 条种子差异：Snip、Compact 算法、Resume、Scheduler、Sandbox、Surface、Permission classifier）+ `README.md`
- `scripts/check_docs_governance.py`：B6 交付目录与 `reference-differences` 进入 allowlist；新增 `check_reference_differences`（required tokens / 状态·原因·证据等级·对齐策略·影响词汇表 / id 唯一性），治理门禁通过
- `docs/progress/2026/2026-08-14-b6-hierarchical-alignment-wave-f0-p0-p1.md` 按模板记录
- 触及模块全部补 Reference Mapping / REF-DIFF 注释

### P0 — 安全旁路审计（7 项核对，修复 2 个真实问题）
1. **沙箱 guard 能力感知化**（`src/permissions/sandbox_guard.py`）：原先声称"本构建无沙箱 enforcement"，导致 macOS Seatbelt 真实可用时误报 UNSANDBOXED、`failIfUnavailable` 连可用沙箱都硬拒绝。现改为查询真实 backend capability（探测按进程缓存）；无隔离平台保持 warn / fail-closed
2. **MCP 断开后 stale 工具清理**：`McpClient._on_disconnect` 原先声明但从未接线，server 崩溃后其 `mcp__<server>__*` 工具永远留在 live registry。现实现 client→runtime→agent_server 全链路清理（干净 close / OAuth 重连旧 client 迟到关闭有 identity 保护）

其余核对项（deny 不可绕过、background 不成为旁路、Resume 不恢复密钥、timeout 进程树清理、symlink/path escape）均有既有防线与测试锁定，无新问题。

### P1 — 三个最高优先级功能项
- **新进程 Resume smoke**：`tests/test_b6_resume_new_process_smoke.py` — 两个独立解释器跨进程完成 transcript+metadata 写入→重建→resume→终态
- **Linux/Windows 最低隔离**：`LinuxSandboxBackend`（bubblewrap，真实隔离）+ `WindowsSandboxBackend`（Job Object 进程树包含，LIMITED）+ `win_job_launcher.py`；`default_sandbox_backend` 逐平台选择；`require_isolation` 一律 fail-closed
- **Surface smoke 套件**：`tests/test_b6_surface_smoke.py` — Server 面（启动/回答/Read/权限 allow/中断/续谈）+ CLI headless 面（启动/回答/Read），全部走真实协议链路

## 测试

```text
新增 5 个 test_b6_* 文件：36 passed
存量回归（sandbox / MCP / resume / server e2e / settings）：127 + 58 + 33 passed
阶段收尾全量套件：10157 passed
```

7 项全量失败已在基线 commit `dc7393b` 上复跑确认**完全相同**，均为环境性（本终端 `sandbox-exec` 被禁、无 PTY、`~/.clawcodex`/`~/.npm` 写入被沙箱拒绝、外部 npm MCP 服务不可用），与本次改动无关，**零回归**。

## 平台真机验证（重要）

`docs/reference-differences/platform-verification.md` 逐项登记：

| 项 | 状态 |
|---|---|
| Windows Job Object launcher | `PENDING_REAL_DEVICE` — 需 win32 真机验证（ctypes 布局、线程恢复、KILL_ON_JOB_CLOSE 整树结束） |
| Linux bubblewrap | `PENDING_REAL_DEVICE` — 需 Linux 主机验证（bwrap+用户命名空间、容器内执行、写入限制、断网） |
| macOS Seatbelt | 结构 VERIFIED；本环境受管终端阻止 `sandbox_apply`（`Operation not permitted`），普通终端需复测 → `BLOCKED`（环境） |
| Server / CLI Surface smoke | `VERIFIED`（本机全绿） |

**红线**：真机验证前不宣称 Windows/Linux 隔离已验证；`provides_isolation` 真实披露；CI 结果与 local 分开记录。

## 已知事实

- 本仓库未配置 `.github/workflows/` hosted CI —— 当前仅能记录 `local tests green`，不能写 `current-head GitHub CI green`
- B6 目标为 `FUNCTIONALLY_SIMILAR_CORE_COMPLETE`（核心功能类似 + Python-native + 差异透明），**不是** Source-Aligned 1:1 复刻

---

## 追加：Wave P2（已并入本 PR）

### Python-native Snip（DIFF-CCR03-001 → FUNCTIONAL_ADAPTATION）
- `snip_compact` 从 no-op 占位升级为保守实现：只裁剪**可重建**（只读 allowlist：Read/Glob/Grep/ListDir/WebFetch/TaskOutput）的旧工具结果；对话文本、tool_use 块、**变更类工具**（Write/Edit/Bash 等）结果、最近 `keep_recent` 条一律保留；来源工具未知的 tool_result 保守保留
- 修复 `keep_recent=0` 的 `[-0:]` 切片边界

### Scheduler file-backed 持久化（DIFF-SCHED-001 更新）
- `SessionCronScheduler(persist_path=...)`：每次变更（create/delete/set_wakeup/clear_wakeup/pop_due）原子写盘（临时文件+fsync+replace）；`from_persisted` / `restore_persisted` 支持新进程跨进程恢复，无需会话 resume 文件；失败仅告警不阻断调度
- `_AgentSession.cron_scheduler` 默认挂 `~/.clawcodex/scheduled_tasks.json`；resume 恢复后同步文件

### 测试
```text
新增：test_snip_compact.py(10) + test_scheduler_file_backed.py(12)
更新：test_compression_pipeline.py Layer 2（真实 Snip 生效 + 变更类工具不裁剪）
针对性合计：332 passed（223 + 109）
```

至此 B6 计划文档中全部可执行开发项（P0–P2）完成；Windows/Linux 真机验证仍为 `PENDING_REAL_DEVICE`（见平台验证台账）。
