# ClaudeRuntime B3 — Wave 4/5 最终测试与行为圣经核验报告

> 文档编号：`CR-B3-W4W5-FINAL-TEST`
> 日期：2026-08-12
> 测试分支：`codex-b3-wave1-source-alignment`
> 测试基点：`e7a9021` 及当前待提交修复
> 规范：`03_CLAUDE_CODE_SOURCE_ALIGNED_RULE_BIBLE_v4.0.md`

## 0. 总体结论

本轮功能回归、Wave 4/5 定向测试、文档治理、POSIX 安装行为、Python 打包与 CLI 入口均通过；发现的异步测试假绿、sourcemap 链接、docs 治理登记和 zsh 安装命令问题已修复。

**本轮代码可进入 main 提交准备，但不得宣称 7×5×14 已 source-aligned complete。** 规则圣经 §18 Exit Gate 仍被 Real Sandbox、resume 真重入及多项差分证据缺口阻塞。

## 1. 测试范围与结果

| 检查 | 结果 | 说明 |
|---|---:|---|
| Wave 4/5 定向测试 | 40 passed | execution/env/network/sandbox/cross-surface/fault |
| 联合定向回归 | 66 passed | 上述 40 + sourcemap 25 + bundled workflow 1 |
| command system 修复复测 | 26 passed | 4 条 async 测试已真实 await |
| 全量 pytest 首轮 | 10122 passed, 10 skipped, 12 warnings | 345 subtests，260.48s |
| 全量 pytest 最终复跑 | 10122 passed, 10 skipped, 4 warnings | 345 subtests，265.23s |
| 文档治理 | passed | `scripts/check_docs_governance.py` |
| B3 基线校验和 | 13/13 passed | 00–08、index、reference 基线文件 |
| POSIX 安装器 | passed | bash 语法、status、dry-run |
| Python 发布构建 | passed | sdist + wheel 1.5.0 |
| CLI 入口 | passed | console script 与 `python -m src.cli` |
| Windows 安装器 | 未实机验证 | 当前 macOS 无 PowerShell；仅源码核查 |

最终复跑与首轮通过数一致；修复异步测试基类后，相关 8 条 warning 消失，剩余 4 条已在 §6 分类。

## 2. 已发现并修复的问题

### BUG-01：4 条异步 unittest 假绿

- 严重度：高（测试可信度）
- 现象：普通 `unittest.TestCase` 中定义 `async def test_*`，协程未 await，pytest 仍计为 passed。
- 影响：`/help`、unknown command、`/init` 两条异步路径实际未执行。
- 修复：相关类改为 `unittest.IsolatedAsyncioTestCase`。
- 复测：`tests/test_command_system.py` 26 passed，原 8 条 Runtime/Deprecation warning 消除。

### BUG-02：sourcemap Markdown 索引链接失效

- 严重度：中（文档可用性）
- 现象：`markdown/index-*.md` 使用同目录 HTML 链接，但 HTML 实际位于父目录；共修复 146 条。
- 修复：生成器输出 `../<module>.html`，同步既有三个索引并补 Python/reference 两侧断言。
- 复测：sourcemap 25 passed；文档治理通过。

### BUG-03：新增交付目录未纳入 docs 治理

- 严重度：中（CI/治理）
- 现象：B3 交付目录和 `docs/sourcemap` 未在顶层 allowlist，治理检查失败。
- 修复：显式纳入治理目录；未使用 broken-link allowlist 掩盖错误。
- 复测：文档治理通过。

### BUG-04：README 开发安装命令在 zsh 失败

- 严重度：中（安装）
- 现象：`pip install -e .[dev]` 被 zsh 当作 glob，报 `no matches found`。
- 修复：改为 `pip install -e ".[dev]"`。
- 复测：zsh 失败原因确认；打包与现有 CLI 入口通过。

### TEST-05：bundled workflow 被通用 compileall 误报

- 类型：测试工具适配，不是产品 bug。
- 原因：工作流 DSL 刻意允许顶层 await/return，由 `compile_workflow()` 包入 async 函数；普通 compileall 不理解该语义。
- 处理：增加 bundled workflow 专用编译测试；`deep-research` meta 提取和编译通过。

## 3. 未修复问题与风险

