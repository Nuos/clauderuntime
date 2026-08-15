# ClaudeRuntime B6 完成态评估校验与审核报告

> 文档编号：`CR-AUDIT-B6-20260814`  
> 审核对象：`Nuos/clauderuntime`  
> 审核基线：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code `2.1.88` recovered source @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*, arXiv:2604.14228v2  
> 审核结论：**B6 功能核心有条件通过；Source-Aligned 不通过且不应继续作为 B6 完成口径；进入 B7 前必须先修正文档真值与证据基线。**

---

## 0. 结论摘要

本次审核不是只检查“有没有功能”，而是同时检查四条轴：

1. **Reference 架构轴**：是否覆盖论文与 Claude Code 2.1.88 source 所揭示的关键架构机制；
2. **行为轴**：Python 实现是否真正进入主运行链，而非存在于孤立模块；
3. **安全轴**：Permission、执行隔离、trust lifecycle、resume 等是否维持硬不变量；
4. **证据轴**：项目状态、差异台账、CI、scorecard、README 是否描述同一个事实。

审核后的建议状态为：

| 维度 | 结论 | 说明 |
|---|---|---|
| B6 功能核心 | **PASS** | Agent Loop、Permission、Tools、Context/Compact、MCP、Hooks、Resume、Scheduler、Surface smoke 主体已经闭合 |
| Claude Code 2.1.88 功能相似性 | **PASS WITH KNOWN DIVERGENCES** | 采用 Python-native adaptation，且大部分关键差异已有记录 |
| Source-Aligned / 1:1 parity | **NOT READY** | 旧机器 scorecard 仍为 NOT_READY；且 B6 已主动放弃逐控制流严格 parity 作为完成口径 |
| 安全基线 | **PASS WITH PLATFORM LIMITS** | deny-first、workspace boundary、pre-trust hook gate、resume trust reset 较强；Windows/Linux 实隔离仍未真机闭合 |
| CI / Release evidence | **CONDITIONAL PASS** | 主分支文档记录 CI 全绿，但 workflow 对 5 个测试做了显式 deselect，且未形成 Windows/Linux 真实 platform gate |
| 文档治理 | **FAIL / MUST FIX FIRST** | `current.md`、scorecard、registry、README、active plan 使用了不同 HEAD/状态口径，当前 SSOT 不唯一 |

**总体判定：`B6_FUNCTIONALLY_SIMILAR_CORE_COMPLETE` 可以保留，但必须追加限定：`DOCUMENTATION_EVIDENCE_REBASE_REQUIRED`。**

---

# 一、证据基线与方法

## 1.1 Reference 不是“Anthropic 官方开源仓库”

当前对照源码是从公开 Claude Code source map 恢复出的 `2.1.88` TypeScript 快照。项目自身已经把 Reference 锁到：

```text
version: 2.1.88
commit: a8a678cb6244e6770e1e421767ff0987a1d95549
```

这与论文分析快照一致。后续文档应统一使用“recovered source / source-map recovered snapshot”措辞，避免写成“官方开源源码”。

## 1.2 本次直接抽查的关键证据

Reference：

- `restored-src/src/query.ts`：主 query loop、五层 context shaping 的实际调用次序；
- `restored-src/src/utils/permissions/permissions.ts`：Permission 决策、dontAsk、auto mode、safety-check 的约束；
- `restored-src/src/tools.ts`：tool pool 与 deny prefilter；
- 论文 Sections 3–9：7 组件、5 层、Agent Loop、Permission、Extensibility、Context、Subagent、Persistence。

ClaudeRuntime：

- `src/query/query.py`；
- `src/services/compact/pipeline.py`；
- `src/permissions/check.py`；
- `src/tool_system/context.py`；
- `src/entrypoints/headless.py`；
- `docs/reference-differences/registry.yaml`；
- `docs/status/current.md`；
- `docs/parity/scorecards/latest.yaml`；
- `.github/workflows/ci.yml`；
- B6 验收文档与 PR #3 合并记录。

## 1.3 证据等级

本报告把结论分为：

- **V1 — 源码直接确认**：从 ClaudeRuntime 当前 HEAD 或 Reference 源码直接可见；
- **V2 — 项目机器/测试记录**：仓库文档记录的 test/CI 结果，但本次未在本机重跑；
- **V3 — 工程推断**：依据架构与代码关系推导，需后续运行验证闭合。

本报告不会把 V2 写成“本次独立复现”。

---

# 二、与论文 7 个核心组件的对照审核

