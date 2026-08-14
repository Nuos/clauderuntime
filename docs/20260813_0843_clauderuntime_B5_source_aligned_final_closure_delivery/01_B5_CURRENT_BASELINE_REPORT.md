# ClaudeRuntime B5 前置基线报告：B4 完成声明后的独立 Source-Aligned 审计

> 文档编号：`CR-B5-BASELINE-2026-08-13`  
> 审计时间：2026-08-13 08:43（UTC-07:00）  
> ClaudeRuntime `main` HEAD：`95efbaec4796147657668c4947a0d2088ecc4738`  
> B4 功能提交：`eff80250b0603a8305660e9f2c88d77d5e73b547`  
> Claude Code recovered source：`2.1.88` @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：`Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems`，arXiv:2604.14228v2  
> 上一最高约束：`CR-SOURCE-ALIGNED-RULE-BIBLE-v5.0`  
> 本报告定位：**B5 的事实基线，不接受“代码存在/测试多/文档写完成”作为 Source-Aligned 完成证据。**

---

# 0. 执行摘要

本次重新读取最新 GitHub 主分支、B4 进度、B4 机器证据、关键 Python 实现以及 Claude Code 2.1.88 recovered source 后，结论如下：

> **B4 的 C2–C5 确实完成了大量有效开发并显著提高了项目质量，但“B4 开发计划已全部完成”这一表述不被当前仓库事实支持。**

当前主分支自身仍明确记录：

- C2：Verified；
- C3：Verified（但本次独立复核发现其中至少两项 Source-Aligned 结论需要降级重审）；
- C4：Verified（Scheduler 的 source differential 仍需补强）；
- C5：Verified（当前跨 Surface 的真实 differential 只覆盖 core/server 代表路径，不能等价为全部支持 Surface）；
- C1：In Progress，仅 macOS Seatbelt 已实现；Linux、Windows 真实隔离未完成；
- C6：In Progress；
- 最新仓库记录的全量本地测试：`10144 passed, 10 skipped, 0 failed, 345 subtests`；
- GitHub connector 对当前 HEAD 没有返回 combined status / workflow run，因此不能宣称“当前 HEAD GitHub CI 已绿”。

更重要的是，**B4 的机器证据彼此已经发生矛盾**：

- `scorecards/latest.yaml`：Exit Gate = `NOT_READY`；
- `coverage-ledger.yaml`：R7 只有 3/7 VERIFIED，R5 3/5，CCR 9/14；
- `reference-callgraph-map.yaml` 仍把 Resume 标成 BLOCKED，且仍指向旧的 `register_async_agent` 终点；
- `reference-state-transition-map.yaml` 仍把 Resume、Streaming Tool、Scheduler 标成 PARTIAL/BLOCKED；
- `reference-runtime-trace-map.yaml` 却把 Resume、Scheduler、Cross-Surface 标成 VERIFIED；
- 多数机器文件的 `baseline_commit` 仍是 B3 的 `4a77f...`，不是当前 HEAD。

因此当前最准确的状态不是“B4 完成”，而是：

> **核心运行时已接近高成熟度，但 Source-Aligned 证明体系尚未收口，而且 Compact-5、Context-9、Resume、Scheduler、Cross-Surface、Isolation 中仍存在被 B4 过早标记 VERIFIED 的项目。**

---

# 1. 本次审计事实源与优先级

本报告按以下证据优先级判定：

1. Claude Code 2.1.88 recovered source 的实际文件/symbol/call-edge；
2. 论文 v2 对 7-component / 5-layer 及运行机制的源码级归纳；
3. ClaudeRuntime 当前 HEAD 的生产代码；
4. 当前 HEAD 的测试；
5. 当前 HEAD 的 machine-readable parity assets；
6. B4 Markdown 进度/声明；
7. 工程推断。

发生冲突时：**源代码 > 测试实际断言 > 机器证据 > 进度文档 > 完成声明。**

