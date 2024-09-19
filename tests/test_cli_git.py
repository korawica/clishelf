import datetime as dt
import subprocess
import sys
import unittest
from unittest.mock import DEFAULT, patch

import clishelf.git as git


def side_effect_func(*args, **kwargs):
    if any(["git", "rev-parse", "--abbrev-ref", "HEAD"] == a for a in args):
        _ = kwargs
        return "0.1.2".encode(encoding=sys.stdout.encoding)
    elif any(["git", "describe", "--tags", "--abbrev=0"] == a for a in args):
        _ = kwargs
        return "v0.0.1".encode(encoding=sys.stdout.encoding)
    else:
        return DEFAULT


class GitTestCase(unittest.TestCase):
    def test_commit_message(self):
        msg = git.CommitMsg(content="test: test commit message", body="")
        self.assertEqual(
            ":test_tube: test: test commit message",
            msg.content,
        )
        self.assertEqual(
            "Code Changes",
            msg.mtype,
        )

    def test_commit_log(self):
        commit_log = git.CommitLog(
            hash="",
            refs="",
            date=dt.datetime(2021, 1, 1),
            msg=git.CommitMsg(content="test: test commit message", body="|"),
            author="Demo Username",
        )
        self.assertEqual(
            ":test_tube: test: test commit message",
            commit_log.msg.content,
        )

    @patch("clishelf.git.subprocess.check_output", side_effect=side_effect_func)
    def test_get_latest_tag(self, mock):
        # Start Test after mock subprocess.
        result = git.get_latest_tag()
        self.assertTrue(mock.called)
        self.assertEqual("v0.0.1", result)

    @patch(
        "clishelf.git.subprocess.check_output",
        side_effect=subprocess.CalledProcessError(1, "git"),
    )
    def test_get_latest_tag_raise(self, mock):
        # Start Test after mock subprocess.
        result = git.get_latest_tag()
        self.assertTrue(mock.called)
        self.assertEqual("v0.0.0", result)
