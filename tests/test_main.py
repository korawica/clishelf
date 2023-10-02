import unittest

from click.testing import CliRunner

from clishelf.cli import echo


class MainTestCase(unittest.TestCase):
    def test_hello_world(self):
        runner = CliRunner()
        result = runner.invoke(echo)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "Hello World\n")
