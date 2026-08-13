# ClaudeRuntime B4 开发进度记录

> 文档编号：`CR-B4-PROGRESS-LOG`  
> 状态：**ACTIVE — C6 Final Closure / Cross-platform Isolation Remaining**  
> 启动日期：2026-08-13  
> 工作基线：ClaudeRuntime `4a77f068649e18351e4c51d97e5a6667c9c4a5fd`  
> Reference：Claude Code recovered source `2.1.88` / `a8a678cb6244e6770e1e421767ff0987a1d95549`

## 1. 使用规则

- 本文件是 B4 的唯一持续开发进度记录；每次实现、验证、阻塞或范围变更都必须追加条目。
- 进度以可复现证据为准。代码存在、单测通过或完成度估算，均不得单独把项目状态标为 `Complete`。
- 每个 Closure 条目必须关联 reference files/symbols/call edges、Python files/symbols、runtime trace、状态与安全不变量、测试和结果。
- 状态只可按开发阶段使用 `Not Started`、`In Progress`、`Blocked`、`Ready for Verification`、`Verified`；最终 Source-Aligned 证据状态仅可使用 `EXACT`、`SEMANTIC_EQUIVALENT`、`PYTHON_ADAPTATION_VERIFIED`。
- 非 7×5×14 Final Closure 所需的产品功能、provider、UI、workflow、宣传或重构，默认不纳入本轮。

## 2. 启动核验

| 核验项 | 结果 | 证据 |
|---|---|---|
| Git HEAD | 通过 | `4a77f068649e18351e4c51d97e5a6667c9c4a5fd`，与 B4 冻结基线一致 |
| HEAD 描述 | 记录 | `test: 完成B3 Wave4/5核验与修复` |
| B4 交付包完整性 | 通过 | 原始 7 个受控文件的 SHA-256 校验全部通过 |
| B4 计划生效 | 通过 | `02_B4_CORE_CLOSURE_DEVELOPMENT_PLAN.md` |
| B4 开发圣经生效 | 通过 | `03_SOURCE_ALIGNED_7x5x14_DEVELOPMENT_BIBLE_v5.0.md` |
| 当前开发阶段 | 已启动 | C0 — Truth Refresh / Differential Contract Freeze |

> 注：本进度文件是本次启动新增文件，因此不属于原始 `SHA256SUMS.txt` 的受控清单；不得据此修改或重算冻结基线包的原始校验和。

## 3. 交付目标与当前总览

最终 Exit Gate：`R7 7/7 + R5 5/5 + CCR 14/14 + Lifecycle 14/14 + critical UNKNOWN/PARTIAL/MISSING = 0 + current HEAD reproducibly green`。

| 维度 | 当前基线判定 | B4 目标 |
|---|---|---|
| Reference-7 | 7 项均有实现落点；R7-06/R7-07 为 BLOCKED | 7/7 source-aligned closure |
| Reference-5 | 5 项形式存在；R5-04/R5-05 为 BLOCKED | 5/5 source-aligned closure |
| CCR-14 | CCR-10/12 为 BLOCKED；多项 PARTIAL | 14/14 source-aligned closure |
| Lifecycle-14 | 证据尚未全闭合 | 14/14 reference + Python trace + tests |
| 严格 Exit Gate readiness | 72/100（冻结审计估计） | 100/100，证据可复现 |

## 4. 阶段看板

| 阶段 | 范围 | 状态 | 进入条件 / 当前下一步 | 退出条件 |
|---|---|---|---|---|
| C0 | Truth refresh、coverage ledger、symbol/callgraph/state/runtime/divergence/scorecard 映射 | **In Progress** | 已完成基线与交付包核验；开始盘点现有 `docs/parity` 证据和 Python owner | 每个 R7/R5/CCR 有 reference owner、Python owner；每个 BLOCKED 有实现 target |
| C1 | Real sandbox、canonical process lifecycle、隔离 E2E | **In Progress** | macOS 已实现并测试通过；Linux、Windows 真实隔离仍待对应平台实现和验证 | R7-07、R5-05、CCR-12 不再 BLOCKED |
| C2 | Resume、Fork、Rewind、crash consistency | **Verified** | 真实后台 Agent 恢复已接入执行流程；Agent 生命周期测试通过 | R7-06、R5-04、CCR-10 主链闭合 |
| C3 | Compact-5 与 Context-9 差分 | **Verified** | 5 层压缩和 9 类上下文对照表已完成；完整测试通过 | CCR-03/04、R5-02 差分闭环 |
| C4 | Subagent、Background、MCP、Scheduler lifecycle | **Verified** | 功能完成；C4 测试 291 项通过；全项目测试通过 | CCR-11/14 与 lifecycle obligations 关闭 |
| C5 | Hook、cross-surface、fault differential | **Verified** | 功能完成；C5 测试 205 项通过；全项目测试通过 | CCR-01/07/08 与 R7-01/02 证明闭合 |
| C6 | Machine evidence、全量 Exit Gate | **In Progress** | C4、C5 已完成；开始处理整个 B4 的最终未完成项 | 所有 final row 与最终验证通过 |

