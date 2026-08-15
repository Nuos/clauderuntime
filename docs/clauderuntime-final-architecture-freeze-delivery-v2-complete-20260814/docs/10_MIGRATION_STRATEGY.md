# 低风险迁移策略与回滚设计

> 文档编号：`CR-MIGRATION-STRATEGY-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 原则

最后一次大改最危险的是“收口过程中把成熟功能重写坏”。因此全部采用 **characterize → introduce facade → dual-read shadow → cutover → remove duplicate writer**，禁止 big-bang。

## Turn Preparation

- 先记录各 surface 输入/最终 prompt/tool visibility 快照；
- 新 service 与旧路径 shadow compare；
- 差异必须分类：bug / intentional surface diff / accepted diff；
- 生产切换后保留一轮 compatibility wrapper；
- 最后删除旧 owner。

## Task Registry

短期允许 dual-read，禁止 dual-write。写操作先迁移到 registry，再让旧 API 只读 registry projection。

## Extension Trust

先把 loader 注册动作包到 activation gate 后面，不先改 Plugin/MCP/Skill/Hook 内部实现。Gate 失败必须 rollback 未完成注册。

## Permission

constructor default 变化应先跑全量调用点 grep/static check；任何未显式传 context 的 production call site 都要明确选择 safe mode，而不是批量填 bypass。

## Rollback

每个 P0 独立 PR；不得把 Truth Reset、Permission、TurnPreparation、Extension Trust 混成一个不可回滚 PR。
