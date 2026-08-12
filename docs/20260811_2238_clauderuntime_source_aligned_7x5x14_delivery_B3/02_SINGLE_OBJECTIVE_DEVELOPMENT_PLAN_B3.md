# ClaudeRuntime B3 唯一首要目标开发计划

> 文档编号：`CR-B3-SINGLE-OBJECTIVE-PLAN`  
> 最高行为约束：`CR-SOURCE-ALIGNED-RULE-BIBLE-v4.0`  
> 基线：`def709361a86900920bf1d6b75134fdc9bc59def` / Reference `2.1.88`

# 0. 唯一目标

> **把 Reference-7、Reference-5、CCR-14 全部做到 source-aligned complete。**

当前开发只允许三种工作类型：

```text
CORE_REQUIRED
EVIDENCE_REQUIRED
DEFERRED
```

只要一项工作不能证明“不做它就无法完成 7×5×14”，它就是 `DEFERRED`。

# 1. Critical Cone

当前允许主动开发的代码与证据范围仅限：

- User authority / surface adapters / RuntimeEvent；
- shared query/queryLoop；
- context assembly + Compact-5；
- hooks；
- permission / authorization；
- tool pool / tool descriptor / orchestration / streaming executor；
- retry / recovery / terminal / stop；
- result normalization / budget / persistence；
- transcript / session / sidechain；
- subagent / background / scheduler 必要生命周期；
- trust lifecycle；
- workspace / sandbox / env / network / process；
- MCP critical capability/transport/trust path；
- resume / fork / rewind；
- 证明以上行为所需 source-map、callgraph、tests、fault injection、CI。

# 2. 执行原则

## 2.1 不按“模块好不好做”排序

执行顺序只由 dependency graph 决定：

```text
Reference Contract
    ↓
Core Spine
    ↓
Safety/Action
    ↓
State/Session
    ↓
Isolation/Backend
    ↓
Cross-surface
    ↓
Total Differential Closure
```

## 2.2 不做 cosmetic parity

允许 Python-native package layout，但必须满足：

- reference owner 可定位；
- Python owner 可定位；
- call edge 可映射；
- state transition 可映射；
- behavior/safety/error trace 可比较。

# 3. Wave 0 — Reference Contract Freeze

必须完成：

1. Reference-7 每个组件：文件、symbol、关键 call-edge、state-edge；
2. Reference-5 每层：边界、入口、出口、跨层调用；
3. CCR-14 每个机制：入口、状态机、正常路径、失败路径、退出路径；
4. 旧 AUX lifecycle obligations 全部映射到 R7/R5/CCR；
5. package/symbol/callgraph maps 覆盖整个 critical cone；
6. 所有未确认内容保持 `UNKNOWN`，不得凭记忆填充。

**Exit Gate：所有后续实现任务都有明确 reference evidence。**

# 4. Wave 1 — Canonical Core Spine

覆盖：

- R7-01 User；
- R7-02 Interfaces；
- R7-03 Agent Loop；
- R5-01 Surface；
- R5-02 Core；
- CCR-03 Context Shaping；
- CCR-04 Context Assembly；
- CCR-08 Recovery；
- CCR-14 Runtime Config。

必须实现/验证：

1. 所有 surface 汇入一个 authoritative query path；
2. 一次 turn 的主顺序：
   `settings → mutable state → context assembly → pre-model shapers → model → tool dispatch → permission gate → execution/result → stop/continue`；
3. Compact-5 顺序：
   `Result Budget → Snip → Microcompact → Context Collapse → Auto-Compact`；
4. retry / max-output / prompt-too-long / reactive compact / stream fallback / fallback model；
5. stop condition 与 terminal reasons；
6. abort/generator-close 不留下不可解释 transient state；
7. runtime config 在 query entry 明确快照，避免同一 turn 中配置漂移。

# 5. Wave 2 — Safety / Action Spine

覆盖：

- R7-04 Permission System；
- R7-05 Tools；
- R5-03 Safety/Action；
- CCR-01 Hook Runtime；
- CCR-02 Authorization Pipeline；
- CCR-05 Capability Assembly；
- CCR-06 Tool Orchestration；
- CCR-07 Streaming Tool Execution；
- CCR-09 Result Processing。

