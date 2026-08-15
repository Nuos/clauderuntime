# Architecture Freeze 验收门

> 文档编号：`CR-FREEZE-GATE-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

所有 Gate 必须 PASS，不能以“后面再补测试”跳过。

## Gate A — Canonical Truth
- [ ] CURRENT machine/docs 全部绑定最终 SHA
- [ ] reference generation 唯一
- [ ] active plan 唯一
- [ ] archive 不参与 current truth

## Gate B — Canonical Loop
- [ ] production authoritative query state machine = 1
- [ ] compatibility paths 不再独立实现 loop

## Gate C — Canonical Turn Preparation
- [ ] full prompt/context/tool visibility owner = 1
- [ ] CLI/headless/server/TUI 走同一 preparation contract

## Gate D — Canonical Permission
- [ ] implicit bypass default = 0
- [ ] bypass 都有 explicit origin/reason
- [ ] headless ask fail-closed
- [ ] deliberate divergences 都已登记

## Gate E — Canonical Execution
- [ ] foreground/background/subagent/scheduler 均进入 normal execution boundary
- [ ] platform evidence 与声明分开

## Gate F — Canonical Task State
- [ ] runtime task writable owner = 1
- [ ] legacy state 无双写

## Gate G — Canonical Extension Gate
- [ ] project executable extension activation 必经 trust gate
- [ ] collision policy deterministic
- [ ] provenance 可审计

## Gate H — Canonical Persistence
- [ ] resume 不恢复 ephemeral trust/privilege/live handles
- [ ] crash-safe/atomic contracts 有测试

## Gate I — Legacy Production Paths
- [ ] 旧 owner production refs=0 或明确 compatibility-only
- [ ] `cli_backup` 有 zero-ref proof 或保留理由

## Gate J — Test Truth
- [ ] 每个 CI deselect 均登记
- [ ] quarantine 数量与 workflow 实际一致
- [ ] local/CI/platform evidence 独立
- [ ] final evidence 绑定 freeze SHA

全部通过后允许记录：`ARCHITECTURE_FREEZE`。