Recovered source 是对公开 sourcemap 的还原研究材料，不等同于 Anthropic 内部 Git 仓库；项目只对其“可确认行为”负责。

---

# 2. 最新仓库状态冻结

## 2.1 当前 HEAD

```text
95efbaec4796147657668c4947a0d2088ecc4738
docs: 更新 B4 GitHub 发布状态
```

其前一个功能提交：

```text
eff80250b0603a8305660e9f2c88d77d5e73b547
feat: 完成 B4 C2-C5 闭环与验证
```

B4 功能提交相对 B3 基线新增/修改的关键生产文件包括：

- `src/agent/resume_agent.py`
- `src/execution/sandbox.py`
- `src/hooks/hook_executor.py`
- `src/services/mcp/connection_manager.py`
- `src/settings/types.py`
- `src/tasks/local_agent.py`
- `src/tool_system/tools/bash/background.py`
- `src/tool_system/tools/bash/bash_tool.py`
- `src/tool_system/tools/send_message.py`

同时新增了 callgraph/runtime/state/divergence/scorecard 等 parity 资产。

## 2.2 项目自报验证

B4 最新进度记录：

```text
C2: 42 + 244 passed
C3: 283 passed
C4: 291 passed
C5: 205 passed
Full project: 10144 passed, 10 skipped, 0 failed, 345 subtests
```

这是非常强的工程回归证据，但仍只是本地记录；当前 GitHub API 没有返回当前 HEAD workflow/status。

---

# 3. 独立完成度评分

以下为本次审计的**人工工程估计**，不作为自动 scorecard：

| 维度 | 估计 | 解释 |
|---|---:|---|
| 一般工程成熟度 | **93/100** | 模块化、测试规模、故障处理、文档治理已很高 |
| 7×5×14 主体实现度 | **90/100** | 绝大多数机制已经真实存在 |
| 关键行为与 2.1.88 语义一致度 | **78/100** | 多处接近，但 Compact/Context/Scheduler/Resume/Isolation 尚有实质差异 |
| Source-level 证据完整度 | **62/100** | 机器映射有明显滞后和相互矛盾 |
| Safety / State / Failure 证明成熟度 | **82/100** | Permission/Tools/Hook 很强；Isolation/跨进程恢复仍拖累 |
| **严格 Final Exit Gate readiness** | **72/100** | 不能宣告 7/7 + 5/5 + 14/14 complete |

关键点：B4 比 B3 的**实现质量明显提升**，但本次发现若干“原先被 VERIFIED、实际仍不满足 source-aligned”的问题，因此严格 Exit readiness 没有按测试数量同比上升。

---

# 4. 7 个核心功能组件重新评估

| ID | 组件 | 实现度 | 证据度 | 独立判定 | 核心问题 |
|---|---|---:|---:|---|---|
| R7-01 | User | 92% | 72% | PARTIAL | core/server 对比已做，但全 Surface 用户动作等价尚未证明 |
| R7-02 | Interfaces | 93% | 70% | PARTIAL | shared core 方向正确；CLI/TUI/Desktop/IDE 全入口 runtime differential 不全 |
| R7-03 | Agent Loop | 95% | 80% | STRONG_PARTIAL | 单一 reactive loop 很成熟；机器 callgraph 仍 PARTIAL |
| R7-04 | Permission System | 97% | 86% | STRONG_PARTIAL | deny-first 等核心很强；机器映射与 trust 全向量还没 final |
| R7-05 | Tools | 97% | 85% | STRONG_PARTIAL | orchestration/result 很强；CCR-06/09 机器证据仍 PARTIAL |
| R7-06 | State & Persistence | 90% | 70% | STRONG_PARTIAL | 同进程 background resume 已真重入；跨进程 durable reconstruction、fork/rewind/crash closure 不足 |
| R7-07 | Execution Environment | 76% | 58% | **BLOCKED** | macOS 有真实隔离；Linux/Windows 无真实 backend，domain allowlist 等不全 |

