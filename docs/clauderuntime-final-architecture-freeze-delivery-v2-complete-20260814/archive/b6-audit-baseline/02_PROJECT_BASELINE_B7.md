# ClaudeRuntime 项目基线 B7

> 文档编号：`CR-PROJECT-BASELINE-B7-v1.0`  
> 生效建议：B7 开始  
> 项目：`Nuos/clauderuntime`  
> Subject HEAD：`16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference Source：Claude Code `2.1.88` recovered source @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> Reference Paper：arXiv:2604.14228v2  
> 基线目的：**把 B6 完成态冻结为可审计事实，并为 B7 建立唯一开发真值。**

---

# 1. 项目身份

## 1.1 Canonical Identity

B7 起建议统一：

```text
Repository:      Nuos/clauderuntime
Project name:    ClaudeRuntime
Runtime type:    Python Agent Runtime / Coding Agent Harness
Legacy alias:    ClawCodex
CLI compatibility command: clawcodex（暂保留）
```

`ClawCodex` 可作为历史兼容名称存在，但文档、issue、baseline、release note 应以 **ClaudeRuntime** 为主名。

## 1.2 项目定位

ClaudeRuntime 是：

> **以 Claude Code recovered source 2.1.88 与 Dive into Claude Code 架构分析为主要 Reference、采用 Python-native 实现的 production-oriented agent runtime。**

它的目标不是逐行翻译 TypeScript，也不是声称是 Claude Code 的官方实现。

---

# 2. Reference Lock

B7 reference 不允许漂移：

```yaml
reference_generation: CC-2.1.88-G1
source_repo: https://github.com/ChinaSiro/claude-code-sourcemap
source_version: 2.1.88
source_commit: a8a678cb6244e6770e1e421767ff0987a1d95549
paper: arXiv:2604.14228v2
paper_title: Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems
```

任何后续 Claude Code 新版本不得静默覆盖本 generation。升级 Reference 必须创建 `G2/G3...` 并保留 G1 对照。

---

# 3. 当前状态必须分成两条轴

从 B7 起禁止用一个“完成/未完成”字段同时表达功能与 parity。

## 3.1 Functional Axis

```text
FUNCTIONALLY_SIMILAR_CORE_COMPLETE
```

含义：主要用户路径与核心 harness 功能已可运行，关键失败路径、安全边界与测试存在。

## 3.2 Reference Parity Axis

```text
PARTIAL_NOT_RELEASE_GATE
```

含义：Reference-confirmed 核心语义大量对齐，但不是 1:1 Source-Aligned，仍存在 accepted adaptation、unknown implementation、platform limitation。

## 3.3 Evidence Axis

当前 B7 入场时先标：

```text
REBASE_REQUIRED
```

原因：旧 scorecard/registry/active plan 的 subject commit 不全部等于当前 main HEAD。

---

# 4. 正式架构基线

## 4.1 七个高层组件

唯一正式 7 组件：

1. **User**
2. **Interfaces**
3. **Agent Loop**
4. **Permission System**
5. **Tools**
6. **State & Persistence**
7. **Execution Environment**

Context/Memory、Hooks、MCP、Plugins、Skills、Subagents 是跨组件或子系统能力，不新增“第八组件”。

## 4.2 五层 Subsystem

唯一正式 5 层：

1. **Surface Layer**
2. **Core Layer**
3. **Safety / Action Layer**
4. **State Layer**
5. **Backend Layer**

## 4.3 核心运行脊柱

```text
User / Surface
  ↓
Context Assembly
  ↓
Agent Loop
  ↓
Model Response
  ↓
Tool Request
  ↓
Permission / Hooks / Safety Gate
  ↓
Execution Boundary / Sandbox
  ↓
Tool Result
  ↓
State / Transcript
  ↓
