# ClaudeRuntime B5 开发计划：7×5×14 Source-Aligned Final Truth Closure

> 文档编号：`CR-B5-7x5x14-FINAL-TRUTH-CLOSURE-PLAN`  
> 起始 HEAD：`95efbaec4796147657668c4947a0d2088ecc4738`  
> Reference：Claude Code `2.1.88` @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 上一功能提交：`eff80250b0603a8305660e9f2c88d77d5e73b547`  
> 核心原则：**先纠正错误 VERIFIED，再补最后功能；先事实一致，再追求完成率。**

---

# 0. Program Goal

B5 不再以“开发更多功能”为目标，而以**消灭错误完成声明和最后语义差距**为目标。

最终必须同时达到：

```text
R7      7/7 FINAL VERIFIED
R5      5/5 FINAL VERIFIED
CCR-14 14/14 FINAL VERIFIED
Lifecycle obligations all covered
Machine evidence internally consistent
Native platform isolation verified
Current HEAD reproducibly green
```

---

# 1. 优先级

```text
P0-A  Truth / Evidence Integrity
P0-B  Context & Compact semantic corrections
P0-C  Durable State / Resume / Fork / Rewind
P0-D  Cross-platform Isolation
P1-E  Scheduler / MCP / Subagent full source lifecycle
P1-F  All-surface runtime differential
P1-G  Remaining core contract maps
P0-Z  Final Exit Gate
```

B5 期间禁止新 provider、新 UI 功能、新 workflow、benchmark 宣传、非关键重构。

---

# 2. Wave A0 — Constitution & Machine Evidence Reconciliation

## 目标

先让“项目说自己是什么状态”重新可信。

## 任务

1. 将所有 current parity assets 的 baseline 更新到当前工作 HEAD；
2. 重建：
   - `coverage-ledger.yaml`
   - `reference-callgraph-map.yaml`
   - `reference-state-transition-map.yaml`
   - `reference-runtime-trace-map.yaml`
   - `unmapped-reference-symbols.yaml`
   - `known-divergences.yaml`
   - `scorecards/latest.yaml`
3. 修正 Resume / Scheduler / Cross-Surface 的相互矛盾状态；
4. `docs/status/current.md`、`docs/parity/README.md` 改为 v6 唯一分类：Reference-7 + Reference-5 + CCR-14；
5. legacy 5 Parity Layers / AUX-14 只保留映射，不再计分；
6. 新增 schema + consistency checker：任何同一 work item 在不同文件状态冲突时 CI fail；
7. `VERIFIED` 必须包含 source symbol + Python symbol + call edge + runtime trace + differential test。

## Exit Gate

- baseline commit 100% = 当前 HEAD；
- machine maps 之间 0 contradiction；
- 所有错误 VERIFIED 已降级；
- scorecard 可自动重建，不手工填完成率。

---

# 3. Wave A1 — Compact-5 Source Correction

这是 B5 第一项真正的运行时修正，因为 B4 C3 有明显 source drift。

## A1.1 移除/隔离非 Reference early-exit

当前 `early_exit_tokens` 可导致早层后直接 return。Reference `query.ts` 会继续运行后续 shapers。

方案：

- Source-Aligned mode：禁止该全局 early-return；
- 若希望保留优化：移到 `PRODUCT_EXTENSION` profile，并登记 divergence，不能参与 parity score。

## A1.2 Snip

当前 `snip_compact()` 是固定 no-op stub；必须：

- 从 2.1.88 source-map 中继续恢复/定位 `snipCompactIfNeeded` implementation；
- 若确实无法恢复，状态保持 UNKNOWN，不能制造模拟实现后标 EXACT；
- 复现 HISTORY_SNIP gate、tokensFreed、boundary semantics；
- 测试必须以 source trace 为 oracle，而不是 `ts_compression_layers.json` 手写 snapshot。

## A1.3 Microcompact

Reference 每轮调用 `microcompactMessages()`，内部：

