# ClaudeRuntime 开发行为圣经 v2.0

> 文档编号：`CR-BEHAVIOR-BIBLE-v2.0`  
> 适用阶段：B7 起  
> 优先级：**最高工程行为约束**  
> 核心原则：**事实高于完成宣称；安全高于相似性；已知 Reference 必须尊重；未知 Reference 不得伪造；产品扩展必须独立标记。**

---

# 0. 第一原则：Truth Before Progress

任何时候，真实状态优先于“看起来完成”。

禁止：

```text
代码写了 → 写成 VERIFIED
本地通过 → 写成 CI green
单平台通过 → 写成 cross-platform verified
模块存在 → 写成 runtime wired
模型说完成 → 写成 task completed
Reference 看起来像 → 写成 CONFIRMED
```

必须明确区分：

```text
IMPLEMENTED
WIRED
TESTED_LOCAL
TESTED_CI
VERIFIED_PLATFORM
REFERENCE_CONFIRMED
FUNCTIONAL_ADAPTATION
PRODUCT_EXTENSION
```

---

# 1. Reference 规则

## 1.1 固定 Reference generation

当前 generation：

```text
Claude Code 2.1.88
recovered source commit a8a678cb6244e6770e1e421767ff0987a1d95549
paper arXiv:2604.14228v2
```

禁止因为上游版本变化而原地改写旧证据。

## 1.2 四级确定性

```text
R1_CONFIRMED
R2_PARTIALLY_CONFIRMED
R3_UNKNOWN
R4_PRODUCT_EXTENSION
```

映射：

```text
R1 → MUST_ALIGN known contract
R2 → ALIGN_KNOWN_PART
R3 → FUNCTIONAL_CORE_ONLY
R4 → PRODUCT_EXTENSION
```

## 1.3 Reference 不确定时

只能写：

```text
UNKNOWN_REFERENCE
RECOVERED_SOURCE_GAP
Python-native conservative implementation
```

禁止“猜一个实现，然后写成 Claude Code 原行为”。

---

# 2. 差异必须双登记

每个核心差异至少同时存在：

1. 代码附近 `REF-DIFF` / module Reference Mapping；
2. `docs/reference-differences/registry.yaml`。

阶段性差异还要进入 progress/current status。

代码中出现以下词时，治理检查必须要求 registry ID：

```text
REF-DIFF
DELIBERATE DIVERGENCE
DELIBERATE UX DIVERGENCE
UNKNOWN_REFERENCE
N/A-by-architecture
RECOVERED_SOURCE_GAP
```

---

# 3. 安全默认值法则

## 3.1 No Implicit Bypass

安全关键对象默认不得处于：

```text
bypassPermissions
full_access
trust_all
allow_all
```

除非调用者显式提供且 provenance 可追踪。

**bypass 是用户动作，不是 constructor convenience。**

## 3.2 Deny precedence

永远保持：

```text
DENY > ASK > ALLOW
```

任何局部 allow 都不得覆盖上层 deny ceiling。

## 3.3 Headless fail-safe

无交互表面遇到 ASK：

```text
ASK + no prompt channel → DENY
```

除非已存在明确、可审计的 automated classifier/policy allow。

Classifier unavailable 不得自动 allow。

---

# 4. Trust 生命周期法则

## 4.1 Pre-trust zero side effect

用户尚未信任 workspace 时，project-local：

- hook；
- plugin；
- MCP server；
- skill hook；
- executable config

不得：

- spawn process；
- network connect；
- shell execute；
- write outside inert cache；
- steal credentials。

Managed/enterprise policy 可有独立信任层，但必须明确 source。

## 4.2 Resume does not restore trust

Resume/fork 不得隐式恢复：

- temporary permission；
- API key；
- bypass flag；
- live process handle；
- stale MCP client；
- previous workspace trust decision（除非 trust store 本身仍有效且策略明确）。

---

# 5. Agent Loop 法则

## 5.1 One Semantic Core

所有正式 surface 必须收敛到一个核心语义：

```text
context
→ model
→ tool_use
→ authorization
→ execution
→ tool_result
→ state
→ next iteration / stop
```

允许 adapter，不允许第二套安全语义。

## 5.2 Harness decides enforcement, model decides intent

