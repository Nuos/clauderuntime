# Current Repo Evidence Summary

> 文档编号：`CR-CURRENT-REPO-EVIDENCE-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

本包生成前重新检查 GitHub：`Nuos/clauderuntime` default branch 为 `main`，最近 HEAD 仍为 `16da0cfea98d69987739a319ff6ae42cfd432d2c`。

关键证据点：

- `.github/workflows/ci.yml` 当前手工 deselect 5 项；
- `pyproject.toml` distribution 仍为 `clawcodex-cli`，project URLs 仍指向旧 `agentforce314/clawcodex`；
- README current pointers 仍是旧 active plan / behavior bible；
- `ToolContext.permission_context` 当前 default factory 为 `bypassPermissions`；
- Permission 实现已有 deny-first ordering 与 headless fail-closed；
- Permission 代码注释明确列出 WebSearch/AskUserQuestion/SendUserMessage/StructuredOutput 等 deliberate UX divergences。

这些是本轮 P0/P1 收口的入口事实。完整代码行为仍应在实施分支上重新读取当前文件与运行 characterization tests。
