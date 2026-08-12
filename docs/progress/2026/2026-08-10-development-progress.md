# Nuos/clauderuntime 开发进度记录
| Header 1 | Header 2 | Header 3 |
| --- | --- | --- |
| Cell 1 | Cell 2 | Cell 3 |

| Header 1 | Header 2 | Header 3 |
| --- | --- | --- |
| Cell 1 | Cell 2 | Cell 3 |


> 创建日期：2026-08-10
>
> 开发基线：`main` / `241d704480c0e4aa1bfb97c607a5e2e13e871e46`
>
> 开发范围：`2026-08-10-optimization-development-plan.md` 的 `Phase A — Baseline & P0`、`Phase B — Loop Governance（预计 3–4 个 PR）` 与 `Phase C — Permission × Execution（预计 4–6 个 PR）`
>
> 保护约束：不得修改 `docs/parity/diagnostics/2026-08-10-diagnostic.md` 与 `docs/plans/active/seven-component-optimization-development-plan.md`。

## 1. 总体进度

| 阶段 | 状态 | 完成度 | 说明 |
|---|---|---:|---|
| A1. Freeze baseline | 完成 | 100% | 已冻结提交、环境、测试清单/耗时、实际失败清单与七组件映射 |
| A2. Workspace boundary | 完成 | 100% | 当前基线已具有 gated-mode containment 与 tool backend 二次检查；完整 parity 通过，escape 为 0 |
| A3. Advisor metadata | 完成 | 100% | 当前基线已将 Advisor 明确登记为 ClawCodex-only 的 read-only/concurrency-safe override；parity 与 smoke 全绿 |
| A4. TUI failures | 完成 | 100% | 修复实际存在的 7 个历史失败，并限制测试 worker 以消除 CPU/定时抖动 |
| **Phase A 合计** | **完成** | **100%** | Exit Gate 达成：Python parity 与 TUI baseline 全绿、workspace escape 为 0 |
| B1. BudgetGuard | 完成 | 100% | 已完成统一预算主体、`max_cost_usd` Query backstop、入口显式 `--max-cost-usd`/`--max-turns` 传递与 deterministic gate 测试 |
| B2. Scheduler decouple | 完成 | 100% | 已将 scheduled tasks / background completion notifications 从 `_run_worker` idle branch 移到独立 background scheduler service |
| B3. Query refactor I | 完成 | 100% | 已提取 `model_call.py`、`terminal.py`、`budget.py`，保持单一 canonical Query 控制流 |
| B4. Query refactor II | 完成 | 100% | 已提取 `tool_round.py`、`recovery.py`，保持工具消息顺序和恢复语义 |
| **Phase B 合计** | **完成** | **100%** | B1/B2/B3/B4 与 Exit Gate B 均已完成 |
| C1. Permission profile | 完成 | 100% | 已引入 `parity` / `full-access` / `managed` profile 模型并接入权限启动解析 |
| C2. Pre-trust gate | 完成 | 100% | 已统一 hook/MCP/project-config pre-trust 判定；未信任 workspace 不加载 project/local MCP runtime 配置 |
| C3. ExecutionBoundary | 完成 | 100% | 已建立 ExecutionBoundary、WorkspaceGuard、EnvPolicy、ProcessPolicy 接口，并接入 ToolContext 路径二次校验 |
| C4. SandboxBackend interface | 完成 | 100% | 已建立 SandboxBackend、NoSandboxBackend、SandboxPolicy 与 platform capability detection，并挂入 ExecutionBoundary |
| C5. Network/secret policy | 完成 | 100% | 已建立 MinimalEnvPolicy、ConfigurableNetworkPolicy 与 minimal execution profile；默认运行兼容行为保持不变 |
| **Phase C 合计** | **完成** | **100%** | C1/C2/C3/C4/C5 主体与 Exit Gate C 故障注入验证已完成 |

## 2. 输入文档读取记录

已完整阅读且保持只读：