必须实现/验证：

```text
Tool Intent
  ↓
Tool Pool / Capability Projection
  ↓
PreToolUse / Hook
  ↓
deny-first rules
  ↓
tool-specific checks
  ↓
permission mode / classifier / human escalation
  ↓
execution-boundary preparation
  ↓
Tool Orchestration
  ↓
Execution
  ↓
Result normalization / budget / persistence
```

强制安全规则：

- deny > ask > allow；
- headless cannot-prompt → fail closed；
- hook allow 不能越过 deny/safety；
- classifier unavailable 不得 silent allow；
- builtin/MCP/subagent-as-tool 使用同一 action contract；
- tool result 必须按 tool-use contract 回写；
- speculative tool execution 不能改变 permission precedence。

# 6. Wave 3 — State / Session / Trust Spine

覆盖：

- R7-06 State & Persistence；
- R5-04 State；
- CCR-10 Session / Transcript；
- CCR-11 Subagent；
- CCR-13 Trust。

必须区分：

```text
Durable Transcript
Runtime State
Working Context
Projected Context
Compacted Summary
Instruction/Memory
Sidechain Transcript
Externalized Result Payload
```

必须闭环：

- append-oriented transcript；
- tail crash tolerance；
- UUID/lineage；
- content replacement reconstruction；
- compact boundary；
- sidechain；
- subagent isolated context + summary return；
- background lifecycle；
- Resume 真正重入 query/model；
- Fork 独立 lineage；
- Rewind 明确 working-state 与 durable history 语义；
- session-scoped trust 不恢复；
- scheduler/pending message/resume race safety。

# 7. Wave 4 — Isolation / Backend Spine

覆盖：

- R7-07 Execution Environment；
- R5-05 Backend；
- CCR-12 Isolation；
- CCR-13 Trust；
- CCR-14 Runtime Config。

必须形成：

```text
Permission
  ↓
Workspace canonicalization / second check
  ↓
Sandbox policy
  ↓
Env / secret policy
  ↓
Network policy
  ↓
Process policy
  ↓
Backend invocation
  ↓
timeout / abort / kill-tree / result
```

`NoSandboxBackend` 只能作为显式 unsandboxed backend。最终 source-aligned mode 必须具备参考语义要求的真实 isolation，或以有证据的 OS-specific verified adaptation 实现。

# 8. Wave 5 — Cross-Surface / Crosscut Closure

此阶段禁止新增产品功能，只做完整闭环：

- same scripted turn → Interactive / Headless / SDK / Desktop / TUI 语义等价；
- hook traces；
- permission traces；
- tool streaming/batched traces；
- result-order traces；
- recovery traces；
- transcript/resume/fork/rewind traces；
- sandbox deny/escape/network/env/process fault traces；
- subagent/background/MCP/scheduler lifecycle traces；
- current HEAD reproducible CI。

# 9. 最终判定

每个 R7/R5/CCR 只能以以下状态计入完成：

- `EXACT`
- `SEMANTIC_EQUIVALENT`
- `PYTHON_ADAPTATION_VERIFIED`

以下全部视为未完成：

- `PARTIAL`
- `UNKNOWN`
- `MISSING`
- `PRODUCT_EXTENSION`
- `INTENTIONAL_DIVERGENCE`

产品 divergence 只能存在于 core source-aligned path 外。

# 10. 默认延期

B3 完成前默认延期：

- 新 provider/vendor；
- 非 reference 必需的新工具；
- 新 workflow 产品功能；
- UI 视觉增强；
- 新 benchmark 包装；
- 营销/发布工程；
- 与 critical cone 无关的性能优化；
- 纯命名/目录模仿；
- 非必要文档美化。

# 11. Program 结束条件

```text
7/7  Reference-7 complete
5/5  Reference-5 complete
14/14 CCR-14 complete

old AUX lifecycle obligations fully covered
critical unknown/partial/missing = 0
critical divergence = 0
critical source / callgraph map complete
critical behavior / safety / state / fault tests green
cross-surface traces equivalent
current HEAD CI reproducible
```
