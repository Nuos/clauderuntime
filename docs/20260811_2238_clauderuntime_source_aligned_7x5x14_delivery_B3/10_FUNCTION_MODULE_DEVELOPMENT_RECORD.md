# ClaudeRuntime B3 功能模块开发记录

> 文档编号：`CR-B3-MODULE-RECORD`（随开发迭代持续更新）
> 程序：`clauderuntime-source-aligned-7x5x14`
> 基线：`def709361a86900920bf1d6b75134fdc9bc59def`
> Reference：Claude Code `2.1.88` @ `a8a678cb6244e6770e1e421767ff0987a1d95549`
> 数据来源：`docs/sourcemap/` 盘点快照（20260811_2304）+ 开发动作记录
> 关联文档：`09_DEVELOPMENT_PROGRESS.md`（进度日志，宏观迭代视角）；本文档为模块维度视角

## 1. 状态定义

**开发状态机**（每模块一列，按序升级）：

| 状态 | 含义 |
|---|---|
| `INVENTORY_COMPLETE` | 自动盘点完成（文件/符号/import 边已提取，见 docs/sourcemap/） |
| `MAPPING_VERIFYING` | R7/R5/CCR 归属核实中（对照 reference source 逐项确认） |
| `SOURCE_ALIGNED` | 达到 B3 完成门（EXACT / SEMANTIC_EQUIVALENT / PYTHON_ADAPTATION_VERIFIED 之一） |
| `DEFERRED` | 明确延期（不阻塞 7×5×14 的必要依赖以外工作） |

**映射状态词**（沿用 B3 宪法）：完成 = `EXACT` / `SEMANTIC_EQUIVALENT` / `PYTHON_ADAPTATION_VERIFIED`；未完成 = `PARTIAL` / `UNKNOWN` / `MISSING`；不计入 core = `PRODUCT_EXTENSION` / `INTENTIONAL_DIVERGENCE`。启发式初版一律 `UNVERIFIED`，核实后方可升级。

## 2. 模块总表（55 模块）

