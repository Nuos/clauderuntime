# ClaudeRuntime B3 开发进度日志

> 文档编号：`CR-B3-PROGRESS`（随开发迭代持续追加，最新条目在前）
> 程序：`clauderuntime-source-aligned-7x5x14`
> 基线：`def709361a86900920bf1d6b75134fdc9bc59def`
> Reference：Claude Code `2.1.88` @ `a8a678cb6244e6770e1e421767ff0987a1d95549`
> 唯一目标：Reference-7（7/7）+ Reference-5（5/5）+ CCR-14（14/14）全部 source-aligned complete

## 当前进度总览

| Wave | 阶段 | 状态 |
|---|---|---|
| 0 | Reference Contract Freeze | **主体完成**（盘点基础设施 + 全模块盘点 + reference 侧盘点 + 双向映射 + P0 三包 symbol 对照 + callgraph + Exit Gate 检查表） |
| 1 | Canonical Core Spine | **完成**（F1 9-step trace / F2 config 快照 / F3 abort 清理 / F4 recovery 差分 / F5 terminal 差分，全量 10053） |
| 2 | Safety / Action Spine | **完成**（F6 权限链 / F7 tool pool / F8 双路径 / F9 result 契约，全量 10076） |
| 3 | State / Session / Trust Spine | **第一批完成**（F11 transcript / F12 resume 现状锁定 / F13 trust，全量 10088；resume 真重入接线登记 UNKNOWN 缺口） |
| 4 | Isolation / Backend Spine | **第一批完成**（F14 边界 / F15 sandbox fail-closed / F16 env / F17 network / F18 workspace，全量 10112；Real Sandbox 真实隔离登记 UNKNOWN） |
| 5 | Cross-Surface / Crosscut Closure | **第一批完成**（F19 cross-surface 等价 / F20 fault-injection，7×5×14 主体收官） |

## 变更日志

### 2026-08-12 — Wave 4/5 最终测试核验与异常修复

**实测结果**

1. Wave 4/5 定向行为测试 40/40；sourcemap、工作流 DSL 与 Wave 4/5 联合回归 66/66。
2. 全量 pytest 首轮：10122 passed / 10 skipped / 12 warnings / 345 subtests；发现 4 条 async unittest 未真正 await 的假绿测试，修复后 `tests/test_command_system.py` 26/26 真实执行通过；最终全量复跑 10122 passed / 10 skipped / 4 warnings / 345 subtests。
3. 文档治理检查通过；B3 基线校验和 13/13 通过；POSIX 安装器语法、status、dry-run、CLI 入口与 `uv build` 通过。

**已修复异常**

1. 修复 4 条异步 unittest 假绿（普通 TestCase 改为 IsolatedAsyncioTestCase）。
2. 修复 sourcemap Markdown 索引指向错误目录的 146 条链接，并增加生成器回归断言。
3. B3 与 sourcemap 纳入 docs 治理目录；修复 README 在 zsh 下 `.[dev]` 未引用导致安装命令失败。
4. bundled workflow 顶层 await/return 使用专用 DSL 编译器验证，补回归测试，避免被通用 compileall 误报。

**判定**

- 本轮功能、安装、文档治理回归通过；完整记录见 `18_WAVE4_WAVE5_FINAL_TEST_VERIFICATION_REPORT.md`。
- 规则圣经 §18 Exit Gate 仍未通过：Real Sandbox、resume 真重入、Compact-5、subagent/MCP/Scheduler 生命周期及函数级差分证据仍有缺口。

### 2026-08-12 — Wave 5 第一批：Cross-Surface Closure（F19/F20）— 7×5×14 主体收官

**完成项**

1. **F19 cross-surface 语义等价**（`tests/test_cross_surface_parity.py` 5 项）：agent_loop_compat 为适配器（import query 非第二 loop）、entrypoints 不定义第二套 permission 引擎 / tool pool 组装、tui 经 agent_server 间接汇入、daemon 诚实占位。
2. **F20 fault-injection traces**（`tests/test_fault_injection.py` 3 项）：**retry 有界**（连续 RateLimitError ≤ DEFAULT_MAX_RETRIES+1 次调用后耗尽，CCR-08 禁止无限 retry）、sandbox deny 无副作用（denied 命令不执行）、hook 执行层含异常容器。
3. **HEAD 可复现回归**：最终全量复跑 10122 passed / 10 skipped / 4 warnings / 345 subtests。