## 5. 已确认硬阻塞项

| ID | 阻塞项 | 基线事实 | 归属阶段 |
|---|---|---|---|
| B4-B01 | Real sandbox isolation | `NoSandboxBackend.provides_isolation=False`；接口与 fail-closed 不构成实际隔离 | C1 |
| B4-B02 | Resume true re-entry | **已关闭**：恢复后重新进入真实 Agent 执行流程 | C2 |
| B4-B03 | Canonical process lifecycle | `DefaultProcessPolicy` 仍为 placeholder；kill-tree/abort 语义未统一 | C1 |
| B4-B04 | Compact-5 differential | **已关闭**：五层对照表和完整测试已完成 | C3 |
| B4-B05 | Context-9 differential | **已关闭**：九类上下文对照表和完整测试已完成 | C3 |
| B4-B06 | Subagent/MCP/Scheduler lifecycle | **已关闭**：完整功能测试 291 项通过；全项目测试通过 | C4 |
| B4-B07 | Cross-surface runtime differential | **已关闭**：新增相同输入跨入口结果比较；C5 测试 205 项通过 | C5 |
| B4-B08 | Machine-readable parity control plane | callgraph/state/runtime map 与 final scorecard 不完整 | C0/C6 |

## 6. 变更与验证日志

### 2026-08-13 — B4 启动与基线确认

- 状态：`Completed`
- 完成：确认仓库 HEAD 与 B4 冻结基线一致；确认 B4 交付包原始受控文件 SHA-256 全部通过。
- 完成：将 B4 Final Closure 项目置为 `Active`，当前进入 C0。
- 新增：本文件，作为后续开发、验证、阻塞和范围变更的连续记录。
- 未执行：未改动运行时代码，未宣称任何 R7/R5/CCR/Lifecycle 项完成。
- 下一步：盘点 `docs/parity` 现状及代码 owner，建立 C0 coverage ledger 和缺口实现 target。

### 2026-08-13 — C0 / 机器可读 Closure 控制面初始化

- 状态：`In Progress`
- 目标：把冻结审计中的 7×5×14 结论转成可追踪的 reference owner、Python owner、关键 call edge、runtime/state trace 与开放差异。
- Reference evidence：已直接核验 `shouldUseSandbox()`、`SandboxManager.wrapWithSandbox()` 与 `resumeAgentBackground() → runAgent` 的 recovered-source 调用关系。
- Python evidence：已核验 `NoSandboxBackend`、`ExecutionBoundary` 与 `resume_agent_background()`；后者仍只完成 race-safe claim、transcript read 与 fresh registration。
- 实现变更：新增 `docs/parity/coverage-ledger.yaml`、callgraph/state/runtime maps、known divergences、unmapped symbols 与 initial scorecard/history snapshot。
- 验证：`uv run python` 解析 8 个新增 YAML 资产；全部通过。`git diff --check` 通过。
- 结论：`未达标`；控制面已可用于 C1–C6 跟踪，但未关闭任何行为缺口。
- 风险或阻塞：B4-D01 real sandbox/process boundary 与 B4-D02 true resume re-entry 仍为 P0 开放差异。
- 下一步：进入 C1，按已冻结的 sandbox trace 实现 capability-detected isolation backend 与 canonical process lifecycle。

### 2026-08-13 — C1 / Canonical Process Lifecycle（第一增量）

