# 风险台账与 Stop-the-Line 条件

> 文档编号：`CR-RISK-REGISTER-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

| ID | 风险 | 等级 | Stop-the-line 条件 | 对策 |
|---|---|---|---|---|
| R1 | safe default 改动导致入口全被 deny | P0 | 基本 CLI/headless 失效 | callsite inventory + targeted migration |
| R2 | TurnPreparation cutover prompt/tool 漂移 | P0 | surface snapshot diff 未解释 | shadow compare |
| R3 | Trust gate 阻断 managed/bundled extensions | P0 | bundled regression | source-specific policy tests |
| R4 | Task registry 切换丢后台任务 | P0 | task lifecycle mismatch | dual-read, single-write migration |
| R5 | AgentServer facade 改坏并发 | P1 | deadlock/event loss | ownership only, no protocol rewrite |
| R6 | quarantine manifest 漏掉真实 deselect | P0 | workflow != manifest | generated args only |
| R7 | identity rename 破坏 CLI | P1 | existing command broken | alias/deprecation |
| R8 | Freeze 文档绑定旧 SHA | P0 | subject mismatch | machine gate |
