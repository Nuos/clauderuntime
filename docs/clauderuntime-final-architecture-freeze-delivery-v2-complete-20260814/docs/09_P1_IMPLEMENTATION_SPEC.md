# P1 Implementation Spec

> 文档编号：`CR-P1-IMPLEMENTATION-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 1. AgentServer owner facades

不改变 WebSocket / worker thread / permission Event roundtrip。只把 `_AgentSession` 中不同生命周期对象放入明确子对象，减少测试时“一改全 session”。

## 2. ModelCapabilityResolver

把 adaptive thinking、streaming/tool schema/cache capability 等 model/provider 判定集中，query 读取 immutable snapshot。不要在 query.py 与 model_call.py 分别维护 allowlist。

## 3. CompressionOutcome

所有压缩入口返回结构化结果：

```python
changed: bool
stage: str | None
warnings: tuple[str,...]
hard_limit_reached: bool
artifacts: tuple[str,...]
tokens_before: int | None
tokens_after: int | None
```

manual compact 与 automatic pipeline 共用 contracts/types，但不混淆产品语义。

## 4. CompletionVerifier

Freeze 前只定义 protocol 与最小 wiring，不建立“大型评测平台”。Verifier 应消费 task contract + trace/evidence，而不是要求模型再次自评。

## 5. Legacy Cleanup

`cli_backup`、旧 compatibility helpers、deprecated docs 的删除必须先有 zero-production-ref 证据。无法证明时先标 deprecated，不强删。
