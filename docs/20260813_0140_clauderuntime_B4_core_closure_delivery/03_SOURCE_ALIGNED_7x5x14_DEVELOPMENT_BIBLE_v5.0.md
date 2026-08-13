# Claude Code Source-Aligned 7×5×14 开发圣经 v5.0 — B4 Final Closure Edition

> 文档编号：`CR-SOURCE-ALIGNED-RULE-BIBLE-v5.0`  
> 状态：**SUPREME ACTIVE DEVELOPMENT CONSTITUTION**  
> 生效：2026-08-13  
> ClaudeRuntime baseline：`4a77f068649e18351e4c51d97e5a6667c9c4a5fd`  
> Claude Code recovered source baseline：`a8a678cb6244e6770e1e421767ff0987a1d95549` / `2.1.88`  
> 论文基线：arXiv `2604.14228v2`  
> 继承 v4.0；本版只强化 B3 后剩余 closure，不改变唯一目标。

# 0. 最高命令

> **所有开发行为、目标、代码、测试、文档、CI、映射和资源分配，必须且只能优先服务于：把 Reference-7 七核心组件、Reference-5 五层系统架构、CCR-14 十四横切机制全部实现并验证到与 Claude Code 2.1.88 recovered source 的可确认核心行为一致。**

Final Exit Gate 前，任何非必要产品开发一律推后。

# 1. Source-Aligned 唯一含义

```text
Code Exists            != Source-Aligned
Tests Exist             != Source-Aligned
Many Tests Pass         != Source-Aligned
Architecture Looks Same != Source-Aligned
Feature Name Same       != Source-Aligned
```

Source-Aligned 必须有 source owner、symbol owner、call-edge、control-flow、state-transition、ordering、safety invariant、failure invariant、runtime trace、differential test。

允许 Python adaptation，但必须 `PYTHON_ADAPTATION_VERIFIED`。

# 2. 分类宪法

## Reference-7
1. User
2. Interfaces
3. Agent Loop
4. Permission System
5. Tools
6. State & Persistence
7. Execution Environment

## Reference-5
1. Surface Layer
2. Core Layer
3. Safety / Action Layer
4. State Layer
5. Backend Layer

## CCR-14
1. Hook Runtime
2. Authorization Pipeline
3. Context Shaping Pipeline
4. Context Assembly / Injection
5. Tool Pool / Capability Assembly
6. Tool Orchestration
7. Streaming Tool Execution
8. Recovery / Resilience Controller
9. Result Normalization / Result Budget
10. Session / Transcript Runtime
11. Subagent Orchestration
12. Isolation Runtime
13. Trust Lifecycle
14. Runtime Config / Feature Gate Control Plane

CCR-14 是论文+recovered source 的工程化归纳，不宣称为论文官方编号 taxonomy。

# 3. 十四条不可破坏设计原则

1. **Human Decision Authority**：用户可观察、批准/拒绝、打断、恢复/分叉/回退；headless 无法询问时 fail-closed。
2. **Deny-first**：风险未知动作不得 silent allow。
3. **Graduated Trust**：Trust 有 source/scope/lifetime；恢复 transcript 不恢复 session 临时 trust。
4. **Defense in Depth**：`Permission != Hook != Workspace != Sandbox != Network != Process`。
5. **Externalized Policy**：rules/modes/hooks/settings 的来源和 precedence 可追踪。
6. **Context Is Scarce**：先轻后重 progressive shaping。
7. **Append-oriented Durable State**：transcript 是恢复事实源；projection/compact 不伪造 durable history。
8. **Minimal Loop, Maximal Harness**：不得引入第二 core loop/DAG planner 替代 reactive loop。
9. **Values over Workarounds**：临时修复不得破坏上层 invariant。
10. **Composable Extensibility**：MCP/Plugin/Skill/Hook 无旁路。
11. **Reversibility-weighted Risk**：高副作用动作提高 gate/isolation/audit。
12. **Transparent Context Sources**：instruction/memory/config 有 scope/source/load order/provenance。
13. **Isolated Subagents**：共享 canonical loop，但 context/permission/state/transcript 隔离。
14. **Graceful Recovery**：retry/recovery 有显式 trigger、预算、边界和 terminal；不得无限重试。

