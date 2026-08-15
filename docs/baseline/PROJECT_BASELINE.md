# Project Baseline

status: CURRENT
owner: repository-governance
created: 2026-08-15
last_verified: 2026-08-15
subject_commit: a01b089b4cef06c05a941b2c0dedaa30ba02069a
reference_commit: a8a678cb6244e6770e1e421767ff0987a1d95549
supersedes: B6 completion baseline
superseded_by: none

> 文档编号：`CR-BASELINE-B7-FREEZE-v2.0`
> 依据交付包：`docs/clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814/`
> 机器可读真值：`machine/baseline.yaml`（本文件是其人工可读渲染，二者必须一致）

## 1. 基线声明

| 项 | 值 |
|---|---|
| project | ClaudeRuntime |
| repository | Nuos/clauderuntime |
| subject_entry_commit | `16da0cfea98d69987739a319ff6ae42cfd432d2c` |
| functional_status | `FUNCTIONALLY_SIMILAR_CORE_COMPLETE` |
| architecture_status | `FINAL_CLOSURE_REQUIRED` |
| reference_alignment | `HIERARCHICAL_REFERENCE_ALIGNMENT` |
| reference_parity_status | `PARTIAL_NOT_RELEASE_GATE` |
| evidence_status | `REBASE_REQUIRED` |
| next_gate | `ARCHITECTURE_FREEZE` |

## 2. Reference 锁定

| 项 | 值 |
|---|---|
| reference product | Claude Code |
| version | 2.1.88 |
| source_kind | `recovered_source_map_snapshot`（非 Anthropic 官方开源源码） |
| reference commit | `a8a678cb6244e6770e1e421767ff0987a1d95549` |
| paper | arXiv:2604.14228v2 |

权威锁定文件：`docs/reference/reference-lock.yaml` / `machine/reference-lock.yaml`。

## 3. 已成熟主体（不因 Freeze 移动）

- canonical Query 主循环为生产主路径；
- Permission deny-first / ask / allow 与 headless fail-closed 逻辑；
- Tool execution、hooks、结果持久化、streaming 主路径；
- 五阶段 Context/Compact 次序固定；
- MCP、Skill、Hook、Plugin、Subagent、Task、State/Resume 均非"缺模块"；
- B6 已有 10k+ 本地测试与 CI green 证据（需在 W9 重新绑定 Freeze SHA）。

## 4. 不得写成"已完成"的部分

- Windows/Linux isolation 未取得最终真实设备证据（PENDING_REAL_DEVICE）；
- strict Source-Aligned / 1:1 parity 不成立，也不作为 Freeze Gate；
- CURRENT docs / scorecard / registry 的 subject commit 存在 generation drift（W0 修复）；
- `ToolContext` 仍有隐式 bypass 默认值（W1 修复）；
- Turn preparation 仍存在两个语义 owner（W2 修复）；
- extension activation trust 还没有统一前置边界（W3 修复）；
- task runtime state 仍存在 legacy mirrors / 双写风险（W4 修复）；
- CI quarantine 没有真正的单一机器清单（W7 修复）。

## 5. 二维状态词汇（禁止单一"完成度百分比"混合口径）

| 轴 | 示例状态 |
|---|---|
| Functional | `COMPLETE / PARTIAL / MISSING` |
| Wiring | `WIRED / ISOLATED / LEGACY_ONLY` |
| Evidence | `NONE / LOCAL / CI / PLATFORM` |
| Reference | `CONFIRMED / ADAPTATION / ACCEPTED_DIFF` |
| Risk | `P0 / P1 / TEST_ONLY` |

## 6. Architecture Freeze 意义

Freeze 不是"没有 bug"，而是：runtime 主脊柱、owner、security boundary、extension
activation boundary、persistence owner 与 CURRENT truth 均不再移动。后续 bug fix 在
这些 contract 内完成。
