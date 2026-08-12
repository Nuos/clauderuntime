# ClaudeRuntime Source-Aligned 7×5×14 B3 总交付包

> 版本：B3  
> 日期：2026-08-11  
> ClaudeRuntime baseline：`def709361a86900920bf1d6b75134fdc9bc59def`  
> Claude Code recovered source baseline：`a8a678cb6244e6770e1e421767ff0987a1d95549` / `2.1.88`  
> 论文：arXiv `2604.14228v2`

## 0. 本次重写的唯一方向

本包把所有开发行为重新锁定到一个唯一目标：

> **完整实现并验证 7 个核心功能组件、Reference-5 五层系统架构、14 个 Runtime 横切机制，使其关键功能、控制流、状态转换、安全语义、错误/恢复语义与 Claude Code 2.1.88 recovered source 的可确认行为一致。**

任何不能证明是上述目标直接依赖的工作，一律默认延期。

## 1. 本次相对 B2 的关键修订

1. **修复 HTML 交付方式**：所有主 HTML 均为完整、独立、UTF-8 单文件，CSS 内联，不依赖图片、CDN、脚本或外部资源；压缩包根目录另提供 `index.html`。
2. **采用附件 `index.html` 的横切机制框架**：将 14 个 Runtime 横切机制改为真正的 Cross-Cutting Harness，而不是把若干 lifecycle loop 与横切机制混为同一层级。
3. **保留旧 AUX-14 的所有必要行为要求**：旧 Main Loop、Stop Hook、Background、MCP、Scheduler、Resume/Fork/Rewind、Surface Interrupt 等不删除，而是映射到新的 14 个横切机制或 Reference-7/Reference-5 中，作为必须闭环的 runtime obligations。
4. **永久区分三套分类**：
   - `Reference-7`：论文正式七个核心功能组件；
   - `Reference-5`：论文正式五层 subsystem architecture；
   - `CCR-14`：论文 + recovered source 二次工程化归纳的 14 个 Cross-Cutting Runtime Mechanisms。
5. **Legacy 7 模块不再作为正式验收口径**：附件中的 `LLM / Context / AgentLoop / ToolRuntime / Policy / State / Execution Environment` 保留为分析视图，但正式验收必须用论文 Reference-7。
6. **单独重写 Source-Aligned Rules Bible v4.0**，把 13 条设计原则、9-step turn pipeline、两类 tool execution path、5 类 recovery、5 类 stop、7 层 safety、permission mode/behavior、tool pool assembly、context sources、session/sidechain/trust 等整合为可执行规则。

## 2. 文件说明

| 文件 | 用途 |
|---|---|
| `index.html` | **直接打开此文件**；总包导航，完全离线可查看 |
| `01_CURRENT_BASELINE_DIAGNOSTIC_B3.md` | B3 当前诊断基准线 |
| `02_SINGLE_OBJECTIVE_DEVELOPMENT_PLAN_B3.md/.html` | 唯一目标开发计划 |
| `03_CLAUDE_CODE_SOURCE_ALIGNED_RULE_BIBLE_v4.0.md/.html` | **最高行为/目标/要求圣经** |
| `04_7x5x14_CLOSURE_MATRIX_B3.md` | 7×5×14 验收矩阵与旧 AUX 映射 |
| `05_TAXONOMY_AND_TERMINOLOGY_CONSTITUTION_B3.md` | 分类、术语和冲突裁决宪法 |
| `06_BASELINE_MANIFEST_B3.json` | 机器可读基线 |
| `07_SOURCE_ALIGNMENT_CHANGELOG_B3.md` | B2→B3 重写说明 |
| `SHA256SUMS.txt` | 文件校验 |

## 3. HTML 打开方式

压缩包必须**先解压**，然后：

1. 双击根目录 `index.html`；或
2. 直接打开 `03_CLAUDE_CODE_SOURCE_ALIGNED_RULE_BIBLE_v4.0.html`。

这两个文件均为 standalone HTML，不需要 HTTP server，也不需要同目录图片资源。

## 4. 完成标准

只有同时满足以下条件，B3 Program 才可宣布结束：

```text
Reference-7: 7/7 SOURCE-ALIGNED COMPLETE
Reference-5: 5/5 SOURCE-ALIGNED COMPLETE
CCR-14:     14/14 SOURCE-ALIGNED COMPLETE

critical UNKNOWN = 0
critical PARTIAL = 0
critical MISSING = 0
critical undocumented divergence = 0

critical source map / symbol map / callgraph = complete
critical behavior / safety / state / fault tests = green
cross-surface runtime traces = source-equivalent
current HEAD validation = reproducible
```