| 编号 | 模块 | 类型 | 文件 | 行数 | R7 候选 | R5 候选 | CCR 候选 | 开发状态 | 映射状态 |
|---|---|---|---|---|---|---|---|---|---|
| 01 | `agent` | 包 | 18 | 3879 | R7-03 | R5-02 | CCR-11 | INVENTORY_COMPLETE | UNVERIFIED |
| 02 | `assistant` | 包 | 3 | 289 | R7-02 | R5-01 | — | INVENTORY_COMPLETE | UNVERIFIED |
| 03 | `auth` | 包 | 8 | 1422 | R7-04 | R5-03 | CCR-02/CCR-13 | INVENTORY_COMPLETE | UNVERIFIED |
| 04 | `background` | 包 | 2 | 121 | — | — | CCR-11/CCR-10/CCR-14 | INVENTORY_COMPLETE | UNVERIFIED |
| 05 | `bootstrap` | 包 | 2 | 1310 | R7-02 | R5-01 | CCR-14 | INVENTORY_COMPLETE | UNVERIFIED |
| 06 | `bridge` | 包 | 37 | 11760 | R7-02 | R5-01 | CCR-14 | INVENTORY_COMPLETE | UNVERIFIED |
| 07 | `buddy` | 包 | 9 | 1510 | R7-02 | R5-01 | — | INVENTORY_COMPLETE | UNVERIFIED |
| 08 | `cli_backup` | 包 | 1 | 16 | R7-02 | R5-01 | — | INVENTORY_COMPLETE | UNVERIFIED（shim） |
| 09 | `cli_core` | 包 | 4 | 351 | R7-02 | R5-01 | — | INVENTORY_COMPLETE | UNVERIFIED |
| 10 | `command_system` | 包 | 38 | 8250 | R7-02 | R5-01 | — | INVENTORY_COMPLETE | UNVERIFIED |
| 11 | `compact_service` | 包 | 2 | 335 | — | — | CCR-03 | INVENTORY_COMPLETE | UNVERIFIED |
| 12 | `components` | 包 | 1 | 23 | R7-02 | R5-01 | — | INVENTORY_COMPLETE | UNVERIFIED（shim） |
| 13 | `constants` | 包 | 3 | 195 | — | — | CCR-14 | INVENTORY_COMPLETE | UNVERIFIED |
| 14 | `context_system` | 包 | 14 | 4513 | — | — | CCR-03/CCR-04 | INVENTORY_COMPLETE | UNVERIFIED |
| 15 | `coordinator` | 包 | 4 | 794 | — | — | CCR-06 | INVENTORY_COMPLETE | UNVERIFIED |
| 16 | `core-single-files` | 组 | 13 | 3343 | R7-02 | R5-01 | CCR-14 | INVENTORY_COMPLETE | UNVERIFIED |
| 17 | `eco` | 包 | 6 | 1002 | — | — | — | INVENTORY_COMPLETE | UNVERIFIED |
| 18 | `entrypoints` | 包 | 12 | 3360 | R7-02 | R5-01 | — | INVENTORY_COMPLETE | UNVERIFIED |
| 19 | `execution` | 包 | 4 | 635 | R7-07 | R5-05 | CCR-12 | INVENTORY_COMPLETE | UNVERIFIED |
| 20 | `goals` | 包 | 3 | 1317 | R7-03 | R5-02 | — | INVENTORY_COMPLETE | UNVERIFIED |
| 21 | `hooks` | 包 | 14 | 3350 | — | — | CCR-01 | INVENTORY_COMPLETE | UNVERIFIED |
| 22 | `keybindings` | 包 | 1 | 29 | R7-02 | R5-01 | — | INVENTORY_COMPLETE | UNVERIFIED（shim） |
| 23 | `knowledge` | 包 | 3 | 172 | — | R5-04 | — | INVENTORY_COMPLETE | UNVERIFIED |
| 24 | `memdir` | 包 | 10 | 2203 | — | R5-04 | — | INVENTORY_COMPLETE | UNVERIFIED |
| 25 | `memory` | 包 | 8 | 2020 | — | R5-04 | — | INVENTORY_COMPLETE | UNVERIFIED |
| 26 | `migrations` | 包 | 1 | 16 | — | — | CCR-10 | INVENTORY_COMPLETE | UNVERIFIED（shim） |
| 27 | `models` | 包 | 9 | 1316 | — | — | CCR-14 | INVENTORY_COMPLETE | UNVERIFIED |
| 28 | `moreright` | 包 | 1 | 16 | — | — | — | INVENTORY_COMPLETE | UNVERIFIED（shim） |
| 29 | `native_ts` | 包 | 1 | 16 | — | — | — | INVENTORY_COMPLETE | UNVERIFIED（shim） |
| 30 | `outputStyles` | 包 | 3 | 238 | — | — | CCR-14 | INVENTORY_COMPLETE | UNVERIFIED |
| 31 | `permissions` | 包 | 31 | 11719 | R7-04 | R5-03 | CCR-02/CCR-13 | MAPPING_VERIFYING | STRUCTURAL_VERIFIED（4 EXACT 族+4 强对应，见 14 报告） |
| 32 | `plan` | 包 | 2 | 39 | R7-03 | R5-02 | — | INVENTORY_COMPLETE | UNVERIFIED（shim） |
| 33 | `plugins` | 包 | 11 | 1145 | — | — | CCR-05 | INVENTORY_COMPLETE | UNVERIFIED |
| 34 | `providers` | 包 | 20 | 8711 | — | R5-05 | — | INVENTORY_COMPLETE | UNVERIFIED |
| 35 | `query` | 包 | 16 | 5837 | R7-03 | R5-02 | CCR-03/CCR-04/CCR-08/CCR-14 | MAPPING_VERIFYING | STRUCTURAL_VERIFIED(11)/UNVERIFIED（见 13 报告） |
| 36 | `reference_data` | 包 | 1 | 1 | — | — | CCR-14 | INVENTORY_COMPLETE | UNVERIFIED（shim） |
| 37 | `remote` | 包 | 4 | 908 | — | R5-05 | CCR-12 | INVENTORY_COMPLETE | UNVERIFIED |
| 38 | `scheduled_tasks` | 包 | 3 | 648 | — | — | CCR-14 | INVENTORY_COMPLETE | UNVERIFIED |
| 39 | `schemas` | 包 | 1 | 16 | — | — | — | INVENTORY_COMPLETE | UNVERIFIED（shim） |
| 40 | `screens` | 包 | 1 | 22 | R7-02 | R5-01 | — | INVENTORY_COMPLETE | UNVERIFIED（shim） |
| 41 | `server` | 包 | 22 | 11906 | R7-02 | R5-01 | CCR-14 | INVENTORY_COMPLETE | UNVERIFIED |
| 42 | `services` | 包 | 108 | 21733 | — | — | CCR-06/CCR-14 | INVENTORY_COMPLETE | UNVERIFIED |
| 43 | `settings` | 包 | 8 | 957 | — | — | CCR-14 | INVENTORY_COMPLETE | UNVERIFIED |
| 44 | `skills` | 包 | 17 | 3219 | — | — | CCR-05 | INVENTORY_COMPLETE | UNVERIFIED |
| 45 | `state` | 包 | 4 | 1009 | R7-06 | R5-04 | CCR-10 | INVENTORY_COMPLETE | UNVERIFIED |
| 46 | `tasks` | 包 | 9 | 2070 | — | — | CCR-06 | INVENTORY_COMPLETE | UNVERIFIED |
| 47 | `tool_system` | 包 | 63 | 15772 | R7-05 | R5-03 | CCR-05/CCR-06/CCR-07/CCR-09 | MAPPING_VERIFYING | STRUCTURAL_VERIFIED（tools.ts↔registry.py 同名族 + Tool.ts↔build_tool.py，见 14 报告） |
| 48 | `transports` | 包 | 9 | 3146 | R7-02 | R5-01 | — | INVENTORY_COMPLETE | UNVERIFIED |
| 49 | `types` | 包 | 4 | 1321 | — | — | CCR-14 | INVENTORY_COMPLETE | UNVERIFIED |
| 50 | `upstreamproxy` | 包 | 6 | 1065 | — | R5-05 | CCR-12 | INVENTORY_COMPLETE | UNVERIFIED |
| 51 | `utils` | 包 | 47 | 11305 | — | — | — | INVENTORY_COMPLETE | UNVERIFIED |
| 52 | `vim` | 包 | 1 | 24 | R7-02 | R5-01 | — | INVENTORY_COMPLETE | UNVERIFIED（shim） |
| 53 | `voice` | 包 | 1 | 16 | R7-02 | R5-01 | — | INVENTORY_COMPLETE | UNVERIFIED（shim） |
| 54 | `wiki` | 包 | 4 | 368 | — | R5-04 | — | INVENTORY_COMPLETE | UNVERIFIED |
| 55 | `workflow` | 包 | 20 | 2302 | R7-05 | R5-03 | — | INVENTORY_COMPLETE | UNVERIFIED |

