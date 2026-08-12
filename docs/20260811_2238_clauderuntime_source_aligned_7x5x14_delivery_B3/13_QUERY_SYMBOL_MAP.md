# ClaudeRuntime B3 — Query 包 Symbol 级双向对照报告

> 文档编号：`CR-B3-QUERY-SYMBOL-MAP`
> 依据：Wave 0 收尾第 2 步——P0 模块（query）symbol 级对照
> 基线：`def709361a86900920bf1d6b75134fdc9bc59def` / Reference `2.1.88` @ `a8a678cb`
> 对照范围：reference `src/query.ts`（1729 行）+ `src/query/`（config.ts/deps.ts/stopHooks.ts/tokenBudget.ts）↔ python `src/query/`（16 文件，5837 行）
> 日期：2026-08-12

## 1. 结论摘要

1. **EXACT 名称对应 4 处**（reference type/class ↔ python class 同名）：QueryParams、QueryConfig、QueryDeps、BudgetTracker —— 升级 **STRUCTURAL_VERIFIED**（文件级 1:1 + 符号级同名双证据）。
2. **命名规约对应 9 处**（camelCase → snake_case）：query↔query、buildQueryConfig↔build_query_config、handleStopHooks↔handle_stop_hooks、createBudgetTracker↔create_budget_tracker、checkTokenBudget↔check_token_budget、yieldMissingToolResultBlocks↔_yield_missing_tool_result_blocks、isWithheldMaxOutputTokens↔is_withheld_max_output_tokens、productionDeps（python 缺失，reference-only）—— 升级 **STRUCTURAL_VERIFIED**（除 productionDeps）。
3. **语义/结构对应**：queryLoop ↔ query.py 内 query() 生成器主循环（L686–1936，无独立函数）；MAX_OUTPUT_TOKENS_RECOVERY_LIMIT（ref L164）↔ query.py L103（=3，值一致）；COMPLETION_THRESHOLD/DIMINISHING_THRESHOLD（tokenBudget.ts L2/L4）↔ token_budget.py L14/L15；TerminalReason（旧 yaml SYM-QUERY-TERMINAL-001）↔ terminal.py L13 Literal —— 状态 **SEMANTIC_EQUIVALENT-CANDIDATE**（行为差分待 Wave 1 验证）。
4. **旧 yaml 种子复核**：5 条中 4 条在当前基线复核通过（SYM-QUERY-001/TERMINAL/MODEL/TOOL-ROUND），1 条（RECOVERY）部分通过（is_withheld_error 存在，且新增 is_withheld_max_output_tokens 直接对应 ref isWithheldMaxOutputTokens）。
5. **reference-only**：productionDeps（deps.ts L32）、feature 标记常量（reactiveCompact/contextCollapse/skillPrefetch/jobClassifier/snipModule/taskSummaryModule）→ python 侧 feature gate 机制待定位（CCR-14 关联）。
6. **python-only**：QueryEngine（engine.py，查询引擎封装）、ToolFailureLoopGuard（tool_failure_loop_guard.py）、continuation_nudge.py、BudgetGuard（budget.py）、Transition/QueryState（transitions.py）—— 其中 transitions.py 与 ref query.ts 内部 `transition: { reason: 'next_turn' }` 结构对应；engine.py 疑似产品扩展，待标记。

## 2. EXACT 名称对应（STRUCTURAL_VERIFIED）

| Reference | Python | 状态 |
|---|---|---|
| `type QueryParams`（query.ts L180） | `class QueryParams`（query.py L111） | STRUCTURAL_VERIFIED |
| `type QueryConfig`（config.ts L15） | `class QueryConfig`（config.py L10） | STRUCTURAL_VERIFIED |
| `type QueryDeps`（deps.ts L21） | `class QueryDeps`（deps.py L9） | STRUCTURAL_VERIFIED |
| `type BudgetTracker`（tokenBudget.ts L5） | `class BudgetTracker`（token_budget.py L29） | STRUCTURAL_VERIFIED |

## 3. 命名规约对应（camelCase → snake_case，STRUCTURAL_VERIFIED）

| Reference | Python | 说明 |
|---|---|---|
| `export async function* query`（L218） | `query`（query.py L686） | 主查询生成器，文件级 1:1（query.ts↔query.py） |
| `buildQueryConfig`（config.ts L28） | `build_query_config`（config.py L68） | 文件级 1:1（config.ts↔config.py） |
| `handleStopHooks`（stopHooks.ts L64） | `handle_stop_hooks`（stop_hooks.py L39） | 文件级 1:1（stopHooks.ts↔stop_hooks.py） |
| `createBudgetTracker`（tokenBudget.ts L12） | `create_budget_tracker`（token_budget.py L36） | 文件级 1:1 |
| `checkTokenBudget`（tokenBudget.ts L44） | `check_token_budget`（token_budget.py L59） | 文件级 1:1 |
| `yieldMissingToolResultBlocks`（L122） | `_yield_missing_tool_result_blocks`（query.py L331） | 同文件内对应 |
| `isWithheldMaxOutputTokens`（L175） | `is_withheld_max_output_tokens`（recovery.py L40） | 跨文件，语义一致 |
| `productionDeps`（deps.ts L32） | 无 | **reference-only，UNKNOWN** |

## 4. 语义/结构对应（SEMANTIC_EQUIVALENT-CANDIDATE，行为待 Wave 1 差分）

