# Eval / CompletionVerifier 最小规范

> 文档编号：`CR-EVAL-VERIFIER-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

Freeze 前只建立最小 interface：

```text
TaskContract
ExecutionTrace
EvidenceArtifact[]
Verifier.verify(...) -> CompletionDecision
```

`CompletionDecision` 至少有：`PASS / FAIL / INDETERMINATE` + reasons + evidence refs。

典型 verifier：file exists/hash、tests pass、command exit code、JSON schema、git diff constraints、user-specified acceptance checks。禁止默认让同一模型用一句“已经完成”充当 verifier。
