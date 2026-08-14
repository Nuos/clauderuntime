# B6 v1.1 修订说明：分级 Reference 对齐

> 修订时间：2026-08-14  
> 基线仓库 HEAD：`dc7393bb05de7dc328d5206e19ba2e15997c1656`

本修订纠正 v1.0 中可能造成误解的一点：

> **B6 并不是把全部 Claude Code 对齐要求降成“功能类似”。**

正式原则：

```text
能确定的 → 继续对齐
部分确定的 → 已知部分对齐，未知部分功能一致
不能确定的 → 核心功能一致 + 明确注释
产品扩展 → 单独标记
```

只有 `R3_UNKNOWN`，或者 `R2_PARTIALLY_CONFIRMED` 的未知部分，才进入 `FUNCTIONAL_CORE_ONLY`。

对于 `R1_CONFIRMED`，功能、模块职责、关键函数契约、关键控制行为仍以 Claude Code 2.1.88 为对齐基准。Python 可以采用不同语言 primitive，但不得借“Python-native”之名无理由改变已经能够确认的 Reference 行为。