Agent Loop Continue or Stop
```

这个数据流是 B7 的核心架构不变量。

---

# 5. Agent Loop 基线

## 5.1 唯一核心循环原则

所有正式 surface 必须最终进入同一语义 core：

```text
model → tool_use → authorize → execute → tool_result → model
```

允许 adapter 不同，不允许存在第二套具有不同 permission/context/recovery 语义的隐式 loop。

## 5.2 明确终态

至少支持：

```text
SUCCESS
NO_TOOL_USE
MAX_TURNS
MAX_COST
PROMPT_TOO_LONG
HOOK_STOPPED
ABORTED
MODEL_ERROR
TOOL_FAILURE_RECOVERED / TERMINAL_FAILURE
```

终态必须可追踪、可测试，不能用自然语言猜测。

---

# 6. Context / Memory 基线

## 6.1 五层 Compaction 顺序

B7 固定保持：

```text
1. Tool Result Budget
2. Snip
3. Microcompact
4. Context Collapse
5. Auto-compact
```

允许 Python-native 算法差异，但：

- 顺序变化必须有 RFC/DIFF；
- 不能把 mutating tool 的关键结果无证据删除；
- compact 不得破坏可恢复 transcript；
- compact 后必须恢复必要 runtime attachments / file state / rules；
- 每层输出 observability metadata。

## 6.2 Memory 原则

Memory 必须：

- 用户可见、可编辑；
- 来源/作用域可追踪；
- 不覆盖 permission policy；
- 不因 resume 自动恢复旧 trust；
- 可标 stale / invalidated；
- 对外来内容执行 injection/suspicious content scan（B7 增强项）。

---

# 7. Permission / Trust 基线

## 7.1 默认安全姿态

**默认不得是 bypass。**

```text
DENY > ASK > ALLOW
```

任何 bypass 必须由显式用户/managed policy 决定，且来源可审计。

## 7.2 Permission 与 Execution 是两道边界

```text
Permission says YES
AND
Execution boundary permits
AND
Sandbox requirement satisfied
```

任何一个失败，action 不得执行。

## 7.3 Trust 生命周期

- project-local hook/plugin/MCP 在 untrusted workspace 下不得执行副作用；
- resume/fork 不恢复 temporary permission / API key / session trust；
- background/subagent 不得降低 parent 的 policy ceiling；
- stale MCP connection 被清理后对应 tools 必须失效。

---

# 8. Tool / Extensibility 基线

## 8.1 Tool Descriptor 必备字段

每个正式 tool 应可描述：

```text
name
side_effect_class
read_only
concurrency_safe
permission_class
sandbox_requirement
result_budget_class
reversible
namespace/source
```

## 8.2 四类扩展面

B7 保持与 Reference 相同的概念边界：

- MCP：外部 tool/resource/service；
- Plugin：多组件打包与分发；
- Skill：按需注入领域指令/能力；
- Hook：生命周期拦截与 policy/control。

Plugin 不是“另一个 Agent Loop”，Hook 也不能绕过 deny-first。

---

# 9. Subagent 基线

Subagent 默认：

- context isolation；
- tool/permission scope 显式；
- parent policy ceiling 不可被 child 放宽；
- full transcript 独立保存/sidechain；
- parent 只接收 bounded summary/result；
- background abort 必须传播；
- worktree/remote/in-process capability 必须如实标注。

---

# 10. State / Persistence 基线

## 10.1 Durable State

优先 append-first、可审计、可重放。

## 10.2 Resume

Resume 只能恢复：

- 对话/消息状态；
- 可安全重建的 runtime metadata；
- 当前进程重新解析后的 provider/tool registry；
- 已持久化但不敏感的 task/scheduler 状态。

Resume **禁止**恢复：

- API key；
- provider client object；
- temporary allow；
- bypass flag 的隐式继承；
- AbortController / live process handle；
- stale MCP callable object。

---

# 11. Execution Environment 基线

## 11.1 平台状态

B7 入场状态：

| 平台 | 状态 |
|---|---|
| macOS | code path verified；当前受管环境 Seatbelt probe blocked |
| Linux | `PENDING_REAL_DEVICE` |
| Windows | `PENDING_REAL_DEVICE` |

## 11.2 Fail-closed

只要调用方声明 `require_isolation=true`：

```text
backend unavailable
→ DENY / FAIL
```

绝不能自动退化成 unrestricted execution。

---

# 12. Python / Build 基线

当前 package metadata 声明：

```text
requires-python >= 3.10
classifiers: 3.10–3.14
```

B7 把“支持”拆为：

- **Declared support**：pyproject 所声明；
- **CI verified support**：CI 实际运行；
- **Platform verified support**：对应 OS 真机执行关键边界测试。

建议 B7 release 目标：

```text
Full suite: Python 3.12 / macOS
Core smoke: Python 3.10 + 3.14
Platform smoke: macOS + Ubuntu + Windows
```

---

# 13. Canonical 文档真值路径

B7 起建议只有以下文件具有 CURRENT 权威：

```text
docs/baseline/PROJECT_BASELINE.md
docs/status/current.md
docs/governance/BEHAVIOR_BIBLE.md
docs/plans/active/CURRENT_PLAN.md
docs/reference/reference-lock.yaml
docs/reference-differences/registry.yaml
docs/parity/scorecards/latest.yaml
```

阶段交付目录、旧 B3/B4/B5/B6 文档只能是 historical evidence，不再作为“当前开发规范”的入口。

---

# 14. Evidence Baseline

每次声称“完成”必须同时回答：

```text
SUBJECT_COMMIT
REFERENCE_GENERATION
CODE_EVIDENCE
TEST_EVIDENCE
CI_EVIDENCE
PLATFORM_EVIDENCE
KNOWN_DIFFS
BLOCKERS
```

没有 subject commit 的“已完成”一律视为陈述不完整。

---

# 15. Release Gate

一个 release candidate 至少必须满足：

1. `docs/status/current.md` 与机器 scorecard 不冲突；
2. registry `repository_head` = release subject commit；
3. P0 security invariants 0 open；
4. CI quarantine 0 未登记项；
5. Windows/Linux/macOS 的声明与真实验证一致；
6. critical paths smoke 全绿；
7. context semantic corpus 无阻塞回归；
8. resume 不恢复 session trust；
9. MCP/plugin/hook pre-trust gate 通过；
10. release evidence bundle 可复现。

---

# 16. B7 入场未闭合项

```text
B7-ENTRY-01  current/status/scorecard/registry HEAD 统一
B7-ENTRY-02  ToolContext permissive constructor default 收紧
B7-ENTRY-03  permission deliberate divergences 完整登记
B7-ENTRY-04  CI quarantine 从散落注释变成单一 manifest
B7-ENTRY-05  Linux/Windows 真机安全验证
B7-ENTRY-06  README / pyproject 项目身份与 canonical docs 修正
```

这些是 B7 第一个 Wave 的工作，不应继续被新的功能 PR 淹没。
