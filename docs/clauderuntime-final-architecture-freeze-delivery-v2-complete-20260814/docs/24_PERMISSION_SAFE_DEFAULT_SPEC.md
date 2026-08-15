# Permission Safe Default 详细规范

> 文档编号：`CR-PERM-SAFE-DEFAULT-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 问题定义

危险不是“当前 headless 已经 bypass”，而是 constructor omission 能获得高权限。修复目标是把 omission 变成安全失败。

## 推荐实现

### 首选
`ToolContext.permission_context` 改为 required positional/keyword field。

### 兼容方案
默认 `ToolPermissionContext(mode="default", should_avoid_permission_prompts=True)`，但必须确认交互式调用点不会因此错误 deny；因此首选 required 更清楚。

## Bypass 约束

- 仅显式 CLI flag、受控内部 test harness 或受信管理策略可以申请；
- context 中记录 `bypass_origin`、`bypass_reason`；
- telemetry/evidence 可看到 bypass；
- subagent/background/scheduler 不得自行升级为 bypass。

## Regression Matrix

constructor omission、default interactive、headless、plan、acceptEdits、dontAsk、auto classifier unavailable、explicit bypass、deny rule always wins。
