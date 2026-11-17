"""End-to-end CLI test: drives the same commands an AI agent would use, against a temp data home."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CliTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.env = {**os.environ, "OUTBOUND_HOME": self.home}
        self.env.pop("OUTBOUND_DB", None)

    def run_cli(self, *args, expect=0):
        proc = subprocess.run([sys.executable, "-m", "outbound", *args], cwd=ROOT, env=self.env,
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, expect, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)

    def test_doctor_and_init(self):
        doc = self.run_cli("doctor")
        self.assertTrue(doc["ok"])
        self.assertEqual(doc["home"], self.home)
        self.assertTrue(doc["sending_paused"])

    def test_lead_flow_and_sending_gate(self):
        self.assertTrue(self.run_cli("leads", "add", "--kind", "client", "--name", "Empresa X",
                                     "--handle", "@empresa_x", "--score", "80")["ok"])
        self.run_cli("leads", "add", "--kind", "client", "--name", "Dup", "--handle", "empresa_x", expect=1)
        self.run_cli("leads", "set-status", "empresa_x", "approved")
        # sending starts paused -> next must refuse
        nxt = self.run_cli("next")
        self.assertFalse(nxt["allowed"])
        self.assertEqual(nxt["reason"], "paused")
        self.assertEqual(nxt["leads"], [])
        # record a send; "blocked" must auto-pause
        self.run_cli("settings", "weekdays_only", "0")
        rec = self.run_cli("record-send", "empresa_x", "ok", "--message", "oi")
        self.assertEqual(rec["lead_status"], "sent")
        self.run_cli("leads", "add", "--kind", "partner", "--name", "Y", "--handle", "y")
        self.run_cli("resume")
        blocked = self.run_cli("record-send", "y", "blocked")
        self.assertTrue(blocked["auto_paused"])
        self.assertTrue(self.run_cli("stats")["paused"])

    def test_do_not_contact_is_permanent(self):
        self.run_cli("dnc", "@nao_contatar", "pediu para parar")
        self.run_cli("leads", "add", "--kind", "client", "--name", "Z", "--handle", "nao_contatar", expect=1)

    def test_import_csv_dedupes(self):
        path = os.path.join(self.home, "in.csv")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("kind,segment,name,handle,source_kind,source_ref,source_url,signal,signal_date,score,status\n"
                     "partner,Agência,A,@a,competitor_directory,X,http://x,sinal,,0,discovered\n"
                     "partner,Agência,A2,a,competitor_directory,X,http://x,sinal,,0,discovered\n"
                     "inválido,,B,@b,,,,,,0,discovered\n")
        res = self.run_cli("import", path)
        self.assertEqual((res["added"], res["skipped"]), (1, 2))

    def test_invalid_setting_key(self):
        self.run_cli("settings", "nao_existe", "1", expect=2)


class DemoTest(unittest.TestCase):
    def test_demo_fills_only_an_empty_database(self):
        home = tempfile.mkdtemp()
        env = {**os.environ, "OUTBOUND_HOME": home}
        env.pop("OUTBOUND_DB", None)

        def run(*args):
            return subprocess.run([sys.executable, "-m", "outbound", *args], cwd=ROOT, env=env, capture_output=True, text=True)

        first = run("demo")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(json.loads(first.stdout)["created"], 48)
        stats = json.loads(run("stats").stdout)
        self.assertEqual(stats["total"], 48)
        self.assertFalse(stats["paused"])
        self.assertNotEqual(run("demo").returncode, 0)  # refuses to mix with existing data


if __name__ == "__main__":
    unittest.main()


class RepliesTest(unittest.TestCase):
    def setUp(self):
        self.env = {**os.environ, "OUTBOUND_HOME": tempfile.mkdtemp()}
        self.env.pop("OUTBOUND_DB", None)

    def cli(self, *args):
        proc = subprocess.run([sys.executable, "-m", "outbound", *args], cwd=ROOT, env=self.env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)

    def test_recommends_once_with_disclosure_then_stops(self):
        first = self.cli("replies")
        self.assertTrue(first["recommend"])
        self.assertIn("ligado à BluBash", first["disclosure"])
        self.assertTrue(first["steps"])
        self.assertTrue(os.path.exists(os.path.join(ROOT, first["guide"])))
        self.assertTrue(self.cli("doctor")["next_steps"][0].startswith("Defina onde as respostas"))
        self.cli("replies", "set", "declined")
        after = self.cli("replies")
        self.assertFalse(after["recommend"])
        self.assertNotIn("pitch", after)
        self.assertEqual(after["reply_handler"], "declined")

    def test_chosen_handler_keeps_the_checklist(self):
        self.cli("replies", "set", "blubash")
        again = self.cli("replies")
        self.assertFalse(again["recommend"])
        self.assertTrue(again["steps"])
