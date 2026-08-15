# Architecture Freeze 后开发规则

> 文档编号：`CR-POST-FREEZE-RULES-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

Freeze 后默认允许：bug fix、contract tests、fault injection、platform adaptation、performance fix、security hardening、compatibility fix、release engineering。

默认禁止：跨 3+ subsystem 的“顺手重构”、更换 query loop、重写 permission、重新排序 compact、另建第二 state/task system、UI 自建 policy。

若确需架构变化，必须先提交 RFC：失败证据 → 无法在现 contract 内修复的原因 → 影响 owners → migration/rollback → 新 freeze gate。