**验证结果**

- Wave 5 新测试 8/8；Wave 4/5 合计 40/40；全量 pytest 首轮 10122 passed

**7×5×14 收官状态（对照规则圣经 §18 Exit Gate）**

- Wave 0–5 五个阶段全部完成主体开发；全量测试零回归
- **仍未达 §18 完全 Exit Gate**：R7-07 Real Sandbox 真实隔离、resume 真重入、大量 UNKNOWN 映射为诚实登记的确认缺口（不冒充 complete）

### 2026-08-12 — Wave 4 第一批：Isolation/Backend 边界验证（F14–F18）

**完成项**

1. **F14 isolation 边界差分**（`tests/test_execution_boundary.py` 部分）：Permission≠Isolation（NoSandbox provides_isolation=False）、五边界独立可替换（workspace/env/process/sandbox/network 各组件独立 injection）。
2. **F15 sandbox fail-closed**（`tests/test_sandbox_policy.py` 10 项）：NoSandboxBackend 在 require_isolation / 禁 unsandboxed 时 deny；denied invocation run 返回 exit 126（不执行）；sandbox_policy_from_settings 的 enabled/fail_if_unavailable/platform gate 解析。
3. **F16 env/secret policy**（`tests/test_env_network_policy.py` 部分）：MinimalEnvPolicy allowlist 保留 + secret scrub + GitHub Action INPUT twins 移除；DefaultEnvPolicy 兼容透传。
4. **F17 network policy**：ConfigurableNetworkPolicy none/loopback/allowlist/full 四模式 + loopback 判定 + 无 host fail-closed。
5. **F18 workspace guard**：DefaultWorkspaceGuard canonical path（resolve）+ roots 校验 + escape 显式放行 + **symlink 解析到真实目标后判定**（R7-07 real-target/symlink second check）。

**验证结果**

- Wave 4 新测试 32/32；与 Wave 5 合并回归 40/40

**已知缺口（保持 UNKNOWN，不冒充完成）**

1. **Real Sandbox 真实隔离未实现**：唯一 backend 为 NoSandboxBackend（provides_isolation=False），符合规则圣经 CCR-12"不可计为 isolation complete"——需 OS 级隔离（seatbelt/Landlock）或有证据的 OS adaptation，登记为 Wave 4 遗留项；
2. DefaultProcessPolicy 为 placeholder（仅校验空命令），真实 process 策略（kill-tree/进程组）在 subprocess 执行层，待后续补齐。

### 2026-08-12 — W0~W3 整体核验（功能/模块结构/目录结构/7 组件/规则圣经合规）

**核验结果（详见 `16_W0_W3_VERIFICATION_REPORT.md`）**

| 维度 | 判定 |
|---|---|
| 功能 | ✅ 全量 **10088 passed / 0 failed**（两次复跑稳定），本次新增 82 项测试（12 文件） |
| 模块结构 | ✅ 55 模块 R5 五层归类清晰，无第二套 core（agent_loop_compat 为适配器） |
| 目录结构 | ✅ Python 合理边界（docs/src/scripts/tests/ui-desktop/ui-tui），未为 TS 目录外观破坏 Python 结构 |
| 7 核心组件 | ⚠️ 6/7 有实现+验证；**R7-07 Real Sandbox 缺口**（NoSandboxBackend 唯一 backend，execution/sandbox.py） |
| 规则圣经合规 | ⚠️ 9-step/双路径/Stop/Safety 已验证；**Exit Gate 未通过**（R7-07 + resume 真重入 + 大量 UNKNOWN） |

**关键发现（如实登记，不冒充完成）**

