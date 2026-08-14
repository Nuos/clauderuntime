# ClaudeRuntime 分级 Reference 对齐开发圣经 v1.1

> 文档编号：`CR-HIERARCHICAL-REFERENCE-ALIGNMENT-BIBLE-v1.1`  
> 状态：**B6 起最高开发约束**  
> 当前 HEAD：`dc7393bb05de7dc328d5206e19ba2e15997c1656`  
> Reference：Claude Code recovered source `2.1.88`  
> 核心命令：**能确定则对齐；不能确定则功能一致；所有差异透明；安全不退化。**

---

# 核心修订：分级 Reference 对齐

> **凡是 Claude Code recovered source 能够确定的功能、模块、函数契约、关键控制行为，仍然以 Claude Code 2.1.88 为对齐目标；只有 Reference 具体实现无法确定或恢复不完整的部分，才降低为“核心功能一致 + Python-native 实现 + 差异透明记录”。**

B6 不是“所有模块都只要求功能类似”，而是：

```text
Reference 可确定
→ 必须优先对齐

Reference 部分可确定
→ 已确定部分必须对齐
→ 未确定部分允许功能类似

Reference 无法确定
→ 只要求核心功能/用户目标一致
→ 必须记录不确定性与 Python 实现

Product Extension
→ 明确与 Reference 分离
→ 不得伪装为 Claude Code 原有行为
```

| Reference 证据等级 | 定义 | 开发要求 |
|---|---|---|
| `R1_CONFIRMED` | 源文件、symbol、函数体/关键控制流能够确认 | **必须对齐功能、模块职责、关键行为和已知安全/状态语义** |
| `R2_PARTIALLY_CONFIRMED` | call-site、接口、返回契约或部分逻辑可确认，但实现体不完整 | **已确认部分必须对齐；未知部分允许 Functional Adaptation** |
| `R3_UNKNOWN` | recovered source 无法确认具体实现，只能确认功能名称/高层目的 | **只要求核心功能一致，并明确标记 UNKNOWN_REFERENCE** |
| `R4_PRODUCT_EXTENSION` | ClaudeRuntime 自己新增的功能或增强 | **独立记录，不计作 Claude Code 对齐能力** |

---

# 0. 最高原则

> **Reference 能确定的部分，不应以“Python 实现不同”为理由主动偏离；Reference 不能确定的部分，允许 Python-native adaptation，但不允许不说明不一致。**

任何关键模块/函数只要参考 Claude Code 设计或行为，都必须回答五个问题：

```text
REF：Claude Code 是什么？
PY：Python 现在是什么？
DIFF：哪里不同？
WHY：为什么不同？
STATUS：这个差异当前是否接受？
```

---

# 1. 新目标

ClaudeRuntime 不再以“逐控制流 Source-Aligned”作为核心目标，而定位为：

> **Claude Code inspired / functionally similar Python Agent Runtime。**

Reference 仍然重要，但用途从“必须复制”变成“必须理解并记录”。

---

# 2. 三个不可妥协项

## 2.1 功能不能虚假完成

`running` 必须真的在运行；`sandboxed` 必须真的有隔离；`connected` 必须真的能调用；`resumed` 必须真的重启了 Agent 生命周期。

## 2.2 安全不能用“功能类似”作为借口降低

Permission、workspace boundary、sandbox-required fail-closed、secret handling、process cleanup、trust reset 等仍是硬底线。

## 2.3 差异必须在代码附近和项目台账同时存在

只写在一个总结文档里不够。

---

# 2.1 Reference Certainty 与 Alignment Policy

核心模块/函数必须记录：

```text
REFERENCE_CERTAINTY:
  R1_CONFIRMED | R2_PARTIALLY_CONFIRMED | R3_UNKNOWN | R4_PRODUCT_EXTENSION

ALIGNMENT_POLICY:
  MUST_ALIGN | ALIGN_KNOWN_PART | FUNCTIONAL_CORE_ONLY | PRODUCT_EXTENSION
```

