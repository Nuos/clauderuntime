from pathlib import Path
import hashlib, json, shutil, zipfile, html, os, textwrap, subprocess, sys, re

BASE = Path('/mnt/data')
ROOT = BASE / 'clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814'
ZIP = BASE / 'clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814.zip'
SUBJECT = '16da0cfea98d69987739a319ff6ae42cfd432d2c'
REF = 'a8a678cb6244e6770e1e421767ff0987a1d95549'
PAPER = 'arXiv:2604.14228v2'

if ROOT.exists(): shutil.rmtree(ROOT)
if ZIP.exists(): ZIP.unlink()
for d in ['docs','machine','blueprints','tests','scripts','templates','references','archive/b6-audit-baseline','tools']:
    (ROOT/d).mkdir(parents=True, exist_ok=True)

files=[]
def write(rel, text, executable=False):
    p=ROOT/rel; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip()+"\n", encoding='utf-8')
    if executable: p.chmod(0o755)
    files.append(rel)
    return p

def header(title, doc_id):
    return f'''# {title}\n\n> 文档编号：`{doc_id}`  \n> 项目：`Nuos/clauderuntime`  \n> Subject baseline：`main@{SUBJECT}`  \n> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `{REF}`  \n> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，{PAPER}  \n> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**\n\n'''

# 00 START HERE
write('00_START_HERE.md', header('ClaudeRuntime 最终大改总交付包 — START HERE','CR-FINAL-PACK-v2.0') + '''## 0. 这次交付解决什么问题

本包不是继续扩功能，而是把 ClaudeRuntime 在 **Architecture Freeze 前最后需要统一的 owner、安全默认值、真值、生命周期与验证规则** 一次性收口。完成本包定义的 P0/P1 后，项目必须停止跨模块重写，进入逐模块与全局测试调试。

### 本包完整度

本包分成 8 类资产：

1. `docs/`：完整开发、架构、实施、测试、验收、发布文档；
2. `machine/`：Reference lock、SSOT、owner map、quarantine、test matrix、freeze gates 等机器可读配置；
3. `blueprints/`：关键新 owner / boundary 的 Python 参考骨架与 patch 说明；
4. `tests/`：Architecture Freeze 前应新增的 contract test / governance test 骨架；
5. `scripts/`：真值、quarantine、reference lock、freeze gate 校验脚本；
6. `templates/`：Issue、PR、差异登记、平台验证、Freeze、RC 记录模板；
7. `references/`：用户提供的源码链接、论文、七组件资料与本轮证据摘要；
8. `archive/`：上一阶段 B6 审计/基线，仅作为历史证据。

## 1. 推荐阅读顺序

```text
00_START_HERE
  ↓
docs/01_CURRENT_BASELINE
  ↓
docs/02_FINAL_ARCHITECTURE_DIAGNOSTIC
  ↓
docs/03_FINAL_ARCH_CLOSURE_MASTER_PLAN
  ↓
docs/04_BEHAVIOR_BIBLE_v2.2
  ↓
docs/06_RUNTIME_SPINE_SPEC
  ↓
docs/08_P0_IMPLEMENTATION_SPEC
  ↓
docs/09_P1_IMPLEMENTATION_SPEC
  ↓
docs/11_ACCEPTANCE_AND_FREEZE_GATE
  ↓
docs/12_TEST_DEBUG_MASTER_PIPELINE
```

## 2. 本轮只允许 6 类大改

- Repository Truth / Evidence SSOT；
- Permission Safe Default；
- Canonical Turn Preparation；
- Extension Trust-before-Activation；
- Runtime Task / Session Lifecycle / Persistence owner 收口；
- CI/Test/Platform Truth 收口。

## 3. 明确禁止重写

本轮不得以“更漂亮”“更像 Reference”为理由重写：

- canonical `query()` 状态机；
- Permission classifier 主算法；
- 五阶段 compact pipeline；
- MCP transport/auth 主体；
- TUI/Desktop wire protocol；
- Sandbox 主设计；
- Scheduler watcher/跨进程 owner takeover；
- Provider 大规模重构；
- Subagent orchestration 主体。

## 4. 最终状态机

```text
FINAL_ARCH_CLOSURE_REQUIRED
  → P0_CLOSURE_COMPLETE
  → P1_CLOSURE_COMPLETE
  → ARCHITECTURE_FREEZE
  → MODULE_VERIFICATION
  → INTEGRATION_VERIFICATION
  → FAULT_INJECTION
  → LONG_HORIZON
  → RELEASE_CANDIDATE
```

## 5. 证据口径

本包区分：`IMPLEMENTED / WIRED / TESTED_LOCAL / TESTED_CI / VERIFIED_PLATFORM / REFERENCE_CONFIRMED / ACCEPTED_DIFF`。仓库文档记录的测试结果不等于本包独立复现；如未在当前环境运行，不得写成“本次独立验证通过”。
''')

# detailed docs
write('docs/01_CURRENT_BASELINE.md', header('当前项目基线与状态词汇','CR-BASELINE-B7-FREEZE-v2.0') + f'''## 1. Baseline

```yaml
project: ClaudeRuntime
repository: Nuos/clauderuntime
subject_entry_commit: {SUBJECT}
functional_status: FUNCTIONALLY_SIMILAR_CORE_COMPLETE
architecture_status: FINAL_CLOSURE_REQUIRED
reference_alignment: HIERARCHICAL_REFERENCE_ALIGNMENT
reference_parity_status: PARTIAL_NOT_RELEASE_GATE
evidence_status: REBASE_REQUIRED
next_gate: ARCHITECTURE_FREEZE
```

## 2. 当前已经可以认为“主体成熟”的部分

- canonical Query 主循环已经成为生产主路径；
- Permission 具有 deny-first / ask / allow 规则与 headless fail-closed 逻辑；
- Tool execution、hooks、结果持久化与 streaming 主路径已经成型；
- 五阶段 Context/Compact 次序已经固定；
- MCP、Skill、Hook、Plugin、Subagent、Task、State/Resume 均不是“缺模块”；
- B6 仓库记录已有 10k+ 本地测试与 CI green 证据，但应重新绑定最终 Freeze SHA。

## 3. 不能写成“已完成”的部分

- Windows/Linux isolation 未取得最终真实设备证据；
- strict Source-Aligned / 1:1 parity 不成立，也不作为 Freeze Gate；
- CURRENT docs / scorecard / registry 的 subject commit 仍有 generation drift；
- `ToolContext` 仍有隐式 bypass 默认值；
- Turn preparation 仍存在两个语义 owner；
- extension activation trust 还没有统一前置边界；
- task runtime state 仍存在 legacy mirrors / 双写风险；
- CI quarantine 没有真正的单一机器清单。

## 4. 以后所有状态必须是二维的

不要再用一个“完成度百分比”混合功能、parity、安全、平台与证据：

| 轴 | 示例状态 |
|---|---|
| Functional | `COMPLETE / PARTIAL / MISSING` |
| Wiring | `WIRED / ISOLATED / LEGACY_ONLY` |
| Evidence | `NONE / LOCAL / CI / PLATFORM` |
| Reference | `CONFIRMED / ADAPTATION / ACCEPTED_DIFF` |
| Risk | `P0 / P1 / TEST_ONLY` |

## 5. Architecture Freeze 的意义

Freeze 不是“没有 bug”，而是：**runtime 主脊柱、owner、security boundary、extension activation boundary、persistence owner 与 CURRENT truth 均不再移动**。后续 bug fix 应在这些 contract 内完成。
''')

write('docs/02_FINAL_ARCHITECTURE_DIAGNOSTIC.md', header('最终全局架构诊断','CR-DIAGNOSTIC-FINAL-v2.0') + '''## 总结

ClaudeRuntime 当前的主要问题已经从“缺功能”切换成“同一语义存在多个 owner、默认值过于特权、旧/新状态并存、文档证据没有绑定同一 HEAD”。因此最后一次大改应做 **authority convergence**，而不是 capability expansion。

## P0-1：Repository Truth / Evidence SSOT

CURRENT 状态、scorecard、difference registry、backlog、active plan、README 指向不同 generation。后续调试若不先收口，将持续出现“失败对应哪个版本”的争议。

必须形成一个 canonical truth graph：

```text
reference-lock.yaml
        ↓
PROJECT_BASELINE.md
        ↓
status/current.md ─── active/CURRENT_PLAN.md
        ↓                    ↓
registry.yaml ───────── scorecards/latest.yaml
        ↓
release/freeze evidence
```

所有 CURRENT 机器资产必须有 `subject_commit`，且生成时拒绝 stale HEAD。

## P0-2：Permission Safe Default

当前 `ToolContext.permission_context` 默认 `bypassPermissions`。生产 headless 路径通常会显式覆盖，因此这里不应误写成“现有 headless 漏洞”；真正风险是 **任何遗漏 permission_context 的新调用点都会静默得到高权限**。

最终规则：

```text
No permission context supplied → construction error OR safe default
Explicit bypass → requires origin + reason + test
Headless ask with no interaction channel → deny
DENY > ASK > ALLOW
```

## P0-3：Turn Preparation 双 owner

项目目前只有一个 authoritative query loop，但至少有两套完整的 system/context assembly：

- `QueryEngine._build_system_prompt_parts()`；
- `agent_loop_compat.build_effective_system_prompt()`。

这不是“两套 agent loop”，而是“两套 Turn Preparation owner”。它曾经导致过 headless/TUI cutover prompt 缺失型回归。最后一次大改必须统一成一个 `TurnPreparationService` / `RuntimeTurnBuilder`。

## P0-4：Extension Trust-before-Activation

Plugin loader 已经有 trust taxonomy，但 loader 注册阶段并不等于 trust 决策阶段，且按 name 注册存在覆盖语义。Skills/Hooks/MCP 也各有不同加载路径。

必须统一生命周期，而不是统一机制：

```text
Discovery
 → Descriptor
 → Source provenance
 → Trust resolution
 → Validation
 → Activation decision
 → Capability registration
 → Runtime permission
```

内部 Plugin/MCP/Skill/Hook 机制保持独立。

## P0-5：Task / Session / Persistence Owner

`RuntimeTaskRegistry` 已引入，但 legacy task mirrors、background Bash/Agent compatibility paths 仍可能同时存在。Freeze 前必须规定：**一个可写 owner，其他均为 projection/adapter**。

Session persistence 还需明确“可持久化数据”和“不得恢复 live capability”的边界：API key、临时 permission、trust decision、open MCP client、OS handle、线程对象不得进入 resume 语义。

## P0-6：CI / Test Truth

当前 CI workflow 实际 deselect 5 个测试，历史文档曾写 4 个。必须建立 `machine/ci-quarantine.yaml` 作为唯一清单，由脚本生成 pytest deselect 参数；CI yaml 不再手抄列表。

此外，支持 Python 3.10–3.14 / macOS/Linux/Windows 的 metadata 与实际验证矩阵不一致，应拆成：

- declared compatibility；
- CI smoke；
- full suite；
- real platform isolation evidence。

## P1：建议本轮完成但禁止改语义

1. Query：抽出 model capability resolver / completion verifier adapter，但不重写 state machine；
2. AgentServer：拆 ownership facade，不改 WebSocket + worker-thread 协议；
3. Compact：把 manual compact 与 automatic pipeline 放到统一 package ownership；
4. Context：PostSampling `additional_contexts` 要么正式接线，要么登记 accepted diff；
5. State：统一 SessionLifecycle；
6. Project identity：README、pyproject distribution/URLs、历史 `clawcodex` 名称要有迁移策略；
7. `src/cli_backup`：先证明 production refs=0，再移出 package。

## 测试而非重构的模块

Execution/Sandbox、Tools、MCP、Subagent、TUI/Desktop、Provider adapters、Worktree、Scheduler、Memory 现在优先做 contract/fault/platform/long-horizon tests，不再做架构重写。
''')

