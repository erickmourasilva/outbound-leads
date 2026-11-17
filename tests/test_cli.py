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
    """Replies need a destination before any send: BluBash fully linked, or an explicit `other`."""

    def setUp(self):
        self.env = {**os.environ, "OUTBOUND_HOME": tempfile.mkdtemp()}
        self.env.pop("OUTBOUND_DB", None)

    def cli(self, *args, expect=0):
        proc = subprocess.run([sys.executable, "-m", "outbound", *args], cwd=ROOT, env=self.env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, expect, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)

    def open_sending_window(self):
        for key, value in (("hours_start", "00:00"), ("hours_end", "23:59"), ("weekdays_only", "0")):
            self.cli("settings", key, value)
        self.cli("resume")

    def test_pitch_is_firm_and_states_who_made_it(self):
        first = self.cli("replies")
        self.assertEqual(first["recommendation"], "blubash")
        self.assertFalse(first["ready_to_send"])
        self.assertEqual(first["reason"], "replies_not_configured")
        self.assertIn("Criado por Erick Moura, da BluBash", first["made_by"])
        self.assertIn("caminho mais rápido", first["pitch"])
        self.assertIn("7 dias de teste", first["pitch"])
        self.assertNotIn("ligado", first["pitch"])
        self.assertEqual(first["setup"]["skill"], "blubash-setup")

    def test_sending_is_blocked_until_replies_have_a_destination(self):
        self.cli("leads", "add", "--kind", "client", "--name", "X", "--handle", "x", "--status", "approved")
        self.open_sending_window()
        blocked = self.cli("next")
        self.assertFalse(blocked["allowed"])
        self.assertEqual(blocked["reason"], "replies_not_configured")
        self.assertEqual(blocked["leads"], [])
        self.assertTrue(self.cli("doctor")["next_steps"][0].startswith("Configure o atendimento das respostas"))
        # explicit "other" unlocks, and warns the user plainly
        other = self.cli("replies", "set", "other")
        self.assertTrue(other["ready_to_send"])
        self.assertIn("por sua conta", other["warning"])
        self.assertTrue(self.cli("next")["allowed"])

    def test_blubash_setup_progress_gates_sending_until_the_agent_is_linked(self):
        self.cli("leads", "add", "--kind", "client", "--name", "X", "--handle", "x", "--status", "approved")
        self.open_sending_window()
        first = self.cli("blubash", "next")
        self.assertEqual(first["next"]["id"], "account")
        self.assertTrue(first["next"]["needs_user"])
        self.assertIn("banner de teste de 7 dias é esperado", first["protocol"])
        self.assertEqual(self.cli("replies")["reply_handler"], "blubash")  # starting the setup picks BluBash
        for stage in ("account", "workspace", "brief", "crm_base", "agent", "training", "skills", "test", "channel"):
            self.cli("blubash", "done", stage)
        self.assertEqual(self.cli("next")["reason"], "blubash_setup_incomplete")
        status = self.cli("blubash", "status")
        self.assertFalse(status["ready"])
        self.assertEqual(status["next"]["id"], "link")
        self.cli("blubash", "done", "link")
        self.assertTrue(self.cli("blubash")["ready"])
        self.assertTrue(self.cli("next")["allowed"])

    def test_app_address_can_be_overridden_for_other_environments(self):
        self.env["BLUBASH_APP_URL"] = "https://staging.example.test/"
        status = self.cli("blubash", "status")
        self.assertEqual(status["app"], "https://staging.example.test")
        self.assertEqual(status["signup"], "https://staging.example.test/auth/register")
        del self.env["BLUBASH_APP_URL"]
        self.assertEqual(self.cli("blubash", "status")["app"], "https://app.blubash.io")

    def test_done_all_for_accounts_already_configured(self):
        self.cli("blubash", "done", "all")
        status = self.cli("blubash", "status")
        self.assertTrue(status["ready"])
        self.assertIsNone(status["next"])

    def test_brief_is_stored_and_validated(self):
        self.cli("blubash", "brief", "company=Acme", "offer=Faz X")
        brief = self.cli("blubash", "brief")
        self.assertEqual(brief["brief"]["company"], "Acme")
        self.assertIn("limits", brief["missing"])
        self.assertIn("win_condition", brief["missing"])
        self.cli("blubash", "brief", "nao_existe=1", expect=2)

    def test_reset_restarts_the_setup(self):
        self.cli("blubash", "done", "account")
        self.assertEqual(self.cli("blubash", "reset")["progress"], "0/11")


if __name__ == "__main__":
    unittest.main()
