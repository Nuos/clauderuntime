# PR / Commit 执行顺序

> 文档编号：`CR-PR-SEQUENCE-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

建议分 10 个 PR，任一 P0 失败可独立回滚：

1. `docs(B7): truth reset + reference lock`
2. `security(B7): remove implicit permission bypass default`
3. `runtime(B7): introduce canonical turn preparation`
4. `security(B7): extension trust-before-activation`
5. `runtime(B7): task registry single writer + session lifecycle`
6. `context(B7): compression outcome and ownership closure`
7. `runtime(B7): capability resolver + server ownership facades`
8. `ci(B7): quarantine manifest + platform/python matrix`
9. `chore(B7): identity + legacy cleanup`
10. `release(B7): architecture freeze evidence and baseline lock`

禁止把 PR 2–5 squash 成一个大型不可 bisect 变更。
