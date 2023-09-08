import unittest

from click.testing import CliRunner

from clishelf.cli import say


class MainTestCase(unittest.TestCase):
    def test_hello_world(self):
        runner = CliRunner()
        result = runner.invoke(say)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, "Hello World\n")
