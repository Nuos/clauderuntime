# Runtime Task / Session / Persistence 规范

> 文档编号：`CR-TASK-STATE-PERSIST-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## RuntimeTaskRegistry

负责 local shell、local agent、其他 runtime/background task 的生命周期。所有 mutate 操作走 typed registry；legacy maps 不得单独更新。

## Durable vs Ephemeral

**Durable**：task id/type/status、command/spec、timestamps、result metadata、parent session lineage。  
**Ephemeral**：Popen/thread/future/event/lock/abort controller/live MCP connection/temporary permission/trust verdict。

## Resume

Resume 只能重新构造 runtime handles；不得 deserialize 后直接信任旧 privilege。任何需要权限的重新启动动作必须重新进入 permission/execution boundary。

## Scheduler

本轮不增加跨进程 watcher/leader election。需要测试其当前 file-backed contract：load、idempotent create/delete、restart、missed fire、duplicate fire policy。
