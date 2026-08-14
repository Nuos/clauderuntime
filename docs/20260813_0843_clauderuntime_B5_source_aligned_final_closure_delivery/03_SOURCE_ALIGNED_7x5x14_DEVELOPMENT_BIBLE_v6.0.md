# Claude Code Source-Aligned 7×5×14 开发圣经 v6.0 — B5 Truth-First Final Closure Edition

> 文档编号：`CR-SOURCE-ALIGNED-RULE-BIBLE-v6.0`  
> 状态：**SUPREME ACTIVE DEVELOPMENT CONSTITUTION**  
> 生效：2026-08-13  
> ClaudeRuntime 起始 HEAD：`95efbaec4796147657668c4947a0d2088ecc4738`  
> Claude Code recovered source：`2.1.88` @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：arXiv `2604.14228v2`  
> 继承 v5.0 的安全与架构原则；本版新增 **Truth-First / Evidence Consistency / No Self-Authored Oracle** 强制条款。

---

# 0. 最高命令

> **B5 的唯一目标不是“让完成率看起来更高”，而是让 7 Reference Components + 5 System Layers + 14 CCR Mechanisms 的每个完成声明都能从 Claude Code 2.1.88 source → Python implementation → runtime trace → differential test 连续证明。**

发现历史 VERIFIED 错误时，必须立即降级；降级是质量改进，不是项目倒退。

---

# 1. 唯一正式分类

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

旧 “5 Parity Layers” 与 legacy AUX-01..14 只能作为历史映射，不再是 active completion taxonomy。

---

# 2. Source-Aligned 完成证据

一个节点只能在以下字段全部满足后标 final verified：

```yaml
reference_files: non-empty
reference_symbols: non-empty
reference_call_edges: non-empty
python_files: non-empty
python_symbols: non-empty
python_call_edges: non-empty
control_flow: proven
state_transitions: proven
ordering_invariants: proven
safety_invariants: proven_if_applicable
failure_invariants: proven_if_applicable
runtime_trace: non-empty
differential_tests: non-empty
platform_evidence: complete_if_platform_dependent
divergence: none_or_registered
```

完成证据状态只允许：

```text
EXACT
SEMANTIC_EQUIVALENT
PYTHON_ADAPTATION_VERIFIED
```

`PARTIAL / UNKNOWN / MISSING / PRODUCT_EXTENSION / INTENTIONAL_DIVERGENCE` 都不能计 final complete。

---

# 3. B5 新增十二条 Truth Rules

## TR-01 — One Active Taxonomy

仓库只能存在一套 active 7×5×14 分类。旧体系必须标 LEGACY，不得同时声称“official”。

## TR-02 — HEAD-bound Evidence

release scorecard 的 `baseline_commit` 必须等于被验收的当前 HEAD。旧 commit 的 map 不能证明新 HEAD。

## TR-03 — Evidence Atomicity

coverage/callgraph/state/runtime/divergence/scorecard 必须原子生成。任何同一节点状态冲突，CI 直接失败。

## TR-04 — No Self-Authored Oracle

项目自己编写的 `reference_data/*.json`、手写表格、注释不能作为唯一 Reference oracle。

它们只能是 cache/snapshot；必须能追溯到 recovered source 文件/symbol/hash 或论文明确事实。

## TR-05 — Feature-gated Semantics Must Stay Feature-gated

Reference 中由 build flag / runtime flag 控制的机制，不得被 Python 无条件执行，也不得因默认关闭而删除整个调用形态。

## TR-06 — Semantic Category Integrity

“路径作用域上下文规则”不能映射成“权限规则”；“permission”不能映射成“sandbox”；“transcript”不能映射成“working context”。名称相似不构成语义等价。

## TR-07 — Durable Means Restart-survivable

依赖进程内对象的 resume 只能叫 same-process resume。除非 Reference 本身只要求进程内，否则不能计 durable resume complete。

## TR-08 — Platform Truthfulness

只在 macOS 验证的 real sandbox 只能写“macOS verified”。如果产品声明 Linux/Windows 支持，则 R7-07/CCR-12 不能整体 complete。

## TR-09 — Stronger Is Still a Divergence

Python 做得“更安全/更严格/更方便”仍可能改变 observable behavior。任何更强行为必须登记 divergence 并证明它是否允许 `PYTHON_ADAPTATION_VERIFIED`。

## TR-10 — Surface Claims Require Surface Execution

不能用源码 grep 或 core/server 两入口测试代表 TUI/Desktop/IDE。每个声明支持的 Surface 要么执行 differential，要么明确排除在 core parity 计分外。

