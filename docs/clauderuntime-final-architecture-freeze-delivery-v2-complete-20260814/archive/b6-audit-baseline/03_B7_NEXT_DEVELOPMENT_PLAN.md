# ClaudeRuntime B7 下一步开发计划

> 计划编号：`CR-B7-EVIDENCE-RUNTIME-RELIABILITY-PLAN-v1.0`  
> 基线：`PROJECT_BASELINE_B7`  
> 总目标：**从“功能核心已完成”转入“证据一致、默认安全、跨平台可验证、长任务可评估”的生产化阶段。**

---

# 0. B7 不再做什么

B7 不应继续以“增加更多工具/更多 provider/更多 UI 功能”为主线。

当前最大收益来自四件事：

1. **真值统一**；
2. **安全默认值收紧**；
3. **真实平台验证**；
4. **从 observability 升级到 evaluation / verifier。**

---

# 1. 总 Workflow

```text
W0  Truth Reset / Evidence Rebase
 ↓
W1  Safe-by-Default Hardening
 ↓
W2  CI + Platform Matrix Closure
 ↓
W3  Eval / Silent-Failure Layer
 ↓
W4  Long-Horizon State & Scheduler Reliability
 ↓
W5  Context / Memory Provenance & Semantic Retention
 ↓
W6  Extension Supply-Chain & Trust Lifecycle
 ↓
W7  B7 Release Gate / Baseline Freeze
```

建议按 7–9 个小 PR 推进，避免一次大重构。

---

# 2. Wave 0 — Truth Reset（P0，必须最先）

## 目标

让仓库只存在一个 CURRENT truth。

## 工作项

### B7-W0-01 Regenerate machine evidence

以当前 main HEAD 为 subject：

```text
16da0cfea98d69987739a319ff6ae42cfd432d2c
```

重新生成：

- `docs/parity/scorecards/latest.yaml`；
- evidence manifest；
- symbol map / path map 中的 subject_commit；
- registry head。

### B7-W0-02 Dual-axis status

重写 `docs/status/current.md`：

```yaml
functional_status: FUNCTIONALLY_SIMILAR_CORE_COMPLETE
reference_parity_status: PARTIAL_NOT_RELEASE_GATE
evidence_status: CURRENT
```

删除同页“B6 已完成”与“任何 R7/R5/CCR 都未完成”并存的冲突表达。

### B7-W0-03 Supersede stale active plan

把旧 `seven-component-optimization-development-plan.md` 标为 completed/superseded，CURRENT_PLAN 指向 B7。

### B7-W0-04 Canonical project identity

更新：

- README；
- pyproject URLs；
- docs headers；
- issue/PR template（若存在）。

建议 canonical：ClaudeRuntime；`clawcodex` 仅保留 CLI/包兼容名。

### B7-W0-05 CI quarantine manifest

新增：

```text
docs/verification/ci-quarantine.yaml
```

至少记录当前 5 个 deselected tests。

## DoD

```text
[ ] current.md / scorecard / registry / baseline subject commit 一致
[ ] 当前文档不再引用旧 bible 作为最高规范
[ ] CI deselect 数量与 manifest 完全一致
[ ] docs governance 自动检查上述不变量
```

---

# 3. Wave 1 — Safe-by-Default Hardening（P0）

## 3.1 ToolContext 默认权限收紧

当前构造默认 `bypassPermissions`，生产入口通常覆盖，但 API default 仍不安全。

改为二选一：

**方案 A（推荐）**

```python
permission_context: ToolPermissionContext
```

取消默认值，所有构造点显式传入。

**方案 B**

默认 `mode="default"`，并对高风险调用无 handler 时自动 deny。

## 3.2 Bypass origin tracking

任何 bypass 必须携带：

```text
origin = cli_explicit | sdk_explicit | managed_policy
```

禁止“因为某个 helper 没传 context”产生 bypass。

## 3.3 Permission divergence registry closure

扫描代码中的：

```text
REF-DIFF
DELIBERATE ... DIVERGENCE
UNKNOWN_REFERENCE
N/A-by-architecture
```

对核心 runtime 文件逐个绑定 registry ID。

重点补：

- WebSearch gating；
- AskUserQuestion gating；
- SendUserMessage / StructuredOutput；
- plan-file exemption ordering；
- headless tool removal；
- 其他明确写“TS diverges”的行为。

