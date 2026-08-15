# B7 Wave 记录（WAVE_RECORD）

## W0 — Truth Reset / Evidence Rebase ✅（2026-08-15）

- 交付包入库：`docs/clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814/`
- 建立 repo 级 `machine/` 真值目录（12 个 yaml + 1 个 json，全部绑定 subject_commit=16da0cf）
- canonical truth graph 建成：
  - `docs/baseline/PROJECT_BASELINE.md`（新建）
  - `docs/status/current.md`（重写：subject 绑定 16da0cf，新增 B7 状态段）
  - `docs/plans/active/CURRENT_PLAN.md`（新建；旧七组件计划标 HISTORICAL/SUPERSEDED）
  - `docs/governance/BEHAVIOR_BIBLE.md`（新建）
  - `docs/reference/reference-lock.yaml`（新建）
  - `docs/parity/scorecards/latest.yaml`（subject 7619ff2 → 16da0cf）
  - `docs/reference-differences/registry.yaml`（repository_head dc7393bb → subject_commit 16da0cf）
- 治理扩展：`scripts/check_docs_governance.py` 新增 `check_truth_ssot`（7 资产 subject 一致、
  reference-lock 策略、archive 非事实源、accepted diff 必带 evidence、machine 资产绑定）
- 测试：`tests/test_b7_truth_ssot.py` 10 项，全部通过
- 治理门禁：`python3 scripts/check_docs_governance.py` → PASS
- 退出条件：CURRENT assets 全部绑定同一 subject SHA ✅（16da0cf）

### changed owner / unchanged semantics / rollback
- changed owner：CURRENT truth（docs+机器资产）统一绑定 subject；旧字段 repository_head 废弃
- unchanged semantics：无任何运行时代码改动（纯文档/治理）
- rollback：回退本提交即可（无代码耦合）

## W1 — Permission Safe-by-Default ✅（2026-08-15）

- `ToolContext.permission_context` 默认值：`bypassPermissions` → **`default`**（fail-closed），
  隐式 bypass=0。
- `ToolPermissionContext` 新增 `bypass_origin` / `bypass_reason` + `is_bypass_justified()`；
  `check.py` 裁决点强制：裸 `bypassPermissions` 不再被认可（fall through → ask/deny）。
- 生产入口全部显式构造：`setup_permissions`（含 headless CLI `--dangerously-skip-permissions`
  origin/reason）、`run_agent._build_permission_context`（subagent 传播 parent provenance）、
  `_wrap_avoid_prompts`、`apply_rules_to_context` 保留 bypass 字段。
- headless ask-without-channel → deny（既有行为，新增回归测试固定）。
- registry 新增 5 条 PERM accepted-diff（machine/accepted-differences.yaml → registered），
  治理门禁要求 accepted diff 必须带 evidence。
- W0 补漏：`generate_parity_evidence.py` 将全部 15 个 parity 资产重绑 subject 16da0cf
  （evidence-manifest/coverage-ledger/source-map/runtime 等）。
- 测试：`tests/test_b7_permission_safe_default.py` 17 项；既有权限/工具测试适配
  （~20 个测试文件改为显式 justified bypass，含 3 处过时默认值注释更新）。
- 全量测试：后台确认（预计仅剩 B6 已知 7 项环境失败）。

### changed owner / unchanged semantics / rollback
- changed owner：permission context 默认值（安全默认）；bypass 溯源字段
- unchanged semantics：deny/ask/allow 裁决逻辑、安全不变量不变；仅"未注明溯源的 bypass"
  从 allow 变为 fail-closed
- rollback：回退本提交即可（默认值 + 校验为独立改动）

## W2 — Canonical Turn Preparation ✅（2026-08-15）

- 新建 `src/runtime/turn_preparation.py`：`PreparedTurn`（8 字段，frozen）+
  `TurnPreparationService`（无模型调用/无副作用/无 bypass）。
- `assemble_system_prompt_blocks` = canonical 冷启动块列表唯一实现（从
  `build_effective_system_prompt` 原样迁入，含 coordinator 分支与尾块缓存作用域）。
- `agent_loop_compat.build_effective_system_prompt` → 薄包装委托服务（无组装逻辑），
  headless/TUI/server cutover 路径 owner=1。
- `QueryEngine._build_system_prompt_parts` 保留为 legacy adapter（共享同一
  build_full_system_prompt_blocks helper），W6 完成 facade 收口
  （machine/deprecation-plan.yaml 记录 cutover_pending_w6）。
- 测试：`tests/test_b7_turn_preparation.py` 7 项（字节级等价、薄包装委托、无组装
  import、PreparedTurn 形状/不突变/冻结）；既有 212 项受影响测试全部通过。

### changed owner / unchanged semantics / rollback
- changed owner：turn preparation 唯一 owner = TurnPreparationService（cutover 路径）
- unchanged semantics：system prompt 输出与历史字节一致（等价性测试证明），零漂移
- rollback：回退本提交即可（服务为新增代码，旧函数保持签名）

## W3 — Extension Trust Boundary ✅（2026-08-15）

- 新建 `src/runtime/extension_activation.py`：`ExtensionDescriptor` +
  `ExtensionActivationGate`（ALLOW/DENY/REQUIRE_TRUST/INVALID/COLLISION）+ provenance
  ledger（name→scope+hash，可审计）；policy 读 `machine/extension-trust-policy.yaml`。
- 决策顺序确定性：INVALID（结构）→ 策略 DENY（project_over_managed）→ COLLISION
  （同 hash dedupe / 不同内容 reject / silent overwrite forbidden）→ REQUIRE_TRUST
  （project/user/mcp scope 未信任 workspace）→ ALLOW。