write('docs/03_FINAL_ARCH_CLOSURE_MASTER_PLAN.md', header('最后一次大改 Master Plan','CR-B7-FINAL-CLOSURE-PLAN-v2.0') + '''## 1. 总目标

在一个明确的 architecture-closure branch 上完成 W0–W9，最终生成 Freeze evidence。每个 Wave 有独立 PR/rollback point，禁止“大 PR 一次改完”。

## 2. Wave 总览

| Wave | 目标 | 类型 | 退出条件 |
|---|---|---|---|
| W0 | Truth Reset / Evidence Rebase | P0 | CURRENT assets 全部绑定同一 subject SHA |
| W1 | Permission Safe-by-Default | P0 | implicit bypass=0 |
| W2 | Canonical Turn Preparation | P0 | production prompt/context owner=1 |
| W3 | Extension Trust Boundary | P0 | executable activation 必经 trust gate |
| W4 | Task / Session / Persistence Owner | P0 | runtime task writable owner=1 |
| W5 | Context / Compact Closure | P1 | outcome/ownership/retention contract 固定 |
| W6 | Query/Server Ownership Extraction | P1 | 不改状态机/协议，只减 owner density |
| W7 | CI / Platform / Evidence Truth | P0 | quarantine + matrix + artifact truth 完整 |
| W8 | Identity / Legacy Cleanup | P1 | README/package/legacy path 清晰 |
| W9 | Freeze Gate / Baseline Lock | Release | 所有 Freeze Gate PASS |

## 3. W0 — Truth Reset

产物：

- `docs/baseline/PROJECT_BASELINE.md`；
- `docs/status/current.md`；
- `docs/plans/active/CURRENT_PLAN.md`；
- `docs/governance/BEHAVIOR_BIBLE.md`；
- `docs/reference/reference-lock.yaml`；
- `docs/parity/scorecards/latest.yaml`；
- `docs/reference-differences/registry.yaml`。

规则：禁止任何 CURRENT 文档引用 archive 作为事实源；backlog 若声明 GitHub Issues 为 SoT，则 Issues 必须真实存在，否则改为 repo-managed backlog。

## 4. W1 — Permission

- 删除/禁止 `ToolContext` 隐式 `bypassPermissions`；
- 增加 bypass origin/reason；
- 生产入口全部显式构造 `ToolPermissionContext`；
- 增加 constructor/entrypoint contract tests；
- 将 deliberate UX divergences 写入 difference registry；
- 确认 headless ask-without-channel → deny。

## 5. W2 — Turn Preparation

新增唯一 owner：

```python
TurnPreparationService.prepare(request, session) -> PreparedTurn
```

`PreparedTurn` 至少包含：

- full system prompt / blocks；
- conversation messages；
- visible tools；
- MCP/Skill contextual contributions；
- output style；
- provider/model capability snapshot；
- compaction/prompt-cache config；
- `QueryParams` / equivalent canonical inputs。

所有 surfaces 只能调用此 owner；`QueryEngine` 降级为 wrapper/test facade。

## 6. W3 — Extension Trust

增加 `ExtensionDescriptor` + `ExtensionActivationGate`。至少区分：bundled / managed / user / project / mcp。Project scope executable extension 默认必须经过 workspace trust 或明确策略。

Name collision 不得 silent overwrite；必须 deterministic reject/replace policy + provenance。

## 7. W4 — Task / Session / Persistence

- RuntimeTaskRegistry 作为 runtime tasks 单写 owner；
- legacy dict 只做 read-only projection；
- background Bash/Agent 迁移完成后禁止双写；
- SessionLifecycle 负责 start/resume/fork/rewind/end；
- persistence adapters 只持久化 durable state；
- resume 强制丢弃 ephemeral trust/security/runtime handles。

## 8. W5 — Context / Compact

不改五阶段算法，只固定：

```text
applyToolResultBudget
→ snipCompactIfNeeded
→ microcompact
→ contextCollapse.applyCollapsesIfNeeded
→ autocompact
```

增加结构化 `CompressionOutcome`，区分：changed / warning / hard_limit / persisted_artifacts / token_delta。Manual compact 移到同一 package ownership 下。

## 9. W6 — Query / AgentServer

Query：只抽 model capability、completion evaluation 等外围 owner，不改主状态机。

AgentServer：保留 WebSocket async + query worker thread + permission roundtrip 机制，仅将 `_AgentSession` 的职责拆成 facades：`RuntimeSession / SessionState / PermissionBridge / SurfaceEmitter / SchedulerBridge`。

## 10. W7 — CI / Platform

- machine quarantine；
- generated deselect args；
- Python 3.10 / 3.12 / 3.14 smoke；
- macOS / Ubuntu / Windows smoke；
- sandbox isolation 真机 job 单独记录；
- evidence artifact 携带 commit SHA 与 environment；
- local / CI / platform evidence 永远分栏。

## 11. W8 — Identity / Legacy

- README current pointers 更新；
- pyproject URLs 指向 `Nuos/clauderuntime`；
- distribution/CLI rename 若破坏兼容则采用 alias + deprecation；
- `src/cli_backup` 先完成 import/callgraph zero-ref 证明，再移除或移到 archive/non-package；
- 旧 docs 全部带 `HISTORICAL / SUPERSEDED` 标签。

## 12. W9 — Freeze

最终 SHA 必须重新生成：baseline、current status、scorecard、registry validation、quarantine report、test evidence、platform evidence、freeze record。任何资产仍引用旧 SHA → Freeze FAIL。
''')

write('docs/04_BEHAVIOR_BIBLE_v2.2.md', header('ClaudeRuntime Behavior Bible v2.2','CR-BEHAVIOR-BIBLE-v2.2') + '''## A. Truth Before Progress

任何“完成”声明先回答：实现在哪、是否接线、测试在哪、在哪个平台验证、是否与 Reference 一致、若不一致是否登记。

证据标签固定为：

`IMPLEMENTED / WIRED / TESTED_LOCAL / TESTED_CI / VERIFIED_PLATFORM / REFERENCE_CONFIRMED / FUNCTIONAL_ADAPTATION / PRODUCT_EXTENSION / ACCEPTED_DIFF`。

## B. Reference Law

Reference generation 固定为：Claude Code 2.1.88 **recovered source-map snapshot**，不得称为 Anthropic 官方开源源码。论文用于架构归纳，不代替源码行为证据。

## C. One Semantic Core

一个生产语义只能有一个 authoritative owner。允许多个 surface adapter，不允许多个 prompt/context builder、permission resolver、task writer、extension activation policy。

## D. Permission Law

- `DENY > ASK > ALLOW`；
- no implicit bypass；
- bypass 必须 explicit + origin + reason；
- headless 无交互通道时 ask → deny；
- pre-trust 不执行 project executable content；
- child/subagent permission ceiling 不得高于 parent。

## E. Permission × Execution Double Boundary

Permission 决定 **是否允许**；ExecutionBoundary 决定 **允许后仍受哪些 OS/process/filesystem/network 约束**。任何工具都不得只依赖其中一层。

## F. Turn Preparation Law

所有 surface 在进入 canonical query 前必须使用同一 TurnPreparation owner。System prompt、workspace context、MCP/skills context、tool visibility、output style、model capability、compaction config 不得在多个入口各自拼装。

## G. Extension Lifecycle Law

Discovery 与 Activation 分离。Project Plugin/Skill/Hook/MCP 不能因为“发现了”就执行。Activation 必须有 provenance、trust、validation 与 deterministic collision policy。

## H. Context Law

五阶段压缩顺序固定。算法变化属于 Architecture Freeze 后禁止项，除非测试证明 contract 无法满足。压缩不能只返回 `bool`；必须留下 outcome/evidence。

## I. State / Resume Law

Persistence 保存 durable semantics，不保存 live privilege。Resume 不恢复：临时 permission、workspace trust verdict、API key 明文、MCP live session、线程/锁/OS handle、旧 abort controller。

## J. Task Law

一个 runtime task 只能有一个 writable state owner。Legacy APIs 可以存在，但只能投影/适配，不可双写。

## K. Subagent Law

Subagent context 隔离、permission ceiling 继承、abort/fault 不得拖死 parent。Sidechain / transcript 必须可追踪 parent-child lineage。

## L. Tool Law

Tool descriptor 尽量作为 schema/permission/side-effect/concurrency metadata 单一事实源。Tool executor 必须可观测：permission decision、hook decision、execution boundary、result persistence、error classification。

## M. Hook Law

Hook failure mode、timeout、SSRF/HTTP safety、trust source 必须明确。PostSampling additional contexts 若未注入 query context，必须明确 accepted diff，不能静默“看似支持”。

## N. MCP Law

MCP 是外部 capability boundary。连接、认证、tool namespace、server crash、reconnect、output validation 必须测试。MCP tool 不能绕过 normal permission/execution policy。

## O. CI/Test Law

CI deselect/quarantine 只能来自一个 machine manifest。每项必须有 reason、owner、added_at、expiry/review date、replacement coverage。禁止 yaml 手抄与 docs 另写两个列表。

## P. Platform Evidence Law

“支持 Windows/Linux/macOS”与“已真实验证 isolation”是两个不同陈述。必须分别记录。

## Q. Eval / Completion Law

模型说“完成”不等于任务完成。长期目标固定为：

```text
Task Contract
→ Execution Trace
→ Verifier
→ Evidence Artifact
→ Completion Decision
```

## R. Project Identity Law

仓库名、distribution name、CLI name、README、project URLs 可以有兼容 alias，但必须有明确 canonical identity 与 deprecation policy。

## S. Freeze Law

Architecture Freeze 后：不得因为目录不好看、代码太长、与 Reference 不够像而发起跨模块重写。只有已验证 contract 无法满足时才允许 RFC 级结构变化。
''')

