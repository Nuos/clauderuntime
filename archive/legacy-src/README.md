# Legacy Source Archive (non-package)

> B7 W8 — legacy code moved OUT of the `src/` package so it can never be
> imported as `src.<name>` again. Nothing here is part of the runtime.

## cli_backup

- **Zero-ref proof**: `src/cli_backup` had zero imports/references across
  `src/` and `tests/` (verified by full-tree grep incl. string/importlib
  usage); only historical sourcemap analysis docs mention it
  (`docs/sourcemap/markdown/08-cli_backup-*.md`).
- **Action** (machine/deprecation-plan.yaml): `remove_or_move_outside_package`
  → moved here on 2026-08-15 (W8). Safe to delete after the next release
  audit confirms no third-party import of `src.cli_backup`.