映射：

```text
R1_CONFIRMED → MUST_ALIGN
R2_PARTIALLY_CONFIRMED → ALIGN_KNOWN_PART
R3_UNKNOWN → FUNCTIONAL_CORE_ONLY
R4_PRODUCT_EXTENSION → PRODUCT_EXTENSION
```

对于 `R1_CONFIRMED`，Python 内部语法和 runtime primitive 可以不同，但已确认的功能、模块职责、关键函数契约、状态/失败/安全行为不得无理由偏离。

---

# 3. 强制差异记录层级

每个重要差异至少记录在以下两个位置：

```text
A. 代码附近：模块 docstring 或函数 REF-DIFF 块
B. 全局 registry：docs/reference-differences/registry.yaml
```

涉及阶段进度时还要有：

```text
C. progress 文档：本轮 Reference vs Python 差异摘要
```

---

# 4. 模块级注释规则

新增或重大修改的核心模块，模块 docstring 必须包含：

```text
Reference Mapping
Reference source
Reference behavior
Python behavior
Known differences
Reason
Functional status
```

允许简洁，不要求复制源码解释全文。

---

# 5. 函数级 REF-DIFF 规则

以下函数必须加 REF-DIFF：

- 直接对应 Reference 关键 symbol；
- 行为与 Reference 已知不同；
- 使用 Python-native adaptation；
- Reference behavior unknown；
- 安全/状态/恢复逻辑发生简化；
- 产品扩展改变 Reference 行为。

标准格式：

```python
# REF-DIFF:
# REF: query.ts::queryLoop — model -> tool -> result -> continue.
# PY:  src/query/query.py::query — Python async generator + shared ToolContext.
# DIFF: async/runtime wiring differs; user-visible loop goal is equivalent.
# WHY: PYTHON_RUNTIME_ADAPTATION.
# IMPACT: no known user-visible functional loss.
# STATUS: FUNCTIONAL_ADAPTATION.
```

---

# 6. 差异原因枚举

WHY 字段只能优先使用以下标准原因：

```text
PYTHON_RUNTIME_ADAPTATION
PYTHON_ECOSYSTEM_ADAPTATION
OS_PLATFORM_ADAPTATION
RECOVERED_SOURCE_GAP
PRODUCT_SCOPE_SIMPLIFICATION
SAFETY_STRENGTHENING
MAINTAINABILITY_SIMPLIFICATION
PERFORMANCE_OPTIMIZATION
LEGACY_COMPATIBILITY
DEFERRED_REFERENCE_DETAIL
UNKNOWN
```

不要写模糊的：

```text
“实现不一样”
“Python 原因”
“后续再看”
```

---

# 7. 差异影响必须分开记录

每项差异至少判断：

```text
user_impact: NONE | LOW | MEDIUM | HIGH
safety_impact: NONE | LOW | MEDIUM | HIGH
compatibility_impact: NONE | LOW | MEDIUM | HIGH
```

如果 safety impact 为 HIGH：

```text
不得标 FUNCTIONAL_COMPLETE
```

---

# 8. 功能状态

正式功能状态：

```text
FUNCTIONAL_COMPLETE
FUNCTIONAL_ADAPTATION
LIMITED
DEFERRED_REFERENCE_DETAIL
UNKNOWN_REFERENCE
MISSING
```

### FUNCTIONAL_COMPLETE

主要功能与 Reference 相近，用户路径完整，差异不影响核心能力。

### FUNCTIONAL_ADAPTATION

主要功能相近，但 Python 采用不同机制，例如 asyncio、snapshot persistence、不同 sandbox primitive。

### LIMITED

核心功能存在，但平台/场景有限制。

### DEFERRED_REFERENCE_DETAIL

Reference 的细节存在，但不阻塞主要功能。

### UNKNOWN_REFERENCE

Reference source 无法确认。禁止猜测后标“等价”。