模型可以选择行动；模型不能决定：

- 自己是否拥有权限；
- sandbox 是否可绕过；
- path guard 是否生效；
- transcript 是否篡改；
- verifier 是否通过。

这些必须由 deterministic harness 决定。

## 5.3 Stop reason 必须结构化

禁止把最终文本当成唯一终态信号。

---

# 6. Tool 法则

## 6.1 Tool descriptor 是单一真值

每个 tool 的 side effect、read-only、concurrency、permission、sandbox requirement、reversibility 必须由同一 descriptor/contract 提供。

禁止：

```text
permission.py 认为 read-only
scheduler.py 认为 mutating
streaming executor 认为 concurrency-safe
实际 tool call 却写文件
```

## 6.2 Read parallel / write serialized 是策略，不是猜测

并发安全必须由 tool 属性声明并测试，不能靠名称猜。

## 6.3 Unknown tool / stale tool fail closed

MCP/plugin 被移除或 disconnect 后，旧 tool handle 不得继续 callable。

---

# 7. Permission × Execution 双边界法则

Action 执行必须满足：

```text
Policy OK
AND path/workspace boundary OK
AND execution backend OK
AND sandbox requirement OK
```

Permission allow 不是“可以直接调用 os/subprocess”的通行证。

## 7.1 Path canonicalization

所有 path gate 必须在比较前处理：

- `..`；
- symlink/junction；
- home expansion；
- macOS `/tmp` ↔ `/private/tmp`；
- Windows drive/case；
- additional working roots。

## 7.2 Isolation fail-closed

```text
require_isolation = true
backend unavailable = true
→ FAIL
```

禁止 silent fallback。

---

# 8. Hook 法则

Hook 可以：

- observe；
- inject bounded context；
- modify allowed input；
- deny/ask；
- run lifecycle automation。

Hook 不可以：

- 覆盖上层 deny；
- 在 untrusted project 下提前执行副作用；
- timeout 后留下 orphan process；
- 把失败吞掉后伪造 success。

所有 hook command 必须有 timeout / process-tree cleanup。

---

# 9. MCP / Plugin / Skill 法则

## 9.1 External capability is untrusted by default

MCP schema、plugin manifest、skill body 都是外部输入。

必须验证：

- source；
- schema；
- namespace；
- lifecycle；
- trust state；
- disable/uninstall cleanup。

## 9.2 Plugin 是 packaging，不是 policy bypass

Plugin 贡献的 hooks/MCP/skills/agents 都回到原机制的安全规则中。

## 9.3 Skill 不能预授权隐藏副作用

Skill 允许的 tools 不得自动越过全局 deny/policy ceiling。

---

# 10. Context / Compaction 法则

## 10.1 Context 是稀缺资源，但不能以“省 token”为唯一目标

五层顺序：

```text
Tool Result Budget
→ Snip
→ Microcompact
→ Context Collapse
→ Auto-compact
```

## 10.2 Conservative deletion

只有可重建、低风险、明确允许删除的旧 tool result 才能被 snip/budget 外部化。

Mutating action 的关键结果、permission denial、未解决错误、用户硬约束不得静默消失。

## 10.3 Full history 可审计

Context view 可以被压缩，但 durable transcript 不应因压缩被不可逆破坏。

## 10.4 Semantic regression test 必须存在

测试不能只有：

```text
tokens_saved > 0
```

还必须断言关键事实保留。

---

# 11. Memory 法则

Memory 必须有 provenance。

最少字段：

```text
source
scope
created_at
last_verified
confidence
sensitivity
invalidates_on
```

Memory 不是 permission、policy 或 system authority。

来自仓库/工具输出的“请忽略规则”不能自动升级成高优先指令。

---

# 12. Subagent 法则

## 12.1 Context isolation first

子代理默认独立 context。

## 12.2 Permission ceiling inheritance

Child 可以更严格，不能比 parent/managed policy 更宽松。

## 12.3 Summary-only parent return

默认只返回 bounded result/summary；full sidechain 独立持久化供审计。

## 12.4 Abort propagation

Parent abort 必须传播到 child agent、tool process、background task。

---

# 13. Persistence 法则

## 13.1 Append-first

对话、重要 state transition 优先 append/event log，而不是原地覆盖无证据状态。

