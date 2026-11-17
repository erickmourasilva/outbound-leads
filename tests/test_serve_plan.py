import unittest

from outbound import cli


class ServePlanTest(unittest.TestCase):
    def test_uses_portless_when_available(self):
        mode, cmd = cli.serve_plan(portless_path="/usr/bin/portless", env={}, plain=False, port=None)
        self.assertEqual(mode, "portless")
        self.assertEqual(cmd[0:2], ["/usr/bin/portless", "outbound-leads"])
        self.assertEqual(cmd[-3:], ["-m", "outbound", "serve"])

    def test_plain_without_portless(self):
        self.assertEqual(cli.serve_plan(portless_path=None, env={}, plain=False, port=None)[0], "plain")

    def test_plain_when_already_under_portless(self):
        env = {"PORTLESS_URL": "https://outbound-leads.localhost"}
        self.assertEqual(cli.serve_plan(portless_path="/usr/bin/portless", env=env, plain=False, port=None)[0], "plain")

    def test_plain_when_forced_or_fixed_port(self):
        self.assertEqual(cli.serve_plan(portless_path="/p", env={}, plain=True, port=None)[0], "plain")
        self.assertEqual(cli.serve_plan(portless_path="/p", env={}, plain=False, port=8787)[0], "plain")


if __name__ == "__main__":
    unittest.main()