| Reference | Python | 依据 |
|---|---|---|
| `queryLoop`（L240 async generator） | query.py 内 query() 主循环（L686–1936） | 无独立 python 符号；循环语义对应（model→tool→result→repeat） |
| `MAX_OUTPUT_TOKENS_RECOVERY_LIMIT`（L164） | `MAX_OUTPUT_TOKENS_RECOVERY_LIMIT = 3`（query.py L103） | 常量名+值一致 |
| `COMPLETION_THRESHOLD`/`DIMINISHING_THRESHOLD`（L2/L4） | `COMPLETION_THRESHOLD = 0.9`/`DIMINISHING_THRESHOLD = 500`（token_budget.py L14/15） | 常量名+语义一致 |
| `TokenBudgetDecision`（type L42） | `ContinueDecision`/`StopDecision`（token_budget.py L41/51） | 决策类型拆分对应 |
| terminal reasons（query.ts 内部） | `TerminalReason`（terminal.py L13 Literal） | 旧 yaml SYM-QUERY-TERMINAL-001 复核通过 |
| `transition: { reason }`（query.ts L1309 附近） | `Transition`/`QueryState`（transitions.py L37/47） | 状态转移结构对应 |
| model call boundary | `invoke_provider`（model_call.py L163） | 旧 yaml SYM-QUERY-MODEL-001 复核通过 |
| tool round（msgToolUseBlocks L828 附近） | `execute_tool_round`（tool_round.py L32） | 旧 yaml SYM-QUERY-TOOL-ROUND-001 复核通过 |

## 5. 跨包对应（CCR 关联，UNVERIFIED→候选）

| Reference（query.ts 内） | Python 候选 | 关联机制 |
|---|---|---|
| `reactiveCompact`/`contextCollapse`/`snipModule`/`postCompactMessages`（const） | `services/compact/*` + `context_system` | CCR-03 Context Shaping |
| `useStreamingToolExecution`（L561） | `tool_system` streaming executor | CCR-07 |
| `permissionMode`（L571） | `permissions` | CCR-02 |
| `isWithheld413`（L1070）/`isWithheldMedia`（L1082） | `recovery.py` is_withheld_* 族 | CCR-08 |
| `extractMemoriesModule`/`jobClassifierModule`（stopHooks.ts） | `memory`/`services` | CCR-10/14 |

## 6. reference-only / python-only 清单

**reference-only（python 侧无对应，UNKNOWN）**：`productionDeps`；feature 常量组（reactiveCompact/contextCollapse/skillPrefetch/jobClassifier/snipModule/taskSummaryModule）。

**python-only（reference 侧无同名，UNKNOWN 或产品扩展候选）**：`QueryEngine`（engine.py）、`ToolFailureLoopGuard`（tool_failure_loop_guard.py）、`continuation_nudge.py`、`BudgetGuard`（budget.py）、`StreamEvent`（query.py L183）。

## 7. 旧 yaml 种子复核结果（当前基线 def7093）

| yaml 条目 | 复核结果 | 说明 |
|---|---|---|
| SYM-QUERY-001（query.ts:query ↔ query.py:query） | ✅ 通过 | EXACT 名称，升级 STRUCTURAL_VERIFIED |
| SYM-QUERY-TERMINAL-001（terminal reasons ↔ TerminalReason） | ✅ 通过 | terminal.py L13 Literal 确认 |
| SYM-QUERY-MODEL-001（model call ↔ invoke_provider） | ✅ 通过 | model_call.py L163 确认 |
| SYM-QUERY-TOOL-ROUND-001（tool round ↔ execute_tool_round） | ✅ 通过 | tool_round.py L32 确认 |
| SYM-QUERY-RECOVERY-001（recovery ↔ is_withheld_error） | ⚠️ 部分 | is_withheld_error 存在（L33）；新增 is_withheld_max_output_tokens（L40）为 ref isWithheldMaxOutputTokens 直接对应 |
| PKG-QUERY-001（query.ts ↔ query/*.py 7 文件） | ✅ 通过 | 本报告 §2/§3 佐证 |

## 8. 未确认项

1. ☐ queryLoop 与 query.py 主循环的逐行行为差分（Wave 1 differential test 目标）
2. ☐ QueryEngine/ToolFailureLoopGuard 属产品扩展还是 reference 语义（登记待定）
3. ☐ reference-only 常量（feature gates）的 python 侧机制落点（CCR-14）
4. ☐ token_budget.py 解析器（parse_token_budget/find_token_budget_positions）对应 reference 何处（疑似命令层，待查）
5. ☐ 本报告状态升级只到 STRUCTURAL_VERIFIED/SEMANTIC_EQUIVALENT-CANDIDATE；行为/安全/状态差分测试（EXACT 判定）留待 Wave 1

## 9. Stop/Terminal Reasons 差分对照（Wave 1 F5，2026-08-12）

数据源：reference `query.ts` 全部 `reason: '...'` 字面量（17 个）对照 python `TerminalReason`/`ContinueReason`。

**reference 终态（10）↔ python TerminalReason（13）**：全部覆盖。

| Reference 终态 | Python | 状态 |
|---|---|---|
| completed / blocking_limit / image_error / model_error / aborted_streaming / prompt_too_long / stop_hook_prevented / aborted_tools / hook_stopped / max_turns | 同名 TerminalReason 成员 | COVERED（同名） |
| （reference 无） | max_cost / tool_failure_loop / empty_response | PYTHON_ONLY（已登记） |

**reference 继续态（7）↔ python ContinueReason（8）**：全部覆盖（next_turn/token_budget_continuation/stop_hook_blocking/reactive_compact_retry/collapse_drain_retry/max_output_tokens_recovery/max_output_tokens_escalate 同名；python 额外 continuation_nudge 为扩展）。

**F5 修复**：`tool_failure_loop` 原漏登记 PYTHON_ONLY_TERMINAL_REASONS，已补登记（src/query/terminal.py）。

**差分测试**：`tests/test_query_terminal_parity.py`（4 项，全绿）——覆盖性 + 登记完整性（登记集合==差额）+ 终态/继续态互斥。