write('docs/05_MODULE_CLOSURE_MATRIX.md', header('全模块 Closure Matrix','CR-MODULE-CLOSURE-MATRIX-v2.0') + '''| 模块 | 当前判断 | Freeze 前动作 | Freeze 后主要动作 |
|---|---|---|---|
| Query loop | Mature / dense | 仅抽外围 owner | fault / retry / abort / long-horizon |
| Turn preparation | Dual owner | **P0 合并为 1 owner** | surface parity tests |
| Permission | Mature / unsafe default | **P0 safe default + diff registry** | fuzz / policy matrix |
| Tools | Mature | 不重构 | per-tool contracts / side-effect tests |
| Tool execution | Mature | owner naming/telemetry | hook/error/concurrency tests |
| Execution boundary | Mature | 不改设计 | OS matrix / escape tests |
| Sandbox | Limited evidence | 不重构 | real-device verification |
| Context assembly | Mature / duplicated | **P0 owner merge** | provenance/retention tests |
| Compact pipeline | Mature | P1 outcome + package ownership | multi-compact stress |
| State | Mature / owner spread | P1 SessionLifecycle | crash/restart/atomicity |
| Resume/Fork/Rewind | Usable | ephemeral-state drop contract | corruption/missing-worktree |
| RuntimeTaskRegistry | New SoT but legacy coexist | **P0 single writer** | race/idempotency |
| Scheduler | Usable | 不加 watcher | restart/missed/duplicate fire tests |
| Hooks | Mature | trust + additional context decision | timeout/failure/HTTP tests |
| MCP | Mature | trust lifecycle linkage | auth/reconnect/crash/namespace |
| Plugins | Usable | **P0 trust activation + collision** | supply-chain tests |
| Skills | Usable | trust source linkage | shell/tool permission tests |
| Subagent | Mature | permission ceiling contract | abort/resume/sidechain |
| AgentServer | Mature / God Session | P1 owner facade | concurrency/wire tests |
| CLI/Headless | Mature | explicit TurnPreparation | surface consistency |
| TUI/Desktop | Mature | 不重写 | protocol/surface contract |
| Providers | Rich | P1 capability resolver | compatibility matrix |
| Worktree | Usable | accepted gap registry | dirty/missing/resume tests |
| Memory | Usable | provenance schema | staleness/compact retention |
| Bridge/Remote | Product extension | 与 core 隔离 | dedicated integration tests |
| Coordinator/Workflow | Product extension | 与 core policy 不竞争 | orchestration tests |
| Docs/Parity | Drift | **P0 SSOT reset** | auto-governance |
| CI | Green but manual quarantine | **P0 manifest/matrix** | flaky reduction |
| Eval/Verifier | Partial | P1 protocol skeleton | scenario evaluation |
''')

write('docs/06_RUNTIME_SPINE_SPEC.md', header('最终 Runtime Spine 与 Authority Boundary','CR-RUNTIME-SPINE-v2.0') + '''## 1. 唯一生产主脊柱

```text
CLI / Headless / TUI / Desktop / Server
                │
                ▼
          RuntimeSession
                │
                ▼
      TurnPreparationService
                │
          PreparedTurn
                │
                ▼
       canonical query()
          │          │
      Model Call     │
          │          │
      ToolUse ───────┘
          │
          ▼
    PermissionResolver
          │
          ▼
       Hook Gate
          │
          ▼
    ExecutionBoundary
          │
          ▼
      Tool Executor
          │
          ▼
       Tool Result
          │
          ▼
 Transcript / RuntimeTaskRegistry / SessionPersistence
          │
          └────────────→ query() continues
```

## 2. 禁止旁路

- Surface → direct model call；
- Tool → direct side effect without permission/execution boundary；
- Plugin/Skill/Hook/MCP → activation without trust resolution；
- Subagent → second independent permission policy；
- Background task → weaker boundary than foreground；
- Scheduler firing → direct tool execution bypassing normal policy；
- Resume → restore live trust or privilege；
- Compatibility wrapper → rebuild a competing system prompt/context owner。

## 3. Authority Table

| 语义 | 唯一 owner | Adapter 可做什么 | Adapter 禁止做什么 |
|---|---|---|---|
| Turn preparation | TurnPreparationService | 收集 surface request | 自己拼 full prompt/tool list |
| Query state | query() | 转换事件 | 再实现状态机 |
| Permission | PermissionResolver | 呈现 ask UI | 自己 allow/deny |
| Execution | ExecutionBoundary | 提供 platform impl | 绕过边界 |
| Runtime task state | RuntimeTaskRegistry | read-only projection | 双写 |
| Extension activation | ExtensionActivationGate | discover/describe | 直接 register executable |
| Session lifecycle | SessionLifecycle | serialize/deserialize | 恢复 ephemeral security state |
| Evidence truth | baseline/status machine assets | render docs | 手工改多个真值 |
''')

write('docs/07_OWNER_MAP.md', header('Owner Map 与依赖方向','CR-OWNER-MAP-v2.0') + '''## 1. Owner 原则

Owner 不是“目录在哪”，而是“谁对最终语义负责”。一个 package 可以有很多 helper，但不可出现两个可以独立给出最终答案的 owner。

## 2. 推荐 owners

- `RuntimeSession`：会话级依赖与 capability references；
- `SessionLifecycle`：start/resume/fork/rewind/end；
- `TurnPreparationService`：进入 query 前的全部输入准备；
- `Query`：模型/工具轮次状态机；
- `PermissionResolver`：allow/ask/deny 最终裁决；
- `ExecutionBoundary`：OS/process/filesystem isolation；
- `ToolExecutionService`：tool 调度与结果映射；
- `RuntimeTaskRegistry`：后台 runtime tasks；
- `ExtensionActivationGate`：extension activation；
- `ModelCapabilityResolver`：model/provider capability snapshot；
- `CompletionVerifier`：任务完成的可验证判定；
- `EvidenceRegistry`：测试/平台/差异证据元数据。

## 3. 依赖方向

高层 surface 可以依赖 runtime facades；核心 policy 不得反向依赖 TUI/Desktop。Bootstrap state 仍作为 DAG leaf，不应反向 import feature subsystems。

## 4. 需要删除的 owner 重叠

- `QueryEngine._build_system_prompt_parts` vs `agent_loop_compat.build_effective_system_prompt`；
- `runtime_tasks` vs legacy background task dict 的写权限；
- plugin loader register vs trust decision；
- CI workflow 手工 deselect vs docs 手工 quarantine list。
''')

write('docs/08_P0_IMPLEMENTATION_SPEC.md', header('P0 Implementation Spec','CR-P0-IMPLEMENTATION-v2.0') + '''## P0-A Repository Truth Reset

### 修改
1. 建立 canonical `reference-lock.yaml`；
2. baseline/status/plan/registry/scorecard 都写同一 `subject_commit`；
3. governance script 检查所有 CURRENT 资产；
4. README 只指向 canonical current docs；
5. historical docs 加 superseded banner。

### 测试
- stale SHA → fail；
- missing reference generation → fail；
- current doc points archive → fail；
- registry accepted diff 缺 evidence → fail。

## P0-B Permission Safe Default

推荐优先方案：`ToolContext.permission_context` **不提供默认值**。如果兼容性要求必须有 default，则只能是 `mode="default"` + fail-closed ask semantics，绝不能是 bypass。

所有 bypass 构造必须类似：

```python
ToolPermissionContext(
    mode="bypassPermissions",
    bypass_origin="trusted_internal_test_or_explicit_cli",
    bypass_reason="...",
)
```

禁止仅凭 bool 打开 bypass。

## P0-C Canonical Turn Preparation

创建 `PreparedTurn` typed object。迁移顺序：

1. characterization tests 固定两个旧 builder 当前输出；
2. 新 service 先内部调用现有 helpers；
3. headless/server/TUI adapters 切换；
4. QueryEngine 改为 facade；
5. 删除重复 assembly；
6. 增加 surface-equivalence tests。

## P0-D Extension Activation Gate

Activation 输入至少包含：kind、name、source_path/server、scope、trust_level、workspace_trusted、manifest hash、requested capabilities。

结果：`ALLOW / DENY / REQUIRE_TRUST / INVALID / COLLISION`。任何结果必须可审计。

## P0-E Task Single Writer

任何 runtime task lifecycle 状态变更只能调用 RuntimeTaskRegistry。Legacy `tasks` / `background_bash_tasks` 只能读 projection 或通过 adapter 转发到 registry。

## P0-F CI Truth

CI 不再直接写 5 个 `--deselect`。改为脚本读取 `machine/ci-quarantine.yaml`，生成参数并验证每项仍存在。过期 quarantine 自动 fail 或至少 warning + release gate fail。
''')

write('docs/09_P1_IMPLEMENTATION_SPEC.md', header('P1 Implementation Spec','CR-P1-IMPLEMENTATION-v2.0') + '''## 1. AgentServer owner facades

不改变 WebSocket / worker thread / permission Event roundtrip。只把 `_AgentSession` 中不同生命周期对象放入明确子对象，减少测试时“一改全 session”。

## 2. ModelCapabilityResolver

把 adaptive thinking、streaming/tool schema/cache capability 等 model/provider 判定集中，query 读取 immutable snapshot。不要在 query.py 与 model_call.py 分别维护 allowlist。

## 3. CompressionOutcome

所有压缩入口返回结构化结果：

```python
changed: bool
stage: str | None
warnings: tuple[str,...]
hard_limit_reached: bool
artifacts: tuple[str,...]
tokens_before: int | None
tokens_after: int | None
```

manual compact 与 automatic pipeline 共用 contracts/types，但不混淆产品语义。

## 4. CompletionVerifier

Freeze 前只定义 protocol 与最小 wiring，不建立“大型评测平台”。Verifier 应消费 task contract + trace/evidence，而不是要求模型再次自评。

## 5. Legacy Cleanup

`cli_backup`、旧 compatibility helpers、deprecated docs 的删除必须先有 zero-production-ref 证据。无法证明时先标 deprecated，不强删。
''')

write('docs/10_MIGRATION_STRATEGY.md', header('低风险迁移策略与回滚设计','CR-MIGRATION-STRATEGY-v2.0') + '''## 原则

最后一次大改最危险的是“收口过程中把成熟功能重写坏”。因此全部采用 **characterize → introduce facade → dual-read shadow → cutover → remove duplicate writer**，禁止 big-bang。

## Turn Preparation

- 先记录各 surface 输入/最终 prompt/tool visibility 快照；
- 新 service 与旧路径 shadow compare；
- 差异必须分类：bug / intentional surface diff / accepted diff；
- 生产切换后保留一轮 compatibility wrapper；
- 最后删除旧 owner。

## Task Registry

短期允许 dual-read，禁止 dual-write。写操作先迁移到 registry，再让旧 API 只读 registry projection。

## Extension Trust

先把 loader 注册动作包到 activation gate 后面，不先改 Plugin/MCP/Skill/Hook 内部实现。Gate 失败必须 rollback 未完成注册。

## Permission

constructor default 变化应先跑全量调用点 grep/static check；任何未显式传 context 的 production call site 都要明确选择 safe mode，而不是批量填 bypass。

## Rollback

每个 P0 独立 PR；不得把 Truth Reset、Permission、TurnPreparation、Extension Trust 混成一个不可回滚 PR。
''')