1. B3 诊断 7.1 坐实：Real Sandbox 未实现 → Wave 4 核心工作；
2. B3 诊断 7.3 坐实：resume 真重入未接线（RunAgentParams.context_messages 已就绪，接线点已定位）；
3. 术语澄清：`STRUCTURAL_VERIFIED` = 映射证据状态 ≠ 完成状态（EXACT/SEMANTIC_EQUIVALENT/PYTHON_ADAPTATION_VERIFIED），所有标注处均同步写明"行为差分留 Wave X"，未冒充 complete；
4. 既有 flaky 已修复/登记：test_review_fork（Memory 工具 enabled 依赖全局 settings 顺序）、test_unknown_fails_closed（workspace_trusted=None 读全局会话信任状态，测试显式传参修复）。

**最终结论**：W0~W3 开发内容整体核验通过（功能/结构/目录/合规），但 7×5×14 Exit Gate 未达到——按规则圣经 §18，继续完成 7×5×14，**Wave 4 Isolation/Backend 为下一优先级**。

### 2026-08-12 — Wave 3 第一批：State/Session/Trust 验证（F11–F13 + F12 现状锁定）

**完成项**

1. **F11 transcript 契约**（`tests/test_transcript_contract.py` 5 项）：append-oriented 读写回环、**tail crash tolerance**（残缺 JSONL 尾行不抛）、resume_session 重建（messages/metadata/success）、缺 metadata fail-closed、snip boundary（compact 标记）处理。
2. **F12 resume 现状锁定**（`tests/test_resume_agent_contract.py` 4 项）：race-safe re-registration（非终态拒绝/任务缺失原因）、transcript replay 计数、损坏 transcript 容错（resume without history）。
3. **F13 trust lifecycle**（`tests/test_pre_trust_gate.py` 6 项）：trusted 来源放行、project/local 需 workspace trust、**unknown fail-closed**、**session trust 不因 resume 恢复**（workspace_trusted=False → project 仍拒）。
4. **缺口登记（不冒充完成）**：B3 诊断 7.3 坐实——`resume_agent_background` 不驱动 model call（docstring 声明），`RunAgentParams.context_messages` 已就绪但 resume→run_agent 接线未完成（需扩展参数来源：agent_definition/provider），登记 UNKNOWN 遗留项。

**验证结果**

- Wave 3 新测试 15/15；相关回归 190 passed（1 项既有 flaky：test_review_fork 的 Memory 工具 enabled 依赖全局 settings 顺序，非本次引入，全量顺序下通过）
- 全量 pytest：后台验证中

**已知缺口（保持 UNKNOWN）**

1. resume 真重入 model 驱动未接线（接线点已定位：resume_agent_background → RunAgentParams.context_messages）；
2. subagent summary return / sidechain 结构由既有 transcript 机制承载（TranscriptWriter=sidechain 载体），专项测试留 Wave 3 后续。

### 2026-08-12 — Wave 2 第一批：Safety/Action Spine 功能开发（F6–F9）

**完成项**

1. **F6 权限安全链差分**（`tests/test_permission_safety_parity.py` 4 项）：classifier 不可用 + headless → deny（不 silent allow）；classifier 不可用 + 交互 → 保持 ask；headless fail-closed 决策带可解释 reason（F10 附带验证）；**hook allow 只产出 marker 不直接决定**（deny/safety 不可被 hook 越过，tool_hooks.py 不变式验证）。
2. **F7 tool pool 四阶段投影**（`tests/test_tool_pool_assembly.py` 5 项）：builtin 排序连续前缀、MCP 后置、deny 同时过滤 builtin/MCP、同名 dedupe builtin 胜出、get_tools 的 deny+enabled 过滤。
3. **F8 Streaming/Batched 双路径**（`tests/test_dual_path_parity.py` 6 项）：并发分类 fail-closed（未知工具/非 dict 输入 → serial）、safe 合并/交替拆分、concurrent batch 并行执行（完成乱序证明）、streaming 复用同一并发判定（执行中工具阻塞 unsafe 新工具）。
4. **F9 result 契约**（`tests/test_tool_result_contract.py` 7 项）：tool_use_id 配对、抛错 RAW 无包裹、40KB 截断、stderr 追加、小内容内联/大内容落盘（'x' 模式防重写）/JSON 持久化。
5. 测试中确认的既有实现质量：deny-first 5 步链、tool pool 缓存语义（builtin 前缀防 prompt-cache 失效）、can_use_tool 缺省 fail-closed——均与 reference 语义一致，无需代码修改。