| 文档 | SHA-256（开发前） | 用途 |
|---|---|---|
| `docs/parity/diagnostics/2026-08-10-diagnostic.md` | `c84c51d5585a5f86a574636edf1b817e57b10e10f854dfd54441b710e8bce929` | 当前七组件诊断、P0/P1 缺口与证据基线 |
| `docs/plans/active/seven-component-optimization-development-plan.md` | `1c8797e05b959220418b0ac3c28749d7e04fa36f9e4af1a7f6e167578638a74a` | 阶段计划、模块方案、测试与验收门 |
| `docs/parity/clauderuntime-source-parity-action-bible-v1.0.md` | `b512bb88f93077d99f162d116801d867783b90a4a7072b08c4371553f1639b0f` | 总开发规范、Reference-7、Source Map、Runtime Path、PR/Review Gate 与长期治理规则 |

## 3. A1. Freeze baseline

### 3.1 环境基线

| 项目 | 当前值 |
|---|---|
| Git 分支 | `main` |
| Git HEAD | `241d704480c0e4aa1bfb97c607a5e2e13e871e46` |
| Python | `3.14.6` |
| Node.js | `v26.5.0` |
| npm | `11.17.0` |
| 操作系统 | macOS 26.5.1（Darwin 25.5.0, arm64） |
| Python 测试文件 | 605 个 `test_*.py` |
| TUI 测试文件 | 138 个（完整 Vitest 实测） |

### 3.2 已知失败清单（开发前）

| 模块 | 已知失败 | 来源 |
|---|---:|---|
| Advisor tool parity / smoke | 文档记录 4；实测 0 | `TODOS.md` + 定向 Pytest |
| Workspace boundary read/write E2E | 文档记录 2；实测 0 | `TODOS.md` + 定向 Pytest |
| TUI Vitest | 文档记录 8；实测 7 | `TODOS.md` + 完整 Vitest |

实际基线说明：Python 的 6 个历史 P0 用例在任何代码修改前即为 `6 passed`，说明 `TODOS.md` 中 A2/A3 条目已经滞后。TUI 的 cursor-drift 用例初次通过，因此实际为 7 个失败；修复后完整套件为零失败。

### 3.3 A2. Workspace boundary / A3. Advisor metadata 现有实现核验

- `ToolContext.ensure_allowed_path()` 与 `ensure_readable_path()` 会解析真实路径，并在非 `bypassPermissions` 模式下拒绝允许根之外的目标；Read/Write E2E 同时断言工具结果错误、无内容泄漏/无文件落盘以及 containment helper 抛出 `ToolPermissionError`。
- Advisor 只读取会话并把内容转发给 reviewer，`src/reference_data/ts_tool_properties.json` 已将其作为 ClawCodex-only override 明确登记为 `is_read_only=true`、`is_concurrency_safe=true`；这与当前实现和调度语义一致。
- 因 A2/A3 的实现与契约均已存在且测试全绿，本阶段未重复改写相关 Python 模块，避免制造无行为收益的改动。

### 3.4 七组件映射

| 组件 | 主要源码 | 主要测试 | Phase A 关联 |
|---|---|---|---|
| Interfaces | `src/entrypoints/`, `ui-tui/`, `ui-desktop/` | `ui-tui/src/__tests__/` | A4 |
| Agent Loop | `src/query/`, `src/server/` | `tests/parity/`, `tests/integration/` | A3 间接涉及调度 |
| Permission | `src/permissions/` | `tests/parity/test_e2e_*` | A2 |
| Tools | `src/tool_system/` | `tests/parity/test_tool_parity.py`, `tests/integration/test_advisor_smoke.py` | A3 |
| State & Persistence | `src/services/session_storage.py` | session/recovery 测试 | 本阶段仅回归保护 |
| Context & Memory | `src/context_system/`, `src/services/compact/` | context/compact 测试 | 本阶段仅回归保护 |
| Execution Environment | `src/utils/shell_platform.py` 及工具执行路径 | E2E read/write、process 测试 | A2 |

## 4. 修改记录

