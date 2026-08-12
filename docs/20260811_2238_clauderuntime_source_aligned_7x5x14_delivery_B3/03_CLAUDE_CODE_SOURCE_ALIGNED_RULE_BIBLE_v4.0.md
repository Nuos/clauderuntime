# Claude Code Source-Aligned 7×5×14 规则圣经 v4.0

> 文档编号：`CR-SOURCE-ALIGNED-RULE-BIBLE-v4.0`  
> 状态：**SUPREME ACTIVE DEVELOPMENT CONSTITUTION**  
> 生效：2026-08-11  
> ClaudeRuntime baseline：`def709361a86900920bf1d6b75134fdc9bc59def`  
> Claude Code recovered source baseline：`a8a678cb6244e6770e1e421767ff0987a1d95549` / `2.1.88`  
> 论文基线：arXiv `2604.14228v2`  
> 本版依据：上一版 B2 + 用户提供的《Claude Code 论文源码：横切机制与分类体系完整归档》`index.html`

# 0. 最高命令

> **所有行为、目标、设计、实现、测试、验收、文档和研发资源分配，必须服务于唯一目标：完整实现并验证 Reference-7 七个核心功能组件、Reference-5 五层系统架构、CCR-14 十四个 Runtime 横切机制，并使其关键语义与 Claude Code 2.1.88 recovered source 的可确认行为一致。**

任何不能证明是该目标直接依赖的工作，默认延期。

# 1. Source-Aligned 的定义

“与源码一致”不是“看起来相似”，而是至少满足：

- control-flow equivalent；
- state-transition equivalent；
- event ordering equivalent；
- permission precedence equivalent；
- tool scheduling/result ordering equivalent；
- context shaping order equivalent；
- retry/recovery/terminal equivalent；
- persistence/resume/fork/rewind semantics equivalent；
- trust lifecycle equivalent；
- sandbox/isolation safety invariant equivalent；
- subagent isolation/return contract equivalent；
- abort/interrupt propagation equivalent；
- surface-independent core semantics equivalent。

允许 Python / OS 适配，但必须能证明 `PYTHON_ADAPTATION_VERIFIED`。

# 2. 分类宪法：永久禁止混用

## 2.1 Reference-7：系统由什么核心功能组成

正式目标只使用论文口径：

1. User
2. Interfaces
3. Agent Loop
4. Permission System
5. Tools
6. State & Persistence
7. Execution Environment

附件中早期分析的：

```text
LLM / Context / AgentLoop / ToolRuntime / Policy / State / Execution Environment
```

作为“运行概念视图”可保留，但不是正式 7/7 closure taxonomy。

## 2.2 Reference-5：这些系统能力位于什么架构层

1. Surface Layer
2. Core Layer
3. Safety / Action Layer
4. State Layer
5. Backend Layer

## 2.3 CCR-14：核心模块之间靠什么 Runtime Harness 连接

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

**CCR-14 是论文 + recovered source 的工程化归纳，不宣称是论文官方“14 项 taxonomy”。**

# 3. 总体设计哲学

本项目的 source-aligned core 必须遵守以下设计原则。

## P01 Human Decision Authority

用户是 authority actor，不是输入字符串。风险动作、权限升级、停止/继续、session 控制必须保持可观察和可干预。

## P02 Deny-first with Human Escalation

默认安全姿态是：

```text
deny > ask > allow
```

未知风险动作不能因便利性静默扩大权限。

## P03 Graduated Trust Spectrum

Trust 是有 scope、有生命周期、有来源的状态，不是全局布尔值。resume 后临时 trust 不自动恢复。

## P04 Defense in Depth

```text
Permission != Hook != Workspace Guard != Sandbox != Network Policy != Process Policy
```

任何一层成功都不能被解释为其他层可省略。

## P05 Externalized Programmable Policy

规则、模式、hooks、project/user/managed settings 必须可追踪来源，并有确定 precedence。

## P06 Context Is Scarce

Context window 是绑定资源之一。必须 progressive management，而不是粗暴删除 durable history。

## P07 Append-oriented Durable State

持久化事实源优先 append-oriented、可审计、可重建。Context projection/compaction 不得伪造 transcript。

## P08 Minimal Reasoning Scaffolding, Maximal Harness

核心 reasoning loop 保持简单；复杂度放在可测试的 harness：permission、context、tool、state、isolation、recovery。

## P09 Values over Ad-hoc Rules

单个 workaround 不得破坏上层安全、可恢复、可审计原则。

## P10 Composable Extensibility

