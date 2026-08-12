# ClaudeRuntime B3 — Wave 0 Exit Gate 检查表

> 文档编号：`CR-B3-W0-EXIT-GATE`
> 依据：`02_SINGLE_OBJECTIVE_DEVELOPMENT_PLAN_B3.md` §3（Wave 0 — Reference Contract Freeze）
> 基线：`def709361a86900920bf1d6b75134fdc9bc59def` / Reference `2.1.88` @ `a8a678cb`
> 状态：**NOT PASSED**（如实记录，未完成项不得冒充完成）

## 1. Exit Gate 项检查

| # | Exit Gate 要求 | 状态 | 证据 / 缺口 |
|---|---|---|---|
| 1 | Reference-7 每组件：文件、symbol、关键 call-edge、state-edge | PARTIAL→进行中 | 文件级对照完成（803 匹配 / 211 条 1:1）；**query 包 symbol 级对照完成**（13 报告）；**tool_system/permissions symbol 级对照完成**（6 组 EXACT 同名族，14 报告）；函数级 call-edge 差分留各 Wave |
| 2 | Reference-5 每层：边界、入口、出口、跨层调用 | PARTIAL | 层归属候选已映射（10 文档总表）；**每层边界/入口/出口的形式化证明未做** |
| 3 | CCR-14 每机制：入口、状态机、正常路径、失败路径、退出路径 | PARTIAL | 机制归属候选已映射；**状态机/路径证据未做** |
| 4 | 旧 AUX lifecycle obligations 全部映射到 R7/R5/CCR | DONE | 14 项全部登记（10 文档 §3，依据 B3 04 矩阵 §4） |
| 5 | package/symbol/callgraph maps 覆盖 critical cone | PARTIAL→进行中 | **package 级 + import 级 callgraph 完成**（55 节点/38 边，15 报告 + callgraph.json）；symbol 级 map 完成 query/tool_system/permissions 三包；函数级 callgraph 待补 |
| 6 | 所有未确认内容保持 UNKNOWN，不得凭记忆填充 | DONE | 全部映射标注 UNVERIFIED/UNKNOWN，无冒充完成 |

**判定：NOT PASSED** — 3 项 PARTIAL（1/2/3/5），需进入 Wave 0 收尾子任务。

## 2. 未完成项归因

| 项 | 缺口性质 | 原因 |
|---|---|---|
| symbol 级双向对照 | 工作量 | 36 reference 模块 × 逐符号对照 python 实现，需按 critical cone 优先级分批做（P0：query/tool_system/permissions） |
| callgraph（跨模块调用图） | 半成品 | import 级边已提取（两份 index 与模块页可见），但未汇成统一调用图（python↔reference 双图） |
| R5 层边界证明 | 依赖前项 | 依赖组件级对照完成后才能定层边界 |
| CCR-14 状态机 | 依赖前项 | 依赖机制对应模块核实 |

## 3. 既有证据种子（待复核）

| 来源 | 内容 | 复核要求 |
|---|---|---|
| `docs/parity/source-map/reference-package-map.yaml` | PKG-QUERY-001：query.ts ↔ query/*.py（旧基线 SEMANTIC_EQUIVALENT） | 在当前基线 def7093 下重跑确认 |
| `docs/parity/source-map/reference-symbol-map.yaml` | SYM-QUERY-001/TERMINAL/MODEL/TOOL-ROUND/RECOVERY（5 条） | 同上 |
| `docs/parity/source-map/reference-component-map.yaml` | C01–C07（UNKNOWN/PARTIAL，旧 7 组件视图） | 映射到 B3 Reference-7 正式视图 |
| `tests/parity/*.py` | 既有行为/结构 parity 测试（16+ 文件） | 作为 mapping 复核的行为证据来源 |

## 4. 进入 Wave 1 的前置清单（Wave 0 收尾）

1. ☐ P0 模块 symbol 级双向对照（query / tool_system / permissions 三包先行，产出 Closure Gate 模板证据行）；
2. ☐ python 侧与 reference 侧 callgraph 汇总（import 级边 → 图，标注 UNVERIFIED）；
3. ☐ PY_ONLY_MODULES（16 个）reference 落点定位（permissions/memory/compact_service 优先）；
4. ☐ 旧 yaml 证据种子在当前基线复核并升级/降级；
5. ☐ 完成上述后本表 1/2/3/5 转 DONE，Exit Gate 判定转 PASSED，方可进入 Wave 1。
