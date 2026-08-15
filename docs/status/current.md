# Current Project Status

status: CURRENT
owner: repository-governance
created: 2026-08-13
last_verified: 2026-08-15
subject_commit: 16da0cfea98d69987739a319ff6ae42cfd432d2c
reference_commit: a8a678cb6244e6770e1e421767ff0987a1d95549
supersedes: none
superseded_by: none

## Summary

ClaudeRuntime / ClawCodex 当前状态（B7 口径）：**ARCHITECTURE_FREEZE**（2026-08-15，
记录见 `docs/progress/2026/2026-08-15-b7-architecture-freeze.md`）。功能
`FUNCTIONALLY_SIMILAR_CORE_COMPLETE`；W0–W9 全部落地，Gate A–J 全 PASS。历史迁移
记录在 `docs/history/`；B6 阶段记录在 `docs/progress/2026/`。

## B7 状态（2026-08-15 更新）

- **ARCHITECTURE_FREEZE**：最后一次架构收口（W0–W9）完成，全部并入 main；
  门禁 A–J 全 PASS（`scripts/check_architecture_freeze.py`）。
- 收口内容：Truth Reset / Permission Safe-by-Default / Canonical Turn Preparation
  / Extension Trust Boundary / Task·Session·Persistence Owner / Context·Compact
  Closure / Query·Server Ownership Extraction / CI·Platform·Evidence Truth /
  Identity·Legacy Cleanup / Freeze Gate。
- Freeze 后：runtime 主脊柱与 owner 不再移动（Behavior Bible §S）；测试/调试走
  交付包 T0–T14 管线。
- 未闭合（真实披露）：Windows/Linux 真机隔离 `PENDING_REAL_DEVICE`；
  Python 3.10/3.14 + Ubuntu/Windows smoke 为声明（`machine/test-matrix.yaml`）。

## B6 状态（2026-08-14，已并入 main，保留为历史口径）

B6 分级 Reference 对齐口径下结论为 `FUNCTIONALLY_SIMILAR_CORE_COMPLETE`
（不表示 Source-Aligned / 1:1 Compatible），全部已并入 main（PR #2 `7ca77c0` +
PR #3 `ff2ce32`）。平台真机验证仍为 `PENDING_REAL_DEVICE`
（`docs/reference-differences/platform-verification.md`）。

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

## 当前结论（B7 口径）

- 功能主体成熟（canonical query / permission / tools / compact / MCP / resume 等）。
- 架构收口未完成：owner 重叠、隐式特权默认、证据 drift 待 W0–W9 处理。
- 任何"完成"声明须先满足 Behavior Bible A（Truth Before Progress）。

## Critical Runtime Paths

The minimum tracked runtime paths are ordinary answer, Read, Write/Edit, Bash, Compact, Retry/Recovery, Subagent, Background Agent, MCP, Scheduler/Cron, Resume, and Interrupt/Abort.

## Current P0

B7 计划中的 P0 Wave：W0 Truth Reset、W1 Permission Safe-by-Default、
W2 Canonical Turn Preparation、W3 Extension Trust Boundary、
W4 Task/Session/Persistence Owner、W7 CI/Platform/Evidence Truth。
（旧 B6 P0 项均已闭合或转为 B7 处理，见 `docs/progress/2026/`。）

## 当前验证

1. 最新不联网全项目本地测试（2026-08-14，B6 阶段收尾）：`10212 passed, 10 skipped,
   0 deselected, 3 warnings, 345 subtests passed`；7 项失败与基线 commit 复跑结果
   完全一致（本环境 sandbox-exec 被禁、无 PTY、`~/.clawcodex` 与 `~/.npm` 写入被
   环境沙箱拒绝、外部 npm MCP 服务不可用），零回归。
2. 外部依赖测试（2026-08-14 已执行并闭合）：① PyPI editable install 成功；② 官方
   MCP/npm 示例服务真实连接通过。
3. GitHub CI（2026-08-15）：**全绿** —— `docs-governance` ✅ +
   `Python test suite (non-integration)` ✅（5 项 CI 环境特定用例 quarantine）。
4. 证据对象 subject 绑定：`16da0cfea98d69987739a319ff6ae42cfd432d2c`（W0 起统一；
   W9 重新绑定最终 Freeze SHA）。

## Known Intentional Divergences

Intentional divergences must be recorded in parity assets or active plans before they are treated as accepted project behavior.
