import unittest

from click.testing import CliRunner

from clishelf.cli import echo


class CliTestCase(unittest.TestCase):
    def test_hello_world(self):
        runner = CliRunner()
        result = runner.invoke(echo)
        self.assertEqual(0, result.exit_code)
        self.assertEqual("Hello World\n", result.output)