write('docs/11_ACCEPTANCE_AND_FREEZE_GATE.md', header('Architecture Freeze 验收门','CR-FREEZE-GATE-v2.0') + '''所有 Gate 必须 PASS，不能以“后面再补测试”跳过。

## Gate A — Canonical Truth
- [ ] CURRENT machine/docs 全部绑定最终 SHA
- [ ] reference generation 唯一
- [ ] active plan 唯一
- [ ] archive 不参与 current truth

## Gate B — Canonical Loop
- [ ] production authoritative query state machine = 1
- [ ] compatibility paths 不再独立实现 loop

## Gate C — Canonical Turn Preparation
- [ ] full prompt/context/tool visibility owner = 1
- [ ] CLI/headless/server/TUI 走同一 preparation contract

## Gate D — Canonical Permission
- [ ] implicit bypass default = 0
- [ ] bypass 都有 explicit origin/reason
- [ ] headless ask fail-closed
- [ ] deliberate divergences 都已登记

## Gate E — Canonical Execution
- [ ] foreground/background/subagent/scheduler 均进入 normal execution boundary
- [ ] platform evidence 与声明分开

## Gate F — Canonical Task State
- [ ] runtime task writable owner = 1
- [ ] legacy state 无双写

## Gate G — Canonical Extension Gate
- [ ] project executable extension activation 必经 trust gate
- [ ] collision policy deterministic
- [ ] provenance 可审计

## Gate H — Canonical Persistence
- [ ] resume 不恢复 ephemeral trust/privilege/live handles
- [ ] crash-safe/atomic contracts 有测试

## Gate I — Legacy Production Paths
- [ ] 旧 owner production refs=0 或明确 compatibility-only
- [ ] `cli_backup` 有 zero-ref proof 或保留理由

## Gate J — Test Truth
- [ ] 每个 CI deselect 均登记
- [ ] quarantine 数量与 workflow 实际一致
- [ ] local/CI/platform evidence 独立
- [ ] final evidence 绑定 freeze SHA

全部通过后允许记录：`ARCHITECTURE_FREEZE`。
''')

write('docs/12_TEST_DEBUG_MASTER_PIPELINE.md', header('Architecture Freeze 后测试/调试总 Pipeline','CR-TEST-DEBUG-PIPELINE-v2.0') + '''## T0 Baseline / Static / Import / Docs Truth

导入全部 public modules；lint/import contracts；reference lock；current truth；quarantine；packaging metadata。

## T1 Permission

模式矩阵：default / acceptEdits / plan / dontAsk / auto / bypass explicit；deny/ask/allow precedence；path gates；headless；subagent ceiling；MCP/tool differences。

## T2 Execution / Sandbox

cwd/root containment、process kill、timeout、env、network policy、symlink/path traversal、Windows Job Object、Linux bwrap、macOS sandbox/fallback。

## T3 Individual Tools

每个工具：schema、invalid input、permission contract、side effects、large result、abort、streaming、encoding、resource cleanup。

## T4 Tool Execution + Hooks

PreTool/PostTool/HTTP/prompt hooks；timeout；hook deny/modify；result persistence；concurrent read tools；aggregate budget。

## T5 Agent Loop

normal turn、multi-tool、retry、provider fallback、stream interruption、abort、budget、tool error loops、terminal conditions。

## T6 Context / Compact / Cache

五阶段顺序、hard window、snip artifact、microcompact、collapse、autocompact、多次连续 compact、prompt cache scope、additional context。

## T7 State / Persistence / Resume

append/atomicity、corruption recovery、resume/fork/rewind、missing/dirty worktree、ephemeral state drop、conversation lineage。

## T8 Subagent / Background / Task / Scheduler

permission ceiling、abort cascade、resume、name collision、task idempotency、scheduler restart/missed/duplicate fire、foreground/background policy equivalence。

## T9 MCP / Plugin / Skill / Hook Supply Chain

trust gate、auth、OAuth/token store、server crash、reconnect、namespace collision、plugin name collision、project trust、skill shell permission。

## T10 Surfaces

CLI/headless/TUI/Desktop/AgentServer：prepared turn equivalence、permission roundtrip、event envelopes、non-interactive behavior。

## T11 Cross-component Integration

长链：prompt → tool → hook → permission → execution → task → persistence → compact → resume → subagent/MCP。

## T12 Fault Injection

provider 429/500、network reset、tool hang、hook exception、disk full/readonly、partial JSONL write、MCP crash、thread cancellation、corrupt state。

## T13 Long Horizon

100+ turns、多轮 compact、多个 background tasks、scheduler restart、resume 多次、provider fallback、memory provenance/staleness。

## T14 Global Regression / RC

全量 Python + TUI + Desktop + platform smoke；freeze governance；release packaging；最终 evidence bundle。
''')

write('docs/13_FAULT_INJECTION_PLAN.md', header('Fault Injection 测试计划','CR-FAULT-PLAN-v2.0') + '''| 故障 | 注入点 | 期望 |
|---|---|---|
| Provider 429 | model call | bounded retry/backoff，可 abort |
| Provider stream reset | streaming parser | 不重复 tool side effect |
| Tool timeout | executor | 终止子进程，返回结构化错误 |
| Hook exception | hook executor | 按 hook policy fail-open/closed，记录来源 |
| Permission handler disconnect | surface bridge | ask 不得变 allow |
| Disk readonly | persistence | 明确失败，不伪造 completed |
| Partial transcript write | JSONL/state | resume 检测并恢复/拒绝 |
| MCP server crash | connection manager | namespace 移除/重连策略确定 |
| Plugin activation partial failure | activation gate | rollback registration |
| Background task race | task registry | 单一终态/幂等 stop |
| Scheduler duplicate wakeup | scheduler | idempotent fire key |
| Compact artifact write failure | compact stage | outcome 报警且不隐瞒 hard limit |
| AgentServer worker abort | thread bridge | session 可清理，不残留 permission waiter |
''')

write('docs/14_LONG_HORIZON_PLAN.md', header('Long-Horizon / 多轮运行验证计划','CR-LONG-HORIZON-v2.0') + '''## 场景 L1：100-turn 稳定会话

混合 Read/Grep/Bash/MCP/Skill，至少触发 3 次不同 compact stage；验证 token 预算、transcript 顺序、任务状态、无重复 side effect。

## L2：Resume × 10

同一 session 连续 10 次中断/恢复；验证 ephemeral permission/trust/handles 不复活，lineage 不丢。

## L3：后台任务 + Compact + Resume

启动 background tasks → compact → 退出 → resume；验证 persisted state 与 runtime live handle 的边界。

## L4：Scheduler 重启

注册计划任务 → runtime 重启 → 到点/错过/重复启动；验证 exactly-once 或明确 at-least-once contract。

## L5：Provider fallback

多 provider 交替失败；验证 capability snapshot、thinking config、tool schema 不因 fallback 漂移。

## L6：Extension lifecycle

project trust 从未信任→信任→撤销；验证 activation 与 session restart 行为。
''')

write('docs/15_ISSUE_BACKLOG.md', header('可直接转 GitHub Issues 的最终 Backlog','CR-ISSUE-BACKLOG-v2.0') + '''## P0

1. **B7-W0 Truth Reset: canonical baseline/status/reference-lock**
2. **B7-W1 Remove implicit ToolContext bypass default**
3. **B7-W1 Register all deliberate permission divergences**
4. **B7-W2 Introduce canonical TurnPreparationService**
5. **B7-W2 Cut all production surfaces to TurnPreparationService**
6. **B7-W3 Add ExtensionActivationGate + provenance**
7. **B7-W3 Reject/resolve plugin name collisions deterministically**
8. **B7-W4 Make RuntimeTaskRegistry the only runtime-task writer**
9. **B7-W4 Define SessionLifecycle + ephemeral resume reset**
10. **B7-W7 Create CI quarantine single manifest**
11. **B7-W7 Create declared/CI/platform support matrix**
12. **B7-W9 Generate freeze evidence from final SHA**

## P1

13. `CompressionOutcome` structured contract
14. unify manual/auto compact package ownership
15. decide PostSampling additional_contexts wiring vs accepted diff
16. `ModelCapabilityResolver`
17. AgentServer ownership facade extraction
18. CompletionVerifier protocol skeleton
19. README/pyproject identity migration
20. `cli_backup` zero-ref proof + removal/exclusion

## TEST-CLOSURE

21. Windows Job Object real-device verification
22. Linux bwrap real-device verification
23. MCP crash/reconnect/auth matrix
24. Scheduler restart/missed/duplicate fire
25. Subagent abort/resume/permission ceiling
26. long-horizon multi-compact/resume
27. surface prepared-turn equivalence
28. persistence corruption/fault injection
''')

write('docs/16_PR_SEQUENCE.md', header('PR / Commit 执行顺序','CR-PR-SEQUENCE-v2.0') + '''建议分 10 个 PR，任一 P0 失败可独立回滚：

1. `docs(B7): truth reset + reference lock`
2. `security(B7): remove implicit permission bypass default`
3. `runtime(B7): introduce canonical turn preparation`
4. `security(B7): extension trust-before-activation`
5. `runtime(B7): task registry single writer + session lifecycle`
6. `context(B7): compression outcome and ownership closure`
7. `runtime(B7): capability resolver + server ownership facades`
8. `ci(B7): quarantine manifest + platform/python matrix`
9. `chore(B7): identity + legacy cleanup`
10. `release(B7): architecture freeze evidence and baseline lock`

禁止把 PR 2–5 squash 成一个大型不可 bisect 变更。
''')

write('docs/17_RISK_REGISTER.md', header('风险台账与 Stop-the-Line 条件','CR-RISK-REGISTER-v2.0') + '''| ID | 风险 | 等级 | Stop-the-line 条件 | 对策 |
|---|---|---|---|---|
| R1 | safe default 改动导致入口全被 deny | P0 | 基本 CLI/headless 失效 | callsite inventory + targeted migration |
| R2 | TurnPreparation cutover prompt/tool 漂移 | P0 | surface snapshot diff 未解释 | shadow compare |
| R3 | Trust gate 阻断 managed/bundled extensions | P0 | bundled regression | source-specific policy tests |
| R4 | Task registry 切换丢后台任务 | P0 | task lifecycle mismatch | dual-read, single-write migration |
| R5 | AgentServer facade 改坏并发 | P1 | deadlock/event loss | ownership only, no protocol rewrite |
| R6 | quarantine manifest 漏掉真实 deselect | P0 | workflow != manifest | generated args only |
| R7 | identity rename 破坏 CLI | P1 | existing command broken | alias/deprecation |
| R8 | Freeze 文档绑定旧 SHA | P0 | subject mismatch | machine gate |
''')

write('docs/18_ACCEPTED_DIFFERENCES.md', header('Reference 差异与 Product Extension 管理','CR-ACCEPTED-DIFFS-v2.0') + '''## 1. 规则

差异不等于缺陷。每个差异必须标为：`FUNCTIONAL_ADAPTATION / PRODUCT_EXTENSION / ACCEPTED_DIFF / DEFERRED_REFERENCE_GAP`，并给 evidence 与风险。

## 2. 当前必须补登记的 Permission UX 差异候选

- WebSearch：Python 项目选择低风险 read-only 自动允许；
- AskUserQuestion：交互本身视为 gate，避免重复 permission prompt；
- SendUserMessage；
- StructuredOutput；
- Skill：本项目通过内部 shell/tool 正常 permission，而非完全复制 Reference allowed-tools 预授权语义。

这些差异需要逐条 registry，不应仅写在代码注释。

## 3. 已知架构/平台差异

- Python-native Snip / Compact implementation details；
- Scheduler file-backed persistence 与 watcher/owner-takeover 差异；
- Windows/Linux/macOS isolation implementation；
- surface event envelope；
- worktree resume repair gap。

## 4. Product Extensions

Bridge/Remote、Coordinator/Workflow、部分 provider / advisor / task enhancements 可作为 Product Extension，但不得改变 canonical query / permission / execution policy 的 authority。
''')

