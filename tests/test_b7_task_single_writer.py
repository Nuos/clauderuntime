"""B7 W4 — task single-writer contract tests.

Task Law (Behavior Bible §J): RuntimeTaskRegistry is the ONLY writable owner
for runtime task state. The legacy ``background_bash_tasks`` dict-of-dicts
view is a READ-ONLY projection: reads are derived live from the registry,
writes raise RuntimeError, and the background-bash spawn path no longer
dual-writes.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.runtime.legacy_task_projection import LegacyTaskProjection
from src.task_registry import RuntimeTaskRegistry
from src.tasks.local_shell import LocalShellTaskState
from src.tool_system.context import ToolContext


def _task(task_id: str = "b1", output_path: str = "/tmp/x.log") -> LocalShellTaskState:
    return LocalShellTaskState(
        id=task_id,
        status="running",
        description="probe",
        start_time=1.0,
        output_file=output_path,
        output_path=output_path,
        command="echo x",
        cwd="/tmp",
    )


class TestLegacyTaskProjection(unittest.TestCase):
    def test_get_returns_legacy_dict_from_registry(self) -> None:
        registry = RuntimeTaskRegistry()
        registry.upsert(_task())
        projection = LegacyTaskProjection(registry)
        entry = projection.get("b1")
        self.assertIsInstance(entry, dict)
        self.assertEqual(entry["task_id"], "b1")
        self.assertEqual(entry["output_path"], "/tmp/x.log")

    def test_get_missing_returns_default(self) -> None:
        projection = LegacyTaskProjection(RuntimeTaskRegistry())
        self.assertIsNone(projection.get("nope"))
        self.assertEqual(projection.get("nope", {}), {})

    def test_getitem_and_contains(self) -> None:
        registry = RuntimeTaskRegistry()
        registry.upsert(_task())
        projection = LegacyTaskProjection(registry)
        self.assertIn("b1", projection)
        self.assertEqual(projection["b1"]["task_id"], "b1")
        with self.assertRaises(KeyError):
            projection["nope"]

    def test_len_iter_values_items(self) -> None:
        registry = RuntimeTaskRegistry()
        registry.upsert(_task("a"))
        registry.upsert(_task("b"))
        projection = LegacyTaskProjection(registry)
        self.assertEqual(len(projection), 2)
        self.assertEqual({p["task_id"] for p in projection.values()}, {"a", "b"})
        self.assertEqual({k for k, _ in projection.items()}, {"a", "b"})
        self.assertEqual(set(projection), {"a", "b"})

    def test_write_raises(self) -> None:
        projection = LegacyTaskProjection(RuntimeTaskRegistry())
        with self.assertRaises(RuntimeError):
            projection["b1"] = {"output_path": "/tmp/x.log"}  # type: ignore[index]
        with self.assertRaises(RuntimeError):
            del projection["b1"]  # type: ignore[arg-type]
        with self.assertRaises(RuntimeError):
            projection.update({"b1": {}})
        with self.assertRaises(RuntimeError):
            projection.clear()
        with self.assertRaises(RuntimeError):
            projection.pop("b1")
        with self.assertRaises(RuntimeError):
            projection.setdefault("b1", {})


class TestToolContextSingleWriter(unittest.TestCase):
    def test_background_bash_tasks_is_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ctx = ToolContext(workspace_root=Path(tmp))
            self.assertIsInstance(ctx.background_bash_tasks, LegacyTaskProjection)

    def test_write_to_legacy_view_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ctx = ToolContext(workspace_root=Path(tmp))
            with self.assertRaises(RuntimeError):
                ctx.background_bash_tasks["b1"] = {"output_path": "/tmp/x.log"}  # type: ignore[index]

    def test_registry_write_reflected_in_legacy_view(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ctx = ToolContext(workspace_root=Path(tmp))
            ctx.runtime_tasks.upsert(_task("b9", output_path="/tmp/b9.log"))
            entry = ctx.background_bash_tasks.get("b9")
            self.assertEqual(entry["output_path"], "/tmp/b9.log")

    def test_removal_reflected_in_legacy_view(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ctx = ToolContext(workspace_root=Path(tmp))
            ctx.runtime_tasks.upsert(_task("gone"))
            self.assertIn("gone", ctx.background_bash_tasks)
            ctx.runtime_tasks.remove("gone")
            self.assertNotIn("gone", ctx.background_bash_tasks)

    def test_stuck_tracking_store_is_separate(self) -> None:
        # Guard bookkeeping must not leak into the task-state projection.
        with tempfile.TemporaryDirectory() as tmp:
            ctx = ToolContext(workspace_root=Path(tmp))
            ctx.runtime_tasks.upsert(_task("b2"))
            ctx.stuck_task_tracking["b2"] = {"_stuck_polls": 3}
            entry = ctx.background_bash_tasks.get("b2")
            self.assertNotIn("_stuck_polls", entry)


if __name__ == "__main__":
    unittest.main()