MCP、Plugin、Skill、Hook 等扩展机制必须进入统一 capability/policy/runtime boundary，不得形成旁路。

## P11 Reversibility-weighted Risk

不可逆或高副作用动作需要更严格 gate / isolation / audit。

## P12 Transparent File-based Configuration and Memory

配置、instruction/memory source 必须可追溯 scope、source、load order。

## P13 Isolated Subagent Boundaries

Subagent 复用核心 loop，但 context/state/permission/transcript 必须有隔离边界。

## P14 Graceful Recovery and Resilience

Recovery 必须是显式状态机，不是散落 try/except。

# 4. Reference-7 行为圣经

## R7-01 User

必须支持：

- prompt / command；
- permission allow/deny/ask；
- interrupt/abort；
- tool/assistant/result/error 可见性；
- resume/fork/rewind/session control；
- headless 无交互时的明确 fail-closed；
- 不允许 UI 伪造工具已执行、权限已允许、session 已恢复。

**验收不变量**：同一用户动作通过不同支持 surface，进入相同核心 decision/state/terminal 语义。

## R7-02 Interfaces

Surface 只允许承担：

- input adapter；
- event/render adapter；
- permission interaction；
- progress display；
- interrupt bridge。

禁止：

- 第二套 permission engine；
- 第二套 tool scheduler；
- 第二套 retry/compact semantics；
- surface 自己决定 terminal outcome。

所有入口最终汇入 shared core path。

## R7-03 Agent Loop

canonical pattern：

```text
model
  ↓
tool intent
  ↓
permission/action
  ↓
tool result
  ↓
model
  ↓
...
```

必须：

1. 一个 authoritative reactive loop；
2. model-call 前统一 context shaping；
3. streaming response；
4. tool-use dispatch；
5. action boundary；
6. result 回写下一轮；
7. stop/continue 显式；
8. retry/recovery 作为同一 loop 的 transition；
9. terminal reasons 唯一事实源；
10. abort/throw/generator-close 有可解释 cleanup。

禁止 central DAG planner 替代 reference reactive loop。

## R7-04 Permission System

必须区分：

```text
Permission Mode = 会话/agent 所处信任工作模式
Permission Behavior = 单次 action 的 allow / deny / ask
```

必须覆盖：

- rules；
- modes；
- tool-specific check；
- hooks；
- classifier/auto；
- interactive ask；
- headless fail-closed；
- subagent/bubble semantics；
- sandbox override reason；
- trust reset。

任何 reference gated risk-bearing action，在 source-aligned core mode 不能因本地 UX preference silent allow。

## R7-05 Tools

Tool contract 至少包含：

- name / aliases；
- input schema；
- validation；
- permission check；
- concurrency-safe；
- read-only/destructive/open-world；
- interrupt behavior；
- result mapping；
- result-size policy；
- progress/activity metadata；
- MCP identity；
- optional permission matcher / observable input。

必须永久区分：

```text
Tool Registry
Tool Pool Assembly
Tool Orchestration
Tool Execution
Result Processing
```

它们不是同一个模块。

## R7-06 State & Persistence

必须区分：

```text
Durable Transcript
Runtime Mutable State
Working Context
Projected Context
Compacted Summary
Instructions / Memory
Sidechain Transcript
Externalized Tool Payload
```

强制：

- append-oriented；
- schema/version；
- partial-tail tolerance；
- resume reconstruction；
- fork lineage；
- rewind semantics；
- sidechain；
- content replacement；
- trust non-restoration；
- terminal/state consistency。

## R7-07 Execution Environment

必须提供：

- canonical workspace/path；
- real-target/symlink second check；
- process lifecycle；
- env/secret policy；
- network policy；
- real sandbox isolation；
- timeout/kill-tree/abort；
- worktree/remote/MCP backend required path；
- capability detection + fail policy。

# 5. Reference-5 系统架构圣经

## R5-01 Surface Layer

**职责**：entrypoint、render、interaction。

禁止承载 core decision。

## R5-02 Core Layer

**职责**：Agent Loop + Context/Compaction core。

Pre-model Context Shaping 顺序必须保持：

```text
1 Result Budget
2 Snip
3 Microcompact
4 Context Collapse
5 Auto-Compact
```

## R5-03 Safety / Action Layer

包括：

- Permission；
- Hooks；
- Tool/Capability；
- Extensibility；
- Sandbox policy/invocation；
- Subagent action spawning。

原则：defense in depth、deny-first、无旁路。

## R5-04 State Layer

包括：

- Context Assembly；
- Mutable State；
- Transcript；
- Memory / instructions；
- Sidechains；
- Resume/Fork/Rewind。

