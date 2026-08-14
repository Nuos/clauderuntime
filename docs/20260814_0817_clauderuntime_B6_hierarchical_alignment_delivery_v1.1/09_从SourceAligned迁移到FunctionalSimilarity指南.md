# 从 Source-Aligned 迁移到 Functional Similarity 指南

# 1. 不删除旧资料

B3/B4/B5 的 Source-Aligned 文档、source map、runtime trace、scorecard 都保留。

它们的新定位：

```text
研究资料
Reference evidence
历史审计
差异来源
```

不再是 B6 的唯一完成 Gate。

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

# 2. 术语迁移

旧：

```text
EXACT
SEMANTIC_EQUIVALENT
PYTHON_ADAPTATION_VERIFIED
PARTIAL
BLOCKED
```

B6 功能开发使用：

```text
FUNCTIONAL_COMPLETE
FUNCTIONAL_ADAPTATION
LIMITED
DEFERRED_REFERENCE_DETAIL
UNKNOWN_REFERENCE
MISSING
```

Machine parity 文件可以保留旧状态，但 progress 和 B6 dashboard 采用新状态。

---

# 3. 不要强行批量重写所有历史模块

采用“触碰即补标”原则：

```text
新增模块 → 必须标
重大修改 → 必须补标
存在已知关键差异 → 优先补标
长期不动的成熟模块 → 不要求立刻大规模改注释
```

这样避免为了文档迁移阻塞真实开发。

---

# 4. 旧 BLOCKED 的处理

重新判断：

```text
是否影响核心功能？
是否影响安全？
是否只是 Reference 实现细节？
```

如果只是 Reference 细节：

```text
DEFERRED_REFERENCE_DETAIL
```

如果核心功能已有 Python-native 实现：

```text
FUNCTIONAL_ADAPTATION
```

如果真实功能仍缺：

```text
MISSING / LIMITED
```

---

# 5. Machine Evidence 的新用途

保留 `subject_commit + manifest`，但把它从“功能完成阻塞器”变成“差异审计工具”。

建议未来新增：

```text
docs/reference-differences/registry.yaml
docs/reference-differences/generated-summary.yaml
```

而不是继续追求所有 source parity 条目 VERIFIED。

---

# 6. 最终项目声明

可以使用：

```text
Claude Code-inspired Python Agent Runtime
Functionally similar core
Python-native adaptation
```

避免使用：

```text
1:1 Claude Code clone
exact Claude Code port
fully source-aligned
behaviorally identical
```

除非未来重新恢复严格 parity 目标并重新验收。


# 严格对齐不是取消，而是缩小到可证范围

迁移后仍然必须对齐：

```text
R1_CONFIRMED 的模块/函数
R2_PARTIALLY_CONFIRMED 中能够确认的 contract/gate/call-site
安全相关已知 Reference 行为
用户可见且源码明确的关键行为
```

真正降低要求的仅是：

```text
recovered source 缺失的函数体
无法确定的内部算法
非核心实现细节
Python/OS 必须采用不同 primitive 的内部实现
```
