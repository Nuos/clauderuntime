# Current Project Status

status: CURRENT
owner: repository-governance
created: 2026-08-13
last_verified: 2026-08-13
reference_target: Claude Code v2.1.88 analysis baseline
evidence_subject_commit: 95efbaec4796147657668c4947a0d2088ecc4738
supersedes: none
superseded_by: none

## Summary

ClaudeRuntime / ClawCodex 当前状态为 `SOURCE_ALIGNED_CORE_IN_PROGRESS`。本页只保留当前证据对象、测试结论和阻塞项；历史迁移记录已移至 `docs/history/`。

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

最近一次已提交证据对象没有任何 R7、R5 或 CCR 项满足 v6 最终证据字段。跨平台隔离保持 `BLOCKED`，其余项保持 `PARTIAL`。本轮工作区正在修复 Machine Evidence、Compact、Context Rules、Durable Resume 和 Scheduler；未形成新证据提交前不得提升完成状态。

## Critical Runtime Paths

The minimum tracked runtime paths are ordinary answer, Read, Write/Edit, Bash, Compact, Retry/Recovery, Subagent, Background Agent, MCP, Scheduler/Cron, Resume, and Interrupt/Abort.

## Current P0

1. Scheduler file-backed lifecycle、owner takeover 和文件监听。
2. Linux、Windows 原生隔离和真实平台测试。
3. CLI、TUI、Desktop、IDE 全 Surface runtime differential。
4. current-HEAD GitHub CI 和 required status checks。
5. Snip 参考实现函数体恢复；当前保持 UNKNOWN/PARTIAL。

## 当前验证

1. 最近已完成的全项目本地测试：`10151 passed, 10 skipped, 3 warnings, 345 subtests passed`；该结果属于上一提交阶段，不代表本轮未提交工作区。
2. 本轮已完成针对性测试：Compact/Context 组合 `94 passed`；Resume/SendMessage `44 passed`；Scheduler `28 passed`。
3. GitHub CI：本轮尚未提交，状态为 `未测试`，禁止写成 CI 通过。
4. Machine Evidence 使用 `subject_commit`，不再要求证据文件自引用其所在提交 SHA。
5. 2026-08-11 迁移基线见 [../history/2026-08-11-repository-governance-migration-baseline.md](../history/2026-08-11-repository-governance-migration-baseline.md)。

## Known Intentional Divergences

Intentional divergences must be recorded in parity assets or active plans before they are treated as accepted project behavior.
