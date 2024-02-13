import unittest
from typing import Tuple

import clishelf.git as git


class GitTestCase(unittest.TestCase):
    def test_get_commit_prefix(self):
        data = git.get_commit_prefix()

        # This assert will true if run on `pytest -v`
        self.assertEqual(24, len(data))

    def test_get_commit_prefix_group(self):
        data: Tuple[git.CommitPrefixGroup] = git.get_commit_prefix_group()
        feat: git.CommitPrefixGroup = [
            cm for cm in data if cm.name == "Features"
        ][0]
        self.assertEqual(":tada:", feat.emoji)
