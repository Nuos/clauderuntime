# ClaudeRuntime 当前完整诊断基准线 B3

> 文档编号：`CR-B3-DIAGNOSTIC`  
> 状态：**FROZEN BASELINE — SINGLE OBJECTIVE 7×5×14 SOURCE CLOSURE**  
> ClaudeRuntime：`Nuos/clauderuntime@def709361a86900920bf1d6b75134fdc9bc59def`  
> Claude Code reference：`ChinaSiro/claude-code-sourcemap@a8a678cb6244e6770e1e421767ff0987a1d95549` / Claude Code `2.1.88`  
> 论文：arXiv `2604.14228v2`

# 0. B3 基线结论

当前工程已经具备较高实现成熟度，但**不能**按严格 source-aligned 标准宣布完成。

本基线只认一个开发终点：

```text
7 Core Functional Components
+ 5 Reference Subsystem Layers
+ 14 Cross-Cutting Runtime Mechanisms
= 全部与 reference source 的可确认核心语义闭环
```

目录整理、文档治理、产品增强、UI 美化、新 provider、新 workflow、新工具、营销/benchmark 等都不是独立优先级。它们只有在成为 7×5×14 的必要依赖时才允许进入当前开发范围。

# 1. 事实源

冲突裁决顺序：

1. Claude Code 2.1.88 recovered source 的可确认控制流与行为；
2. arXiv 2604.14228v2 对架构、设计空间、机制的解释；
3. 可观察 Claude Code 行为/协议证据；
4. ClaudeRuntime 当前源码与测试；
5. Python / OS 的最小语义等价适配；
6. 历史文档、Roadmap、产品扩展。

**不追求复制 Anthropic 内部 Git 布局。** Source-map 仓库是从公开 npm sourcemap 恢复的研究性源码，因此本项目追求的是可确认运行语义、关键调用关系、状态边界和安全不变量的一致。

# 2. 分类体系修正

## 2.1 Reference-7：正式核心功能组件

1. User
2. Interfaces
3. Agent Loop
4. Permission System
5. Tools
6. State & Persistence
7. Execution Environment

附件中曾使用的：

```text
LLM / Context / AgentLoop / ToolRuntime / Policy / State / Execution Environment
```

只能作为分析视图，**不得再作为正式 7/7 验收清单**。

## 2.2 Reference-5：正式五层系统架构

1. Surface Layer
2. Core Layer
3. Safety / Action Layer
4. State Layer
5. Backend Layer

## 2.3 CCR-14：Cross-Cutting Runtime Mechanisms

B3 采用附件 `index.html` 的 14 类横切机制作为正式工程化 Crosscut Taxonomy：

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

这 14 类是**论文 + recovered source 的二次工程化归纳**，不是论文原文中编号为 14 的官方 taxonomy。

# 3. 当前 Reference-7 状态

| ID | 组件 | B3 状态 | 关键未闭环 |
|---|---|---|---|
| R7-01 | User | UNKNOWN/PARTIAL | 用户 authority contract、跨 surface permission/interrupt/session action trace 仍需正式映射 |
| R7-02 | Interfaces | PARTIAL | 统一 RuntimeEvent、terminal、permission interaction、abort contract 未完整证明 |
| R7-03 | Agent Loop | PARTIAL-HIGH | canonical loop 很强，但 complete source callgraph、stop/recovery/fault differential evidence 不足 |
| R7-04 | Permission System | PARTIAL-HIGH | 存在 deliberate UX divergences；parity/core path 必须恢复 reference gating semantics |
| R7-05 | Tools | PARTIAL-HIGH | descriptor/orchestrator/streaming executor 强，但 tool-pool、MCP、result、interrupt 的完整 source closure 不足 |
| R7-06 | State & Persistence | PARTIAL | Resume/Fork/Rewind、crash consistency、sidechain、trust non-restoration 仍需闭环 |
| R7-07 | Execution Environment | PARTIAL | ExecutionBoundary 已有，但默认 NoSandboxBackend 不提供实际 isolation |

**判定：7/7 有实现表面，0/7 达到 B3 的 `SOURCE-ALIGNED COMPLETE`。**

# 4. 当前 Reference-5 状态

| ID | 层 | 状态 | 关键问题 |
|---|---|---|---|
| R5-01 | Surface | PARTIAL | 各入口是否只做 adapter/render/interaction，尚缺统一 scripted-trace 证明 |
| R5-02 | Core | PARTIAL-HIGH | query loop 与 Compact-5 成熟，但 recovery/stop/terminal 仍需精确对照 |
| R5-03 | Safety / Action | PARTIAL | permission、hooks、tools 已强；sandbox isolation、capability projection、严格 source permission 仍未闭环 |
| R5-04 | State | PARTIAL | durable state / working context / projected context / resume lineage 尚未完整证明 |
| R5-05 | Backend | PARTIAL | local process 强；real sandbox、remote/MCP lifecycle、process/abort boundary 需闭环 |

# 5. 当前 CCR-14 状态

B3 状态按“是否已有 substantial implementation + 是否已有 source-equivalence evidence”综合判断：