## 3.4 Pre-trust extension zero-side-effect test

构造 malicious project：

```text
.claude/hooks
plugin
MCP config
skill hook
```

在 trust dialog 前断言：

- 不启动进程；
- 不连接网络；
- 不执行 shell；
- 不写用户文件；
- managed policy 例外需单独测试。

## DoD

```text
[ ] new ToolContext cannot silently bypass
[ ] all explicit bypasses traceable
[ ] known permission divergence registry coverage = 100%
[ ] untrusted project extension side effects = 0
```

---

# 4. Wave 2 — CI / Platform Matrix Closure（P0/P1）

## 4.1 CI 分层

### Fast PR gate

- docs governance；
- security invariant tests；
- core query/permission/context tests。

### Release gate

- macOS full non-integration suite；
- Ubuntu execution/sandbox smoke；
- Windows execution/process-tree smoke；
- install/import matrix。

## 4.2 Python matrix

```text
3.10  core compatibility smoke
3.12  full suite
3.14  core compatibility smoke
```

若项目实际只想支持 3.12+，则反过来收窄 pyproject；不要“广泛声明、单版本验证”。

## 4.3 Linux real sandbox

在 Ubuntu runner：

- install/probe `bwrap`；
- 写工作目录成功；
- 写 workspace 外失败；
- 默认断网验证；
- `require_isolation` + backend unavailable 必须 fail-closed。

## 4.4 Windows Job Object

Windows runner 验证：

- ctypes layout；
- suspended process resume；
- parent timeout 后 child/grandchild 清理；
- Job Object unavailable/attach fail 时 fail-closed；
- 明确：Job Object 仅 process containment，不等价于 filesystem/network sandbox。

## 4.5 Quarantine lifecycle

每个 quarantine 必须有到期条件。B7 release 前至少要做到：

```text
unregistered deselect = 0
expired quarantine = 0
```

---

# 5. Wave 3 — Eval / Silent-Failure Layer（P1，B7 核心新增）

论文指出 production agent 的关键缺口不是“看不到 trace”，而是**看到了 trace 仍不能判断任务是否真的完成**。

ClaudeRuntime 已有 trace、turn steps、transcript、tool results；B7 应建立正式 Eval Layer。

## 5.1 Task Contract

定义机器可读任务完成条件：

```yaml
objective:
required_artifacts:
verification_commands:
forbidden_regressions:
completion_policy:
```

## 5.2 Verifier API

建议独立于主生成模型：

```python
VerificationResult(
    passed: bool,
    evidence: list[Evidence],
    failures: list[Failure],
    confidence: str,
)
```

## 5.3 Completion gate

Agent 最终文本说“完成”不等于 success。

```text
agent_stop
→ verifier
→ passed ? SUCCESS : CONTINUE / FAIL
```

支持关闭，但 release/eval 模式必须开启。

## 5.4 Trace replay

对关键 turn trace 提供：

- deterministic-ish replay fixture；
- no-model fake provider replay；
- permission/tool/context invariants replay。

## 5.5 Silent failure corpus

首批至少覆盖：

1. 修改了错误文件但模型说完成；
2. 测试未运行但模型声称 tests pass；
3. subagent summary 丢关键 failure；
4. compact 后忘记用户约束；
5. MCP 工具 stale 但模型继续调用；
6. scheduler firing 后实际没有完成任务；
7. background task 被 abort 后仍有 child process；
8. permission denied 后模型错误声称动作已执行。

---

# 6. Wave 4 — Long-Horizon State / Scheduler Reliability（P1）

Scheduler file-backed persistence 是 B6 的正确起点，但“能 restore”不等于“长时间可靠”。

## 6.1 Durable task state machine

建议固定：

```text
CREATED
→ CLAIMED
→ RUNNING
→ VERIFYING
→ COMPLETED
  or RETRYABLE_FAILED
  or TERMINAL_FAILED
  or CANCELLED
```

## 6.2 Idempotency

对 one-shot/recurring task 引入 execution id / idempotency key，避免 restart 后双跑。

## 6.3 Crash-recovery tests

故障注入：

- 写文件一半 kill；
- schedule fire 前 kill；
- tool running 时 kill；
- verify 前 kill；
- restart 两个进程竞争 restore。

## 6.4 Goal persistence

