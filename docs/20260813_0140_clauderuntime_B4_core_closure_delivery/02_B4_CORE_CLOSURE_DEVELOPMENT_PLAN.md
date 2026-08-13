# ClaudeRuntime B4 开发计划：7×5×14 Final Closure Program

> 文档编号：`CR-B4-CORE-CLOSURE-PLAN`  
> 基线：`4a77f068649e18351e4c51d97e5a6667c9c4a5fd`  
> Reference：Claude Code `2.1.88` @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 唯一目标：**尽快关闭 7 Reference Components + 5 System Layers + 14 CCR Runtime Mechanisms**

# 0. 唯一目标

B4 不再进行主体功能扩展；B3 已证明主体架构存在。B4 只做 Closure：

> **把剩余 Blocked / Partial / Evidence Gap 收敛为 Source-Aligned Complete。**

完成定义：`R7 7/7 + R5 5/5 + CCR 14/14 + Lifecycle 14/14 + critical UNKNOWN/PARTIAL/MISSING = 0 + current HEAD reproducibly green`。

# 1. 排序原则

`Real Missing Behavior > Safety/State Invariant > Runtime Differential > Machine Map > Documentation`。

所有新 provider、UI feature、workflow/productivity feature、benchmark 宣传、非核心重构默认延期。

# 2. C0 — Truth Refresh / Differential Contract Freeze

1. 重生成 Python inventory，修复 648→650 漂移；
2. 建 7×5×14 coverage ledger；
3. 提取 recovered source critical symbols；
4. 建 `reference-callgraph-map.yaml`；
5. 建 `reference-state-transition-map.yaml`；
6. 建 `reference-runtime-trace-map.yaml`；
7. 建 `known-divergences.yaml`；
8. 建 current scorecard；
9. 将所有 B3 UNKNOWN/PARTIAL 变成 symbol-level work item。

**Exit**：每个 R7/R5/CCR 有 reference owner + Python owner；每个 BLOCKED 有实现 target。

# 3. C1 — Real Isolation / Execution Environment

## C1.1 Real Sandbox Backend

必须实现 capability detection、filesystem/network isolation、allow/deny read/write、cwd/add-dir、env secret scrub、unavailable fail policy、unsandboxed override、violation diagnostics、timeout/abort。

允许 OS adaptation，但必须 `PYTHON_ADAPTATION_VERIFIED`。

## C1.2 Canonical ProcessPolicy

统一 process group/session、timeout、TERM→grace→KILL、Windows tree termination、sibling abort、stdout/stderr drain、no orphan child、sandboxed/unsandboxed lifecycle。

## C1.3 E2E

真实副作用测试：symlink/cwd escape、denied write/network、secret scrub、timeout/abort kill-tree、permission allow+sandbox deny、permission deny 时零执行。

**Exit**：R7-07、R5-05、CCR-12 不再 BLOCKED。

# 4. C2 — State / Resume / Fork / Rewind True Lifecycle

## Resume 真重入

race-safe claim→transcript reconstruct→typed hydrate→restore durable state→不恢复 temporary trust→构造真实 RunAgentParams→注入 context_messages→启动 canonical run_agent/query→pending message drain→terminal/result 回写。

## Fork

新 session id、lineage、history reconstruction、trust reset、compact boundary/content replacement recovery。

## Rewind

区分 conversation rewind 与 file-history rewind；不把不可逆外部副作用伪装为回滚。

## Crash Consistency

truncated tail、tool-start/tool-complete orphan、crash during compact/resume、concurrent resume、sidechain close。

**Exit**：R7-06、R5-04、CCR-10 主链闭合。

# 5. C3 — Compact-5 + Context-9

## Compact-5 Differential

逐层验证 Result Budget、Snip、Microcompact、Context Collapse、AutoCompact 的 trigger、gate、no-op、token accounting、durable-state interaction、hook/boundary、error semantics。

Microcompact 必须按 2.1.88 实际 source gate 重新核验。

## Context-9 Matrix

对 System Prompt、Environment、CLAUDE.md、Path Rules、Auto Memory、Tool Metadata、Conversation、Tool Results、Compact Summaries 建立 source/scope/load time/insertion/precedence/lazy/trust/provenance/compact matrix。

**Exit**：CCR-03、CCR-04、R5-02 Context/Compact 完成差分闭环。

# 6. C4 — Subagent / Background / MCP / Scheduler Lifecycle

## Subagent

Parent Agent tool_use→definition resolve→tool pool rebuild→permission override→isolated context→canonical loop→sidechain→summary/result→parent。覆盖 Explore/Plan/General/custom、allowed/disallowed tools、permission precedence、in-process/worktree、background、maxTurns、hooks/skills、summary-only。

## Background Agent

`created → running → waiting/message → completed|failed|killed`，并覆盖 `resume → running`；测试 pending/race/stop/abort/terminal/auto-resume。

## MCP

config/trust→connect→transport ready→discover→capability merge→permission→invoke→post-hook/result→disconnect/error/reconnect→shutdown。

## Scheduler / Cron

create/list/delete、due、wakeup、worker queue、长 permission/AskUserQuestion 不阻塞 housekeeping、cancel、persistence、shutdown/restart、scheduled action 仍走 permission/isolation。

**Exit**：CCR-11/14 与 MCP/Scheduler lifecycle obligations 关闭。

# 7. C5 — Hook + Surface + Failure Differential

## Hook

建立论文识别的 27 events / 7 families coverage：authorization、session、user interaction、subagent、context、workspace、notification。验证 match/source/order/timeout/blocking/error/output schema/permission-stop effect。

## Cross-Surface Runtime Differential

使用 deterministic provider：same input/settings/transcript/tool response，经所有支持 surface 比较 canonical trace、permission、tool order、state、terminal、abort；只允许 render envelope 不同。

## Fault Matrix

429/529/5xx、stream break、prompt-too-long、output cap、tool/hook exception、sandbox unavailable、subprocess hang、MCP disconnect、transcript crash、user abort。

**Exit**：CCR-01/07/08 与 R7-01/02 cross-surface 证明闭合。

# 8. C6 — Machine Evidence + Final Exit Gate

必须生成并持续维护：

```text
docs/parity/source-map/reference-package-map.yaml
docs/parity/source-map/reference-symbol-map.yaml
docs/parity/source-map/reference-callgraph-map.yaml
docs/parity/source-map/unmapped-reference-symbols.yaml
docs/parity/runtime/reference-runtime-trace-map.yaml
docs/parity/runtime/reference-state-transition-map.yaml
docs/parity/divergences/known-divergences.yaml
docs/parity/scorecards/latest.yaml
docs/parity/scorecards/history/<commit>.yaml
```

每个 final row 必须有 reference files/symbols/call edges、Python files/symbols、runtime trace、state/safety/failure invariants、tests，并且 status 只能是 EXACT / SEMANTIC_EQUIVALENT / PYTHON_ADAPTATION_VERIFIED。

最终执行 full pytest、parity differential、fault、docs governance、packaging/install smoke、所有支持 surface tests、实际支持平台 tests、current HEAD CI、scorecard generation。

# 9. 推荐 PR 切分

1. `b4/c0-parity-contract-refresh`
2. `b4/c1-real-sandbox-process-boundary`
3. `b4/c2-resume-fork-rewind`
4. `b4/c3-compact-context-differential`
5. `b4/c4-subagent-mcp-scheduler-lifecycle`
6. `b4/c5-hook-surface-fault-differential`
7. `b4/c6-final-evidence-exit-gate`
