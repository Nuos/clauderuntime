# Architecture Decisions / ADR 汇总

> 文档编号：`CR-ADR-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

- ADR-001：只保留一个 production authoritative query state machine。
- ADR-002：Turn preparation 是独立 owner，所有 surfaces 共用。
- ADR-003：Permission context 不允许 privileged implicit default。
- ADR-004：Permission 与 ExecutionBoundary 是双重安全边界。
- ADR-005：Extension discovery 与 activation 分离，trust-before-activation。
- ADR-006：RuntimeTaskRegistry 是 runtime task 单写 owner。
- ADR-007：Resume 只恢复 durable semantics，不恢复 live privilege/handles。
- ADR-008：五阶段 compact 顺序冻结。
- ADR-009：Reference 是 recovered source snapshot，不要求 1:1 目录/语言复刻。
- ADR-010：CI quarantine 必须机器单一事实源。
- ADR-011：Architecture Freeze 后，架构变化需要 failure evidence + RFC。