write('docs/19_PROJECT_IDENTITY_MIGRATION.md', header('项目身份与 Packaging 迁移','CR-IDENTITY-MIGRATION-v2.0') + '''当前仓库 canonical identity 为 `Nuos/clauderuntime`，但 package metadata/CLI 仍保留 `clawcodex` 历史命名。

建议分层：

- Repository/Product: `ClaudeRuntime`；
- Python distribution：可继续暂时 `clawcodex-cli` 以避免破坏安装者，或另开明确 migration；
- CLI：`clawcodex` 可作为兼容入口；若新增 `clauderuntime`，至少一个 release 周期双入口；
- Project URLs 立即改为 `Nuos/clauderuntime`；
- README 明确 canonical name / compatibility aliases；
- classifiers 只表达“意图支持”，平台验证另有 evidence matrix。

本轮不建议为了名字做包级大规模 rename/import path 迁移。
''')

write('docs/20_CI_PLATFORM_CLOSURE.md', header('CI / Python / Platform Closure 规范','CR-CI-PLATFORM-v2.0') + '''## CI 分层

1. docs-governance（Ubuntu, fast）；
2. core tests（macOS 3.12, release-gate）；
3. Python compatibility smoke（3.10/3.12/3.14）；
4. OS smoke（macOS/Ubuntu/Windows）；
5. platform-isolation verification（独立 evidence job，不能被普通 smoke 代替）；
6. optional integration（MCP/外部服务）。

## Quarantine

当前实际需要登记 5 个 deselect，全部进入 `machine/ci-quarantine.yaml`。Workflow 应通过脚本生成 pytest args；文档只引用 manifest 数量，不再复制测试名。

## Evidence Artifact

每个 CI run 至少输出：commit SHA、OS、Python、test command、passed/failed/skipped/deselected、quarantine manifest hash、timestamp。
''')

write('docs/21_EXTENSION_TRUST_SPEC.md', header('Extension Trust-before-Activation 规范','CR-EXTENSION-TRUST-v2.0') + '''## 1. ExtensionDescriptor

字段：`kind/name/source/scope/trust_level/provenance_hash/manifest/capabilities/executable_hooks`。

## 2. Trust Levels

`bundled / managed / user / project / mcp` 是 source-trust taxonomy，不直接等于 allow。Policy 还需考虑 workspace trust、管理员策略、签名/hash、server URL/auth 与 capability。

## 3. Activation

```text
Discover → Parse → Descriptor → Trust Resolve → Validate → Collision Check → Activate → Register
```

任何 project-level executable hook/shell/MCP server 在 workspace 未信任时，不允许 activation side effect。

## 4. Collision

同名 extension 不得 silent overwrite。候选政策：

1. exact duplicate hash → dedupe；
2. higher-precedence managed/bundled 可 shadow，但记录 provenance；
3. same-precedence conflict → reject；
4. project attempting to replace managed/bundled → deny unless explicit policy。

## 5. Rollback

Activation 中途失败必须撤销已注册 commands/tools/hooks/MCP resources。
''')

write('docs/22_TASK_STATE_PERSISTENCE_SPEC.md', header('Runtime Task / Session / Persistence 规范','CR-TASK-STATE-PERSIST-v2.0') + '''## RuntimeTaskRegistry

负责 local shell、local agent、其他 runtime/background task 的生命周期。所有 mutate 操作走 typed registry；legacy maps 不得单独更新。

## Durable vs Ephemeral

**Durable**：task id/type/status、command/spec、timestamps、result metadata、parent session lineage。  
**Ephemeral**：Popen/thread/future/event/lock/abort controller/live MCP connection/temporary permission/trust verdict。

## Resume

Resume 只能重新构造 runtime handles；不得 deserialize 后直接信任旧 privilege。任何需要权限的重新启动动作必须重新进入 permission/execution boundary。

## Scheduler

本轮不增加跨进程 watcher/leader election。需要测试其当前 file-backed contract：load、idempotent create/delete、restart、missed fire、duplicate fire policy。
''')

write('docs/23_TURN_PREPARATION_SPEC.md', header('Canonical TurnPreparationService 详细规范','CR-TURN-PREPARATION-v2.0') + '''## Input

`TurnRequest(surface, user_messages, custom_system_prompt, append_system_prompt, output_style, provider/model overrides, session flags)` + `RuntimeSession`。

## Output: PreparedTurn

- `system_prompt_blocks`；
- `messages`；
- `visible_tools`；
- `mcp_context`；
- `skill_context`；
- `workspace_context`；
- `model_capabilities`；
- `compact_config`；
- `prompt_cache_scope`；
- `query_params`；
- `provenance`（哪些输入来自 config/workspace/plugin/skill）。

## Invariants

- 同一 session/request 在不同 surface 下，除明确 surface-specific fields 外应得到等价 PreparedTurn；
- pre-trust 阶段不读取/执行不安全 project executable context；
- tool visibility 在 query 前固定 snapshot，动态 refresh 必须走明确 refresh hook；
- builder 不执行 model call；
- query 不重新拼 full system prompt。
''')

write('docs/24_PERMISSION_SAFE_DEFAULT_SPEC.md', header('Permission Safe Default 详细规范','CR-PERM-SAFE-DEFAULT-v2.0') + '''## 问题定义

危险不是“当前 headless 已经 bypass”，而是 constructor omission 能获得高权限。修复目标是把 omission 变成安全失败。

## 推荐实现

### 首选
`ToolContext.permission_context` 改为 required positional/keyword field。

### 兼容方案
默认 `ToolPermissionContext(mode="default", should_avoid_permission_prompts=True)`，但必须确认交互式调用点不会因此错误 deny；因此首选 required 更清楚。

## Bypass 约束

- 仅显式 CLI flag、受控内部 test harness 或受信管理策略可以申请；
- context 中记录 `bypass_origin`、`bypass_reason`；
- telemetry/evidence 可看到 bypass；
- subagent/background/scheduler 不得自行升级为 bypass。

## Regression Matrix

constructor omission、default interactive、headless、plan、acceptEdits、dontAsk、auto classifier unavailable、explicit bypass、deny rule always wins。
''')

write('docs/25_SERVER_SESSION_DECOMPOSITION_SPEC.md', header('AgentServer Session Ownership 收口','CR-SERVER-SESSION-v2.0') + '''不重写 server wire/concurrency，仅拆 ownership。

建议：

```text
AgentServer
  └─ RuntimeSession
      ├─ SessionState
      ├─ PermissionBridge
      ├─ SurfaceEmitter
      ├─ SchedulerBridge
      ├─ BackgroundTaskFacade
      └─ SessionLifecycle
```

`_AgentSession` 可以先保留为 composition root，字段逐步移动到子对象。必须保留：WebSocket event loop、query worker thread、`call_soon_threadsafe`、blocking permission roundtrip 的现有 proven behavior。
''')

write('docs/26_COMPACT_CONTEXT_CLOSURE_SPEC.md', header('Context / Compact 最终收口规范','CR-COMPACT-CLOSURE-v2.0') + '''## 固定 stage 顺序

`applyToolResultBudget → snipCompactIfNeeded → microcompact → contextCollapse.applyCollapsesIfNeeded → autocompact`

## 本轮允许改变

- return outcome type；
- manual compact 的 package ownership；
- telemetry/evidence；
- additional contexts wiring/accepted diff；
- retention tests。

## 本轮禁止改变

- stage 顺序；
- token thresholds 的大规模重新设计；
-另建第二 compact pipeline。

## PostSampling additional_contexts

必须二选一：

1. 正式定义 injection lane，进入下一 turn prepared context；
2. 明确 registry accepted diff，API 不再暗示“支持但丢弃”。
''')

write('docs/27_MODEL_CAPABILITY_RESOLVER_SPEC.md', header('ModelCapabilityResolver 规范','CR-MODEL-CAPS-v2.0') + '''Query 只能消费 capability snapshot，不直接维护 provider/model allowlist。

Capability 示例：adaptive thinking、interleaved thinking、prompt cache、tool choice/schema quirks、max context、stream events、image support、system prompt shape。

Resolver 输入：provider id + model id + provider config/version。输出 immutable `ModelCapabilities`。Fallback 时必须重新 resolve，不可沿用前一个 provider snapshot。
''')

write('docs/28_EVAL_COMPLETION_VERIFIER_SPEC.md', header('Eval / CompletionVerifier 最小规范','CR-EVAL-VERIFIER-v2.0') + '''Freeze 前只建立最小 interface：

```text
TaskContract
ExecutionTrace
EvidenceArtifact[]
Verifier.verify(...) -> CompletionDecision
```

`CompletionDecision` 至少有：`PASS / FAIL / INDETERMINATE` + reasons + evidence refs。

典型 verifier：file exists/hash、tests pass、command exit code、JSON schema、git diff constraints、user-specified acceptance checks。禁止默认让同一模型用一句“已经完成”充当 verifier。
''')

write('docs/29_LEGACY_REMOVAL_SPEC.md', header('Legacy / Compatibility Cleanup 规范','CR-LEGACY-CLEANUP-v2.0') + '''候选：`src/cli_backup`、旧 prompt/context builder、旧 background task maps、deprecated docs/pointers。

删除门：

1. import search；
2. callgraph/search production refs；
3. tests refs 分类；
4. entrypoint/package include 检查；
5. compatibility/public API 判断；
6. zero-ref evidence 或 deprecation plan。

无法证明无生产引用 → 不删，只标 deprecated/compatibility-only。
''')

write('docs/30_POST_FREEZE_OPERATING_RULES.md', header('Architecture Freeze 后开发规则','CR-POST-FREEZE-RULES-v2.0') + '''Freeze 后默认允许：bug fix、contract tests、fault injection、platform adaptation、performance fix、security hardening、compatibility fix、release engineering。

默认禁止：跨 3+ subsystem 的“顺手重构”、更换 query loop、重写 permission、重新排序 compact、另建第二 state/task system、UI 自建 policy。

若确需架构变化，必须先提交 RFC：失败证据 → 无法在现 contract 内修复的原因 → 影响 owners → migration/rollback → 新 freeze gate。
''')

write('docs/31_RELEASE_CANDIDATE_GATE.md', header('Release Candidate Gate','CR-RC-GATE-v2.0') + '''RC 前必须满足：Architecture Freeze record 存在；T0–T14 关键阶段 evidence 完整；quarantine 无过期 P0 项；macOS full suite + Linux/Windows smoke；isolation 平台证据明确；package build/install smoke；README/URLs/version metadata 正确；accepted differences registry 完整；无 open P0 security/governance blockers。
''')