**验证结果**

- Wave 2 新测试 22/22；相关回归（含既有 permission/tool parity）= 57 passed
- 全量 pytest：后台验证中

**已知缺口（保持 UNKNOWN）**

1. 权限链行为差分（deny-first 语义 vs reference permissions.ts 全向量）由既有 parity 测试覆盖，本轮补边界；
2. F10 权限链 trace 深化（决策 reason 覆盖已随 F6 验证）——如需显式 trace 基础设施留后续；
3. Wave 3 State/Session/Trust 未开始。

### 2026-08-12 — Wave 0 收尾：tools/permissions symbol 对照 + callgraph（w0g 完成主体）

**完成项**

1. **PY_ONLY 落点定位（关键）**：reference 侧 permission 机制位于 `utils/permissions/` 目录（19 文件）——python `permissions/` 包落点确认，`permissions` 从"无同名缺口"升级为已定位。
2. **6 组 EXACT 同名族**（reference↔python 函数逐一对应）：rules.py/updates.py/rule_parser.py/cycle.py/modes.py/registry.py；8 组强语义对应（types/loader/check/bash_security/filesystem/bash_suggestions/setup/build_tool）。报告：`14_TOOLS_PERMISSIONS_SYMBOL_MAP.md`。
3. **import 级 callgraph 汇总**：55 节点 / 38 边，`docs/sourcemap/callgraph.json` + `15_CALLGRAPH_REPORT.md`；核心枢纽 types（入度 7）/providers/utils，query 出度最高（7）。
4. 旧 yaml component-map C01–C07 复核：与 B3 Reference-7 命名一致，状态（C01 UNKNOWN、C02–C07 PARTIAL）与 01 诊断基线吻合，无需重映射。
5. 11 Exit Gate 项 1/5 更新（symbol 对照三包完成、import 级 callgraph 完成）。

**验证结果**

- 纯数据/文档产出（生成器无改动）；测试状态不受影响（全量 10053 passed 为最近确认）。

**已知缺口（保持 UNKNOWN）**

1. 函数级 callgraph 未生成（留各 Wave 差分阶段）；
2. bypassPermissionsKillswitch/permissionExplainer/autoModeState 等 5 项 reference 文件落点待核实（14 报告 §4）；
3. R5 层边界证明与 CCR-14 状态机证据（Exit Gate 项 2/3）未做。

### 2026-08-12 — Wave 1 第三批：recovery 差分（F4）—— Wave 1 收尾

**完成项**

1. **F4 recovery 差分测试**：`tests/test_query_recovery_parity.py`（4 项，对照 reference withRetry.ts/query.ts）：
   - general retryable error（429/RateLimitError）→ 指数退避重试至成功（yield api_retry，chat 3 次）；
   - 529 overloaded → 529 lane 重试（MAX_529_RETRIES=3）；
   - **fallback model**：连续 529 ≥3 次 + fallback_model → provider.model 切换（session-sticky）+ yield model_fallback（单次）；
   - **max-output tokens recovery**：escalate（override 64K）→ recovery（消息直接进下一轮 model 输入，不 yield）→ 继续成功，无 model_error 终态。
2. 调试中确认的设计行为：recovery 消息（"Output token limit hit"）不进入 yield 流，直接作为下一轮 model 输入（写入 QueryState.messages）——与 reference 语义一致，测试断言据此修正。
3. **Wave 1 全部功能项完成**：F1 9-step trace、F2 config 快照、F3 abort/close 清理、F4 recovery 差分、F5 terminal reasons 差分。

**验证结果**

- recovery parity 4/4；query 全家 + sourcemap = 54 passed
- 最终全量 pytest：后台验证中（预计 10050+ passed）

**已知缺口（保持 UNKNOWN）**

