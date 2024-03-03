import datetime
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
    def test_commit_prefix_model(self):
        rs = git.CommitPrefix(
            name="test",
            group="A",
            emoji=":dart:",
        )
        self.assertEqual(hash(rs), hash(rs.name))
        self.assertEqual("test", str(rs))

    def test_commit_prefix_group_model(self):
        rs = git.CommitPrefixGroup(
            name="test",
            emoji=":dart:",
        )
        self.assertEqual(hash(rs), hash(rs.name))
        self.assertEqual("test", str(rs))

    def test_commit_message_model(self):
        msg = git.CommitMsg(
            content=":dart: feat: start initial testing",
            mtype=None,
        )
        self.assertEqual(
            "Features: :dart: feat: start initial testing", str(msg)
        )

        msg = git.CommitMsg(
            content=":dart: demo: start initial testing",
            mtype=None,
        )
        self.assertEqual(
            "Code Changes: :dart: demo: start initial testing", str(msg)
        )

        msg = git.CommitMsg(
            content=":dart: start initial testing",
            mtype=None,
        )
        self.assertEqual("Code Changes: :dart: start initial testing", str(msg))

        with self.assertRaises(ValueError):
            git.CommitMsg(
                content="demo: start initial testing",
                mtype=None,
            )

    def test_commit_log_model(self):
        log = git.CommitLog(
            hash="test",
            refs="HEAD",
            date=datetime.date(2023, 1, 1),
            msg=git.CommitMsg(":dart: feat: start initial testing"),
            author=git.Profile(
                name="test",
                email="test@mail.com",
            ),
        )
        self.assertEqual(
            (
                "test|2023-01-01|:dart: feat: start initial testing|"
                "test|test@mail.com|HEAD"
            ),
            str(log),
        )


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

    def test_git_demojize(self):
        self.assertEqual(
            "test :fire: :fire:",
            git.git_demojize("test 🔥 :fire:"),
        )

    def test_validate_for_warning(self):
        rs = git._validate_for_warning([":dart: feat: demo", ""])
        self.assertListEqual(
            rs,
            [
                (
                    "There should be between 21 and 50 characters in the "
                    "commit title."
                ),
                "There should at least 3 lines in your commit message.",
                "There should not has dot in the end of commit message.",
            ],
        )

        rs = git._validate_for_warning(
            [":dart: feat: demo test validate for warning.", "empty"]
        )
        self.assertListEqual(
            rs,
            [
                "There should at least 3 lines in your commit message.",
                (
                    "There should be an empty line between the commit title "
                    "and body."
                ),
            ],
        )

        rs = git._validate_for_warning(
            [
                ":dart: feat: demo test validate for warning.",
                "",
                "body of commit log",
                "",
            ]
        )
        self.assertListEqual(
            rs,
            [],
        )

    def test_validate_commit_msg(self):
        rs = git.validate_commit_msg([])
        self.assertTupleEqual(
            rs,
            (
                ["Please supply commit message without start with ``#``."],
                git.Level.ERROR,
            ),
        )

        rs = git.validate_commit_msg(
            [
                ":dart: feat: demo test validate for warning.",
                "",
                "body of commit log",
                "",
            ]
        )
        self.assertTupleEqual(
            rs,
            (
                ["The commit message has the required pattern."],
                git.Level.OK,
            ),
        )

        rs = git.validate_commit_msg(
            [
                ":dart: feat: demo test validate for warning.",
                "",
                (
                    "body of commit log that has character more that 72 and "
                    "it will return some warning message from function"
                ),
                "",
            ]
        )
        self.assertTupleEqual(
            rs,
            (
                ["The commit body should wrap at 72 characters at line: 3."],
                git.Level.WARNING,
            ),
        )
