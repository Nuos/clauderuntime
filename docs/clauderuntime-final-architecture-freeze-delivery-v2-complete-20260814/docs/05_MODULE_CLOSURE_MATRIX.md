# 全模块 Closure Matrix

> 文档编号：`CR-MODULE-CLOSURE-MATRIX-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

| 模块 | 当前判断 | Freeze 前动作 | Freeze 后主要动作 |
|---|---|---|---|
| Query loop | Mature / dense | 仅抽外围 owner | fault / retry / abort / long-horizon |
| Turn preparation | Dual owner | **P0 合并为 1 owner** | surface parity tests |
| Permission | Mature / unsafe default | **P0 safe default + diff registry** | fuzz / policy matrix |
| Tools | Mature | 不重构 | per-tool contracts / side-effect tests |
| Tool execution | Mature | owner naming/telemetry | hook/error/concurrency tests |
| Execution boundary | Mature | 不改设计 | OS matrix / escape tests |
| Sandbox | Limited evidence | 不重构 | real-device verification |
| Context assembly | Mature / duplicated | **P0 owner merge** | provenance/retention tests |
| Compact pipeline | Mature | P1 outcome + package ownership | multi-compact stress |
| State | Mature / owner spread | P1 SessionLifecycle | crash/restart/atomicity |
| Resume/Fork/Rewind | Usable | ephemeral-state drop contract | corruption/missing-worktree |
| RuntimeTaskRegistry | New SoT but legacy coexist | **P0 single writer** | race/idempotency |
| Scheduler | Usable | 不加 watcher | restart/missed/duplicate fire tests |
| Hooks | Mature | trust + additional context decision | timeout/failure/HTTP tests |
| MCP | Mature | trust lifecycle linkage | auth/reconnect/crash/namespace |
| Plugins | Usable | **P0 trust activation + collision** | supply-chain tests |
| Skills | Usable | trust source linkage | shell/tool permission tests |
| Subagent | Mature | permission ceiling contract | abort/resume/sidechain |
| AgentServer | Mature / God Session | P1 owner facade | concurrency/wire tests |
| CLI/Headless | Mature | explicit TurnPreparation | surface consistency |
| TUI/Desktop | Mature | 不重写 | protocol/surface contract |
| Providers | Rich | P1 capability resolver | compatibility matrix |
| Worktree | Usable | accepted gap registry | dirty/missing/resume tests |
| Memory | Usable | provenance schema | staleness/compact retention |
| Bridge/Remote | Product extension | 与 core 隔离 | dedicated integration tests |
| Coordinator/Workflow | Product extension | 与 core policy 不竞争 | orchestration tests |
| Docs/Parity | Drift | **P0 SSOT reset** | auto-governance |
| CI | Green but manual quarantine | **P0 manifest/matrix** | flaky reduction |
| Eval/Verifier | Partial | P1 protocol skeleton | scenario evaluation |
