import unittest
from typing import Tuple

import clishelf.git as git


class GitTestCase(unittest.TestCase):
    def test_get_commit_prefix(self):
        data = git.get_commit_prefix()

        # This assert will true if run on `pytest -v`
        self.assertEqual(23, len(data))

    def test_get_commit_prefix_group(self):
        data: Tuple[git.CommitPrefixGroup] = git.get_commit_prefix_group()

        feat: git.CommitPrefixGroup = [
            cm for cm in data if cm.name == "Features"
        ][0]
        self.assertEqual(":tada:", feat.emoji)

    def test_encoding_emoji(self):

        # msg = "<F0><9F><8E><AF> feat: update docs form 20240206. (#40)"
        # print(msg)
        # msg = '🎯 feat'.encode("utf-8")
        # print(msg)
        # print(repr('🎯'))

        for _ in list(
            git.get_commit_logs(
                all_logs=True,
            )
        ):
            print(_)