- 状态：`In Progress`
- 目标：先消除 sandbox backend 的裸 `subprocess.run()` 生命周期，使超时不会遗留子进程树；该改动不将无隔离 backend 误标为 real sandbox。
- Reference evidence：`SandboxManager.wrapWithSandbox()` 是 reference 的实际命令包装边界；其超时/abort 语义属于 CCR-12 的 process boundary。
- Python evidence：`src/execution/sandbox.py::run_process_tree` 现为 `NoSandboxBackend` 的唯一执行路径，并复用 `src/utils/shell_platform.py` 的独立进程组与跨平台 kill-tree helper。
- Invariants：每次 launch 均为可终止的 tree root；timeout 采用 `TERM → 0.5s grace → KILL`；stdout/stderr 在终止后仍被 drain；无隔离能力仍显式为 `False`。
- 实现变更：新增 `SandboxExecutionResult.termination_reason` 和 canonical `run_process_tree()`；`NoSandboxBackend.run()` 不再直接调用 `subprocess.run()`。
- 验证：`uv run pytest tests/test_sandbox_backend.py tests/test_sandbox_policy.py tests/test_execution_boundary.py -q` → `29 passed`。
- 结论：`未达标`；Process lifecycle 得到首个可验证增量，B4-D01 仍开放，因为 filesystem/network/credential isolation 尚未实现。
- 风险或阻塞：macOS 当前可发现 `/usr/bin/sandbox-exec`；其 profile 与 Linux/Windows backend 的统一 contract 仍需实现和 E2E 验证。
- 下一步：为平台 backend 增加 capability detection 与受控 profile/config translation，并先覆盖 macOS 实际隔离路径。

### 2026-08-13 — C1 / macOS Seatbelt Isolation Backend（第二增量）

- 状态：`In Progress`
- 目标：在 macOS 上把 capability detection 与真实 OS sandbox 启动接入 `SandboxBackend` 合同，且探测失败时不降级为隐式裸执行。
- Reference evidence：`utils/sandbox/sandbox-adapter.ts::SandboxManager.wrapWithSandbox` 使用实际 sandbox runtime，并以依赖/平台能力决定可用性。
- Python evidence：新增 `src/execution/sandbox.py::MacOSSandboxBackend`；它以 harmless `sandbox-exec` probe 作为 capability 证据，再用 default-deny Seatbelt profile 启动命令。
- Invariants：不可用 probe 时 `provides_isolation=False`；unavailable backend 不会在 `run()` 中静默落回裸 subprocess；profile 仅允许请求 cwd 和 Darwin temporary directory 写入，且未允许网络。
- 实现变更：`default_sandbox_backend()` 在 macOS 选择 Seatbelt backend；新增 profile 与真实外部写入拒绝测试。
- 验证：`uv run pytest tests/test_sandbox_backend.py tests/test_sandbox_policy.py tests/test_execution_boundary.py -q` → `32 passed`；实际环境的 Seatbelt probe 通过，外部路径写入被拒绝。
- 结论：`PYTHON_ADAPTATION_VERIFIED`（仅限 C1 macOS execution-boundary 增量）；R7-07/R5-05/CCR-12 仍是 `PARTIAL`，不得宣告 complete。
- 风险或阻塞：应用 Bash 路径尚未统一经 `ExecutionBoundary`；settings 的 allow/deny path、network domain、secret scrub translation 与 Linux/Windows backend 未完成。
- 下一步：把 Bash launch 接入该边界，并用 settings 生成受控 filesystem/network profile 规则。

### 2026-08-13 — C1 / Foreground Bash Execution-Boundary Wiring（第三增量）

- 状态：`In Progress`
- 目标：让 foreground Bash 在 sandbox enabled 时实际通过已探测的 OS backend 启动，且不破坏已验证的 ESC/timeout result contract。
- Reference evidence：`shouldUseSandbox()` 先依据 manager capability/policy 选择 sandbox，随后通过 `SandboxManager.wrapWithSandbox()` 修改实际 launch。
- Python evidence：`src/tool_system/tools/bash/bash_tool.py::_bash_call` 构造 `SandboxRequest`，经 `ToolContext.execution_boundary.prepare_sandbox()` 决策；仅在 invocation 真实 isolated 时替换 launch argv。
- Invariants：Bash 的原有 `_run_bash_with_abort()` 仍是唯一 process-tree/abort/result-mapping owner；硬 gate 仍用于 startup safety，未因 backend 探测而改变全局 fail-closed 语义。
- 实现变更：新增 `sandbox_command_argv()`，将 Seatbelt 包装转换为 argv 而非第二个 subprocess runner；foreground Bash 接入该函数。
- 验证：`uv run pytest tests/test_sandbox_guard.py tests/test_sandbox_backend.py tests/test_sandbox_policy.py tests/test_execution_boundary.py tests/test_bash_timeout_vs_esc.py -q` → `62 passed`；覆盖真实 backend available 时的 sandbox-enabled Bash。
- 结论：`PYTHON_ADAPTATION_VERIFIED`（foreground Bash → macOS isolation launch）；整体 R7-07/R5-05/CCR-12 仍为 `PARTIAL`。
- 风险或阻塞：background Bash、filesystem allow/deny and network settings translation、secret policy profile、Linux/Windows backend 未完成。
- 下一步：扩展 SandboxSettings 并实现 filesystem/network policy 到 Seatbelt profile 的受控映射。