# 4. Reference-7 强制行为

## R7-01 User
prompt/command、permission ask/allow/deny、interrupt、progress、session control、resume/fork/rewind；同一 scripted action 跨 surface 的核心 decision/state/terminal 一致。

## R7-02 Interfaces
Surface 只做 adapter/render/interaction/interrupt bridge；绝对禁止第二套 permission/tool scheduler/retry/compact/terminal semantics。

## R7-03 Agent Loop
唯一 authoritative reactive loop：`Context → Model → Tool Intent → Authorization → Execution → Result → Context`。

强制 9-step：Settings Resolution → Mutable State → Context Assembly → Context Shapers → Model/Streaming → Tool Dispatch → Authorization → Execution/Result → Stop/Continue。

## R7-04 Permission System
Mode 与 Behavior 分离；deny-first；classifier outage 安全；headless fail-closed；hook allow 不覆盖 deny；subagent/bubble；trust reset。

## R7-05 Tools
永久区分 Registry / Pool Assembly / Orchestration / Execution / Result Processing；Tool contract 必须描述 schema、validation、permission、concurrency、read-only/destructive/open-world、interrupt、result/persistence、MCP identity。

## R7-06 State & Persistence
区分 Durable Transcript / Runtime State / Working Context / Projected Context / Compact Summary / Memory / Sidechain / External Payload。B4 强制真实 resume model re-entry、fork lineage、rewind、crash consistency。

## R7-07 Execution Environment
canonical workspace、real-target check、process lifecycle、env/secrets、network、**real sandbox isolation**、timeout/kill-tree/abort、worktree/remote/MCP backend boundary。`NoSandboxBackend` 永不能算 complete。

# 5. Reference-5 边界

- **R5-01 Surface**：entrypoint/render/interaction，无核心决策。
- **R5-02 Core**：Agent Loop + Context/Compaction，Compact-5 以 2.1.88 实际 source gate 为准。
- **R5-03 Safety/Action**：Permission/Hooks/Tools/Extensibility/Sandbox/Subagent，无旁路。
- **R5-04 State**：Context/Runtime State/Transcript/Memory/Sidechain/Resume/Fork/Rewind。
- **R5-05 Backend**：local process/real sandbox/MCP transport/remote/worktree/filesystem/network/external resources。

# 6. CCR-14 强制合同

## CCR-01 Hook Runtime
证明 event vocabulary、matcher、source、handler type、timeout、blocking/async、error aggregation、event-specific output、Permission/Stop integration；B4 建论文识别 27 events / 7 families coverage matrix。

## CCR-02 Authorization Pipeline
`Visibility Prefilter → PreToolUse → Deny → Ask → Tool-specific check → Mode/Classifier/Human → Isolation override → Execution Boundary`。任何 allow 不能越过后续安全层。

## CCR-03 Context Shaping
`Result Budget → Snip → Microcompact → Context Collapse → AutoCompact`；每层有 trigger/no-op/token accounting/durable-state interaction/error/trace。

## CCR-04 Context Assembly
九来源：System / Environment / CLAUDE.md / Path Rules / Auto Memory / Tool Metadata / Conversation / Tool Results / Compact Summaries；记录 scope/precedence/insertion/lazy/provenance/trust/compact behavior。

## CCR-05 Capability Assembly
`Base → Mode Filtering → Deny Prefilter → MCP/Extension Merge → Deduplication`；model-visible schema 与 actual executor 同源。

## CCR-06 Tool Orchestration
并发安全分类、parallel reads、serialized mutation、result order、context modifiers、sibling failure/abort。

## CCR-07 Streaming Tool Execution
queue→executing→completed→ordered yield；permission 时点、fallback、interrupt、no duplicated side effects。

## CCR-08 Recovery / Resilience
max-output、reactive compact、prompt-too-long、stream fallback、fallback model、rate-limit/backoff；retry 有界。

## CCR-09 Result Processing
raw→normalize→API map→budget/externalize→persist→context；tool_use_id/error/reconstruction 一致。

## CCR-10 Session / Transcript
append/lineage/tail recovery/compact boundary/replacement/sidechain/resume/fork/rewind。**恢复历史 ≠ 恢复信任。**

