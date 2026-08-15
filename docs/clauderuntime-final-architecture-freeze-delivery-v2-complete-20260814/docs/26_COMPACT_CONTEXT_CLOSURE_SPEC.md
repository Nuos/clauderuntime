# Context / Compact 最终收口规范

> 文档编号：`CR-COMPACT-CLOSURE-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 固定 stage 顺序

`applyToolResultBudget → snipCompactIfNeeded → microcompact → contextCollapse.applyCollapsesIfNeeded → autocompact`

## 本轮允许改变

- return outcome type；
- manual compact 的 package ownership；
- telemetry/evidence；
- additional contexts wiring/accepted diff；
- retention tests。

## 本轮禁止改变

- stage 顺序；
- token thresholds 的大规模重新设计；
-另建第二 compact pipeline。

## PostSampling additional_contexts

必须二选一：

1. 正式定义 injection lane，进入下一 turn prepared context；
2. 明确 registry accepted diff，API 不再暗示“支持但丢弃”。
