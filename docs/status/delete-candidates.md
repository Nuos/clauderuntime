# Second-Round Delete Candidates

status: CURRENT
owner: repository-governance
created: 2026-08-11
last_verified: 2026-08-11
supersedes: none
superseded_by: none

This file tracks deletion candidates only. Do not delete these items as part of
the first repository-governance migration. The governance bundle requires any
deletion to happen in a separate commit or PR after the migration is reviewable.

## G-01 Personal Editor Workspace State

| Item | Label | Rationale | Next Action |
|---|---|---|---|
| Personal workspace layout state | DELETED | Personal UI layout state; listed by the governance checklist as a second-round candidate; G-02 audit found no current project dependency | Deleted in G-03 cleanup |
| Personal graph UI state | DELETED | Personal graph UI state; listed by the governance checklist as a second-round candidate; G-02 audit found no current project dependency | Deleted in G-03 cleanup |
| Personal appearance UI state | DELETED | Personal appearance UI state; listed by the governance checklist as a second-round candidate; G-02 audit found no current project dependency | Deleted in G-03 cleanup |

## G-02 Shared Editor Configuration

| Item | Label | Rationale | Next Action |
|---|---|---|---|
| Shared editor app configuration | DELETED | G-02 audit found no project structure, script, CI, or parity-map dependency | Deleted in EDITOR-01 cleanup |
| Shared editor plugin configuration | DELETED | G-02 audit found no project structure, script, CI, or parity-map dependency | Deleted in EDITOR-01 cleanup |

## G-03 Local OS Metadata

| Path Pattern | Label | Rationale | Next Action |
|---|---|---|---|
| `docs/**/.DS_Store` | DELETED_LOCAL | macOS metadata; already ignored by `.gitignore` | Removed from the local worktree in G-03 cleanup |

## G-04 Legacy Planning Documents

| Path | Label | Rationale | Next Action |
|---|---|---|---|
| `docs/archive/roadmaps/FEATURE_LIST-legacy.md` | DELETED | Historical roadmap snapshot superseded by `docs/status/`; G-02 audit found no current fact-source references | Deleted in G-03 cleanup |
| `docs/archive/backlog/TODOS-legacy.md` | DELETED | Historical TODO snapshot superseded by `docs/status/backlog.md` and GitHub Issues; G-02 audit found only `supersedes`/progress history references | Deleted in G-03 cleanup |

## G-05 Generated Historical HTML

| Path Pattern | Label | Rationale | Next Action |
|---|---|---|---|
| `docs/parity/*.html` | DELETED | Generated historical HTML retained during the zero-loss migration; G-02 audit found no current entry-point references | Deleted in G-03 cleanup |
| `docs/plans/active/*.html` | DELETED | Generated historical HTML retained during the zero-loss migration; G-02 audit found no current entry-point references | Deleted in G-03 cleanup |

## G-02 Reference Audit

Last audit: 2026-08-11

- README, docs indexes, scripts, CI, and parity maps do not depend on the personal editor state files.
- Legacy FEATURE/TODOS archives are referenced only as historical `supersedes` or migration progress evidence, not as current fact sources.
- Generated historical HTML files have Markdown counterparts and no current docs entry-point links.
- Shared editor app/plugin configuration files had no project structure, script, CI, or parity-map dependency.

## G-03 Cleanup Result

Cleanup date: 2026-08-11

- Deleted confirmed personal editor state files.
- Deleted shared editor app/plugin configuration files in EDITOR-01 after user confirmation that related content should be removed.
- Deleted legacy roadmap/TODO snapshots after the archive tracking correction made them recoverable from Git history.
- Deleted generated historical HTML files that have Markdown counterparts.
- Removed ignored local `.DS_Store` metadata files from the worktree.

## EDITOR-01 Cleanup Result

Cleanup date: 2026-08-11

- Removed all tracked personal editor configuration/state files from the reference tree.
- No related config/state files remain in the tracked reference tree.