统计：55 模块（54 包 + 1 组），648 个 py 文件，159,060 行。shim 模块 13 个（≤60 行小模块/占位，不承载 core 语义的待确认）。

## 3. 模块详细开发记录

记录格式：每个模块按时间顺序追加动作条目；状态升级时同步更新第 2 节总表。当前全部模块仅有 Wave 0 初始动作：

### 2026-08-12 — tools/permissions symbol 对照 + callgraph（Wave 0 收尾主体完成）

1. permissions 落点定位：reference `utils/permissions/` ↔ python `permissions/`（PY_ONLY 缺口消除）。
2. 6 组 EXACT 同名族 + 8 组强对应（`14_TOOLS_PERMISSIONS_SYMBOL_MAP.md`），10 总表 permissions/tool_system 升级 MAPPING_VERIFYING。
3. import 级 callgraph（55 节点/38 边）：`docs/sourcemap/callgraph.json` + `15_CALLGRAPH_REPORT.md`。
4. 旧 component-map C01–C07 复核通过（与 B3 Reference-7 命名一致）。

### 2026-08-12 — query 包 Wave 1 第三批（F4）— Wave 1 完成

1. F4 recovery 差分 4 项全绿：429 重试、529 lane、fallback model 切换、max-output escalate+recovery。
2. 确认设计行为：recovery 消息不 yield、直接进下一轮 model 输入（QueryState.messages）。
3. **Wave 1（query 包）全部功能项完成**：F1–F5。模块开发状态：MAPPING_VERIFYING（行为差分已覆盖核心路径，queryLoop 逐行差分留深化项）。

