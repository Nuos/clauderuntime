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

- W0 Truth Reset：完成（见下方提交）
- W1–W9：待执行

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
