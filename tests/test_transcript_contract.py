"""Wave 3 F11 — transcript 契约测试（CCR-10 Session/Transcript）。

对照 reference transcript 语义：
- append-oriented：TranscriptWriter 追加、TranscriptReader 顺序读回
- tail crash tolerance：尾部残缺 JSONL 行不抛异常（writer 崩溃中途）
- session resume 重建：resume_session 读 JSONL → typed messages + warnings
- 元数据缺失 → success=False（fail-closed）
"""

import json
import tempfile
import unittest
from pathlib import Path

from src.agent.transcript import TranscriptReader, TranscriptWriter
from src.services.session_persistence import SessionPersister
from src.services.session_resume import resume_session


class TestTranscriptRoundtrip(unittest.TestCase):
    """append-oriented 读写契约。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "transcript.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def test_writer_append_reader_roundtrip(self):
        """追加写入 → 顺序读回（append-oriented）。"""
        writer = TranscriptWriter(self.path)
        writer.append({"role": "user", "content": "hello"})
        writer.append({"role": "assistant", "content": "hi"})
        entries = TranscriptReader(self.path).read_all()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["role"], "user")
        self.assertEqual(entries[1]["role"], "assistant")

    def test_reader_tolerates_trailing_partial_line(self):
        """尾部残缺行（writer 崩溃中途）不抛异常，完整行仍读回。"""
        writer = TranscriptWriter(self.path)
        writer.append({"role": "user", "content": "keep me"})
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write('{"role": "assistant", "content": "cr')  # 截断 JSON
        entries = TranscriptReader(self.path).read_all()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["content"], "keep me")


class TestSessionResume(unittest.TestCase):
    """resume_session 重建契约。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.sessions_dir = Path(self.tmp.name) / "sessions"
        self.sessions_dir.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _seed_session(self, session_id: str):
        persister = SessionPersister(session_id, self.sessions_dir)
        persister.start(model="test-model", cwd="/tmp")
        persister.record_user("first prompt")
        persister.record({"role": "assistant", "content": "first reply"})
        persister.flush()
        return session_id

    def test_resume_session_reconstructs_messages(self):
        """resume 重建：2 条消息 + metadata + success。"""
        sid = self._seed_session("sess_resume_1")
        result = resume_session(sid, sessions_dir=self.sessions_dir)
        self.assertTrue(result.success)
        self.assertEqual(result.message_count, 2)
        self.assertIsNotNone(result.metadata)

    def test_resume_missing_metadata_fails_closed(self):
        """无 metadata → success=False + 警告。"""
        result = resume_session(
            "sess_nonexistent", sessions_dir=self.sessions_dir,
        )
        self.assertFalse(result.success)
        self.assertTrue(result.has_warnings)

    def test_resume_handles_snip_boundaries(self):
        """compact boundary：/compact 标记消息被正确截断（snip 边界处理）。"""
        sid = "sess_snip"
        persister = SessionPersister(sid, self.sessions_dir)
        persister.start()
        persister.record_user("before compact")
        persister.record({"role": "assistant", "content": "/compact", "isCompactSummary": True})
        persister.record_user("after compact")
        persister.flush()
        result = resume_session(sid, sessions_dir=self.sessions_dir)
        self.assertTrue(result.success)
        self.assertGreaterEqual(result.message_count, 2)


if __name__ == "__main__":
    unittest.main()
