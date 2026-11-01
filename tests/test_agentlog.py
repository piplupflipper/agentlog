"""agentlog のテスト。実行: python3 tests/test_agentlog.py (リポジトリ root で)"""

from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agentlog"


def load():
    loader = importlib.machinery.SourceFileLoader("agentlog_script", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


agentlog = load()


class TrackedCommands(unittest.TestCase):
    def read(self, content):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.json"
            path.write_text(content)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                return agentlog.load_tracked_commands(path), stderr.getvalue()

    def test_missing_file_tracks_nothing(self):
        self.assertEqual(agentlog.load_tracked_commands(Path("/nonexistent/config.json")), {})

    def test_broken_config_is_reported_and_ignored(self):
        tracked, stderr = self.read("{")
        self.assertEqual(tracked, {})
        self.assertIn("読めません", stderr)

    def test_invalid_pattern_is_skipped(self):
        tracked, stderr = self.read(json.dumps({"tracked_commands": {"ok": "foo", "bad": "("}}))
        self.assertEqual(list(tracked), ["ok"])
        self.assertIn("tracked_commands.bad", stderr)

    def test_matching_commands_are_counted(self):
        tracked, _ = self.read(json.dumps({"tracked_commands": {"deploy": r"\bdeploy\b"}}))
        original = agentlog.TRACKED_COMMANDS
        agentlog.TRACKED_COMMANDS = tracked
        try:
            acc = agentlog.Acc("claude")
            acc.see_command("./deploy --prod")
            acc.see_command("ls")
            self.assertEqual(dict(acc.tracked_commands), {"deploy": 1})
        finally:
            agentlog.TRACKED_COMMANDS = original


if __name__ == "__main__":
    unittest.main()
