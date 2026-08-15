# 最终 ChangeSet Checklist

> 文档编号：`CR-CHANGESET-CHECKLIST-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## W0
- [ ] reference-lock
- [ ] baseline/current/active plan SSOT
- [ ] stale SHA gate
- [ ] README pointers

## W1
- [ ] ToolContext no implicit bypass
- [ ] bypass origin/reason
- [ ] all production callsites explicit
- [ ] headless ask fail-closed tests
- [ ] deliberate permission diffs registered

## W2
- [ ] PreparedTurn type
- [ ] TurnPreparationService
- [ ] surface cutover
- [ ] QueryEngine facade only
- [ ] duplicate builder removed
- [ ] surface-equivalence tests

## W3
- [ ] ExtensionDescriptor
- [ ] trust resolver
- [ ] activation gate
- [ ] collision policy
- [ ] rollback
- [ ] plugin/skill/hook/MCP integration

## W4
- [ ] RuntimeTaskRegistry single writer
- [ ] legacy read projection
- [ ] SessionLifecycle
- [ ] persistence adapters
- [ ] resume ephemeral reset

## W5
- [ ] CompressionOutcome
- [ ] manual compact ownership
- [ ] additional_contexts decision
- [ ] multi-compact retention tests

## W6
- [ ] ModelCapabilityResolver
- [ ] AgentServer facades
- [ ] CompletionVerifier protocol

## W7
- [ ] quarantine manifest
- [ ] generated deselect args
- [ ] Python smoke matrix
- [ ] OS smoke matrix
- [ ] platform evidence records

## W8
- [ ] pyproject URLs
- [ ] identity/deprecation plan
- [ ] cli_backup zero-ref
- [ ] archive labels

## W9
- [ ] freeze gates all PASS
- [ ] final SHA evidence regenerated
- [ ] freeze record
- [ ] switch active plan to T0–T14
