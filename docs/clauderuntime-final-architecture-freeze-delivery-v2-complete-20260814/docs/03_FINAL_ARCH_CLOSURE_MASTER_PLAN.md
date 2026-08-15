# 最后一次大改 Master Plan

> 文档编号：`CR-B7-FINAL-CLOSURE-PLAN-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 1. 总目标

在一个明确的 architecture-closure branch 上完成 W0–W9，最终生成 Freeze evidence。每个 Wave 有独立 PR/rollback point，禁止“大 PR 一次改完”。

## 2. Wave 总览

| Wave | 目标 | 类型 | 退出条件 |
|---|---|---|---|
| W0 | Truth Reset / Evidence Rebase | P0 | CURRENT assets 全部绑定同一 subject SHA |
| W1 | Permission Safe-by-Default | P0 | implicit bypass=0 |
| W2 | Canonical Turn Preparation | P0 | production prompt/context owner=1 |
| W3 | Extension Trust Boundary | P0 | executable activation 必经 trust gate |
| W4 | Task / Session / Persistence Owner | P0 | runtime task writable owner=1 |
| W5 | Context / Compact Closure | P1 | outcome/ownership/retention contract 固定 |
| W6 | Query/Server Ownership Extraction | P1 | 不改状态机/协议，只减 owner density |
| W7 | CI / Platform / Evidence Truth | P0 | quarantine + matrix + artifact truth 完整 |
| W8 | Identity / Legacy Cleanup | P1 | README/package/legacy path 清晰 |
| W9 | Freeze Gate / Baseline Lock | Release | 所有 Freeze Gate PASS |

## 3. W0 — Truth Reset

产物：

- `docs/baseline/PROJECT_BASELINE.md`；
- `docs/status/current.md`；
- `docs/plans/active/CURRENT_PLAN.md`；
- `docs/governance/BEHAVIOR_BIBLE.md`；
- `docs/reference/reference-lock.yaml`；
- `docs/parity/scorecards/latest.yaml`；
- `docs/reference-differences/registry.yaml`。

规则：禁止任何 CURRENT 文档引用 archive 作为事实源；backlog 若声明 GitHub Issues 为 SoT，则 Issues 必须真实存在，否则改为 repo-managed backlog。

## 4. W1 — Permission

- 删除/禁止 `ToolContext` 隐式 `bypassPermissions`；
- 增加 bypass origin/reason；
- 生产入口全部显式构造 `ToolPermissionContext`；
- 增加 constructor/entrypoint contract tests；
- 将 deliberate UX divergences 写入 difference registry；
- 确认 headless ask-without-channel → deny。

## 5. W2 — Turn Preparation

新增唯一 owner：

```python
TurnPreparationService.prepare(request, session) -> PreparedTurn
```

`PreparedTurn` 至少包含：

- full system prompt / blocks；
- conversation messages；
- visible tools；
- MCP/Skill contextual contributions；
- output style；
- provider/model capability snapshot；
- compaction/prompt-cache config；
- `QueryParams` / equivalent canonical inputs。

所有 surfaces 只能调用此 owner；`QueryEngine` 降级为 wrapper/test facade。

## 6. W3 — Extension Trust

增加 `ExtensionDescriptor` + `ExtensionActivationGate`。至少区分：bundled / managed / user / project / mcp。Project scope executable extension 默认必须经过 workspace trust 或明确策略。

Name collision 不得 silent overwrite；必须 deterministic reject/replace policy + provenance。

## 7. W4 — Task / Session / Persistence

- RuntimeTaskRegistry 作为 runtime tasks 单写 owner；
- legacy dict 只做 read-only projection；
- background Bash/Agent 迁移完成后禁止双写；
- SessionLifecycle 负责 start/resume/fork/rewind/end；
- persistence adapters 只持久化 durable state；
- resume 强制丢弃 ephemeral trust/security/runtime handles。

## 8. W5 — Context / Compact

不改五阶段算法，只固定：

```text
applyToolResultBudget
→ snipCompactIfNeeded
→ microcompact
→ contextCollapse.applyCollapsesIfNeeded
→ autocompact
```

增加结构化 `CompressionOutcome`，区分：changed / warning / hard_limit / persisted_artifacts / token_delta。Manual compact 移到同一 package ownership 下。

## 9. W6 — Query / AgentServer

Query：只抽 model capability、completion evaluation 等外围 owner，不改主状态机。

AgentServer：保留 WebSocket async + query worker thread + permission roundtrip 机制，仅将 `_AgentSession` 的职责拆成 facades：`RuntimeSession / SessionState / PermissionBridge / SurfaceEmitter / SchedulerBridge`。

## 10. W7 — CI / Platform

- machine quarantine；
- generated deselect args；
- Python 3.10 / 3.12 / 3.14 smoke；
- macOS / Ubuntu / Windows smoke；
- sandbox isolation 真机 job 单独记录；
- evidence artifact 携带 commit SHA 与 environment；
- local / CI / platform evidence 永远分栏。

## 11. W8 — Identity / Legacy

- README current pointers 更新；
- pyproject URLs 指向 `Nuos/clauderuntime`；
- distribution/CLI rename 若破坏兼容则采用 alias + deprecation；
- `src/cli_backup` 先完成 import/callgraph zero-ref 证明，再移除或移到 archive/non-package；
- 旧 docs 全部带 `HISTORICAL / SUPERSEDED` 标签。

## 12. W9 — Freeze

最终 SHA 必须重新生成：baseline、current status、scorecard、registry validation、quarantine report、test evidence、platform evidence、freeze record。任何资产仍引用旧 SHA → Freeze FAIL。