### 2026-08-12 — query 包 Wave 1 第二批（F3/F5）

1. F3：abort/generator-close 清理验证通过（`tests/test_query_generator_cleanup.py` 3 项），现有 abort lane 无需补 finally。
2. F5：terminal/transition reasons 差分——reference 10 终态 + 7 继续态全覆盖；修复 `tool_failure_loop` 漏登记（src/query/terminal.py）；差分测试 4 项全绿。
3. 13 报告新增 §9 Stop/Terminal Reasons 差分对照。

### 2026-08-12 — query 包 Wave 1 功能开发（F1/F2）

1. F1：`src/query/turn_steps.py` 新增（9-step trace 基础设施），query() 挂接 9 点，`QueryParams.trace_steps` 开关（默认关闭零开销）。
2. F2：验证 `build_query_config()` query-entry 单次构建（config 快照防漂移，测试断言 call_count==1）。
3. 测试 `tests/test_query_turn_steps.py` 9 项全绿；回归 43 passed；query 模块开发状态维持 MAPPING_VERIFYING，行为差分（queryLoop/stop/recovery）留 Wave 1 F3–F5。

### 2026-08-11 — query 包 symbol 级对照（Wave 0 收尾第二步）

1. 4 处 EXACT 名称对应 + 7 处命名规约对应升级 **STRUCTURAL_VERIFIED**（`13_QUERY_SYMBOL_MAP.md`）。
2. 6 处语义/结构对应标 SEMANTIC_EQUIVALENT-CANDIDATE（行为差分留 Wave 1）。
3. 旧 yaml 5 条种子：4 通过 + 1 部分（SYM-QUERY-RECOVERY-001）；PKG-QUERY-001 佐证通过。
4. 10 总表 query 行升级：INVENTORY_COMPLETE → MAPPING_VERIFYING；映射状态 STRUCTURAL_VERIFIED(11)/UNVERIFIED。
5. reference-only 与 python-only 清单登记（保持 UNKNOWN，禁止冒充完成）。

### 2026-08-11 — 文件级同名匹配（Wave 0 收尾第一步）

1. 全量文件级对照：803 条同名匹配（`docs/sourcemap/file-level-match.json`）。
2. 211 条 1:1 唯一匹配升级为 **STRUCTURAL_VERIFIED 候选**（文件级证据，symbol 级待核实）；136 条多候选维持 UNVERIFIED；其余 UNKNOWN。
3. 报告：`12_FILE_LEVEL_MATCH_REPORT.md`（30 个 reference 模块分组全表）。
4. 联动规则：10 文档总表的映射状态以本次 1:1 证据为升级起点，但仍需 symbol 级对照后才可标 MAPPING_VERIFYING 完成。

### 2026-08-11 — reference 侧盘点与双向映射初版（Wave 0 阶段二）

