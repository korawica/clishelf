import sys
import unittest
from typing import Tuple
from unittest.mock import DEFAULT, patch

import clishelf.git as git


def side_effect_func(*args, **kwargs):
    if any(["git", "config", "--local", "user.name"] == a for a in args):
        _ = kwargs
        return "Test User".encode(encoding=sys.stdout.encoding)
    elif any(["git", "config", "--local", "user.email"] == a for a in args):
        _ = kwargs
        return "test@mail.com".encode(encoding=sys.stdout.encoding)
    else:
        return DEFAULT


class GitModelTestCase(unittest.TestCase):
    def test_commit_prefix(self):
        rs = git.CommitPrefix(
            name="test",
            group="A",
            emoji=":dart:",
        )
        self.assertEqual(hash(rs), hash(rs.name))
        self.assertEqual("test", str(rs))

    def test_commit_prefix_group(self):
        rs = git.CommitPrefixGroup(
            name="test",
            emoji=":dart:",
        )
        self.assertEqual(hash(rs), hash(rs.name))
        self.assertEqual("test", str(rs))


class GitTestCase(unittest.TestCase):

    @patch("clishelf.git.subprocess.check_output", side_effect=side_effect_func)
    @patch("clishelf.utils.load_pyproject")
    def test_load_profile(self, mock_load_pyproject, mock):
        mock_load_pyproject.return_value = {}
        rs = git.load_profile()
        self.assertIsInstance(rs, git.Profile)
        self.assertEqual("Test User", rs.name)
        self.assertEqual("test@mail.com", rs.email)
        self.assertTrue(mock.called)

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

    def test_get_branch_name(self): ...

    def test_get_latest_tag(self): ...

    def test_gen_commit_log(self): ...