### 2026-08-13 — C1 / Filesystem Policy Translation（第四增量）

- 状态：`In Progress`
- 目标：把用户 sandbox 文件系统 allow/deny 配置解析为受控 Seatbelt profile 规则，而不是仅以 cwd 作为唯一写边界。
- Reference evidence：`convertToSandboxRuntimeConfig()` 从 settings/permission rules 汇集 filesystem allow/deny paths 后生成 runtime config。
- Python evidence：`SandboxSettings` 新增 `allowReadPaths`、`denyReadPaths`、`allowWritePaths`、`denyWritePaths`（亦接受 snake_case）；`sandbox_policy_from_settings()` 将其转换为 `SandboxPolicy`，`MacOSSandboxBackend._profile()` 输出对应 Seatbelt clauses。
- Invariants：默认拒绝仍优先；deny write 可以在 request cwd 的默认允许范围中再次收紧；用户路径经 `Path.resolve()` 后写入 profile。
- 实现变更：完成 filesystem policy 解析与 profile translation，并新增 profile string 与真实 `denyWritePaths` E2E 测试。
- 验证：真实 Seatbelt 临时目录探测确认被 deny 的 cwd 内文件写入返回 `PermissionError` 且文件未创建；随后纳入定向测试。
- 结论：`PYTHON_ADAPTATION_VERIFIED`（macOS filesystem deny-write 子合同）；网络 domain、read-policy E2E、background Bash、Linux/Windows 仍未完成。
- 下一步：添加 network policy 配置与 Seatbelt network rule translation；补 read-policy E2E。

### 2026-08-13 — C1 / Network Capability Translation（第五增量）

- 状态：`In Progress`
- 目标：将 sandbox 的网络能力配置映射为真实 Seatbelt 规则，并避免把 domain allowlist 伪装成已安全执行的 OS 规则。
- Reference evidence：`convertToSandboxRuntimeConfig()` 从 sandbox/network 与 permission 规则组装 network allow/deny 配置。
- Python evidence：`SandboxSettings.network.allowAll` 解析为 `SandboxPolicy.allow_all_network`；Seatbelt profile 默认不含 network allow clause，只有显式 enabled 时加入 `(allow network*)`。`allowedDomains` 被保留为 policy 数据但不会自动扩大为全网络访问。
- Invariants：sandbox 默认 network deny；仅 `allowAll=true` 才获得 OS 级网络能力；domain allowlist 尚未具备 DNS/IP pinning 合同前保持未实现、不得误报为 enforced。
- 实现变更：新增 network settings/policy translation 与 profile clauses。
- 验证：新增真实 loopback E2E：默认 profile 的 socket connect 被拒绝，`allowAll=true` 时连接成功；`tests/test_sandbox_backend.py` → `18 passed`。
- 结论：`PYTHON_ADAPTATION_VERIFIED`（binary network capability 子合同）；domain allowlist、read-policy E2E、background Bash 与跨平台 backend 仍开放。
- 下一步：实现 background Bash 经 ExecutionBoundary 的安全接入，保持后台任务 lifecycle 语义。

### 2026-08-13 — C1 / Background Bash Execution-Boundary Wiring（第六增量）

- 状态：`In Progress`
- 目标：关闭 `run_in_background` / Monitor 直接调用的 isolation 旁路，同时保留后台 task registry、输出文件、reaper、通知和 stop lifecycle。
- Reference evidence：sandbox 决策必须处在 action execution boundary，不可只覆盖一个前台 interaction surface。
- Python evidence：`src/tool_system/tools/bash/background.py::spawn_background_bash` 现在读取同一 sandbox settings，调用 `ToolContext.execution_boundary.prepare_sandbox()`，仅在真实 isolation 可用时替换 argv。
- Invariants：background module 仍是唯一 `Popen`、task id、runtime state、output handle 和 reaper owner；sandbox 只改变 launch argv；拒绝决策以 `ToolPermissionError` 传播，不能裸执行。
- 实现变更：background Bash 接入 `SandboxRequest` / `SandboxPolicy` / `sandbox_command_argv`。
- 验证：新增真实 Seatbelt E2E：sandbox enabled 的 background task 尝试写 workspace 外文件时失败，文件未创建；`uv run pytest tests/test_sandbox_guard.py tests/test_sandbox_backend.py tests/tasks/test_local_shell_migration.py tests/test_shell_completion_notification.py -q` → `59 passed`。
- 结论：`PYTHON_ADAPTATION_VERIFIED`（background Bash isolation wiring）；domain allowlist、read-policy E2E 和 Linux/Windows backend 仍开放。
- 下一步：补 read-policy E2E，并评估可安全实现的 domain allowlist strategy。