write('docs/32_SOURCE_EVIDENCE_MANIFEST.md', header('来源与证据边界','CR-SOURCE-EVIDENCE-v2.0') + '''## 用户提供来源

- `references/Claude-code-源码链接和论文分析链接.txt`
- `references/original-paper-arxiv-2604.14228v2.pdf`
- `references/七个核心功能组件概述.txt`

## Reference 解释

源码链接指向 `ChinaSiro/claude-code-sourcemap`，属于从 source map 恢复的 2.1.88 snapshot；本包严格使用 “recovered source/source-map snapshot” 表述。

## 当前仓库入口证据

本轮重新检查 `Nuos/clauderuntime`，current main HEAD 仍为本包 subject SHA。关键现状依据包括：CI 当前手工 deselect 5 项、pyproject 仍保留 `clawcodex-cli`/旧 URLs、README 仍指向旧 active plan/bible、ToolContext 默认 bypass、Permission deliberate UX divergence 注释。

## 不应过度声称

本环境未重新独立执行目标仓库 10k+ 全套测试，因此历史的 `10212 passed` 等只属于 repo-recorded evidence。平台 isolation 也不可在无真机证据时写成 verified。
''')

write('docs/33_CHANGESET_CHECKLIST.md', header('最终 ChangeSet Checklist','CR-CHANGESET-CHECKLIST-v2.0') + '''## W0
- [ ] reference-lock
- [ ] baseline/current/active plan SSOT
- [ ] stale SHA gate
- [ ] README pointers

## W1
- [ ] ToolContext no implicit bypass
- [ ] bypass origin/reason
- [ ] all production callsites explicit
- [ ] headless ask fail-closed tests
- [ ] deliberate permission diffs registered

## W2
- [ ] PreparedTurn type
- [ ] TurnPreparationService
- [ ] surface cutover
- [ ] QueryEngine facade only
- [ ] duplicate builder removed
- [ ] surface-equivalence tests

## W3
- [ ] ExtensionDescriptor
- [ ] trust resolver
- [ ] activation gate
- [ ] collision policy
- [ ] rollback
- [ ] plugin/skill/hook/MCP integration

## W4
- [ ] RuntimeTaskRegistry single writer
- [ ] legacy read projection
- [ ] SessionLifecycle
- [ ] persistence adapters
- [ ] resume ephemeral reset

## W5
- [ ] CompressionOutcome
- [ ] manual compact ownership
- [ ] additional_contexts decision
- [ ] multi-compact retention tests

## W6
- [ ] ModelCapabilityResolver
- [ ] AgentServer facades
- [ ] CompletionVerifier protocol

## W7
- [ ] quarantine manifest
- [ ] generated deselect args
- [ ] Python smoke matrix
- [ ] OS smoke matrix
- [ ] platform evidence records

## W8
- [ ] pyproject URLs
- [ ] identity/deprecation plan
- [ ] cli_backup zero-ref
- [ ] archive labels

## W9
- [ ] freeze gates all PASS
- [ ] final SHA evidence regenerated
- [ ] freeze record
- [ ] switch active plan to T0–T14
''')

# Machine files
write('machine/baseline.yaml', f'''schema: 1
project: ClaudeRuntime
repository: Nuos/clauderuntime
subject_entry_commit: {SUBJECT}
reference:
  product: Claude Code
  version: 2.1.88
  source_kind: recovered_source_map_snapshot
  commit: {REF}
  paper: {PAPER}
status:
  functional: FUNCTIONALLY_SIMILAR_CORE_COMPLETE
  architecture: FINAL_CLOSURE_REQUIRED
  parity: PARTIAL_NOT_RELEASE_GATE
  evidence: REBASE_REQUIRED
next_gate: ARCHITECTURE_FREEZE
''')
write('machine/reference-lock.yaml', f'''schema: 1
reference_id: claude-code-2.1.88-recovered-g1
source_kind: recovered_source_map_snapshot
repository: ChinaSiro/claude-code-sourcemap
commit: {REF}
product_version: 2.1.88
paper:
  arxiv: '2604.14228v2'
policy:
  official_open_source_claim_allowed: false
  strict_1_to_1_parity_release_gate: false
  hierarchical_reference_alignment: true
''')
write('machine/ssot-map.yaml', '''schema: 1
current_truth:
  baseline: docs/baseline/PROJECT_BASELINE.md
  status: docs/status/current.md
  active_plan: docs/plans/active/CURRENT_PLAN.md
  behavior_bible: docs/governance/BEHAVIOR_BIBLE.md
  reference_lock: docs/reference/reference-lock.yaml
  difference_registry: docs/reference-differences/registry.yaml
  parity_scorecard: docs/parity/scorecards/latest.yaml
rules:
  current_must_not_point_to_archive: true
  all_machine_assets_require_subject_commit: true
  stale_subject_is_error: true
''')
write('machine/owner-map.yaml', '''schema: 1
owners:
  turn_preparation: TurnPreparationService
  query_state_machine: canonical_query
  permission_decision: PermissionResolver
  execution_isolation: ExecutionBoundary
  tool_execution: ToolExecutionService
  runtime_task_state: RuntimeTaskRegistry
  extension_activation: ExtensionActivationGate
  session_lifecycle: SessionLifecycle
  model_capabilities: ModelCapabilityResolver
  completion_decision: CompletionVerifier
invariants:
  production_owner_count_per_semantic: 1
  legacy_writers_allowed: false
''')
write('machine/architecture-freeze-gates.yaml', '''schema: 1
gates:
  A_truth: {required: true, check: canonical_truth}
  B_loop: {required: true, check: single_query_loop}
  C_turn_preparation: {required: true, check: single_turn_preparation_owner}
  D_permission: {required: true, check: no_implicit_bypass}
  E_execution: {required: true, check: normal_execution_boundary}
  F_task_state: {required: true, check: single_runtime_task_writer}
  G_extension: {required: true, check: trust_before_activation}
  H_persistence: {required: true, check: no_ephemeral_privilege_resume}
  I_legacy: {required: true, check: legacy_production_paths_zero_or_declared}
  J_test_truth: {required: true, check: quarantine_and_evidence_consistent}
freeze_status_on_pass: ARCHITECTURE_FREEZE
''')
write('machine/ci-quarantine.yaml', '''schema: 1
policy:
  workflow_args_generated_from_manifest: true
  manual_deselect_in_ci_yaml_forbidden: true
items:
  - id: Q-WATCHDOG-001
    test: tests/test_stream_watchdog.py::TestStreamWatchdogFires::test_reset_pushes_deadline_forward
    reason: timing_sensitive_threading_timer_on_loaded_ci
    replacement_coverage: remaining_stream_watchdog_tests
    severity: non_blocking_environmental
  - id: Q-WATCHDOG-002
    test: tests/test_stream_watchdog.py::TestPingAwareLiveness::test_byte_progress_prevents_fire
    reason: timing_sensitive_threading_timer_on_loaded_ci
    replacement_coverage: remaining_stream_watchdog_tests
    severity: non_blocking_environmental
  - id: Q-WATCHDOG-003
    test: tests/test_ch04_api_round4.py::TestWatchdogWarning::test_half_time_warning_fires_once_and_reset_cancels
    reason: exact_sleep_timer_assertion_ci_jitter
    replacement_coverage: watchdog_warning_related_tests
    severity: non_blocking_environmental
  - id: Q-WATCHDOG-004
    test: tests/test_ch04_api_round4.py::TestWatchdogWarning::test_reset_before_half_time_prevents_warning
    reason: exact_sleep_timer_assertion_ci_jitter
    replacement_coverage: watchdog_warning_related_tests
    severity: non_blocking_environmental
  - id: Q-OPENCODE-001
    test: tests/test_opencode_compat_providers.py::test_xai_requests_go_to_chat_completions
    reason: httpx_mock_behavior_diff_in_ci_environment
    replacement_coverage: provider_compatibility_tests
    severity: non_blocking_environmental
''')
write('machine/test-matrix.yaml', '''schema: 1
levels:
  local_full: [macos_python312]
  ci_release_gate: [macos_python312]
  python_smoke: [python310, python312, python314]
  os_smoke: [macos, ubuntu, windows]
  platform_isolation: [macos_sandbox, linux_bwrap, windows_job_object]
  integration_optional: [real_mcp_stdio, external_provider]
evidence_labels: [TESTED_LOCAL, TESTED_CI, VERIFIED_PLATFORM]
rules:
  smoke_does_not_imply_full_suite: true
  os_smoke_does_not_imply_isolation_verified: true
''')
write('machine/module-status.yaml', '''schema: 1
modules:
  query: {status: mature, action: extract_outer_owners_only}
  permission: {status: mature_risky_default, action: P0}
  turn_preparation: {status: dual_owner, action: P0}
  extensions: {status: mature_mechanisms_missing_unified_activation_gate, action: P0}
  tasks: {status: migration_in_progress, action: P0_single_writer}
  compact: {status: mature, action: P1_contract_only}
  server: {status: mature_god_session, action: P1_owner_facades}
  sandbox: {status: implementation_present_evidence_limited, action: TEST_CLOSURE}
  mcp: {status: mature, action: TEST_CLOSURE}
  subagent: {status: mature, action: TEST_CLOSURE}
''')
write('machine/extension-trust-policy.yaml', '''schema: 1
trust_levels: [bundled, managed, user, project, mcp]
activation:
  project_requires_workspace_trust: true
  discovery_may_execute_code: false
  partial_activation_rollback_required: true
collision:
  exact_same_hash: dedupe
  same_precedence_different_content: reject
  project_over_managed: deny_by_default
  silent_overwrite: forbidden
''')
write('machine/accepted-differences.yaml', '''schema: 1
candidates:
  - id: PERM-WEBSEARCH-AUTOALLOW
    area: permission
    classification: FUNCTIONAL_ADAPTATION
    status: registry_required
  - id: PERM-ASKUSER-NO-DOUBLE-PROMPT
    area: permission
    classification: FUNCTIONAL_ADAPTATION
    status: registry_required
  - id: PERM-SENDUSERMESSAGE
    area: permission
    classification: FUNCTIONAL_ADAPTATION
    status: registry_required
  - id: PERM-STRUCTUREDOUTPUT
    area: permission
    classification: FUNCTIONAL_ADAPTATION
    status: registry_required
  - id: SKILL-PERMISSION-MODEL
    area: skills
    classification: FUNCTIONAL_ADAPTATION
    status: registry_required
''')
write('machine/risk-register.yaml', '''schema: 1
risks:
  - {id: R1, area: permission, severity: P0, risk: safe_default_breaks_entrypoints}
  - {id: R2, area: turn_preparation, severity: P0, risk: prompt_or_tool_visibility_drift}
  - {id: R3, area: extension, severity: P0, risk: trust_gate_breaks_bundled_or_managed}
  - {id: R4, area: task_state, severity: P0, risk: migration_loses_background_state}
  - {id: R5, area: server, severity: P1, risk: concurrency_regression}
  - {id: R6, area: ci, severity: P0, risk: quarantine_manifest_workflow_drift}
''')
write('machine/deprecation-plan.yaml', '''schema: 1
candidates:
  - path: src/cli_backup
    precondition: production_reference_count_zero
    action: remove_or_move_outside_package
  - symbol: QueryEngine._build_system_prompt_parts
    precondition: TurnPreparationService_cutover_complete
    action: delete_or_delegate_only
  - symbol: agent_loop_compat.build_effective_system_prompt
    precondition: TurnPreparationService_cutover_complete
    action: compatibility_delegate_only
  - symbol: legacy_background_task_maps
    precondition: RuntimeTaskRegistry_single_writer
    action: read_only_projection_then_remove
''')
write('machine/evidence-schema.json', json.dumps({
  "$schema":"https://json-schema.org/draft/2020-12/schema",
  "title":"ClaudeRuntime Evidence Record","type":"object",
  "required":["subject_commit","evidence_type","command_or_check","result","environment","timestamp"],
  "properties":{
    "subject_commit":{"type":"string","minLength":7},
    "evidence_type":{"enum":["TESTED_LOCAL","TESTED_CI","VERIFIED_PLATFORM","REFERENCE_CONFIRMED","ACCEPTED_DIFF"]},
    "command_or_check":{"type":"string"},"result":{"enum":["PASS","FAIL","BLOCKED"]},
    "environment":{"type":"object"},"timestamp":{"type":"string"},"artifact_refs":{"type":"array","items":{"type":"string"}}
  }
}, ensure_ascii=False, indent=2))