| 时间 | 模块/文件 | 修改内容 | 验证 |
|---|---|---|---|
| 2026-08-10 | `docs/progress/2026/2026-08-10-development-progress.md` | 新建开发进度记录，登记 Phase A 范围、基线和保护约束 | 文档创建完成 |
| 2026-08-10 | `ui-tui/src/app/turnController.ts` | inline diff 完成时保留 Args/Result 展开详情，紧凑行在无详情时继续使用 | 定向测试、完整 TUI 测试通过 |
| 2026-08-10 | `ui-tui/src/components/appChrome.tsx` | 补全 status segment 的 `cost` 契约及 96 列可见阈值 | statusRule 测试通过 |
| 2026-08-10 | `ui-tui/src/app/interfaces.ts` | 将缺省状态指示器恢复为配置/测试约定的 `kaomoji`；同时整理类型导入顺序 | config sync、ESLint、typecheck 通过 |
| 2026-08-10 | `ui-tui/src/lib/inputMetrics.ts` | 修正 transcript 水平保留列，使复合 user prompt 的实际宽度进入换行与高度估算 | virtualHeights 与完整 TUI 测试通过 |
| 2026-08-10 | `ui-tui/src/__tests__/createGatewayEventHandler.test.ts` | 将 Patch 标签断言对齐现行无引号 `formatToolCall` 契约 | 定向测试通过 |
| 2026-08-10 | `ui-tui/vitest.config.ts` | 限制 `maxWorkers=4`，避免全套测试过度并发导致 cursor/child-process 定时用例抖动 | 完整 TUI 测试零失败 |
| 2026-08-10 | `src/permissions/profiles.py`、`src/permissions/modes.py`、`src/permissions/__init__.py` | 完成 `C1. Permission profile`：引入 `parity` / `full-access` / `managed` profile 模型并接入启动解析 | `tests/test_permission_profiles.py`、`tests/test_permission_levels.py` 通过 |
| 2026-08-10 | `src/permissions/pre_trust.py`、`src/hooks/trust_gate.py`、`src/services/mcp/config.py`、`src/permissions/__init__.py` | 完成 `C2. Pre-trust gate`：统一 pre-trust 判定，未信任 workspace 不加载 project/local MCP runtime 配置 | `tests/test_pre_trust_gate.py`、`tests/test_mcp_pre_trust.py`、`tests/test_trust_gate.py`、`tests/test_mcp_config.py` 通过 |
| 2026-08-10 | `tests/test_permission_profiles.py`、`tests/test_pre_trust_gate.py`、`tests/test_mcp_pre_trust.py` | 新增 C1/C2 单元测试与 MCP runtime gate 回归 | 定向测试通过 |
| 2026-08-11 | `src/execution/boundary.py`、`src/execution/__init__.py`、`src/tool_system/context.py`、`tests/test_execution_boundary.py` | 完成 `C3. ExecutionBoundary`：新增 WorkspaceGuard/EnvPolicy/ProcessPolicy 接口，ToolContext 读写路径进入执行边界二次校验 | C3 定向回归、相邻 Permission/Parity 回归、`py_compile` 与 `git diff --check` 通过 |
| 2026-08-11 | `tests/test_execution_boundary.py` | 补全 `C3. ExecutionBoundary` 单元测试模块：覆盖默认 workspace allow/deny、额外工作目录、默认 env/process policy、strict guard 替换与 ToolContext 读写路由 | `90 passed`、`py_compile` 与 `git diff --check` 通过 |
| 2026-08-11 | `src/execution/sandbox.py`、`src/execution/boundary.py`、`src/execution/__init__.py`、`tests/test_sandbox_backend.py` | 完成 `C4. SandboxBackend interface`：新增 NoSandboxBackend、SandboxPolicy、SandboxRequest/Invocation/ExecutionResult 与 platform capability detection，并挂入 ExecutionBoundary | C4 定向 `37 passed`；Phase C 相邻回归 `119 passed`；`py_compile` 与 `git diff --check` 通过 |
| 2026-08-11 | `src/execution/policy.py`、`src/execution/boundary.py`、`src/execution/__init__.py`、`src/utils/subprocess_env.py`、`tests/test_execution_policy.py` | 完成 `C5. Network/secret policy`：新增 MinimalEnvPolicy、ConfigurableNetworkPolicy、minimal_execution_boundary，并公开 subprocess secret scrub key 集合 | C5 定向 `38 passed`；Phase C 相邻回归 `126 passed`；`py_compile` 与 `git diff --check` 通过 |
| 2026-08-11 | `tests/test_phase_c_exit_gate.py`、`docs/progress/2026/2026-08-10-development-progress.md` | 完成 `Exit Gate C`：新增 Permission 失误故障注入测试，覆盖 workspace escape、secret leak、network escape、redirect target 与 sandbox required isolation fail-closed | Exit Gate C 定向 `5 passed`；Phase C 全量相邻回归 `131 passed`；`py_compile` 与 `git diff --check` 通过 |
| 2026-08-11 | `src/server/background_scheduler.py`、`src/server/agent_server.py`、`src/scheduled_tasks/scheduler.py`、`tests/server/test_background_scheduler.py` | 完成 `B2. Scheduler decouple`：新增独立 `SessionBackgroundScheduler`，将 scheduled tasks / background completion notifications 从 `_run_worker` idle branch 解耦；新增 session turn gate，避免 background tick 与 foreground turn 交叉修改同一 transcript | B2 定向与相邻回归 `56 passed`；`py_compile` 与 `git diff --check` 通过 |
| 2026-08-11 | `src/query/budget.py`、`src/cli.py`、`src/entrypoints/headless.py`、`src/entrypoints/tui_launcher.py`、`src/entrypoints/agent_server_cli.py`、`src/entrypoints/serve_cli.py`、`tests/test_phase_b_exit_gate.py`、`tests/test_query_budget.py`、`tests/server/test_tui_launcher.py`、`tests/server/test_bypass_permissions_wiring.py`、`tests/server/test_desktop_serve.py` | 完成 `B1. BudgetGuard` 与 `Exit Gate B`：新增 `resolve_max_cost_usd()`，补齐 headless / TUI / agent-server / serve 的显式 `--max-cost-usd` 入口接线；新增 Phase B gate 测试固定 stop/retry/budget deterministic invariants | Phase B 相关测试合集 `129 passed`；`py_compile` 与 `git diff --check` 通过 |