- 插件 loader 注册动作包到 gate 后：`register_plugin(workspace_trusted=, gate=)` 非
  ALLOW 即抛 PluginError（不再静默覆盖）；`load_plugins_from_directories` 批量共享
  一个 gate，跨目录同名插件确定性冲突。
- 未改 Plugin/MCP/Skill/Hook 内部机制（只统一 activation 生命周期边界）。
- 测试：`tests/test_b7_extension_activation.py` 17 项（矩阵 + loader 接线 + 审计）；
  既有插件/技能测试 70 项通过。

### changed owner / unchanged semantics / rollback
- changed owner：extension activation 决策 = ExtensionActivationGate（loader 注册动作
  包到门后）
- unchanged semantics：Plugin/MCP/Skill/Hook 加载内部机制不变；仅同名覆盖从静默改为
  确定性 reject
- rollback：回退本提交即可（gate 为新增代码，loader 参数向后兼容）

## W4 — Task / Session / Persistence Owner ✅（2026-08-15）

- `RuntimeTaskRegistry` 单写 owner 落实：`ToolContext.background_bash_tasks` 改为
  **只读投影** `LegacyTaskProjection`（get/[]/values/items 从 registry 实时派生；
  setitem/delitem/update/clear/pop/setdefault 一律 RuntimeError）。
- 消除双写：`background.py` spawn 与 reaper 的 legacy dict 镜像删除（registry 唯一写）。
- stuck-task guard 计数迁移到 `context.stuck_task_tracking`（派生遥测，非任务状态），
  不再在 legacy dict 上做原地计数。
- `SessionLifecycle`（src/runtime/session_lifecycle.py）：start/resume/fork/rewind/end
  生命周期 owner；`validate_durable_metadata` 拒绝 api_key/permission/trust/mcp/
  thread/handle 等 ephemeral 字段；resume 委托既有 durable 恢复并断言无 live handle。
- 测试：test_b7_task_single_writer 10 项 + test_b7_session_lifecycle 9 项；既有
  tasks/tool_system/server/resume 285 项通过（仅 3 项 pty 环境失败）。

### changed owner / unchanged semantics / rollback
- changed owner：runtime task 写 = RuntimeTaskRegistry 唯一（legacy 只读投影）；
  session 生命周期 = SessionLifecycle（resume 委托既有机制）
- unchanged semantics：legacy 读取方继续工作（投影形状 = to_legacy_dict）；
  任务状态机/恢复行为不变
- rollback：回退本提交即可（投影为新增；loader 调用点向后兼容）

## W5 — Context / Compact Closure ✅（2026-08-15）

- 新增 `src/services/compact/compression_outcome.py`：frozen `CompressionOutcome`
  （changed/stage/warnings/hard_limit_reached/artifacts/tokens_before/tokens_after）
  + `build_outcome` / `outcome_from_layers` 纯函数（共享构建逻辑）。
- 五阶段 pipeline：`CompressionResult.outcome` 字段；所有返回路径（含 early-exit）
  携带 outcome；各层失败改为收集 warnings（不再只 log 吞掉）。
- manual compact：`CompactionResult.outcome` 字段（stage=manual_compact /
  manual_partial_compact），与 automatic pipeline 共用 contract 不混淆 trigger。
- **未改五阶段算法**（顺序/各层逻辑原样），仅加结构化证据（Behavior Bible §H）。
- 测试：`tests/test_b7_compression_outcome.py` 9 项；既有压缩/查询测试 118 项通过。

### changed owner / unchanged semantics / rollback
- changed owner：压缩证据产出 = CompressionOutcome（统一 contract）
- unchanged semantics：五阶段算法与顺序不变；CompressionResult/CompactionResult
  向后兼容（新增字段带默认值）
- rollback：回退本提交即可

## W6 — Query/Server Ownership Extraction ✅（2026-08-15）

- `ModelCapabilityResolver`（src/runtime/model_capability_resolver.py）：capability
  判定唯一 owner。query.py 的 4 个 allowlist 谓词（extended/adaptive thinking、
  effort、xhigh）迁入 resolver（正则与清单逐字迁移，行为字节一致）；query 谓词
  改为薄委托。`ModelCapabilities` 不可变快照；prompt_cache 按 provider 家族判定。
- `CompletionVerifier`（src/runtime/completion_verifier.py）：protocol +
  StructuralCompletionVerifier 最小接线（终态 + evidence 存在性，不要求模型自评）。
- AgentServer facades（src/runtime/server_session_facades.py）：PermissionBridge /
  SurfaceEmitter / SchedulerBridge / SessionState / ServerSessionFacades；
  `_AgentSession.facades()` 懒构建并引用 LIVE 对象（零 wire 协议改动）。
- 测试：test_b7_model_capability 9 + test_b7_completion_verifier_and_facades 7；
  既有 query/server/effort 测试 75 项通过。

### changed owner / unchanged semantics / rollback
- changed owner：model capability 判定 = ModelCapabilityResolver；completion 判定
  protocol = CompletionVerifier；server 生命周期拆分为 typed facades
- unchanged semantics：query 状态机 / WebSocket / worker-thread / permission
  roundtrip / 能力判定结果全部不变（委托等价性测试证明）
- rollback：回退本提交即可

## W7 — CI / Platform / Evidence Truth ⏳

## W8 — Identity / Legacy Cleanup ⏳

## W9 — Freeze Gate / Baseline Lock ⏳