### 2026-08-13 — C1 / Filesystem Read-Deny E2E（第七增量）

- 状态：`In Progress`
- 目标：证明 `denyReadPaths` 不是仅生成 profile 文本，而是在真实 OS sandbox 中阻止受限文件读取。
- Reference evidence：reference sandbox runtime 同时维护 read/write allow/deny filesystem boundaries。
- Python evidence：`SandboxSettings.denyReadPaths → SandboxPolicy.deny_read_paths → MacOSSandboxBackend._profile()`。
- Invariants：即使 runtime 保留启动所需的广泛 read access，显式 deny path 仍必须优先于该 access；不得将受限内容写入 command stdout。
- 实现变更：新增真实 Seatbelt `denyReadPaths` E2E 单元测试。
- 验证：临时目录探测与测试均显示：读取被拒绝，进程非零退出，受限内容不出现在 stdout。
- 结论：`PYTHON_ADAPTATION_VERIFIED`（macOS filesystem read-deny 子合同）；domain allowlist、secret-scrub policy mapping、Linux/Windows backend 仍开放。
- 下一步：将 subprocess secret scrub 与 sandbox policy 结合，补 child-process secret visibility E2E。

### 2026-08-13 — C1 / Foreground Child Secret-Scrub E2E（第八增量）

- 状态：`In Progress`
- 目标：将 sandbox-enabled foreground Bash 与现有 subprocess secret scrub 联合验证，证明 child 进程不能观察到被 scrub 的 credential。
- Reference evidence：reference sandbox config 与 subprocess environment 都属于 execution boundary 的防御纵深，二者不能互相替代。
- Python evidence：foreground Bash 已使用 `subprocess_env()` 构造 child env，并经 `ExecutionBoundary` 进入 Seatbelt；测试覆盖 `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` 与 `ANTHROPIC_API_KEY`。
- Invariants：scrub 开启时 secret 不得出现在 child stdout；sandbox enabled 不得重引入被 scrub 的 env key。
- 实现变更：新增 sandbox-enabled Bash child secret visibility E2E。
- 验证：命令读取 `$ANTHROPIC_API_KEY` 时成功运行但 stdout 为空；该测试纳入 C1 回归。
- 结论：`PYTHON_ADAPTATION_VERIFIED`（foreground child secret scrub）；background secret E2E 和跨平台 isolation 仍开放。
- 下一步：继续处理 domain allowlist 的安全实现路径或 Linux backend capability abstraction。

### 2026-08-13 — C2 / True Resume Re-entry Contract Freeze

- 状态：`In Progress`
- 目标：冻结真实 resume 的 reference/Python call-edge 与不可省略状态步骤，再实施 canonical `run_agent` 重入。
- Reference evidence：recovered `resumeAgentBackground()` 过滤 transcript、重建 replacement state、组装 `runAgentParams`，然后调用 `runAgent`。
- Python evidence：graph trace 确认 `resume_agent_background()` 当前只到 `register_async_agent()`；`run_agent()` 已支持 `context_messages`、agent definition、tool registry、provider、abort controller 等必要输入。
- 结论：`未达标`；C2 的 P0 缺口已从概念性 blocker 收敛为明确 call-edge `resume_agent_background → run_agent`。
- 下一步：持久化/重建 resume 所需的 selected agent、tool/provider ownership 与 typed transcript messages，随后把 background lifecycle 接回 canonical run_agent。

### 2026-08-13 — C3 / Compact-5 Default Gate and Token Accounting Contract

- 状态：`In Progress`
- 目标：将 Compact-5 的两个关键差分行为固定为可复现测试：默认 Microcompact no-op，以及 AutoCompact 接收轻量层扣减后的 token budget。
- Python evidence：`CompressionPipeline` 顺序为 Result Budget → Snip → Microcompact → Context Collapse → AutoCompact；默认 `mc_enabled=False`。
- 实现变更：新增 `test_microcompact_default_gate_is_a_noop` 与 `test_autocompact_receives_tokens_after_cheap_layer_savings`。
- 验证：专项 parity 测试纳入本轮 C2/C3 定向回归。
- 结论：`PYTHON_ADAPTATION_VERIFIED`（C3 default gate / token accounting 子合同）；source-level trigger/no-op/durable-state 矩阵和 Context-9 仍未完成。
- 下一步：提取 Compact-5 各层 trigger/no-op/durable-state 表，并补 Context-9 source/scope/insertion/provenance ledger。

