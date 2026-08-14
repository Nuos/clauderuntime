# Current Project Status

status: CURRENT
owner: repository-governance
created: 2026-08-13
last_verified: 2026-08-13
reference_target: Claude Code v2.1.88 analysis baseline
evidence_subject_commit: 7619ff2886160de3409acd1d4e87880d04da6e9e
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

最新机器证据已使用独立 `subject_commit` 和哈希清单生成。当前没有任何 R7、R5 或 CCR 项满足最终完成证据；跨平台隔离保持 `BLOCKED`，其余项保持 `PARTIAL`。Compact、Context Rules、Durable Resume 和 Scheduler 已有本地修复，但不得据此提升为全项目完成。

## Critical Runtime Paths

The minimum tracked runtime paths are ordinary answer, Read, Write/Edit, Bash, Compact, Retry/Recovery, Subagent, Background Agent, MCP, Scheduler/Cron, Resume, and Interrupt/Abort.

## Current P0

1. Scheduler 独立文件任务、跨进程 owner 接管和文件监听。
2. Linux、Windows 原生隔离和真实平台测试。
3. CLI、TUI、Desktop、IDE 全 Surface runtime differential。
4. current-HEAD GitHub CI 和 required status checks。
5. Snip 参考实现函数体恢复；当前保持 UNKNOWN/PARTIAL。

## 当前验证

1. 最新不联网全项目本地测试：`10160 passed, 10 skipped, 1 deselected, 3 warnings, 345 subtests passed`，失败数为 `0`。
2. 未执行两项外部测试：PyPI editable install、官方 MCP/npm 示例服务；当前没有外联测试结果。
3. 本轮针对性测试：Compact/Context `94 passed`；Resume/SendMessage `44 passed`；Scheduler `28 passed`；本机端口 `177 passed`；服务索引 `13 passed`；macOS 隔离与内存目录 `6 passed`。
4. GitHub CI：本轮尚未推送，状态为 `未测试`，禁止写成 CI 通过。
5. Machine Evidence 对象为 `7619ff2886160de3409acd1d4e87880d04da6e9e`，证据提交为 `cc264e5`。
6. 2026-08-11 迁移基线见 [../history/2026-08-11-repository-governance-migration-baseline.md](../history/2026-08-11-repository-governance-migration-baseline.md)。

## Known Intentional Divergences

Intentional divergences must be recorded in parity assets or active plans before they are treated as accepted project behavior.
