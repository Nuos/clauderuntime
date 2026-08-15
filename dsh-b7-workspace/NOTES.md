# B7 架构收口工作区痕迹（dsh-b7-workspace）

> 依据交付包：`docs/clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814/`（CR-FINAL-PACK-v2.0）
> 执行方式：main 上逐 Wave 独立提交（用户指令：逐步进行完成，直接提交主 main 仓库）
> 开始：2026-08-15
> Subject baseline：`16da0cfea98d69987739a319ff6ae42cfd432d2c`（= 当前 main HEAD，与包一致）

## 执行原则

1. 每 Wave：先 characterization tests → 最小改动 → 针对性测试 → 提交推送 main。
2. 禁止重写：canonical query / permission classifier / 五阶段 compact / MCP /
   TUI-Desktop / sandbox / scheduler watcher。
3. Task 迁移：允许 dual-read，禁止 dual-write。
4. 证据口径：IMPLEMENTED / WIRED / TESTED_LOCAL / TESTED_CI / VERIFIED_PLATFORM
   / REFERENCE_CONFIRMED / ACCEPTED_DIFF；仓库已有测试记录 ≠ 本次独立复现。
5. 平台真机项（Windows Job Object / Linux bwrap / Python 3.10·3.14 / Ubuntu·Windows）
   标记 PENDING_REAL_DEVICE，不作 VERIFIED_PLATFORM。

## Wave 记录（见 WAVE_RECORD.md）

- W0 Truth Reset ✅ (486c55f)
- W1 Permission Safe-by-Default ✅ (9f3f097)
- W2 Canonical Turn Preparation ✅ (1557f2c)
- W3 Extension Trust Boundary ✅ (ade48ca)
- W4 Task/Session/Persistence Owner ✅ (b7158f0)
- W5 Context/Compact Closure ✅ (0ee21e3)
- W6 Query/Server Ownership Extraction ✅ (fa9f4df)
- W7 CI/Platform/Evidence Truth ✅ (21789fe)
- W8 Identity/Legacy Cleanup ✅ (416739a)
- W9 Freeze Gate / Baseline Lock ✅ (a01b089 + 25298ed)
- 收尾修复：sourcemap runtime 映射 + CI matrix yaml（6aabf30 + 13eb0dc）

## B7 完成状态（2026-08-15）

- **ARCHITECTURE_FREEZE**（记录 docs/progress/2026/2026-08-15-b7-architecture-freeze.md）
- 全部 Wave 直接提交推送 main（无分支/PR，按用户指令"逐步进行完成，直接提交主 main仓库"）
- 最终本地全量：10171 passed / 9 failed（7 项已知环境失败 + 2 项 sourcemap 已修复）
- 新增测试：13 个 test_b7_* 文件 136 项
- CI：docs-governance ✅；tests 与 matrix smoke 修复后应全绿（6aabf30/13eb0dc 运行中）
- 未闭合：Windows/Linux 真机隔离 PENDING_REAL_DEVICE、Python 3.10/3.14 + Ubuntu/Windows smoke 声明

## 关键文件映射（canonical truth graph）

| SSOT 资产 | 位置 |
|---|---|
| baseline | docs/baseline/PROJECT_BASELINE.md + machine/baseline.yaml |
| status | docs/status/current.md |
| active plan | docs/plans/active/CURRENT_PLAN.md |
| behavior bible | docs/governance/BEHAVIOR_BIBLE.md |
| reference lock | docs/reference/reference-lock.yaml + machine/reference-lock.yaml |
| difference registry | docs/reference-differences/registry.yaml |
| parity scorecard | docs/parity/scorecards/latest.yaml |
| 机器配置 | machine/*.yaml（12 项，均绑定 subject_commit） |