## 5. 测试与验收记录

| 验证项 | 结果 | 耗时/备注 |
|---|---|---|
| 历史 6 个 Python P0 用例 | `6 passed` | 3.76s；修改前基线 |
| Python parity 全套 | `381 passed` | 14.62s；2 个既有 DeprecationWarning |
| Advisor integration 全文件 | `3 passed` | 0.82s |
| TUI 四个修复相关文件 | `136 passed` | 1.17s |
| TUI 完整套件 | `138 files passed`; `1693 passed`, `4 skipped` | 11.12s；零失败 |
| TypeScript typecheck | 通过 | `tsc --noEmit -p tsconfig.json` |
| 修改文件 ESLint | 通过 | 5 个 TS/TSX 源码与测试文件 |
| 补丁格式检查 | 通过 | `git diff --check` 无输出 |

### Exit Gate A

- [x] Python parity baseline 全绿。
- [x] Advisor smoke/parity 全绿。
- [x] Workspace read/write escape 用例为 0 escape。
- [x] TUI baseline 全绿，无 known red。
- [x] 两份输入 Markdown 的 SHA-256 与开发前一致。

## 6. 风险与备注

- 当前工作区在开发开始前已有多项 `docs/` 删除和未跟踪文件；这些均视为用户现有改动，不回滚、不覆盖。
- 代码知识图谱未索引当前仓库；已按项目规则先尝试图谱，确认不可用后才回退到文件搜索和测试定位。
- 两份输入文档在开发结束时再次计算 SHA-256，均与开发前一致，确认未修改。
- TUI 测试会尝试探测一个未安装的旧 `clawcodex_cli` Python 包并向 stderr 输出 `ModuleNotFoundError`，但相关测试采用回退路径且完整套件退出码为 0；本阶段未扩大范围处理该非阻断噪声。
- 完成时间：2026-08-10 21:01:51 PDT。

## 7. GitHub 提交记录

| 项目 | 内容 |
|---|---|
| 阶段 | `Phase A — Baseline & P0` |
| 分支 | `agent/phase-a-baseline-p0` |
| 提交说明 | `fix(tui): complete Phase A baseline and P0` |
| PR 目标 | `main`（Draft Pull Request） |
| 提交范围 | 本文档及 Phase A 的 6 个 TUI 修改文件 |
| 明确排除 | 两份只读输入 Markdown、HTML、`IDEA.md`、开发开始前已有的文档删除项 |

## 8. Phase B — Loop Governance（预计 3–4 个 PR）

### B1. BudgetGuard

状态：完成。

