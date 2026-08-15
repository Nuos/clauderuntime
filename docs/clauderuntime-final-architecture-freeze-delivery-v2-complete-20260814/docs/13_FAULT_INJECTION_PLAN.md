# Fault Injection 测试计划

> 文档编号：`CR-FAULT-PLAN-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

| 故障 | 注入点 | 期望 |
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