把“任务完成”绑定 verifier，不仅绑定最后 assistant text。

---

# 7. Wave 5 — Context / Memory Provenance（P1/P2）

## 7.1 Semantic retention corpus

Compaction 测试从 token saved 升级为“语义不变量保持”：

- 用户硬约束；
- 修改文件集合；
- 未解决错误；
- permission denial；
- active plan；
- background task status；
- loaded path rule；
- subagent unresolved warning。

## 7.2 每层 trace

每个 shaping layer 记录：

```text
before_tokens
after_tokens
saved_tokens
reason
affected_message_ids
reconstructible
visible_to_user
```

## 7.3 Memory provenance

每条 durable memory 增加：

```text
source
created_at
last_verified
scope
confidence
sensitivity
invalidates_on
```

## 7.4 Injection / invisible Unicode scan

对进入高优先 context 的项目文件、memory、plugin instructions 增加可配置扫描，检测明显 prompt injection markers、不可见字符、伪装 policy blocks。

注意：扫描是风险信号，不应把正常代码文本误判成“安全策略”。

---

# 8. Wave 6 — Extension Supply Chain（P1/P2）

## 8.1 MCP identity

每个 server/tool 必须可追踪：

```text
server_id
transport
source_scope
config_file
trust_state
version/hash
last_connected
```

## 8.2 Plugin lifecycle

Plugin 安装、enable、load、disable、uninstall 需要明确 lifecycle；plugin contribution（hooks/skills/MCP/agents）必须在卸载后全部撤销。

## 8.3 Namespace collision

built-in 与 MCP/plugin tool 同名时：

- deterministic precedence；
- warning/audit；
- deny rule 使用 canonical fully-qualified name；
- 不允许 shadowing 悄悄改变高风险行为。

## 8.4 Dependency provenance

Reference recovered source 只用于研究/对照；ClaudeRuntime 自有代码、第三方依赖、复制片段的 provenance 要能区分。若存在大段直接恢复源码翻译/复制，需要单独做许可/IP review，不应仅靠“Reference”标签处理。

---

# 9. Wave 7 — B7 Release Gate

B7 最终只接受机器可证明的 gate。

## 9.1 Gate A：Truth

```text
status/head/registry/scorecard/reference-lock 全一致
```

## 9.2 Gate B：Safety

```text
P0 security open = 0
untrusted extension side effect = 0
implicit bypass construction = 0
require_isolation silent fallback = 0
```

## 9.3 Gate C：Platform

```text
macOS verified
Linux verified
Windows containment verified + limitation disclosed
```

## 9.4 Gate D：Eval

```text
critical silent-failure corpus = green
completion requires verifier in eval/release mode
```

## 9.5 Gate E：Context

```text
semantic retention corpus = green
five-stage pipeline trace complete
```

## 9.6 Gate F：Docs

```text
current docs = generated/validated against executable state
quarantine manifest exact
no stale active plan
```

---

# 10. 推荐 PR 切分

| PR | 内容 | 优先级 |
|---|---|---|
| B7-PR1 | Truth Reset + baseline + docs SSOT | P0 |
| B7-PR2 | Permission safe default + divergence registry closure | P0 |
| B7-PR3 | CI quarantine manifest + Python matrix | P0/P1 |
| B7-PR4 | Linux/Windows real platform gate | P0/P1 |
| B7-PR5 | Task Contract + Verifier + completion gate | P1 |
| B7-PR6 | Long-horizon scheduler/task state + crash recovery | P1 |
| B7-PR7 | Context semantic corpus + memory provenance | P1 |
| B7-PR8 | MCP/plugin lifecycle & supply-chain controls | P1/P2 |
| B7-PR9 | B7 evidence regenerate + release closure | P0 |

---

# 11. B7 完成定义

```text
B7_COMPLETE =
  B6 functional core remains green
  AND current truth is internally consistent
  AND no implicit permission bypass default exists
  AND all known core divergences are registered
  AND platform claims are verified on their actual OS
  AND CI quarantine is explicit and bounded
  AND verifier-backed completion exists
  AND context semantic preservation is regression-tested
  AND durable task recovery is idempotent
  AND release evidence is generated from release commit
```

建议最终状态名：

```text
EVIDENCE_BACKED_RUNTIME_BASELINE_COMPLETE
```

它仍不等于 `Claude Code 1:1 Clone`。