| CCR | 机制 | 当前状态 | 主要缺口 |
|---|---|---|---|
| CCR-01 | Hook Runtime | PARTIAL-HIGH | 生命周期事件、blocking/async/timeout/aggregation、stop/permission integration 的完整 source map |
| CCR-02 | Authorization Pipeline | PARTIAL-HIGH | deny/ask/allow + tool checks + hook + classifier + sandbox override 的精确 precedence |
| CCR-03 | Context Shaping Pipeline | PARTIAL-HIGH | Compact-5 已实现，仍需每阶段触发/顺序/持久化/错误 differential |
| CCR-04 | Context Assembly / Injection | PARTIAL | 9 类 context source 的 ordering、dedupe、scope/provenance 证据不完整 |
| CCR-05 | Tool Pool / Capability Assembly | PARTIAL | base tools→mode→deny prefilter→MCP→dedupe 的 source-aligned projection 需锁定 |
| CCR-06 | Tool Orchestration | PARTIAL-HIGH | scheduler 强，仍需 concurrent-safe/serial/result-order/context-modifier 全链证据 |
| CCR-07 | Streaming Tool Execution | PARTIAL-HIGH | speculative start、queue/executing/completed/yielded、fallback/abort/order 需 differential |
| CCR-08 | Recovery / Resilience | PARTIAL | retry、max-output、prompt-too-long、reactive compact、stream fallback、fallback model 需统一 state machine |
| CCR-09 | Result Normalization / Budget | PARTIAL | mapping、budget、replacement、externalization、resume reconstruction 需统一契约 |
| CCR-10 | Session / Transcript Runtime | PARTIAL | append-only、UUID/lineage、partial tail、compact boundary、sidechain、reconstruction 需闭环 |
| CCR-11 | Subagent Orchestration | PARTIAL | delegation、isolated context、permission、sidechain、resume/background、summary return 需闭环 |
| CCR-12 | Isolation Runtime | PARTIAL-LOW | **实际 sandbox isolation 是核心缺口**；workspace/env/network/process/worktree/remote 需统一 boundary |
| CCR-13 | Trust Lifecycle | PARTIAL | resume 不恢复临时 trust、pre-trust/project config/MCP/hook trust 需可证明 |
| CCR-14 | Runtime Config / Feature Gate | PARTIAL | query-entry config snapshot、feature gates、session mode、surface consistency 需统一 control-plane contract |

**判定：14/14 均未达到 B3 的最终完成门。**

# 6. 旧 AUX-14 不删除，而是降级为 Lifecycle Verification Set

旧 AUX 项不是新的 14 个横切机制，但其中包含必须验证的 lifecycle/runtime paths。B3 做如下映射：

| 旧 AUX | 必须验证的行为 | 归属 |
|---|---|---|
| Main Query Loop | model→tools→repeat、continue/terminal | R7-03 + R5-02 |
| Tool Execution Loop | tool scheduling/execution | CCR-06/07 |
| Permission Escalation | ask/classifier/headless/bubble | CCR-02/13 |
| Retry / Model Recovery | retry/fallback/recovery | CCR-08 |
| Compaction Loop | Compact-5 | CCR-03 |
| Stop Hook | stop lifecycle | CCR-01 + R7-03 |
| Subagent Loop | forked query/sidechain | CCR-11 |
| Background Agent | async lifecycle/session | CCR-11/10/14 |
| MCP Lifecycle | capability + transport + auth/trust | CCR-05/06/12/13 |
| Scheduler / Cron | scheduling/control plane | CCR-14 + CCR-10/06 |
| Resume / Fork / Rewind | lineage/recovery/trust reset | CCR-10/13 |
| Surface Streaming / Interrupt | streaming/abort/terminal | R7-02 + CCR-07/08 |
| Session Persistence / Recovery | transcript/reconstruct | CCR-10 |
| Long-output Budgeting | result budget/context shaping | CCR-09/03 |

这些行为均属于 **7×5×14 的必要依赖**，不得因为 taxonomy 调整而延期。

# 7. 已确认的关键高风险缺口

## 7.1 Real Sandbox

当前默认 `NoSandboxBackend` 显式不提供 isolation。抽象存在不等于安全层完成。

B3 要求：

```text
Permission Decision
  != Workspace Boundary
  != Sandbox Isolation
  != Network Policy
  != Env/Secret Policy
  != Process Lifecycle
```

它们必须是可独立失败、可测试的 defense-in-depth 边界。

## 7.2 Permission UX Divergence

当前本地实现有 deliberate UX divergence。B3 不允许这些 divergence 被计入 core source alignment。

要求：

- core/parity profile 复现 reference；
- 产品扩展若保留，必须在 core path 外显式 gate；
- deny/safety 不得被 hook/classifier/UX shortcut 绕过。

## 7.3 Resume / Fork / Rewind

恢复脚手架存在，但 resumed lifecycle 必须真正重新进入 model/query path，并证明：

- transcript reconstruction；
- lineage；
- pending messages；
- crash-tail；
- permission trust reset；
- sidechain；
- race safety。

## 7.4 Crosscut Evidence Gap

实现代码成熟度高于 formal evidence。下一轮必须把关键 package/symbol/call-edge/state-edge 映射到 7×5×14 critical cone，避免“看起来像”被当成 source parity。

# 8. B3 唯一完成门

```text
R7     7/7 complete
R5     5/5 complete
CCR   14/14 complete

旧 AUX lifecycle obligations 100% 被上述节点覆盖并有测试
critical source symbols/call edges 100% mapped
critical runtime traces 100% mapped
critical safety/state/fault invariants green
critical undocumented divergence = 0
current HEAD validation reproducible
```

在此之前，外围研发默认延期。