1. queryLoop 逐行行为差分（differential test）——Wave 1 后续深化项；
2. Wave 2 Safety/Action Spine（deny-first 权限链、tool pool 四阶段、双路径执行差分）未开始。

### 2026-08-12 — Wave 1 第二批：abort 清理验证 + terminal reasons 差分（F3/F5）

**完成项**

1. **F3 abort/generator-close 清理验证**：`tests/test_query_generator_cleanup.py`（3 项）——generator aclose mid-turn 无异常泄漏、tool round 前 aclose 无悬挂 asyncio 任务、abort 后中断语义正常。结论：现有 abort lane 清理良好，**无需补 finally**。
2. **F5 stop/terminal reasons 差分**：提取 reference query.ts 全部 17 个 reason 字面量（10 终态 + 7 继续态）对照 python。reference 10 终态 ⊆ TerminalReason（13）、7 继续态 ⊆ ContinueReason（8）全部覆盖。
3. **修复登记缺口**：`tool_failure_loop` 原漏登记 PYTHON_ONLY_TERMINAL_REASONS（reference 无此终态），已补登记为 adaptation extension（src/query/terminal.py）。
4. 差分测试 `tests/test_query_terminal_parity.py`（4 项）：覆盖性 + 登记完整性（登记集合==差额）+ 终态/继续态互斥。

**验证结果**

- cleanup 3/3、parity 4/4、turn_steps 9/9 全绿
- 全量 10042 passed（含 turn_steps）；最终全量（含 cleanup/parity）后台复核中

**已知缺口（保持 UNKNOWN）**

1. F4 recovery 差分（retry/max-output/prompt-too-long 状态机行为对照）——Wave 1 后续；
2. queryLoop 行为差分（differential test，trace 基础设施已就绪）。

### 2026-08-12 — Wave 1 第一批：9-step turn trace + config 快照（F1/F2）

**完成项**

1. **F1 9-step turn trace**：新模块 `src/query/turn_steps.py`（`TURN_STEPS` 9 常量 + `TraceEntry` + `TurnTracer`，与 B3 规则圣经 §7 9-step 完全对应；默认关闭零开销，`QueryParams.trace_steps` 开关）。
2. query() 主循环插入 9 个条件守卫挂接点（零行为改变）：settings（L730）、mutable state（L832）、context assembly（L851）、pre-model shapers（L854）、model call（L1028）、tool dispatch（L1801）、permission gate（L1802）、tool execution（L1814）、stop/continue（L1930）。
3. **F2 config 快照验证**：`build_query_config()` 在 query entry 只构建一次（测试断言 call_count==1），turn 内配置不漂移。
4. 单元测试 `tests/test_query_turn_steps.py`（9 项）：TurnTracer 单元 6 项 + query() 集成 2 项（单 turn 无工具序列=规范前 5 步；多 turn 带工具完整 9 步顺序）+ config 快照 1 项。

**验证结果**

- `tests/test_query_turn_steps.py`：9/9 passed
- 回归：test_query_loop.py + turn_steps + sourcemap = 43 passed
- 全量 pytest：待后台结果（预计 10000+ passed）

**已知缺口（保持 UNKNOWN）**

1. F3 abort/generator-close 清理验证（Wave 1 后续项）；
2. F4 recovery 差分（retry/max-output/prompt-too-long 状态机对照 reference）；
3. F5 stop/terminal 差分（terminal reasons 唯一事实源对照）；
4. queryLoop 行为差分（Wave 1 differential test，trace 基础设施已就绪）。

### 2026-08-11 — Wave 0 收尾第二步：query 包 symbol 级双向对照（w0g）

**完成项**