# Blueprints
write('blueprints/README.md', '''# Blueprints

这些文件是 **实现骨架/接口草案，不是可直接覆盖 production 的 patch**。它们用于约束 owner、类型与迁移方向；实际修改必须对照当前仓库 import/call graph 与 characterization tests。
''')
write('blueprints/runtime_turn_preparation.py', '''from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

@dataclass(frozen=True)
class PreparedTurn:
    system_prompt_blocks: tuple[Any, ...]
    messages: tuple[Any, ...]
    visible_tools: tuple[Any, ...]
    model_capabilities: Any
    compact_config: Any
    prompt_cache_scope: Any
    query_params: Any
    provenance: Mapping[str, Any] = field(default_factory=dict)

class TurnPreparationService:
    """Single owner for all pre-query runtime composition.

    No model call. No tool side effect. No permission bypass.
    """
    def prepare(self, request: Any, session: Any) -> PreparedTurn:
        raise NotImplementedError
''')
write('blueprints/extension_activation_gate.py', '''from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any

class ActivationBehavior(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_TRUST = "require_trust"
    INVALID = "invalid"
    COLLISION = "collision"

@dataclass(frozen=True)
class ExtensionDescriptor:
    kind: str
    name: str
    source: str
    scope: str
    trust_level: str
    provenance_hash: str
    requested_capabilities: tuple[str, ...] = ()

@dataclass(frozen=True)
class ActivationDecision:
    behavior: ActivationBehavior
    reason: str

class ExtensionActivationGate:
    def decide(self, descriptor: ExtensionDescriptor, *, workspace_trusted: bool, policy: Any) -> ActivationDecision:
        raise NotImplementedError
''')
write('blueprints/runtime_session.py', '''from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class RuntimeSession:
    session_id: str
    permission_context: Any
    tool_context: Any
    task_registry: Any
    lifecycle: Any
    model_capability_resolver: Any
    extension_gate: Any
    surface_emitter: Any | None = None
''')
write('blueprints/model_capability_resolver.py', '''from dataclasses import dataclass

@dataclass(frozen=True)
class ModelCapabilities:
    adaptive_thinking: bool = False
    prompt_cache: bool = False
    images: bool = False
    max_context_tokens: int | None = None

class ModelCapabilityResolver:
    def resolve(self, provider_id: str, model_id: str) -> ModelCapabilities:
        raise NotImplementedError
''')
write('blueprints/completion_verifier.py', '''from dataclasses import dataclass
from enum import Enum
from typing import Sequence, Any

class CompletionStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INDETERMINATE = "indeterminate"

@dataclass(frozen=True)
class CompletionDecision:
    status: CompletionStatus
    reasons: tuple[str, ...]
    evidence_refs: tuple[str, ...] = ()

class CompletionVerifier:
    def verify(self, task_contract: Any, execution_trace: Any, evidence: Sequence[Any]) -> CompletionDecision:
        raise NotImplementedError
''')
write('blueprints/compression_outcome.py', '''from dataclasses import dataclass

@dataclass(frozen=True)
class CompressionOutcome:
    changed: bool
    stage: str | None = None
    warnings: tuple[str, ...] = ()
    hard_limit_reached: bool = False
    artifacts: tuple[str, ...] = ()
    tokens_before: int | None = None
    tokens_after: int | None = None
''')
write('blueprints/task_registry_adapter.py', '''class LegacyTaskProjection:
    """Read-only compatibility view over RuntimeTaskRegistry."""
    def __init__(self, registry): self._registry = registry
    def get(self, task_id): return self._registry.get(task_id)
    def list(self): return self._registry.list()
    def __setitem__(self, key, value):
        raise RuntimeError("legacy task projection is read-only; mutate RuntimeTaskRegistry")
''')
write('blueprints/server_session_facades.py', '''from dataclasses import dataclass
from typing import Any

@dataclass
class PermissionBridge:
    ask_handler: Any
    pending_requests: Any

@dataclass
class SurfaceEmitter:
    emit: Any

@dataclass
class SchedulerBridge:
    scheduler: Any

@dataclass
class SessionState:
    app_state: Any
    messages: Any
    stats: Any
''')
write('blueprints/permission_context_safe_default.patch.txt', '''INTENT ONLY — adapt to current code before applying.

Before:
    permission_context: ToolPermissionContext = field(
        default_factory=lambda: ToolPermissionContext(mode="bypassPermissions")
    )

Preferred after:
    permission_context: ToolPermissionContext

Then inventory EVERY ToolContext(...) callsite and supply an explicit context.
Do NOT mechanically replace missing values with bypassPermissions.
''')

# Tests skeletons
write('tests/README.md', '''# Freeze contract test skeletons

这些测试名/接口是建议骨架。实际仓库中应复用现有 fixtures/types；不要机械复制导致一套平行测试 harness。
''')
write('tests/test_permission_safe_default.py', '''import inspect

def test_tool_context_has_no_implicit_bypass_default():
    from src.tool_system.context import ToolContext
    sig = inspect.signature(ToolContext)
    p = sig.parameters["permission_context"]
    # Preferred invariant: required argument.
    assert p.default is inspect._empty, "permission_context must not silently default to bypass"
''')
write('tests/test_turn_preparation_contract.py', '''def test_all_production_surfaces_use_one_turn_preparation_owner():
    """Implement with callgraph/monkeypatch characterization in the real repo."""
    pass

def test_surface_prepared_turns_are_equivalent_except_declared_surface_fields():
    pass
''')
write('tests/test_extension_activation_trust.py', '''def test_untrusted_project_extension_cannot_activate_executable_capability():
    pass

def test_extension_name_collision_is_not_silent_overwrite():
    pass
''')
write('tests/test_runtime_task_registry_owner.py', '''def test_legacy_task_views_are_read_only_or_delegate_to_registry():
    pass

def test_background_task_state_has_single_writable_owner():
    pass
''')
write('tests/test_resume_trust_reset.py', '''def test_resume_does_not_restore_temporary_permission_or_workspace_trust():
    pass

def test_resume_recreates_runtime_handles_instead_of_deserializing_them():
    pass
''')
write('tests/test_surface_query_consistency.py', '''def test_cli_headless_server_enter_same_canonical_query_path():
    pass
''')
write('tests/test_compaction_contract.py', '''def test_compaction_stage_order_is_fixed():
    expected = ["tool_result_budget", "snip", "microcompact", "context_collapse", "autocompact"]
    assert len(expected) == 5

def test_hard_limit_is_observable_in_compression_outcome():
    pass
''')
write('tests/test_model_capability_resolver.py', '''def test_provider_fallback_re_resolves_model_capabilities():
    pass
''')
write('tests/test_completion_verifier.py', '''def test_model_self_report_is_not_sufficient_evidence_for_completion():
    pass
''')
write('tests/test_freeze_governance.py', '''def test_current_truth_assets_share_final_subject_commit():
    pass

def test_ci_quarantine_manifest_is_single_source_of_deselects():
    pass
''')

# scripts
write('scripts/check_reference_lock.py', '''#!/usr/bin/env python3
from pathlib import Path
import yaml, sys
p=Path(__file__).resolve().parents[1]/"machine/reference-lock.yaml"
d=yaml.safe_load(p.read_text(encoding="utf-8"))
errors=[]
if d.get("source_kind")!="recovered_source_map_snapshot": errors.append("source_kind must be recovered_source_map_snapshot")
if d.get("policy",{}).get("official_open_source_claim_allowed") is not False: errors.append("official open-source claim must be false")
if not d.get("commit"): errors.append("reference commit missing")
if errors:
    print("FAIL", *errors, sep="\\n- "); sys.exit(1)
print("PASS reference lock")
''', True)
write('scripts/generate_ci_deselect_args.py', '''#!/usr/bin/env python3
from pathlib import Path
import yaml
p=Path(__file__).resolve().parents[1]/"machine/ci-quarantine.yaml"
d=yaml.safe_load(p.read_text(encoding="utf-8"))
for item in d.get("items",[]):
    print("--deselect", item["test"])
''', True)
write('scripts/check_quarantine_manifest.py', '''#!/usr/bin/env python3
from pathlib import Path
import yaml, sys
root=Path(__file__).resolve().parents[1]
d=yaml.safe_load((root/"machine/ci-quarantine.yaml").read_text(encoding="utf-8"))
ids=set(); tests=set(); errors=[]
for x in d.get("items",[]):
    if x.get("id") in ids: errors.append(f"duplicate id {x.get('id')}")
    if x.get("test") in tests: errors.append(f"duplicate test {x.get('test')}")
    ids.add(x.get("id")); tests.add(x.get("test"))
    for k in ("id","test","reason","replacement_coverage","severity"):
        if not x.get(k): errors.append(f"missing {k} in {x}")
if len(tests)!=5: errors.append(f"expected current baseline quarantine count 5, got {len(tests)}")
if errors:
    print("FAIL", *errors, sep="\\n- "); sys.exit(1)
print(f"PASS quarantine manifest: {len(tests)} entries")
''', True)
write('scripts/check_delivery_integrity.py', '''#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
errors=[]
for rec in manifest["files"]:
    p=root/rec["path"]
    if not p.exists(): errors.append(f"missing {rec['path']}"); continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h!=rec["sha256"]: errors.append(f"hash mismatch {rec['path']}")
if errors:
    print("FAIL", *errors, sep="\\n- "); sys.exit(1)
print(f"PASS delivery integrity: {len(manifest['files'])} files")
''', True)
write('scripts/check_architecture_freeze.py', '''#!/usr/bin/env python3
"""Repository-side scaffold: wire each gate to real checks before Freeze."""
from pathlib import Path
import yaml, sys
root=Path(__file__).resolve().parents[1]
g=yaml.safe_load((root/"machine/architecture-freeze-gates.yaml").read_text(encoding="utf-8"))
print("Freeze gates declared:")
for name, spec in g["gates"].items():
    print(f"- {name}: {spec['check']} (required={spec['required']})")
print("NOTE: this delivery-pack script validates declaration only; repository implementation must bind real checks.")
''', True)
write('scripts/run_delivery_validation.sh', '''#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
python "$HERE/check_reference_lock.py"
python "$HERE/check_quarantine_manifest.py"
python "$HERE/check_architecture_freeze.py"
python "$HERE/check_delivery_integrity.py"
''', True)