| ID | 严重度 | 状态 | 问题 |
|---|---|---|---|
| GAP-01 | 高 | OPEN | Real Sandbox 未实现；默认仍是 `NoSandboxBackend(provides_isolation=False)` |
| GAP-02 | 高 | OPEN | `resume_agent_background` 不驱动真实 model 重入 |
| GAP-03 | 中 | OPEN | `DefaultProcessPolicy` 仅校验空命令，缺真实进程组/kill-tree 策略证明 |
| GAP-04 | 中 | OPEN | Compact-5、9 context sources、subagent summary、MCP/Scheduler 生命周期缺专项差分 |
| GAP-05 | 中 | OPEN | cross-surface 5 项中多项是源码文本断言；hook containment 也是源码计数断言，证据强度有限 |
| GAP-06 | 中 | OPEN | Wave 0 Exit Gate 仍有 R7/R5/CCR 函数级 call-edge/state-machine PARTIAL |
| DOC-01 | 低 | OPEN | 模块盘点快照为 648 个 Python 文件，当前源码为 650 个，需重生成快照 |
| DOC-02 | 低 | OPEN | R7-01 User 仅横切说明，55 模块总表无独立 owner 行，证据追踪不完整 |
| DOC-03 | 低 | FIXING | 原 SHA256SUMS 只覆盖 00–08 等 13 项，需纳入 09–18 |
| ENV-01 | 中 | OPEN | Windows install.ps1 未在 PowerShell/Windows 实机运行 |

## 4. 行为圣经核验

| 维度 | 本轮判定 | 关键证据/缺口 |
|---|---|---|
| Reference-7 | 6/7 有实现与测试；未 complete | R7-07 缺 Real Sandbox；R7-01 owner 追踪不足 |
| Reference-5 | 5/5 有目录落点；未 complete | 边界入口/出口形式化证明未闭合 |
| CCR-14 | 14/14 有候选落点；未 complete | CCR-03/04/11/12/14 等仍 PARTIAL |
| 9-step / stop / retry | 通过核心路径 | 既有 Wave 1/2/5 测试 + retry fault injection |
| Permission / trust | 通过核心安全路径 | deny-first、headless fail-closed、trust reset |
| Isolation | 部分通过 | fail-closed policy 通过；真实 OS isolation 缺失 |
| Cross-surface | 部分通过 | 未发现第二 core；仍缺用户动作 runtime trace 全向量 |
| §18 Exit Gate | **NOT PASSED** | 仍存在 critical UNKNOWN/PARTIAL |

规则圣经 19 章覆盖情况沿用 17 号报告：5 章完全验证，其余为部分验证或有确认缺口。本轮没有足够证据将任何 PARTIAL/UNKNOWN 批量升级为完成状态。

## 5. 结构与目录核验

- `src` 仍按 Python 职责分包；54 个顶层包 + core single-file 组构成 55 模块口径。
- 当前有 650 个 Python 源文件、632 个测试文件；sourcemap 含两套 Python 历史快照（各 55 模块，共 110 HTML）和一套 36 模块 reference 快照。
- 未发现新增第二 Agent Loop、第二 permission engine 或 surface 自有 tool scheduler。
- 当前模块表多数仍为 INVENTORY_COMPLETE/UNVERIFIED，只有 query/permissions/tool_system 进入 MAPPING_VERIFYING；因此“目录齐全”不能解释为“行为 complete”。

## 6. 警告与异常分类

首轮 12 warnings 中，8 条来自 BUG-01，已修复。剩余需后续处理：

1. Starlette TestClient/httpx 弃用警告；
2. `HookSource.SETTINGS` 两处弃用警告；
3. Advisor/Pydantic serializer 类型不匹配警告。

这些警告未导致本轮失败，但均应进入后续兼容性清理，尤其 serializer warning 需要确认线上 payload 是否可能偏离 schema。

## 7. main 提交准备判定

允许准备提交的范围：Wave 4/5 新测试、进展记录、测试可信度修复、sourcemap/docs 治理修复、README 安装修复和本报告。

提交前检查已满足：最终全量复跑通过、docs governance 通过、`git diff --check` 通过；SHA256SUMS 在本报告定稿后更新并复核。合并到 main 后仍应保留 §18 `NOT PASSED`，不得把“本轮测试通过”改写成“7×5×14 complete”。
