"""B6 P2 — Scheduler file-backed 持久化增强（DIFF-SCHED-001）。

`SessionCronScheduler(persist_path=...)` 后每次变更（create/delete/
set_wakeup/clear_wakeup/pop_due）原子写盘；服务重启后由新进程
`from_persisted` / `restore_persisted` 跨进程恢复，无需会话 resume 文件。

恢复规则与 `restore` 一致：7 天内的 recurring 恢复、已过期 one-shot 丢弃、
durable one-shot 补执行一次、未来 wakeup 恢复。
"""

from __future__ import annotations

import json
import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from src.scheduled_tasks import SessionCronScheduler


class Clock:
    """可控时间源，固定在真实墙钟分钟上（避免时区/DST 抖动）。"""

    def __init__(self, start: datetime | float | None = None) -> None:
        if start is None:
            start = datetime(2026, 7, 7, 12, 0, 30)
        self.t = start.timestamp() if isinstance(start, datetime) else float(start)

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


def _make(clock: Clock, path: str | Path) -> SessionCronScheduler:
    return SessionCronScheduler(now_fn=clock, jitter=False, persist_path=str(path))


class TestFileBackedPersistence(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "scheduled_tasks.json"

    def _read_file(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def test_create_persists_job_to_file(self) -> None:
        clock = Clock()
        sched = _make(clock, self.path)
        job = sched.create("* * * * *", "persisted prompt")

        raw = self._read_file()
        self.assertEqual(len(raw["jobs"]), 1)
        self.assertEqual(raw["jobs"][0]["id"], job.id)
        self.assertEqual(raw["jobs"][0]["prompt"], "persisted prompt")

    def test_new_process_restores_recurring_job(self) -> None:
        """另一个进程（新实例）从文件恢复任务 —— 无需会话 resume 文件。"""
        clock = Clock()
        sched = _make(clock, self.path)
        job = sched.create("* * * * *", "survives restart")

        restarted = _make(Clock(clock()), self.path)
        restored = restarted.restore_persisted()
        self.assertEqual(restored, 1)
        jobs = restarted.list_jobs()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].id, job.id)
        self.assertEqual(jobs[0].prompt, "survives restart")

    def test_from_persisted_classmethod(self) -> None:
        clock = Clock()
        sched = _make(clock, self.path)
        sched.create("* * * * *", "via classmethod")

        restarted = SessionCronScheduler.from_persisted(
            self.path, now_fn=clock, jitter=False
        )
        self.assertEqual(len(restarted.list_jobs()), 1)

    def test_delete_persists_removal(self) -> None:
        clock = Clock()
        sched = _make(clock, self.path)
        job = sched.create("* * * * *", "to delete")
        self.assertTrue(sched.delete(job.id))

        raw = self._read_file()
        self.assertEqual(raw["jobs"], [])

    def test_durable_one_shot_past_fire_catches_up_once(self) -> None:
        """durable 一次性任务离线错过 → 恢复后补执行一次（next_fire_at=now）。"""
        clock = Clock()
        sched = _make(clock, self.path)
        job = sched.create("* * * * *", "durable one-shot", recurring=False, durable=True)
        # 任务已过期（下一分钟）→ 推进时间越过 next_fire_at
        clock.advance(120)

        restarted = _make(Clock(clock()), self.path)
        restored = restarted.restore_persisted()
        self.assertEqual(restored, 1)
        jobs = restarted.list_jobs()
        self.assertEqual(len(jobs), 1)
        self.assertLessEqual(jobs[0].next_fire_at, clock())

    def test_non_durable_one_shot_past_fire_dropped(self) -> None:
        clock = Clock()
        sched = _make(clock, self.path)
        sched.create("* * * * *", "plain one-shot", recurring=False, durable=False)
        clock.advance(120)

        restarted = _make(Clock(clock()), self.path)
        self.assertEqual(restarted.restore_persisted(), 0)
        self.assertEqual(restarted.list_jobs(), [])

    def test_recurring_expired_while_away_dropped(self) -> None:
        clock = Clock()
        sched = _make(clock, self.path)
        sched.create("* * * * *", "expires")
        # 推进超过 7 天过期窗口
        clock.advance(8 * 24 * 3600)

        restarted = _make(Clock(clock()), self.path)
        self.assertEqual(restarted.restore_persisted(), 0)
        self.assertEqual(restarted.list_jobs(), [])

    def test_wakeup_persisted_and_restored(self) -> None:
        clock = Clock()
        sched = _make(clock, self.path)
        sched.set_wakeup(delay_seconds=300, prompt="wake me", reason="test")

        raw = self._read_file()
        self.assertIsNotNone(raw["wakeup"])
        self.assertEqual(raw["wakeup"]["prompt"], "wake me")

        restarted = _make(Clock(clock()), self.path)
        self.assertEqual(restarted.restore_persisted(), 1)
        wakeup = restarted.wakeup_info()
        self.assertIsNotNone(wakeup)
        self.assertEqual(wakeup.prompt, "wake me")

    def test_expired_wakeup_not_restored(self) -> None:
        clock = Clock()
        sched = _make(clock, self.path)
        sched.set_wakeup(delay_seconds=60, prompt="expired wake", reason="test")
        clock.advance(3600)  # 超过 wakeup 触发时间

        restarted = _make(Clock(clock()), self.path)
        self.assertEqual(restarted.restore_persisted(), 0)
        self.assertIsNone(restarted.wakeup_info())

    def test_pop_due_persists_one_shot_removal(self) -> None:
        clock = Clock()
        sched = _make(clock, self.path)
        job = sched.create("* * * * *", "fire me", recurring=False)
        clock.advance(120)
        fired = sched.pop_due()
        self.assertEqual(len(fired), 1)
        self.assertTrue(fired[0].deleted)

        raw = self._read_file()
        self.assertEqual(raw["jobs"], [])  # 一次任务触发后已从文件移除

    def test_persist_failure_is_nonfatal(self) -> None:
        """写入失败（如不可写目录）只记日志，不阻断调度操作。"""
        clock = Clock()
        sched = SessionCronScheduler(
            now_fn=clock, jitter=False,
            persist_path="/nonexistent-dir-for-sure/scheduled_tasks.json",
        )
        job = sched.create("* * * * *", "still works")
        self.assertEqual(len(sched.list_jobs()), 1)
        self.assertEqual(job.id[:8], job.id)

    def test_no_persist_path_keeps_in_memory_behavior(self) -> None:
        clock = Clock()
        sched = SessionCronScheduler(now_fn=clock, jitter=False)
        sched.create("* * * * *", "in-memory only")
        self.assertFalse(self.path.exists())
        self.assertEqual(len(sched.list_jobs()), 1)


if __name__ == "__main__":
    unittest.main()