严格 Closure：**0 项建议在 B5 起点直接视作不可复审的“最终完成”**。R7-04/R7-05 很接近，但仍应通过 B5 Final Evidence Gate 后再升级。

---

# 5. 五层架构重新评估

本报告使用论文/B4 v5 的五层架构，而不是旧 `docs/parity/README.md` 中的“5 Parity Layers”。

| ID | 五层架构 | 实现度 | 证据度 | 判定 |
|---|---|---:|---:|---|
| R5-01 | Surface Layer | 92% | 70% | PARTIAL |
| R5-02 | Core Layer | 91% | 68% | PARTIAL — Compact-5 source differential 有错误完成声明 |
| R5-03 | Safety / Action Layer | 94% | 79% | STRONG_PARTIAL |
| R5-04 | State Layer | 89% | 68% | PARTIAL — durable resume/fork/rewind/context lazy rules |
| R5-05 | Backend Layer | 78% | 58% | **BLOCKED — cross-platform isolation** |

---

# 6. CCR-14 横切机制重新评估

| CCR | 机制 | 实现度 | 证据度 | 独立判定 | B5 重点 |
|---|---|---:|---:|---|---|
| CCR-01 | Hook Runtime | 94% | 84% | STRONG_PARTIAL | 事件全量 owner/call-edge finalization |
| CCR-02 | Authorization Pipeline | 97% | 84% | STRONG_PARTIAL | 补全 decision vector + machine map |
| CCR-03 | Context Shaping | 78% | 58% | **PARTIAL / 需降级** | Snip stub、early-exit 非 reference、microcompact 完整 gate |
| CCR-04 | Context Assembly | 80% | 58% | **PARTIAL / 需降级** | path-scoped rules 被错误映射为 permission context，生产 lazy wiring 疑似缺失 |
| CCR-05 | Capability Assembly | 96% | 84% | STRONG_PARTIAL | MCP identity/lifecycle final map |
| CCR-06 | Tool Orchestration | 96% | 80% | STRONG_PARTIAL | 当前 coverage ledger 仍 PARTIAL |
| CCR-07 | Streaming Tool Execution | 94% | 82% | STRONG_PARTIAL | machine state map 仍旧值 |
| CCR-08 | Recovery / Resilience | 95% | 83% | STRONG_PARTIAL | 完整错误族+跨 surface terminal consistency |
| CCR-09 | Result Processing | 94% | 78% | STRONG_PARTIAL | externalization/reconstruction final map |
| CCR-10 | Session / Transcript | 89% | 67% | PARTIAL | durable resume/fork/rewind/crash consistency |
| CCR-11 | Subagent Orchestration | 91% | 73% | STRONG_PARTIAL | resume reconstruction、summary/worktree/source lifecycle |
| CCR-12 | Isolation Runtime | 70% | 52% | **BLOCKED** | Linux/Windows + full policy translation |
| CCR-13 | Trust Lifecycle | 96% | 80% | STRONG_PARTIAL | current ledger 仍 PARTIAL，需全 scope vector |
| CCR-14 | Runtime Config / Feature Gate | 88% | 68% | PARTIAL | Scheduler source semantics、feature gates、active taxonomy |

---

# 7. 本次发现的高优先级问题

## P0-01：B4 并未全部完成，C1/C6 仍公开 In Progress

这不是评价问题，而是仓库自身状态。最新进度与最新 docs commit 均明确：Linux/Windows 真实隔离及最终 C6 尚未完成。

**处理**：B5 不接受“B4 overall complete”为事实，只把 C2–C5 的完成工作作为已交付增量。

## P0-02：机器证据发生“同一事实多种状态”

当前至少存在四类冲突：

1. Resume：runtime trace = VERIFIED；callgraph/state map = BLOCKED；
2. Scheduler：runtime trace = VERIFIED；state map = PARTIAL；
3. Cross-Surface：runtime trace = VERIFIED；state map仍说差分证据缺失；
4. 所有机器文件 baseline 多数仍固定 `4a77f...`，而当前 HEAD 已是 `95efbaec...`。

