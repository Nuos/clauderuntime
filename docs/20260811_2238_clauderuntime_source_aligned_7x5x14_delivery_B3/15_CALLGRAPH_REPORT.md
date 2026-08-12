# ClaudeRuntime B3 — Callgraph 汇总报告（import 级）

> 文档编号：`CR-B3-CALLGRAPH`
> 依据：Wave 0 收尾——package/symbol/callgraph maps 覆盖 critical cone（11 号检查表项 5）
> 基线：`def709361a86900920bf1d6b75134fdc9bc59def` / Reference `2.1.88` @ `a8a678cb`
> 机器可读数据：`docs/sourcemap/callgraph.json`
> 日期：2026-08-12

## 1. 图统计

1. 节点（模块）: 55
2. 边（模块级 import，去重）: 38
3. 边来源: 每模块 AST 提取的 import 目标（绝对 + 相对导入解析），聚合到 src 顶层模块
4. 说明: 本图为模块级 import 边（静态调用边的第一层证据）；函数级 call-edge 逐条对照留 Wave 1+ 各模块差分阶段

## 2. 核心枢纽（入度 Top 12）

| 模块 | 被依赖数 | 定位 |
|---|---|---|
| types | 7 | 类型契约（R7/CCR 通用底座） |
| providers | 5 | Backend Layer 模型提供方 |
| utils | 5 | 通用工具 |
| context_system | 3 | Context 组装 |
| token_estimation | 3 | token 预估（CCR-03/09 依赖） |
| tool_system | 2 | 工具系统（R7-05） |
| cost_tracker | 2 | 成本追踪（CCR-09） |
| skills | 2 | 技能系统 |
| services | 2 | 服务层 |

## 3. 高依赖模块（出度 Top 8）

| 模块 | 依赖数 | 说明 |
|---|---|---|
| query | 7 | Core Spine 枢纽（依赖 types/providers/utils/services/tool_system/context_system/token_estimation） |
| agent | 6 | subagent 编排 |
| command_system | 6 | 命令系统 |
| services | 6 | 服务层 |
| compact_service | 4 | Compact 管线 |
| context_system | 3 | Context 组装 |
| core-single-files | 2 | 顶层入口组 |
| entrypoints | 1 | surface 入口 |

## 4. 解读

1. `query` 出度最高（7）印证其 canonical loop 枢纽地位（R7-03/R5-02）；`types`/`providers`/`utils` 入度最高印证其底座地位。
2. `tool_system` 入度仅 2 偏低于预期——工具大多经 `query`/`services` 间接引用，直接 import 边少（间接调用链待函数级 callgraph 补充）。
3. 边数 38（模块级去重）低于潜在函数级调用数——本图是**第一层静态视图**，函数级 callgraph 为后续 wave 增量。

## 5. 未确认项

1. ☐ 函数级 callgraph（symbol 粒度）未生成——留各模块差分阶段；
2. ☐ tool_system 间接调用链（经 services 中转）待补充；
3. ☐ reference 侧 callgraph（query.ts 等文件级 import 边已在 reference 盘点 md 中，未汇总成图）。
