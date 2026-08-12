# ClaudeRuntime B3 开发进度日志

> 文档编号：`CR-B3-PROGRESS`（随开发迭代持续追加，最新条目在前）
> 程序：`clauderuntime-source-aligned-7x5x14`
> 基线：`def709361a86900920bf1d6b75134fdc9bc59def`
> Reference：Claude Code `2.1.88` @ `a8a678cb6244e6770e1e421767ff0987a1d95549`
> 唯一目标：Reference-7（7/7）+ Reference-5（5/5）+ CCR-14（14/14）全部 source-aligned complete

## 当前进度总览

| Wave | 阶段 | 状态 |
|---|---|---|
| 0 | Reference Contract Freeze | **进行中**（阶段一盘点基础设施已完成；reference 侧盘点与双向映射核实待办） |
| 1 | Canonical Core Spine | 未开始 |
| 2 | Safety / Action Spine | 未开始 |
| 3 | State / Session / Trust Spine | 未开始 |
| 4 | Isolation / Backend Spine | 未开始 |
| 5 | Cross-Surface / Crosscut Closure | 未开始 |

## 变更日志

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
