# Claude Code Parity

status: CURRENT
owner: parity
created: 2026-08-11
last_verified: 2026-08-13
reference_target: Claude Code v2.1.88 analysis baseline
clauderuntime_commit: 95efbaec4796147657668c4947a0d2088ecc4738
supersedes: docs/parity/clauderuntime-source-parity-action-bible-v1.0.md
superseded_by: none

This directory is the single entry point for ClaudeRuntime source parity evidence.

## 唯一正式分类

ClaudeRuntime B5 只通过以下分类判定完成度：

- 7 Reference Components
- 5 System Layers
- 14 CCR Mechanisms
- Critical Runtime Paths
- Intentional Divergence registry
- Machine-readable source and runtime maps

## 7 Core Components

1. User
2. Interfaces
3. Agent Loop
4. Permission System
5. Tools
6. State & Persistence
7. Execution Environment

`Context / Memory` is not an eighth component. It is represented under Agent Loop for context shaping, compaction, and prompt construction, and under State & Persistence for durable memory, transcript, and resume semantics.

## 5 System Layers

| Layer | Name | Scope |
|---|---|---|
| R5-01 | Surface Layer | 用户入口和交互边界 |
| R5-02 | Core Layer | Agent Loop、Context、Compact |
| R5-03 | Safety / Action Layer | Permission、Hook、Tool、Subagent、Sandbox policy |
| R5-04 | State Layer | Context、Transcript、Memory、Resume/Fork/Rewind |
| R5-05 | Backend Layer | Process、Sandbox、MCP、Remote、Filesystem、Network |

## 14 CCR Mechanisms

CCR-01 至 CCR-14 的正式定义以 B5 v6 开发圣经为准，并由
`coverage-ledger.yaml` 记录当前状态。

旧 `5 Parity Layers` 和 `AUX-01..14` 仅保留为 `LEGACY_SUPPORTING_MAP`，
用于查找历史证据，不再参与完成度计分。

## Evidence Assets

- [source-map/reference-package-map.yaml](source-map/reference-package-map.yaml)
- [source-map/reference-component-map.yaml](source-map/reference-component-map.yaml)
- [source-map/reference-symbol-map.yaml](source-map/reference-symbol-map.yaml)
- [runtime/reference-runtime-path-map.yaml](runtime/reference-runtime-path-map.yaml)
- [runtime/reference-aux-loop-map.yaml](runtime/reference-aux-loop-map.yaml)
- [diagnostics/2026-08-10-diagnostic.md](diagnostics/2026-08-10-diagnostic.md)
- [clauderuntime-source-parity-action-bible-v1.0.md](clauderuntime-source-parity-action-bible-v1.0.md)
