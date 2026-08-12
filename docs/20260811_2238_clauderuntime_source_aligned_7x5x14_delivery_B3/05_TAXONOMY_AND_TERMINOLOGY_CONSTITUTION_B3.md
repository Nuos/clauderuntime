# ClaudeRuntime B3 分类与术语宪法

# 1. 三个主坐标系

## Reference-7

回答：**系统由哪些核心功能组件组成？**

- User
- Interfaces
- Agent Loop
- Permission System
- Tools
- State & Persistence
- Execution Environment

## Reference-5

回答：**这些能力位于什么 subsystem architecture layer？**

- Surface
- Core
- Safety / Action
- State
- Backend

## CCR-14

回答：**核心组件之间靠什么横切式 Harness / Runtime Mechanism 连接？**

- Hook Runtime
- Authorization Pipeline
- Context Shaping
- Context Assembly
- Capability Assembly
- Tool Orchestration
- Streaming Tool Execution
- Recovery
- Result Processing/Budget
- Session/Transcript
- Subagent Orchestration
- Isolation
- Trust Lifecycle
- Runtime Config

# 2. 不同分类不能平铺

以下都属于不同问题维度：

| 分类 | 回答 |
|---|---|
| Values | 为什么这样设计 |
| Design Principles | 按什么原则设计 |
| Reference-7 | 有什么核心功能 |
| Reference-5 | 功能位于哪层 |
| CCR-14 | 模块之间如何连接 |
| 9-step Turn Pipeline | 一次 turn 如何运动 |
| Compact-5 | context 太多如何处理 |
| Safety Layers | 安全如何纵深防御 |
| Permission Modes | 当前信任/自治模式 |
| Permission Behavior | 单次 action 的 allow/deny/ask |
| Tool Pool Stages | 模型本轮能看见什么能力 |
| Lifecycle Obligations | 具体运行路径必须验证什么 |

# 3. Policy / Permission / Authorization / Isolation 的区别

```text
Policy / Permission
= 规则、模式、决策语义

Authorization Pipeline
= 一次 action 的规则求值与升级/裁决过程

Isolation
= 即使 action 被允许，仍限制其资源可见范围和副作用边界

Execution Environment
= 实际执行能力与 backend
```

四者不可合并。

# 4. Context / State / Transcript / Memory 的区别

```text
Context
= 本轮模型看到的 working projection

State
= 当前运行时可变状态

Transcript
= durable 会话事实与 lineage

Memory / Instructions
= 跨 turn / session 的显式知识或指令来源
```

Compaction 改变 Context projection，不应伪造 Transcript。

# 5. Tool 四分法

```text
Registry       = 存在哪些 Tool descriptor
Pool Assembly  = 本轮模型能看到哪些 Tool
Orchestration  = 多个 tool call 怎么调度
Execution      = 一个已批准 action 如何真正运行
```

# 6. Source-Aligned 状态词

完成：

- EXACT
- SEMANTIC_EQUIVALENT
- PYTHON_ADAPTATION_VERIFIED

未完成：

- PARTIAL
- UNKNOWN
- MISSING

不计入 core completion：

- PRODUCT_EXTENSION
- INTENTIONAL_DIVERGENCE
