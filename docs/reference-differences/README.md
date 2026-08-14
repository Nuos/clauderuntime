# Reference Differences Registry

> B6 分级 Reference 对齐：**能确定则对齐；部分确定则已知部分对齐；不能确定才做核心功能一致，并强制记录差异。**

This directory is the global ledger for known differences between Claude Code
`2.1.88` reference behavior and ClaudeRuntime Python behavior. It is the
`B`-level of the mandatory two-level difference recording required by the B6
development bible:

```text
A. 代码附近：模块 docstring Reference Mapping 或函数 REF-DIFF 注释块
B. 全局 registry：docs/reference-differences/registry.yaml   ← 本目录
C. progress 文档：每轮 Reference vs Python 差异摘要（docs/progress/2026/）
```

## Files

| File | Purpose |
|---|---|
| `registry.yaml` | Global difference ledger. Each item records REF vs PY behavior, difference, reason, impact and acceptance status. |
| `platform-verification.md` | Platform real-device verification ledger (win32 Job Object, Linux bubblewrap, macOS Seatbelt environment limits). Items are `PENDING_REAL_DEVICE` until verified on the real platform — never claim "verified" from code presence alone. |
| `generated-summary.yaml` | Optional machine-readable summary derived from the registry (future / CI-friendly). |

## Vocabulary (must match the registry schema)

- `reference_certainty`: `R1_CONFIRMED` → must align; `R2_PARTIALLY_CONFIRMED` →
  align the known part; `R3_UNKNOWN` → functional core only, no invented
  reference facts; `R4_PRODUCT_EXTENSION` → separated product extension.
- `alignment_policy`: `MUST_ALIGN` | `ALIGN_KNOWN_PART` | `FUNCTIONAL_CORE_ONLY`
  | `PRODUCT_EXTENSION`.
- `status`: `FUNCTIONAL_COMPLETE` | `FUNCTIONAL_ADAPTATION` | `LIMITED` |
  `DEFERRED_REFERENCE_DETAIL` | `UNKNOWN_REFERENCE` | `MISSING`.
- `reason`: use only the standard reason vocabulary (e.g.
  `PYTHON_RUNTIME_ADAPTATION`, `RECOVERED_SOURCE_GAP`, `OS_PLATFORM_ADAPTATION`,
  `PRODUCT_SCOPE_SIMPLIFICATION`, `SAFETY_STRENGTHENING`, ...). Never write
  vague reasons like "实现不一样".
- Impacts: `user_impact` / `safety_impact` / `compatibility_impact` each in
  `NONE | LOW | MEDIUM | HIGH`. A `HIGH` safety impact forbids
  `FUNCTIONAL_COMPLETE`.

## Rules

1. `reference.behavior` only states what the recovered source confirms; write
   `R3_UNKNOWN` when it does not.
2. `accepted: true` does **not** mean "identical to Reference".
3. Safety differences are never hidden behind `accepted`.
4. When code comments and the registry disagree, fix the documentation — no
   long-lived dual state.
5. Governance gate: `scripts/check_docs_governance.py` validates the registry
   schema and vocabulary on every run.