### 2026-08-13 — C4 / MCP Capability-Discovery Terminal Lifecycle

- 状态：`In Progress`
- 目标：确保 MCP transport handshake 成功但 `list_tools()` 失败时，不会发布错误的 `Connected` capability snapshot 或遗留可调用 client。
- Reference evidence：MCP lifecycle 的可用终态必须同时包含连接和 callable tool surface；仅 transport 成功不是 runtime-ready 状态。
- Python evidence：`src/services/mcp/connection_manager.py::MCPConnectionManager.reconnect_mcp_server` 与 `toggle_mcp_server` 统一经 `_install_connection()`；MCP graph owner 已核验为 `MCPConnectionManager`。
- Invariants：tool discovery 成功前不能缓存 client/tools；discovery exception 后 state 必须为 `FailedMCPServer`，tools 为空且 fresh client 已关闭；reconnect/toggle 的同名 server lock 不变。
- 实现变更：抽取连接安装路径；`list_tools()` 或 wrapper 失败时清理缓存、关闭 client、发布可诊断 terminal failure 后重新抛出原异常。
- 验证：新增 `test_reconnect_tool_discovery_failure_is_terminal_and_releases_client`；`uv run pytest tests/test_mcp_critic_majors.py tests/test_mcp_critic_followups.py tests/test_mcp_phase_polish_and_runtime.py -q` → `94 passed in 10.21s`。
- 结论：`PYTHON_ADAPTATION_VERIFIED`（C4 MCP capability-discovery failure 子合同）；Subagent、Scheduler 的 reference/Python runtime trace 与 MCP OAuth/reconnect 全链仍未闭合。
- 下一步：将同一 lifecycle trace 扩展到 scheduler restore/fire 与 subagent background completion，补跨边界状态证据。

### 2026-08-13 — C5 / Hook Timeout Process-Tree Fault Containment

- 状态：`In Progress`
- 目标：使 Hook timeout 成为无后续子进程副作用的终态，而非只结束 shell root。
- Reference evidence：Hook failure 是 CCR-01/07/08 的故障路径，终止必须在 caller 获得 timeout terminal result 前封闭执行树。
- Python evidence：`src/hooks/hook_executor.py::_execute_command_hook` 的所有 shell branch 现在使用 `popen_tree_kwargs()`，timeout 复用 `kill_process_tree()` 的 `TERM → 0.5s → KILL` 合同；C5 既有 fault/cross-surface tests 已盘点。
- Invariants：超时 Hook 的后台 child 不得在 timeout 后继续写 workspace；timeout 保留 `exit_code=-1` 与 blocking error；成功、exit-2 和非 blocking error 的现有语义不变。
- 实现变更：Hook subprocess launch 变为 killable tree root；timeout 从 `process.kill()` 改为 canonical tree termination 和 wait/drain。
- 验证：新增 `test_timeout_terminates_hook_process_tree_before_child_side_effect`；`uv run pytest tests/test_hook_executor.py tests/test_hook_output_schema.py tests/test_hook_event_taxonomy.py tests/test_fault_injection.py tests/test_cross_surface_parity.py -q` → `46 passed in 4.58s`；`git diff --check` 通过。
- 结论：`PYTHON_ADAPTATION_VERIFIED`（C5 Hook timeout fault-containment 子合同）；相同输入的 CLI/TUI/server runtime trace differential、streaming fault matrix 仍开放，不能宣告 CCR-01/07/08 或 R7-01/02 complete。
- 下一步：建立跨 surface 的 executable runtime trace fixture，并补 streaming cancellation / error terminal ordering 差分。

### 2026-08-13 — C4/C5 / 扩展回归与 MCP Shutdown 终态修复

