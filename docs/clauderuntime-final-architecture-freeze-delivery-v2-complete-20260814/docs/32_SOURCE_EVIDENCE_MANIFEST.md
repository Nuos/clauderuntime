# 来源与证据边界

> 文档编号：`CR-SOURCE-EVIDENCE-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 用户提供来源

- `references/Claude-code-源码链接和论文分析链接.txt`
- `references/original-paper-arxiv-2604.14228v2.pdf`
- `references/七个核心功能组件概述.txt`

## Reference 解释

源码链接指向 `ChinaSiro/claude-code-sourcemap`，属于从 source map 恢复的 2.1.88 snapshot；本包严格使用 “recovered source/source-map snapshot” 表述。

## 当前仓库入口证据

本轮重新检查 `Nuos/clauderuntime`，current main HEAD 仍为本包 subject SHA。关键现状依据包括：CI 当前手工 deselect 5 项、pyproject 仍保留 `clawcodex-cli`/旧 URLs、README 仍指向旧 active plan/bible、ToolContext 默认 bypass、Permission deliberate UX divergence 注释。

## 不应过度声称

本环境未重新独立执行目标仓库 10k+ 全套测试，因此历史的 `10212 passed` 等只属于 repo-recorded evidence。平台 isolation 也不可在无真机证据时写成 verified。
