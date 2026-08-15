# 项目身份与 Packaging 迁移

> 文档编号：`CR-IDENTITY-MIGRATION-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

当前仓库 canonical identity 为 `Nuos/clauderuntime`，但 package metadata/CLI 仍保留 `clawcodex` 历史命名。

建议分层：

- Repository/Product: `ClaudeRuntime`；
- Python distribution：可继续暂时 `clawcodex-cli` 以避免破坏安装者，或另开明确 migration；
- CLI：`clawcodex` 可作为兼容入口；若新增 `clauderuntime`，至少一个 release 周期双入口；
- Project URLs 立即改为 `Nuos/clauderuntime`；
- README 明确 canonical name / compatibility aliases；
- classifiers 只表达“意图支持”，平台验证另有 evidence matrix。

本轮不建议为了名字做包级大规模 rename/import path 迁移。
