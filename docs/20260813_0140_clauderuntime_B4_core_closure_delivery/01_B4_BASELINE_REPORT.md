# ClaudeRuntime B4 前置基线报告：B3 完成后 Source-Aligned 核验

> 文档编号：`CR-B4-BASELINE-2026-08-13`  
> 状态：**NEXT DEVELOPMENT BASELINE / FROZEN AUDIT SNAPSHOT**  
> 审计日期：2026-08-13  
> ClaudeRuntime 当前 `main`：`4a77f068649e18351e4c51d97e5a6667c9c4a5fd`  
> 当前提交：`test: 完成B3 Wave4/5核验与修复`  
> Claude Code recovered source：`2.1.88` @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：`Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems`, arXiv:2604.14228v2  
> 上一约束：`03_CLAUDE_CODE_SOURCE_ALIGNED_RULE_BIBLE_v4.0.md`

---

# 0. 基线结论

B3 **已经完成主体开发和大量验证，但没有达到规则圣经 §18 的最终 Source-Aligned Exit Gate**。

最重要的判断不是“Wave 0–5 是否都做过”，而是：

> **B3 已把项目从“功能存在”推进到“多数核心语义已有专项测试”，但当前仍处于 Source-Aligned Closure 阶段，而不是 7×5×14 完成态。**

当前仓库自身的最终验证报告明确记录：

- 全量 pytest：`10122 passed / 10 skipped / 4 warnings / 345 subtests`；
- Wave 4/5 定向测试：`40/40`；
- 文档治理、POSIX 安装、Python build、CLI 入口通过；
- **Real Sandbox 未实现**；
- **resume_agent_background 不驱动真实 model 重入**；
- `DefaultProcessPolicy` 仍属 placeholder；
- Compact-5、9 Context Sources、Subagent、MCP、Scheduler 仍缺专项行为差分；
- cross-surface 当前部分测试只是源码结构断言，不等于真实 runtime differential；
- machine-readable parity control plane 仍不完整。

因此本报告冻结以下判断：

| 维度 | 评估 | 结论 |
|---|---:|---|
| 一般工程成熟度 | **90/100** | 高：测试体量、模块化、文档治理成熟 |
| 7×5×14 实现成熟度 | **85/100** | 主体机制多数存在，仍有硬缺口 |
| Source-level 证据完整度 | **60/100** | 映射和 differential evidence 落后于实现 |
| Safety / State / Failure 证明成熟度 | **78/100** | 权限强；sandbox/resume 阻塞 |
| 严格 §18 Exit Gate Readiness | **72/100** | 不能宣告 Source-Aligned Complete |

> 百分比是本次审计的工程估计，用于开发排序，不是仓库自动计算结果。

---

# 1. 证据基线

1. Claude Code recovered source 2.1.88：`ChinaSiro/claude-code-sourcemap`；
2. 论文 v2：7-component、5-layer、query loop、permission、context、tools、subagent、persistence；
3. ClaudeRuntime 当前 HEAD 源码；
4. ClaudeRuntime 当前 HEAD 测试与 B3 Wave 0–5 验证记录；
5. B3 规则圣经与 Closure Matrix；
6. 工程推断（只用于排序，不代替 parity evidence）。

Recovered source 是公开 source-map 还原研究材料，不等同于 Anthropic 内部原始 Git repository；本项目目标是与其**可确认行为与运行语义**一致。

---

# 2. 当前 HEAD 与 B3 实际完成情况

## 2.1 当前 HEAD

```text
4a77f068649e18351e4c51d97e5a6667c9c4a5fd
test: 完成B3 Wave4/5核验与修复
```

其父提交 `e7a9021...` 已记录 W0–W3 主体开发；当前提交补齐 Wave 4/5 验证、测试可信度修复、sourcemap 链接修复、文档治理和安装器修复。

## 2.2 可确认测试结果

项目 B3 验证记录的最终本地复跑：

```text
10122 passed
10 skipped
4 warnings
345 subtests
```

同时确认：4 条 async unittest 假绿已修复；sourcemap 146 条 Markdown 相对链接已修复；docs governance、POSIX install smoke、`uv build` 均通过。

**但 GitHub API 对当前 HEAD 没有返回 combined status 或 commit workflow runs。** 因而这里只能定义为“项目记录的本地可复现验证”，不能说“当前 HEAD GitHub Actions 已绿”。

---

# 3. B3 行为圣经一致性核验

B3 v4.0 的 13 类 Source-Aligned 等价当前状态：

