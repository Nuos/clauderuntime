# Claude Code Parity

status: CURRENT
owner: parity
created: 2026-08-11
last_verified: 2026-08-11
reference_target: Claude Code v2.1.88 analysis baseline
clauderuntime_commit: d29bfe597fe03da951888b0ec7732660852a6196
supersedes: docs/parity/clauderuntime-source-parity-action-bible-v1.0.md
superseded_by: none

This directory is the single entry point for ClaudeRuntime source parity evidence.

## Core Framework

ClaudeRuntime tracks parity through:

- 7 Core Components
- 5 Parity Layers
- 14 Auxiliary Loops
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

## 5 Parity Layers

| Layer | Name | Scope |
|---|---|---|
| L1 | Framework / Architecture Parity | System boundaries, responsibilities, component relationships |
| L2 | Structure / Source Parity | Packages, modules, symbols, key call edges |
| L3 | Runtime Mechanism Parity | Main runtime paths, state machines, control flow, recovery |
| L4 | Auxiliary Mechanism Parity | Surrounding lifecycle loops and secondary mechanisms |
| L5 | Behavior / Safety / Continuous Parity | Observable behavior, safety invariants, tests, version tracking |

## 14 Auxiliary Loops

| ID | Mechanism | Primary Component |
|---|---|---|
| AUX-01 | Main Agent Query Loop | Agent Loop |
| AUX-02 | Tool Execution Loop | Agent Loop / Tools |
| AUX-03 | Permission Escalation Loop | Permission |
| AUX-04 | Retry / Model Recovery Loop | Agent Loop |
| AUX-05 | Compaction Loop | Agent Loop / State |
| AUX-06 | Stop Hook Loop | Agent Loop / Tools |
| AUX-07 | Subagent Query Loop | Agent Loop / State |
| AUX-08 | Background Agent Lifecycle Loop | Agent Loop / Execution |
| AUX-09 | MCP Lifecycle Loop | Tools / Execution |
| AUX-10 | Scheduler / Cron Loop | Agent Loop / State |
| AUX-11 | Resume / Fork / Rewind Loop | State & Persistence |
| AUX-12 | Surface Streaming / Interrupt Loop | Interfaces / Agent Loop |
| AUX-13 | Session Persistence / Recovery Loop | State & Persistence |
| AUX-14 | Long-output Result Budgeting Loop | Tools / State / Agent Loop |

## Evidence Assets

- [source-map/reference-package-map.yaml](source-map/reference-package-map.yaml)
- [source-map/reference-component-map.yaml](source-map/reference-component-map.yaml)
- [source-map/reference-symbol-map.yaml](source-map/reference-symbol-map.yaml)
- [runtime/reference-runtime-path-map.yaml](runtime/reference-runtime-path-map.yaml)
- [runtime/reference-aux-loop-map.yaml](runtime/reference-aux-loop-map.yaml)
- [diagnostics/2026-08-10-diagnostic.md](diagnostics/2026-08-10-diagnostic.md)
- [clauderuntime-source-parity-action-bible-v1.0.md](clauderuntime-source-parity-action-bible-v1.0.md)