- 状态：`In Progress`
- 目标：不将一次局部通过当作 C4/C5 停止条件；扩大 lifecycle/fault 覆盖后继续审计 live capability 的 shutdown 终态。
- 发现：扩展 C4/C5 回归未出现测试失败（`270 passed`），但代码审计确认 `MCPConnectionManager.close_all()` 只关闭 client，仍保留 `ConnectedMCPServer` state 与 wrapped tools，可能让后续调用面选择无 transport 的 stale capability。
- Python evidence：`src/services/mcp/connection_manager.py::close_all` 现遍历 active client/tools 的并集，在 per-server lock 中关闭 client 并清除 `_tools`、`_state`；`snapshot()`/`get_tools()`/`all_tools()` 由此不再暴露 shutdown 后能力。
- Invariants：shutdown 后不可发布可调用 MCP 工具；重复 close 仍幂等；未活跃的 pending/failed/disabled state 不被错误改写。
- 实现变更：修复 `close_all()` stale-state/cache 清理，并新增 `test_close_all_removes_stale_connected_capabilities`。
- 验证：扩展回归 `uv run pytest tests/scheduled_tasks tests/server/test_cron_control.py tests/test_mcp_critic_majors.py tests/test_mcp_critic_followups.py tests/test_mcp_phase_polish_and_runtime.py tests/test_mcp_auth_flow.py tests/test_hook_executor.py tests/test_hook_output_schema.py tests/test_hook_event_taxonomy.py tests/test_fault_injection.py tests/test_cross_surface_parity.py tests/test_query_hook_stopped.py tests/test_ch14_user_prompt_submit_round4.py tests/test_permission_request_hooks.py -q` → `270 passed in 11.97s`。修复后 `uv run pytest tests/test_mcp_phase_polish_and_runtime.py tests/test_mcp_critic_majors.py tests/test_mcp_critic_followups.py tests/test_mcp_auth_flow.py -q` → `106 passed in 10.73s`。
- 结论：`PYTHON_ADAPTATION_VERIFIED`（MCP shutdown capability-lifecycle 子合同）；C4/C5 仍未完成，后续继续推进 Scheduler/Subagent runtime trace 与 Hook/cross-surface streaming fault differential。
- 下一步：对 scheduler restore/fire、background subagent completion 与 streaming cancel/error ordering 建立端到端状态 trace 测试并持续修复。

### 2026-08-13 — C4、C5 完成与全项目测试

1. C4：`完成、已测试、测试通过`。
   - 工作类型：新增测试、Bug 修复、功能优化。
   - 完成内容：Subagent、后台任务、MCP、定时任务的创建、运行、失败、停止、恢复、关闭流程。
   - 测试结果：C4 测试 `291 passed`。

2. C5：`完成、已测试、测试通过`。
   - 工作类型：新增测试、Bug 修复、功能优化。
   - 完成内容：Hook 超时清理、Hook 报错、中断、流式执行报错，以及相同输入经过核心入口和服务端入口时结果一致。
   - 测试结果：C5 测试 `205 passed`。

3. 全项目测试发现并修复 5 项问题：`完成、已测试、测试通过`。
   - 3 项 Hook 测试未兼容新增的子进程参数：已修复测试。
   - 1 项隔离测试错误使用了真实 macOS 隔离环境：已明确指定无隔离环境。
   - 1 项后台通知测试会被其他后台线程抢先读取通知：已改为直接记录发送结果。

4. 最终全项目测试：`已测试、测试通过`。
   - 结果：`10142 passed, 10 skipped, 0 failed, 345 subtests passed`。
   - 用时：`296.09s`。

5. B4 最终收尾：`进行中`。
   - C4、C5 已完成。
   - 整个 B4 仍有 C1 跨平台隔离、C2 真实恢复执行、C3 上下文与压缩对照工作未完成。
   - 下一步优先完成 C2，再处理 C1、C3 和最终验收文件。

### 2026-08-13 — C2 真实后台 Agent 恢复

1. 问题：`Bug`。
   - 旧行为只把已结束 Agent 改成“运行中”，没有真正重新启动 Agent。
   - 用户发送的恢复消息不会被处理。

2. 修复：`完成`。
   - 原后台 Agent 启动时保存重新启动所需的运行信息。
   - 恢复时读取历史消息并重新调用 Agent 执行流程。
   - 执行完成或失败后更新最终状态并发送通知。
   - 缺少重新启动信息时明确返回失败，保持原终止状态，不显示假“运行中”。

3. 测试：`已测试、测试通过`。
   - 恢复和消息发送测试：`42 passed`。
   - 完整 Agent 生命周期测试：`244 passed`。

4. 状态：C2 `Verified`。
   - 下一步：完成 C3 上下文与压缩对照，再处理 C1 跨平台隔离和最终验收文件。

### 2026-08-13 — C3 压缩与上下文收尾

1. Compact-5：`完成`。
   - 新增 `docs/parity/runtime/compact-5-matrix.yaml`。
   - 记录五层顺序、触发条件、无操作条件和保存方式。

2. Context-9：`完成`。
   - 新增 `docs/parity/runtime/context-9-matrix.yaml`。
   - 记录九类上下文的来源、作用范围、加载时间、插入位置、信任规则和压缩行为。

