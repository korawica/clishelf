import unittest

import clishelf.git as git


class GitTestCase(unittest.TestCase):
    def test_get_commit_prefix(self):
        data = git.get_commit_prefix()

        # This assert will true if run on `pytest -v`
        self.assertEqual(23, len(data))

    def test_get_commit_prefix_group(self):
        data = git.get_commit_prefix_group()

        features = [_ for _ in data if _[0] == "Features"][0]
        self.assertEqual(":tada:", features[1])