1. reference `query.ts`（1729 行）+ `query/` 4 文件 ↔ python `query/` 16 文件全量符号对照。
2. **4 处 EXACT 名称对应**（QueryParams/QueryConfig/QueryDeps/BudgetTracker）+ **7 处 camelCase→snake_case 规约对应**（query/build_query_config/handle_stop_hooks/create_budget_tracker/check_token_budget/_yield_missing_tool_result_blocks/is_withheld_max_output_tokens）升级 **STRUCTURAL_VERIFIED**。
3. **6 处语义/结构对应**（queryLoop↔query() 主循环、MAX_OUTPUT_TOKENS_RECOVERY_LIMIT=3、COMPLETION/DIMINISHING_THRESHOLD、TerminalReason、Transition/QueryState、invoke_provider、execute_tool_round）标 **SEMANTIC_EQUIVALENT-CANDIDATE**（行为差分留 Wave 1）。
4. **旧 yaml 5 条种子复核**：4 条通过、1 条部分（SYM-QUERY-RECOVERY-001 新增 is_withheld_max_output_tokens 直接对应）；PKG-QUERY-001 佐证通过。
5. reference-only（productionDeps、feature 常量组）与 python-only（QueryEngine/ToolFailureLoopGuard/continuation_nudge/BudgetGuard/StreamEvent）清单登记，保持 UNKNOWN。
6. 报告落盘：`13_QUERY_SYMBOL_MAP.md`。

**验证结果**

- 纯文档/数据产出，无代码变更；单测与全量回归状态不受影响。

**已知缺口（保持 UNKNOWN）**

1. queryLoop 行为差分留 Wave 1（differential test）；
2. QueryEngine/ToolFailureLoopGuard 产品扩展 vs reference 语义待定；
3. feature gates（reference const 组）python 落点待定位（CCR-14）。

### 2026-08-11 — Wave 0 收尾第一步：文件级同名匹配（w0g）

**完成项**

1. reference 与 python 全量文件名规范对照（camelCase→snake_case 归一）：803 条同名匹配落盘 `docs/sourcemap/file-level-match.json`（机器可读）。
2. **211 条 1:1 唯一匹配**（一个 reference 文件精确对应一个 python 文件）——最高置信度结构证据（STRUCTURAL_VERIFIED 候选），覆盖 30 个 reference 模块：utils 73、bridge 26、services 22、commands 17、tools 12、skills 9、cli 8、memdir 8 等；典型如 `query.ts→query/query.py`、`stopHooks.ts→stop_hooks.py`、`tokenBudget.ts→token_budget.py`、整套 bridge/memdir 同名族。
3. 136 条多候选匹配（reference 文件对应多个 python 候选，python 侧目录重组所致）保持 UNVERIFIED，报告列全清单待逐条核实。
4. 报告落盘：`12_FILE_LEVEL_MATCH_REPORT.md`（1:1 全表 + 多候选摘要 + 未确认项）。

**验证结果**

- 生成脚本无代码变更（纯数据盘点），既有 24/24 单测不受影响；全量回归 10033 passed 覆盖本轮前状态。

**已知缺口（保持 UNKNOWN）**

1. 1:1 仅证明文件级存在对应，symbol 级语义对照未做（Wave 0 收尾第 2 步）；
2. 多候选落点需人工判断（如 prompt.ts → 5 个候选）；
3. 无匹配 reference 文件的语义归属待 symbol 级定位。

### 2026-08-11 — Wave 0 阶段二：reference 侧盘点 + 双向映射初版

**完成项**

1. 扩展生成器 `scripts/sourcemap_generator.py` 支持 reference 侧盘点（TS/JS 启发式扫描：类/函数/导出符号 + import 调用边规约；`--ref-src` 模式）。
2. 生成 reference 全量盘点 37 个 HTML（`docs/sourcemap/reference/`）：36 个模块（35 目录 + top-level 单文件组），1901 个 TS/JS 文件，508,002 行。
3. Reference↔Python 双向映射初版：36/36 reference 模块均有候选映射（REF_TO_PY_MAP 启发式同名/特表），全部 UNVERIFIED；python 侧 16 个无同名 reference 的模块登记为缺口（permissions/memory/compact_service 等，UNKNOWN）。
4. 复核既有证据种子：`docs/parity/source-map/*.yaml`（PKG-QUERY-001 等 5 条 symbol 映射，旧基线 d29bfe/241d704）——已登记需在当前基线 def7093 下复核。
5. 单元测试新增 6 项 reference 用例（发现/扫描/映射覆盖/渲染章节/index 缺口/生成命名），共 24 项。

