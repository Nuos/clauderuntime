# B4 修复反馈建议 v2 交付包

本包用于记录对 `Nuos/clauderuntime` 最新一轮 B4 遗留问题修复的定向评估和后续反馈建议。

## 文件
- `01_B4修复反馈建议_v2.md`：主文档。
- `01_B4修复反馈建议_v2.html`：standalone HTML，可离线直接打开。
- `02_B4问题状态矩阵_v2.json`：机器可读问题状态摘要。
- `index.html`：HTML 入口。
- `SHA256SUMS.txt`：文件校验。

## 核心结论
本轮优化有效，重点修正了 Compact early-return、Microcompact 调用形态、Project path-scoped rule 实际接线、machine evidence 错误 VERIFIED 和 taxonomy 漂移；但 Durable Resume、完整 Context-9、Snip、跨平台 Sandbox、Scheduler、全 Surface、current-HEAD CI 仍未闭合。