## 2.1 User — `FUNCTIONAL_ADAPTATION`

论文把 User 视为权限确认、interrupt、review 的最终权威。ClaudeRuntime 已有 permission request/reply、interrupt/abort、plan/ask、session surface。用户权威的基本控制面存在。

**问题**：不同 surface 的行为并未完全证明为同一 typed contract，B6 改为 smoke compatibility，这在功能相似口径可接受，但不能再写为 full parity。

审核：**通过，保留 adaptation 标签。**

## 2.2 Interfaces — `FUNCTIONAL_ADAPTATION`

存在 CLI/headless、TUI、server/desktop gateway 等入口，并且主路径已逐步收敛到 canonical query loop。B6 surface smoke 是正确方向。

**差异**：Reference 的 Interactive CLI / Headless / SDK / IDE 共享 `query()`，而 Python 仍保留 adapter、compat wrapper、server gateway 等额外层；这属于 Python/runtime surface adaptation，不构成功能缺失。

审核：**通过，但 B7 要把“共享同一 core”变成自动 contract test，而非文档声明。**

## 2.3 Agent Loop — `FUNCTIONAL_COMPLETE`（强项）

Reference `query.ts` 的核心结构是：

```text
messages after compact boundary
→ tool-result budget
→ snip
→ microcompact
→ context collapse
→ autocompact
→ model
→ tool dispatch
→ permission
→ tool result
→ continue/stop
```

ClaudeRuntime `src/query/query.py` 已具备 async generator、stream event、tool round、recovery、abort、budget、fallback、compaction pipeline 等机制。这里不是简单“有 while loop”，而是已经形成生产 harness。

审核：**强通过。**

建议下一阶段不要继续向 `query.py` 叠功能，应“拆职责、不改控制语义”，否则会形成 God Module 风险。

## 2.4 Permission System — `FUNCTIONAL_COMPLETE`，但存在两个重要治理/默认值风险

`src/permissions/check.py` 直接体现：

- deny rule 优先；
- deny content 再于 ask；
- ask 再于 allow；
- dontAsk 将 ask 转 deny；
- auto classifier 不可在 classifier unavailable 时静默 allow；
- headless 无 prompt 时 fail-closed。

这与论文的 deny-first、human escalation、defense-in-depth 高度一致。

但存在两个必须进入 B7 的问题：

### A. `ToolContext` 构造默认是 `bypassPermissions`

`src/tool_system/context.py` 的默认 factory 使用：

```python
ToolPermissionContext(mode="bypassPermissions")
```

生产 headless 路径随后显式通过 `setup_permissions(... mode=effective_mode)` 覆盖，因此**不能据此断言当前 headless 默认绕过权限**；实际 headless 的 `HeadlessOptions.permission_mode` 为 `default`，且构造时传入 `_perm_setup.context`。

但是，从“安全构造原则”看，核心安全上下文默认值不应是最高权限。任何未来新入口、测试辅助路径或第三方调用忘记显式传值，就会得到 permissive default。

审核建议：**P0：把 `ToolContext` 改为 fail-safe default（`default` / 明确要求传入），bypass 必须只能由显式用户动作构造。**

### B. 已知 permission UX divergence 未全部进入 registry

`src/permissions/check.py` 明确写了 `DELIBERATE UX DIVERGENCE`：例如 WebSearch、AskUserQuestion、SendUserMessage、StructuredOutput 的 gating 与 Reference 不完全一致。当前 `registry.yaml` 的 `DIFF-PERM-001` 主要描述 classifier internals，不能覆盖所有这些用户可见策略差异。

这违反 B6 Bible 自己规定的“双重登记：代码附近 + global registry”。

审核建议：**P0：把每个“Reference 明确不同”的 permission default/gating 差异登记成独立 DIFF 项。**

## 2.5 Tools — `FUNCTIONAL_COMPLETE`

工具 registry、tool schema、permission check、result normalization、streaming executor、MCP namespace、Read/Edit/Bash/Grep/Glob 等核心 coding tool 已成熟。

强项是 Tool 与 Permission/Execution 已经不再只是同一层逻辑：workspace guard、execution boundary、sandbox prepare 分离，符合论文“reasoning 与 enforcement 分离”的核心思想。

审核：**通过。**

后续优先级应从“继续加工具数量”转为 tool descriptor 单一真值、side-effect 属性、并发属性、sandbox requirement 与结果预算一致性。

## 2.6 State & Persistence — `FUNCTIONAL_ADAPTATION`

