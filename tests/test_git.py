import unittest

import clishelf.git as git


class GitTestCase(unittest.TestCase):
    def test_get_commit_prefix(self):
        data = git.get_commit_prefix()

        # This assert will true if run on `pytest -v`
        self.assertEqual(23, len(data))