| 等价维度 | 当前判定 | 主要依据 / 缺口 |
|---|---|---|
| control-flow | PARTIAL | 9-step 有 trace；reference→Python 完整函数级 callgraph 未闭合 |
| state-transition | PARTIAL | terminal/transition 已有；resume/background/compact 仍缺全状态差分 |
| event ordering | STRONG PARTIAL | 9-step、双 tool path 已验证；cross-surface 仍不足 |
| permission precedence | NEAR COMPLETE | deny-first、headless fail-closed、classifier outage、hook allow 不越权已测 |
| tool scheduling/result order | NEAR COMPLETE | batched/streaming 双路径、ordered yield 已测 |
| context shaping order | PARTIAL | Compact-5 代码存在；trigger/no-op/token/durable-state 全向量差分未做 |
| retry/recovery/terminal | STRONG PARTIAL | bounded retry、terminal、fault injection 已有；全错误族未闭合 |
| persistence/resume/fork/rewind | BLOCKED | transcript 强；resume 真重入未完成 |
| trust lifecycle | NEAR COMPLETE | pre-trust 与 resume 不恢复 session trust 已测 |
| sandbox/isolation | BLOCKED | `NoSandboxBackend.provides_isolation=False` |
| subagent isolation/return | PARTIAL | agent/task/sidechain 存在；summary/background/resume/permission cascade 未闭环 |
| abort/interrupt propagation | STRONG PARTIAL | core abort 已测；process tree / cross-surface 仍缺 |
| surface-independent core | PARTIAL | 无第二 core 已证明；真实用户动作 runtime differential 不足 |

---

# 4. Reference-7 七核心组件

| ID | 组件 | 实现成熟度 | 严格 Closure | 主要结论 |
|---|---|---:|---|---|
| R7-01 | User | 86% | PARTIAL | 用户动作存在；缺独立 owner map 与跨 surface 行为矩阵 |
| R7-02 | Interfaces | 88% | PARTIAL | 汇入 shared core；cross-surface 主要还是结构证据 |
| R7-03 | Agent Loop | 93% | STRONG PARTIAL | reactive loop/9-step/retry/terminal 很强；完整 call-edge 未封口 |
| R7-04 | Permission System | 96% | NEAR COMPLETE | deny-first/mode/classifier/hooks/headless fail-closed 成熟 |
| R7-05 | Tools | 95% | NEAR COMPLETE | pool/orchestration/streaming/result contract 已专项验证 |
| R7-06 | State & Persistence | 82% | BLOCKED | transcript 强；resume 真重入、fork/rewind/sidechain 差分不足 |
| R7-07 | Execution Environment | 65% | BLOCKED | boundary/env/network/workspace 有；real sandbox/process lifecycle 缺 |

**7/7 都有实际落点，但按 v4.0 §18 当前不能写 7/7 complete。**

---

# 5. Reference-5 五层架构

| ID | Layer | 成熟度 | 严格 Closure | 关键问题 |
|---|---|---:|---|---|
| R5-01 | Surface | 86% | PARTIAL | 需要 runtime-equivalence，不是代码文本检查 |
| R5-02 | Core | 90% | PARTIAL | Agent Loop 强；Compact-5 差分不足 |
| R5-03 | Safety / Action | 91% | PARTIAL | Permission/Tools 强；Sandbox/Subagent lifecycle 拖累 |
| R5-04 | State | 82% | BLOCKED | resume/fork/rewind、context-9、sidechain 未闭合 |
| R5-05 | Backend | 68% | BLOCKED | NoSandbox、ProcessPolicy placeholder、MCP/remote lifecycle 证据不足 |

形式上 5/5 已建；严格上 5/5 都还没有满足全证据字段的 final closure。

---

# 6. CCR-14 横切机制

| CCR | 机制 | 成熟度 | 当前判定 | 下一步最小闭环 |
|---|---|---:|---|---|
| CCR-01 | Hook Runtime | 86% | PARTIAL | 27 events/Stop/timeout/error ordering 差分 |
| CCR-02 | Authorization Pipeline | 96% | NEAR COMPLETE | 补全 reference decision vector 与 callgraph |
| CCR-03 | Context Shaping | 78% | PARTIAL | Compact-5 trigger/order/no-op/persistence/token 差分 |
| CCR-04 | Context Assembly | 76% | PARTIAL | 9 sources 的 scope/placement/lazy/provenance |
| CCR-05 | Capability Assembly | 95% | NEAR COMPLETE | MCP/extensions lifecycle evidence |
| CCR-06 | Tool Orchestration | 94% | NEAR COMPLETE | sibling abort + mutation serial 全差分 |
| CCR-07 | Streaming Tool Execution | 90% | STRONG PARTIAL | fallback/duplicate-side-effect/interrupt 全路径 |
| CCR-08 | Recovery / Resilience | 92% | STRONG PARTIAL | max-output/prompt-too-long/fallback model 全错误族 |
| CCR-09 | Result Processing | 92% | STRONG PARTIAL | externalized payload resume reconstruction |
| CCR-10 | Session / Transcript | 82% | BLOCKED | resume/fork/rewind true lifecycle |
| CCR-11 | Subagent Orchestration | 78% | PARTIAL | summary/sidechain/background/bubble/worktree |
| CCR-12 | Isolation Runtime | 58% | BLOCKED | real sandbox + process lifecycle |
| CCR-13 | Trust Lifecycle | 95% | NEAR COMPLETE | managed policy/add-dir/MCP source scope 全向量 |
| CCR-14 | Runtime Config / Gates | 82% | PARTIAL | snapshot/precedence + Scheduler/Background/MCP gates |