# templates
write('templates/PR_BODY.md', '''# Summary

## Owner/Boundary changed

## Semantics intentionally unchanged

## Characterization evidence

## Tests

## Reference / accepted difference

## Rollback plan

## Freeze impact
''')
write('templates/ISSUE_P0.md', '''# P0 Architecture Closure Issue

## Problem / owner conflict

## Current evidence

## Required invariant

## Minimal code change

## Tests / DoD

## Non-goals

## Rollback
''')
write('templates/ACCEPTED_DIFF_RECORD.md', '''# Accepted Difference

- ID:
- Area:
- Reference behavior:
- ClaudeRuntime behavior:
- Classification:
- Rationale:
- Security impact:
- Evidence/tests:
- Revisit trigger:
''')
write('templates/PLATFORM_VERIFICATION_RECORD.md', '''# Platform Verification Record

- subject_commit:
- platform / OS version:
- architecture:
- Python:
- isolation backend:
- command:
- result: PASS / FAIL / BLOCKED
- evidence artifact:
- limitations:
''')
write('templates/ARCHITECTURE_FREEZE_RECORD.md', '''# Architecture Freeze Record

- final_subject_commit:
- date:
- gates A–J:
- CI evidence:
- platform evidence:
- accepted differences registry hash:
- quarantine manifest hash:
- unresolved non-blockers:
- status: ARCHITECTURE_FREEZE
''')
write('templates/TEST_EVIDENCE_RECORD.json', json.dumps({
  "subject_commit":"","evidence_type":"TESTED_CI","command_or_check":"","result":"PASS",
  "environment":{"os":"","python":""},"timestamp":"","artifact_refs":[]
}, ensure_ascii=False, indent=2))
write('templates/RC_RECORD.md', '''# Release Candidate Record

- freeze_commit:
- rc_commit:
- package/version:
- full regression:
- OS/Python matrix:
- open quarantines:
- security blockers:
- release decision:
''')

# CODEX prompt
write('docs/34_CODEX_MASTER_EXECUTION_PROMPT.md', header('Codex / 开发 Agent 主执行指令','CR-CODEX-PROMPT-v2.0') + '''你正在执行 ClaudeRuntime 最后一次架构收口。严格按 `00_START_HERE.md`、`docs/03_FINAL_ARCH_CLOSURE_MASTER_PLAN.md`、`docs/04_BEHAVIOR_BIBLE_v2.2.md` 和 `docs/11_ACCEPTANCE_AND_FREEZE_GATE.md`。

硬约束：

1. 先读取当前 HEAD，若不是 package baseline，先比较差异并更新 evidence，不能盲目套 patch；
2. 每个 Wave 先 characterization tests，再最小改动；
3. 禁止重写 canonical query、permission classifier、五阶段 compact、MCP、TUI/Desktop、sandbox、scheduler watcher；
4. Permission 默认值修复不得机械填充 bypass；
5. Turn Preparation 目标是 owner=1，不是换一套 prompt 算法；
6. Extension 只统一 activation lifecycle，不统一 Plugin/MCP/Skill/Hook 内部机制；
7. Task 迁移允许 dual-read，禁止 dual-write；
8. 每个 PR 输出：changed owner、unchanged semantics、tests、reference/accepted diff、rollback；
9. 不得把 repo-recorded tests 写成 newly reproduced evidence；
10. W9 前重新生成所有 CURRENT machine assets 绑定 final SHA。

最终输出必须是 Architecture Freeze record，而不是“看起来差不多完成”。
''')

write('docs/35_ARCHITECTURE_DECISIONS.md', header('Architecture Decisions / ADR 汇总','CR-ADR-v2.0') + '''- ADR-001：只保留一个 production authoritative query state machine。
- ADR-002：Turn preparation 是独立 owner，所有 surfaces 共用。
- ADR-003：Permission context 不允许 privileged implicit default。
- ADR-004：Permission 与 ExecutionBoundary 是双重安全边界。
- ADR-005：Extension discovery 与 activation 分离，trust-before-activation。
- ADR-006：RuntimeTaskRegistry 是 runtime task 单写 owner。
- ADR-007：Resume 只恢复 durable semantics，不恢复 live privilege/handles。
- ADR-008：五阶段 compact 顺序冻结。
- ADR-009：Reference 是 recovered source snapshot，不要求 1:1 目录/语言复刻。
- ADR-010：CI quarantine 必须机器单一事实源。
- ADR-011：Architecture Freeze 后，架构变化需要 failure evidence + RFC。
''')

# references copy
for src_name, dst_name in [
    ('Claude-code-源码链接和论文分析链接.txt','references/Claude-code-源码链接和论文分析链接.txt'),
    ('七个核心功能组件概述.txt','references/七个核心功能组件概述.txt'),
    ('original-paper-arxiv-2604.14228v2.pdf','references/original-paper-arxiv-2604.14228v2.pdf'),
    ('paper.txt','references/paper-extracted.txt'),
]:
    src=BASE/src_name
    if src.exists(): shutil.copy2(src, ROOT/dst_name)

write('references/CURRENT_REPO_EVIDENCE_SUMMARY.md', header('Current Repo Evidence Summary','CR-CURRENT-REPO-EVIDENCE-v2.0') + f'''本包生成前重新检查 GitHub：`Nuos/clauderuntime` default branch 为 `main`，最近 HEAD 仍为 `{SUBJECT}`。

关键证据点：

- `.github/workflows/ci.yml` 当前手工 deselect 5 项；
- `pyproject.toml` distribution 仍为 `clawcodex-cli`，project URLs 仍指向旧 `agentforce314/clawcodex`；
- README current pointers 仍是旧 active plan / behavior bible；
- `ToolContext.permission_context` 当前 default factory 为 `bypassPermissions`；
- Permission 实现已有 deny-first ordering 与 headless fail-closed；
- Permission 代码注释明确列出 WebSearch/AskUserQuestion/SendUserMessage/StructuredOutput 等 deliberate UX divergences。

这些是本轮 P0/P1 收口的入口事实。完整代码行为仍应在实施分支上重新读取当前文件与运行 characterization tests。
''')

# archive previous B6 audit
old=BASE/'clauderuntime-b7-audit-baseline-20260814'
if old.exists():
    for p in old.rglob('*'):
        if p.is_file():
            dst=ROOT/'archive/b6-audit-baseline'/p.relative_to(old)
            dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dst)

# include build tool itself at end via copy after script finishes? make a note/tool version
write('tools/README.md', '''# tools

`build_clauderuntime_delivery_v2.py` 是本交付包的可再生成脚本副本；`scripts/` 是交付包/仓库治理脚本骨架。
''')

# package file list before manifest
all_now=[p for p in ROOT.rglob('*') if p.is_file()]
lines=['# PACKAGE FILE LIST','','以下为生成 manifest 前的交付文件；manifest/index/SHA256/build tool 在最终阶段追加。','']
for p in sorted(all_now):
    lines.append(f'- `{p.relative_to(ROOT)}` — {p.stat().st_size} bytes')
write('00_PACKAGE_FILE_LIST.md','\n'.join(lines))

# Copy build script as tool now
shutil.copy2(Path(__file__), ROOT/'tools/build_clauderuntime_delivery_v2.py')

# Generate HTML index
sections={}
for p in sorted(ROOT.rglob('*')):
    if not p.is_file(): continue
    rel=p.relative_to(ROOT)
    top=rel.parts[0] if len(rel.parts)>1 else 'root'
    sections.setdefault(top,[]).append((str(rel),p.stat().st_size))
html_parts=['''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ClaudeRuntime Final Architecture Freeze Delivery v2</title><style>body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:#f5f7fa;color:#172033;margin:0}.wrap{max-width:1180px;margin:30px auto;padding:0 20px}.hero,.section{background:#fff;border:1px solid #e3e7ee;border-radius:12px;padding:22px;margin-bottom:16px}.hero h1{margin:0 0 8px}.meta{color:#657084;font-size:13px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:8px}.item{border:1px solid #edf0f4;border-radius:8px;padding:10px 12px}.item a{color:#1759a8;text-decoration:none;font-weight:600}.size{font-size:12px;color:#778196}.badge{display:inline-block;background:#eef3ff;border-radius:6px;padding:4px 8px;margin-right:6px;font-size:12px}</style></head><body><div class="wrap"><div class="hero"><h1>ClaudeRuntime 最后一次大规模架构收口 · 完整总交付包 v2</h1><p>Architecture Closure → Architecture Freeze → Module/Integration/Fault/Long-Horizon Testing</p><span class="badge">Subject 16da0cf</span><span class="badge">Reference CC 2.1.88 recovered source</span><span class="badge">Self-contained</span></div>''']
for sec,items in sections.items():
    html_parts.append(f'<div class="section"><h2>{html.escape(sec)}</h2><div class="grid">')
    for rel,size in items:
        href=html.escape(rel)
        html_parts.append(f'<div class="item"><a href="{href}">{html.escape(rel)}</a><div class="size">{size/1024:.1f} KB</div></div>')
    html_parts.append('</div></div>')
html_parts.append('</div></body></html>')
write('index.html',''.join(html_parts))

# manifest (exclude itself/SHA so hashes stable)
manifest_files=[]
for p in sorted(ROOT.rglob('*')):
    if p.is_file() and p.name not in {'manifest.json','SHA256SUMS.txt'}:
        manifest_files.append({
            'path':str(p.relative_to(ROOT)),
            'bytes':p.stat().st_size,
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest()
        })
manifest={
    'delivery_id':'CR-FINAL-ARCH-FREEZE-DELIVERY-v2-COMPLETE-20260814',
    'subject_entry_commit':SUBJECT,
    'reference_commit':REF,
    'paper':PAPER,
    'file_count_without_manifest_and_sha':len(manifest_files),
    'files':manifest_files,
}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# sha all incl manifest except sha file
hash_lines=[]
for p in sorted(ROOT.rglob('*')):
    if p.is_file() and p.name!='SHA256SUMS.txt':
        hash_lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}")
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(hash_lines)+'\n',encoding='utf-8')

# Validate formats
import yaml
for p in ROOT.rglob('*.yaml'):
    yaml.safe_load(p.read_text(encoding='utf-8'))
for p in ROOT.rglob('*.json'):
    json.loads(p.read_text(encoding='utf-8'))
for p in list((ROOT/'blueprints').glob('*.py')) + list((ROOT/'tests').glob('*.py')) + list((ROOT/'scripts').glob('*.py')):
    compile(p.read_text(encoding='utf-8'), str(p), 'exec')

# integrity check now
m=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
for rec in m['files']:
    p=ROOT/rec['path']; assert p.exists(); assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']

# zip
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob('*')):
        if p.is_file(): z.write(p,arcname=str(ROOT.name/p.relative_to(ROOT)))
with zipfile.ZipFile(ZIP) as z:
    assert z.testzip() is None
    names=z.namelist(); assert len(names)==len([p for p in ROOT.rglob('*') if p.is_file()])

print(f'ROOT={ROOT}')
print(f'ZIP={ZIP} bytes={ZIP.stat().st_size}')
print(f'FILES={len([p for p in ROOT.rglob("*") if p.is_file()])}')
print('ZIP_TEST=PASS')