## R5-05 Backend Layer

包括：

- local shell/process；
- sandbox backend；
- MCP transports；
- remote/worktree required backend；
- filesystem/network/external resources。

# 6. CCR-14 Runtime 横切机制行为圣经

## CCR-01 Hook Runtime

Hook 是 lifecycle extension runtime，不是普通 callback 集合。

必须定义并验证：

- event vocabulary；
- event → matching → handler selection；
- command/prompt/http/agent/function/callback 等 supported execution forms；
- blocking vs non-blocking；
- timeout；
- error aggregation；
- allow/deny/ask/continue/stop 等 event-specific result；
- SessionStart/End、UserPrompt、Pre/PostTool、Permission、Pre/PostCompact、Subagent、Stop 等关键 lifecycle；
- hook failure 不得隐式绕过 permission/safety。

**Stop Hook** 是 CCR-01 + R7-03 的 lifecycle obligation。

## CCR-02 Authorization Pipeline

`Policy/Permission` 是规则与决策语义；`Authorization Pipeline` 是一次 action 如何从 intent 变为最终执行决策。

目标流水：

```text
Tool Intent
  ↓
Tool visibility / prefilter
  ↓
PreToolUse Hook
  ↓
deny rules
  ↓
ask rules
  ↓
tool-specific permission check
  ↓
mode / classifier / user escalation
  ↓
sandbox override / execution decision
  ↓
Execution Boundary
```

必须保证：

- deny-first；
- ask 不被 silent allow；
- classifier outage fail-safe；
- headless no-prompt fail-closed；
- hook allow 不能覆盖 deny/safety；
- user-updated input 的传播可追踪。

## CCR-03 Context Shaping Pipeline

回答：“上下文太多时怎么办”。

强制 Compact-5：

```text
Result Budget
  ↓
Snip
  ↓
Microcompact
  ↓
Context Collapse
  ↓
Auto-Compact
```

每阶段必须有：

- trigger；
- input/output contract；
- token accounting；
- durable-state interaction；
- no-op semantics；
- error behavior；
- trace evidence。

Context Collapse 必须保持 read-time projection / equivalent semantics，不得被实现为 destructive transcript deletion。

## CCR-04 Context Assembly / Injection

回答：“这一轮模型究竟看到什么”。

至少跟踪 9 类 source：

1. System Prompt
2. Environment
3. CLAUDE.md / Instructions
4. Path-scoped Rules
5. Auto Memory
6. Tool Metadata
7. Conversation History
8. Tool Results
9. Compact Summaries

必须规定：

- source scope；
- precedence；
- insertion point；
- dedupe；
- provenance；
- security filtering；
- compact boundary behavior。

## CCR-05 Tool Pool / Capability Assembly

模型可见能力必须是运行时投影，不是 registry 全量暴露。

目标 stages：

```text
1 Base Tool Enumeration
2 Mode Filtering
3 Deny-rule Pre-filtering
4 MCP / Extension Integration
5 Deduplication
```

必须保证：

- denied capability 不进入 model-visible pool；
- MCP identity 不与 builtin 名称混淆；
- tool schema/metadata 与 runtime executor 同源；
- session/mode/tool availability changes 有确定生效点。

## CCR-06 Tool Orchestration

负责多个 tool call 的调度：

- concurrency classification；
- parallel safe reads；
- serialized mutation；
- dependency/order；
- context modifiers；
- completion tracking；
- result ordering；
- sibling failure/abort semantics。

`ToolRuntime = executor`，`Tool Orchestrator = scheduler`，不得混淆。

## CCR-07 Streaming Tool Execution

必须覆盖：

```text
model streaming
  ↓ partial/complete tool_use
queue
  ↓
executing
  ↓
completed
  ↓
ordered yield
```

必须验证：

- speculative/early execution；
- permission 在正确阶段；
- fallback to non-streaming path；
- sibling abort；
- user interrupt；
- completed result 的原 tool-use 顺序；
- stream failure 不泄漏重复 side effect。

## CCR-08 Recovery / Resilience Controller

至少覆盖五类：

1. max-output-token escalation；
2. reactive compaction；
3. prompt-too-long recovery；
4. streaming fallback；
5. fallback model。

另外统一 retry/backoff、429/5xx 等模型错误策略。

每个 recovery 必须显式拥有：

- trigger；
- bounded retry count；
- state mutation；
- emitted/withheld intermediate error；
- continue reason；
- terminal reason；
- budget interaction。

禁止无限 retry。