这意味着 `VERIFIED` 已无法由单一控制面可靠解释。

**处理**：B5 A0 首先重建 machine evidence atomically；任何文件不一致，scorecard 必须失败。

## P0-03：Compact-5 的 B4 VERIFIED 结论存在实质性 Source Drift

Claude Code 2.1.88 `query.ts` 的实际顺序是：

```text
applyToolResultBudget
→ HISTORY_SNIP gate 下 snipCompactIfNeeded
→ microcompactMessages（每轮调用，内部自行决定 no-op / time-based / cached path）
→ CONTEXT_COLLAPSE gate
→ autocompact
```

当前 Python `CompressionPipeline`：

- 自定义 `early_exit_tokens=20_000`；早层保存足够 token 时**直接 return，跳过后续 shaper**；
- `snip_compact()` 是固定 no-op stub；
- `microcompact` 在 pipeline 外层由 `mc_enabled=False` 默认完全不调用；
- parity test 的“early exit=true”来源于项目自写 `ts_compression_layers.json`，不是直接 reference symbol/trace。

这与 2.1.88 `query.ts` 的 source-observable control flow 不完全一致。

**判定**：CCR-03/R5-02 必须从 VERIFIED 降为 PARTIAL，重新实现或登记清晰 divergence。

## P0-04：Context-9 的 `path_rules` 被分类错位

当前 `context-9-matrix.yaml` 把：

```text
path_rules → src/permissions → insertion: permission_context
```

但论文和 recovered source 里的 Path-scoped Rules 指 `.claude/rules/*.md` 的**上下文指令**，会根据路径/目录进行 lazy load，不是 permission rule。

当前 `clawcodex_md.py` 确实能解析 `paths:` frontmatter，也有 `conditional_rule` 参数；但生产 `get_memory_files()` 只看到 `conditional_rule=False` 的调用。代码搜索未发现生产路径调用 `conditional_rule=True`。

**风险**：B4 的 Context-9 “VERIFIED” 可能掩盖了一个真实的 lazy path-rule 缺失。

**判定**：CCR-04/R5-04 降为 PARTIAL，B5 必须做真实 file-read→rules-load→context injection E2E。

## P0-05：Resume 真重入已改善，但依赖“内存 recipe”，不等同于 durable reconstruction

当前 Python 已做到：

```text
terminal → race-safe claim
→ transcript hydrate
→ copy resume_run_params
→ canonical run_agent
→ transcript/terminal/notification
```

这是 B4 的真实成果。

但 `LocalAgentTaskState.resume_run_params` 明确标注：**不持久化**。服务进程重启后依赖丢失，Python 会明确失败并要求 spawn fresh agent。

Reference `resumeAgentBackground()` 则从磁盘 transcript + metadata + 当前 ToolUseContext 重新构建：

- 过滤 whitespace/orphan thinking/unresolved tool uses；
- reconstruct content replacements；
- 恢复/验证 worktree；
- 从当前 active agent definitions 重选 agent；
- 重建 permission context / tool pool / system prompt；
- 再进入 `runAgent`。

因此 Python 当前只实现了**same-process true resume**，未完全实现 reference 的 durable rehydration。

**判定**：R7-06 / CCR-10 / CCR-11 不能作为最终 closure。

## P0-06：Real Sandbox 只有 macOS 子集

当前实现已经比 B3 强很多：

- `run_process_tree()`：process group + TERM→0.5s→KILL；
- macOS `sandbox-exec` 真实 capability probe；
- default-deny Seatbelt；
- write scope、explicit read/write deny；
- default network deny / allowAll；
- foreground/background Bash 均接入。

但当前：

- Linux/Windows 默认仍 `NoSandboxBackend`；
- `allowed_network_hosts` 只是数据，没有执行；
- Seatbelt 默认 `(allow file-read*)`，与 reference 的完整 read restriction 语义仍有差距；
- reference 还有 settings 文件、managed drop-in、`.claude/skills`、bare-git escape 等保护逻辑；
- reference network config 还包括 allowed/denied domains、Unix sockets/local binding/proxy 等；
- 没有 native Linux/Windows platform CI 证据。

