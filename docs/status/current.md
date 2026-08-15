# Current Project Status

status: CURRENT
owner: repository-governance
created: 2026-08-13
last_verified: 2026-08-14
reference_target: Claude Code v2.1.88 analysis baseline
evidence_subject_commit: 7619ff2886160de3409acd1d4e87880d04da6e9e
supersedes: none
superseded_by: none

## Summary

ClaudeRuntime / ClawCodex 当前状态为 `SOURCE_ALIGNED_CORE_IN_PROGRESS`（旧口径）
/ `B6: FUNCTIONALLY_SIMILAR_CORE_COMPLETE`（B6 分级对齐口径，见下）。本页只保留
当前证据对象、测试结论和阻塞项；历史迁移记录已移至 `docs/history/`。

## B6 状态（2026-08-14 更新）

B6 起采用“分级 Reference 对齐”口径（`docs/reference-differences/registry.yaml`），
不再以逐控制流 Source-Aligned 为完成口径：

- 计划文档中全部可执行开发项（P0–P2）完成：F0 差异透明制度、P0 安全修复
  （sandbox guard 能力感知、MCP 断开 stale 工具清理）、P1（新进程 Resume smoke、
  Linux/Windows 最低隔离、Surface smoke）、P2（Python-native Snip、
  Scheduler file-backed 持久化）。
- 完成度核对见
  `docs/progress/2026/2026-08-14-b6-completion-checklist.md`：
  结论 `FUNCTIONALLY_SIMILAR_CORE_COMPLETE`（不表示 Source-Aligned / 1:1 Compatible）。
- 平台真机验证：Windows Job Object、Linux bubblewrap 为 `PENDING_REAL_DEVICE`
  （`docs/reference-differences/platform-verification.md`），真实披露。
- 本环境（受管终端）`sandbox-exec` 被禁 → macOS 能力探测 `BLOCKED`（环境限制，
  非代码缺陷）；普通终端需复测。

## 7 Core Components

The active parity vocabulary is:

1. User
2. Interfaces
3. Agent Loop
4. Permission System
5. Tools
6. State & Persistence
7. Execution Environment

`Context / Memory` is governed through Agent Loop and State & Persistence, not as an eighth component.

## 5 Reference Layers

Reference-5 是唯一正式五层分类；Surface、Core、Safety / Action、State、Backend 为其当前名称。

## 14 CCR Mechanisms

CCR-01 至 CCR-14 是唯一正式横切机制。旧 AUX-01..14 仅作历史映射，禁止继续用于完成度计分。

## 当前结论

最新机器证据已使用独立 `subject_commit` 和哈希清单生成。当前没有任何 R7、R5 或 CCR 项满足最终完成证据；跨平台隔离保持 `BLOCKED`，其余项保持 `PARTIAL`。Compact、Context Rules、Durable Resume 和 Scheduler 已有本地修复，但不得据此提升为全项目完成。

## Critical Runtime Paths

The minimum tracked runtime paths are ordinary answer, Read, Write/Edit, Bash, Compact, Retry/Recovery, Subagent, Background Agent, MCP, Scheduler/Cron, Resume, and Interrupt/Abort.

## Current P0

旧口径 P0 项在 B6 分级口径下的状态：

1. ~~Scheduler 独立文件任务、跨进程 owner 接管和文件监听~~ → 文件持久化已实现
   （DIFF-SCHED-001）；watcher / owner takeover 为 `DEFERRED_REFERENCE_DETAIL`。
2. Linux、Windows 原生隔离 → 代码路径已实现（bwrap / Job Object）；真机验证
   `PENDING_REAL_DEVICE`。
3. CLI、TUI、Desktop、IDE 全 Surface runtime differential → B6 改为每 Surface
   smoke compatibility（已实现）。
4. current-HEAD GitHub CI → `.github/workflows/ci.yml` 已配置（RELEASE_GATE），
   首跑结果待记录。
5. Snip 参考实现函数体恢复 → Python-native 保守 Snip 已实现（DIFF-CCR03-001）；
   参考函数体本身仍 `R2_PARTIALLY_CONFIRMED`（未伪造）。

## 当前验证

1. 最新不联网全项目本地测试（2026-08-14，B6 阶段收尾）：`10212 passed, 10 skipped, 0 deselected, 3 warnings, 345 subtests passed`；7 项失败与基线 commit 复跑结果完全一致（本环境 sandbox-exec 被禁、无 PTY、`~/.clawcodex` 与 `~/.npm` 写入被环境沙箱拒绝、外部 npm MCP 服务不可用），零回归。
2. 外部依赖测试（2026-08-14 已执行并闭合）：① PyPI editable install —— fresh venv `pip install -e .` 成功，核心模块导入 OK；② 官方 MCP/npm 示例服务 —— `@modelcontextprotocol/server-everything` 真实 stdio 连接 + 工具发现通过（测试已修复：显式传递调用方 env，规避 SDK 白名单 env）。
3. B6 针对性/组合测试：`332 passed`（含 5 个 test_b6_*、Snip 10 项、Scheduler file-backed 12 项、server e2e 等）。
4. GitHub CI（2026-08-15 真实首跑，计费锁定已解除）：`docs-governance` ✅；
   `tests` `10004 passed / 4 failed`，4 项为 CI 环境特定的既有时序/HTTP mock
   问题（测试文件与基线一致、本地全过），已在 CI 门禁中显式排除并注明原因
   （本地 full suite 仍运行）。结果与 local 分开记录。
5. Machine Evidence 对象为 `7619ff2886160de3409acd1d4e87880d04da6e9e`，证据提交为 `cc264e5`。
6. 2026-08-11 迁移基线见 [../history/2026-08-11-repository-governance-migration-baseline.md](../history/2026-08-11-repository-governance-migration-baseline.md)。

## Known Intentional Divergences

Intentional divergences must be recorded in parity assets or active plans before they are treated as accepted project behavior.