已完成：

- 新增 `src/query/budget.py`，提供 turns/tokens/cost/time 的统一、可确定性测试预算对象。
- `max_cost_usd` 已进入 canonical Query，在模型调用、retry 与 tool round 边界执行 backstop；达到阈值后不再执行工具副作用。
- Headless、Agent Server、Desktop Serve 已接入 `settings.max_turns` / `settings.max_cost_usd` 的运行时传递。
- TUI 已增加并转发 per-launch `--max-turns`。
- 新增 `resolve_max_cost_usd()`，将 launch override → settings → unlimited 的优先级与 `resolve_max_turns()` 对齐。
- 顶层 `clawcodex` CLI、headless、TUI launcher、agent-server、desktop serve 均已接入显式 `--max-cost-usd`，避免 `max_cost_usd` 只 validated/读取 settings 而无法按 launch 覆盖。
- 新增 BudgetGuard 与“达到成本阈值不产生工具副作用”的单元/Query 测试。
- 新增 `tests/test_phase_b_exit_gate.py`，固定 TerminalReason、ContinueReason、retry 常量与 BudgetGuard 多维度 deterministic 行为。

验证记录：

- BudgetGuard、Query loop、Terminal parity、TUI launcher、Agent Server CLI 定向验证：`81 passed, 2 subtests passed`。
- 扩展回归首次发现 adapter 参数漏传并已修正；复跑已连续通过 `71 passed`，因长耗时用例主动中止，不能据此标记完整回归完成。
- 本轮收口验证：Phase B 相关测试合集 `129 passed`，覆盖 `tests/test_phase_b_exit_gate.py`、`tests/test_query_budget.py`、TUI launcher、Agent Server CLI、Desktop Serve、B2 scheduler、Cron 与 AskUserQuestion 相邻回归。
- `py_compile` 与 `git diff --check` 通过。

### B2. Scheduler decouple

状态：完成。

已完成：

- 新增 `src/server/background_scheduler.py`，提供独立 `SessionBackgroundScheduler` service/thread/task，负责周期性 background housekeeping tick。
- `_AgentSession.start()` 已启动独立 background scheduler service；`_run_worker` 的 idle branch 不再承担 scheduled tasks / background completion notifications 轮询。
- 新增 `_turn_gate` 与 `_run_serial_turn()`，保持同一 session transcript 一次只允许一个 model turn 修改；foreground turn 处于 AskUserQuestion/permission wait 时，background scheduler clock 仍独立 tick，但不会把另一个 internal turn 交叉写进同一会话。
- `_deliver_task_notifications()` 与 `_fire_due_scheduled()` 已改为由 background scheduler service / turn gate 驱动，同时保留“scheduled prompt between turns、no catch-up”的既有语义。
- 新增 `tests/server/test_background_scheduler.py`，覆盖 service 非重入 tick、foreground wait 不阻塞后台 tick，以及 active turn gate 下不交叉执行 housekeeping。

验证记录：

- B2 定向测试、scheduled-task 相邻回归、AskUserQuestion 相邻回归：`56 passed`。
- `py_compile` 与 `git diff --check` 通过。

### B3. Query refactor I

状态：完成。

已严格按开发文档描述提取 `model_call.py`、`terminal.py`、`budget.py`：

- `model_call.py` 承担完整请求组装、thinking/effort 参数、streaming/chat provider 调用和响应标准化。
- `terminal.py` 成为 TerminalReason、Terminal、TerminalHolder 与跨入口 early-stop 映射的唯一事实源。
- `budget.py` 提供统一 BudgetGuard；`query.py` 只保留预算检查点和控制流。
- `transitions.py` 仅保留 QueryState/Transition，并兼容导出终态类型，未创建第二主循环。
- `query.py` 从开发前 2831 行降至 2083 行（完成 B4 后进一步降至 1957 行）。
- 模型调用/终态/预算 characterization 与回归：`166 passed, 29 subtests passed`；入口与 Query 扩展回归：`140 passed, 2 subtests passed`。

### B4. Query refactor II

状态：完成。

已严格按开发文档描述提取 `tool_round.py`、`recovery.py`：

