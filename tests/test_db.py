import os
import tempfile
import unittest

_TMP = tempfile.mkdtemp()
os.environ["OUTBOUND_DB"] = os.path.join(_TMP, "test.db")

from outbound import db  # noqa: E402  (env must be set before import)


class DbTest(unittest.TestCase):
    def setUp(self):
        if os.path.exists(db.DB_PATH):
            os.remove(db.DB_PATH)
        db.init()

    def test_dedupe_by_normalized_handle(self):
        with db.connect() as con:
            self.assertTrue(db.add_lead(con, kind="client", name="A", handle="@Clinica_X/"))
            self.assertFalse(db.add_lead(con, kind="client", name="A2", handle="clinica_x"))
            self.assertEqual(con.execute("SELECT COUNT(*) FROM leads").fetchone()[0], 1)

    def test_do_not_contact_blocks_new_leads(self):
        with db.connect() as con:
            con.execute("INSERT INTO do_not_contact(handle, reason, created_at) VALUES ('bloqueado', 'pediu', ?)", (db.now_utc(),))
            self.assertFalse(db.add_lead(con, kind="partner", name="B", handle="@bloqueado"))

    def test_invalid_kind_rejected(self):
        with self.assertRaises(Exception):
            with db.connect() as con:
                con.execute("INSERT INTO leads(kind,name,handle,created_at,updated_at) VALUES ('x','n','h','t','t')")

    def test_sending_starts_paused(self):
        with db.connect() as con:
            self.assertEqual(db.get_settings(con)["paused"], "1")


if __name__ == "__main__":
    unittest.main()