项目已覆盖 transcript、session、resume、background/subagent state、scheduler file-backed persistence；B6 还加入“真实双进程 resume smoke”。

与 Reference 的 mostly append-only JSONL、resume/fork、session trust reset 的方向一致。

保留 adaptation 的原因是：

- content replacement / worktree auto-recovery 等 Reference 细节未全部复刻；
- scheduler durable lifecycle 是 Python-native；
- current machine scorecard 尚未重新生成到当前 HEAD。

审核：**功能通过，证据再基线化后再提高状态。**

## 2.7 Execution Environment — `LIMITED`

macOS、Linux bubblewrap、Windows Job Object 代码路径已存在；fail-closed contract 也被明确写入。

但平台 ledger 明确：

- Linux `PENDING_REAL_DEVICE`；
- Windows `PENDING_REAL_DEVICE`；
- 当前受管 macOS 终端对 Seatbelt probe 为 `BLOCKED`。

这意味着“代码存在”不能升级为“跨平台隔离已验证”。论文把 sandbox/permission 当成独立安全层，因此这不是普通兼容性小问题，而是 release safety gate。

审核：**LIMITED，不能在 B7 前改写为 verified。**

---

# 三、论文 5 层架构审核

| Reference Layer | ClaudeRuntime 对应 | 审核 |
|---|---|---|
| Surface | CLI/headless/TUI/server/desktop | **通过，Functional Adaptation** |
| Core | `src/query/` + compact pipeline | **强通过** |
| Safety / Action | permissions/hooks/tools/MCP/sandbox/subagent | **通过，但需修安全默认值与 diff registry** |
| State | context/session/transcript/memory/resume | **通过，Functional Adaptation** |
| Backend | filesystem/process/network/MCP transports/sandbox | **部分通过，跨平台验证未闭合** |

这个结果与 B6 自己“5 层稳定 Python owner”的目标总体一致。

---

# 四、五层 Context Compaction 校验

这是本项目目前与 Reference 对齐较好的部分之一。

Reference `query.ts` 直接确认五阶段：

1. `applyToolResultBudget`；
2. `snipCompactIfNeeded`；
3. `microcompact`；
4. `contextCollapse.applyCollapsesIfNeeded`；
5. `autocompact`。

ClaudeRuntime `src/services/compact/pipeline.py` 也按同样的**阶段顺序**执行：

```text
Tool Result Budget
→ Snip Compact
→ Microcompact
→ Context Collapse
→ Autocompact
```

而且 B6 对 Snip 未恢复的函数体采取保守 read-only allowlist，没有伪造“Reference 就是同算法”，这个处理符合 R2/R3 证据纪律。

需要修正的地方不是算法本身，而是文档词汇：pipeline.py 仍大量使用 “Source-Aligned mode” 描述，而 B6 已将项目完成口径改为 hierarchical functional alignment。建议 B7 把运行配置名称与项目状态口径解耦，避免 `source_aligned=True` 被误解成全项目 Source-Aligned。

---

# 五、Extensibility、Subagent、Persistence 的专项判断

## 5.1 MCP / Plugins / Skills / Hooks

仓库已有：

- `src/services/mcp/`；
- `src/plugins/`；
- `src/skills/`；
- `src/hooks/`；
- plugin agent loader。

整体形态与论文四类扩展面一致。

更值得肯定的是：`ToolContext` 已有 `workspace_trusted=False` 的默认 trust gate，并对 hook config 做 snapshot/frozen read 思路，意图修正论文讨论过的 pre-trust initialization 风险。

B7 应继续把规则收紧为：**未信任 workspace 时，project-local hook/plugin/MCP 不能产生任何可执行副作用；policy-managed source 另行定义。**

## 5.2 Subagent

项目具备 subagent context、background agent、runtime task registry、agent naming、worktree 相关路径与 summary/sidechain 思路。整体符合“isolated context + delegation”的 Reference 方向。

下一阶段重点不是继续增加 agent 类型，而是验证：

- parent permission ceiling 不被 child 降低；
- background 与 foreground 共用安全边界；
- summary-only/sidechain 不造成 trust/context 污染；
- abort 能杀完整 child process/task tree。

## 5.3 Session / Resume

B6 对“resume 不恢复 API key / 临时权限 / session temporary trust”已经明确写成硬约束，并有白名单 metadata 思路。这一点与论文 Section 9 “resume/fork 不恢复 session-scoped permissions”一致，是正确的安全选择。