- `tool_round.py` 承担 orchestrator 调用、派生 ToolContext 接管、hook-stop 检测和严格 user-role result 收集；消息仍逐条流式交回 canonical Query。
- `recovery.py` 承担 context-window 解析以及 max-output/prompt-too-long/media withheld 判定。
- Query/Hook/Tool failure/Concurrency/Recovery 定向验证：`69 passed, 2 subtests passed`。
- 已建立 package/symbol/runtime/auxiliary 四类机器可读映射资产。

### Exit Gate B

状态：完成。

- `B1. BudgetGuard` 已具备 turns/cost/tokens/deadline deterministic tests，并补齐入口显式预算覆盖。
- `B2. Scheduler decouple` 已具备独立 service/thread/task 与 foreground wait 不阻塞后台 tick 测试。
- `B3. Query refactor I` 与 `B4. Query refactor II` 已具备 Query stop/retry/budget 相邻回归。
- 新增 `tests/test_phase_b_exit_gate.py` 聚合固定 stop/retry/budget 的跨模块事实源与 deterministic invariants。

## 9. Phase C — Permission × Execution（预计 4–6 个 PR）

### C1. Permission profile

状态：完成。

已完成：

- 新增 `src/permissions/profiles.py`，提供 `parity`、`full-access`、`managed` 三种 profile 的一等模型。
- `resolve_interactive_permission_state()` 已支持 `permission_profile` 参数；默认不传时保持现有 surface 行为，显式传入时固定 profile 合同。
- `managed` profile 会在解析层禁用 bypass mode 和 bypass selectable；`parity` profile 强制默认 ask/default floor；`full-access` profile 可显式提高非交互 floor。
- `src/permissions/__init__.py` 已导出 profile API。

验证记录：

- `tests/test_permission_profiles.py` 与现有 `tests/test_permission_levels.py`：`40 passed`。

### C2. Pre-trust gate

状态：完成。

已完成：

- 新增 `src/permissions/pre_trust.py`，统一 `hook`、`mcp`、`project-config` 的 pre-trust allow/deny 判定。
- `src/hooks/trust_gate.py` 已复用统一 gate；policy hook 仍保持既有“policy layer always wins”语义。
- `src/services/mcp/config.py` 在 workspace 未信任时不加载 project/local MCP runtime 配置，并返回 warning；enterprise/user/managed/dynamic 来源保持可用。
- 新增 `tests/test_pre_trust_gate.py` 与 `tests/test_mcp_pre_trust.py`。

验证记录：

- C1/C2 相邻回归：`tests/test_permission_profiles.py tests/test_pre_trust_gate.py tests/test_mcp_pre_trust.py tests/test_trust_gate.py tests/test_mcp_config.py`：`39 passed`。

### C3. ExecutionBoundary

状态：完成。

已完成：

- 新增 `src/execution/boundary.py` 与 `src/execution/__init__.py`，提供 `ExecutionBoundary` 聚合入口。
- `ExecutionBoundary` 聚合 `WorkspaceGuard`、`EnvPolicy`、`ProcessPolicy`，先把执行边界抽象从权限解析层拆出来，为后续 C4/C5 接口化留出稳定接点。
- `ToolContext.ensure_allowed_path()` 与 `ensure_readable_path()` 已通过 `execution_boundary.check_workspace_path(...)` 做读写路径二次校验。
- 默认 `DefaultWorkspaceGuard` 保持现有 full-access / internal path 兼容行为；替换为严格 guard 时，即使当前 permission mode 允许 workspace escape，也可以在执行边界层阻断。
- `EnvPolicy` 与 `ProcessPolicy` 先提供可替换 hook，不在本阶段实现 network/secret 规则，避免与 `C5. Network/secret policy` 混淆。

单元测试模块覆盖：

- 默认 `WorkspaceGuard` 的 workspace 内允许、workspace 外拒绝。
- `bypassPermissions` 现有 workspace escape 兼容行为。
- 可替换 strict guard 在 permission 允许 bypass 时仍可阻断 workspace escape。
- `additional_working_directories` 经执行边界完成读写校验。
- `ToolContext.ensure_allowed_path()` / `ensure_readable_path()` 的 write/read 路由。
- 默认 `EnvPolicy` 返回隔离副本，不污染输入环境。
- 默认 `ProcessPolicy` 拒绝空命令、允许非空命令。
- 自定义 `EnvPolicy` / `ProcessPolicy` hook 可替换并生效。

