"""B6 Wave F1 — NotebookEdit tool edge cases.

05 号文档 Tools 项“补缺失 tool edge cases”。覆盖 replace/insert/delete 三种
编辑模式、输入校验（非 .ipynb / 非法 edit_mode / insert 缺 cell_type）、
不存在的 cell、越界删除、文件必须已读且未变。
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.tool_system.context import ToolContext
from src.tool_system.errors import ToolInputError
from src.tool_system.tools.notebook_edit import NotebookEditTool


def _notebook(cells: list[dict] | None = None) -> dict:
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {"language_info": {"name": "python"}},
        "cells": cells or [
            {"id": "c1", "cell_type": "code", "source": "print(1)", "metadata": {}},
            {"id": "c2", "cell_type": "markdown", "source": "# title", "metadata": {}},
        ],
    }


def _write_nb(path: Path, nb: dict | None = None) -> dict:
    nb = nb or _notebook()
    path.write_text(json.dumps(nb), encoding="utf-8")
    return nb


def _ctx(tmp_path: Path, path: Path, read_ok: bool = True) -> ToolContext:
    ctx = ToolContext(workspace_root=tmp_path)
    ctx.was_file_read_and_unchanged = lambda p: read_ok  # type: ignore[method-assign]
    ctx.ensure_allowed_path = lambda p: Path(p)  # type: ignore[method-assign]
    return ctx


def _cells_after(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["cells"]


class TestNotebookEdit:
    def test_replace_cell_source(self, tmp_path: Path) -> None:
        path = tmp_path / "nb.ipynb"
        _write_nb(path)
        result = NotebookEditTool.call(
            {"notebook_path": str(path), "cell_id": "c1", "new_source": "print(2)"},
            _ctx(tmp_path, path),
        )
        assert result.is_error is False
        assert _cells_after(path)[0]["source"] == "print(2)"

    def test_replace_by_positional_cell_id(self, tmp_path: Path) -> None:
        path = tmp_path / "nb.ipynb"
        _write_nb(path)
        NotebookEditTool.call(
            {"notebook_path": str(path), "cell_id": "cell-1", "new_source": "# changed"},
            _ctx(tmp_path, path),
        )
        assert _cells_after(path)[1]["source"] == "# changed"

    def test_insert_cell_after_target(self, tmp_path: Path) -> None:
        path = tmp_path / "nb.ipynb"
        _write_nb(path)
        result = NotebookEditTool.call(
            {"notebook_path": str(path), "cell_id": "c1", "edit_mode": "insert",
             "cell_type": "code", "new_source": "print(1.5)"},
            _ctx(tmp_path, path),
        )
        assert result.is_error is False
        cells = _cells_after(path)
        assert len(cells) == 3
        assert cells[1]["source"] == "print(1.5)"

    def test_insert_at_beginning_without_cell_id(self, tmp_path: Path) -> None:
        path = tmp_path / "nb.ipynb"
        _write_nb(path)
        NotebookEditTool.call(
            {"notebook_path": str(path), "edit_mode": "insert",
             "cell_type": "markdown", "new_source": "# intro"},
            _ctx(tmp_path, path),
        )
        cells = _cells_after(path)
        assert cells[0]["source"] == "# intro"

    def test_delete_cell(self, tmp_path: Path) -> None:
        path = tmp_path / "nb.ipynb"
        _write_nb(path)
        result = NotebookEditTool.call(
            {"notebook_path": str(path), "cell_id": "c1", "edit_mode": "delete"},
            _ctx(tmp_path, path),
        )
        assert result.is_error is False
        assert len(_cells_after(path)) == 1

    def test_non_ipynb_rejected(self, tmp_path: Path) -> None:
        path = tmp_path / "notes.txt"
        path.write_text("x", encoding="utf-8")
        with pytest.raises(ToolInputError, match="Not a notebook"):
            NotebookEditTool.call(
                {"notebook_path": str(path), "new_source": "x"}, _ctx(tmp_path, path)
            )

    def test_invalid_edit_mode_rejected(self, tmp_path: Path) -> None:
        path = tmp_path / "nb.ipynb"
        _write_nb(path)
        with pytest.raises(ToolInputError, match="Invalid edit_mode"):
            NotebookEditTool.call(
                {"notebook_path": str(path), "edit_mode": "shred", "new_source": "x"},
                _ctx(tmp_path, path),
            )

    def test_insert_requires_cell_type(self, tmp_path: Path) -> None:
        path = tmp_path / "nb.ipynb"
        _write_nb(path)
        with pytest.raises(ToolInputError, match="cell_type is required"):
            NotebookEditTool.call(
                {"notebook_path": str(path), "edit_mode": "insert", "new_source": "x"},
                _ctx(tmp_path, path),
            )

    def test_unknown_cell_id_rejected(self, tmp_path: Path) -> None:
        path = tmp_path / "nb.ipynb"
        _write_nb(path)
        with pytest.raises(ToolInputError, match="Cell not found"):
            NotebookEditTool.call(
                {"notebook_path": str(path), "cell_id": "nope", "new_source": "x"},
                _ctx(tmp_path, path),
            )

    def test_missing_file_rejected(self, tmp_path: Path) -> None:
        path = tmp_path / "missing.ipynb"
        with pytest.raises(ToolInputError, match="does not exist"):
            NotebookEditTool.call(
                {"notebook_path": str(path), "new_source": "x"}, _ctx(tmp_path, path)
            )

    def test_unread_or_changed_file_rejected(self, tmp_path: Path) -> None:
        path = tmp_path / "nb.ipynb"
        _write_nb(path)
        with pytest.raises(ToolInputError, match="read first"):
            NotebookEditTool.call(
                {"notebook_path": str(path), "new_source": "x"},
                _ctx(tmp_path, path, read_ok=False),
            )

    def test_invalid_notebook_json_rejected(self, tmp_path: Path) -> None:
        path = tmp_path / "nb.ipynb"
        path.write_text("{not json", encoding="utf-8")
        with pytest.raises(ToolInputError, match="Invalid notebook JSON"):
            NotebookEditTool.call(
                {"notebook_path": str(path), "new_source": "x"}, _ctx(tmp_path, path)
            )