---

# 六、发现的问题与整改优先级

## P0-01：项目当前没有单一事实源（SSOT）

这是本次审核最明确的治理缺陷。

当前同时存在：

- 实际 main HEAD：`16da0cfea98d...`；
- `registry.yaml.repository_head`：`dc7393bb05de...`；
- `scorecards/latest.yaml.subject_commit`：`7619ff288616...`；
- active plan baseline：`241d704480c...`；
- `docs/status/current.md` 一方面写 B6 `FUNCTIONALLY_SIMILAR_CORE_COMPLETE`，另一方面“当前结论”仍写 Reference-7/5/CCR 全部没有 final complete evidence；
- scorecard 仍是 `exit_gate: NOT_READY`。

这些内容不是“历史文件不一样”，而是**都处在 current/active/latest 路径**。

### 整改

B7 第一个 PR 必须只做 truth reset：

```text
actual main HEAD
→ regenerate evidence
→ regenerate scorecard
→ update registry repository_head
→ rewrite docs/status/current.md as dual-axis state
→ active plan supersede/archive
```

建议正式分成两个状态轴：

```text
functional_status: FUNCTIONALLY_SIMILAR_CORE_COMPLETE
reference_parity_status: PARTIAL / NOT_READY
```

禁止再把两个状态写进同一个模糊字段。

## P0-02：Permission 核心对象的默认构造过于宽松

`ToolContext.permission_context` 默认 `bypassPermissions`。即使主生产入口会覆盖，这仍是一个 unsafe constructor default。

### 整改

- 默认 `default`，或移除默认值强制显式传入；
- 任何 bypass 必须携带 explicit origin：CLI flag / trusted SDK caller / managed policy；
- 增加测试：`ToolContext(workspace_root=...)` 不能执行需授权副作用工具。

## P0-03：差异 registry 覆盖不完整

代码中已明确存在若干 deliberate divergence，但 registry 只有 7 条，且 `DIFF-PERM-001` 不能代表所有 permission UX default 差异。

### 整改

建立自动审计：扫描 `REF-DIFF` / `DELIBERATE ... DIVERGENCE` / `UNKNOWN_REFERENCE` 标签，要求每个核心模块 annotation 对应 registry ID。

## P0-04：CI quarantine 事实有数字漂移

B6 completion 文档中多处写“排除 4 项 CI 环境特定用例”，但当前 `.github/workflows/ci.yml` 实际显式 `--deselect` **5 个测试**：

- stream watchdog 2；
- ch04 watchdog 2；
- opencode compat 1。

这说明治理文档与 executable gate 再次发生 drift。

### 整改

不要把 deselect 列表写散在 workflow 注释和 progress 文档里，改为：

```yaml
ci_quarantine.yaml
- test_id
- reason
- owner
- introduced_at
- expires_at
- local_status
- ci_status
- unblock_condition
```

workflow 由脚本读取或至少由治理检查比对。

## P1-01：Windows / Linux 隔离没有真机闭合

这是已知且正确披露的问题，但 B7 应将它从“文档欠项”升级为 CI matrix gate。

## P1-02：项目身份与发布 metadata 漂移

当前仓库是 `Nuos/clauderuntime`，README 使用 `ClaudeRuntime / ClawCodex Runtime`，但 `pyproject.toml` 仍是：

```text
name = clawcodex-cli
Homepage/Repository/Documentation = github.com/agentforce314/clawcodex
```

这会影响包发布、问题追踪、用户理解与供应链 provenance。

### 整改

建议：

- Canonical product name：`ClaudeRuntime`；
- `clawcodex` CLI 名可作为兼容命令暂时保留；
- pyproject URL 改向 `Nuos/clauderuntime`；
- 若 PyPI 名不能改，文档明确“distribution name ≠ project name”。

## P1-03：README 指向旧规范

README 当前仍把 `seven-component-optimization-development-plan.md` 和 `clauderuntime-source-parity-action-bible-v1.0.md` 写成“当前开发规范”，而 B6 已声明 v1.1 hierarchical bible 为最高约束。

### 整改

README 只指向 canonical：

```text
docs/baseline/PROJECT_BASELINE.md
docs/governance/BEHAVIOR_BIBLE.md
docs/plans/active/CURRENT_PLAN.md
docs/status/current.md
```

历史交付包只作为 archive/reference，不再作为入口。

## P1-04：Python 支持矩阵与 CI 验证矩阵不一致

