# AgentServer Session Ownership 收口

> 文档编号：`CR-SERVER-SESSION-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

不重写 server wire/concurrency，仅拆 ownership。

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
