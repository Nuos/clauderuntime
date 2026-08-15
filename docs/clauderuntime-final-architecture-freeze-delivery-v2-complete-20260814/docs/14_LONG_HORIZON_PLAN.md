# Long-Horizon / 多轮运行验证计划

> 文档编号：`CR-LONG-HORIZON-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 场景 L1：100-turn 稳定会话

混合 Read/Grep/Bash/MCP/Skill，至少触发 3 次不同 compact stage；验证 token 预算、transcript 顺序、任务状态、无重复 side effect。

## L2：Resume × 10

同一 session 连续 10 次中断/恢复；验证 ephemeral permission/trust/handles 不复活，lineage 不丢。

## L3：后台任务 + Compact + Resume

启动 background tasks → compact → 退出 → resume；验证 persisted state 与 runtime live handle 的边界。

## L4：Scheduler 重启

注册计划任务 → runtime 重启 → 到点/错过/重复启动；验证 exactly-once 或明确 at-least-once contract。

## L5：Provider fallback

多 provider 交替失败；验证 capability snapshot、thinking config、tool schema 不因 fallback 漂移。

## L6：Extension lifecycle

project trust 从未信任→信任→撤销；验证 activation 与 session restart 行为。