## TR-11 — Side-effect Proof

安全测试必须证明副作用未发生：文件未写、网络未连、子进程已死、secret 未暴露；不能只断言返回错误文本。

## TR-12 — CI Truthfulness

没有 current HEAD workflow/status 证据时，只能写“local tests green”，禁止写“CI green”。

---

# 4. 十四条架构原则继续生效

1. Human Decision Authority
2. Deny-first with Human Escalation
3. Graduated Trust
4. Defense in Depth
5. Externalized Programmable Policy
6. Context Is Scarce
7. Append-oriented Durable State
8. Minimal Loop, Maximal Harness
9. Values over Workarounds
10. Composable Extensibility
11. Reversibility-weighted Risk
12. Transparent File-based Configuration / Context Sources
13. Isolated Subagent Boundaries
14. Graceful Recovery and Resilience

强制关系：

```text
Permission != Hook != Workspace Guard != Sandbox != Network != Process
Session State != Working Context != Durable Transcript
Tool Registry != Tool Pool != Orchestration != Execution != Result Processing
```

---

# 5. Reference-7 Hard Contracts

## R7-01 User

支持 prompt/command、permission allow-deny-ask、interrupt、progress、session actions、resume/fork/rewind。相同用户动作跨支持 Surface 进入相同 core semantics。

## R7-02 Interfaces

Surface 只负责 input/output/render/interaction/interrupt bridge。禁止第二套 permission、retry、compact、scheduler、tool execution、terminal semantics。

## R7-03 Agent Loop

唯一 authoritative reactive loop：

```text
Context → Model → Tool Intent → Authorization → Execution → Result → Context
```

不得用 DAG planner 替代。9-step trace 必须可重放。

## R7-04 Permission System

Mode 与 action behavior 分开；deny-first；headless fail-closed；classifier failure 安全；hook allow 不越过 deny/safety；trust scope 可追踪。

## R7-05 Tools

Registry / Pool / Orchestrator / Executor / Result Processor 分离；streaming/batched path 的 authorization、ordering、abort、result mapping 等价。

## R7-06 State & Persistence

Durable transcript 是恢复事实源。必须覆盖：tail tolerance、content replacement、compact boundary、sidechain、resume、fork、rewind、lineage、crash consistency、trust non-restoration。

**同进程内 `resume_run_params` 不可独立证明 durable resume。**

## R7-07 Execution Environment

workspace canonicalization、real-target check、env/secret、process lifecycle、network、real sandbox、worktree/remote、capability detection、fail policy。

`NoSandboxBackend` 永不计 real isolation。

---

# 6. Reference-5 Hard Boundaries

## Surface
只做 surface concerns，不拥有 core decision。

## Core
Agent Loop + Context/Compact。必须按 2.1.88 source 的真实调用顺序和 feature gates。

## Safety / Action
Permission/Hooks/Tools/Extensions/Subagent/Sandbox policy；无 bypass。

## State
Context Assembly/Mutable State/Transcript/Memory/Sidechain/Resume/Fork/Rewind。

## Backend
Process/Sandbox/MCP/Remote/Worktree/Filesystem/Network/External Resources。

---

# 7. CCR-14 Hard Contracts

## CCR-01 Hook Runtime

事件 vocabulary、matcher、source、handler type、blocking/async、timeout、error aggregation、event-specific output、Stop/Permission integration。

## CCR-02 Authorization Pipeline

```text
Capability visibility
→ PreToolUse
→ deny
→ ask
→ tool-specific check
→ mode/classifier/user
→ isolation decision
→ execution boundary
```

## CCR-03 Context Shaping

Reference 2.1.88 真实行为是连续的 pre-model shaping pipeline。禁止无 source 证据的全局 early-return 改变后续 shaper 是否执行。

Snip/Microcompact/Collapse/Autocompact 的 feature gate、boundary、cache、token、persistence 语义分别验证。

## CCR-04 Context Assembly

九来源中的 Path-scoped Rules 是 context instructions，不是 permission rules。必须有 file-path-triggered lazy load E2E。

## CCR-05 Capability Assembly

Base→mode/filter→deny prefilter→MCP/extensions→dedupe；model-visible schema 与 executor 同源。

## CCR-06 Tool Orchestration

parallel safe reads、serialized mutation、sibling abort、ordered result、dependency/state modifier。

## CCR-07 Streaming Tool Execution

partial tool_use→queue→authorization→execute→complete→ordered yield；failure 不重复 side effect。

