# Repository Governance Migration Progress

status: ACTIVE
owner: repository-governance
created: 2026-08-11
last_verified: 2026-08-11
reference_target: Claude Code v2.1.88 analysis baseline
clauderuntime_commit: d29bfe597fe03da951888b0ec7732660852a6196
supersedes: none
superseded_by: none

## Baseline

- HEAD before migration: `d29bfe597fe03da951888b0ec7732660852a6196`
- Initial untracked files: `IDEA.md`, `docs/20260811_0357_clauderuntime_repository_governance_bundle/`
- Python baseline command: `.venv/bin/python -m pytest tests/ --maxfail=1 --disable-warnings`
- Python baseline result: collection failed before migration at `tests/test_ch04_api_round4.py` due to missing `PROMPT_CACHING_SCOPE_BETA_HEADER` export from `src.query.query`.
- Markdown local-link baseline before migration: 114 Markdown files scanned, 105 broken local links found.
- `ui-desktop/node_modules`: absent.
- `ui-tui/node_modules`: present.

## Migration Actions

- Archived `FEATURE_LIST.md` to `docs/archive/roadmaps/FEATURE_LIST-legacy.md`.
- Archived `TODOS.md` to `docs/archive/backlog/TODOS-legacy.md`.
- Moved README-facing root assets to `docs/assets/readme/`.
- Moved Claude Code reference wiki to `docs/reference/claude-code/`.
- Renamed `demos/` to `examples/`.
- Moved architecture, workflow, NEWS, guide, i18n, progress, diagnostic, parity bible, and active plan documents into the governed docs information architecture.
- Moved the repository governance bundle to `docs/archive/governance/`.
- Moved root `IDEA.md` to `docs/archive/governance/IDEA-legacy.md` with an `ARCHIVED / UNKNOWN` label.

## Follow-up Gates

- Re-run Python tests after migration: same collection failure as baseline, `tests/test_ch04_api_round4.py` cannot import `PROMPT_CACHING_SCOPE_BETA_HEADER` from `src.query.query`.
- Run targeted path/reference search: no remaining migrated root-doc paths except intentional historical metadata/text references.
- Run Markdown local-link scan and compare against baseline: post-migration scan found 37 broken local links, down from 105 before migration. Remaining failures are missing historical i18n screenshot assets, one pre-existing `CHANGELOG.md` placeholder link, and missing files inside the imported Claude Code reference snapshot.
- Run `git diff --check`: passed.
- Run `ui-tui` typecheck: passed.
- Run `ui-tui` tests: 1692 passed, 4 skipped, 1 failed in `execFileNoThrow` timing assertion (`1311ms` / `1009ms` on repeat, threshold `500ms`). This appears unrelated to the docs migration.
- Run targeted Python tests for touched path examples: `tests/test_bash_suggestions.py` passed; `tests/workflow` had 189 passed and 1 timing failure in `test_concurrent_agents_run_in_parallel` (`1.05s` / `1.01s` on repeat, threshold `1.0s`).
- Added `scripts/check_docs_governance.py` as a CI-friendly documentation governance gate.
- Wired the gate into `.github/workflows/ci.yml` before the Python test suite.
- Added `docs/status/markdown-link-allowlist.txt` for pre-existing broken local Markdown links, so new broken links fail while the historical baseline remains auditable.
- Updated `.gitignore` demo build-output rules from `demos/` to `examples/`.
- Added `docs/parity/source-map/reference-component-map.yaml`.
- Expanded `docs/parity/runtime/reference-aux-loop-map.yaml` to cover AUX-01 through AUX-14.
- Expanded `docs/parity/runtime/reference-runtime-path-map.yaml` to cover RP-01 through RP-12.
- Extended the documentation governance gate to enforce archive-link policy and 7/5/14 parity-map coverage.
- Added `docs/status/parity-unknown-allowlist.txt` and enforced UNKNOWN baseline checks in `scripts/check_docs_governance.py`.
- Added `docs/status/delete-candidates.md` for Phase G second-round cleanup candidates without deleting them in this migration.
- Completed G-02 delete-candidate reference audit and recorded the results in `docs/status/delete-candidates.md`.
- Completed G-03 cleanup for confirmed DELETE_CANDIDATE files.
- Completed EDITOR-01 cleanup after human confirmation; all tracked personal editor config/state files were removed.
