import pathlib
import unittest

import clishelf.utils as utils


class UtilsTestCase(unittest.TestCase):
    def test_pwd(self):
        result = utils.pwd()
        self.assertEqual(pathlib.Path("."), result)

    def test_make_color(self):
        result = utils.make_color("test", utils.Level.OK)
        self.assertEqual("\x1b[92m\x1b[1mOK: test\x1b[0m", result)