`pyproject.toml` 声明 Python `>=3.10`，classifiers 覆盖 3.10–3.14；当前核心 CI 只跑 3.12。

这不是说 3.10/3.11/3.13/3.14 一定有 bug，而是**声明支持 ≠ 证据支持**。

B7 建议：

- 3.12：完整 non-integration suite；
- 3.10 + 3.14：core smoke + import/install + critical permission/context suite；
- Linux/Windows/macOS：各至少一条 execution boundary smoke。

## P1-05：Reference generation 缺少统一 lockfile

虽然文档反复写 `2.1.88 @ a8a678c...`，但没有一个单独不可歧义的 `reference-lock.yaml` 来锁：

- source repo URL；
- source commit；
- version；
- paper arXiv version；
- evidence generation script version；
- ClaudeRuntime subject commit。

B7 应增加该文件，后续 Reference 升级必须新建 generation，而不是原地覆盖。

## P2-01：观测很多，但正式 eval 层仍不足

论文 Future Directions 对“silent failure / observability-evaluation gap”强调很强。ClaudeRuntime 目前 trace、tests、parity assets 很丰富，但没有把“任务是否真正完成”作为统一 verifier contract。

B7 应从“trace 可见”升级为：

```text
Task Contract
→ Execution Trace
→ Verifier
→ Evidence Artifact
→ Completion Decision
```

模型不能仅凭自然语言说“完成”就进入 success。

---

# 七、与论文 13 项设计原则的总体评价

| 原则 | 当前判断 |
|---|---|
| Deny-first with human escalation | **较强**，但构造默认值需收紧 |
| Graduated trust spectrum | **已覆盖** |
| Defense in depth | **较强**，permission + workspace + sandbox + hooks |
| Externalized programmable policy | **已覆盖** |
| Context as scarce resource | **强**，五层 pipeline 已进入主链 |
| Append-only durable state | **基本覆盖**，细节 adaptation |
| Minimal scaffolding / maximal harness | **高度一致** |
| Values over rules + deterministic guardrails | **基本一致** |
| Composable extensibility | **已覆盖 MCP/plugins/skills/hooks** |
| Reversibility-weighted risk | **部分覆盖**，仍需统一 Tool descriptor |
| Transparent file-based config/memory | **已覆盖** |
| Isolated subagent boundaries | **基本覆盖** |
| Graceful recovery/resilience | **较强**，retry/abort/resume/compaction 均已有 |

---

# 八、最终审核判定

## 8.1 可以确认的结论

可以确认：ClaudeRuntime 已经从“最小 Agent demo”进入了**真实 harness 工程阶段**。其 Agent Loop、Permission、Context、Extensibility、State、Execution 的设计不是表面命名相似，而是已经出现了与 Claude Code 相同的一组核心设计问题与工程回答。

B6 将目标从“机械 source parity”调整为“分级 Reference 对齐 + Python-native adaptation”是合理修正；它避免为了 TypeScript 细节牺牲 Python 可维护性，同时保留了安全和差异透明底线。

## 8.2 不能确认/不能宣称的结论

当前不能宣称：

```text
Claude Code 2.1.88 Source-Aligned
1:1 Compatible
Cross-platform sandbox fully verified
All current evidence points to current HEAD
All known divergences are registered
All supported Python versions are CI-verified
```

## 8.3 B7 准入条件

在开始新增大功能前，建议先满足以下 6 项：

1. `current.md` 消除双重结论；
2. scorecard/evidence/registry 全部 rebase 到当前 main HEAD；
3. Permission 默认构造改 fail-safe；
4. 全量登记已知 deliberate divergence；
5. CI quarantine 数量与列表唯一化；
6. 新 baseline / behavior bible / active plan 成为唯一入口。

完成后再进入 B7 的跨平台安全、eval、长期运行能力开发。

---

# 九、审核后的推荐状态字符串

```yaml
project: ClaudeRuntime
baseline: B7-entry
functional_status: FUNCTIONALLY_SIMILAR_CORE_COMPLETE
reference_alignment: HIERARCHICAL_REFERENCE_ALIGNMENT
reference_parity_status: PARTIAL_NOT_RELEASE_GATE
security_status: PASS_WITH_PLATFORM_LIMITS
evidence_status: REBASE_REQUIRED
platform_status:
  macos: BLOCKED_IN_CURRENT_MANAGED_ENVIRONMENT
  linux: PENDING_REAL_DEVICE
  windows: PENDING_REAL_DEVICE
next_gate: B7_TRUTH_RESET
```
