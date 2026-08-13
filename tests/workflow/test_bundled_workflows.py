"""Compilation checks for bundled workflow DSL scripts."""

from pathlib import Path

from src.workflow.sandbox import compile_workflow, extract_meta


def test_bundled_workflows_compile_with_workflow_compiler() -> None:
    """Top-level await/return are valid after the workflow async wrapper is applied."""
    bundled_dir = Path("src/workflow/bundled")
    scripts = sorted(path for path in bundled_dir.glob("*.py") if path.name != "__init__.py")

    assert scripts, "expected at least one bundled workflow"
    for script in scripts:
        source = script.read_text(encoding="utf-8")
        meta = extract_meta(source)
        assert meta.name
        compile_workflow(source)