## CCR-09 Result Normalization / Result Budget

Tool world → Model observation 的转换必须显式：

```text
Raw Tool Output
  ↓
Normalization
  ↓
API Mapping
  ↓
Budget / Replacement / Externalization
  ↓
Persistence Record
  ↓
Context Projection
```

必须保证：

- tool_use_id 一致；
- error flag 一致；
- oversize payload 可重建；
- resume 后 replacement 不丢失；
- Read 等特殊工具的 persistence policy 与 reference 一致；
- truncation/externalization 不伪造完整结果。

## CCR-10 Session / Transcript Runtime

必须覆盖：

- main session；
- sidechain/subagent transcript；
- UUID/parent lineage；
- append-oriented write；
- partial-tail recovery；
- compact boundary；
- content replacement；
- worktree/session metadata；
- resume reconstruction；
- fork lineage；
- rewind semantics。

**Session state ≠ Context**。Context 可以被重塑，durable transcript 是恢复事实源。

## CCR-11 Subagent Orchestration

必须明确 delegation contract：

- prompt；
- model；
- tool pool；
- permission mode；
- skills/hooks；
- max turns/budget；
- cwd/worktree；
- sidechain transcript。

运行不变量：

```text
Parent
  ↓ delegate
Isolated Subagent Context
  ↓ shared canonical query loop
Sidechain Transcript
  ↓ summary / result contract
Parent Context
```

Background Agent lifecycle、pending messages、auto-resume、task stop 都是 CCR-11 的必要生命周期验证项。

## CCR-12 Isolation Runtime

回答：“即使 action 被允许，它仍能看到/影响什么”。

必须独立约束：

- filesystem；
- network；
- env/secrets；
- subprocess；
- worktree；
- remote；
- credentials。

强制：

```text
Permission ≠ Isolation
Execution Environment ≠ Isolation
```

`NoSandboxBackend` 不可计为 source-aligned isolation complete。

## CCR-13 Trust Lifecycle

Trust 必须带 scope/source/time/lifecycle。

必须验证：

- project config trust；
- hook source trust；
- MCP server trust；
- session permission grants；
- additional working directory grants；
- resume/fork 后哪些 trust 可恢复、哪些必须重新建立；
- managed policy 对 trust 的上限约束。

核心原则：**恢复历史 ≠ 恢复临时信任。**

## CCR-14 Runtime Config / Feature Gate Control Plane

必须在明确边界快照/解析：

- settings；
- environment；
- feature flags；
- experiment gates；
- permission/session mode；
- model/tool gates；
- surface mode。

必须：

- query/turn 内不可出现无定义配置漂移；
- source of truth 明确；
- precedence 明确；
- disabled feature 必须完全退出相关 critical path；
- surface 不得私自覆写 core semantic gate。

Scheduler/Cron、Background 模式、Streaming feature 等生命周期要求在此与各目标机制交叉验证。

# 7. 一次 Agent Turn 的强制 9-step Trace

每个 source-aligned differential test 应能映射到：

```text
1 Settings Resolution
2 Mutable State Initialization
3 Context Assembly
4 Pre-model Context Shapers
5 Model Call / Streaming
6 Tool-use Dispatch
7 Permission / Authorization Gate
8 Tool Execution + Result Collection
9 Stop / Continue Decision
```

如果某 surface 或优化路径跳过其中一步，必须能说明 reference source 的等价路径。

# 8. Tool Execution 的双路径规则

## Path A — Streaming Tool Executor

目标：降低 latency，但不改变安全语义。

```text
LLM still streaming
  ↓
tool_use formed
  ↓
permission/action boundary
  ↓
early execution where safe
```

## Path B — Batched / runTools-style

```text
complete tool calls
  ↓
concurrency classification
  ↓
parallel safe / serialized unsafe
  ↓
ordered result yield
```

两路径必须在：

- permission；
- tool validation；
- result mapping；
- state update；
- abort；
- final ordering

上保持语义一致。

# 9. Stop / Continue 规则

至少覆盖五类终止条件：

1. no tool use / natural completion；
2. max turns/budget；
3. context overflow unrecoverable；
4. hook intervention；
5. explicit abort。

此外 Python-only terminal reason 可以保留，但必须登记为 adaptation/product extension，不得改变 reference-observable core semantics。

# 10. Safety Architecture 规则

按纵深防御验证至少七类 safety gate：

```text
1 Tool visibility / pre-filter
2 Deny-first rules
3 Permission mode constraints
4 Auto/classifier decision
5 Hook interception
6 Workspace / Sandbox / Network / Process isolation
7 Resume trust non-restoration
```

