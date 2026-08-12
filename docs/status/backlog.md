# Current Backlog Index

status: CURRENT
owner: repository-governance
created: 2026-08-11
last_verified: 2026-08-11
reference_target: Claude Code v2.1.88 analysis baseline
clauderuntime_commit: d29bfe597fe03da951888b0ec7732660852a6196
supersedes: docs/archive/backlog/TODOS-legacy.md
superseded_by: none

This file is a high-level gap index only. GitHub Issues are the source of truth for executable work items.

| ID | Component | Layer | AUX | Priority | Issue |
|---|---|---|---|---|---|
| GOV-01 | Repository Governance | L5 | none | DONE | CI check added in `scripts/check_docs_governance.py` |
| GOV-02 | Repository Governance | L5 | none | DONE | Broken-link check, historical allowlist, and archive-link policy added in `scripts/check_docs_governance.py` |
| PAR-01 | Parity Evidence | L2-L4 | AUX-01..AUX-14 | PARTIAL | Machine-readable maps now cover 7 components, 14 AUX loops, and 12 runtime paths; UNKNOWN/PARTIAL evidence remains to verify |
| PAR-02 | Parity Evidence | L2-L4 | AUX-06,AUX-14,RP-03,RP-07..RP-12 | P1 | Resolve or justify records in `parity-unknown-allowlist.txt` |
| GOV-03 | Repository Governance | L5 | none | DONE | Confirmed second-round delete candidates removed; personal editor config/state files removed |
| TEST-01 | Test Baseline | L5 | AUX-01 | P0 | Resolve current `tests/test_ch04_api_round4.py` import collection failure |
