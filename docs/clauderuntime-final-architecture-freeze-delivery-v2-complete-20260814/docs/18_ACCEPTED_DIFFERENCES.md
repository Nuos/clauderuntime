# Reference 差异与 Product Extension 管理

> 文档编号：`CR-ACCEPTED-DIFFS-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 1. 规则

差异不等于缺陷。每个差异必须标为：`FUNCTIONAL_ADAPTATION / PRODUCT_EXTENSION / ACCEPTED_DIFF / DEFERRED_REFERENCE_GAP`，并给 evidence 与风险。

## 2. 当前必须补登记的 Permission UX 差异候选

- WebSearch：Python 项目选择低风险 read-only 自动允许；
- AskUserQuestion：交互本身视为 gate，避免重复 permission prompt；
- SendUserMessage；
- StructuredOutput；
- Skill：本项目通过内部 shell/tool 正常 permission，而非完全复制 Reference allowed-tools 预授权语义。

这些差异需要逐条 registry，不应仅写在代码注释。

## 3. 已知架构/平台差异

- Python-native Snip / Compact implementation details；
- Scheduler file-backed persistence 与 watcher/owner-takeover 差异；
- Windows/Linux/macOS isolation implementation；
- surface event envelope；
- worktree resume repair gap。

## 4. Product Extensions

Bridge/Remote、Coordinator/Workflow、部分 provider / advisor / task enhancements 可作为 Product Extension，但不得改变 canonical query / permission / execution policy 的 authority。