## CCR-11 Subagent
parent delegate→isolated context→shared loop→sidechain→summary/result→parent；background/pending/stop/resume 是强制 lifecycle。

## CCR-12 Isolation
filesystem/network/env/process/worktree/remote/credentials 独立边界；必须有真实隔离实现。

## CCR-13 Trust
project/hook/MCP/session/add-dir/managed policy 的 source/scope/lifetime；resume/fork 只恢复允许的 durable facts。

## CCR-14 Runtime Config
settings/env/features/experiments/modes/model/tool/surface 在明确边界 snapshot；precedence 稳定；disabled feature 退出 critical path。Scheduler/Background/Streaming/MCP gates 交叉验证。

# 7. Lifecycle Obligations

1. Main Query Loop
2. Tool Execution Loop
3. Permission Escalation
4. Retry / Recovery
5. Compaction
6. Stop Hook
7. Subagent Query
8. Background Agent
9. MCP Lifecycle
10. Scheduler / Cron
11. Resume / Fork / Rewind
12. Surface Streaming / Interrupt
13. Session Persistence / Recovery
14. Long-output Result Budgeting

每项没有 `reference trace + Python trace + tests`，对应 R7/R5/CCR 不得 complete。

# 8. B4 五个特别硬门

- **H1 Real Sandbox**：无真实 isolation，R7-07/R5-05/CCR-12 不完成。
- **H2 Resume True Re-entry**：只有 registry 重注册没有 model/query 重入，R7-06/CCR-10/11 不完成。
- **H3 Compact-5 Differential**：只有 pipeline 代码没有 2.1.88 trigger/order/state differential，CCR-03 不完成。
- **H4 Lifecycle Differential**：Subagent/MCP/Scheduler/Background 没生命周期 trace，不完成。
- **H5 Machine Evidence**：Markdown 声明不能替代 package/symbol/callgraph/state/runtime maps。

# 9. 测试圣经

每个 critical behavior 至少：happy、denied/no-op、error、abort/timeout、resume/recovery（适用）、reference differential、observable side-effect assertion。

安全测试必须验证“未发生副作用”；Cross-surface 必须执行 runtime，不允许只 grep；Sandbox 必须触发真实 isolation；Resume 必须看到 model/tool loop 真实运行。

# 10. Machine Evidence 圣经

最终必须存在：

```text
reference-package-map.yaml
reference-symbol-map.yaml
reference-callgraph-map.yaml
unmapped-reference-symbols.yaml
reference-runtime-trace-map.yaml
reference-state-transition-map.yaml
known-divergences.yaml
scorecards/latest.yaml
scorecards/history/*.yaml
```

完成状态只允许 EXACT / SEMANTIC_EQUIVALENT / PYTHON_ADAPTATION_VERIFIED；PARTIAL/UNKNOWN/MISSING/PRODUCT_EXTENSION/INTENTIONAL_DIVERGENCE 都是未完成。

# 11. PR Gate

每个 B4 PR 必须回答：影响哪个 R7/R5/CCR/lifecycle；Reference 文件/symbol/call-edge；Python owner；control/state/safety/failure invariant；tests；runtime trace；divergence；machine maps 更新。

# 12. 绝对禁止

第二 Agent Loop；DAG planner 替代 reactive loop；Permission 代替 Sandbox；Sandbox 代替 Permission；Hook allow 覆盖 deny；headless silent allow；resume 恢复 temporary trust；compact destructive rewrite；streaming duplicate side effect；surface 私有 core；用测试数量/文档冒充 parity；篡改 UNKNOWN；Final Exit 前抢做外围功能。

# 13. Final Exit Gate

```text
R7: 7/7 complete
R5: 5/5 complete
CCR: 14/14 complete
Lifecycle: 14/14 covered + tested

critical source owners = 100%
critical symbol maps = 100%
critical callgraph = 100%
critical state transitions = 100%
critical runtime traces = 100%

behavior/safety/state-recovery/fault-abort = green
cross-surface runtime differential = green
real sandbox tests = green
current HEAD CI = reproducibly green

critical UNKNOWN = 0
critical PARTIAL = 0
critical MISSING = 0
undocumented divergence = 0
```

在此之前，唯一正确的开发动作是继续关闭 7×5×14。