1. reference 侧 36 模块全部完成盘点（`docs/sourcemap/reference/`，快照 20260811_2337）：文件清单、类/函数/导出符号（启发式正则）、import 级调用边。
2. Reference↔Python 候选映射：36/36 有候选（`REF_TO_PY_MAP`），全部 UNVERIFIED；python 侧 16 个无同名 reference 模块登记为缺口（UNKNOWN），名单：auth、background、compact_service、eco、execution、goals、knowledge、memory、models、permissions、plan、providers、reference_data、scheduled_tasks、settings、workflow。
3. 既有证据种子登记：`docs/parity/source-map/reference-package-map.yaml`（PKG-QUERY-001：query.ts ↔ query/*.py，旧基线 SEMANTIC_EQUIVALENT）、`reference-symbol-map.yaml`（SYM-QUERY-001/TERMINAL/MODEL/TOOL-ROUND/RECOVERY 共 5 条）、`reference-component-map.yaml`（C01–C07，含 UNKNOWN/PARTIAL）。均需在当前基线 def7093 下复核。
4. 旧 AUX-14 lifecycle obligations → B3 canonical owner 登记（依据 B3 04 矩阵 §4，全部已覆盖）：

| 旧 AUX obligation | B3 canonical owner |
|---|---|
| Main Agent Query Loop | R7-03 / R5-02 |
| Tool Execution Loop | CCR-06 + CCR-07 |
| Permission Escalation Loop | CCR-02 + CCR-13 |
| Retry / Model Recovery | CCR-08 |
| Compaction Loop | CCR-03 |
| Stop Hook Loop | CCR-01 + R7-03 |
| Subagent Query Loop | CCR-11 |
| Background Agent Lifecycle | CCR-11 + CCR-10 + CCR-14 |
| MCP Lifecycle | CCR-05 + CCR-06 + CCR-12 + CCR-13 |
| Scheduler / Cron | CCR-14 + CCR-10 + CCR-06 |
| Resume / Fork / Rewind | CCR-10 + CCR-13 |
| Surface Streaming / Interrupt | R7-02 + CCR-07 + CCR-08 |
| Session Persistence / Recovery | CCR-10 |
| Long-output Result Budgeting | CCR-09 + CCR-03 |

### 2026-08-11 — 全模块初始盘点（Wave 0 阶段一）

1. 全部 55 模块完成自动盘点：文件清单、类/函数符号（含行号）、import 级调用边（含相对导入解析）已提取并生成 `docs/sourcemap/NN-<模块>-20260811_2304.html`。
2. R7/R5/CCR 归属为启发式初版（见总表候选列），全部 `UNVERIFIED`，禁止冒充完成。
3. 模块一句话职责全部 `UNKNOWN`，待人工核实。

### 重点模块核实优先级（critical cone 内，Wave 1/2 先行）

| 优先级 | 模块 | 核实重点（对照 reference source） |
|---|---|---|
| P0 | `query` | authoritative query path、9-step turn、stop/terminal、recovery 状态机（R7-03/R5-02/CCR-03/04/08/14） |
| P0 | `tool_system` | tool pool 四阶段、Streaming/Batched 双路径、result 契约（R7-05/CCR-05/06/07/09） |
| P0 | `permissions` | deny-first、ask/classifier/escalation precedence、fail-closed（R7-04/CCR-02/13） |
| P1 | `hooks` | lifecycle event、timeout、blocking/async、stop/permission integration（CCR-01） |
| P1 | `context_system` + `compact_service` | 9 context sources、Compact-5 顺序（CCR-03/04） |
| P1 | `state` + `memory` + `memdir` | transcript/lineage/sidechain、resume/fork/rewind（R7-06/R5-04/CCR-10） |
| P2 | `agent` | subagent 隔离、delegation、summary return（CCR-11） |
| P2 | `execution` + `remote` + `upstreamproxy` | sandbox/env/network/process boundary（R7-07/R5-05/CCR-12） |
| P3 | `providers` + `transports` + `entrypoints` | backend 生命周期、surface 汇入（R5-01/05） |

## 4. 更新规则

1. 每次对某模块的盘点、核实、实现、修复动作完成后，在本文件追加动作条目（日期 + 内容 + 验证结果 + 证据路径），并同步更新第 2 节总表状态列。
2. 映射状态升级必须附 reference evidence（reference 文件/symbol/call-edge + python 侧对应 + 测试），不允许无证据升级。
3. 模块职责从 `UNKNOWN` 变更为确认描述时，在动作条目中登记依据（reference 或源码行为证据）。
4. shim 模块确认不承载 core 语义后，标注 `DEFERRED` 并从 critical cone 移除；若发现承载 core 语义则升级为正常模块。
5. 与 `09_DEVELOPMENT_PROGRESS.md` 保持同步：进度日志记宏观迭代，本文档记模块粒度动作。