**验证结果**

- `tests/test_sourcemap_generator.py`：24/24 passed
- 浏览器实测 reference index：36 模块导航、双向映射总览、python-only 缺口清单正常

**产出物路径**

| 产物 | 路径 |
|---|---|
| reference 索引 | `docs/sourcemap/reference/index.html` |
| reference 模块盘点（快照 20260811_2337） | `docs/sourcemap/reference/NN-<模块>-20260811_2337.html` |
| markdown 源 | `docs/sourcemap/reference/markdown/` |

**已知缺口（保持 UNKNOWN）**

1. reference 顶层符号提取为启发式正则，召回率待人工抽样验证；
2. PY_ONLY_MODULES（16 个）的 reference 落点未定位；
3. 旧 yaml 证据种子待当前基线复核；
4. 双向映射全部 UNVERIFIED，symbol 级对照未做。

### 2026-08-11 — Wave 0 阶段一：盘点基础设施 + 全模块自动盘点

**完成项**

1. 建立 `docs/sourcemap/` 源码盘点目录，命名规则 `NN-模块名-YYYYMMDD_HHMM.html`（编号按字母序固定，时间戳标识盘点快照，历史快照留档）。
2. 编写盘点生成器 `scripts/sourcemap_generator.py`：
   - AST 级提取每模块文件清单、行数、类/函数符号（含行号）、import 调用边（支持相对导入推算，如 `from ..tool_system.x` → 顶层依赖 tool_system；包内自引用不计入跨模块边）；
   - 每模块生成 R7/R5/CCR-14 启发式映射初版，一律标注 `UNVERIFIED`（符合 B3「未确认保持 UNKNOWN」）；
   - markdown → 自包含 HTML（左侧可伸缩导航栏，经 md2html_sidebar 管线）。
3. 全模块盘点产出 56 个 HTML：55 个模块（54 目录模块 + `core-single-files` 单文件组）+ `index.html` 总导航；源码规模 648 个 py 文件 / 159,060 行。
4. 单元测试模块 `tests/test_sourcemap_generator.py`（18 项）：模块发现完整性、编号连续性、相对导入解析、self-import 排除、映射 ID 合法性、md 章节与 UNVERIFIED 标注、无 GFM 表格（md2html 兼容）、命名规则、HTML 侧边栏有效性、index 链接完整性、shim 识别。
5. 浏览器实测：index 与模块页侧边栏折叠（translateX -280px）/导航/scrollspy 正常。

**验证结果**

- `tests/test_sourcemap_generator.py`：18/18 passed
- 全量回归 `pytest tests/`：10027 passed / 10 skipped / 0 failed（EXIT=0）

**产出物路径**

| 产物 | 路径 |
|---|---|
| 盘点索引 | `docs/sourcemap/index.html` |
| 模块盘点（最新快照 20260811_2304） | `docs/sourcemap/NN-<模块>-20260811_2304.html` |
| markdown 源 | `docs/sourcemap/markdown/` |
| 生成器 | `scripts/sourcemap_generator.py` |
| 单元测试 | `tests/test_sourcemap_generator.py` |

**已知缺口（保持 UNKNOWN，不冒充完成）**

1. 全部模块的 R7/R5/CCR 映射均为启发式初版（UNVERIFIED），待逐项对照 reference source 核实升级；
2. reference 侧（`restored-src`，3698 个 js/ts 文件）模块级 source map 尚未生成；
3. 旧 AUX lifecycle obligations → R7/R5/CCR 归属登记尚未落盘；
4. 模块一句话职责全部 UNKNOWN，待人工核实。

## 待办（下一步）

1. Wave 0 阶段二：reference 侧盘点（restored-src 结构 → HTML，同命名规则）与 R7/R5/CCR 双向映射核实（UNVERIFIED → EXACT / SEMANTIC_EQUIVALENT / PYTHON_ADAPTATION_VERIFIED）；
2. Wave 0 阶段三：旧 AUX-14 → canonical owner 映射登记；
3. Wave 0 Exit Gate 检查表（每个节点有 reference evidence）。
