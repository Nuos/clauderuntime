# 可直接转 GitHub Issues 的最终 Backlog

> 文档编号：`CR-ISSUE-BACKLOG-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## P0

1. **B7-W0 Truth Reset: canonical baseline/status/reference-lock**
2. **B7-W1 Remove implicit ToolContext bypass default**
3. **B7-W1 Register all deliberate permission divergences**
4. **B7-W2 Introduce canonical TurnPreparationService**
5. **B7-W2 Cut all production surfaces to TurnPreparationService**
6. **B7-W3 Add ExtensionActivationGate + provenance**
7. **B7-W3 Reject/resolve plugin name collisions deterministically**
8. **B7-W4 Make RuntimeTaskRegistry the only runtime-task writer**
9. **B7-W4 Define SessionLifecycle + ephemeral resume reset**
10. **B7-W7 Create CI quarantine single manifest**
11. **B7-W7 Create declared/CI/platform support matrix**
12. **B7-W9 Generate freeze evidence from final SHA**

## P1

13. `CompressionOutcome` structured contract
14. unify manual/auto compact package ownership
15. decide PostSampling additional_contexts wiring vs accepted diff
16. `ModelCapabilityResolver`
17. AgentServer ownership facade extraction
18. CompletionVerifier protocol skeleton
19. README/pyproject identity migration
20. `cli_backup` zero-ref proof + removal/exclusion

## TEST-CLOSURE

21. Windows Job Object real-device verification
22. Linux bwrap real-device verification
23. MCP crash/reconnect/auth matrix
24. Scheduler restart/missed/duplicate fire
25. Subagent abort/resume/permission ceiling
26. long-horizon multi-compact/resume
27. surface prepared-turn equivalence
28. persistence corruption/fault injection
