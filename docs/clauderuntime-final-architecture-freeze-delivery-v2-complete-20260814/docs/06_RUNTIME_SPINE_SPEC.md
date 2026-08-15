# 最终 Runtime Spine 与 Authority Boundary

> 文档编号：`CR-RUNTIME-SPINE-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 1. 唯一生产主脊柱

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