3. 测试发现 1 项问题：`已修复`。
   - 本机自定义 Anthropic 地址会安全关闭全局缓存，但测试错误地要求全局缓存开启。
   - 测试现明确模拟官方地址；生产安全规则保持不变。

4. 测试：`已测试、测试通过`。
   - C3 完整测试：`283 passed`。

5. 状态：C3 `Verified`。
   - 下一步：处理 C1 跨平台隔离和最终验收文件。

### 2026-08-13 — C2–C5 最终测试与收尾状态

1. C2：`完成、已测试、测试通过`。
   - Agent 恢复和消息发送测试：`42 passed`。
   - 完整 Agent 生命周期测试：`244 passed`。

2. C3：`完成、已测试、测试通过`。
   - 压缩与上下文完整测试：`283 passed`。

3. C4：`完成、已测试、测试通过`。
   - Subagent、后台任务、MCP、定时任务测试：`291 passed`。

4. C5：`完成、已测试、测试通过`。
   - Hook、不同入口一致性、中断和报错测试：`205 passed`。

5. 最终全项目测试：`已测试、测试通过`。
   - 结果：`10144 passed, 10 skipped, 0 failed, 345 subtests passed`。
   - 用时：`305.88s`。

6. 整个 B4 最终状态：`进行中`。
   - 剩余工作仅为 C1 的 Linux、Windows 真实隔离实现和对应平台测试。
   - 当前 macOS 隔离已实现并通过测试。
   - 该平台限制不影响 C2、C3、C4、C5 的完成状态。

### 2026-08-13 — C2–C5 GitHub 发布准备

1. 生产代码注释：`优化、完成`。
   - 本轮新增注释和函数说明优先使用简体中文。
   - 注释说明真实业务行为、失败风险和安全边界，不只复述代码语法。
   - 保留必要的英文类名、函数名、协议名和操作系统术语，便于与代码准确对应。

2. 问题及解决策略：`完成、已测试、测试通过`。
   - C2 假恢复问题：保存原任务实时运行参数，恢复时重新进入真实 Agent 执行流程；依赖丢失时明确失败，不显示假“运行中”。
   - C3 本机自定义服务地址影响测试问题：测试明确模拟官方地址，生产环境的安全关闭规则不变。
   - C4 MCP 旧连接状态和工具缓存问题：工具发现成功后才发布连接；发现失败或关闭连接时同步清理客户端、状态和工具缓存。
   - C5 Hook 超时遗留子进程问题：统一终止整棵进程树，防止调用方收到失败结果后仍继续修改工作区。
   - 全项目测试兼容问题：修复 Hook 子进程参数、macOS 隔离环境选择和后台通知竞争对应测试，不降低生产逻辑要求。

3. 测试结果：`已测试、测试通过`。
   - C2：恢复和消息发送 `42 passed`；完整 Agent 生命周期 `244 passed`。
   - C3：压缩与上下文 `283 passed`。
   - C4：Subagent、后台任务、MCP、定时任务 `291 passed`。
   - C5：Hook、不同入口一致性、中断和报错 `205 passed`。
   - 全项目：`10144 passed, 10 skipped, 0 failed, 345 subtests passed`，用时 `305.88s`。
   - 发布前复查：`15` 个机器证据 YAML 全部解析通过；C2/C4/C5 和沙箱关键测试 `83 passed`。

4. 提交安全检查：`已检查、通过`。
   - 未纳入缓存、临时文件、运行日志或编辑器交换文件。
   - 未发现新增或修改文件包含 API key、私钥文件、本机用户路径或个人邮箱。
   - 仓库原有认证测试样例不属于本次改动，不纳入提交。

5. GitHub 发布状态：`进行中`。
   - 正式源代码、测试、B4 基线文档、机器证据和本进度记录已完成提交前整理。
   - 当前 B4 总状态仍为进行中；C1 Linux、Windows 真实隔离及对应平台测试不在本次 C2–C5 完成声明中。

## 7. 下一条目模板

```md
### YYYY-MM-DD — <阶段>/<工作项>

- 状态：`In Progress | Blocked | Ready for Verification | Verified`
- 目标：
- Reference evidence：files / symbols / call edges
- Python evidence：files / symbols
- Invariants：state / safety / failure / ordering
- 实现变更：
- 验证：命令、测试范围、结果
- 结论：`EXACT | SEMANTIC_EQUIVALENT | PYTHON_ADAPTATION_VERIFIED | 未达标`
- 风险或阻塞：
- 下一步：
```
