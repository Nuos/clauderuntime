# CI / Python / Platform Closure 规范

> 文档编号：`CR-CI-PLATFORM-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## CI 分层

1. docs-governance（Ubuntu, fast）；
2. core tests（macOS 3.12, release-gate）；
3. Python compatibility smoke（3.10/3.12/3.14）；
4. OS smoke（macOS/Ubuntu/Windows）；
5. platform-isolation verification（独立 evidence job，不能被普通 smoke 代替）；
6. optional integration（MCP/外部服务）。

## Quarantine

当前实际需要登记 5 个 deselect，全部进入 `machine/ci-quarantine.yaml`。Workflow 应通过脚本生成 pytest args；文档只引用 manifest 数量，不再复制测试名。

## Evidence Artifact

每个 CI run 至少输出：commit SHA、OS、Python、test command、passed/failed/skipped/deselected、quarantine manifest hash、timestamp。