顺序若与具体 source path 不同，以 source callgraph 为准；但任何层不得被等价“折叠掉”。

# 11. Permission 分类规则

## Mode

必须以 reference source 实际 mode vocabulary 和行为为准；当前实现中的外部/内部 modes 必须分别标注。

## Behavior

单次 action 只有：

```text
allow
deny
ask
```

不得把 mode 与 behavior 混写。

# 12. Context 与 Memory 规则

## Context Sources

使用 CCR-04 的 9 类来源。

## Instruction / Memory Scope

对 CLAUDE.md / memory-like instructions 必须明确：

- managed；
- user；
- project；
- local/path-scoped；
- auto memory / generated memory（若 reference critical cone 存在）。

加载层级、覆盖/合并、scope、trust 都必须有 source evidence。

# 13. Extension 规则

MCP / Plugin / Skill / Hook 等扩展不按“插件数量”验收，而按：

- context cost；
- insertion point；
- unique capability；
- permission/isolation boundary；
- lifecycle；
- source/trust provenance

验收。

任何 extension 不得绕开 CCR-02、CCR-05、CCR-06、CCR-12、CCR-13。

# 14. Lifecycle Obligations：旧 AUX 全部保留

以下不是新的 peer taxonomy，但都是 7×5×14 completion 的强制验证：

- Main Query Loop；
- Tool Execution Loop；
- Permission Escalation；
- Retry/Recovery；
- Compaction；
- Stop Hook；
- Subagent Query；
- Background Agent；
- MCP Lifecycle；
- Scheduler/Cron；
- Resume/Fork/Rewind；
- Surface Streaming/Interrupt；
- Session Persistence/Recovery；
- Long-output Result Budgeting。

任何一项没有 source trace + Python trace + tests，则相关 R7/R5/CCR 不能 complete。

# 15. PR / Commit 强制 Gate

每个 critical PR 必须回答：

1. 影响哪个 R7？
2. 影响哪个 R5？
3. 影响哪个 CCR？
4. 影响哪些 lifecycle obligations？
5. reference source 文件/symbol/call-edge 是什么？
6. Python owner 是什么？
7. control-flow invariant？
8. state invariant？
9. safety invariant？
10. failure/abort/retry invariant？
11. tests？
12. 是否有 divergence？
13. 若是 Python adaptation，等价证据是什么？
14. machine-readable maps 是否更新？

缺一项，不得以“功能已能运行”宣告 source-aligned complete。

# 16. 完成状态

只允许三种完成状态：

```text
EXACT
SEMANTIC_EQUIVALENT
PYTHON_ADAPTATION_VERIFIED
```

以下全部算未完成：

```text
PARTIAL
UNKNOWN
MISSING
PRODUCT_EXTENSION
INTENTIONAL_DIVERGENCE
```

产品 extension/divergence 可以存在，但必须在 source-aligned core path 外。

# 17. 绝对禁止

- 禁止新增第二 Agent Loop；
- 禁止用 DAG planner 取代 reference reactive loop；
- 禁止 permission 代替 sandbox；
- 禁止 sandbox 代替 permission；
- 禁止 hook allow 覆盖 deny/safety；
- 禁止 headless risky ask 静默 allow；
- 禁止恢复 session-scoped temporary trust；
- 禁止 compact 删除 durable history 以伪装节省 context；
- 禁止 tool streaming 造成重复 side effect；
- 禁止 surface 自己实现不同 core semantics；
- 禁止为 TypeScript 目录外观破坏 Python 合理边界；
- 禁止把“代码存在”“测试文件存在”“文档写了”当成 parity evidence；
- 禁止为了完成率把 UNKNOWN 直接改 PARTIAL/COMPLETE；
- 禁止外围产品需求抢占 7×5×14 critical cone。

# 18. 最终 Exit Gate

只有以下全部成立，本圣经允许解除“外围研发默认延期”：

```text
R7:   7/7   complete
R5:   5/5   complete
CCR: 14/14  complete

Lifecycle obligations: 14/14 covered and tested

critical source owner = 100%
critical symbol map = 100%
critical callgraph = 100%
critical state transitions = 100%
critical runtime traces = 100%

critical behavior tests = green
critical safety tests = green
critical state/recovery tests = green
critical fault/abort tests = green
cross-surface equivalence = green
current HEAD validation = reproducible

critical UNKNOWN = 0
critical PARTIAL = 0
critical MISSING = 0
critical undocumented divergence = 0
```

在此之前，唯一正确的开发行为是继续完成 7×5×14。