成熟度高不等于 complete：Closure Matrix 需要 source files / symbols / call edges / runtime trace / invariants / tests 全字段齐备。

---

# 7. 核心代码问题

## 7.1 Real Sandbox：首要硬缺口

当前 `src/execution/sandbox.py` 默认仍是：

```text
NoSandboxBackend
provides_isolation = False
```

它在要求 isolation 时 fail-closed 是正确的，但允许 unsandboxed 时最终仍用普通 `subprocess.run()`。

Reference 2.1.88 的 `shouldUseSandbox.ts` 使用 `SandboxManager.isSandboxingEnabled()`；`sandbox-adapter.ts` 桥接 `@anthropic-ai/sandbox-runtime`，将 filesystem/network/managed settings/allowed+denied paths/domains 转换成实际 sandbox runtime config。

所以“有接口 + fail-closed”不等于“实现 Reference Sandbox”。

## 7.2 Resume：仍是重注册，不是继续推理

`resume_agent_background()` docstring 明确写：`The resume run does NOT actually drive a model call in this chunk.`

已完成 race-safe claim、transcript replay、fresh running state、pending prompt handoff；但没有把 reconstructed messages + prompt 接到 canonical `run_agent/query` 继续执行。

## 7.3 ProcessPolicy 仍是占位

真实 kill-tree/process-group 逻辑散布在 subprocess 层，没有形成 canonical ProcessPolicy。风险包括 orphan child、timeout/abort 不一致、surface interrupt 难以统一证明。

## 7.4 Compact-5：代码存在，但 Source-Aligned 证据不足

`CompressionPipeline.run()` 已按 Result Budget→Snip→Microcompact→Context Collapse→AutoCompact 排列，但还缺 reference feature gate/trigger、no-op、token accounting、boundary/durable transcript、cached microcompact、prompt-too-long/reactive compact 交互的逐项差分。

尤其 `mc_enabled=False` 的默认语义必须回到 recovered 2.1.88 源码逐 symbol 核验，不能只依赖论文或本地注释。

## 7.5 Context Assembly 9 来源没有统一合同

需要统一记录每个 source 的 scope、precedence、insertion point、lazy/eager、trust、provenance、compact behavior。

## 7.6 Subagent 生命周期未闭环

需要端到端证明 shared query loop、isolated context、tool/permission override、worktree/in-process、background、sidechain、summary-only、pending message、stop/resume/bubble。

## 7.7 MCP / Scheduler / Background：实现丰富、证据不足

- MCP：pre-trust→connect→discover→capability merge→permission→invoke→result→error/reconnect→shutdown；
- Scheduler：due→wake→queue→execute→persist→reschedule/cancel→shutdown；
- Background agent：spawn→progress→message→stop→terminal→auto-resume。

## 7.8 Cross-surface 证据强度不足

B3 证明了“没有第二 core”，但应升级为 deterministic runtime differential：同一 scripted model/input/settings/tool result，在各 surface 得到相同 permission/tool order/state/terminal，只允许 render envelope 不同。

## 7.9 Machine-readable parity control plane 落后

当前 `docs/parity/source-map/` 仍只有：

- `reference-component-map.yaml`
- `reference-package-map.yaml`
- `reference-symbol-map.yaml`

正式缺少 callgraph、unmapped symbols、state transition、runtime trace、divergence registry、scorecard/history。B3 的强验证还大量停留在测试与 Markdown 报告。

---

# 8. 与论文总体一致性

当前方向与论文高度一致：单一 shared reactive loop、model reasons/harness enforces、deny-first+defense-in-depth、context 为绑定资源、progressive Compact-5、tool pool+MCP/extensibility、append-oriented transcript、isolated subagent+sidechain、resume 不恢复 session trust。

真正差距集中在**端到端组合边界**：Sandbox、Resume、Context Assembly、Subagent lifecycle、cross-surface、machine evidence。

---

# 9. B4 基线冻结

从 `4a77f068649e18351e4c51d97e5a6667c9c4a5fd` 起，唯一首要目标继续是：

```text
7/7 Reference-7
5/5 Reference-5
14/14 CCR-14
+ 14 lifecycle obligations
全部达到 EXACT / SEMANTIC_EQUIVALENT / PYTHON_ADAPTATION_VERIFIED
```

在此之前，非必要产品功能、UI 美化、新 provider、新 workflow、benchmark、非核心重构全部 `DEFERRED`。