**判定**：R7-07 / R5-05 / CCR-12 继续 BLOCKED。

## P1-01：Scheduler 功能很强，但与 reference scheduler 的 durable/file-backed lifecycle 不完全同构

Python `SessionCronScheduler` 已实现：50 job cap、7-day expiry、no catch-up、jitter、wakeup、snapshot/restore、thread safety。

Reference `cronScheduler.ts` 还包含：

- `.claude/scheduled_tasks.json` file-backed tasks；
- filesystem watch；
- scheduler lock/owner takeover；
- session task vs file task 两条路径；
- missed one-shot handling；
- `lastFiredAt` persistence；
- daemon/filter/killswitch semantics。

B5 应分别判定哪些是 2.1.88 source-aligned core、哪些属于 Python product adaptation，禁止只凭“功能更丰富”直接 VERIFIED。

## P1-02：Cross-Surface 只证明 core ↔ server，不是“所有支持 Surface”

新增 E2E 使用 deterministic provider 对比：

```text
run_query_as_agent_loop
vs
DirectConnectServer
```

比较 response/terminal/usage/turn count。这是有效的 differential，但没有直接执行 TUI、Desktop、VSCode/IDE adapter 的同一 scripted action。

**判定**：R7-01/R7-02/R5-01 仍需 final surface matrix。

## P1-03：旧治理文档仍在传播第二套 5层/14循环 taxonomy

`docs/status/current.md` 与 `docs/parity/README.md`：

- last_verified 仍是 2026-08-11；
- commit 仍是旧值；
- 使用旧 “5 Parity Layers”；
- 使用 legacy AUX-01..AUX-14 编号。

B4 v5 已明确正式分类是 Reference-7 + Reference-5 + CCR-14。因此当前仓库仍存在双重“官方词汇”。

**处理**：B5 v6 必须只保留一个 active constitution，旧体系标为 LEGACY_MAPPING，不得再作为完成计分口径。

## P1-04：缺当前 HEAD 的独立 CI 证明

GitHub connector 没有返回当前 HEAD 的 combined status 或 workflow runs；仓库根目录也未发现 `.github/workflows` 路径。

**处理**：B5 Final Exit 必须把 native Linux/macOS/Windows CI 与核心 parity suite 作为 required evidence；没有 CI 证据时只能说“local green”。

---

# 8. 与论文架构的一致与不一致

## 已高度一致

- 单一 reactive Agent Loop，而非 DAG planner；
- model reasons / harness enforces；
- deny-first + human escalation；
- Permission 与 Sandbox 分离；
- Tool Registry / Pool / Orchestration / Execution / Result 分层；
- append-oriented transcript；
- subagent sidechain；
- context 作为绑定资源；
- MCP/Skills/Hooks 等 composable extensions；
- resume 不恢复 session temporary trust。

## 尚未严格一致

- Compact-5 的 feature gate / call semantics；
- Path-scoped instruction lazy loading；
- Cross-process subagent resume rehydration；
- Scheduler durable/file-backed lifecycle；
- Cross-platform real sandbox；
- 全 Surface shared-loop differential；
- current-HEAD machine evidence 原子一致性。

---

# 9. B5 冻结基线

B5 的唯一目标：

```text
7/7 Reference-7
5/5 Reference-5
14/14 CCR-14
+ lifecycle obligations
+ current-head machine evidence
+ native platform tests
```

全部满足：

```text
EXACT | SEMANTIC_EQUIVALENT | PYTHON_ADAPTATION_VERIFIED
```

并且：

```text
critical UNKNOWN = 0
critical PARTIAL = 0
critical MISSING = 0
critical undocumented divergence = 0
cross-file evidence contradiction = 0
```

在此之前，外围研发继续延期。
