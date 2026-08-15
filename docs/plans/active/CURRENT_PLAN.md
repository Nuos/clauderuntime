# CURRENT PLAN — B7 最后一次架构收口（Architecture Closure）

status: CURRENT
owner: repository-governance
created: 2026-08-15
last_verified: 2026-08-15
subject_commit: 16da0cfea98d69987739a319ff6ae42cfd432d2c
supersedes: seven-component-optimization-development-plan.md（已标 HISTORICAL）
superseded_by: none

> 文档编号：`CR-B7-FINAL-CLOSURE-PLAN-v2.0`
> 依据交付包：`docs/clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814/`
> 主执行指令：`docs/clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814/docs/34_CODEX_MASTER_EXECUTION_PROMPT.md`

## 1. 总目标

在 main 上以"每 Wave 独立提交"的方式完成 W0–W9，最终生成 Architecture Freeze
evidence。每个 Wave 独立提交/可回滚，禁止"大提交一次改完"。

## 2. Wave 总览

| Wave | 目标 | 类型 | 退出条件 | 状态 |
|---|---|---|---|---|
| W0 | Truth Reset / Evidence Rebase | P0 | CURRENT assets 全部绑定同一 subject SHA | DONE (486c55f) |
| W1 | Permission Safe-by-Default | P0 | implicit bypass=0 | DONE (9f3f097) |
| W2 | Canonical Turn Preparation | P0 | production prompt/context owner=1 | DONE (1557f2c) |
| W3 | Extension Trust Boundary | P0 | executable activation 必经 trust gate | DONE (ade48ca) |
| W4 | Task / Session / Persistence Owner | P0 | runtime task writable owner=1 | DONE (b7158f0) |
| W5 | Context / Compact Closure | P1 | outcome/ownership/retention contract 固定 | DONE (0ee21e3) |
| W6 | Query/Server Ownership Extraction | P1 | 不改状态机/协议，只减 owner density | DONE (fa9f4df) |
| W7 | CI / Platform / Evidence Truth | P0 | quarantine + matrix + artifact truth 完整 | DONE (21789fe) |
| W8 | Identity / Legacy Cleanup | P1 | README/package/legacy path 清晰 | DONE (416739a) |
| W9 | Freeze Gate / Baseline Lock | Release | 所有 Freeze Gate PASS | DONE (ARCHITECTURE_FREEZE) |
## 3. 硬约束（来自 34_CODEX_MASTER_EXECUTION_PROMPT）

1. 先读取当前 HEAD，若不是 package baseline（`16da0cf...`），先比较差异并更新
   evidence，不能盲目套 patch；
2. 每个 Wave 先 characterization tests，再最小改动；
3. 禁止重写 canonical query、permission classifier、五阶段 compact、MCP、
   TUI/Desktop、sandbox、scheduler watcher；
4. Permission 默认值修复不得机械填充 bypass；
5. Turn Preparation 目标是 owner=1，不是换一套 prompt 算法；
6. Extension 只统一 activation lifecycle，不统一 Plugin/MCP/Skill/Hook 内部机制；
7. Task 迁移允许 dual-read，禁止 dual-write；
8. 每个 Wave 提交输出：changed owner、unchanged semantics、tests、
   reference/accepted diff、rollback；
9. 不得把 repo-recorded tests 写成 newly reproduced evidence；
10. W9 前重新生成所有 CURRENT machine assets 绑定 final SHA。

## 4. Wave 详细目标（执行时逐项展开）

- **W0**：交付包入库；建立 `machine/` 真值目录；canonical truth graph
  （`docs/baseline/PROJECT_BASELINE.md`、`docs/status/current.md`、
  `docs/plans/active/CURRENT_PLAN.md`、`docs/governance/BEHAVIOR_BIBLE.md`、
  `docs/reference/reference-lock.yaml`、`docs/parity/scorecards/latest.yaml`、
  `docs/reference-differences/registry.yaml`）统一 subject_commit；治理脚本
  `check_truth_ssot` 校验。
- **W1**：`ToolContext.permission_context` 无默认值或 safe default；bypass 必须
  explicit + origin + reason；headless ask 无通道 → deny；差异登记。
- **W2**：`TurnPreparationService.prepare(request, session) -> PreparedTurn` 唯一
  owner；所有 surface 只调用此 owner；QueryEngine 降级为 facade。
- **W3**：`ExtensionDescriptor` + `ExtensionActivationGate`（ALLOW/DENY/
  REQUIRE_TRUST/INVALID/COLLISION）；project executable 默认过 workspace trust；
  name collision 确定性策略。
- **W4**：`RuntimeTaskRegistry` 单写 owner；legacy dict 只读 projection；禁双写；
  `SessionLifecycle`；resume 丢弃 ephemeral trust/security/runtime handles。
- **W5**：不改五阶段算法；`CompressionOutcome` 结构化结果；manual/auto 统一
  package ownership。
- **W6**：`ModelCapabilityResolver` 集中 capability 判定；`_AgentSession` 拆
  facades（RuntimeSession/SessionState/PermissionBridge/SurfaceEmitter/
  SchedulerBridge）。
- **W7**：`machine/ci-quarantine.yaml` 唯一清单；`generate_ci_deselect_args.py`
  生成 pytest deselect；CI yaml 不再手抄；Python 3.10/3.12/3.14 + macOS/Ubuntu/
  Windows 矩阵声明。
- **W8**：README/pyproject URLs 指向 `Nuos/clauderuntime`；`src/cli_backup`
  zero-ref 证明；旧 docs 标 HISTORICAL/SUPERSEDED。
- **W9**：Gate A–J 全 PASS；全部 CURRENT machine assets 重新绑定最终 SHA；
  ARCHITECTURE_FREEZE 记录。

## 5. 最终状态机

```text
FINAL_ARCH_CLOSURE_REQUIRED
  → P0_CLOSURE_COMPLETE
  → P1_CLOSURE_COMPLETE
  → ARCHITECTURE_FREEZE
  → MODULE_VERIFICATION
  → INTEGRATION_VERIFICATION
  → FAULT_INJECTION
  → LONG_HORIZON
  → RELEASE_CANDIDATE
```
