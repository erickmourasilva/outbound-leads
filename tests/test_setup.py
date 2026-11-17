"""setup --check must report precisely what is missing, without installing anything."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SetupTest(unittest.TestCase):
    def run_setup(self, path_value):
        env = {**os.environ, "OUTBOUND_HOME": tempfile.mkdtemp(), "PATH": path_value}
        proc = subprocess.run([sys.executable, "-m", "outbound", "setup", "--check"], cwd=ROOT, env=env,
                              capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout)

    def test_extraction_ready_even_without_node_or_browser(self):
        code, report = self.run_setup(tempfile.mkdtemp())  # empty PATH: no node, npm or agent-browser
        self.assertEqual(code, 0, report)
        self.assertTrue(report["extract_tools_ready"])
        self.assertFalse(report["send_tools_ready"])
        statuses = {s["step"]: s["status"] for s in report["steps"]}
        self.assertEqual(statuses["node+npm"], "manual")
        self.assertTrue(any("Node" in m for m in report["manual_steps"]))

    def test_check_mode_installs_nothing(self):
        _, report = self.run_setup(tempfile.mkdtemp())
        self.assertNotIn("installed", {s["status"] for s in report["steps"]})


if __name__ == "__main__":
    unittest.main()