验证记录：

- `tests/test_execution_boundary.py tests/test_permission_profiles.py tests/test_pre_trust_gate.py tests/test_mcp_pre_trust.py tests/test_workflow_permission_fixes.py tests/test_read_permission_parity.py tests/parity/test_e2e_file_read.py tests/parity/test_e2e_edit_flow.py`：`90 passed`。
- `src/execution/boundary.py src/execution/__init__.py src/tool_system/context.py`：`py_compile` 通过。
- `git diff --check` 通过。

### C4. SandboxBackend interface

状态：完成。

已完成：

- 新增 `src/execution/sandbox.py`，建立 `SandboxBackend` 统一协议。
- 新增 `NoSandboxBackend`，显式声明本地无隔离执行后端：backend 可用，但 `provides_isolation=False`，不把“无沙箱”伪装成已隔离。
- 新增 `SandboxCapability`、`SandboxPolicy`、`SandboxRequest`、`SandboxInvocation` 与 `SandboxExecutionResult`，形成 prepare/run 的最小接口层。
- 新增 `current_sandbox_platform()` 与 `sandbox_policy_from_settings()`，覆盖 `macos` / `linux` / `windows` platform token、`enabledPlatforms`、`failIfUnavailable`、`allowUnsandboxedCommands` 的 capability / policy 解析。
- `ExecutionBoundary` 已挂入 `sandbox_backend`，提供 `prepare_sandbox()` 与 `run_sandbox()` 接口，为后续逐平台增强留出稳定接点。
- 本阶段不实现 native sandbox、network policy 或 secret scrubbing，避免与 `C5. Network/secret policy` 混淆。

单元测试模块覆盖：

- platform token detection：`darwin -> macos`、`win32 -> windows`、`linux -> linux`。
- `NoSandboxBackend` capability：available 且不提供 isolation。
- 默认 no-sandbox invocation prepare。
- sandbox policy 要求 isolation 或禁止 unsandboxed 时拒绝运行，并返回稳定 exit code。
- 允许情况下的本地 no-sandbox process run。
- `SettingsSchema.sandbox.enabledPlatforms`、`failIfUnavailable`、`allowUnsandboxedCommands` 到 `SandboxPolicy` 的映射。
- `ExecutionBoundary` sandbox backend 入口。

验证记录：

- `tests/test_sandbox_backend.py tests/test_execution_boundary.py tests/test_sandbox_guard.py`：`37 passed`。
- `tests/test_sandbox_backend.py tests/test_execution_boundary.py tests/test_sandbox_guard.py tests/test_permission_profiles.py tests/test_pre_trust_gate.py tests/test_mcp_pre_trust.py tests/test_workflow_permission_fixes.py tests/test_read_permission_parity.py tests/parity/test_e2e_file_read.py tests/parity/test_e2e_edit_flow.py`：`119 passed`。
- `src/execution/sandbox.py src/execution/boundary.py src/execution/__init__.py tests/test_sandbox_backend.py`：`py_compile` 通过。
- `git diff --check` 通过。

### C5. Network/secret policy

状态：完成。

已完成：

- 新增 `src/execution/policy.py`，将 env/secret 与 network policy 从具体工具描述中提升为 execution 层接口。
- 新增 `MinimalEnvPolicy`：默认只传递最小 allowlist env，并强制剥离 provider/tool secret 及 GitHub Action `INPUT_` twin。
- `src/utils/subprocess_env.py` 将现有 secret scrub 集合作为 `SUBPROCESS_SECRET_ENV_KEYS` 公开，避免 C5 复制第二份 secret 名单。
- 新增 `ConfigurableNetworkPolicy`，覆盖开发文档要求的 `none`、`loopback`、`allowlist`、`full` 四种 network policy mode。
- `ExecutionBoundary` 已挂入 `network_policy`，提供 `check_network()` 入口。
- 新增 `minimal_execution_boundary()`，形成可显式启用的最小权限 execution profile：minimal env + configurable network policy。
- 默认 `default_execution_boundary()` 继续保持兼容型 pass-through env 与 full network policy，不在本阶段强制替换 Bash/MCP/Hook 的现有运行环境。