### MISSING

重要功能未实现。

---

# 9. 7 个核心组件继续保留

1. User
2. Interfaces
3. Agent Loop
4. Permission System
5. Tools
6. State & Persistence
7. Execution Environment

它们现在是**功能覆盖地图**，不是 Source parity 得分表。

---

# 10. 五层架构继续保留

1. Surface Layer
2. Core Layer
3. Safety / Action Layer
4. State Layer
5. Backend Layer

只要求每层拥有稳定 Python owner 和主要能力。

---

# 11. CCR-14 继续保留但重新定位

CCR-14 继续用于防止遗漏 Harness 功能，但不再要求逐机制完全复制 Reference。

一个 CCR 可以是：

```text
FUNCTIONAL_ADAPTATION
```

例如 Scheduler 使用 Python snapshot/restore，而 Reference 使用不同 durable/file lifecycle，只要功能目标足够接近且差异被记录即可。

---

# 12. Compact 特别规则

Reference body 未恢复的 Snip：

```text
REF = call-site confirmed
PY = no-op placeholder 或 Python-native conservative snip
WHY = RECOVERED_SOURCE_GAP
STATUS = UNKNOWN_REFERENCE / FUNCTIONAL_ADAPTATION
```

禁止写：

```text
“Reference 也是 no-op”
```

除非源码确实证明。

---

# 13. Resume 特别规则

B6 不要求内部重建过程完全一致，但必须：

- transcript 可读；
- 常见服务重启场景可恢复；
- current provider/tool registry 重新解析；
- API key/temp permission 不落盘；
- 并发单 winner；
- 失败明确；
- 不制造 false-running。

worktree auto-repair/content replacement 可标 `DEFERRED_REFERENCE_DETAIL`。

---

# 14. Sandbox 特别规则

允许不同平台采用不同 primitive。

但以下文字必须真实：

```text
available
provides_isolation
platform
limitations
```

如果没有真正 isolation：

```text
provides_isolation = False
```

调用方要求 isolation 时必须 fail-closed。

---

# 15. Scheduler 特别规则

Python snapshot/restore 可以接受为 `FUNCTIONAL_ADAPTATION`。

Reference 的 file watch / cross-process owner takeover 可以延期，只要在 registry 写清楚：

```text
Reference
Current Python
Difference
Reason
Impact
Deferred status
```

---

# 16. Testing 规则

开发阶段：

```text
小改 → targeted tests
跨模块 → combination tests
阶段收尾 → full suite
```

每个差异对应的功能测试至少验证“Python 当前承诺的行为”，不再强制要求 Reference differential。

但是安全相关必须有副作用断言。

---

# 17. 开发进度规则

每次阶段进度必须出现：

```text
本轮完成
测试
Reference 对照
已知差异
差异原因
是否接受
剩余功能缺口
```

禁止只写：

```text
“已完成 / 已对齐 / 已验证”
```

---

# 18. 代码评审规则

核心模块 PR 至少检查：

```text
[ ] 功能是否可用
[ ] targeted tests 是否通过
[ ] module Reference Mapping 是否更新
[ ] function REF-DIFF 是否需要更新
[ ] registry.yaml 是否更新
[ ] progress 是否记录
[ ] 是否引入安全旁路
[ ] 是否把 UNKNOWN 错写成 Reference fact
```

---

# 19. 最终完成定义

当：

```text
核心功能 MISSING = 0
主要用户路径可工作
核心安全旁路 = 0
每个已知差异可追踪
所有 7 组件有 FUNCTIONAL_* 状态
所有 5 层有稳定 Python owner
CCR-14 不存在未说明的功能空洞
阶段 full suite 通过
```

即可宣布：

```text
FUNCTIONALLY_SIMILAR_CORE_COMPLETE
```

此状态明确**不表示**：

```text
Claude Code 2.1.88 Source-Aligned
1:1 Compatible
Exact Behavioral Clone
```