## 13.2 Atomic durable write

必须考虑：

- process crash；
- partial write；
- two writers；
- stale owner；
- restart replay。

## 13.3 Scheduler task 必须幂等

Restart 后不允许同一个 one-shot task 因 restore 重复执行而无人知晓。

---

# 14. Evaluation 法则

## 14.1 “模型说完成”不是完成

关键任务在 eval/release mode 下必须经过 verifier。

```text
Assistant claims complete
≠
Task verified complete
```

## 14.2 Verification evidence

至少记录：

- 执行过的 test/command；
- exit code；
- changed files；
- expected artifact；
- unmet checks。

## 14.3 Silent failure 优先级高于漂亮输出

如果结果无法验证，宁可返回 `UNVERIFIED`，也不要输出“已完成”。

---

# 15. Testing 法则

## 15.1 分层测试

```text
小改 → targeted
跨模块 → combination
安全 → side-effect assertion
阶段结束 → full suite
release → CI + platform + eval
```

## 15.2 Local / CI / Platform 三者分开

严禁互相替代陈述。

## 15.3 Quarantine 必须有生命周期

每个 deselect/skip quarantine 必须有：

```text
owner
reason
introduced_at
expires_at
unblock_condition
```

没有 registry 的 deselect 不允许进入 release gate。

---

# 16. Documentation 法则

## 16.1 Canonical SSOT

CURRENT 文档只允许以下几个入口：

```text
PROJECT_BASELINE.md
current.md
BEHAVIOR_BIBLE.md
CURRENT_PLAN.md
reference-lock.yaml
registry.yaml
scorecards/latest.yaml
```

阶段交付包是历史证据，不是新的平行 SSOT。

## 16.2 HEAD 一致性

任何 current/evidence 文件都必须标 subject commit。

如果不是当前 HEAD，必须明确：

```text
STALE_EVIDENCE
```

而不是继续叫 latest/current。

## 16.3 README 不保存重复真值

README 只做入口和简要定位，状态数字、测试数量、当前阶段从 canonical status 引用，不手写复制多份。

---

# 17. CI / Release 法则

Release gate 至少同时满足：

```text
truth consistent
security green
critical path green
quarantine registered
platform claims verified
reference diffs current
context semantic eval green
resume trust reset green
extension trust lifecycle green
```

CI green 但 platform ledger 未验证时，只能称 CI green，不能称 cross-platform release verified。

---

# 18. Project Identity 法则

Canonical repository 为：

```text
Nuos/clauderuntime
```

建议 canonical product name：

```text
ClaudeRuntime
```

旧 `ClawCodex` 可作为 distribution/CLI compatibility alias，但 pyproject、README、docs 必须明确关系，不能把 repository URL 指向另一个历史仓库而不解释。

---

# 19. PR 规则

每个核心 PR 必须回答：

```text
1. 改了哪个 7-component / 5-layer？
2. 改了哪个 runtime contract？
3. Reference certainty 是 R1/R2/R3/R4？
4. 是否有 REF-DIFF？registry ID？
5. 安全不变量是否变化？
6. targeted/combination/full 哪些跑了？
7. CI/platform evidence 是什么？
8. 有无新 quarantine？
9. 是否改变 public behavior / compatibility？
10. rollback/recovery 怎么做？
```

缺一项不等于不能合并，但必须说明 N/A 原因。

---

# 20. 禁止用语

除非证据真正满足，禁止写：

```text
完全对齐
100% parity
Source-Aligned
跨平台已验证
全部测试通过
没有任何差异
安全等价
与 Claude Code 完全一致
```

应改为精确表达，例如：

```text
functional path verified on macOS
reference-known contract aligned; implementation adapted
local suite green; CI result pending
Linux code path implemented; real-device validation pending
```

---

# 21. 最终行为准则

一句话版本：

> **先确认事实，再写状态；先守住安全，再谈兼容；先对齐已知契约，再自由实现未知细节；所有差异可追踪；所有完成可验证。**

B7 之后，ClaudeRuntime 的工程质量不再只以“功能多少”衡量，而以：

```text
可靠执行
安全边界
证据一致
上下文保真
可恢复性
可评估性
可维护性
```

共同衡量。