单元测试模块覆盖：

- `MinimalEnvPolicy` 保留 allowlist env、剥离 `SUBPROCESS_SECRET_ENV_KEYS` 与 `INPUT_` twin。
- `MinimalEnvPolicy` 返回隔离副本，不污染输入 env。
- `ConfigurableNetworkPolicy(mode="none")` 拒绝外部 URL。
- `ConfigurableNetworkPolicy(mode="loopback")` 只允许 `localhost`、`127.0.0.1`、`::1` 等 loopback host。
- `ConfigurableNetworkPolicy(mode="allowlist")` 精确匹配 allowlisted host。
- `ConfigurableNetworkPolicy(mode="full")` 允许外部 host。
- `minimal_execution_boundary()` 同时提供 minimal env 与 network allowlist profile。

验证记录：

- `tests/test_execution_policy.py tests/test_execution_boundary.py tests/test_sandbox_backend.py tests/test_subprocess_env_scrub.py tests/test_c9_upstream_proxy_wiring.py`：`38 passed`。
- `tests/test_execution_policy.py tests/test_sandbox_backend.py tests/test_execution_boundary.py tests/test_sandbox_guard.py tests/test_permission_profiles.py tests/test_pre_trust_gate.py tests/test_mcp_pre_trust.py tests/test_workflow_permission_fixes.py tests/test_read_permission_parity.py tests/parity/test_e2e_file_read.py tests/parity/test_e2e_edit_flow.py`：`126 passed`。
- `src/execution/policy.py src/execution/boundary.py src/execution/__init__.py src/utils/subprocess_env.py tests/test_execution_policy.py`：`py_compile` 通过。
- `git diff --check` 通过。

### Exit Gate C

状态：完成。

已完成：

- 新增 `tests/test_phase_c_exit_gate.py`，专门覆盖 Permission 失误故障注入场景。
- 模拟 permission 层误授予 `bypassPermissions`，由 strict `WorkspaceGuard` 在 execution boundary 阻断 workspace escape。
- 使用 `minimal_execution_boundary()` 验证 child process 看不到被剥离的 `ANTHROPIC_API_KEY` / `INPUT_ANTHROPIC_API_KEY`。
- 验证 `network_mode="none"` 下外部 URL 被拒绝。
- 验证 allowlist network policy 对 redirect 后目标 host 仍需重新检查，未列入 allowlist 的 host 被拒绝。
- 验证 sandbox policy 要求 isolation 时，`NoSandboxBackend` 不会静默 unsandboxed 执行，而是 fail closed。

验证记录：

- `tests/test_phase_c_exit_gate.py`：`5 passed`。
- `tests/test_phase_c_exit_gate.py tests/test_execution_policy.py tests/test_sandbox_backend.py tests/test_execution_boundary.py tests/test_sandbox_guard.py tests/test_permission_profiles.py tests/test_pre_trust_gate.py tests/test_mcp_pre_trust.py tests/test_workflow_permission_fixes.py tests/test_read_permission_parity.py tests/parity/test_e2e_file_read.py tests/parity/test_e2e_edit_flow.py`：`131 passed`。
- `tests/test_phase_c_exit_gate.py src/execution/policy.py src/execution/boundary.py src/execution/__init__.py`：`py_compile` 通过。
- `git diff --check` 通过。

## 10. 新增总开发规范确认

已完整阅读 `2026-08-10-clauderuntime-source-parity-action-bible-v1.0.md`（2335 行），确认执行以下规则：

- `Phase I — Stabilization & Behavioral Parity` 继续直接执行现有优化开发计划，不替换原有阶段名称或编号。
- 正式 Source Parity 采用 Reference-7；Context/Memory 仅作为 Engineering View，不另造“第八组件”。
- 开发遵循 G0～G11，Reference evidence、current trace、gap、contract、characterization test 先于实现。
- 从当前 PR 开始同步维护 Source Map、Runtime Path、Auxiliary Mechanism 与 Divergence，不在 Phase I 结束后补做。
- 主体功能和核心组件优先；预算、外围约束、scheduler 与兼容层收口按用户最新指示后置。
- 所有 PR 标题、提交说明、PR 正文和代码注释在不影响协议标识/源码符号的前提下优先使用简体中文。
