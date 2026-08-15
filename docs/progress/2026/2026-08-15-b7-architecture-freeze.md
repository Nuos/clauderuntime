# Architecture Freeze Record — B7

status: FREEZE
owner: repository-governance
created: 2026-08-15
last_verified: 2026-08-15
freeze_sha: a01b089b4cef06c05a941b2c0dedaa30ba02069a
subject_entry_commit: a01b089b4cef06c05a941b2c0dedaa30ba02069a
reference_commit: a8a678cb6244e6770e1e421767ff0987a1d95549
supersedes: B6 FUNCTIONALLY_SIMILAR_CORE_COMPLETE
superseded_by: none

> 文档编号：`CR-FREEZE-RECORD-v1.0`
> 依据交付包：`docs/clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814/`
> 门禁：`machine/architecture-freeze-gates.yaml` + `scripts/check_architecture_freeze.py`

## 结论

**ARCHITECTURE_FREEZE** —— B7 最后一次架构收口完成。W0–W9 全部落地，
Gate A–J 全部 PASS（`python scripts/check_architecture_freeze.py` → FREEZE PASS）。

## 门禁结果（2026-08-15，subject `a01b089b4cef06c05a941b2c0dedaa30ba02069a`）

| Gate | 检查 | 结果 |
|---|---|---|
| A_truth | canonical truth 全部绑定同一 subject；archive 非事实源 | PASS |
| B_loop | query() 单一状态机；compat 适配器委托 | PASS |
| C_turn_preparation | TurnPreparationService 唯一 owner；builder 委托 | PASS |
| D_permission | 无隐式 bypass；bypass 需 origin+reason；headless fail-closed | PASS |
| E_execution | 执行边界单一；平台证据分离（PENDING_REAL_DEVICE 声明） | PASS |
| F_task_state | RuntimeTaskRegistry 单写；legacy 只读投影 | PASS |
| G_extension | 插件 loader 注册包在 ExtensionActivationGate 后 | PASS |
| H_persistence | SessionLifecycle durable-only 契约；resume 无 ephemeral 恢复 | PASS |
| I_legacy | cli_backup 移出包（zero-ref） | PASS |
| J_test_truth | quarantine 单一机器清单驱动；evidence schema 就位 | PASS |

## Wave 收口（全部在 main 直接提交）

| Wave | 提交（近似） | 内容 |
|---|---|---|
| W0 | 486c55f | Truth Reset / canonical truth graph |
| W1 | 9f3f097 | Permission Safe-by-Default |
| W2 | 1557f2c | Canonical Turn Preparation |
| W3 | ade48ca | Extension Trust Boundary |
| W4 | b7158f0 | Task/Session/Persistence Owner |
| W5 | 0ee21e3 | Context/Compact Closure |
| W6 | fa9f4df | Query/Server Ownership Extraction |
| W7 | 21789fe | CI/Platform/Evidence Truth |
| W8 | 416739a | Identity/Legacy Cleanup |
| W9 | a01b089b4cef06c05a941b2c0dedaa30ba02069a | Freeze Gate / Baseline Lock |

## Freeze 后的约束（Behavior Bible §S）

- runtime 主脊柱、owner、security boundary、extension activation boundary、
  persistence owner 与 CURRENT truth 均不再移动；
- 不得因目录/代码长度/与 Reference 相似度发起跨模块重写；
- 只有已验证 contract 无法满足时才允许 RFC 级结构变化；
- 测试/调试管线见交付包 `docs/12_TEST_DEBUG_MASTER_PIPELINE.md`（T0–T14）。

## 未闭合项（真实披露，不构成 Freeze 阻塞）

- Windows Job Object / Linux bubblewrap 真机隔离：`PENDING_REAL_DEVICE`
  （`docs/reference-differences/platform-verification.md`，需对应平台执行）；
- Python 3.10/3.14 + Ubuntu/Windows smoke：声明于 `machine/test-matrix.yaml`，
  实跑为 macOS（Behavior Bible §P：声明 ≠ 已验证）。
