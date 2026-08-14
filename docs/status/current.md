# Current Project Status

status: CURRENT
owner: repository-governance
created: 2026-08-11
last_verified: 2026-08-13
reference_target: Claude Code v2.1.88 analysis baseline
clauderuntime_commit: 95efbaec4796147657668c4947a0d2088ecc4738
supersedes: none
superseded_by: none

## Summary

ClaudeRuntime / ClawCodex is in a high-fidelity Python runtime parity phase. Current repository governance separates production code, engineering infrastructure, reference materials, active plans, progress history, and archived documents.

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

## 5 System Layers

Surface、Core、Safety / Action、State、Backend 是唯一正式五层。

## 14 CCR Mechanisms

CCR-01 至 CCR-14 是唯一正式横切机制。旧 AUX-01..14 仅作历史映射，禁止继续用于完成度计分。

## 当前结论

B5 起点没有任何 R7、R5 或 CCR 项满足 v6 最终证据字段。跨平台隔离保持
`BLOCKED`，其余项保持 `PARTIAL`；不得把本地局部测试通过写成整体完成。

## Critical Runtime Paths

The minimum tracked runtime paths are ordinary answer, Read, Write/Edit, Bash, Compact, Retry/Recovery, Subagent, Background Agent, MCP, Scheduler/Cron, Resume, and Interrupt/Abort.

## Current P0

Current P0/P1 items should be tracked in GitHub Issues and summarized in [backlog.md](backlog.md). Historical P0 references in archived TODO/progress files are not authoritative unless confirmed against current source and tests.

## Verification Baseline

Migration baseline on 2026-08-11:

- HEAD: `d29bfe597fe03da951888b0ec7732660852a6196`
- Python test baseline: `tests/` collection fails before migration at `tests/test_ch04_api_round4.py` because `src.query.query` does not export `PROMPT_CACHING_SCOPE_BETA_HEADER`.
- Markdown local-link baseline before migration: 114 Markdown files scanned, 105 broken local links found. After migration: 119 Markdown files scanned, 37 broken local links remain.
- Post-migration checks: `git diff --check` passed; `ui-tui` typecheck passed; Python full suite remains blocked by the same baseline collection error; `ui-tui` and workflow test runs have timing-related failures recorded in [../progress/2026/2026-08-11-repository-governance-migration.md](../progress/2026/2026-08-11-repository-governance-migration.md).
- Documentation governance gate: `scripts/check_docs_governance.py` now enforces root Markdown and docs top-level whitelists, forbids newly misplaced date/TODO/FEATURE docs, blocks new broken local Markdown links beyond [markdown-link-allowlist.txt](markdown-link-allowlist.txt), checks archive-link policy, and validates 7/5/14 parity-map coverage.
- Current parity UNKNOWN records are tracked in [parity-unknown-allowlist.txt](parity-unknown-allowlist.txt). Second-round deletion candidates are tracked in [delete-candidates.md](delete-candidates.md) and must not be mixed into the first migration commit.
- Desktop dependencies were not installed in `ui-desktop/node_modules` at migration start.
- `ui-tui/node_modules` existed at migration start.

## Known Intentional Divergences

Intentional divergences must be recorded in parity assets or active plans before they are treated as accepted project behavior.