## CCR-08 Recovery / Resilience

bounded retry、max-output、prompt-too-long、reactive compact、stream fallback、model fallback；intermediate error 是否可见必须匹配 reference。

## CCR-09 Result Processing

raw→normalize→API map→budget/externalize→persist→reconstruct→context；tool_use_id/error flag 不能漂移。

## CCR-10 Session / Transcript

resume/fork/rewind 必须建立在 durable data + current runtime reconstruction 上；历史恢复不能恢复 session temporary trust。

## CCR-11 Subagent

isolated context、rebuilt tool/permission scope、sidechain、summary-only return、background、message/stop/resume、worktree lifecycle。

## CCR-12 Isolation

filesystem/network/env/process/worktree/remote/credentials 独立约束；按产品支持平台逐一证明。

## CCR-13 Trust

source/scope/lifetime/managed upper bound；pre-trust initialization 不允许扩权；resume/fork trust reset。

## CCR-14 Runtime Config

settings/env/features/modes/model/tool/surface gate 有单一 snapshot/precedence；Scheduler/Background/MCP gate lifecycle 不得散落成互相冲突的状态。

---

# 8. Compact-5 特别禁令

以下行为在 B5 必须 source-proof：

- HISTORY_SNIP 是否开启、何时执行、是否产生 boundary；
- microcompact 是“调用后内部 no-op”还是“整个 stage 不调用”；
- cached microcompact 的 cache_edits；
- context collapse 的 read-time projection；
- autocompact threshold/attachments/hooks；
- reactive compact 与 normal compact 交互。

任何 `early_exit_tokens` 类优化如果无法在 2.1.88 source 找到等价 call-edge，只能放 PRODUCT_EXTENSION path。

---

# 9. Context-9 特别禁令

`.clawcodex/rules/*.md paths:` 必须作为**上下文指令**处理。禁止将它计入 permission rule 以满足矩阵。

`VERIFIED` 必须包含：

```text
read file A
→ resolve path A
→ discover/match rule
→ inject rule exactly once
→ next model call sees it
→ unrelated file does not load it
```

---

# 10. Resume 特别禁令

只有以下行为完整时才能叫 durable source-aligned resume：

```text
Disk transcript/meta
→ sanitize/reconstruct
→ current runtime dependencies rebuild
→ current tool/permission/system prompt rebuild
→ worktree/content replacements restore
→ canonical agent loop
→ durable terminal state
```

进程内复制对象不是持久化。

---

# 11. Sandbox 特别禁令

- macOS verified ≠ cross-platform verified；
- process-tree kill ≠ isolation；
- host 字符串 allowlist ≠ secure network isolation；
- Permission allow ≠ Sandbox allow；
- Sandbox deny 发生后必须验证无副作用；
- capability unavailable 且 policy 要求 isolation 时必须 fail-closed。

---

# 12. Scheduler 特别规则

Scheduler 必须区分：session-scoped / durable file-backed / missed / recurring / owner locking / reschedule / cancel / restart。

如果 Python 使用不同 persistence architecture，必须给出 state-machine differential 证明 observable equivalence。

---

# 13. Testing Constitution

每个 critical contract 至少：

1. happy path；
2. no-op/disabled gate；
3. deny/failure path；
4. timeout/abort；
5. recovery/resume（适用时）；
6. side-effect assertion；
7. reference differential；
8. machine map update。

Reference fixture 必须从 source-extracted evidence 生成或附 source hash；禁止手写一个“TS snapshot”后只测试 Python 符合这个 snapshot。

---

# 14. PR Gate

每个 B5 PR 必须填写：

```text
R7 owner
R5 owner
CCR owner
Reference files/symbols/call edges
Python files/symbols/call edges
Control flow
State transition
Ordering invariant
Safety invariant
Failure invariant
Runtime trace
Differential tests
Platform evidence
Divergence
Machine maps changed
```

缺一项不得命名为 `closure`。

---

# 15. Final Exit Gate

最终生成的 machine scorecard 必须满足：

```text
R7 = 7/7
R5 = 5/5
CCR = 14/14
critical UNKNOWN = 0
critical PARTIAL = 0
critical MISSING = 0
critical open divergence = 0
unmapped critical symbol = 0
cross-file status contradiction = 0
```

并且 native macOS/Linux/Windows（对声明支持的平台）与全部支持 Surface 的 runtime differential 均绿。

在此之前，唯一正确的项目状态是：

```text
SOURCE_ALIGNED_CORE_IN_PROGRESS
```