1. time-based trigger；
2. cached microcompact feature path；
3. otherwise no-op。

Python 应改为同等调用形态：

- time-based config default disabled，但函数仍进入；
- main-thread source predicate；
- cached `cache_edits` / pinned edits 或明确 Python adaptation；
- legacy path absent；
- cache-deletion accounting / boundary ordering。

## A1.4 Context Collapse / AutoCompact

补齐：feature gate、projection persistence、Pre/PostCompact hooks、boundary/attachments、failure circuit breaker、reactive compact interaction。

## Exit

CCR-03/R5-02 只有在 control-flow differential 全绿后恢复 VERIFIED。

---

# 4. Wave A2 — Context-9 Semantic Correction

## A2.1 Path-scoped Rules

实现并验证：

```text
.clawcodex/rules/*.md frontmatter paths
→ file read resolves canonical path
→ match applicable rule
→ lazy load once
→ user-context insertion
→ provenance/dedupe
→ compact/reload semantics
```

不能再把 path rules 映射到 `src/permissions`。

## A2.2 九来源真实 insertion matrix

逐项记录并测试：

1. System Prompt
2. Environment
3. Project Instructions
4. Path-scoped Rules
5. Auto Memory
6. Tool Metadata
7. Conversation
8. Tool Results
9. Compact Summaries

每项必须有：source owner、load time、insertion point、scope、precedence、lazy/eager、trust、compact behavior。

## A2.3 Late Injection

补 differential：

- relevant memory prefetch；
- MCP instruction delta；
- agent listing delta；
- background task notifications；
- ToolSearch deferred schemas。

## Exit

CCR-04/R5-04 Context 部分恢复 VERIFIED；必须有真实 read-file E2E。

---

# 5. Wave A3 — Durable Resume / Fork / Rewind / Crash Consistency

## A3.1 Background Resume 从 in-memory recipe 升级为 durable reconstruction

禁止把 `resume_run_params` 作为唯一恢复依赖。

对齐 Reference：

```text
transcript + metadata
→ filter invalid/orphan/unresolved messages
→ content replacement reconstruction
→ worktree validation / fallback
→ current agent definition resolution
→ current permission context + tool pool rebuild
→ system prompt rebuild
→ canonical run_agent
→ lifecycle/terminal persistence
```

进程重启后仍应能根据 durable metadata 做安全恢复；若有无法持久化的 provider/session object，应从当前 session/runtime factory 重建，而不是序列化对象。

## A3.2 Main Session Resume / Fork

验证：

- session/project dir；
- lineage；
- compact boundary chain patch；
- content replacements；
- new session id for fork；
- session temporary trust 不恢复。

## A3.3 Rewind

明确：

- conversation rewind；
- file-history rewind；
- external irreversible effects 不伪装回滚；
- parent UUID / checkpoint consistency。

## A3.4 Crash Matrix

- partial JSONL tail；
- tool_use without result；
- content replacement interruption；
- compact during crash；
- resume crash；
- concurrent resume；
- sidechain close。

## Exit

R7-06、R5-04、CCR-10/11 达到 final evidence。

---

# 6. Wave A4 — Cross-platform Real Isolation & Full Policy Translation

## A4.1 macOS 完整化

补齐：

- managed/user/project sandbox path translation；
- settings files/skills/bare-git escape protection；
- read allow/deny semantics；
- domain allow/deny；
- Unix socket/local bind/proxy policies；
- background secret scrub；
- violation diagnostics。

## A4.2 Linux Real Backend

优先选择可验证的 OS primitive，例如 Landlock/bubblewrap 等；要求：

- capability probe；
- filesystem isolation；
- network isolation；
- process namespace/lifecycle；
- fail-closed when required；
- native Linux CI E2E。

不允许“Linux 走 NoSandboxBackend”后仍计 complete。

## A4.3 Windows Real Backend

使用可证明的 Windows primitive/adaptation：restricted token/AppContainer/Job Object/ACL 或等价组合，至少验证：

