# 最终全局架构诊断

> 文档编号：`CR-DIAGNOSTIC-FINAL-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 总结

ClaudeRuntime 当前的主要问题已经从“缺功能”切换成“同一语义存在多个 owner、默认值过于特权、旧/新状态并存、文档证据没有绑定同一 HEAD”。因此最后一次大改应做 **authority convergence**，而不是 capability expansion。

## P0-1：Repository Truth / Evidence SSOT

CURRENT 状态、scorecard、difference registry、backlog、active plan、README 指向不同 generation。后续调试若不先收口，将持续出现“失败对应哪个版本”的争议。

必须形成一个 canonical truth graph：

```text
reference-lock.yaml
        ↓
PROJECT_BASELINE.md
        ↓
status/current.md ─── active/CURRENT_PLAN.md
        ↓                    ↓
registry.yaml ───────── scorecards/latest.yaml
        ↓
release/freeze evidence
```

所有 CURRENT 机器资产必须有 `subject_commit`，且生成时拒绝 stale HEAD。

## P0-2：Permission Safe Default

当前 `ToolContext.permission_context` 默认 `bypassPermissions`。生产 headless 路径通常会显式覆盖，因此这里不应误写成“现有 headless 漏洞”；真正风险是 **任何遗漏 permission_context 的新调用点都会静默得到高权限**。

最终规则：

```text
No permission context supplied → construction error OR safe default
Explicit bypass → requires origin + reason + test
Headless ask with no interaction channel → deny
DENY > ASK > ALLOW
```

## P0-3：Turn Preparation 双 owner

项目目前只有一个 authoritative query loop，但至少有两套完整的 system/context assembly：

- `QueryEngine._build_system_prompt_parts()`；
- `agent_loop_compat.build_effective_system_prompt()`。

这不是“两套 agent loop”，而是“两套 Turn Preparation owner”。它曾经导致过 headless/TUI cutover prompt 缺失型回归。最后一次大改必须统一成一个 `TurnPreparationService` / `RuntimeTurnBuilder`。

## P0-4：Extension Trust-before-Activation

Plugin loader 已经有 trust taxonomy，但 loader 注册阶段并不等于 trust 决策阶段，且按 name 注册存在覆盖语义。Skills/Hooks/MCP 也各有不同加载路径。

必须统一生命周期，而不是统一机制：

```text
Discovery
 → Descriptor
 → Source provenance
 → Trust resolution
 → Validation
 → Activation decision
 → Capability registration
 → Runtime permission
```

内部 Plugin/MCP/Skill/Hook 机制保持独立。

## P0-5：Task / Session / Persistence Owner

`RuntimeTaskRegistry` 已引入，但 legacy task mirrors、background Bash/Agent compatibility paths 仍可能同时存在。Freeze 前必须规定：**一个可写 owner，其他均为 projection/adapter**。

Session persistence 还需明确“可持久化数据”和“不得恢复 live capability”的边界：API key、临时 permission、trust decision、open MCP client、OS handle、线程对象不得进入 resume 语义。

## P0-6：CI / Test Truth

当前 CI workflow 实际 deselect 5 个测试，历史文档曾写 4 个。必须建立 `machine/ci-quarantine.yaml` 作为唯一清单，由脚本生成 pytest deselect 参数；CI yaml 不再手抄列表。

此外，支持 Python 3.10–3.14 / macOS/Linux/Windows 的 metadata 与实际验证矩阵不一致，应拆成：

- declared compatibility；
- CI smoke；
- full suite；
- real platform isolation evidence。

## P1：建议本轮完成但禁止改语义

1. Query：抽出 model capability resolver / completion verifier adapter，但不重写 state machine；
2. AgentServer：拆 ownership facade，不改 WebSocket + worker-thread 协议；
3. Compact：把 manual compact 与 automatic pipeline 放到统一 package ownership；
4. Context：PostSampling `additional_contexts` 要么正式接线，要么登记 accepted diff；
5. State：统一 SessionLifecycle；
6. Project identity：README、pyproject distribution/URLs、历史 `clawcodex` 名称要有迁移策略；
7. `src/cli_backup`：先证明 production refs=0，再移出 package。

## 测试而非重构的模块

Execution/Sandbox、Tools、MCP、Subagent、TUI/Desktop、Provider adapters、Worktree、Scheduler、Memory 现在优先做 contract/fault/platform/long-horizon tests，不再做架构重写。
