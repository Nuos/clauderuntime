# B7 Wave 记录（WAVE_RECORD）

## W0 — Truth Reset / Evidence Rebase ✅（2026-08-15）

- 交付包入库：`docs/clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814/`
- 建立 repo 级 `machine/` 真值目录（12 个 yaml + 1 个 json，全部绑定 subject_commit=16da0cf）
- canonical truth graph 建成：
  - `docs/baseline/PROJECT_BASELINE.md`（新建）
  - `docs/status/current.md`（重写：subject 绑定 16da0cf，新增 B7 状态段）
  - `docs/plans/active/CURRENT_PLAN.md`（新建；旧七组件计划标 HISTORICAL/SUPERSEDED）
  - `docs/governance/BEHAVIOR_BIBLE.md`（新建）
  - `docs/reference/reference-lock.yaml`（新建）
  - `docs/parity/scorecards/latest.yaml`（subject 7619ff2 → 16da0cf）
  - `docs/reference-differences/registry.yaml`（repository_head dc7393bb → subject_commit 16da0cf）
- 治理扩展：`scripts/check_docs_governance.py` 新增 `check_truth_ssot`（7 资产 subject 一致、
  reference-lock 策略、archive 非事实源、accepted diff 必带 evidence、machine 资产绑定）
- 测试：`tests/test_b7_truth_ssot.py` 10 项，全部通过
- 治理门禁：`python3 scripts/check_docs_governance.py` → PASS
- 退出条件：CURRENT assets 全部绑定同一 subject SHA ✅（16da0cf）

### changed owner / unchanged semantics / rollback
- changed owner：CURRENT truth（docs+机器资产）统一绑定 subject；旧字段 repository_head 废弃
- unchanged semantics：无任何运行时代码改动（纯文档/治理）
- rollback：回退本提交即可（无代码耦合）

## W1 — Permission Safe-by-Default ✅（2026-08-15）

- `ToolContext.permission_context` 默认值：`bypassPermissions` → **`default`**（fail-closed），
  隐式 bypass=0。
- `ToolPermissionContext` 新增 `bypass_origin` / `bypass_reason` + `is_bypass_justified()`；
  `check.py` 裁决点强制：裸 `bypassPermissions` 不再被认可（fall through → ask/deny）。
- 生产入口全部显式构造：`setup_permissions`（含 headless CLI `--dangerously-skip-permissions`
  origin/reason）、`run_agent._build_permission_context`（subagent 传播 parent provenance）、
  `_wrap_avoid_prompts`、`apply_rules_to_context` 保留 bypass 字段。
- headless ask-without-channel → deny（既有行为，新增回归测试固定）。
- registry 新增 5 条 PERM accepted-diff（machine/accepted-differences.yaml → registered），
  治理门禁要求 accepted diff 必须带 evidence。
- W0 补漏：`generate_parity_evidence.py` 将全部 15 个 parity 资产重绑 subject 16da0cf
  （evidence-manifest/coverage-ledger/source-map/runtime 等）。
- 测试：`tests/test_b7_permission_safe_default.py` 17 项；既有权限/工具测试适配
  （~20 个测试文件改为显式 justified bypass，含 3 处过时默认值注释更新）。
- 全量测试：后台确认（预计仅剩 B6 已知 7 项环境失败）。

### changed owner / unchanged semantics / rollback
- changed owner：permission context 默认值（安全默认）；bypass 溯源字段
- unchanged semantics：deny/ask/allow 裁决逻辑、安全不变量不变；仅"未注明溯源的 bypass"
  从 allow 变为 fail-closed
- rollback：回退本提交即可（默认值 + 校验为独立改动）

## W2 — Canonical Turn Preparation ⏳

## W2 — Canonical Turn Preparation ⏳

## W3 — Extension Trust Boundary ⏳

## W4 — Task / Session / Persistence Owner ⏳

## W5 — Context / Compact Closure ⏳

## W6 — Query/Server Ownership Extraction ⏳

## W7 — CI / Platform / Evidence Truth ⏳

## W8 — Identity / Legacy Cleanup ⏳

## W9 — Freeze Gate / Baseline Lock ⏳