- workspace write boundary；
- protected path read/write；
- child-process tree termination；
- environment secret boundary；
- network policy；
- native Windows CI。

Git Bash 进程管理不等于 Windows sandbox。

## A4.4 DNS / Domain policy

域名 allowlist 必须解决解析时 TOCTOU / rebinding；不能只做字符串 host suffix 匹配后放开全网络。

## Exit

R7-07 / R5-05 / CCR-12 final complete。

---

# 7. Wave A5 — Scheduler / MCP / Subagent Lifecycle Differential

## A5.1 Scheduler

建立 Reference `cronScheduler.ts` ↔ Python scheduler 矩阵：

- session task；
- durable/file task；
- file watch/reload；
- cross-session lock/owner；
- missed one-shot；
- lastFiredAt；
- jitter；
- no catch-up；
- expiry；
- daemon/filter/killswitch；
- permission/isolation propagation。

若 Python 采用 snapshot persistence 而非 file watcher，必须证明 `PYTHON_ADAPTATION_VERIFIED` 的等价 observable behavior，不能只写“功能都有”。

## A5.2 MCP

完成 connect→discover→merge→permission→invoke→result→reconnect/fail→shutdown，覆盖 transport identity/trust/OAuth 和 stale tool prevention。

## A5.3 Subagent

验证：

- isolated context；
- summary-only return；
- allowed/disallowed tools；
- permission mode precedence；
- worktree；
- background；
- sidechain；
- stop/resume；
- pending messages；
- parent result contract。

## Exit

CCR-05/11/14 的 lifecycle proof 完整。

---

# 8. Wave A6 — Full Cross-Surface Runtime Differential

建立 deterministic model/tool fixture，对每个**官方声明支持**的 Surface 执行同一 script：

```text
same prompt
same settings
same permission response
same model chunks
same tool outputs
same initial transcript
```

至少覆盖：

- core API / headless；
- CLI；
- DirectConnect/Agent Server；
- TUI；
- Desktop；
- IDE/VSCode（若项目宣称 parity surface）。

比较：

- model call count；
- tool visibility；
- permission decision；
- tool order；
- state transition；
- transcript；
- interrupt；
- terminal reason；
- usage/turn count。

只允许 renderer/event envelope 不同。

## Exit

R7-01/R7-02/R5-01 final verified。

---

# 9. Wave A7 — Remaining Core Contracts

对当前 coverage ledger 的 PARTIAL 项做最后 closure：

- R7-03：query control flow / continue sites；
- R7-04 + CCR-02：Authorization 全 vector；
- R7-05 + CCR-06/09：Tool orchestration/result processing；
- CCR-13：Trust scope/source/lifetime/managed upper bound。

每项必须生成 symbol/callgraph/state/test evidence。

---

# 10. Wave AZ — Final Exit Gate

## 机器证据

最终所有文件必须由同一命令生成：

```text
coverage-ledger.yaml
reference-package-map.yaml
reference-symbol-map.yaml
reference-callgraph-map.yaml
unmapped-reference-symbols.yaml
reference-state-transition-map.yaml
reference-runtime-trace-map.yaml
known-divergences.yaml
scorecards/latest.yaml
scorecards/history/<HEAD>.yaml
```

## 测试

- Python full suite；
- parity/differential suite；
- safety/fault/state/recovery suite；
- macOS/Linux/Windows native isolation E2E；
- CLI/TUI/Desktop/IDE supported-surface tests；
- packaging/install smoke；
- docs governance；
- current HEAD CI。

## Final Condition

```text
R7 7/7
R5 5/5
CCR 14/14
critical UNKNOWN/PARTIAL/MISSING = 0
unmapped critical symbol = 0
open critical divergence = 0
machine evidence contradiction = 0
```

只有通过 AZ，才允许把项目状态写为 `SOURCE_ALIGNED_CORE_COMPLETE`。
