# Codex / 开发 Agent 主执行指令

> 文档编号：`CR-CODEX-PROMPT-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

你正在执行 ClaudeRuntime 最后一次架构收口。严格按 `00_START_HERE.md`、`docs/03_FINAL_ARCH_CLOSURE_MASTER_PLAN.md`、`docs/04_BEHAVIOR_BIBLE_v2.2.md` 和 `docs/11_ACCEPTANCE_AND_FREEZE_GATE.md`。

硬约束：

1. 先读取当前 HEAD，若不是 package baseline，先比较差异并更新 evidence，不能盲目套 patch；
2. 每个 Wave 先 characterization tests，再最小改动；
3. 禁止重写 canonical query、permission classifier、五阶段 compact、MCP、TUI/Desktop、sandbox、scheduler watcher；
4. Permission 默认值修复不得机械填充 bypass；
5. Turn Preparation 目标是 owner=1，不是换一套 prompt 算法；
6. Extension 只统一 activation lifecycle，不统一 Plugin/MCP/Skill/Hook 内部机制；
7. Task 迁移允许 dual-read，禁止 dual-write；
8. 每个 PR 输出：changed owner、unchanged semantics、tests、reference/accepted diff、rollback；
9. 不得把 repo-recorded tests 写成 newly reproduced evidence；
10. W9 前重新生成所有 CURRENT machine assets 绑定 final SHA。

最终输出必须是 Architecture Freeze record，而不是“看起来差不多完成”。
